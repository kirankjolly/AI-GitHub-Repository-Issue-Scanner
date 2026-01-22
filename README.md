# KushoAI Issue Analyzer

Backend service for scanning and analyzing GitHub issues using GPT-4.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:

On Windows (Git Bash/Cygwin):
```bash
source venv/Scripts/activate
```

On Windows (CMD):
```bash
venv\Scripts\activate.bat
```

On Linux/Mac:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
```

Then edit `.env` and add your API keys:
- **GITHUB_TOKEN**: Get from https://github.com/settings/tokens
- **OPENAI_API_KEY**: Get from https://platform.openai.com/api-keys

5. Run the server:
```bash
uvicorn main:app --reload
```

6. Access the API:
- API: `http://127.0.0.1:8000`
- Interactive docs: `http://127.0.0.1:8000/docs`
- Alternative docs: `http://127.0.0.1:8000/redoc`

## API Endpoints

### POST /scan

Fetches all open GitHub issues from a repository and caches them locally.

**Request:**
```json
{
  "repo": "owner/repository-name"
}
```

**Response:**
```json
{
  "repo": "owner/repository-name",
  "issues_fetched": 42,
  "cached_successfully": true
}
```

**Features:**
- Fetches ALL open issues with automatic pagination
- Excludes pull requests (only actual issues)
- Replaces old cached data on re-scan
- Stores: id, title, body, html_url, created_at, repo

**Error Responses:**
- `400 Bad Request`: Invalid repository format
- `404 Not Found`: Repository not found on GitHub
- `401 Unauthorized`: Invalid GitHub token
- `403 Forbidden`: GitHub API rate limit exceeded
- `500 Internal Server Error`: Server or API errors

### POST /analyze

Analyzes cached issues using GPT-4 based on a natural language prompt.

**Request:**
```json
{
  "repo": "owner/repository-name",
  "prompt": "What are the most common bugs reported?"
}
```

**Response:**
```json
{
  "analysis": "Based on the issues provided, the most common bugs are:\n1. Authentication failures (15 issues)\n2. UI rendering problems (12 issues)\n3. Performance degradation (8 issues)\n..."
}
```

**Features:**
- Natural language prompts (no keyword tagging required)
- Automatic context size management with chunking
- Uses GPT-4 for high-quality analysis
- Includes issue details: title, description, URL, creation date

**Error Responses:**
- `400 Bad Request`: Invalid input (empty repo/prompt)
- `404 Not Found`: Repository not scanned or no issues cached
- `401 Unauthorized`: Invalid OpenAI API key
- `429 Too Many Requests`: OpenAI rate limit exceeded
- `500 Internal Server Error`: Server or API errors

## Example Usage

### Using cURL

**1. Scan a repository:**
```bash
curl -X POST http://127.0.0.1:8000/scan \
  -H "Content-Type: application/json" \
  -d '{"repo": "fastapi/fastapi"}'
```

**2. Analyze issues:**
```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "repo": "fastapi/fastapi",
    "prompt": "Summarize the top 5 most critical bugs"
  }'
```

### Using Python

```python
import requests

# Scan repository
response = requests.post(
    "http://127.0.0.1:8000/scan",
    json={"repo": "fastapi/fastapi"}
)
print(response.json())

# Analyze issues
response = requests.post(
    "http://127.0.0.1:8000/analyze",
    json={
        "repo": "fastapi/fastapi",
        "prompt": "What are the most common feature requests?"
    }
)
print(response.json())
```

## Architecture

```
main.py              - FastAPI application and endpoints
models.py            - SQLAlchemy database models (Issue, Scan)
database.py          - Database connection and initialization
services.py          - Business logic (caching, retrieval)
github_client.py     - GitHub API integration
openai_client.py     - OpenAI GPT-4 integration
```

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLite with SQLAlchemy ORM
- **APIs**: GitHub REST API, OpenAI GPT-4
- **Language**: Python 3

## Error Handling

The service implements comprehensive error handling for:
- Invalid input validation
- Repository not found
- Authentication failures
- API rate limiting
- Network errors
- Database errors

All errors return appropriate HTTP status codes with clear error messages.
