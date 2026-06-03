-- Rode no SQL Editor se o banco já existia antes dos blobs (idempotente).

ALTER TABLE user_photos
    ADD COLUMN IF NOT EXISTS content BYTEA,
    ADD COLUMN IF NOT EXISTS content_type VARCHAR(64),
    ADD COLUMN IF NOT EXISTS kind VARCHAR(16) NOT NULL DEFAULT 'gallery';
