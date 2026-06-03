# Supabase — DevMatch

## 1. Criar o schema

1. Abra o [Supabase Dashboard](https://supabase.com/dashboard) → seu projeto → **SQL Editor**.
2. Cole e execute o arquivo [`schema.sql`](./schema.sql) (Run).
3. Execute também [`indexes.sql`](./indexes.sql) para deixar feed/match/chat mais rápidos.

## 2. Credenciais (Settings → API)

| Variável | Onde achar |
|----------|------------|
| `SUPABASE_PROJECT_ID` | URL do projeto: `https://**abcdefgh**.supabase.co` → `abcdefgh` |
| `SUPABASE_URL` | Project URL |
| `SUPABASE_ANON_KEY` | `anon` / publishable key |
| `SUPABASE_SERVICE_ROLE_KEY` | `service_role` / secret (**não expor no frontend**) |

## 3. Senha do banco (Settings → Database)

| Variável | Onde achar |
|----------|------------|
| `SUPABASE_DB_PASSWORD` | Database password (a que você definiu ao criar o projeto) |

O backend monta automaticamente:

`postgresql+asyncpg://postgres:SENHA@db.PROJECT_ID.supabase.co:5432/postgres`

**Mais rápido (recomendado):** no `.env`:

```env
SUPABASE_USE_POOLER=true
SUPABASE_POOLER_HOST=aws-0-REGIAO.pooler.supabase.com
```

(Host em Dashboard → Database → Connection pooling → Transaction, porta 6543)

Ou defina `DATABASE_URL` manualmente (Connection string → URI, trocando `postgresql://` por `postgresql+asyncpg://`).

## 4. `.env` do backend

Copie `backend/.env.example` para `backend/.env` e preencha.

## 5. Dependências e servidor

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## 6. Migração de dados do SQLite (opcional)

Se já tinha usuários em `data/app.db`, exporte manualmente ou recadastre. O schema é o mesmo; só muda o motor.

## Storage de fotos (futuro)

Hoje os uploads ficam em `UPLOAD_DIR` local. Para produção com Supabase Storage, use o bucket + `SUPABASE_SERVICE_ROLE_KEY` numa etapa posterior.
