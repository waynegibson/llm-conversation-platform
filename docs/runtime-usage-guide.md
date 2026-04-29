# Runtime Usage Guide

This guide covers day-to-day usage for the local platform:

- Running the stack (API + Postgres + Ollama)
- Pulling and listing models inside the Ollama container
- Prompting models through the API
- Confirming conversations/messages are persisted in PostgreSQL

## 1) Start The Platform

From the repository root:

```bash
podman compose up -d --build
```

Check service status:

```bash
podman compose ps
```

Check health endpoints:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

## 2) Run Ollama In Container (No Host Ollama Required)

If `ollama` on macOS is stopped, that is fine. This project uses the Ollama container defined in `docker-compose.yaml`.

List models available in the container:

```bash
podman compose exec ollama ollama list
```

Pull a model (if needed):

```bash
podman compose exec ollama ollama pull llama3.3:latest
```

Quick direct model test inside container:

```bash
podman compose exec ollama ollama run llama3.3:latest "Reply in one short sentence: hello"
```

## 3) Sync Models Into The App Database

Sync the models known by Ollama into the app's `models` table:

```bash
curl "http://localhost:8000/api/v1/models?sync=true"
```

You should see your model entries in the JSON response.

## 4) Create A Conversation

```bash
curl -X POST http://localhost:8000/api/v1/conversations \
  -H "Content-Type: application/json" \
  -d '{"title":"Demo conversation"}'
```

Copy the returned `id` as `CONVERSATION_ID`.

## 5) Send A Prompt (Non-Streaming)

```bash
curl -X POST http://localhost:8000/api/v1/conversations/CONVERSATION_ID/messages \
  -H "Content-Type: application/json" \
  -d '{"model_name":"llama3.3:latest","content":"Give me 3 bullet tips for writing good prompts."}'
```

What happens on this call:

- The user message is saved to `messages`
- Ollama is called
- The assistant response is saved to `messages`
- Token/latency metadata is saved when available

## 6) Send A Prompt (Streaming SSE)

```bash
curl -N -X POST http://localhost:8000/api/v1/conversations/CONVERSATION_ID/messages \
  -H "Content-Type: application/json" \
  -d '{"model_name":"llama3.3:latest","content":"Write a short summary of containerized inference.","stream":true}'
```

You will receive token events as they stream, followed by a final `done` event.

## 7) Verify Conversation History Via API

```bash
curl http://localhost:8000/api/v1/conversations/CONVERSATION_ID/messages
```

You should see both `user` and `assistant` messages persisted.

## 8) Verify Persistence In PostgreSQL

Open a psql shell in the database container:

```bash
podman compose exec postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

Run these checks:

```sql
SELECT id, title, created_at FROM conversations ORDER BY created_at DESC LIMIT 5;
SELECT conversation_id, role, left(content, 80) AS preview, created_at
FROM messages
ORDER BY created_at DESC
LIMIT 10;
```

Exit psql:

```sql
\q
```

## 9) Common Operations

Stop stack:

```bash
podman compose down
```

View API logs:

```bash
podman compose logs -f api
```

View Ollama logs:

```bash
podman compose logs -f ollama
```

## 10) Troubleshooting

- `model not found`: pull model in container and run `/api/v1/models?sync=true` again
- `503 from /ready`: check Postgres and Ollama health/logs
- Port `11434` conflict: ensure host Ollama service is stopped
