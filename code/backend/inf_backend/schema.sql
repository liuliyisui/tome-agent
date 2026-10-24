CREATE TABLE IF NOT EXISTS tome_schema_version (
    version integer PRIMARY KEY,
    applied_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS tome_books (
    id text PRIMARY KEY,
    metadata jsonb NOT NULL,
    state jsonb NOT NULL,
    state_kind text NOT NULL CHECK (state_kind IN ('snapshot','longform')),
    style jsonb NOT NULL DEFAULT '{"instructions":"","reference":""}',
    checkpoint text,
    storage_key text,
    last_usage jsonb,
    pinned boolean NOT NULL DEFAULT false,
    deleted_at timestamptz,
    restore_token text UNIQUE,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CHECK ((deleted_at IS NULL) = (restore_token IS NULL))
);
CREATE TABLE IF NOT EXISTS tome_chapters (
    book_id text NOT NULL REFERENCES tome_books(id) ON DELETE CASCADE,
    number integer NOT NULL CHECK(number>0),
    title text NOT NULL,
    body text NOT NULL,
    version integer NOT NULL CHECK(version>0),
    PRIMARY KEY(book_id,number)
);
CREATE TABLE IF NOT EXISTS tome_chapter_versions (
    book_id text NOT NULL,
    number integer NOT NULL,
    version integer NOT NULL CHECK(version>0),
    title text NOT NULL,
    body text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY(book_id,number,version),
    FOREIGN KEY(book_id,number) REFERENCES tome_chapters(book_id,number) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS tome_jobs (
    id text PRIMARY KEY,
    book_id text NOT NULL REFERENCES tome_books(id) ON DELETE CASCADE,
    status text NOT NULL CHECK(status IN ('running','completed','failed','interrupted')),
    payload jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS tome_one_running_job ON tome_jobs(book_id) WHERE status='running';
CREATE INDEX IF NOT EXISTS tome_job_history ON tome_jobs(book_id,created_at DESC);
CREATE INDEX IF NOT EXISTS tome_active_shelf ON tome_books(pinned,created_at) WHERE deleted_at IS NULL;
CREATE TABLE IF NOT EXISTS tome_usage (
    book_id text NOT NULL REFERENCES tome_books(id) ON DELETE CASCADE,
    checkpoint text NOT NULL,
    payload jsonb NOT NULL,
    saved_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY(book_id,checkpoint)
);
INSERT INTO tome_schema_version(version) VALUES(1) ON CONFLICT DO NOTHING;
