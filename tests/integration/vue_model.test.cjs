/* Exercise the real Vue reactive model without a browser or paid model calls. */
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const frontend = path.resolve(__dirname, "../../code/frontend");
const clone = (value) => JSON.parse(JSON.stringify(value));
const flush = () => new Promise((resolve) => setImmediate(resolve));

async function fixture({ configured = true, theme = null, darkSystem = false, blockStorage = false } = {}) {
  const calls = [],
    timers = [],
    mounted = [],
    beforeUnmount = [];
  const book = (id) => ({
    metadata: {
      title: id,
      target_chapters: 4,
      prompt: "测试",
      model: { model: "test" },
    },
    mode: "longform",
    style: { instructions: "原文风", reference: "" },
    job: null,
    state: {
      project_id: id,
      chapters: [{ number: 1, title: "首章", text: "正文。" }],
      facts: {},
      revision: 1,
    },
  });
  const books = { a: book("a"), b: book("b") };
  let model,
    gate = null,
    jobStatus = "running";
  const response = (data) => ({ ok: true, json: async () => clone(data) });
  const storage = new Map(theme === null ? [] : [["tome-theme", theme]]);
  const root = { dataset: {} };
  const themeListeners = new Set();
  const media = {
    matches: darkSystem,
    addEventListener: (name, listener) => themeListeners.add(listener),
    removeEventListener: (name, listener) => themeListeners.delete(listener),
  };
  const context = vm.createContext({
    console,
    window: { TomeRender: () => {}, matchMedia: () => media },
    history: {},
    localStorage: {
      getItem(key) { if (blockStorage) throw new Error("Storage unavailable"); return storage.get(key) ?? null; },
      setItem(key, value) { if (blockStorage) throw new Error("Storage unavailable"); storage.set(key, value); },
      removeItem(key) { storage.delete(key); },
    },
    setTimeout: (callback) => {
      timers.push(callback);
      return timers.length;
    },
    clearTimeout() {},
    fetch: async (url, options) => {
      const payload = options?.body ? JSON.parse(options.body) : undefined;
      calls.push({ url, payload });
      if (url === "/api/config") return response({ configured, model: "test" });
      if (url === "/api/books")
        return response({
          books: Object.entries(books).map(([id, b]) => ({
            id,
            metadata: b.metadata,
            chapters: b.state.chapters.length,
          })),
        });
      if (url === "/api/books/trash") return response({ books: [] });
      if (url === "/api/skills") return response({ skills: [] });
      if (url === "/api/jobs/job-1")
        return response({
          status: jobStatus,
          count: 2,
          completed: jobStatus === "completed" ? 2 : 0,
          current_chapter: 2,
        });
      if (url.endsWith("/style")) {
        books[url.split("/")[3]].style = clone(payload);
        return response({ style: payload });
      }
      if (url.endsWith("/estimate"))
        return response({
          book_id: url.split("/")[3],
          estimate_id: "estimate-1",
          count: payload.count,
          first_chapter: 2,
        });
      if (url.endsWith("/generate")) return response({ job_id: "job-1" });
      if (url === "/api/books/trash/purge") return response({ purged: true });
      const id = url.split("/")[3];
      if (gate && id === gate.id) return gate.promise;
      if (books[id]) return response(books[id]);
      throw new Error("Unexpected test request: " + url);
    },
  });
  context.window.scrollTo = () => {};
  vm.runInContext(
    fs.readFileSync(path.join(frontend, "vue.runtime.global.prod.js"), "utf8"),
    context,
  );
  context.document = { documentElement: root };
  context.Vue = {
    ...context.Vue,
    onMounted: (callback) => mounted.push(callback),
    onBeforeUnmount: (callback) => beforeUnmount.push(callback),
    createApp: (component) => ({
      directive() {},
      mount() {
        model = component.setup();
      },
    }),
  };
  vm.runInContext(
    fs.readFileSync(path.join(frontend, "app.js"), "utf8"),
    context,
  );
  for (const callback of mounted) await callback();
  return {
    model,
    calls,
    timers,
    books,
    response,
    root,
    storage,
    themeListeners,
    changeSystemTheme(dark) {
      media.matches = dark;
      themeListeners.forEach((listener) => listener());
    },
    delayBook(id) {
      let resolve;
      const promise = new Promise((r) => {
        resolve = r;
      });
      gate = { id, promise };
      return () => {
        gate = null;
        resolve(response(books[id]));
      };
    },
    finishJob() {
      jobStatus = "completed";
    },
    dispose() {
      beforeUnmount.forEach((callback) => callback());
    },
  };
}

