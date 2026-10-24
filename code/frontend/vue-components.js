/* Vue 3 runtime-only components. Render functions keep the existing CSP:
 * no runtime template compilation, eval, inline scripts, or remote CDN. */
window.createTomeLibrary = function createTomeLibrary(actions) {
  const {createApp, h, reactive} = Vue;
  const state = reactive({books:[], trash:[], selectedId:null, pending:new Set()});
  const titleOf = book => book.metadata?.title || book.id;
  async function run(key, action) {
    if (state.pending.has(key)) return;
    state.pending.add(key);
    try { await action(); }
    catch(error) { actions.error(error); }
    finally { state.pending.delete(key); }
  }
  const BookShelf = {
    name:'BookShelf',
    setup() {
      return () => state.books.length ? state.books.map(book => {
        const title = titleOf(book);
        const busy = state.pending.has(book.id);
        return h('div', {key:book.id, class:['book-row', {selected:state.selectedId === book.id}]}, [
          h('button', {class:'book-item', 'data-book':book.id, disabled:busy,
            onClick:() => run(book.id, () => actions.select(book.id))}, [
            h('span', {class:'mini-book'}),
            h('span', [h('strong', title), h('small', [
              book.pinned ? h('span', {class:'pin-mark'}, '置顶 · ') : null,
              book.error || `${book.chapters} / ${book.metadata.target_chapters} 章`
            ])])
          ]),
          h('details', {class:'book-menu'}, [
            h('summary', {'aria-label':`管理《${title}》`, title:'管理作品'}, '⋯'),
            h('div', {class:'book-menu-options'}, [
              h('button', {type:'button', 'data-pin':book.id, disabled:busy,
                onClick:event => { event.currentTarget.closest('details').open = false; run(book.id, () => actions.pin(book)); }},
                book.pinned ? '取消置顶' : '置顶'),
              h('button', {type:'button', class:'danger-text', 'data-delete':book.id, disabled:busy,
                onClick:event => { event.currentTarget.closest('details').open = false; actions.remove(book); }}, '删除作品')
            ])
          ])
        ]);
      }) : h('p', {class:'empty-library'}, ['书架还是空的。', h('br'), '为第一个故事留个位置吧。']);
    }
  };
  const TrashList = {
    name:'TrashList',
    setup() {
      return () => state.trash.length ? state.trash.map(book => {
        const date = new Date(book.deleted_at);
        const when = Number.isNaN(date.getTime()) ? '删除时间未记录' : date.toLocaleString('zh-CN', {timeZone:'Asia/Shanghai', hour12:false});
        const busy = state.pending.has(book.restore_token);
        return h('div', {key:book.restore_token, class:'trash-book'}, [
          h('div', [h('strong', book.title), h('small', `移入时间：${when}`)]),
          h('div', {class:'trash-book-actions'}, [
            h('button', {class:'outline', type:'button', 'data-restore':book.restore_token, disabled:busy,
              onClick:() => run(book.restore_token, () => actions.restore(book))}, busy ? '正在恢复…' : '恢复到书架'),
            h('button', {class:'purge-button', type:'button', 'data-purge':book.restore_token, disabled:busy,
              onClick:() => actions.purge(book)}, '彻底删除')
          ])
        ]);
      }) : h('div', {class:'trash-empty'}, [h('span', {'aria-hidden':'true'}, '◇'),
        h('h3', '废案箱还是空的'), h('p', '从书架删除的作品会保存在这里，可随时恢复。')]);
    }
  };
  createApp(BookShelf).mount('#book-list');
  createApp(TrashList).mount('#trash-list');
  createApp({
    name:'WorksCollection',
    setup() {
      return () => state.books.length ? state.books.map(book => h('button', {
        key:book.id, type:'button', class:'work-card', disabled:state.pending.has(book.id),
        onClick:() => run(book.id, () => actions.select(book.id))
      }, [h('span', {class:'work-card-cover', 'aria-hidden':'true'}, 'T'),
        h('span', {class:'work-card-info'}, [h('strong', titleOf(book)),
          h('small', book.error || `${book.chapters} / ${book.metadata.target_chapters} 章`),
          h('span', {class:'work-card-open'}, '继续创作 ↗')])
      ])) : h('div', {class:'works-empty'}, [h('h3', '书架还是空的'), h('p', '创建一部新作品，让故事从这里开始。')]);
    }
  }).mount('#works-grid');
  return state;
};
