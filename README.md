# Filechat

A local document-question-answering demo using Flask, OpenAI embeddings and PostgreSQL/pgvector through LangChain. Index a UTF-8 text file, retrieve relevant chunks, then ask a model to answer from that context.

**Status: prototype.** This is a small RAG integration example, not a hosted product or a production-ready multi-user service.

## Architecture

`Text file → 2,000-character chunks → embeddings → pgvector collection → top-3 retrieval → model response + source filenames`

The current code uses `langchain-openai`, `langchain-postgres` (psycopg 3) and `langchain-text-splitters`. Collection names are values rather than caller-controlled table identifiers. Input validation rejects malformed JSON, empty fields and document paths outside the configured root.

## Run locally with Docker Compose

```sh
cp .env.example .env
# Edit .env: provide your own API key and a local alphanumeric database password.
docker compose up --build -d
```

Docker and Compose are required. A full Docker/PostgreSQL/provider smoke test has not been run in this cleanup; local unit tests and provider imports were verified. Calls to `/add`, `/query` and `/sql` can make paid API requests using your key. Model availability depends on your account; set `OPENAI_CHAT_MODEL` accordingly. The API binds to `127.0.0.1:8081`; the database has no published host port. The two bundled sample texts are mounted read-only under `/documents`.

```sh
curl --fail-with-body http://localhost:8081/add \
  -H 'Content-Type: application/json' \
  -d '{"collection_name":"constitution","document_path":"US-Constitution-With-Amendments.txt"}'

curl --fail-with-body http://localhost:8081/query \
  -H 'Content-Type: application/json' \
  -d '{"collection_name":"constitution","query":"What does the First Amendment protect?"}'
```

`/sql` returns a parameterized SQL example and embedding parameters for inspecting retrieval; it does not execute the returned SQL. `/query` performs retrieval through the vector store.

Stop with `docker compose down`. The named database volume persists. The migration from the old community PGVector integration can require a fresh database/reindexing; no existing data migration is provided. The old `Dockerfile.pgvector` is a historical alternative and is not used by Compose.

## Tests without API calls

Python 3.11+:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.lock
python -m unittest discover -s tests
```

Tests substitute in-memory storage and answer functions. They verify request validation, path boundaries, indexing and retrieval behavior without using credentials, billing an API or connecting to PostgreSQL. They do not establish end-to-end provider/database behavior.

## Limitations

- No authentication, authorization or tenant isolation: keep this on localhost.
- Repeated indexing can duplicate chunks; deletion and durable job tracking are not implemented.
- Retrieved text can contain prompt injection; the system instruction is a basic boundary, not a comprehensive defense.
- No retrieval-quality evaluation, answer-accuracy benchmark or throughput claim is provided.
- requirements.txt defines direct dependency ranges; requirements.lock records the resolved dependency versions used for verification. Regenerate it with uv pip compile requirements.txt -o requirements.lock when updating dependencies.

[LangChain PGVector API](https://reference.langchain.com/python/langchain-postgres/vectorstores/PGVector) · [pgvector Docker setup](https://github.com/pgvector/pgvector#docker)
