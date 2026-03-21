# FastAPI Server

## Folder Structure

```text
backend/
  app/
    __init__.py
    main.py
    api/
      __init__.py
      routes.py
    tools/
      __init__.py
      search.py
    schemas/
      __init__.py
      analyze.py
  requirements.txt
  README.md
```

## Run

```bash
cd backend
cp .env.example .env
# .env 파일에 TAVILY_API_KEY 값을 입력
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## API

- `POST /analyze`

Request body:

```json
{
  "company_name": "OpenAI"
}
```

Response body:

```json
{
  "company_name": "OpenAI",
  "results": [
    {
      "title": "...",
      "url": "...",
      "content": "..."
    }
  ]
}
```