test("first use opens key configuration; home always hides sidebar", async () => {
  const f = await fixture({ configured: false });
  assert.equal(f.model.state.dialogs.api, true);
  assert.equal(f.model.sidebarHidden.value, true);
  f.model.state.apiKey = "test input";
  f.model.closeDialog("api");
  assert.equal(f.model.state.apiKey, "");
  f.dispose();
});
test("late book response cannot replace a more recent library navigation", async () => {
  const f = await fixture(),
    release = f.delayBook("a");
  const request = f.model.selectBook("a");
  f.model.showLibrary();
  release();
  await request;
  assert.equal(f.model.state.view, "library");
  assert.equal(f.model.state.current, null);
  f.dispose();
});
test("unsaved styles survive book switching and save before estimation", async () => {
  const f = await fixture();
  await f.model.selectBook("a");
  f.model.style.value.instructions = "新的草稿";
  await f.model.selectBook("b");
  await f.model.selectBook("a");
  assert.equal(f.model.style.value.instructions, "新的草稿");
  await f.model.prepareGeneration();
  assert.equal(f.books.a.style.instructions, "新的草稿");
  const saved = f.calls.findIndex((c) => c.url.endsWith("/style"));
  assert.ok(saved < f.calls.findIndex((c) => c.url.endsWith("/estimate")));
  assert.equal(f.calls.filter((c) => c.url.endsWith("/generate")).length, 0);
  f.model.closeDialog("estimate");
  assert.equal(f.model.state.estimate, null);
  f.dispose();
});
test("job status reports received prose without claiming it is saved", async () => {
  const f = await fixture();
  await f.model.selectBook("a");
  f.model.state.jobs.a = "job-1";
  f.model.state.current.job = { count: 1, completed: 0, current_chapter: 2, live_units: 123, live_phase: "writing" };
  assert.match(f.model.jobStatus.value, /当前片段已接收约 123 字/);
  assert.match(f.model.jobStatus.value, /尚未存档/);
  f.model.state.current.job.live_draft_units = 1800;
  f.model.state.current.job.live_completed_units = 500;
  f.model.state.current.job.live_unit_number = 2;
  f.model.state.current.job.live_unit_total = 3;
  f.model.state.current.job.live_units = 0;
  assert.match(f.model.jobStatus.value, /本章已完成片段约 500 字/);
  assert.match(f.model.jobStatus.value, /第 2 \/ 3 段草稿约 1,800 字，正在调整，调整内容已接收约 0 字/);
  f.model.state.current.job.live_draft_units = null;
  f.model.state.current.job.live_phase = "processing";
  assert.match(f.model.jobStatus.value, /正在整理/);
  f.dispose();
});
test("approval fills remaining chapters; background completion stays in library", async () => {
  const f = await fixture();
  await f.model.selectBook("a");
  f.model.batch.value.approved = true;
  f.model.approveFirst();
  assert.equal(f.model.batch.value.count, 3);
  f.model.batch.value.count = 2;
  await f.model.prepareGeneration();
  await f.model.confirmGeneration();
  await flush();
  assert.equal(f.calls.filter((c) => c.url.endsWith("/generate")).length, 1);
  assert.equal(f.model.running.value, true);
  f.model.showLibrary();
  f.finishJob();
  await f.timers.shift()();
  await flush();
  assert.equal(f.model.state.view, "library");
  assert.equal(f.model.state.current, null);
  assert.equal(Object.keys(f.model.state.jobs).length, 0);
  f.dispose();
});
test("purge guard rejects wrong title before any request", async () => {
  const f = await fixture();
  f.model.requestPurge({ title: "测试作品", restore_token: "test-token" });
  f.model.state.purgeTitle = "错误名称";
  await f.model.purgeBook();
  assert.equal(f.calls.filter((c) => c.url.endsWith("/purge")).length, 0);
  f.model.closeDialog("purge");
  assert.equal(f.model.state.purgeTitle, "");
  f.dispose();
});


test("system theme follows device appearance and removes its listener on disposal", async () => {
  const f = await fixture({ darkSystem: true });
  assert.equal(f.model.state.theme, "system");
  assert.equal(f.root.dataset.theme, "dark");
  f.changeSystemTheme(false);
  assert.equal(f.root.dataset.theme, "light");
  f.changeSystemTheme(true);
  assert.equal(f.root.dataset.theme, "dark");
  assert.equal(f.themeListeners.size, 1);
  f.dispose();
  assert.equal(f.themeListeners.size, 0);
});

test("explicit themes override system appearance and survive a reload", async () => {
  const f = await fixture({ darkSystem: true });
  f.model.state.theme = "light";
  assert.equal(f.root.dataset.theme, "light");
  assert.equal(f.storage.get("tome-theme"), "light");
  f.changeSystemTheme(true);
  assert.equal(f.root.dataset.theme, "light");
  f.model.state.theme = "dark";
  f.changeSystemTheme(false);
  assert.equal(f.root.dataset.theme, "dark");
  const reload = await fixture({ theme: f.storage.get("tome-theme"), darkSystem: false });
  assert.equal(reload.model.state.theme, "dark");
  assert.equal(reload.root.dataset.theme, "dark");
  reload.model.state.theme = "system";
  assert.equal(reload.root.dataset.theme, "light");
  reload.changeSystemTheme(true);
  assert.equal(reload.root.dataset.theme, "dark");
  f.dispose();
  reload.dispose();
});

test("invalid or blocked theme storage falls back to system without breaking startup", async () => {
  for (const options of [{ theme: "obsolete" }, { blockStorage: true }]) {
    const f = await fixture({ ...options, darkSystem: true });
    assert.equal(f.model.state.theme, "system");
    assert.equal(f.root.dataset.theme, "dark");
    assert.equal(f.model.state.connectionError, false);
    f.model.state.theme = "light";
    assert.equal(f.root.dataset.theme, "light");
    f.dispose();
  }
});
