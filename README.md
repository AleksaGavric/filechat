# ai-pgvector-langchain-llm-examples

Using PGVector with Language Chain and OpenAI's GPT models to create a simple RAG system.

Useful setup commands:

- `docker system prune --all --force --volumes`
- `docker build -t filechat .`
- `docker compose -f compose.yaml up -d --build`

CURL commands to test the API:

- `curl -X POST <http://localhost:8081/add> \
    -H "Content-Type: application/json" \
    -d '{"collection_name": "my_collection", "document_path": "US-Constitution-With-Amendments.txt"}'`

- `curl -X POST <http://localhost:8081/query> \
    -H "Content-Type: application/json" \
    -d '{"collection_name": "my_collection", "query": "What is the US Constitution?"}'`
