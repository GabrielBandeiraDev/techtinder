-- Rode só se a criação de user_profiles falhou por causa de current_role (palavra reservada no Postgres).
-- Se user_profiles já existe sem a coluna, descomente a linha ALTER abaixo.

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
