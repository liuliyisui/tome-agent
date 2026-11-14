"""Persistent account and session storage for the hosted service."""

import hashlib
import hmac
import re
import secrets
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path


class AccountStore:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript(
                """CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY, username TEXT NOT NULL UNIQUE,
                    salt BLOB NOT NULL, password_hash BLOB NOT NULL
                );
                CREATE TABLE IF NOT EXISTS sessions (
                    token_hash BLOB PRIMARY KEY, user_id TEXT NOT NULL,
                    expires_at INTEGER NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                );"""
            )
            columns = {row[1] for row in db.execute("PRAGMA table_info(users)")}
            if "disabled" not in columns:
                db.execute(
                    "ALTER TABLE users ADD COLUMN disabled INTEGER NOT NULL DEFAULT 0"
                )

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        try:
            db.execute("PRAGMA foreign_keys = ON")
            with db:
                yield db
        finally:
            db.close()

    @staticmethod
    def _username(username):
        if not isinstance(username, str) or not re.fullmatch(
            r"[A-Za-z0-9_]{3,32}", username
        ):
            raise ValueError("用户名须为 3 至 32 位字母、数字或下划线")
        return username.lower()

    @staticmethod
    def _password(password, salt):
        if not isinstance(password, str) or not 8 <= len(password) <= 128:
            raise ValueError("密码长度须为 8 至 128 位")
        return hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=32768,
            r=8,
            p=3,
            dklen=32,
            maxmem=67108864,
        )

    def register(self, username, password):
        name = self._username(username)
        if not isinstance(password, str) or not 8 <= len(password) <= 16:
            raise ValueError("注册密码长度须为 8 至 16 位")
        salt = secrets.token_bytes(16)
        digest = self._password(password, salt)
        user_id = secrets.token_hex(16)
        try:
            with self.connect() as db:
                db.execute(
                    "INSERT INTO users (id, username, salt, password_hash) VALUES (?, ?, ?, ?)",
                    (user_id, name, salt, digest),
                )
        except sqlite3.IntegrityError:
            raise ValueError("用户名已被使用") from None
        return user_id

    def authenticate(self, username, password):
        try:
            name = self._username(username)
        except ValueError:
            name = ""
        with self.connect() as db:
            row = db.execute(
                "SELECT id, salt, password_hash, disabled FROM users WHERE username = ?",
                (name,),
            ).fetchone()
        salt = row[1] if row else bytes(16)
        try:
            digest = self._password(password, salt)
        except ValueError:
            return None
        return (
            row[0]
            if row and not row[3] and hmac.compare_digest(digest, row[2])
            else None
        )

    def create_session(self, user_id, lifetime=86400):
        token = secrets.token_urlsafe(32)
        digest = hashlib.sha256(token.encode("ascii")).digest()
        with self.connect() as db:
            db.execute(
                "DELETE FROM sessions WHERE expires_at <= ?", (int(time.time()),)
            )
            db.execute(
                "INSERT INTO sessions VALUES (?, ?, ?)",
                (digest, user_id, int(time.time()) + lifetime),
            )
        return token

    def resolve_session(self, token):
        if not isinstance(token, str) or not re.fullmatch(r"[A-Za-z0-9_-]{43}", token):
            return None
        digest = hashlib.sha256(token.encode("ascii")).digest()
        with self.connect() as db:
            row = db.execute(
                "SELECT sessions.user_id FROM sessions JOIN users ON users.id = sessions.user_id "
                "WHERE token_hash = ? AND expires_at > ? AND users.disabled = 0",
                (digest, int(time.time())),
            ).fetchone()
        return row[0] if row else None

    def username_for(self, user_id):
        with self.connect() as db:
            row = db.execute(
                "SELECT username FROM users WHERE id = ?", (user_id,)
            ).fetchone()
        return row[0] if row else None

    def list_users(self):
        with self.connect() as db:
            return [
                {"username": row[0], "disabled": bool(row[1])}
                for row in db.execute(
                    "SELECT username, disabled FROM users ORDER BY username"
                )
            ]

    def set_disabled(self, username, disabled):
        name = self._username(username)
        if not isinstance(disabled, bool):
            raise ValueError("无效状态")
        with self.connect() as db:
            row = db.execute(
                "SELECT id FROM users WHERE username = ?", (name,)
            ).fetchone()
            if not row:
                raise ValueError("用户不存在")
            db.execute("UPDATE users SET disabled = ? WHERE id = ?", (disabled, row[0]))
            if disabled:
                db.execute("DELETE FROM sessions WHERE user_id = ?", (row[0],))

    def reset_password(self, username, password):
        name = self._username(username)
        if not isinstance(password, str) or not 8 <= len(password) <= 16:
            raise ValueError("密码长度须为 8 至 16 位")
        salt = secrets.token_bytes(16)
        digest = self._password(password, salt)
        with self.connect() as db:
            row = db.execute(
                "SELECT id FROM users WHERE username = ?", (name,)
            ).fetchone()
            if not row:
                raise ValueError("用户不存在")
            db.execute(
                "UPDATE users SET salt = ?, password_hash = ? WHERE id = ?",
                (salt, digest, row[0]),
            )
            db.execute("DELETE FROM sessions WHERE user_id = ?", (row[0],))

    def revoke_session(self, token):
        if not isinstance(token, str) or not re.fullmatch(r"[A-Za-z0-9_-]{43}", token):
            return
        with self.connect() as db:
            db.execute(
                "DELETE FROM sessions WHERE token_hash = ?",
                (hashlib.sha256(token.encode("ascii")).digest(),),
            )
