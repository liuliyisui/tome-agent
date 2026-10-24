import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from inf_backend import library, service
from inf_backend.settings import Settings


class LibraryTests(unittest.TestCase):
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
