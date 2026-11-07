/* AI-assisted interactive prototype. All state is isolated in this browser. */
(() => {
  'use strict';
  const storageKey = 'tome-interactive-prototype-v1';
  const copy = value => JSON.parse(JSON.stringify(value));
  const makeBook = (id, title, prompt, chapters = 6, units = 12000, style = {}) => ({
    metadata: { title, prompt, target_chapters: chapters, target_units: units, model: {model: '原型模拟'} },
    mode: 'longform', style: {instructions: '', reference: '', ...style},
    state: {project_id: id, chapters: [], facts: {}, revision: 0}, job: null,
  });
  function addChapter(book) {
    const number = book.state.chapters.length + 1;
    const titles = ['雨夜来信', '旧城灯火', '渡口的约定', '雾中的钟声', '归途', '黎明之后'];
    const title = titles[(number - 1) % titles.length];
    book.state.chapters.push({number, title, text: `雨落在青石路上，细碎的水声一直延伸到街角。林舟推开旧书店的门，门铃轻轻响了一声。\n柜台上放着一封没有署名的信。信封微微泛黄，封口却很整齐，像是刚刚被人放下。\n“你终于来了。”守店老人合上手中的书，指了指窗外。远处的钟楼亮起一盏灯，光从雨幕中慢慢透出来。\n林舟把信收进口袋，决定沿着河岸走向渡口。他还不知道，这个决定会改变往后的每一个清晨。\n（交互原型示例：第 ${number} 章。这里展示排版与任务流程，未调用模型生成。）`});
    book.state.facts[`fact-${number}`] = {subject: '林舟', value: number === 1 ? '收到一封没有署名的来信。' : `第${number}章沿河岸前往渡口，追寻来信线索。`, status: 'active', revision: number, tier: 'working', kind: 'event', source: {chapter_number: number, quote: '林舟把信收进口袋，决定沿着河岸走向渡口。'}};
    book.state.revision++;
  }
  function seed() {
    const book = makeBook('rain-letter', '雨夜来信', '一封来信，牵出旧城深藏多年的秘密。', 6, 12000, {instructions: '克制、细腻，多用环境细节推进悬念。'});
    addChapter(book); addChapter(book);
    const second = makeBook('star-sea', '星海拾光', '年轻的航行者寻找失落的星图。', 8, 16000);
    return {books: {'rain-letter': book, 'star-sea': second}, trash: {}};
  }
  let data;
  try { const saved = JSON.parse(localStorage.getItem(storageKey)); data = saved?.books && saved?.trash ? saved : seed(); } catch { data = seed(); }
  const jobs = {}, estimates = {};
  const persist = () => {try {localStorage.setItem(storageKey, JSON.stringify(data));} catch {}};
  persist();
  const fail = message => {throw new Error(message);};
  const getBook = id => data.books[id] || fail('作品不存在，请返回书架。');
  const bookSummary = ([id, book]) => ({id, metadata: book.metadata, chapters: book.state.chapters.length, pinned: !!book.pinned});
  const response = (value, status = 200) => ({ok: status < 400, status, json: async () => copy(value)});

  // This adapter never delegates to native fetch: API calls stay in memory.
  window.fetch = async (path, options = {}) => {
    try {
      const payload = options.body ? JSON.parse(options.body) : undefined;
      if (path === '/api/config') return response({configured: true, model: '交互原型 · 模拟生成'});
      if (path === '/api/books/trash') return response({books: Object.entries(data.trash).map(([token, item]) => ({restore_token: token, title: item.book.metadata.title, deleted_at: item.deleted_at}))});
      if (path === '/api/books/restore') {
        const item = data.trash[payload.restore_token] || fail('废案不存在');
        data.books[item.book.state.project_id] = item.book;
        delete data.trash[payload.restore_token]; persist(); return response(item.book);
      }
      if (path === '/api/books/trash/purge') {
        const item = data.trash[payload.restore_token] || fail('废案不存在');
        if (!payload.confirmed || payload.confirmation_title !== item.book.metadata.title) fail('请输入完整作品名称并确认。');
        delete data.trash[payload.restore_token]; persist(); return response({purged: true});
      }
      if (path === '/api/books') {
        if (!payload) return response({books: Object.entries(data.books).map(bookSummary).sort((a,b) => Number(b.pinned) - Number(a.pinned))});
        if (!payload.title?.trim() || !payload.prompt?.trim()) fail('请填写作品名称和故事构想。');
        const id = 'prototype-' + Date.now().toString(36);
        const book = makeBook(id, payload.title.trim(), payload.prompt, payload.chapters, payload.target_units, payload.style);
        data.books[id] = book; persist(); return response(book);
      }
      if (path.startsWith('/api/jobs/')) return response(jobs[path.split('/').pop()] || fail('任务不存在'));
      const match = /^\/api\/books\/([^/]+)(?:\/(\w+))?$/.exec(path);
      if (!match) fail('原型暂未提供该交互。');
      const id = decodeURIComponent(match[1]), action = match[2], book = getBook(id);
      if (!action) return response(book);
      if (action === 'style') {book.style = copy(payload); persist(); return response({style: book.style});}
      if (action === 'pin') {book.pinned = !!payload.pinned; persist(); return response({pinned: book.pinned});}
      if (action === 'delete') {
        if (book.job?.status === 'running') fail('请等待本批次完成。');
        if (!payload.confirmed) fail('请确认删除。');
        data.trash[id] = {book, deleted_at: new Date().toISOString()}; delete data.books[id]; persist(); return response({deleted: true});
      }
      if (action === 'estimate') {
        const remaining = book.metadata.target_chapters - book.state.chapters.length;
        const count = Number(payload.count);
        if (!Number.isInteger(count) || count < 1 || count > remaining || (count > 1 && (!book.state.chapters.length || !payload.approved_first))) fail('请先确认第一章并选择有效章节数。');
        const input = 6500 * count, output = 2200 * count;
        const estimate_id = 'estimate-' + Date.now();
        const estimate = {estimate_id, book_id: id, count, first_chapter: book.state.chapters.length + 1, last_chapter: book.state.chapters.length + count, input_tokens: input, output_tokens: output, total_tokens: input + output, basis: '原型固定样例估算，用于展示确认流程。', prices: {input: 2, output: 3}, estimated_cost_cny: (input * 2 + output * 3) / 1000000, peak_cost_cny: null, pricing: {label: '演示价格（非实时官价）', model: '原型模拟', rule: '仅展示费用信息结构；不代表实际模型报价。', source: 'https://api-docs.deepseek.com/zh-cn/quick_start/pricing/', checked_at: '原型样例', status: 'live', period: 'peak', warning: '本原型不调用模型，不产生任何费用。'}, note: '点击继续仅模拟生成过程。正式产品以实际官方计费为准。'};
        estimates[estimate_id] = estimate; return response(estimate);
      }
      if (action === 'generate') {
        const estimate = estimates[payload.estimate_id];
        if (!payload.confirmed || !estimate || estimate.book_id !== id) fail('请先预估并确认。');
        if (book.job?.status === 'running') fail('已有任务正在生成。');
        if (estimate.first_chapter !== book.state.chapters.length + 1) fail('章节已更新，请重新预估。');
        delete estimates[payload.estimate_id];
        const job_id = 'job-' + Date.now();
        const job = {job_id, status: 'running', count: estimate.count, completed: 0, current_chapter: estimate.first_chapter};
        jobs[job_id] = job; book.job = job;
        const tick = () => {
          addChapter(book); job.completed++; job.current_chapter = book.state.chapters.length;
          if (job.completed === job.count) job.status = 'completed';
          else {job.current_chapter++; setTimeout(tick, 800);}
          persist();
        };
        setTimeout(tick, 800); return response({job_id});
      }
      fail('原型暂未提供该交互。');
    } catch (error) {return response({error: error.message}, 400);}
  };
  // On a reload, retain completed chapters and allow an interrupted simulation to retry.
  for (const book of Object.values(data.books)) if (book.job?.status === 'running') book.job = null;
  document.addEventListener('click', event => {
    const target = event.target.closest('a');
    if (target?.id !== 'export') return;
    event.preventDefault();
    const match = /\/books\/([^/]+)\/export/.exec(target.getAttribute('href'));
    const book = match && data.books[decodeURIComponent(match[1])];
    if (!book) return;
    const content = '# ' + book.metadata.title + '\n\n' + book.state.chapters.map(c => `## 第${c.number}章 ${c.title}\n\n` + c.text.split('\n').map(p => '　　' + p.trim()).join('\n\n')).join('\n\n');
    const url = URL.createObjectURL(new Blob([content], {type: 'text/markdown;charset=utf-8'}));
    const link = document.createElement('a'); link.href = url; link.download = book.metadata.title + '.md'; link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  }, true);
  document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('prototype-reset').addEventListener('click', () => {
      if (confirm('重置本浏览器中的原型示例？仅清除原型数据。')) {localStorage.removeItem(storageKey); location.reload();}
    });
  });
})();
