"""Placeholder titles must not escape into saved chapters or exports."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from inf_backend.service import export_markdown
from inf_writer.domain import canonical
from inf_writer.models import ModelReply
from memory_runtime.chapter_titles import clean_title, resolve_title
from memory_runtime.completion import PlanningOutputFailure, unplanned_packet
from memory_runtime.continuity import empty
from memory_runtime.event_first import verify
from memory_runtime.test_writing import Local, config
from memory_runtime.writing import WritingSession, load_resume


class ChapterTitleTests(unittest.TestCase):
    def test_normal_titles_preserved_without_model_call(self):
        gateway = Mock()
        self.assertEqual(resolve_title('南津关', '正文。', 2, gateway=gateway), '南津关')
        self.assertEqual(clean_title('续写传奇'), '续写传奇')
        gateway.complete.assert_not_called()

    def test_placeholder_and_duplicate_number_prefix_removed(self):
        for value in ('续写', '续写1', '续写 12', '第3章 续写3', '## 第三章 续写三', '第3章'):
            self.assertIsNone(clean_title(value), value)
        self.assertEqual(clean_title('## 第三章 南津关'), '南津关')

    def test_existing_outline_title_wins_before_any_model_call(self):
        gateway = Mock()
        self.assertEqual(resolve_title('续写3', '沈砚秋登船。', 3, '名单上的陌生人', gateway=gateway), '名单上的陌生人')
        gateway.complete.assert_not_called()

    def test_explicit_prose_heading_can_supply_title_without_changing_body(self):
        prose = '## 第三章 灯下的名单\n\n沈砚秋展开名单。'
        gateway = Mock()
        self.assertEqual(resolve_title('续写3', prose, 3, gateway=gateway), '灯下的名单')
        self.assertTrue(prose.startswith('## 第三章'))
        gateway.complete.assert_not_called()

    def test_missing_title_uses_one_bounded_title_request(self):
        gateway = Mock()
        gateway.complete.return_value = ModelReply('{"title":"灯下的名单"}', 12, 8, .0001)
        prose = '沈砚秋展开名单。' * 1000
        self.assertEqual(resolve_title('续写1', prose, 1, gateway=gateway), '灯下的名单')
        gateway.complete.assert_called_once()
        request = gateway.complete.call_args.args[0]
        self.assertEqual(request.role, 'chapter_title')
        self.assertEqual(request.max_output_tokens, 128)
        self.assertLessEqual(len(request.payload['prose_excerpt']), 4000)

    def test_title_errors_do_not_retry_or_block_saved_prose(self):
        for reply in ('{"title":"续写7"}', '{}', '{', '{"title":"甲","title":"乙"}', '{"title":42}'):
            gateway = Mock()
            gateway.complete.return_value = ModelReply(reply, 1, 1, 0)
            prose = '雾里的脚步停在门外，沈砚秋没有开门。'
            self.assertEqual(resolve_title('续写7', prose, 7, gateway=gateway), '雾里的脚步停在门外')
            gateway.complete.assert_called_once()
        gateway.complete.side_effect = RuntimeError('offline')
        self.assertEqual(resolve_title('续写7', prose, 7, gateway=gateway), '雾里的脚步停在门外')

    def test_fallback_packet_keeps_existing_title_and_valid_commit_hashes(self):
        packet = unplanned_packet(empty(), 3, '继续', title='江心的第二声汽笛')
        original = copy.deepcopy(packet)
        self.assertEqual(packet['proposal']['title'], '江心的第二声汽笛')
        verify(packet['commit'])
        resolve_title('续写3', '正文。', 3, packet['proposal']['title'])
        self.assertEqual(packet, original)
        self.assertNotIn('续写', unplanned_packet(empty(), 3, '继续')['proposal']['title'])

    def test_planning_failure_saved_title_and_export_use_generated_title(self):
        class Provider(Local):
            def complete(self, request):
                if request.role == 'chapter_title':
                    self.requests.append(request)
                    return ModelReply('{"title":"名单之外"}', 1, 1, 0)
                if request.role == 'writer':
                    self.requests.append(request)
                    return ModelReply('沈砚秋发现名单上多了一个名字。', 1, 1, 0)
                return super().complete(request)
        with tempfile.TemporaryDirectory() as folder:
            session = WritingSession(Path(folder) / 'run', Provider(), dict(config(1), event_first=True))
            with patch.object(session, '_prepare_events', side_effect=PlanningOutputFailure('offline malformed plan')):
                row = session.write_next('继续')
            self.assertIsNone(row['stop_reason'], row)
            chapter = session.book['chapters'][0]
            self.assertEqual(chapter['title'], '名单之外')
            self.assertEqual(session.book['plan']['1']['title'], '名单之外')
            self.assertEqual(chapter['text'], '沈砚秋发现名单上多了一个名字。')
            restored = load_resume(session.latest_checkpoint, session.plan)
            self.assertEqual(restored['chapters'][0]['title'], '名单之外')
            result = export_markdown(dict(metadata=dict(title='雾航'), state=session.book))
            self.assertIn('## 第1章 名单之外', result)
            self.assertNotIn('续写', result)

    def test_legacy_placeholder_is_repaired_before_commit(self):
        class Provider(Local):
            def complete(self, request):
                if request.role == 'chapter_title':
                    return ModelReply('{"title":"甲的记录"}', 1, 1, 0)
                reply = super().complete(request)
                if request.role == 'planner':
                    value = json.loads(reply.content)
                    value['title'] = '续写1'
                    return ModelReply(canonical(value), 1, 1, 0)
                return reply
        with tempfile.TemporaryDirectory() as folder:
            session = WritingSession(Path(folder) / 'run', Provider(), dict(config(1), event_first=False))
            row = session.write_next('继续')
            self.assertIsNone(row['stop_reason'], row)
            self.assertEqual(session.book['chapters'][0]['title'], '甲的记录')
            self.assertEqual(session.book['plan']['1']['title'], '甲的记录')
