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
        user_id = self.store.register("Writer_1", "correct horse battery")
        reopened = AccountStore(self.path)
        self.assertEqual(
            reopened.authenticate("writer_1", "correct horse battery"), user_id
        )
        self.assertIsNone(reopened.authenticate("writer_1", "incorrect password"))
        self.assertIsNone(reopened.authenticate("unknown", "correct horse battery"))
        with closing(sqlite3.connect(self.path)) as db:
            salt, stored = db.execute(
                "SELECT salt, password_hash FROM users"
            ).fetchone()
        self.assertNotIn(b"correct horse battery", salt + stored)
        with self.assertRaises(ValueError):
            reopened.register("WRITER_1", "another good password")

    def test_session_is_persistent_revocable_and_expires(self):
        user_id = self.store.register("writer", "long enough password")
        token = self.store.create_session(user_id)
        self.assertEqual(AccountStore(self.path).resolve_session(token), user_id)
        self.assertIsNone(self.store.resolve_session(token + "x"))
        self.store.revoke_session(token)
        self.assertIsNone(self.store.resolve_session(token))
        expired = self.store.create_session(user_id, lifetime=-1)
        self.assertIsNone(self.store.resolve_session(expired))

    def test_invalid_inputs_are_rejected(self):
        for username, password in (("ab", "long enough password"), ("name", "short")):
            with self.subTest(username=username), self.assertRaises(ValueError):
                self.store.register(username, password)
