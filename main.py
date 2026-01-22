from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from database import init_db, get_db
from github_client import GitHubClient
from openai_client import OpenAIClient
from services import cache_issues, get_cached_issues, is_repo_scanned

load_dotenv()

app = FastAPI(title="KushoAI Issue Analyzer")


@app.on_event("startup")
def startup_event():
    init_db()


def validate_repo_format(v: str) -> str:
    v = v.strip()
    if not v:
        raise ValueError("Repository name cannot be empty")
    if "/" not in v:
        raise ValueError("Repository must be in format 'owner/repository'")
    parts = v.split("/")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError("Repository must be in format 'owner/repository'")
    return v


class ScanRequest(BaseModel):
    repo: str

    @field_validator("repo")
    @classmethod
    def validate_repo(cls, v: str) -> str:
        return validate_repo_format(v)


class AnalyzeRequest(BaseModel):
    repo: str
    prompt: str

    @field_validator("repo")
    @classmethod
    def validate_repo(cls, v: str) -> str:
        return validate_repo_format(v)

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Prompt cannot be empty")
        return v


@app.get("/")
def root():
    return {"message": "KushoAI Issue Analyzer API"}


@app.post("/scan")
async def scan_repo(request: ScanRequest, db: Session = Depends(get_db)):
    try:
        github_client = GitHubClient()
        issues = await github_client.fetch_all_open_issues(request.repo)

        count = cache_issues(db, request.repo, issues)

        return {
            "repo": request.repo,
            "issues_fetched": count,
            "cached_successfully": True
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scanning repository: {str(e)}")


@app.post("/analyze")
async def analyze_issues(request: AnalyzeRequest, db: Session = Depends(get_db)):
    try:
        if not is_repo_scanned(db, request.repo):
            raise HTTPException(
                status_code=404,
                detail=f"Repository '{request.repo}' has not been scanned. Please run /scan first."
            )

        issues = get_cached_issues(db, request.repo)

        if not issues:
            raise HTTPException(
                status_code=404,
                detail=f"Repository '{request.repo}' was scanned but has no open issues to analyze."
            )

        openai_client = OpenAIClient()
        analysis = await openai_client.analyze_issues(issues, request.prompt)

        return {"analysis": analysis}

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing issues: {str(e)}")
