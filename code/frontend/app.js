const $ = (id) => document.getElementById(id);
let books = [], current = null, selectedChapter = 0;
const jobs = new Map();
const pollingJobs = new Set();
const jobErrors = new Map();
const styleDrafts = new Map();
const batchChoices = new Map();
let pendingEstimate = null;
let preparing = false;
let pendingDelete = null;
let lastDeleted = null;
const factSelections = new Map();
const esc = (value) => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function api(path, data) {
  const response = await fetch(path, data === undefined ? {} : {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
  const result = await response.json();
  if (!response.ok) {
    const error = new Error(result.error || '操作失败');
    error.status = response.status;
    throw error;
  }
  return result;
}
function notice(message = '') {
  $('notice').textContent = message;
  $('notice').hidden = !message;
  if (message) $('notice').scrollIntoView({behavior:'smooth',block:'center'});
}
function openCreate() { $('form-error').textContent = ''; $('create-dialog').showModal(); }
$('new-book').onclick = $('welcome-create').onclick = openCreate;
$('close-dialog').onclick = () => $('create-dialog').close();
async function refreshBooks() {
  books = (await api('/api/books')).books;
  $('book-count').textContent = books.length;
  $('book-list').innerHTML = books.length ? books.map(book => {
    const title = book.metadata?.title || book.id;
    return `<div class="book-row ${current?.state.project_id === book.id ? 'selected' : ''}"><button class="book-item" data-book="${esc(book.id)}"><span class="mini-book"></span><span><strong>${esc(title)}</strong><small>${book.pinned ? '<span class="pin-mark">置顶 · </span>' : ''}${book.error ? esc(book.error) : `${book.chapters} / ${book.metadata.target_chapters} 章`}</small></span></button><details class="book-menu"><summary aria-label="管理《${esc(title)}》" title="管理作品">⋯</summary><div class="book-menu-options"><button type="button" data-pin="${esc(book.id)}" data-pinned="${!book.pinned}">${book.pinned ? '取消置顶' : '置顶'}</button><button type="button" class="danger-text" data-delete="${esc(book.id)}">删除作品</button></div></details></div>`;
  }).join('') : '<p class="empty-library">书架还是空的。<br>为第一个故事留个位置吧。</p>';
  document.querySelectorAll('[data-book]').forEach(button => button.onclick = () => selectBook(button.dataset.book).catch(e => notice(e.message)));
  document.querySelectorAll('[data-pin]').forEach(button => button.onclick = async () => {
    button.disabled = true;
    try { await api(`/api/books/${encodeURIComponent(button.dataset.pin)}/pin`, {pinned:button.dataset.pinned === 'true'}); await refreshBooks(); }
    catch(e) { notice(e.message); button.disabled = false; }
  });
  document.querySelectorAll('[data-delete]').forEach(button => button.onclick = () => {
    pendingDelete = books.find(book => book.id === button.dataset.delete);
    button.closest('details').open = false;
    $('delete-book-title').textContent = `《${pendingDelete.metadata?.title || pendingDelete.id}》`;
    $('delete-error').textContent = '';
    $('delete-dialog').showModal();
  });
}
document.addEventListener('click', event => {
  if (!event.target.closest('.book-menu')) document.querySelectorAll('.book-menu[open]').forEach(menu => menu.open = false);
});
$('delete-cancel').onclick = () => { $('delete-dialog').close(); pendingDelete = null; };
$('delete-dialog').oncancel = () => { pendingDelete = null; };
$('delete-confirm').onclick = async () => {
  if (!pendingDelete) return;
  const book = pendingDelete;
  $('delete-confirm').disabled = true;
  try {
    const result = await api(`/api/books/${encodeURIComponent(book.id)}/delete`, {confirmed:true});
    lastDeleted = {token:result.restore_token,title:book.metadata?.title || book.id};
    localStorage.setItem('tome-last-deleted',JSON.stringify(lastDeleted));
    styleDrafts.delete(book.id); batchChoices.delete(book.id); factSelections.delete(book.id); jobErrors.delete(book.id);
    if (current?.state.project_id === book.id) {
      current = null; selectedChapter = 0; localStorage.removeItem('tome-selected-book');
      $('book-workspace').hidden = true; $('welcome').hidden = false; $('breadcrumb-title').textContent = '创作空间';
    }
    $('delete-dialog').close(); pendingDelete = null;
    await refreshBooks();
    if (!current) { const next = books.find(item => !item.error); if (next) await selectBook(next.id); }
    $('undo-delete-message').textContent = `已从书架删除《${lastDeleted.title}》。`;
    $('undo-delete-panel').hidden = false;
  } catch(e) { $('delete-error').textContent = e.message; }
  finally { $('delete-confirm').disabled = false; }
};
$('undo-delete').onclick = async () => {
  if (!lastDeleted) return;
  $('undo-delete').disabled = true;
  try {
    const book = await api('/api/books/restore', {restore_token:lastDeleted.token});
    await selectBook(book.state.project_id);
    $('undo-delete-panel').hidden = true; lastDeleted = null;
    localStorage.removeItem('tome-last-deleted');
  } catch(e) { notice(e.message); }
  finally { $('undo-delete').disabled = false; }
};
async function selectBook(id, latest = false) {
  const book = await api(`/api/books/${encodeURIComponent(id)}`);
  selectedChapter = latest ? Math.max(0, book.state.chapters.length - 1) : (current?.state.project_id === id ? selectedChapter : 0);
  current = book;
  renderStyle();
  renderBatch();
  if (book.job?.status === 'running') {
    jobs.set(id, book.job.job_id);
    jobErrors.delete(id);
    startPolling(id, book.job.job_id);
  } else {
    jobs.delete(id);
    if (book.job?.status === 'failed') jobErrors.set(id, book.job.error);
    else jobErrors.delete(id);
  }
  localStorage.setItem('tome-selected-book', id);
  notice();
  renderBook();
  await refreshBooks();
}
function renderBook() {
  if (!current) return;
  const {metadata:meta,state} = current;
  $('welcome').hidden = true;
  $('book-workspace').hidden = false;
  $('breadcrumb-title').textContent = meta.title;
  $('book-kind').textContent = current.mode === 'legacy' ? 'LEGACY / 旧版存档' : 'EVENT FIRST / 事件先行 · 三层记忆';
  $('book-title').textContent = meta.title;
  $('book-prompt').textContent = meta.prompt;
  $('stat-chapters').textContent = `${state.chapters.length} / ${meta.target_chapters}`;
  const units = state.chapters.reduce((n,c) => n + (c.text.match(/[\u3400-\u9fff]|[A-Za-z0-9]+/g) || []).length, 0);
  $('stat-units').textContent = units.toLocaleString();
  const facts = Object.values(state.facts).filter(f => f.status === 'active');
  $('stat-facts').textContent = facts.length;
  $('stat-progress').textContent = Math.round(state.chapters.length / meta.target_chapters * 100) + '%';
  $('revision').textContent = `存档版本 ${state.revision}`;
  $('export').href = `/api/books/${encodeURIComponent(state.project_id)}/export`;
  $('generation-description').textContent = current.mode === 'legacy' ? '旧版正文可阅读和导出。请新建作品使用新版引擎，保留旧存档。' : `使用 ${meta.model.model}，先规划事件，再生成正文并维护三层记忆。每次生成一章，可能需要数分钟；已保存正文仍需人工检查。`;
  renderFacts(facts);
  $('chapter-tabs').innerHTML = state.chapters.map((c,i) => `<button data-chapter="${i}" class="${i === selectedChapter ? 'active' : ''}" aria-pressed="${i === selectedChapter}">第 ${c.number} 章</button>`).join('');
  document.querySelectorAll('[data-chapter]').forEach(button => button.onclick = () => { selectedChapter = Number(button.dataset.chapter); renderBook(); });
  const chapter = state.chapters[selectedChapter];
  const paragraphs = chapter ? chapter.text.split(/\r\n|[\n\r\u2028\u2029]/).map(p => p.trim()).filter(Boolean) : [];
  $('chapter-body').innerHTML = chapter ? `<h3>第${chapter.number}章 · ${esc(chapter.title)}</h3>${paragraphs.map(p => `<p class="prose-paragraph">${esc(p)}</p>`).join('')}` : '<div class="chapter-empty"><span>✧</span><h3>故事，正待落笔。</h3><p>点击「生成下一章」，让你的构想变成正文。</p></div>';
  renderGeneration();
}
function concise(value, limit = 18) {
  const text = String(value ?? '').replace(/\s+/g,' ').replace(/^[“”「」『』"'\s]+/g,'').trim();
  const first = text.split(/[。！？；\n]/)[0] || text;
  return Array.from(first).length > limit ? Array.from(first).slice(0,limit).join('') + '…' : first;
}
function renderFacts(facts) {
  const groups = new Map();
  const valueOf = fact => typeof fact.value === 'object' ? JSON.stringify(fact.value) : String(fact.value ?? '');
  facts.forEach(fact => {
    const excerpt = fact.kind === 'prose_excerpt' || String(fact.subject).startsWith('prose:');
    const number = fact.source?.chapter_number;
    const chapter = current.state.chapters.find(ch => ch.number === number);
    const key = excerpt ? `chapter:${number}` : `subject:${fact.subject}`;
    const label = excerpt ? `第${number}章 · ${concise(chapter?.title || valueOf(fact),12)}` : concise(fact.subject,12);
    if (!groups.has(key)) groups.set(key,{key,label,facts:[],number:excerpt ? Number(number) || 0 : null});
    groups.get(key).facts.push(fact);
  });
  const items = [...groups.values()].sort((a,b) => a.number !== null && b.number !== null ? b.number-a.number : a.number === null ? b.number === null ? a.label.localeCompare(b.label,'zh-CN') : -1 : 1);
  const preferred = factSelections.get(current.state.project_id) || `chapter:${selectedChapter+1}`;
  $('fact-topic').innerHTML = items.length ? items.map(group => `<option value="${esc(group.key)}">${esc(group.label)}（${group.facts.length}）</option>`).join('') : '<option value="">暂无事实主题</option>';
  $('fact-topic').disabled = !items.length;
  $('fact-topic').value = groups.has(preferred) ? preferred : items[0]?.key || '';
  $('fact-topic-summary').textContent = items.length ? `${items.length} 个主题 · ${facts.length} 条记忆，选择标题查看。` : '生成章节后，将自动整理事实主题。';
  function showGroup() {
    const group = groups.get($('fact-topic').value);
    if (!group) { $('facts').innerHTML = '<p class="empty-facts">暂时没有可查看的事实记忆。</p>'; return; }
    factSelections.set(current.state.project_id,group.key);
    const tiers = {working:'工作记忆',recent:'近期记忆',long:'长期记忆'};
    $('facts').innerHTML = group.facts.map(fact => {
      const value = valueOf(fact), quote = fact.source?.quote || '';
      const excerpt = fact.kind === 'prose_excerpt' || String(fact.subject).startsWith('prose:');
      const title = excerpt ? concise(value,20) : `${concise(fact.subject,10)} · ${concise(value,14)}`;
      return `<div class="fact">${excerpt ? '' : `<h4>${esc(title)}</h4>`}<p>${esc(value)}</p><small>第 ${esc(fact.source?.chapter_number || '—')} 章 · 版本 ${esc(fact.revision)}${fact.tier ? ' · ' + esc(tiers[fact.tier] || fact.tier) : ''}</small>${quote && quote !== value ? `<details class="fact-source"><summary>查看正文依据</summary><blockquote>${esc(quote)}</blockquote></details>` : ''}</div>`;
    }).join('');
  }
  $('fact-topic').onchange = showGroup;
  showGroup();
}
function renderGeneration() {
  if (!current) return;
  const running = jobs.has(current.state.project_id);
  const complete = current.state.chapters.length >= current.metadata.target_chapters;
  const legacy = current.mode === 'legacy';
  $('generate').disabled = running || complete || legacy || preparing;
  $('approve-first').disabled = running || !current.state.chapters.length || complete;
  $('generation-count').disabled = running || !batchChoices.get(current.state.project_id)?.approved || complete;
  $('style-save').disabled = running;
  $('style-instructions').disabled = running;
  $('style-reference').disabled = running;
  const chosen = Number($('generation-count').value) || 1;
  $('generate').textContent = running ? '◌ 正在创作…' : preparing ? '正在估算…' : legacy ? '旧版存档 · 仅供阅读' : complete ? '✓ 全书章节已完成' : chosen > 1 ? `预估并生成 ${chosen} 章` : '预估并生成下一章';
  const error = jobErrors.get(current.state.project_id);
  $('job-status').classList.toggle('error', Boolean(error));
  const progress = current.job?.count ? `本批次已完成 ${current.job.completed || 0} / ${current.job.count} 章，正在生成第 ${current.job.current_chapter} 章。` : '已提交，正在生成。';
  $('job-status').textContent = running ? error || `${progress}可刷新页面，完成后自动显示正文。` : error ? `生成停止：${error}。已保存章节仍可阅读和导出。` : complete ? '所有目标章节已存档，可导出作品。' : current.job?.status === 'completed' ? `✓ 本批次 ${current.job.count || 1} 章已生成并存档。` : '';
}
function renderBatch() {
  const remaining = Math.max(0, current.metadata.target_chapters - current.state.chapters.length);
  const choice = batchChoices.get(current.state.project_id) || {approved:false,count:1};
  $('approve-first').checked = choice.approved;
  $('generation-count').max = Math.max(1,remaining);
  $('generation-count').value = Math.max(1,Math.min(choice.count,remaining));
  $('batch-hint').textContent = !current.state.chapters.length ? '先生成第一章，阅读确认后再自动续写。' : `剩余 ${remaining} 章。确认首章后自动填入剩余章节数，可修改；提交前会显示用量和费用预估。`;
}
$('approve-first').onchange = () => {
  batchChoices.set(current.state.project_id, {approved:$('approve-first').checked,count:$('approve-first').checked ? Math.max(1,current.metadata.target_chapters-current.state.chapters.length) : 1});
  renderBatch(); renderGeneration();
};
$('generation-count').oninput = () => {
  batchChoices.set(current.state.project_id, {approved:$('approve-first').checked,count:Number($('generation-count').value)});
  renderGeneration();
};
function renderStyle() {
  const id = current.state.project_id;
  const style = styleDrafts.get(id) || current.style || {instructions:'',reference:''};
  $('style-instructions').value = style.instructions;
  $('style-reference').value = style.reference;
  $('style-status').classList.remove('error');
  $('style-status').textContent = styleDrafts.has(id) ? '有未保存的修改；生成下一章时会先自动保存。' : style.instructions || style.reference ? '已保存 · 从下一章生效。' : '尚未设置，使用默认文风。';
}
function editStyle() {
  if (!current) return;
  styleDrafts.set(current.state.project_id, {instructions:$('style-instructions').value, reference:$('style-reference').value});
  $('style-status').classList.remove('error');
  $('style-status').textContent = '有未保存的修改；生成下一章时会先自动保存。';
}
$('style-instructions').oninput = $('style-reference').oninput = editStyle;
async function saveStyle(id) {
  const style = styleDrafts.get(id) || current.style || {instructions:'',reference:''};
  $('style-save').disabled = true;
  $('style-instructions').disabled = true;
  $('style-reference').disabled = true;
  $('style-status').textContent = '正在保存…';
  try {
    const result = await api(`/api/books/${encodeURIComponent(id)}/style`, style);
    styleDrafts.delete(id);
    if (current?.state.project_id === id) {
      current.style = result.style;
      renderStyle();
      if (!result.style.instructions && !result.style.reference) {
        $('style-status').textContent = '已保存 · 使用默认文风。';
      }
    }
  } catch(e) {
    $('style-status').classList.add('error');
    $('style-status').textContent = `保存失败：${e.message}`;
    throw e;
  } finally { renderGeneration(); }
}
$('style-form').onsubmit = async event => {
  event.preventDefault();
  try { await saveStyle(current.state.project_id); }
  catch(e) { /* The form retains the draft and displays the error beside Save. */ }
};
$('create-form').onsubmit = async event => {
  event.preventDefault();
  const form = new FormData(event.target);
  $('create-submit').disabled = true;
  $('form-error').textContent = '';
  try {
    const book = await api('/api/books', {title:form.get('title'),prompt:form.get('prompt'),chapters:Number(form.get('chapters')),target_units:Number(form.get('target_units')),style:{instructions:form.get('style_instructions'),reference:form.get('style_reference')}});
    $('create-dialog').close(); event.target.reset();
    await selectBook(book.state.project_id);
  } catch(e) { $('form-error').textContent = e.message; }
  finally { $('create-submit').disabled = false; }
};
$('generate').onclick = async () => {
  const id = current.state.project_id;
  preparing = true; renderGeneration(); notice();
  try {
    if (styleDrafts.has(id)) await saveStyle(id);
    const estimate = await api(`/api/books/${encodeURIComponent(id)}/estimate`, {count:Number($('generation-count').value),approved_first:$('approve-first').checked});
    pendingEstimate = estimate;
    showEstimate(estimate);
    $('estimate-error').textContent = '';
    $('estimate-continue').disabled = false;
    $('estimate-dialog').showModal();
  } catch(e) { notice(e.message); }
  finally { preparing = false; renderGeneration(); }
};
function showEstimate(estimate) {
  $('estimate-scope').textContent = `《${current.metadata.title}》· 第 ${estimate.first_chapter} 至 ${estimate.last_chapter} 章，共 ${estimate.count} 章`;
  $('estimate-input').textContent = estimate.input_tokens.toLocaleString();
  $('estimate-output').textContent = estimate.output_tokens.toLocaleString();
  $('estimate-total').textContent = '≈ ' + estimate.total_tokens.toLocaleString();
  $('estimate-basis').textContent = estimate.basis;
  $('estimate-cost').textContent = estimate.estimated_cost_cny === null ? '该模型暂无法自动匹配官方价格' : `≈ ¥ ${estimate.estimated_cost_cny.toFixed(4)}`;
  $('estimate-input-price').textContent = estimate.prices ? `¥ ${estimate.prices.input} / 百万 token` : '未匹配';
  $('estimate-output-price').textContent = estimate.prices ? `¥ ${estimate.prices.output} / 百万 token` : '未匹配';
  $('estimate-period').textContent = `${estimate.pricing.label} · ${estimate.pricing.model}`;
  $('estimate-price-rule').textContent = estimate.pricing.rule;
  $('estimate-price-source').href = estimate.pricing.source;
  $('estimate-price-date').textContent = `核验：${estimate.pricing.checked_at} ${estimate.pricing.status === 'live' ? '· 官方实时同步' : '· 已核验缓存价，联网不可用时使用'}`;
  $('estimate-price-warning').textContent = estimate.pricing.warning;
  $('estimate-price-warning').hidden = !estimate.pricing.warning;
  $('estimate-peak-cost').textContent = estimate.peak_cost_cny !== null && estimate.pricing.period === 'off_peak' ? `若按高峰价计：约 ¥ ${estimate.peak_cost_cny.toFixed(4)}` : '';
  $('estimate-note').textContent = estimate.note;
}
$('estimate-close').onclick = $('estimate-cancel').onclick = () => { $('estimate-dialog').close(); pendingEstimate = null; };
$('estimate-dialog').oncancel = () => { pendingEstimate = null; };
$('estimate-continue').onclick = async () => {
  if (!pendingEstimate) return;
  const estimate = pendingEstimate, id = estimate.book_id;
  $('estimate-continue').disabled = true;
  try {
    const {job_id} = await api(`/api/books/${encodeURIComponent(id)}/generate`, {estimate_id:estimate.estimate_id,confirmed:true});
    jobs.set(id,job_id); jobErrors.delete(id);
    current.job = {count:estimate.count,completed:0,current_chapter:estimate.first_chapter};
    $('estimate-dialog').close(); pendingEstimate = null;
    renderGeneration(); startPolling(id,job_id);
  } catch(e) { $('estimate-error').textContent = e.message; }
  finally { $('estimate-continue').disabled = false; }
};
function startPolling(id, jobId) {
  if (pollingJobs.has(jobId)) return;
  pollingJobs.add(jobId);
  pollJob(id, jobId);
}
async function pollJob(id, jobId) {
  try {
    const job = await api(`/api/jobs/${jobId}`);
    if (current?.state.project_id === id) current.job = job;
    jobErrors.delete(id);
    if (job.status === 'running') {
      if (current?.state.project_id === id && current.state.chapters.length < (job.current_chapter || 1) - 1) await selectBook(id,true);
      renderGeneration(); setTimeout(() => pollJob(id,jobId), 1500); return;
    }
    pollingJobs.delete(jobId);
    jobs.delete(id);
    if (current?.state.project_id === id) await selectBook(id, true);
    else await refreshBooks();
    if (job.status === 'failed') notice(job.error);
  } catch(e) {
    if (e.status === 404) {
      pollingJobs.delete(jobId);
      jobs.delete(id);
      try { if (current?.state.project_id === id) await selectBook(id,true); }
      catch(refreshError) { notice(refreshError.message); }
      notice('任务状态已失效，已重新读取作品存档。请确认正文后再提交。');
      return;
    }
    if (pollingJobs.has(jobId)) {
      jobErrors.set(id, '状态连接暂时中断，正在重连；请勿重复提交。');
      renderGeneration();
      setTimeout(() => pollJob(id,jobId), 3000);
    }
  }
}
async function init() {
  try {
    try { lastDeleted = JSON.parse(localStorage.getItem('tome-last-deleted') || 'null'); }
    catch(e) { localStorage.removeItem('tome-last-deleted'); }
    if (lastDeleted?.token && lastDeleted?.title) {
      $('undo-delete-message').textContent = `已从书架删除《${lastDeleted.title}》。`;
      $('undo-delete-panel').hidden = false;
    }
    const cfg = await api('/api/config');
    $('connection-text').textContent = cfg.configured ? `${cfg.model} 已就绪` : '引擎已连接 · 离线可用';
    $('connection-dot').classList.add('ready');
    await refreshBooks();
    const saved = localStorage.getItem('tome-selected-book');
    const first = books.find(b => !b.error && b.id === saved) || books.find(b => !b.error);
    if (first) await selectBook(first.id);
  } catch(e) { $('connection-text').textContent = '连接失败'; notice(e.message); }
}
init();
