-- Índices de performance — rode no SQL Editor após schema.sql
-- Acelera feed, matches, likes e chat

CREATE INDEX IF NOT EXISTS ix_users_active_created
    ON users (is_active, created_at DESC)
    WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS ix_likes_from_to
    ON likes (from_user_id, to_user_id);

CREATE INDEX IF NOT EXISTS ix_likes_from_created
    ON likes (from_user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS ix_passes_from_to
    ON passes (from_user_id, to_user_id);

CREATE INDEX IF NOT EXISTS ix_matches_user_one
    ON matches (user_one_id, matched_at DESC);

CREATE INDEX IF NOT EXISTS ix_matches_user_two
    ON matches (user_two_id, matched_at DESC);

CREATE INDEX IF NOT EXISTS ix_messages_conversation_created
    ON messages (conversation_id, created_at);

CREATE INDEX IF NOT EXISTS ix_user_photos_user_position
    ON user_photos (user_id, position);

CREATE INDEX IF NOT EXISTS ix_refresh_tokens_user
    ON refresh_tokens (user_id);

ANALYZE users;
ANALYZE likes;
ANALYZE passes;
ANALYZE matches;
ANALYZE messages;
