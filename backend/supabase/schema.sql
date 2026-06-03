-- DevMatch / Tech Matchmakers — schema para Supabase (PostgreSQL)
-- Cole no SQL Editor do projeto: https://supabase.com/dashboard/project/_/sql
-- Rode uma vez em banco vazio. Se já existir tabela, apague antes ou use IF NOT EXISTS abaixo.

-- Extensão útil (já vem no Supabase, mas não custa garantir)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ---------------------------------------------------------------------------
-- users
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(36) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    birth_date DATE,
    city VARCHAR(120),
    state VARCHAR(120),
    country VARCHAR(120),
    bio TEXT,
    profile_picture VARCHAR(512),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS ix_users_email ON users (email);
CREATE INDEX IF NOT EXISTS ix_users_uuid ON users (uuid);

-- ---------------------------------------------------------------------------
-- skills
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS skills (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL UNIQUE
);

-- ---------------------------------------------------------------------------
-- user_photos
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_photos (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    photo_url VARCHAR(512) NOT NULL,
    position INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_user_photos_user_id ON user_photos (user_id);

-- ---------------------------------------------------------------------------
-- user_profiles
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users (id) ON DELETE CASCADE,
    "current_role" VARCHAR(255),
    company VARCHAR(255),
    years_experience INTEGER,
    works_with_ai BOOLEAN NOT NULL DEFAULT FALSE,
    works_with_backend BOOLEAN NOT NULL DEFAULT FALSE,
    works_with_frontend BOOLEAN NOT NULL DEFAULT FALSE,
    works_with_mobile BOOLEAN NOT NULL DEFAULT FALSE,
    works_with_data_science BOOLEAN NOT NULL DEFAULT FALSE,
    works_with_devops BOOLEAN NOT NULL DEFAULT FALSE,
    works_with_cloud BOOLEAN NOT NULL DEFAULT FALSE,
    works_with_cybersecurity BOOLEAN NOT NULL DEFAULT FALSE,
    future_goals TEXT,
    favorite_technologies TEXT,
    github_url VARCHAR(512),
    linkedin_url VARCHAR(512),
    portfolio_url VARCHAR(512),
    remote_only BOOLEAN NOT NULL DEFAULT FALSE,
    open_to_partnerships BOOLEAN NOT NULL DEFAULT FALSE,
    open_to_startups BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- user_skills
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_skills (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    skill_id INTEGER NOT NULL REFERENCES skills (id) ON DELETE CASCADE,
    experience_years INTEGER,
    CONSTRAINT uq_user_skill UNIQUE (user_id, skill_id)
);

CREATE INDEX IF NOT EXISTS ix_user_skills_user_id ON user_skills (user_id);

-- ---------------------------------------------------------------------------
-- likes
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS likes (
    id SERIAL PRIMARY KEY,
    from_user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    to_user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_like_pair UNIQUE (from_user_id, to_user_id)
);

CREATE INDEX IF NOT EXISTS ix_likes_from_user_id ON likes (from_user_id);
CREATE INDEX IF NOT EXISTS ix_likes_to_user_id ON likes (to_user_id);

-- ---------------------------------------------------------------------------
-- passes (dislikes)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS passes (
    id SERIAL PRIMARY KEY,
    from_user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    to_user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_pass_pair UNIQUE (from_user_id, to_user_id)
);

CREATE INDEX IF NOT EXISTS ix_passes_from_user_id ON passes (from_user_id);
CREATE INDEX IF NOT EXISTS ix_passes_to_user_id ON passes (to_user_id);

-- ---------------------------------------------------------------------------
-- matches
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS matches (
    id SERIAL PRIMARY KEY,
    user_one_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    user_two_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    matched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_match_pair UNIQUE (user_one_id, user_two_id)
);

CREATE INDEX IF NOT EXISTS ix_matches_user_one_id ON matches (user_one_id);
CREATE INDEX IF NOT EXISTS ix_matches_user_two_id ON matches (user_two_id);

-- ---------------------------------------------------------------------------
-- conversations
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    match_id INTEGER NOT NULL UNIQUE REFERENCES matches (id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- messages
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations (id) ON DELETE CASCADE,
    sender_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    read_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS ix_messages_conversation_id ON messages (conversation_id);

-- ---------------------------------------------------------------------------
-- refresh_tokens
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    token_jti VARCHAR(64) NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_refresh_tokens_user_id ON refresh_tokens (user_id);

-- ---------------------------------------------------------------------------
-- Alembic version (opcional — se for usar `alembic stamp head` depois)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL PRIMARY KEY
);

-- ---------------------------------------------------------------------------
-- Skills iniciais
-- ---------------------------------------------------------------------------
INSERT INTO skills (name) VALUES
    ('Python'),
    ('JavaScript'),
    ('TypeScript'),
    ('Rust'),
    ('Go'),
    ('Java'),
    ('C#'),
    ('PHP'),
    ('SQL'),
    ('Docker'),
    ('Kubernetes'),
    ('AWS')
ON CONFLICT (name) DO NOTHING;

-- Marca migração como aplicada (equivalente ao Alembic 001)
INSERT INTO alembic_version (version_num) VALUES ('001')
ON CONFLICT (version_num) DO NOTHING;
