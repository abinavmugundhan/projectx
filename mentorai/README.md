# MentorAI

Working local document search with persistent SQLite passages, keyword retrieval, an extractive answer and source citations. Unicode text can be indexed; this baseline has no evaluated multilingual embedding quality or LangGraph/FAISS implementation.

```bash
pip install -r mentorai/requirements.txt
cd mentorai && uvicorn server:app --reload
curl -X POST localhost:8000/documents -H 'Content-Type: application/json' -d '{"name":"guide","text":"Python is used for automation. SQL is used for queries."}'
curl -X POST localhost:8000/ask -H 'Content-Type: application/json' -d '{"question":"What is SQL used for?"}'
```

Bring licensed documents and evaluate retrieval on held out questions before making production claims. The local database is ignored by git.

Open `http://localhost:8000/` for the browser interface. Docker: `docker build -t mentorai mentorai && docker run --rm -p 8000:8000 -v "$PWD/mentorai-data:/app/data" -w /app mentorai` (add `-e MENTOR_DB=/app/data/mentorai.sqlite3` to persist indexed passages).
