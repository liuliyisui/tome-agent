import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from inf_backend import library, service
from inf_backend.settings import Settings


class LibraryTests(unittest.TestCase):
    def test_permanent_delete_requires_matching_title_and_only_removes_selected_trash(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(service, "BOOKS", Path(directory) / "books"):
            tokens = []
            for number in (1, 2):
                book_id = f"purge-{number}"
                service.create_book(book_id, f"测试作品{number}", "故事", 3, 3000, settings=Settings(api_key="FAKE_TEST_KEY"))
                nested = service.book_path(book_id) / "test-archive"
                nested.mkdir()
                (nested / "chapter.txt").write_text("测试正文", encoding="utf-8")
                tokens.append(library.delete_book(book_id)["restore_token"])
            with self.assertRaises(ValueError):
                library.permanently_delete_book(tokens[0], "错误的作品名称")
            self.assertEqual(len(library.list_deleted_books()), 2)
            with self.assertRaises(ValueError):
                library.permanently_delete_book("../../outside", "测试作品1")
            self.assertEqual(library.permanently_delete_book(tokens[0], "测试作品1"), {"purged": True})
            self.assertFalse((library.trash_root() / tokens[0]).exists())
            self.assertEqual([book["title"] for book in library.list_deleted_books()], ["测试作品2"])
            self.assertTrue((library.trash_root() / tokens[1] / "test-archive" / "chapter.txt").exists())
            with self.assertRaises(FileNotFoundError):
                library.restore_book(tokens[0])
            library.restore_book(tokens[1])
            self.assertEqual((service.book_path("purge-2") / "test-archive" / "chapter.txt").read_text(encoding="utf-8"), "测试正文")

    def test_trash_lists_multiple_books_without_browser_undo_state(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(service, "BOOKS", Path(directory) / "books"):
            self.assertEqual(library.list_deleted_books(), [])
            tokens = []
            for number in (1, 2):
                book_id = f"discard-{number}"
                service.create_book(book_id, f"废案{number}", "故事", 3, 3000, settings=Settings(api_key="FAKE_TEST_KEY"))
                tokens.append(library.delete_book(book_id)["restore_token"])
            removed = library.list_deleted_books()
            self.assertEqual([row["title"] for row in removed], ["废案2", "废案1"])
            self.assertEqual({row["restore_token"] for row in removed}, set(tokens))
            library.restore_book(tokens[0])
            self.assertEqual([row["title"] for row in library.list_deleted_books()], ["废案2"])
            self.assertEqual(service.load_book("discard-1")["metadata"]["title"], "废案1")

    def test_delete_restore_preserves_every_saved_file_and_pin_preference(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(service, "BOOKS", Path(directory) / "books"):
            service.create_book("shelf-book", "书架测试", "故事", 3, 3000, settings=Settings(api_key="FAKE_TEST_KEY"))
            service.save_writing_style("shelf-book", {"instructions": "短句", "reference": "参考文本"})
            library.pin_book("shelf-book", True)
            folder = service.book_path("shelf-book")
            before = {p.relative_to(folder): p.read_bytes() for p in folder.rglob("*") if p.is_file()}
            with service.operation_lock(folder):
                with self.assertRaises(ValueError):
                    library.delete_book("shelf-book")
            deleted = library.delete_book("shelf-book")
            self.assertFalse(folder.exists())
            self.assertEqual(service.list_books(), [])
            self.assertEqual(library.restore_book(deleted["restore_token"]), "shelf-book")
            after = {p.relative_to(folder): p.read_bytes() for p in folder.rglob("*") if p.is_file()}
            self.assertEqual(before, after)
            self.assertTrue(library.is_pinned("shelf-book"))
            self.assertEqual(service.load_book("shelf-book")["metadata"]["title"], "书架测试")
            with self.assertRaises(ValueError):
                library.pin_book("shelf-book", "yes")
            with self.assertRaises(ValueError):
                library.delete_book("../escape")


if __name__ == "__main__":
    unittest.main()
