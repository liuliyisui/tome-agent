"""Local author workbench. Model calls require explicit button clicks."""
import json
import streamlit as st
from tome_backend.checkpoints import load_checkpoint
from tome_backend.providers.deepseek import Settings
from tome_backend.service import (book_path, create_book, generate, list_books,
                                export_markdown, update_outline, new_book_id, book_labels)
from tome_agent.agent import count_units
from tome_agent.state import Workspace

st.set_page_config(page_title="Tome Agent · 长篇创作", page_icon="📖", layout="wide")
st.title("Tome Agent")
st.caption("从故事构想到连贯长篇 · 分层规划 / 跨章记忆 / 保存续写")

with st.sidebar:
    st.subheader("模型配置")
    try:
        cfg = Settings.load(require_key=False)
        st.write(f"模型：{cfg.model}")
        st.write("密钥：已配置" if cfg.api_key else "密钥：尚未配置")
        st.caption("在项目 .env 填写密钥，不会在页面显示。")
        st.caption(f"每次操作最多 {cfg.max_requests} 请求 / {cfg.max_total_tokens:,} token；单次响应可能使软预算超限。")
    except (ValueError, TypeError):
        st.error("配置格式有误，请检查 .env。")
    st.divider()
    books = list_books()
    labels = book_labels(books)
    next_book = st.session_state.pop("open_book_next", None)
    if next_book in books:
        st.session_state["active_book"] = next_book
    active = st.selectbox("打开作品", [None, *books], key="active_book",
                          format_func=lambda book_id: "新建作品" if book_id is None else labels[book_id])


def report_error(exc):
    if isinstance(exc, (ValueError, RuntimeError)):
        st.error(str(exc))
    else:
        st.error(f"操作未完成（{type(exc).__name__}），请检查配置、网络和存档。")


@st.cache_data(show_spinner=False, max_entries=8, ttl=600)
def export_payloads(snapshot):
    """Cache the displayed snapshot; never reread a newer checkpoint for export."""
    workspace = Workspace.from_dict(snapshot)
    return export_markdown(workspace), json.dumps(workspace.to_dict(), ensure_ascii=False, indent=2)


if active is None:
    st.subheader("规划一部小说")
    with st.form("new_book"):
        title = st.text_input("作品名称", "灯塔来信")
        prompt = st.text_area("故事构想、人物、世界观与写作要求", height=200,
                              placeholder="描述主角、核心冲突、情节方向、叙述视角和风格。")
        left, right = st.columns(2)
        chapters = left.number_input("章节数", 1, 100, 8)
        target = right.number_input("目标篇幅（中文字 / 英文词计数）", 500, 200000, 10000, 500)
        approved = st.checkbox("我确认生成大纲会调用 DeepSeek 并产生费用")
        start = st.form_submit_button("生成分层大纲", type="primary")
    if start:
        if not approved:
            st.warning("请先确认模型调用费用。")
        else:
            try:
                with st.spinner("正在规划故事前提、详细梗概、幕结构与章节大纲…"):
                    # Keep the same internal identity on retry, without asking the author to manage it.
                    book_id = st.session_state.setdefault("new_book_id", new_book_id())
                    create_book(book_id, title, prompt, int(chapters), int(target))
                st.session_state.pop("new_book_id", None)
                st.session_state["open_book_next"] = book_id
                st.rerun()
            except Exception as exc:
                report_error(exc)
