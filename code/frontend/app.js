/* Vue controls rendering, forms and events. Native dialog lifecycle is a directive. */
const {
  createApp,
  reactive,
  computed,
  ref,
  nextTick,
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
    error.safety = result.safety;
    throw error;
  }
  return result;
}
const MESSAGE_LABELS = Object.freeze({ info: "提示", success: "成功", warning: "警告", danger: "危险", error: "错误" });
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
const isEventFact = (fact) =>
  fact.kind === "event" || String(fact.subject || "").startsWith("event:");
// Literal matching preserves source offsets, including emoji and mixed-case text.
const literalPattern = (query) => new RegExp(query.replace(/[\^$\\.*+?()[\]{}|]/g, "\\$&"), "giu");
const MEMORY_CATEGORIES = [
  { key: "characters", label: "人物卡" },
  { key: "relations", label: "人物关系" },
  { key: "chapters", label: "章节事实" },
  { key: "settings", label: "其他设定" },
];
function memoryCategory(fact) {
  const subject = String(fact.subject || ""), attribute = String(fact.attribute || "");
  if (fact.kind === "prose_excerpt" || subject.startsWith("prose:")) return "chapters";
  if (/关系|亲属|师徒|父子|母子|夫妻|兄弟|姐妹|恋人|盟友|敌对|relationship|relation/i.test(subject + " " + attribute)) return "relations";
  if (/地点|位置|地理|建筑|场所|道具|物品|兵器|组织|门派|世界观|规则|location|artifact/i.test(attribute) ||
      /武馆|客栈|城池|村庄|宗门|长剑|令牌|秘籍/.test(subject)) return "settings";
  if (/姓名|年龄|身份|性格|外貌|职业|称呼|性别|人物|角色|person|character/i.test(attribute) ||
      /主角|配角|小厮|掌柜|师父|师傅|老爷/.test(subject) ||
      /^[赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜谢邹苏潘葛范彭鲁韦马苗方俞任袁柳鲍史唐费薛雷贺倪汤殷罗毕郝邬安常于傅齐康伍余元顾孟平黄穆萧尹姚邵湛汪祁毛禹狄米贝明臧计伏成戴谈宋茅庞熊纪舒屈项祝董梁杜阮蓝闵席季麻强贾路娄危江童颜郭梅盛林钟徐邱骆高夏蔡田胡凌霍虞万卢莫房解应宗丁宣邓洪包左石崔吉龚程陆欧阳司徒上官诸葛][\p{Script=Han}]{1,3}$/u.test(subject)) return "characters";
  return "settings";
}
function searchChapters(chapters, query) {
  const term = query.trim();
  if (!term) return { items: [], total: 0 };
  const items = [], pattern = literalPattern(term);
  let total = 0;
  chapters.forEach((chapter, index) => {
    for (const field of ["title", "text"]) {
      const text = String(chapter[field] || "");
      pattern.lastIndex = 0;
      let match;
      while ((match = pattern.exec(text)) !== null) {
        total++;
        if (items.length < 100) {
          const start = match.index, end = start + match[0].length;
          items.push({ index, number: chapter.number, title: chapter.title, field, start, end,
            match: match[0], before: (start > 35 ? "…" : "") + text.slice(Math.max(0, start - 35), start),
            after: text.slice(end, end + 55) + (end + 55 < text.length ? "…" : "") });
        }
      }
    }
  });
  return { items, total };
}
function highlightedText(text, start, match, field) {
  if (!match || match.field !== field) return text;
  const from = Math.max(0, match.start - start), to = Math.min(text.length, match.end - start);
  if (to <= from) return text;
  return [text.slice(0, from), h("mark", { class: "search-hit-active" }, text.slice(from, to)), text.slice(to)];
}
function readProviderPreference(key, fallback) {
  try {
    return JSON.parse(localStorage.getItem(key) || "null") ?? fallback;
  } catch {
    return fallback;
  }
}
const ChapterReader = {
  name: "ChapterReader",
  props: ["chapter", "match"],
  setup(props) {
    return () => {
      if (!props.chapter) return h("div", { class: "chapter-empty" }, [
        h("span", "✧"), h("h3", "故事，正待落笔。"),
        h("p", "点击「生成下一章」，让你的构想变成正文。"),
      ]);
      const chapter = props.chapter;
      return [
        h("h3", ["第" + chapter.number + "章 · ", ...[highlightedText(chapter.title, 0, props.match, "title")].flat()]),
        ...Array.from(chapter.text.matchAll(/[^\r\n\u2028\u2029]+/g)).filter(row => row[0].trim()).map(row => {
          const text = row[0].trim(), start = row.index + row[0].indexOf(text);
          return h("p", { key: row.index, class: "prose-paragraph" },
            highlightedText(text, start, props.match, "text"));
        }),
      ];
    };
  },
};
const FactMemory = {
  name: "FactMemory",
  props: ["fact"],
  emits: ["locate"],
  setup(props, { emit }) {
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
          : h("h4", isEventFact(f) ? `事件 · ${concise(value, 18)}` : `${concise(f.subject, 10)} · ${concise(value, 14)}`),
        h("p", value),
        h(
          "small",
          `第 ${f.source?.chapter_number || "—"} 章 · 版本 ${f.revision}${f.tier ? " · " + (tiers[f.tier] || f.tier) : ""}`,
        ),
        Number(f.source?.chapter_number) > 0
          ? h("button", { type: "button", class: "fact-locate text-button", onClick: () => emit("locate", f) }, "定位到正文 ↗")
          : null,
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

const ProofreadingResults = {
  name: "ProofreadingResults",
  props: ["report", "acknowledged", "editable"],
  emits: ["update:acknowledged", "locate", "apply"],
  setup(props, { emit }) {
    return () => {
      const report = props.report;
      if (!report) return null;
      return h("section", { class: ["proofreading-results", "status-message", report.blocked ? "message-danger" : report.total ? "message-warning" : "message-success"], "aria-label": "本地复查结果" }, [
        h("h4", { role: "status" }, report.blocked ? "危险：发现疑似密钥，请先移除" : report.total ? `发现 ${report.total} 条待核对提示` : "本地规则未发现问题"),
        h("p", { class: "form-hint" }, report.note),
        report.truncated ? h("p", "提示较多，仅展示部分结果，请修改后重新复查。") : null,
        h("ol", { class: "proofreading-list" }, (report.findings || []).map((item, index) => h("li", { key: index }, [
          h("strong", `${item.level === "danger" ? "危险" : "提示"} · 第 ${item.chapter} 章${item.field === "title" ? "标题" : `第 ${item.line} 行`}：${item.message}`),
          h("p", item.suggestion),
          h("div", { class: "proofreading-actions" }, [
            h("button", { type: "button", class: "text-button", onClick: () => emit("locate", item) }, "定位修改"),
            props.editable && item.replacement !== null ? h("button", { type: "button", class: "outline", onClick: () => emit("apply", item) }, `采用建议：${item.replacement}`) : null,
          ]),
        ]))),
        report.total && !report.blocked ? h("label", { class: "check-label proofread-ack" }, [
          h("input", { type: "checkbox", checked: props.acknowledged === true, onChange: event => emit("update:acknowledged", event.target.checked) }),
          h("span", "我已核对以上提示，确认按当前内容提交"),
        ]) : null,
      ]);
    };
  },
};

const WritingNotes = {
  name: "WritingNotes",
  props: ["notes"],
  setup(props) {
    return () => {
      const note = props.notes;
      if (!note) return null;
      const context = note.context || {}, comparison = note.comparison;
      const scenes = Array.isArray(note.scenes) ? note.scenes : [];
      const hasRevision = note.operation === "regenerate" || Boolean(comparison);
      const block = (title, children) => h("div", { class: "writing-note-block" }, [h("h4", title), ...children]);
      const revision = comparison ? [
        h("p", comparison.format_only ? "仅调整了段落间空白或缩进，文字内容未变。" : comparison.text_changed
          ? `与原稿相比：更新 ${comparison.updated} 段，新增 ${comparison.added} 段，移除 ${comparison.removed} 段。`
          : "本次正文与原稿相同。"),
        comparison.title_changed ? h("p", `标题由「${comparison.previous_title}」调整为当前标题。`) : null,
        ...(comparison.examples || []).map((change, index) => h("details", { class: "revision-example", key: index }, [
          h("summary", `${change.old_paragraph ? `原稿第 ${change.old_paragraph} 段起` : "新增内容"} → ${change.new_paragraph ? `新稿第 ${change.new_paragraph} 段起` : "已移除"}`),
          h("div", { class: "revision-comparison" }, [
            h("div", [h("strong", "原稿"), h("p", change.before || "（无对应内容）")]),
            h("div", [h("strong", "新稿"), h("p", change.after || "（已移除）")]),
          ]),
        ])),
      ] : [h("p", note.operation === "generate"
        ? "本章为新生成内容，没有历史正文可供对照。"
        : "该历史章节未保存当次修改对照。")];
      return h("section", { class: "writing-notes", "aria-label": "本章安排" }, [
        h("h3", "本章安排"),
        h("p", { class: "writing-notes-brief" }, note.brief || "本章未保留简要规划，可展开查看现存记录。"),
        h("details", { class: "writing-notes-details" }, [
          h("summary", hasRevision ? "查看章节安排与修改对照" : "查看章节安排"),
          block("场景安排", scenes.length ? [
            h("ol", scenes.map((scene, index) => h("li", { key: index }, [
              h("p", scene.purpose || `场景 ${index + 1}`),
              h("ul", (scene.events || []).map((event, i) => h("li", { key: i }, event))),
            ]))),
            note.scenes_omitted ? h("p", { class: "form-hint" }, `另有 ${note.scenes_omitted} 个场景；此处展示前 ${scenes.length} 个。`) : null,
          ] : [h("p", "没有可展示的场景规划记录。")]),
          hasRevision ? block("修改说明", [
            context.author_feedback ? h("p", { class: "author-feedback-note" }, `本次作者意见：${context.author_feedback}`) : null,
            ...revision,
          ]) : null,
        ]),
      ]);
    };
  },
};

const LocalSafetyReview = {
  name: "LocalSafetyReview",
  props: ["report", "confirmed"],
  emits: ["update:confirmed"],
  setup(props, { emit }) {
    return () => {
      const report = props.report;
      if (!report?.total) return null;
      return h("section", {
        class: ["privacy-review", "status-message", `message-${report.blocked ? "danger" : "warning"}`, { "privacy-blocked": report.blocked }],
        "aria-label": "本地敏感信息检查",
      }, [
        h("h3", `${report.blocked ? "危险" : "警告"} · 本地敏感信息检查`),
        h("p", { role: report.blocked ? "alert" : "status" }, report.blocked
          ? "发现疑似密钥，请从创作内容中移除后再提交。"
          : "以下内容可能包含个人信息，发送前请核实。"),
        report.findings?.length ? h("ul", report.findings.map((item, index) =>
          h("li", { key: index }, `${item.source}：${item.label}，${item.count} 处`))) : null,
        h("p", { class: "form-hint" }, "检查在本机完成，结果不显示敏感原文。规则可能漏检；请用虚构信息替换真实隐私。"),
        report.requires_confirmation && !report.blocked
          ? h("label", { class: "privacy-confirm" }, [
            h("input", {
              type: "checkbox", checked: props.confirmed === true,
              onChange: (event) => emit("update:confirmed", event.target.checked),
            }),
            h("span", "我已核实这些信息为虚构或已获授权，同意本次发送给模型服务商"),
          ]) : null,
      ]);
    };
  },
};

const PROVIDER_PRESETS = [
  { id: "deepseek", name: "DeepSeek", icon: "D", provider: "deepseek", model: "deepseek-chat", endpoint: "" },
  { id: "openai", name: "OpenAI", icon: "O", provider: "openai", model: "gpt-4o", endpoint: "" },
  { id: "qwen", name: "千问（阿里云百炼）", icon: "千", provider: "compatible", endpoint: "https://dashscope.aliyuncs.com/compatible-mode/v1" },
  { id: "doubao", name: "豆包（火山方舟）", icon: "豆", provider: "compatible", endpoint: "https://ark.cn-beijing.volces.com/api/v3" },
  { id: "gemini", name: "Gemini", icon: "G", provider: "compatible", endpoint: "https://generativelanguage.googleapis.com/v1beta/openai" },
  { id: "minimax", name: "MiniMax Global", icon: "M", provider: "compatible", endpoint: "https://api.minimax.io/v1" },
  { id: "siliconflow", name: "SiliconFlow", icon: "S", provider: "compatible", endpoint: "https://api.siliconflow.cn/v1" },
  { id: "openrouter", name: "OpenRouter", icon: "O", provider: "compatible", endpoint: "https://openrouter.ai/api/v1" },
  { id: "glm", name: "GLM（智谱）", icon: "智", provider: "compatible", endpoint: "https://open.bigmodel.cn/api/paas/v4" },
  { id: "mimo", name: "Xiaomi MiMo", icon: "米", provider: "compatible", endpoint: "https://api.xiaomimimo.com/v1" },
];
const app = createApp({
  name: "TomeStudio",
  components: { ChapterReader, FactMemory, LocalSafetyReview, WritingNotes, ProofreadingResults },
  render: window.TomeRender,
  setup() {
    let sidebarCollapsed = false;
    let theme = "system";
    const navigationKey = "tome-session-navigation-v1";
    let previousNavigation = null;
    try { previousNavigation = JSON.parse(sessionStorage.getItem(navigationKey) || "null"); } catch {}
    try {
      sidebarCollapsed =
        localStorage.getItem("tome-sidebar-collapsed") === "true";
      const savedTheme = localStorage.getItem("tome-theme");
      if (["light", "dark", "system"].includes(savedTheme)) theme = savedTheme;
    } catch {}
    const systemTheme = window.matchMedia?.("(prefers-color-scheme: dark)");
    const state = reactive({
      view: "home",
      restoringNavigation: previousNavigation?.view === "book" || previousNavigation?.view === "library",
      theme,
      sidebarCollapsed,
      books: [],
      trash: [],
      current: null,
      chapterIndex: 0,
      configured: false,
      model: "",
      connectionError: false,
      notice: "",
      noticeType: "info",
      menuId: null,
      dialogs: {
        settings: false,
        api: false,
        create: false,
        trash: false,
        delete: false,
        purge: false,
        estimate: false,
        regenerate: false,
        review: false,
      },
      busy: {
        api: false,
        create: false,
        skill: false,
        style: false,
        cover: false,
        estimate: false,
        start: false,
        regenerate: false,
        delete: false,
        purge: false,
        edit: false,
        proofread: false,
        review: false,
        export: false,
      },
      pending: new Set(),
      errors: {
        api: "",
        create: "",
        style: "",
        delete: "",
        purge: "",
        estimate: "",
        regenerate: "",
      },
      editor: null,
      exportReview: null,
      editError: "",
      reviewError: "",
      draftStatus: "",
      draftStored: true,
      regeneration: null,
      apiKey: "",
      providerSlot: "deepseek",
      activeProvider: null,
      customProviders: [],
      providerDrafts: {},
      modelForm: { provider: "deepseek", providerName: "DeepSeek", model: "deepseek-chat", endpoint: "" },
      createForm: {
        title: "",
        prompt: "",
        chapters: 10,
        target_units: 10000,
        instructions: "",
        reference: "",
        skills: [],
      },
      styles: {},
      skills: [],
      batches: {},
      factChoices: {},
      memoryFilter: "",
      memoryFolders: { characters: false, relations: false, chapters: true, settings: false },
      chapterPickerOpen: false,
      chapterFilter: "",
      searchQuery: "",
      searchTerm: "",
      searchMatch: null,
      jobs: {},
      jobErrors: {},
      estimate: null,
      estimateTitle: "",
      privacyConfirmed: false,
      deleteBook: null,
      purgeBook: null,
      purgeTitle: "",
      trashMessage: "",
      trashLoading: false,
      trashError: "",
    });
    const draftKey = (key, number) => `tome-chapter-draft:${key}:${number}`;
    function sizeEditor() {
      const el = document.getElementById("chapter-edit-text");
      if (!el) return;
      el.style.height = "auto";
      el.style.height = `${el.scrollHeight + 2}px`;
    }
    const PARAGRAPH_INDENT = "\u3000\u3000";
    function normalizeParagraphIndent(text) {
      return String(text ?? "")
        .split("\n")
        .map((line) =>
          line.trim() === ""
            ? ""
            : PARAGRAPH_INDENT + line.replace(/^[\u3000\s]+/, ""),
        )
        .join("\n");
    }
    let editorResizeFrame = 0;
    function scheduleEditorResize() {
      if (editorResizeFrame) return;
      editorResizeFrame = requestAnimationFrame(() => {
        editorResizeFrame = 0;
        sizeEditor();
      });
    }
    function onEditorInput(event) {
      if (event.target && event.target.id === "chapter-edit-text") scheduleEditorResize();
    }
    function onEditorKeydown(event) {
      if (!state.editor) return;
      if (event.key === "Escape") {
        event.preventDefault();
        closeEditor();
        return;
      }
      const target = event.target;
      if (
        event.key === "Enter" &&
        !event.shiftKey &&
        !event.ctrlKey &&
        !event.metaKey &&
        !event.altKey &&
        !event.isComposing &&
        target &&
        target.id === "chapter-edit-text"
      ) {
        event.preventDefault();
        const start = target.selectionStart ?? target.value.length;
        const end = target.selectionEnd ?? start;
        const insert = "\n" + PARAGRAPH_INDENT;
        target.value =
          target.value.slice(0, start) + insert + target.value.slice(end);
        const caret = start + insert.length;
        target.setSelectionRange(caret, caret);
        target.dispatchEvent(new Event("input", { bubbles: true }));
      }
    }
    watch(() => Boolean(state.editor), (open) => {
      document.body.classList.toggle("editor-open", open);
      if (open) nextTick(scheduleEditorResize);
    }, { immediate: true });
    onMounted(() => {
      document.addEventListener("input", onEditorInput, true);
      document.addEventListener("keydown", onEditorKeydown);
      window.addEventListener("resize", scheduleEditorResize);
    });
    onBeforeUnmount(() => {
      document.removeEventListener("input", onEditorInput, true);
      document.removeEventListener("keydown", onEditorKeydown);
      window.removeEventListener("resize", scheduleEditorResize);
    });
    watch(() => state.editor && [state.editor.key, state.editor.number, state.editor.title, state.editor.text], () => {
      const draft = state.editor;
      if (!draft) return;
      draft.report = null;
      draft.acknowledged = false;
      try {
        localStorage.setItem(draftKey(draft.key, draft.number), JSON.stringify({ title: draft.title, text: draft.text, base_revision: draft.base_revision }));
        state.draftStored = true;
        state.draftStatus = "草稿已保存在当前浏览器，提交后才会同步正文与记忆。";
      } catch { state.draftStored = false; state.draftStatus = "浏览器无法暂存草稿，请及时提交或复制保留文字。"; }
      scheduleEditorResize();
    }, { flush: "sync" });
    function applyTheme() {
      const dark = state.theme === "dark" ||
        (state.theme === "system" && systemTheme?.matches);
      document.documentElement.dataset.theme = dark ? "dark" : "light";
    }
    watch(() => state.theme, () => {
      applyTheme();
      try {
        localStorage.setItem("tome-theme", state.theme);
      } catch {}
    }, { immediate: true, flush: "sync" });
    systemTheme?.addEventListener("change", applyTheme);
    onBeforeUnmount(() => systemTheme?.removeEventListener("change", applyTheme));

    let navigationVersion = 0,
      libraryVersion = 0,
      trashVersion = 0,
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
        (f) => f.status === "active" && !isEventFact(f),
      ),
    );
    const factGroups = computed(() => {
      const groups = new Map();
      for (const fact of facts.value) {
        const category = memoryCategory(fact), number = Number(fact.source?.chapter_number) || 0;
        const excerpt = category === "chapters";
        const key = excerpt ? "chapter:" + number : category + ":" + fact.subject;
        const source = chapters.value.find(c => Number(c.number) === number);
        if (!groups.has(key)) groups.set(key, { key, category, number: excerpt ? number : null,
          label: excerpt ? "第" + (number || "—") + "章 · " + (source?.title || "章节摘录") : String(fact.label || fact.subject || "未命名主题"), facts: [] });
        groups.get(key).facts.push(fact);
      }
      return [...groups.values()].sort((a, b) => a.category === "chapters" && b.category === "chapters"
        ? a.number - b.number : a.label.localeCompare(b.label, "zh-CN"));
    });
    const memoryCategories = computed(() => MEMORY_CATEGORIES.map(category => ({
      ...category,
      groups: factGroups.value.filter(group => group.category === category.key),
      visible: factGroups.value.filter(group => group.category === category.key &&
        group.label.toLocaleLowerCase().includes(state.memoryFilter.trim().toLocaleLowerCase())),
    })));
    const filteredChapters = computed(() => chapters.value.map((item, index) => ({ ...item, index }))
      .filter(item => (item.number + " " + item.title).toLocaleLowerCase().includes(state.chapterFilter.trim().toLocaleLowerCase())));
    const searchResults = computed(() => searchChapters(chapters.value, state.searchTerm));
    const readerMatch = computed(() => {
      const match = state.searchMatch, current = chapter.value;
      return current && match && Number(current.number) === Number(match.number) &&
        String(current[match.field] || "").slice(match.start, match.end) === match.match ? match : null;
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
        Boolean(state.editor) ||
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
          `${job?.count ? `本批次已完成 ${job.completed || 0} / ${job.count} 章，正在生成第 ${job.current_chapter} 章。` : "已提交，正在生成。"}${typeof job?.live_units === "number" ? `本章已完成片段约 ${fmt(job.live_completed_units)} 字。${job.live_output_number ? `第 ${job.live_output_number} 次输出：` : ""}${job.live_unit_number ? `第 ${job.live_unit_number}${job.live_unit_total ? ` / ${job.live_unit_total}` : ""} 段` : "当前片段"}${typeof job.live_draft_units === "number" ? `草稿约 ${fmt(job.live_draft_units)} 字，正在调整，调整内容已接收约 ${fmt(job.live_units)} 字` : `已接收约 ${fmt(job.live_units)} 字，${job.live_phase === "writing" ? "正在生成" : "正在整理"}`}；正文尚未存档，可能调整。` : "正在准备正文。"}可刷新页面，完成后自动显示正文。`
        );
      return error
        ? `生成停止：${error}。已保存章节仍可阅读和导出。`
        : complete.value
          ? "所有目标章节已存档，可导出作品。"
          : job?.status === "completed"
            ? `✓ 本批次 ${job.count || 1} 章已生成并存档。`
            : "";
    });
    const jobLevel = computed(() => {
      if (state.jobErrors[id.value]) return running.value ? "warning" : "error";
      return !running.value && (complete.value || state.current?.job?.status === "completed") ? "success" : "info";
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
    const notify = (message, type = "info") => {
      state.notice = message || "";
      state.noticeType = message && Object.hasOwn(MESSAGE_LABELS, type) ? type : "info";
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
    function closeBookMenu() { state.menuId = null; }
    function toggleSidebar() {
      state.sidebarCollapsed = !state.sidebarCollapsed;
      try {
        localStorage.setItem(
          "tome-sidebar-collapsed",
          String(state.sidebarCollapsed),
        );
      } catch {}
    }
    function showHome() {
      if (!leaveEditor()) return;
      navigationVersion++;
      state.current = null;
      state.view = "home";
      state.menuId = null;
      notify();
      window.scrollTo({ top: 0, left: 0 });
    }
    function showLibrary() {
      if (!leaveEditor()) return;
      navigationVersion++;
      state.current = null;
      state.view = "library";
      state.menuId = null;
      notify();
      window.scrollTo({ top: 0, left: 0 });
      refreshBooks().catch((e) => notify(e.message, "error"));
    }
    function closeDialog(name) {
      if (state.busy[name] || (name === "estimate" && state.busy.start)) return;
      state.dialogs[name] = false;
      if (name === "api") state.apiKey = "";
      if (name === "estimate") state.estimate = null;
      if (name === "regenerate") state.regeneration = null;
      if (name === "review") state.exportReview = null;
      if (name === "delete") state.deleteBook = null;
      if (name === "purge") {
        state.purgeBook = null;
        state.purgeTitle = "";
      }
    }
    function openApiConfig() {
      state.apiKey = "";
      state.errors.api = "";
      state.dialogs.settings = false;
      state.dialogs.api = true;
    }
    function openCreate() {
      if (!leaveEditor()) return;
      if (!state.configured) return openApiConfig();
      state.errors.create = "";
      state.dialogs.create = true;
    }
    function selectProvider(slot) {
      if (state.providerSlot === slot) return;
      state.providerDrafts[state.providerSlot] = { ...state.modelForm };
      state.providerSlot = slot;
      const preset = PROVIDER_PRESETS.find((item) => item.id === slot);
      state.modelForm = state.providerDrafts[slot] ? { ...state.providerDrafts[slot] } : {
        provider: preset?.provider || "compatible",
        providerName: preset?.name || "",
        model: preset?.model || "",
        endpoint: preset?.endpoint || "",
      };
      state.apiKey = "";
      state.errors.api = "";
    }
    function registerCustomProviderSlot() {
      let number = 1;
      while (state.customProviders.includes(`custom-${number}`)) number++;
      const slot = `custom-${number}`;
      state.customProviders.push(slot);
      return slot;
    }
    function addCustomProvider() {
      selectProvider(registerCustomProviderSlot());
    }
    function removeCustomProvider(slot) {
      if (!state.customProviders.includes(slot)) return;
      const removed = state.providerSlot === slot ? state.modelForm : state.providerDrafts[slot];
      if (removed && state.activeProvider && removed.providerName === state.activeProvider.providerName && removed.endpoint === state.activeProvider.endpoint) {
        try { localStorage.setItem("tome-hidden-active-provider", JSON.stringify(state.activeProvider)); } catch {}
      }
      if (state.providerSlot === slot) {
        state.providerSlot = "deepseek";
        state.modelForm = state.providerDrafts.deepseek ? { ...state.providerDrafts.deepseek } : {
          provider: "deepseek", providerName: "DeepSeek", model: "deepseek-chat", endpoint: "",
        };
        state.apiKey = "";
        state.errors.api = "";
      }
      state.customProviders = state.customProviders.filter((item) => item !== slot);
      delete state.providerDrafts[slot];
      saveCustomProviders();
    }
    function saveCustomProviders() {
      const records = state.customProviders.map((slot) => {
        const draft = slot === state.providerSlot ? state.modelForm : state.providerDrafts[slot];
        return draft && { providerName: draft.providerName, model: draft.model, endpoint: draft.endpoint };
      }).filter((draft) => draft && draft.providerName && draft.model && draft.endpoint);
      try {
        localStorage.setItem("tome-custom-providers", JSON.stringify(records));
        const presets = {};
        for (const item of PROVIDER_PRESETS) {
          const draft = item.id === state.providerSlot ? state.modelForm : state.providerDrafts[item.id];
          if (draft && draft.model && (draft.provider !== "compatible" || draft.endpoint)) presets[item.id] = { provider: draft.provider, providerName: draft.providerName, model: draft.model, endpoint: draft.endpoint };
        }
        localStorage.setItem("tome-provider-presets", JSON.stringify(presets));
      } catch {}
    }
    async function configure() {
      if (state.busy.api) return;
      state.busy.api = true;
      state.errors.api = "";
      try {
        const form = state.modelForm;
        const payload = { provider: form.provider, provider_name: form.providerName.trim(), model: form.model.trim(), endpoint: form.endpoint.trim(), api_key: state.apiKey.trim() };
        await api("/api/model-test", payload);
        const cfg = await api("/api/model-config", payload);
        state.configured = cfg.configured;
        state.model = cfg.model;
        state.modelForm = modelFormFromConfig(cfg);
        state.activeProvider = { providerName: cfg.provider_name, endpoint: cfg.endpoint };
        try { localStorage.removeItem("tome-hidden-active-provider"); } catch {}
        saveCustomProviders();
        state.apiKey = "";
        state.dialogs.api = false;
        notify("API Key 已保存，可以开始创作。", "success");
      } catch (e) {
        state.errors.api = e.message;
      } finally {
        state.busy.api = false;
      }
    }
    async function refreshBooks() {
      const version = ++libraryVersion;
      const [books] = await Promise.all([api("/api/books"), refreshTrash()]);
      if (disposed || version !== libraryVersion) return;
      state.books = books.books;
    }
    async function refreshTrash() {
      const version = ++trashVersion;
      state.trashLoading = true;
      state.trashError = "";
      try {
        const result = await api("/api/books/trash");
        if (!disposed && version === trashVersion) state.trash = result.books;
      } catch (e) {
        if (!disposed && version === trashVersion) state.trashError = e.message || "请稍后重试。";
      } finally {
        if (!disposed && version === trashVersion) state.trashLoading = false;
      }
    }
    function acceptBook(book, latest = false) {
      const same = id.value === book.state.project_id;
      if (!same) {
        clearBookSearch();
        state.memoryFilter = "";
        state.chapterPickerOpen = false;
      }
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
      const summary = state.books.find((item) => item.id === key);
      if (summary) summary.chapters = book.state.chapters.length;
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
      if (!leaveEditor()) return;
      if (state.pending.has(key)) return;
      const version = ++navigationVersion;
      state.pending.add(key);
      state.menuId = null;
      try {
        const book = await api(bookUrl(key));
        if (disposed || version !== navigationVersion) return;
        acceptBook(book);
        state.view = "book";
        notify();
        // 侧栏计数在后台刷新，不阻塞这次点击
        refreshBooks().catch(() => {});
      } catch (e) {
        if (version === navigationVersion) notify(e.message, "error");
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
            skills: [...f.skills],
          });
        state.dialogs.create = false;
        state.createForm = {
          title: "",
          prompt: "",
          chapters: 10,
          target_units: 10000,
          instructions: "",
          reference: "",
          skills: [],
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
        notify(e.message, "error");
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
    function openTrash() {
      state.trashMessage = "";
      state.dialogs.trash = true;
      if (!state.trashLoading) refreshTrash();
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
        try {
          for (let i = localStorage.length - 1; i >= 0; i--) {
            const key = localStorage.key(i);
            if (key?.startsWith(`tome-chapter-draft:${book.book_id}:`)) localStorage.removeItem(key);
          }
        } catch {}
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
    function closeChapterPicker() { state.chapterPickerOpen = false; }
    async function toggleChapterPicker() {
      state.chapterPickerOpen = !state.chapterPickerOpen;
      if (state.chapterPickerOpen) {
        state.chapterFilter = "";
        await nextTick();
        document.getElementById("chapter-filter")?.focus();
      }
    }
    async function chooseChapter(index, match = null) {
      if (!Number.isInteger(index) || index < 0 || index >= chapters.value.length || !leaveEditor()) return;
      state.chapterIndex = index;
      state.searchMatch = match;
      closeChapterPicker();
      await nextTick();
      const body = document.getElementById("chapter-body");
      const target = match ? body?.querySelector(".search-hit-active") || body : body;
      target?.scrollIntoView({ block: match ? "center" : "start" });
      body?.focus({ preventScroll: true });
    }
    function turnChapter(direction) { return chooseChapter(state.chapterIndex + direction); }
    function submitBookSearch() {
      state.searchTerm = state.searchQuery.trim();
      state.searchMatch = null;
    }
    function clearBookSearch() {
      state.searchQuery = "";
      state.searchTerm = "";
      state.searchMatch = null;
    }
    function jumpToSearch(item) { return chooseChapter(item.index, item); }
    function jumpToFact(fact) {
      const index = chapters.value.findIndex(c => Number(c.number) === Number(fact.source?.chapter_number));
      if (index < 0) { notify("该条记忆的来源章节暂不可用。", "warning"); return; }
      const text = chapters.value[index].text, quote = fact.source?.quote || valueOf(fact);
      const start = quote ? text.indexOf(quote) : -1;
      return chooseChapter(index, start >= 0 ? {
        number: chapters.value[index].number, field: "text", start, end: start + quote.length, match: quote,
      } : null);
    }

    async function uploadCover(event) {
      const input = event.target;
      const file = input.files?.[0];
      const key = id.value;
      if (!file || !key) return;
      if (!['image/png', 'image/jpeg', 'image/webp'].includes(file.type) || file.size > 2 * 1024 * 1024) {
        notify('请选择不超过 2 MB 的 PNG、JPEG 或 WebP 图片。', 'warning');
        input.value = '';
        return;
      }
      state.busy.cover = true;
      try {
        const encoded = await new Promise((resolve, reject) => {
          const reader = new FileReader();
          reader.onload = () => resolve(String(reader.result).split(',')[1]);
          reader.onerror = () => reject(new Error('无法读取图片。'));
          reader.readAsDataURL(file);
        });
        const result = await api(`${bookUrl(key)}/cover`, { image: encoded });
        if (id.value === key) state.current.cover_version = result.cover_version;
        const summary = state.books.find((book) => book.id === key);
        if (summary) summary.cover_version = result.cover_version;
        await refreshBooks();
        notify('封面已保存。', 'success');
      } catch (error) {
        notify(error.message, "error");
      } finally {
        input.value = '';
        state.busy.cover = false;
      }
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
    async function installSkill(event) {
      const input = event.target;
      const file = input.files?.[0];
      if (!file) return;
      state.busy.skill = true;
      try {
        if (file.size > 48000) throw new Error("技能文件过大");
        const content = await file.text();
        const match = content.match(/^---\s*\r?\n[\s\S]*?^name:\s*([^\r\n]+)$/m);
        const name = (match?.[1] || file.name.replace(/\.md$/i, "")).replace(/^['"]|['"]$/g, "").trim();
        const result = await api("/api/skills", {name, content});
        state.skills.push(result.skill);
        notify("技能已安装，请为作品选择后使用。", "success");
      } catch (e) { notify(e.message, "error"); }
      finally { input.value = ""; state.busy.skill = false; }
    }
    async function selectSkills(event) {
      const key = id.value;
      if (!key) return;
      const selected = [...event.currentTarget.querySelectorAll('input[type="checkbox"]:checked')].map(x => x.value);
      try {
        const result = await api(`${bookUrl(key)}/skills`, {skills: selected});
        if (id.value === key) state.current.skills = result.skills;
      } catch (e) { notify(e.message, "error"); event.target.checked = !event.target.checked; }
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
        state.privacyConfirmed = false;
        state.estimateTitle = meta.value.title;
        state.errors.estimate = "";
        state.dialogs.estimate = true;
      } catch (e) {
        notify(e.message, "error");
      } finally {
        state.busy.estimate = false;
      }
    }
    async function confirmGeneration() {
      const estimate = state.estimate;
      if (!estimate || state.busy.start || estimate.safety?.blocked ||
          (estimate.safety?.requires_confirmation && !state.privacyConfirmed)) return;
      state.busy.start = true;
      state.errors.estimate = "";
      try {
        const { job_id } = await api(`${bookUrl(estimate.book_id)}/generate`, {
          estimate_id: estimate.estimate_id,
          confirmed: true,
          privacy_confirmed: state.privacyConfirmed,
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
        if (e.safety) { state.estimate.safety = e.safety; state.privacyConfirmed = false; }
      } finally {
        state.busy.start = false;
      }
    }
    function openEditor(number = chapter.value?.number) {
      if (running.value || state.busy.edit || state.busy.proofread) return;
      const source = chapters.value.find(item => item.number === number);
      if (!source) return;
      navigationVersion++;
      state.chapterIndex = chapters.value.findIndex(item => item.number === number);
      let saved = null;
      try { saved = JSON.parse(localStorage.getItem(draftKey(id.value, number)) || "null"); } catch {}
      const restored = saved && typeof saved.title === "string" && typeof saved.text === "string";
      state.editError = "";
      state.editor = {
        key: id.value, number, title: restored ? saved.title : source.title,
        text: normalizeParagraphIndent(
          (restored ? saved.text : source.text).replace(/\r\n?/g, "\n"),
        ),
        base_revision: restored ? saved.base_revision : state.current.edit_revision,
        report: null, acknowledged: false,
      };
      if (restored && saved.base_revision !== state.current.edit_revision)
        state.editError = "检测到旧草稿：作品已更新，请先复制保留，再丢弃旧草稿并重新编辑。";
    }
    function leaveEditor() {
      if (state.busy.edit || state.busy.proofread) return false;
      if (state.editor && !state.draftStored) { notify("草稿尚未保存，请先提交或复制保留文字。", "warning"); return false; }
      state.editor = null;
      return true;
    }
    function closeEditor() { leaveEditor(); }
    function discardDraft() {
      const draft = state.editor;
      if (!draft || state.busy.edit || state.busy.proofread) return;
      state.editor = null;
      try { localStorage.removeItem(draftKey(draft.key, draft.number)); } catch {}
      state.editError = "";
    }
    async function proofreadDraft() {
      const draft = state.editor;
      if (!draft || state.busy.proofread) return null;
      state.busy.proofread = true;
      state.editError = "";
      try {
        const report = await api(`${bookUrl(draft.key)}/chapters/${draft.number}/review`, {title: draft.title, text: draft.text});
        if (state.editor !== draft) return null;
        draft.report = report;
        draft.acknowledged = false;
        return report;
      } catch (e) { state.editError = e.message; return null; }
      finally { state.busy.proofread = false; }
    }
    async function saveEditedChapter() {
      const draft = state.editor;
      if (!draft || state.busy.edit || state.busy.proofread || running.value) return;
      const report = draft.report || await proofreadDraft();
      if (!report || state.editor !== draft) return;
      if (report.blocked || (report.total && !draft.acknowledged)) {
        state.editError = report.blocked ? "请先移除疑似密钥，再重新复查。" : "请核对提示并勾选确认后再提交。";
        return;
      }
      state.busy.edit = true;
      try {
        const result = await api(`${bookUrl(draft.key)}/chapters/${draft.number}/edit`, {
          title: draft.title, text: draft.text, base_revision: draft.base_revision,
          review_revision: report.revision, acknowledged: draft.acknowledged,
        });
        state.editor = null;
        try { localStorage.removeItem(draftKey(draft.key, draft.number)); } catch {}
        acceptBook(result.book);
        state.chapterIndex = chapters.value.findIndex(item => item.number === draft.number);
        await refreshBooks();
        notify("正文已保存，记忆已按修订正文同步，后续续写使用新稿。", "success");
      } catch (e) { state.editError = e.message; }
      finally { state.busy.edit = false; }
    }
    async function locateFinding(item) {
      state.dialogs.review = false;
      state.exportReview = null;
      if (!state.editor || state.editor.number !== item.chapter) openEditor(item.chapter);
      await nextTick();
      const input = document.getElementById(item.field === "title" ? "chapter-edit-title" : "chapter-edit-text");
      input?.focus();
      input?.setSelectionRange(item.start, item.end);
      if (input?.tagName === "TEXTAREA") {
        // Textarea selection APIs do not reliably reveal a distant match.
        // Measure the prefix with matching wrapping, then center that line.
        const mirror = document.createElement("div"), css = getComputedStyle(input);
        for (const prop of ["fontFamily", "fontSize", "fontWeight", "fontStyle", "lineHeight", "letterSpacing", "wordSpacing", "paddingTop", "paddingRight", "paddingBottom", "paddingLeft", "tabSize", "textIndent", "whiteSpace", "overflowWrap", "wordBreak"])
          mirror.style[prop] = css[prop];
        Object.assign(mirror.style, { position: "fixed", visibility: "hidden", pointerEvents: "none", left: "-100000px", top: "0", width: `${input.clientWidth}px`, boxSizing: "border-box", border: "0", height: "auto" });
        const marker = document.createElement("span");
        marker.textContent = input.value.slice(item.start, item.end) || "\u200b";
        mirror.append(document.createTextNode(input.value.slice(0, item.start)), marker);
        document.body.append(mirror);
        const offset = marker.getBoundingClientRect().top - mirror.getBoundingClientRect().top;
        const scroller = input.closest(".editor-scroll");
        if (scroller) {
          const top = input.getBoundingClientRect().top - scroller.getBoundingClientRect().top + scroller.scrollTop + offset;
          scroller.scrollTop = Math.max(0, top - scroller.clientHeight / 2);
        } else {
          input.scrollTop = Math.max(0, offset - input.clientHeight / 2);
        }
        mirror.remove();
        return;
      }
      input?.scrollIntoView({ block: "center", behavior: "smooth" });
    }
    async function applyProofreading(item) {
      if (item.replacement === null) return locateFinding(item);
      if (!state.editor || state.editor.number !== item.chapter) { await locateFinding(item); return; }
      const draft = state.editor;
      if (!draft.report) return;
      const field = item.field === "title" ? "title" : "text";
      draft[field] = draft[field].slice(0, item.start) + item.replacement + draft[field].slice(item.end);
      await nextTick();
      document.getElementById(field === "title" ? "chapter-edit-title" : "chapter-edit-text")?.focus();
    }
    async function reviewForExport() {
      if (!id.value || state.busy.review) return;
      if (state.editor) { state.editError = "请先提交本地修改，再复查导出。"; return; }
      state.busy.review = true;
      state.reviewError = "";
      try {
        const key = id.value, report = await api(`${bookUrl(key)}/review`, {});
        if (key !== id.value) return;
        state.exportReview = { key, report, acknowledged: false };
        state.dialogs.review = true;
      } catch (e) { notify(e.message, "error"); }
      finally { state.busy.review = false; }
    }
    async function exportReviewed() {
      const draft = state.exportReview;
      if (!draft || state.busy.export || draft.report.blocked || (draft.report.total && !draft.acknowledged)) return;
      state.busy.export = true;
      state.reviewError = "";
      try {
        const response = await fetch(`${bookUrl(draft.key)}/export`, {method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({review_revision: draft.report.revision, acknowledged: draft.acknowledged})});
        if (!response.ok) { const result = await response.json(); throw new Error(result.error || "导出失败"); }
        const url = URL.createObjectURL(await response.blob());
        const link = document.createElement("a"); link.href = url; link.download = `${titleOf(state.current)}.md`;
        document.body.append(link); link.click(); link.remove();
        setTimeout(() => URL.revokeObjectURL(url), 10000);
        state.dialogs.review = false; state.exportReview = null;
      } catch (e) { state.reviewError = e.message; }
      finally { state.busy.export = false; }
    }
    function openRegeneration() {
      const key = id.value;
      const chapter = chapters.value[state.chapterIndex];
      if (!key || !chapter || running.value || state.busy.regenerate) return;
      state.errors.regenerate = "";
      state.regeneration = {
        key,
        number: chapter.number,
        later: chapters.value.length - chapter.number,
        feedback: "",
        safety: null,
        privacyConfirmed: false,
      };
      state.dialogs.regenerate = true;
    }
    async function regenerateChapter() {
      const draft = state.regeneration;
      if (!draft || draft.key !== id.value || running.value || state.busy.regenerate) return;
      const { key, number } = draft;
      const feedback = draft.feedback.trim();
      if (draft.safety?.blocked || (draft.safety?.requires_confirmation && !draft.privacyConfirmed)) return;
      if (!feedback) {
        state.errors.regenerate = "请填写希望调整的内容。";
        return;
      }
      state.busy.regenerate = true;
      state.errors.regenerate = "";
      try {
        const { job_id } = await api(
          `${bookUrl(key)}/chapters/${number}/regenerate`,
          { confirmed: true, author_feedback: feedback, privacy_confirmed: draft.privacyConfirmed },
        );
        state.dialogs.regenerate = false;
        state.regeneration = null;
        state.jobs[key] = job_id;
        delete state.jobErrors[key];
        if (id.value === key)
          state.current.job = {
            count: 1,
            completed: 0,
            current_chapter: number,
          };
        startPolling(key, job_id);
        notify("已开始重新生成，请稍候。");
      } catch (e) {
        state.errors.regenerate = e.message;
        if (e.safety) { draft.safety = e.safety; draft.privacyConfirmed = false; }
      } finally {
        state.busy.regenerate = false;
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
          notify(job.error, "error");
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
            notify(error.message, "error");
          }
          notify("任务状态已失效，已重新读取作品存档。请确认正文后再提交。", "warning");
          return;
        }
        if (polling.has(jobId)) {
          state.jobErrors[key] = "状态连接暂时中断，正在重连；请勿重复提交。";
          schedule(key, jobId, 3000);
        }
      }
    }
    function restoreProviderDrafts() {
      const presets = readProviderPreference("tome-provider-presets", {});
      for (const preset of PROVIDER_PRESETS) {
        const draft = presets[preset.id];
        if (draft?.provider !== preset.provider ||
            typeof draft.model !== "string" || typeof draft.endpoint !== "string") continue;
        state.providerDrafts[preset.id] = {
          provider: preset.provider, providerName: preset.name, model: draft.model, endpoint: draft.endpoint,
        };
      }

      const custom = readProviderPreference("tome-custom-providers", []);
      if (!Array.isArray(custom)) return;
      const valid = custom.filter((entry) =>
        typeof entry?.providerName === "string" && typeof entry.model === "string" && typeof entry.endpoint === "string",
      );
      for (const { providerName, model, endpoint } of valid.slice(0, 100)) {
        const slot = registerCustomProviderSlot();
        state.providerDrafts[slot] = { provider: "compatible", providerName, model, endpoint };
      }
    }
    function modelFormFromConfig(config) {
      const preset = PROVIDER_PRESETS.find((item) => item.id === config.provider);
      return {
        provider: config.provider,
        providerName: config.provider_name || preset?.name || "自定义",
        model: config.model,
        endpoint: config.provider === "compatible" ? config.endpoint : "",
      };
    }
    function compatibleProviderSlot(config) {
      const preset = PROVIDER_PRESETS.find((item) =>
        item.provider === "compatible" && item.name === config.provider_name,
      );
      if (preset) return preset.id;
      const existing = state.customProviders.find((slot) => {
        const draft = state.providerDrafts[slot];
        return draft?.endpoint === config.endpoint && draft?.providerName === config.provider_name;
      });
      return existing || registerCustomProviderSlot();
    }
    async function restoreActiveModel() {
      const config = await api("/api/model-config");
      if (!config.provider) return;
      state.activeProvider = { providerName: config.provider_name, endpoint: config.endpoint };
      const hidden = readProviderPreference("tome-hidden-active-provider", null);
      const compatible = config.provider === "compatible";
      if (compatible && hidden && hidden.providerName === config.provider_name &&
          hidden.endpoint === config.endpoint) return;
      state.providerSlot = compatible ? compatibleProviderSlot(config) : config.provider;
      state.modelForm = modelFormFromConfig(config);
    }
    watch(
      () => [state.view, state.current?.state?.project_id, chapter.value?.number],
      ([view, bookId, chapterNumber]) => {
        try {
          sessionStorage.setItem(navigationKey, JSON.stringify({ view, bookId, chapterNumber }));
        } catch {}
      },
    );
    onMounted(async () => {
      try {
        localStorage.removeItem("tome-selected-book");
        localStorage.removeItem("tome-last-deleted");
      } catch {}
      restoreProviderDrafts();
      try {
        const cfg = await api("/api/config");
        state.configured = cfg.configured;
        state.model = cfg.model;
        try {
          await restoreActiveModel();
        } catch { /* Keep defaults when connecting to an older server. */ }
        if (!cfg.configured) openApiConfig();
        await refreshBooks();
        if (previousNavigation?.view === "library") {
          state.view = "library";
        } else if (previousNavigation?.view === "book" &&
                   state.books.some((book) => book.id === previousNavigation.bookId)) {
          await selectBook(previousNavigation.bookId);
          if (id.value === previousNavigation.bookId) {
            const index = chapters.value.findIndex((item) => item.number === previousNavigation.chapterNumber);
            if (index >= 0) state.chapterIndex = index;
          }
        }
        try { state.skills = (await api("/api/skills")).skills; }
        catch (e) { notify(`技能列表加载失败：${e.message}`, "warning"); }
      } catch (e) {
        state.connectionError = true;
        notify(e.message, "error");
      } finally {
        state.restoringNavigation = false;
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
      memoryCategories, filteredChapters, searchResults, readerMatch,
      toggleChapterPicker, closeChapterPicker, chooseChapter, submitBookSearch, clearBookSearch, jumpToSearch, jumpToFact,
      factTopic,
      selectedFacts,
      units,
      generationDisabled,
      generateLabel,
      jobStatus,
      jobLevel,
      messageLabels: MESSAGE_LABELS,
      connectionText,
      breadcrumb,
      sidebarHidden,
      noticePanel,
      titleOf,
      bookUrl,
      uploadCover,
      turnChapter,
      openEditor, closeEditor, discardDraft, proofreadDraft, saveEditedChapter, locateFinding, applyProofreading, reviewForExport, exportReviewed,
      fmt,
      cost,
      price,
      deletedAt,
      toggleSidebar,
      closeBookMenu,
      openApiConfig,
      showHome,
      showLibrary,
      closeDialog,
      openCreate,
      configure,
      providerPresets: PROVIDER_PRESETS,
      selectProvider,
      addCustomProvider,
      removeCustomProvider,
      createBook,
      selectBook,
      pinBook,
      requestDelete,
      deleteBook,
      openTrash,
      refreshTrash,
      restoreBook,
      requestPurge,
      purgeBook,
      approveFirst,
      submitStyle,
      installSkill,
      selectSkills,
      prepareGeneration,
      confirmGeneration,
      openRegeneration,
      regenerateChapter,
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
const floatingMenuCleanup = new WeakMap();
app.directive("floating-menu", {
  mounted(el, { value }) {
    const anchor = document.getElementById(value.anchorId);
    if (!anchor) { value.close(); return; }
    // Teleport escapes scroll clipping; Popover puts supporting browsers in
    // the native top layer. Fixed positioning remains the fallback.
    if (typeof el.showPopover === "function") el.showPopover();
    const place = () => {
      if (!anchor.isConnected) { value.close(); return; }
      const rect = anchor.getBoundingClientRect();
      const shelf = anchor.closest("#book-list")?.getBoundingClientRect();
      if (shelf && (rect.bottom <= Math.max(0, shelf.top) || rect.top >= Math.min(innerHeight, shelf.bottom) ||
          rect.right <= Math.max(0, shelf.left) || rect.left >= Math.min(innerWidth, shelf.right))) {
        value.close(); return;
      }
      const gap = 8;
      if (value.matchAnchorWidth) el.style.width = `${rect.width}px`;
      const menu = el.getBoundingClientRect();
      const below = innerHeight - rect.bottom, above = rect.top;
      const top = below >= menu.height + gap || below >= above
        ? rect.bottom + 4 : rect.top - menu.height - 4;
      el.style.left = `${Math.max(gap, Math.min(rect.right - menu.width, innerWidth - menu.width - gap))}px`;
      el.style.top = `${Math.max(gap, Math.min(top, innerHeight - menu.height - gap))}px`;
    };
    const outside = (event) => {
      if (!el.contains(event.target) && !anchor.contains(event.target)) value.close();
    };
    const keyboard = (event) => {
      if (event.key === "Escape") {
        event.preventDefault(); value.close(); anchor.focus({ preventScroll: true });
      } else if (event.key === "Tab" && el.contains(document.activeElement)) {
        const controls = [...el.querySelectorAll("button:not(:disabled)")];
        if ((event.shiftKey && document.activeElement === controls[0]) ||
            (!event.shiftKey && document.activeElement === controls.at(-1))) {
          value.close(); anchor.focus({ preventScroll: true });
        }
      }
    };
    place();
    document.addEventListener("pointerdown", outside);
    document.addEventListener("keydown", keyboard);
    window.addEventListener("scroll", place, true);
    window.addEventListener("resize", place);
    const observer = typeof ResizeObserver === "function" ? new ResizeObserver(place) : null;
    observer?.observe(anchor);
    observer?.observe(el);
    floatingMenuCleanup.set(el, () => {
      document.removeEventListener("pointerdown", outside);
      document.removeEventListener("keydown", keyboard);
      window.removeEventListener("scroll", place, true);
      window.removeEventListener("resize", place);
      observer?.disconnect();
    });
    el.querySelector("button:not(:disabled)")?.focus({ preventScroll: true });
  },
  beforeUnmount(el) {
    floatingMenuCleanup.get(el)?.();
    floatingMenuCleanup.delete(el);
  },
});
app.mount("#tome-app");
