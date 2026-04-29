# LLM Conversation Platform

Production-ready FastAPI backend for persisting LLM conversations and messages using local [Ollama](https://ollama.com) models stored on an external SSD.

## Features

- Persist conversations and full message history in PostgreSQL
- Non-streaming and SSE streaming chat via local Ollama models
- Automatic token-budget trimming to fit model context windows
- Migration-driven schema management with Alembic
- Structured JSON logging with per-request `X-Request-ID` correlation
- Prometheus metrics at `/metrics`
- Thin route handlers backed by a service and repository layer
- Container hardening: `no-new-privileges`, CPU/memory limits
- Pinned dependencies, Ruff linting, and `pytest` coverage gates

## Requirements

- [Podman](https://podman.io) with `podman compose` (or Docker Compose)
- Python 3.12+
- Ollama running with models accessible at the path configured in `.env`

## Quick Start

1. Copy and update the environment file:

```bash
cp .env.example .env
# Edit .env — set DATABASE_URL, OLLAMA_URL, OLLAMA_MODELS_PATH, etc.
```

2. Bootstrap the local virtual environment:

```bash
make bootstrap
```

3. Start the stack:

```bash
make up
# or: podman compose up --build
```

4. Apply database migrations:

```bash
make migrate
# or: podman compose exec api alembic upgrade head
```

5. Verify the service is healthy:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

## API Endpoints

| Method | Path                                  | Description                                 |
| ------ | ------------------------------------- | ------------------------------------------- |
| `GET`  | `/health`                             | Liveness check                              |
| `GET`  | `/ready`                              | Readiness check (DB + Ollama)               |
| `GET`  | `/metrics`                            | Prometheus metrics                          |
| `POST` | `/api/v1/conversations`               | Create a conversation                       |
| `GET`  | `/api/v1/conversations`               | List conversations                          |
| `GET`  | `/api/v1/conversations/{id}`          | Get a conversation                          |
| `GET`  | `/api/v1/conversations/{id}/messages` | List messages                               |
| `POST` | `/api/v1/conversations/{id}/messages` | Send a message (streaming or non-streaming) |
| `GET`  | `/api/v1/models?sync=true`            | List available Ollama models                |

## Example Flow

### Create a conversation

```bash
curl -X POST http://localhost:8000/api/v1/conversations \
  -H "Content-Type: application/json" \
  -d '{"title":"My first chat"}'
```

### Send a message

```bash
curl -X POST http://localhost:8000/api/v1/conversations/CONVERSATION_ID/messages \
  -H "Content-Type: application/json" \
  -d '{"model_name":"llama3.1:8b","content":"Hello"}'
```

### Send a streaming message (SSE)

```bash
curl -N -X POST http://localhost:8000/api/v1/conversations/CONVERSATION_ID/messages \
  -H "Content-Type: application/json" \
  -d '{"model_name":"llama3.1:8b","content":"Hello","stream":true}'
```

### Retrieve message history

```bash
curl http://localhost:8000/api/v1/conversations/CONVERSATION_ID/messages
```

## Development

```bash
make lint      # Ruff lint check
make format    # Ruff auto-format
make test      # pytest with coverage
make check     # lint + test combined
```

## Releases

Track user-facing changes in [CHANGELOG.md](CHANGELOG.md) using Keep a Changelog style and semantic versioning.

1. Update [CHANGELOG.md](CHANGELOG.md) under `Unreleased`.
2. Run the quality gate:

```bash
make check
```

3. Create an annotated tag:

```bash
make tag VERSION=v0.1.0
make tag-push VERSION=v0.1.0
```

4. Cut the GitHub release from the pushed tag.

## Database Migrations

Migrations live in `migrations/versions/`. The legacy SQL bootstrap file is archived at `docs/archive/schema.sql`; Alembic migrations are the source of truth.

Create a new migration:

```bash
make revision msg="describe your change"
```

Apply all pending migrations:

```bash
make migrate
```

## Contributors

- [Wayne Gibson](https://github.com/waynegibson)

## Repository Settings

Repository settings as code live in [.github/settings.yml](.github/settings.yml). GitHub does not natively consume a `settings.json` file for repository configuration; the standard automation-friendly format is YAML, typically applied by the Probot Settings app or equivalent tooling.

## License

MIT — see [LICENSE.md](LICENSE.md).
