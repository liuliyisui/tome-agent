/* Vue controls rendering, forms and events. Native dialog lifecycle is a directive. */
const {
  createApp,
  reactive,
  computed,
  ref,
  watch,
  onMounted,
  onBeforeUnmount,
  h,
} = Vue;
if ("scrollRestoration" in history) history.scrollRestoration = "manual";
async function api(path, data) {
  const response = await fetch(
    path,
    data === undefined
      ? {}
      : {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        },
  );
  const result = await response.json();
  if (!response.ok) {
    const error = new Error(result.error || "操作失败");
    error.status = response.status;
    throw error;
  }
  return result;
}
const bookUrl = (id) => `/api/books/${encodeURIComponent(id)}`;
const titleOf = (book) =>
  book?.metadata?.title || book?.title || book?.id || "";
const concise = (value, limit = 18) => {
  const text = String(value ?? "")
    .replace(/\s+/g, " ")
    .replace(/^[“”「」『』"'\s]+/g, "")
    .trim();
  const first = text.split(/[。！？；\n]/)[0] || text;
  return Array.from(first).length > limit
    ? Array.from(first).slice(0, limit).join("") + "…"
    : first;
};
const valueOf = (fact) =>
  typeof fact.value === "object"
    ? JSON.stringify(fact.value)
    : String(fact.value ?? "");
const ChapterReader = {
  name: "ChapterReader",
  props: ["chapter"],
  setup(props) {
    return () =>
      props.chapter
        ? [
            h("h3", `第${props.chapter.number}章 · ${props.chapter.title}`),
            ...props.chapter.text
              .split(/\r\n|[\n\r\u2028\u2029]/)
              .map((p) => p.trim())
              .filter(Boolean)
              .map((text, key) =>
                h("p", { key, class: "prose-paragraph" }, text),
              ),
          ]
        : h("div", { class: "chapter-empty" }, [
            h("span", "✧"),
            h("h3", "故事，正待落笔。"),
            h("p", "点击「生成下一章」，让你的构想变成正文。"),
          ]);
  },
};
const FactMemory = {
  name: "FactMemory",
  props: ["fact"],
  setup(props) {
    return () => {
      const f = props.fact,
        value = valueOf(f),
        quote = f.source?.quote || "",
        excerpt =
          f.kind === "prose_excerpt" || String(f.subject).startsWith("prose:"),
        tiers = { working: "工作记忆", recent: "近期记忆", long: "长期记忆" };
      return h("div", { class: "fact" }, [
        excerpt
          ? null
          : h("h4", `${concise(f.subject, 10)} · ${concise(value, 14)}`),
        h("p", value),
        h(
          "small",
          `第 ${f.source?.chapter_number || "—"} 章 · 版本 ${f.revision}${f.tier ? " · " + (tiers[f.tier] || f.tier) : ""}`,
        ),
        quote && quote !== value
          ? h("details", { class: "fact-source" }, [
              h("summary", "查看正文依据"),
              h("blockquote", quote),
            ])
          : null,
      ]);
    };
  },
};

const app = createApp({
  name: "TomeStudio",
  components: { ChapterReader, FactMemory },
  render: window.TomeRender,
  setup() {
    let sidebarCollapsed = false;
    try {
      sidebarCollapsed =
        localStorage.getItem("tome-sidebar-collapsed") === "true";
    } catch {}
    const state = reactive({
      view: "home",
      sidebarCollapsed,
      books: [],
      trash: [],
      current: null,
      chapterIndex: 0,
      configured: false,
      model: "",
      connectionError: false,
      notice: "",
      menuId: null,
      dialogs: {
        api: false,
        create: false,
        trash: false,
        delete: false,
        purge: false,
        estimate: false,
      },
      busy: {
        api: false,
        create: false,
        style: false,
        estimate: false,
        start: false,
        delete: false,
        purge: false,
      },
      pending: new Set(),
      errors: {
        api: "",
        create: "",
        style: "",
        delete: "",
        purge: "",
        estimate: "",
      },
      apiKey: "",
      createForm: {
        title: "",
        prompt: "",
        chapters: 10,
        target_units: 10000,
        instructions: "",
        reference: "",
      },
      styles: {},
      batches: {},
      factChoices: {},
      jobs: {},
      jobErrors: {},
      estimate: null,
      estimateTitle: "",
      deleteBook: null,
      purgeBook: null,
      purgeTitle: "",
      trashMessage: "",
    });
    let navigationVersion = 0,
      libraryVersion = 0,
      disposed = false;
    const timers = new Map(),
      polling = new Set(),
      noticePanel = ref(null);
    const id = computed(() => state.current?.state.project_id),
      meta = computed(() => state.current?.metadata),
      chapters = computed(() => state.current?.state.chapters || []),
      chapter = computed(() => chapters.value[state.chapterIndex]);
    const remaining = computed(() =>
        Math.max(0, (meta.value?.target_chapters || 0) - chapters.value.length),
      ),
      running = computed(() => Boolean(state.jobs[id.value])),
      complete = computed(
        () => Boolean(state.current) && remaining.value === 0,
      );
    const style = computed(
        () => state.styles[id.value] || { instructions: "", reference: "" },
      ),
      batch = computed(
        () => state.batches[id.value] || { approved: false, count: 1 },
      );
    const styleDirty = computed(
      () =>
        Boolean(state.current) &&
        JSON.stringify(style.value) !==
          JSON.stringify({
            instructions: state.current.style?.instructions || "",
            reference: state.current.style?.reference || "",
          }),
    );
    const styleStatus = computed(
      () =>
        state.errors.style ||
        (state.busy.style
          ? "正在保存…"
          : styleDirty.value
            ? "有未保存的修改；生成下一章时会先自动保存。"
            : style.value.instructions || style.value.reference
              ? "已保存 · 从下一章生效。"
              : "尚未设置，使用默认文风。"),
    );
    const facts = computed(() =>
      Object.values(state.current?.state.facts || {}).filter(
        (f) => f.status === "active",
      ),
    );
    const factGroups = computed(() => {
      const groups = new Map();
      for (const fact of facts.value) {
        const excerpt =
            fact.kind === "prose_excerpt" ||
            String(fact.subject).startsWith("prose:"),
          number = fact.source?.chapter_number,
          sourceChapter = chapters.value.find((c) => c.number === number),
          key = excerpt ? `chapter:${number}` : `subject:${fact.subject}`,
          label = excerpt
            ? `第${number}章 · ${concise(sourceChapter?.title || valueOf(fact), 12)}`
            : concise(fact.subject, 12);
        if (!groups.has(key))
          groups.set(key, {
            key,
            label,
            facts: [],
            number: excerpt ? Number(number) || 0 : null,
          });
        groups.get(key).facts.push(fact);
      }
      return [...groups.values()].sort((a, b) =>
        a.number !== null && b.number !== null
          ? b.number - a.number
          : a.number === null
            ? b.number === null
              ? a.label.localeCompare(b.label, "zh-CN")
              : -1
            : 1,
      );
    });
    const factTopic = computed({
      get() {
        const choice =
          state.factChoices[id.value] ||
          `chapter:${chapter.value?.number || 1}`;
        return factGroups.value.some((g) => g.key === choice)
          ? choice
          : factGroups.value[0]?.key || "";
      },
      set(value) {
        state.factChoices[id.value] = value;
      },
    });
    const selectedFacts = computed(
      () =>
        factGroups.value.find((g) => g.key === factTopic.value)?.facts || [],
    );
    const units = computed(() =>
      chapters.value.reduce(
        (sum, c) =>
          sum + (c.text.match(/[\u3400-\u9fff]|[A-Za-z0-9]+/g) || []).length,
        0,
      ),
    );
    const generationDisabled = computed(
      () =>
        !state.current ||
        running.value ||
        complete.value ||
        state.current.mode === "legacy" ||
        state.busy.estimate ||
        state.busy.start ||
        state.busy.style,
    );
    const generateLabel = computed(() =>
      running.value
        ? "◌ 正在创作…"
        : state.busy.estimate
          ? "正在估算…"
          : state.current?.mode === "legacy"
            ? "旧版存档 · 仅供阅读"
            : complete.value
              ? "✓ 全书章节已完成"
              : Number(batch.value.count) > 1
                ? `预估并生成 ${batch.value.count} 章`
                : "预估并生成下一章",
    );
    const jobStatus = computed(() => {
      const job = state.current?.job,
        error = state.jobErrors[id.value];
      if (running.value)
        return (
          error ||
          `${job?.count ? `本批次已完成 ${job.completed || 0} / ${job.count} 章，正在生成第 ${job.current_chapter} 章。` : "已提交，正在生成。"}可刷新页面，完成后自动显示正文。`
        );
      return error
        ? `生成停止：${error}。已保存章节仍可阅读和导出。`
        : complete.value
          ? "所有目标章节已存档，可导出作品。"
          : job?.status === "completed"
            ? `✓ 本批次 ${job.count || 1} 章已生成并存档。`
            : "";
    });
    const connectionText = computed(() =>
        state.connectionError
          ? "连接失败"
          : state.configured
            ? `${state.model} 已就绪`
            : "请先配置 API Key",
      ),
      breadcrumb = computed(() =>
        state.view === "home"
          ? "首页"
          : state.view === "library"
            ? "我的作品"
            : meta.value?.title || "作品",
      ),
      sidebarHidden = computed(
        () => state.view === "home" || state.sidebarCollapsed,
      );
    const fmt = (value) => Number(value || 0).toLocaleString(),
      cost = (value) =>
        value === null || value === undefined
          ? "该模型暂无法自动匹配官方价格"
          : `≈ ¥ ${Number(value).toFixed(4)}`,
      price = (value) =>
        value === null || value === undefined
          ? "未匹配"
          : `¥ ${value} / 百万 token`,
      deletedAt = (value) => {
        const date = new Date(value);
        return Number.isNaN(date.getTime())
          ? "删除时间未记录"
          : date.toLocaleString("zh-CN", {
              timeZone: "Asia/Shanghai",
              hour12: false,
            });
      };
    const notify = (message) => {
      state.notice = message || "";
    };
    watch(
      () => state.notice,
      (message) => {
        if (message)
          noticePanel.value?.scrollIntoView({
            behavior: "smooth",
            block: "center",
          });
      },
      { flush: "post" },
    );
    function toggleSidebar() {
      state.sidebarCollapsed = !state.sidebarCollapsed;
      try {
        localStorage.setItem(
          "tome-sidebar-collapsed",
          String(state.sidebarCollapsed),
        );
      } catch {}
    }
    function showLibrary() {
      navigationVersion++;
      state.current = null;
      state.view = "library";
      state.menuId = null;
      notify();
      window.scrollTo({ top: 0, left: 0 });
      refreshBooks().catch((e) => notify(e.message));
    }
    function closeDialog(name) {
      if (state.busy[name] || (name === "estimate" && state.busy.start)) return;
      state.dialogs[name] = false;
      if (name === "api") state.apiKey = "";
      if (name === "estimate") state.estimate = null;
      if (name === "delete") state.deleteBook = null;
      if (name === "purge") {
        state.purgeBook = null;
        state.purgeTitle = "";
      }
    }
    function openApiConfig() {
      state.apiKey = "";
      state.errors.api = "";
      state.dialogs.api = true;
    }
    function openCreate() {
      if (!state.configured) return openApiConfig();
      state.errors.create = "";
      state.dialogs.create = true;
    }
    async function configure() {
      if (state.busy.api) return;
      state.busy.api = true;
      state.errors.api = "";
      try {
        const cfg = await api("/api/config", { api_key: state.apiKey.trim() });
        state.configured = cfg.configured;
        state.model = cfg.model;
        state.apiKey = "";
        state.dialogs.api = false;
        notify("API Key 已保存，可以开始创作。");
      } catch (e) {
        state.errors.api = e.message;
      } finally {
        state.busy.api = false;
      }
    }
    async function refreshBooks() {
      const version = ++libraryVersion;
      const [books, trash] = await Promise.all([
        api("/api/books"),
        api("/api/books/trash"),
      ]);
      if (disposed || version !== libraryVersion) return;
      state.books = books.books;
      state.trash = trash.books;
    }
    function acceptBook(book, latest = false) {
      const same = id.value === book.state.project_id;
      state.chapterIndex = latest
        ? Math.max(0, book.state.chapters.length - 1)
        : same
          ? Math.min(
              state.chapterIndex,
              Math.max(0, book.state.chapters.length - 1),
            )
          : 0;
      state.current = book;
      const key = book.state.project_id;
      state.styles[key] ??= {
        instructions: book.style?.instructions || "",
        reference: book.style?.reference || "",
      };
      state.batches[key] ??= { approved: false, count: 1 };
      state.batches[key].count = Math.max(
        1,
        Math.min(Number(state.batches[key].count) || 1, remaining.value),
      );
      state.errors.style = "";
      if (book.job?.status === "running") {
        state.jobs[key] = book.job.job_id;
        startPolling(key, book.job.job_id);
      } else {
        delete state.jobs[key];
        if (book.job?.status === "failed")
          state.jobErrors[key] = book.job.error;
        else delete state.jobErrors[key];
      }
    }
    async function selectBook(key) {
      const version = ++navigationVersion;
      state.pending.add(key);
      state.menuId = null;
      try {
        const book = await api(bookUrl(key));
        if (disposed || version !== navigationVersion) return;
        acceptBook(book);
        state.view = "book";
        notify();
        await refreshBooks();
      } catch (e) {
        if (version === navigationVersion) notify(e.message);
      } finally {
        state.pending.delete(key);
      }
    }
    async function refreshCurrent(key, latest = false) {
      const book = await api(bookUrl(key));
      if (!disposed && id.value === key && state.view === "book")
        acceptBook(book, latest);
    }
    async function createBook() {
      if (state.busy.create) return;
      state.busy.create = true;
      state.errors.create = "";
      try {
        const f = state.createForm,
          book = await api("/api/books", {
            title: f.title,
            prompt: f.prompt,
            chapters: Number(f.chapters),
            target_units: Number(f.target_units),
            style: { instructions: f.instructions, reference: f.reference },
          });
        state.dialogs.create = false;
        state.createForm = {
          title: "",
          prompt: "",
          chapters: 10,
          target_units: 10000,
          instructions: "",
          reference: "",
        };
        await selectBook(book.state.project_id);
      } catch (e) {
        state.errors.create = e.message;
      } finally {
        state.busy.create = false;
      }
    }
    async function pinBook(book) {
      if (state.pending.has(book.id)) return;
      state.pending.add(book.id);
      state.menuId = null;
      try {
        await api(`${bookUrl(book.id)}/pin`, { pinned: !book.pinned });
        await refreshBooks();
      } catch (e) {
        notify(e.message);
      } finally {
        state.pending.delete(book.id);
      }
    }
    function requestDelete(book) {
      state.deleteBook = book;
      state.errors.delete = "";
      state.menuId = null;
      state.dialogs.delete = true;
    }
    async function deleteBook() {
      if (!state.deleteBook || state.busy.delete) return;
      state.busy.delete = true;
      const key = state.deleteBook.id;
      try {
        await api(`${bookUrl(key)}/delete`, { confirmed: true });
        delete state.styles[key];
        delete state.batches[key];
        delete state.factChoices[key];
        delete state.jobErrors[key];
        state.dialogs.delete = false;
        state.deleteBook = null;
        if (id.value === key) {
          navigationVersion++;
          state.current = null;
          state.view = "library";
        }
        await refreshBooks();
      } catch (e) {
        state.errors.delete = e.message;
      } finally {
        state.busy.delete = false;
      }
    }
    async function openTrash() {
      state.trashMessage = "";
      try {
        await refreshBooks();
        state.dialogs.trash = true;
      } catch (e) {
        notify(e.message);
      }
    }
    async function restoreBook(book) {
      const key = book.restore_token;
      if (state.pending.has(key)) return;
      state.pending.add(key);
      state.trashMessage = "正在恢复…";
      try {
        const result = await api("/api/books/restore", { restore_token: key });
        await refreshBooks();
        state.trashMessage = `《${result.metadata.title}》已恢复到书架。`;
      } catch (e) {
        state.trashMessage = e.message;
      } finally {
        state.pending.delete(key);
      }
    }
    function requestPurge(book) {
      state.purgeBook = book;
      state.purgeTitle = "";
      state.errors.purge = "";
      state.dialogs.purge = true;
    }
    async function purgeBook() {
      const book = state.purgeBook;
      if (!book || state.busy.purge || state.purgeTitle !== book.title) return;
      state.busy.purge = true;
      try {
        await api("/api/books/trash/purge", {
          restore_token: book.restore_token,
          confirmation_title: state.purgeTitle,
          confirmed: true,
        });
        state.dialogs.purge = false;
        state.purgeBook = null;
        state.purgeTitle = "";
        await refreshBooks();
        state.trashMessage = `《${book.title}》已彻底删除，无法恢复。`;
      } catch (e) {
        state.errors.purge = e.message;
      } finally {
        state.busy.purge = false;
      }
    }
    function approveFirst() {
      batch.value.count = batch.value.approved
        ? Math.max(1, remaining.value)
        : 1;
    }
    async function saveStyle(key = id.value) {
      if (!key || state.busy.style) return;
      state.busy.style = true;
      state.errors.style = "";
      const submitted = { ...state.styles[key] };
      try {
        const result = await api(`${bookUrl(key)}/style`, submitted);
        if (id.value === key) state.current.style = result.style;
      } catch (e) {
        state.errors.style = `保存失败：${e.message}`;
        throw e;
      } finally {
        state.busy.style = false;
      }
    }
    async function submitStyle() {
      try {
        await saveStyle();
      } catch {
        /* Form keeps draft and displays its own error. */
      }
    }
    async function prepareGeneration() {
      if (generationDisabled.value) return;
      const key = id.value;
      state.busy.estimate = true;
      notify();
      try {
        if (styleDirty.value) await saveStyle(key);
        if (id.value !== key) return;
        const result = await api(`${bookUrl(key)}/estimate`, {
          count: Number(batch.value.count),
          approved_first: batch.value.approved,
        });
        if (id.value !== key) return;
        state.estimate = result;
        state.estimateTitle = meta.value.title;
        state.errors.estimate = "";
        state.dialogs.estimate = true;
      } catch (e) {
        notify(e.message);
      } finally {
        state.busy.estimate = false;
      }
    }
    async function confirmGeneration() {
      const estimate = state.estimate;
      if (!estimate || state.busy.start) return;
      state.busy.start = true;
      state.errors.estimate = "";
      try {
        const { job_id } = await api(`${bookUrl(estimate.book_id)}/generate`, {
          estimate_id: estimate.estimate_id,
          confirmed: true,
        });
        state.jobs[estimate.book_id] = job_id;
        delete state.jobErrors[estimate.book_id];
        if (id.value === estimate.book_id)
          state.current.job = {
            count: estimate.count,
            completed: 0,
            current_chapter: estimate.first_chapter,
          };
        state.dialogs.estimate = false;
        state.estimate = null;
        startPolling(estimate.book_id, job_id);
      } catch (e) {
        state.errors.estimate = e.message;
      } finally {
        state.busy.start = false;
      }
    }
    function schedule(key, jobId, delay) {
      if (!disposed)
        timers.set(
          jobId,
          setTimeout(() => pollJob(key, jobId), delay),
        );
    }
    function startPolling(key, jobId) {
      if (!jobId || polling.has(jobId)) return;
      polling.add(jobId);
      pollJob(key, jobId);
    }
    async function pollJob(key, jobId) {
      if (disposed) return;
      try {
        const job = await api(`/api/jobs/${encodeURIComponent(jobId)}`);
        if (disposed || state.jobs[key] !== jobId) return;
        if (id.value === key) state.current.job = job;
        delete state.jobErrors[key];
        if (job.status === "running") {
          if (
            id.value === key &&
            chapters.value.length < (job.current_chapter || 1) - 1
          )
            await refreshCurrent(key, true);
          schedule(key, jobId, 1500);
          return;
        }
        polling.delete(jobId);
        timers.delete(jobId);
        delete state.jobs[key];
        if (id.value === key) await refreshCurrent(key, true);
        else await refreshBooks();
        if (job.status === "failed") {
          state.jobErrors[key] = job.error;
          notify(job.error);
        }
      } catch (e) {
        if (disposed) return;
        if (e.status === 404) {
          polling.delete(jobId);
          delete state.jobs[key];
          timers.delete(jobId);
          try {
            if (id.value === key) await refreshCurrent(key);
          } catch (error) {
            notify(error.message);
          }
          notify("任务状态已失效，已重新读取作品存档。请确认正文后再提交。");
          return;
        }
        if (polling.has(jobId)) {
          state.jobErrors[key] = "状态连接暂时中断，正在重连；请勿重复提交。";
          schedule(key, jobId, 3000);
        }
      }
    }
    onMounted(async () => {
      try {
        localStorage.removeItem("tome-selected-book");
        localStorage.removeItem("tome-last-deleted");
      } catch {}
      try {
        const cfg = await api("/api/config");
        state.configured = cfg.configured;
        state.model = cfg.model;
        if (!cfg.configured) openApiConfig();
        await refreshBooks();
      } catch (e) {
        state.connectionError = true;
        notify(e.message);
      } finally {
        window.scrollTo({ top: 0, left: 0 });
      }
    });
    onBeforeUnmount(() => {
      disposed = true;
      timers.forEach((timer) => clearTimeout(timer));
    });
    return {
      state,
      id,
      meta,
      chapters,
      chapter,
      remaining,
      running,
      complete,
      style,
      batch,
      styleStatus,
      facts,
      factGroups,
      factTopic,
      selectedFacts,
      units,
      generationDisabled,
      generateLabel,
      jobStatus,
      connectionText,
      breadcrumb,
      sidebarHidden,
      noticePanel,
      titleOf,
      fmt,
      cost,
      price,
      deletedAt,
      toggleSidebar,
      showLibrary,
      closeDialog,
      openCreate,
      configure,
      createBook,
      selectBook,
      pinBook,
      requestDelete,
      deleteBook,
      openTrash,
      restoreBook,
      requestPurge,
      purgeBook,
      approveFirst,
      submitStyle,
      prepareGeneration,
      confirmGeneration,
    };
  },
});
app.directive("dialog", {
  mounted(el, binding) {
    if (binding.value) el.showModal();
  },
  updated(el, binding) {
    if (binding.value && !el.open) el.showModal();
    else if (!binding.value && el.open) el.close();
  },
  beforeUnmount(el) {
    if (el.open) el.close();
  },
});
app.mount("#tome-app");
