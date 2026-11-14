"""Account isolation starts with persistent credentials and revocable sessions."""

import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from inf_backend.accounts import AccountStore


class AccountTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / "accounts.sqlite3"
        self.store = AccountStore(self.path)

    def test_registration_login_and_password_hash_persist(self):
        user_id = self.store.register("Writer_1", "correcthorse123")
        reopened = AccountStore(self.path)
        self.assertEqual(reopened.authenticate("writer_1", "correcthorse123"), user_id)
        self.assertIsNone(reopened.authenticate("writer_1", "incorrect password"))
        self.assertIsNone(reopened.authenticate("unknown", "correcthorse123"))
        with closing(sqlite3.connect(self.path)) as db:
            salt, stored = db.execute(
                "SELECT salt, password_hash FROM users"
            ).fetchone()
        self.assertNotIn(b"correcthorse123", salt + stored)
        with self.assertRaises(ValueError):
            reopened.register("WRITER_1", "anotherpass123")

    def test_session_is_persistent_revocable_and_expires(self):
        user_id = self.store.register("writer", "longenough123")
        token = self.store.create_session(user_id)
        self.assertEqual(AccountStore(self.path).resolve_session(token), user_id)
        self.assertIsNone(self.store.resolve_session(token + "x"))
        self.store.revoke_session(token)
        self.assertIsNone(self.store.resolve_session(token))
        expired = self.store.create_session(user_id, lifetime=-1)
        self.assertIsNone(self.store.resolve_session(expired))

    def test_password_length_boundaries_and_existing_long_password(self):
        for password in ("a" * 7, "a" * 17, "a" * 129):
            with self.subTest(length=len(password)), self.assertRaises(ValueError):
                self.store.register("too_short_or_long", password)
        for index, password in enumerate(("a" * 8, "b" * 15, "c" * 16)):
            username = f"writer_{index}"
            with self.subTest(length=len(password)):
                user_id = self.store.register(username, password)
                self.assertEqual(self.store.authenticate(username, password), user_id)
        legacy_password = "legacy-password-over-16"
        salt = b"0123456789abcdef"
        with self.store.connect() as db:
            db.execute(
                "INSERT INTO users VALUES (?, ?, ?, ?)",
                (
                    "legacy-id",
                    "legacy",
                    salt,
                    self.store._password(legacy_password, salt),
                ),
            )
        self.assertEqual(
            self.store.authenticate("legacy", legacy_password), "legacy-id"
        )

    def test_invalid_inputs_are_rejected(self):
        for username, password in (("ab", "long enough password"), ("name", "short")):
            with self.subTest(username=username), self.assertRaises(ValueError):
                self.store.register(username, password)
