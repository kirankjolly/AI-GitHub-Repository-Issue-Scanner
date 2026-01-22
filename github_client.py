import httpx
import os
from typing import List, Dict
from datetime import datetime


class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GITHUB_TOKEN not found in environment variables")

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

    async def fetch_all_open_issues(self, repo: str) -> List[Dict]:
        owner, repo_name = self._parse_repo(repo)
        url = f"{self.BASE_URL}/repos/{owner}/{repo_name}/issues"

        all_issues = []
        page = 1
        per_page = 100

        try:
            async with httpx.AsyncClient() as client:
                while True:
                    params = {
                        "state": "open",
                        "per_page": per_page,
                        "page": page
                    }

                    response = await client.get(url, headers=self.headers, params=params, timeout=30.0)

                    if response.status_code == 404:
                        raise ValueError(f"Repository '{repo}' not found on GitHub")
                    elif response.status_code == 401:
                        raise ValueError("GitHub authentication failed. Check your GITHUB_TOKEN")
                    elif response.status_code == 403:
                        raise ValueError("GitHub API rate limit exceeded or access forbidden")
                    elif response.status_code != 200:
                        raise Exception(f"GitHub API error: {response.status_code} - {response.text}")

                    issues = response.json()

                    if not issues:
                        break

                    for issue in issues:
                        if "pull_request" not in issue:
                            all_issues.append({
                                "id": issue["number"],
                                "title": issue["title"],
                                "body": issue.get("body", ""),
                                "html_url": issue["html_url"],
                                "created_at": datetime.strptime(issue["created_at"], "%Y-%m-%dT%H:%M:%SZ"),
                                "repo": repo
                            })

                    page += 1

        except httpx.TimeoutException:
            raise Exception("GitHub API request timed out. Please try again later")
        except httpx.NetworkError:
            raise Exception("Network error while connecting to GitHub API")
        except (ValueError, Exception):
            raise

        return all_issues

    def _parse_repo(self, repo: str) -> tuple:
        parts = repo.split("/")
        if len(parts) != 2:
            raise ValueError(f"Invalid repo format: {repo}. Expected 'owner/repository'")
        return parts[0], parts[1]
