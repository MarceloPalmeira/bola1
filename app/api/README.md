# bola1 API

Backend FastAPI do projeto `bola1`.

## Instalação

```bash
cd app/api
uv sync
```

## Configuração

```bash
cp .env.example .env
```

Configure `DATABASE_URL` apontando para PostgreSQL.

## Migrations

```bash
uv run alembic upgrade head
```

## Seed

```bash
uv run python -m bola1_api.scripts.seed
```

## Superuser inicial

Crie ou promova um usuário admin fora do cadastro público:

```bash
uv run python -m bola1_api.scripts.create_superuser \
  --email admin@example.com \
  --password "troque-esta-senha" \
  --nickname Admin
```

Também é possível usar `BOLA1_SUPERUSER_EMAIL`, `BOLA1_SUPERUSER_PASSWORD` e
`BOLA1_SUPERUSER_NICKNAME`.

## Servidor

```bash
uv run uvicorn bola1_api.main:app --reload
```

Swagger: `http://127.0.0.1:8000/docs`.

## Testes

```bash
uv run pytest
```