else:
    try:
        workspace = load_checkpoint(book_path(active))
    except Exception as exc:
        report_error(exc)
        st.stop()
    st.subheader(workspace.title)
    a, b, c = st.columns(3)
    a.metric("完成章节", f"{len(workspace.chapters)} / {len(workspace.outline)}")
    b.metric("当前篇幅", sum(count_units(t) for t in workspace.chapters.values()))
    c.metric("当前事实", len([f for f in workspace.state.facts.values() if f["status"] == "active"]))
    write_tab, outline_tab, memory_tab, export_tab = st.tabs(["续写", "故事与大纲", "故事记忆", "导出"])
    with write_tab:
        finished = len(workspace.chapters) >= len(workspace.outline)
        if finished:
            st.success("大纲中的所有章节已完成。")
        else:
            next_plan = workspace.outline[len(workspace.chapters)]
            st.write(f"下一章：{next_plan['title']}")
            st.write(next_plan["goal"])
            st.caption("每章完成即保存；模型在同一章节循环中更新记忆。当前版本自动提交通过校验的章节，尚未加入人工逐条审核模式。")
            count = st.number_input("本次最多生成章节数", 1, len(workspace.outline)-len(workspace.chapters), 1)
            resume = st.checkbox("继续上次失败的章节工作副本", value=False)
            turns = st.number_input("每章工具轮次上限（恢复时包含已用轮次）", 3, 100, 30)
            consent = st.checkbox("我确认本次续写会产生模型费用")
            if st.button("开始续写", type="primary", disabled=not consent):
                try:
                    with st.spinner("正在逐章生成，成功章节会自动保存…"):
                        generate(active, int(count), resume, int(turns))
                    st.rerun()
                except Exception as exc:
                    report_error(exc)
            st.caption("需要暂停时将本次章节数设为1。关闭页面不保证立即取消正在进行的请求；不要同时打开多个窗口生成同一作品。")
        for n, text in sorted(workspace.chapters.items(), reverse=True):
            with st.expander(f"第{n}章 · {workspace.outline[n-1]['title']}", expanded=n == len(workspace.chapters)):
                st.text(text)
    with outline_tab:
        st.write(workspace.prompt)
        outline_text = st.text_area("章节大纲 JSON（仅开始生成前可修改）", json.dumps(workspace.outline, ensure_ascii=False, indent=2), height=350)
        if st.button("保存大纲", disabled=bool(workspace.chapters)):
            try:
                update_outline(active, json.loads(outline_text))
                st.rerun()
            except Exception as exc:
                report_error(exc)
        # Hidden JSON is not sent to the browser until explicitly requested.
        if st.toggle("显示四阶段规划原始 JSON", key=f"planning-{active}"):
            st.json(workspace.planning, expanded=False)
    with memory_tab:
        st.caption("引文和版本检查不保证事实语义正确。历史版本与故事内时间并不等同。")
        view = workspace.state.view()
        st.subheader(f"当前事实（{len(view['facts'])}）")
        if view["facts"]:
            st.dataframe([{"主体": f["subject"], "属性": f["key"], "值": str(f["value"]),
                           "版本": f["revision"], "类别": f["category"], "认知": f["epistemic_status"],
                           "出处": f"第{f['evidence']['chapter']}章"} for f in view["facts"]],
                         hide_index=True)
        else:
            st.info("暂无已入库事实。")
        for label, entries in (("角色", view["characters"]), ("历史事件", view["past_events"])):
            if entries:
                st.markdown(f"**{label}**")
                for name, item in entries.items():
                    text = item.get("description") if isinstance(item, dict) else item
                    st.text(f"• {name}：{text}")
        requirements = view["future_requirements"]
        st.markdown("**未来义务 · 待完成**")
        pending = {key: item for key, item in requirements.items() if not item.get("resolved", False)}
        resolved = {key: item for key, item in requirements.items() if item.get("resolved", False)}
        if pending:
            for key, item in pending.items():
                st.text(f"• {key}：{item['description']}")
        else:
            st.caption("暂无待完成义务。")
        if resolved:
            with st.expander(f"已完成义务（{len(resolved)}）"):
                for key, item in resolved.items():
                    chapter = item.get("resolved_chapter")
                    source = f"第{chapter}章完成" if chapter is not None else "完成章节未记录"
                    st.text(f"• {key}：{item['description']}（{source}）")
        if workspace.state.history:
            st.subheader(f"历史归档（{len(workspace.state.history)}）")
            st.dataframe([{"主体": h["subject"], "属性": h["key"], "旧值": str(h["value"]),
                           "归档于": f"第{h['archived_by']['chapter']}章", "原因": h["archived_by"].get("reason", "")}
                          for h in workspace.state.history], hide_index=True)
        if st.toggle("显示事实账本原始 JSON", key=f"facts-{active}"):
            st.json(view, expanded=False)
            st.json(workspace.state.history, expanded=False)
    with export_tab:
        try:
            markdown_text, book_json = export_payloads(workspace.to_dict())
        except Exception as exc:
            report_error(exc)
        else:
            st.download_button("下载小说 Markdown", markdown_text, f"{active}.md", "text/markdown")
            st.download_button("下载作品数据 JSON", book_json, f"{active}.json", "application/json")
        st.caption("作品和创作记录保存在本机，导出文件可用于分享。")
