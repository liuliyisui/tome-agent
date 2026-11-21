/* Exercise the real Vue reactive model without a browser or paid model calls. */
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const frontend = path.resolve(__dirname, "../../code/frontend");
const clone = (value) => JSON.parse(JSON.stringify(value));
const flush = () => new Promise((resolve) => setImmediate(resolve));

async function fixture({
  configured = true, theme = null, darkSystem = false, blockStorage = false,
  storedProviders = [], modelConfig = null,
} = {}) {
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
    edit_revision: "revision-" + id,
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
  const storage = new Map(storedProviders);
  if (theme !== null) storage.set("tome-theme", theme);
  const root = { dataset: {} };
  const themeListeners = new Set();
  const media = {
    matches: darkSystem,
    addEventListener: (name, listener) => themeListeners.add(listener),
    removeEventListener: (name, listener) => themeListeners.delete(listener),
  };
  const context = vm.createContext({
    console,
    window: { TomeRender: () => {}, matchMedia: () => media, addEventListener() {}, removeEventListener() {} },
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
    requestAnimationFrame: () => 1,
    fetch: async (url, options) => {
      const payload = options?.body ? JSON.parse(options.body) : undefined;
      calls.push({ url, payload });
      if (url === "/api/config") return response({ configured, model: "test" });
      if (url === "/api/model-config" && modelConfig && payload === undefined) {
        return response(modelConfig);
      }
      if (url === "/api/books")
        return response({
          books: Object.entries(books).map(([id, b]) => ({
            id,
            metadata: b.metadata,
            chapters: b.state.chapters.length,
          })),
        });
      if (url === "/api/books/trash") return response({ books: [] });
      if (url === "/api/skills") return payload
        ? response({ skill: { id: "installed-skill", name: payload.name, content: payload.content } })
        : response({ skills: [] });
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
  context.document = {
    documentElement: root,
    body: { classList: { toggle() {} } },
    addEventListener() {},
    removeEventListener() {},
    getElementById() { return null; },
  };
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

test("provider selection preserves unsaved fields and clears the previous key", async () => {
  const f = await fixture();
  f.model.addCustomProvider();
  f.model.state.modelForm.providerName = "千问";
  f.model.state.modelForm.endpoint = "https://example.com/v1";
  f.model.state.modelForm.model = "qwen-test";
  f.model.state.apiKey = "custom-key";
  f.model.selectProvider("openai");
  assert.equal(f.model.state.modelForm.provider, "openai");
  assert.equal(f.model.state.apiKey, "");
  f.model.selectProvider("custom-1");
  assert.equal(f.model.state.modelForm.providerName, "千问");
  assert.equal(f.model.state.modelForm.endpoint, "https://example.com/v1");
  assert.equal(f.model.state.modelForm.model, "qwen-test");
  assert.equal(f.model.state.apiKey, "");
  f.dispose();
});


test("adding another custom provider creates an independent editable entry", async () => {
  const f = await fixture();
  f.model.addCustomProvider();
  f.model.state.modelForm.providerName = "千问";
  f.model.state.modelForm.model = "qwen";
  f.model.addCustomProvider();
  assert.equal(f.model.state.providerSlot, "custom-2");
  assert.equal(f.model.state.modelForm.providerName, "");
  f.model.state.modelForm.providerName = "其他服务";
  f.model.selectProvider("custom-1");
  assert.equal(f.model.state.modelForm.providerName, "千问");
  assert.equal(f.model.state.modelForm.model, "qwen");
  f.model.selectProvider("custom-2");
  assert.equal(f.model.state.modelForm.providerName, "其他服务");
  f.dispose();
});


test("remove custom entries and select common providers", async () => {
  const f = await fixture();
  f.model.addCustomProvider();
  f.model.addCustomProvider();
  f.model.removeCustomProvider("custom-1");
  assert.deepEqual(Array.from(f.model.state.customProviders), ["custom-2"]);
  f.model.removeCustomProvider("custom-2");
  assert.equal(f.model.state.providerSlot, "deepseek");
  f.model.selectProvider("qwen");
  assert.equal(f.model.state.modelForm.provider, "compatible");
  assert.equal(f.model.state.modelForm.endpoint, "https://dashscope.aliyuncs.com/compatible-mode/v1");
  f.model.selectProvider("doubao");
  assert.equal(f.model.state.modelForm.endpoint, "https://ark.cn-beijing.volces.com/api/v3");
  f.dispose();
});


test("a corrupt preset preference does not hide a saved custom provider", async () => {
  const endpoint = "https://custom.example.test/v1";
  const f = await fixture({
    storedProviders: [
      ["tome-provider-presets", "invalid JSON"],
      ["tome-custom-providers", JSON.stringify([
        { providerName: "个人服务", model: "draft-model", endpoint },
      ])],
    ],
    modelConfig: { provider: "compatible", provider_name: "个人服务", model: "active-model", endpoint },
  });
  assert.equal(f.model.state.customProviders.length, 1);
  assert.equal(f.model.state.providerSlot, "custom-1");
  assert.equal(f.model.state.modelForm.model, "active-model");
  assert.equal(f.model.state.modelForm.endpoint, endpoint);
  f.dispose();
});

test("provider catalog contains requested compatible services", async () => {
  const f = await fixture();
  for (const id of ["gemini", "minimax", "siliconflow", "openrouter", "glm", "mimo"]) {
    f.model.selectProvider(id);
    assert.equal(f.model.state.modelForm.provider, "compatible");
    assert.match(f.model.state.modelForm.endpoint, /^https:\/\//);
  }
  f.dispose();
});


test("event identifiers are hidden without removing other facts", async () => {
  const f = await fixture();
  f.books.a.state.facts = {
    a: { status: "active", kind: "event", subject: "event:c0001.a0001", value: "主角抵达客栈", source: { chapter_number: 1 } },
    b: { status: "active", kind: "event", subject: "event:c0001.a0002", value: "主角发现线索", source: { chapter_number: 1 } },
    c: { status: "active", kind: "event", subject: "event:c0002.a0001", value: "主角遇见对手", source: { chapter_number: 2 } },
    d: { status: "active", subject: "主角", value: "信使", source: { chapter_number: 1 } },
  };
  await f.model.selectBook("a");
  const groups = f.model.factGroups.value;
  assert.equal(f.model.facts.value.length, 1);
  assert.equal(Object.keys(f.books.a.state.facts).length, 4);
  assert.ok(groups.some((g) => g.label === "主角"));
  assert.ok(groups.every((g) => !g.label.includes("event:")));
  f.dispose();
});


test("personal information needs explicit acknowledgement for each estimate", async () => {
  const f = await fixture();
  await f.model.selectBook("a");
  await f.model.prepareGeneration();
  f.model.state.estimate.safety = { blocked: false, requires_confirmation: true };
  await f.model.confirmGeneration();
  assert.equal(f.calls.filter(c => c.url.endsWith("/generate")).length, 0);
  f.model.state.privacyConfirmed = true;
  await f.model.confirmGeneration();
  assert.equal(f.calls.find(c => c.url.endsWith("/generate")).payload.privacy_confirmed, true);
  f.dispose();
});

test("suspected credentials block generation despite acknowledgement", async () => {
  const f = await fixture();
  await f.model.selectBook("a");
  await f.model.prepareGeneration();
  f.model.state.estimate.safety = { blocked: true, requires_confirmation: false };
  f.model.state.privacyConfirmed = true;
  await f.model.confirmGeneration();
  assert.equal(f.calls.filter(c => c.url.endsWith("/generate")).length, 0);
  f.model.closeDialog("estimate");
  await f.model.prepareGeneration();
  assert.equal(f.model.state.privacyConfirmed, false);
  f.dispose();
});


test("notices distinguish input warnings, failures and successful saves", async () => {
  const f = await fixture();
  await f.model.selectBook("a");
  await f.model.uploadCover({ target: { files: [{ type: "application/pdf", size: 1 }], value: "bad" } });
  assert.equal(f.model.state.noticeType, "warning");
  assert.match(f.model.state.notice, /PNG/);
  await f.model.installSkill({ target: { files: [{ size: 1, name: "bad.md", text: async () => { throw new Error("无法读取技能文件"); } }], value: "bad" } });
  assert.equal(f.model.state.noticeType, "error");
  assert.match(f.model.state.notice, /无法读取/);
  await f.model.installSkill({ target: { files: [{ size: 10, name: "writing.md", text: async () => "逐步揭示线索" }], value: "ok" } });
  assert.equal(f.model.state.noticeType, "success");
  assert.equal(f.model.state.skills[0].id, "installed-skill");
  await f.model.prepareGeneration();
  assert.equal(f.model.state.notice, "");
  assert.equal(f.model.state.noticeType, "info");
  f.dispose();
});

test("reconnecting is a warning while failed and completed jobs have distinct levels", async () => {
  const f = await fixture();
  await f.model.selectBook("a");
  f.model.state.jobs.a = "job-1";
  f.model.state.current.job = { status: "running", count: 1 };
  f.model.state.jobErrors.a = "状态连接暂时中断，正在重连";
  assert.equal(f.model.jobLevel.value, "warning");
  delete f.model.state.jobs.a;
  f.model.state.current.job.status = "failed";
  assert.equal(f.model.jobLevel.value, "error");
  delete f.model.state.jobErrors.a;
  f.model.state.current.job.status = "completed";
  assert.equal(f.model.jobLevel.value, "success");
  f.dispose();
});


test("local manuscript drafts survive reopening and block generation while editing", async () => {
  const f = await fixture();
  await f.model.selectBook("a");
  f.model.openEditor();
  f.model.state.editor.text = "作者修改后的正文。";
  assert.equal(f.model.generationDisabled.value, true);
  assert.equal(JSON.parse(f.storage.get("tome-chapter-draft:a:1")).text, "作者修改后的正文。");
  f.model.closeEditor();
  f.model.openEditor();
  assert.equal(f.model.state.editor.text, "　　作者修改后的正文。");
  assert.equal(f.model.state.editor.base_revision, "revision-a");
  f.model.discardDraft();
  assert.equal(f.storage.has("tome-chapter-draft:a:1"), false);
  f.dispose();
});


test("failed browser draft storage cannot silently discard manuscript edits", async () => {
  const f = await fixture({ blockStorage: true });
  await f.model.selectBook("a");
  f.model.openEditor();
  f.model.state.editor.text = "尚未保存的作者文字。";
  assert.equal(f.model.state.draftStored, false);
  f.model.showLibrary();
  assert.equal(f.model.state.view, "book");
  assert.equal(f.model.state.editor.text, "尚未保存的作者文字。");
  assert.equal(f.model.state.noticeType, "warning");
  f.model.discardDraft();
  f.model.showLibrary();
  assert.equal(f.model.state.view, "library");
  f.dispose();
});

test("memory directory separates character cards, relations, chapter excerpts and settings", async () => {
  const f = await fixture();
  f.books.a.state.chapters.push({ number: 2, title: "重逢", text: "林渊在客栈重逢韩老三。" });
  const fact = (subject, attribute, number = 1, kind = "state") =>
    ({ subject, attribute, value: "原有记忆", kind, status: "active", source: { chapter_number: number } });
  f.books.a.state.facts = {
    person: fact("林渊", "身份"), relation: fact("林渊与夏老爷的关系", "关系"),
    place: fact("雷火武馆", "地点"), prose2: fact("prose:c0002.a", "excerpt", "2", "prose_excerpt"),
    prose1: fact("prose:c0001.a", "excerpt", 1, "prose_excerpt"),
    event: fact("event:c0001.a", "event", 1, "event"),
  };
  await f.model.selectBook("a");
  const categories = Object.fromEntries(f.model.memoryCategories.value.map(c => [c.key, c]));
  assert.equal(categories.characters.groups[0].label, "林渊");
  assert.equal(categories.relations.groups[0].label, "林渊与夏老爷的关系");
  assert.equal(categories.settings.groups[0].label, "雷火武馆");
  assert.deepEqual(Array.from(categories.chapters.groups, g => g.number), [1, 2]);
  assert.match(categories.chapters.groups[1].label, /重逢/);
  f.model.state.memoryFilter = "林渊";
  assert.equal(f.model.memoryCategories.value.find(c => c.key === "chapters").visible.length, 0);
  assert.equal(f.model.facts.value.length, 5);
  assert.equal(Object.keys(f.books.a.state.facts).length, 6);
  f.dispose();
});

test("whole-book search matches literals, titles and later chapters with intact Unicode offsets", async () => {
  const f = await fixture();
  f.books.a.state.chapters = [
    { number: 1, title: "初见", text: "🦊韩老三找到了[a+b]，随后离开。" },
    { number: 4, title: "韩老三归来", text: "他问韩老三：API 和 api 是否相同？" },
  ];
  await f.model.selectBook("a");
  f.model.state.searchQuery = "[a+b]";
  f.model.submitBookSearch();
  assert.equal(f.model.searchResults.value.total, 1);
  assert.equal(f.model.searchResults.value.items[0].start, 8);
  f.model.state.searchQuery = "韩老三";
  f.model.submitBookSearch();
  assert.equal(f.model.searchResults.value.total, 3);
  const last = f.model.searchResults.value.items.at(-1);
  await f.model.jumpToSearch(last);
  assert.equal(f.model.chapter.value.number, 4);
  assert.equal(f.model.readerMatch.value.match, "韩老三");
  f.model.state.searchQuery = "API";
  f.model.submitBookSearch();
  assert.equal(f.model.searchResults.value.total, 2);
  f.model.clearBookSearch();
  assert.equal(f.model.searchResults.value.total, 0);
  assert.equal(f.model.readerMatch.value, null);
  f.dispose();
});

test("search results are bounded while counting all occurrences and update after edits", async () => {
  const f = await fixture();
  f.books.a.state.chapters[0].text = "线索".repeat(150);
  await f.model.selectBook("a");
  f.model.state.searchQuery = "线索";
  f.model.submitBookSearch();
  assert.equal(f.model.searchResults.value.total, 150);
  assert.equal(f.model.searchResults.value.items.length, 100);
  f.model.state.current.state.chapters[0].text = "已改稿。";
  assert.equal(f.model.searchResults.value.total, 0);
  await f.model.selectBook("b");
  assert.equal(f.model.state.searchQuery, "");
  f.dispose();
});

test("chapter filtering preserves real indices and search cannot discard an unsaved draft", async () => {
  const f = await fixture({ blockStorage: true });
  f.books.a.state.chapters.push({ number: 4, title: "归途", text: "新线索。" });
  await f.model.selectBook("a");
  f.model.state.chapterFilter = "归途";
  assert.equal(f.model.filteredChapters.value[0].index, 1);
  f.model.openEditor();
  f.model.state.editor.text = "尚未保存。";
  await f.model.chooseChapter(1);
  assert.equal(f.model.state.chapterIndex, 0);
  assert.equal(f.model.state.editor.text, "尚未保存。");
  f.model.discardDraft();
  await f.model.chooseChapter(1);
  assert.equal(f.model.chapter.value.number, 4);
  f.dispose();
});

test("memory source navigation locates saved text and invalidates stale highlights", async () => {
  const f = await fixture();
  f.books.a.state.chapters.push({ number: 2, title: "再会", text: "开场。韩老三把信交给林渊。" });
  await f.model.selectBook("a");
  await f.model.jumpToFact({ source: { chapter_number: "2", quote: "韩老三把信交给林渊" } });
  assert.equal(f.model.state.chapterIndex, 1);
  assert.equal(f.model.readerMatch.value.start, 3);
  f.model.state.current.state.chapters[1].text = "作者改了剧情。";
  assert.equal(f.model.readerMatch.value, null);
  f.dispose();
});
