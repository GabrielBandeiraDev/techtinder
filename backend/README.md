# Tech Matchmakers — Backend

API FastAPI para rede profissional de tecnologia (match, feed, chat).

## Stack

- Python 3.12+
- FastAPI, SQLAlchemy 2.0, PostgreSQL (Supabase) ou SQLite (dev)
- JWT (access + refresh), Bcrypt
- Alembic, Pydantic v2
- WebSocket (chat), SlowAPI (rate limit), structlog

## Setup

### Supabase

1. Rode [`supabase/schema.sql`](supabase/schema.sql) no SQL Editor do projeto.
2. `cp .env.example .env` e preencha `SUPABASE_PROJECT_ID`, `SUPABASE_URL`, keys e `SUPABASE_DB_PASSWORD`.
3. `pip install -r requirements.txt` e `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`

Detalhes: [`supabase/README.md`](supabase/README.md).

### SQLite (dev local)

No `.env`: `DATABASE_URL=sqlite+aiosqlite:///./data/app.db` e `alembic upgrade head`.

Documentação interativa: http://localhost:8000/docs

## Arquitetura (Clean)

```
app/
├── domain/          # exceções e regras
├── application/     # serviços (casos de uso)
├── infrastructure/  # DB, JWT, uploads, logs
└── presentation/    # rotas HTTP, WebSocket, schemas
```

## Endpoints principais

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/v1/auth/register` | Cadastro |
| POST | `/api/v1/auth/login` | Login (tokens) |
| POST | `/api/v1/auth/refresh` | Renovar access token |
| POST | `/api/v1/auth/logout` | Revogar refresh token |
| GET | `/api/v1/users/me` | Perfil autenticado |
| POST | `/api/v1/users/me/photos` | Upload de foto |
| PUT | `/api/v1/users/me/profile` | Perfil profissional |
| GET | `/api/v1/feed` | Recomendações |
| GET | `/api/v1/search` | Busca de perfis |
| POST | `/api/v1/swipes/like/{id}` | Curtir (cria match se mútuo) |
| POST | `/api/v1/swipes/dislike/{id}` | Dislike (exclui do feed) |
| GET | `/api/v1/matches` | Lista de matches |
| GET/POST | `/api/v1/conversations/{id}/messages` | Chat REST |
| WS | `/ws/chat/{conversation_id}?token=...` | Chat em tempo real |

## Regra de match e chat

1. Usuário A curte B → registro em `likes`
2. Usuário B curte A → `matches` + `conversations` criados automaticamente
3. Sem match → HTTP 403: `{"error": "Chat disponível apenas após match."}`

A tabela `passes` registra dislikes para não reaparecerem no feed.

## Upload

Formatos: JPG, JPEG, PNG, WEBP. Validação de extensão, MIME e tamanho (`MAX_UPLOAD_SIZE_MB`).

## Variáveis de ambiente

Ver `.env.example` — Supabase: `SUPABASE_PROJECT_ID`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_DB_PASSWORD`.
