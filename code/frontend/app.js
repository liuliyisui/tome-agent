const $ = (id) => document.getElementById(id);
let books = [], current = null, selectedChapter = 0;
const jobs = new Map();
const pollingJobs = new Set();
const jobErrors = new Map();
const styleDrafts = new Map();
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
  $('book-list').innerHTML = books.length ? books.map(book => `<button class="book-item ${current?.state.project_id === book.id ? 'selected' : ''}" data-book="${esc(book.id)}"><span class="mini-book"></span><span><strong>${esc(book.metadata?.title || book.id)}</strong><small>${book.error ? esc(book.error) : `${book.chapters} / ${book.metadata.target_chapters} 章 · ${book.metadata.model.model === 'offline-demo' ? '离线演示' : '创作中'}`}</small></span></button>`).join('') : '<p class="empty-library">书架还是空的。<br>为第一个故事留个位置吧。</p>';
  document.querySelectorAll('[data-book]').forEach(button => button.onclick = () => selectBook(button.dataset.book).catch(e => notice(e.message)));
}
async function selectBook(id, latest = false) {
  const book = await api(`/api/books/${encodeURIComponent(id)}`);
  selectedChapter = latest ? Math.max(0, book.state.chapters.length - 1) : (current?.state.project_id === id ? selectedChapter : 0);
  current = book;
  renderStyle();
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
  const demo = meta.model.model === 'offline-demo';
  $('welcome').hidden = true;
  $('book-workspace').hidden = false;
  $('breadcrumb-title').textContent = meta.title;
  $('book-kind').textContent = demo ? 'OFFLINE DEMO / 离线样本' : current.mode === 'legacy' ? 'LEGACY / 旧版存档' : 'EVENT FIRST / 事件先行 · 三层记忆';
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
  $('generation-description').textContent = demo ? '固定两章的旧版四角色流程演示，不联网，不消耗额度。样本篇幅不代表实际生成长度。' : current.mode === 'legacy' ? '旧版正文可阅读和导出。请新建作品使用新版引擎，保留旧存档。' : `使用 ${meta.model.model}，先规划事件，再生成正文并维护三层记忆。每次生成一章，可能需要数分钟；已保存正文仍需人工检查。`;
  $('facts').innerHTML = facts.length ? facts.map(f => `<div class="fact"><strong>${esc(f.subject)} · ${esc(f.attribute === 'eye_color' ? '眼睛颜色' : f.attribute)}</strong><p>${esc(typeof f.value === 'object' ? JSON.stringify(f.value) : f.value)}</p><small>第 ${f.source.chapter_number} 章 · 版本 ${f.revision}</small><blockquote>${esc(f.source.quote)}</blockquote></div>`).join('') : '<p class="empty-facts">章节生成后，人物事实将在这里留存。</p>';
  $('chapter-tabs').innerHTML = state.chapters.map((c,i) => `<button data-chapter="${i}" class="${i === selectedChapter ? 'active' : ''}" aria-pressed="${i === selectedChapter}">第 ${c.number} 章</button>`).join('');
  document.querySelectorAll('[data-chapter]').forEach(button => button.onclick = () => { selectedChapter = Number(button.dataset.chapter); renderBook(); });
  const chapter = state.chapters[selectedChapter];
  const paragraphs = chapter ? chapter.text.split(/\r\n|[\n\r\u2028\u2029]/).map(p => p.trim()).filter(Boolean) : [];
  $('chapter-body').innerHTML = chapter ? `<h3>第${chapter.number}章 · ${esc(chapter.title)}</h3>${paragraphs.map(p => `<p class="prose-paragraph">${esc(p)}</p>`).join('')}` : '<div class="chapter-empty"><span>✧</span><h3>故事，正待落笔。</h3><p>点击「生成下一章」，让你的构想变成正文。</p></div>';
  renderGeneration();
}
function renderGeneration() {
  if (!current) return;
  const running = jobs.has(current.state.project_id);
  const complete = current.state.chapters.length >= current.metadata.target_chapters;
  const legacy = current.mode === 'legacy';
  $('generate').disabled = running || complete || legacy;
  $('style-save').disabled = running;
  $('style-instructions').disabled = running;
  $('style-reference').disabled = running;
  $('generate').textContent = running ? '◌ 正在创作…' : legacy ? '旧版存档 · 仅供阅读' : complete ? '✓ 全书章节已完成' : '✧ 生成下一章';
  const error = jobErrors.get(current.state.project_id);
  $('job-status').classList.toggle('error', Boolean(error));
  $('job-status').textContent = running ? error || '已提交，正在生成。通常需要数十秒至数分钟；可刷新页面，完成后会自动显示正文。' : error ? `生成失败：${error}` : complete ? '所有目标章节已存档，可导出作品。' : current.job?.status === 'completed' ? '✓ 上一章已生成并存档。' : '';
}
function renderStyle() {
  const id = current.state.project_id;
  const style = styleDrafts.get(id) || current.style || {instructions:'',reference:''};
  $('style-instructions').value = style.instructions;
  $('style-reference').value = style.reference;
  $('style-status').classList.remove('error');
  $('style-status').textContent = current.mode === 'demo' ? '离线演示使用固定正文；文风设定仅对真实创作生效。' : styleDrafts.has(id) ? '有未保存的修改；生成下一章时会先自动保存。' : style.instructions || style.reference ? '已保存 · 从下一章生效。' : '尚未设置，使用默认文风。';
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
      if (current.mode !== 'demo' && !result.style.instructions && !result.style.reference) {
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
$('demo').onclick = async () => {
  $('demo').disabled = true;
  try { const book = await api('/api/demo', {}); await selectBook(book.state.project_id); }
  catch(e) { notice(e.message); }
  finally { $('demo').disabled = false; }
};
$('generate').onclick = async () => {
  const id = current.state.project_id;
  jobErrors.delete(id);
  jobs.set(id, null); renderGeneration(); notice();
  try {
    if (styleDrafts.has(id)) await saveStyle(id);
    const {job_id} = await api(`/api/books/${encodeURIComponent(id)}/generate`, {});
    jobs.set(id, job_id);
    startPolling(id, job_id);
  } catch(e) { jobs.delete(id); jobErrors.set(id,e.message); renderGeneration(); notice(e.message); }
};
function startPolling(id, jobId) {
  if (pollingJobs.has(jobId)) return;
  pollingJobs.add(jobId);
  pollJob(id, jobId);
}
async function pollJob(id, jobId) {
  try {
    const job = await api(`/api/jobs/${jobId}`);
    jobErrors.delete(id);
    if (job.status === 'running') { renderGeneration(); setTimeout(() => pollJob(id,jobId), 1500); return; }
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
