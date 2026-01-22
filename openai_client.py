import os
from openai import OpenAI, AuthenticationError, RateLimitError, APIError, APIConnectionError
from typing import List
from models import Issue


class OpenAIClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4"
        self.max_tokens = 8000

    async def analyze_issues(self, issues: List[Issue], prompt: str) -> str:
        issues_text = self._format_issues(issues)

        if self._estimate_tokens(issues_text) > self.max_tokens:
            issues_text = self._chunk_issues(issues, self.max_tokens - 1000)

        system_message = "You are an expert at analyzing GitHub issues. Provide clear, actionable insights based on the issues provided."

        user_message = f"""Here are the GitHub issues:

{issues_text}

User request: {prompt}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=2000
            )

            return response.choices[0].message.content

        except AuthenticationError:
            raise ValueError("OpenAI authentication failed. Check your OPENAI_API_KEY")
        except RateLimitError:
            raise Exception("OpenAI API rate limit exceeded. Please try again later")
        except APIConnectionError:
            raise Exception("Failed to connect to OpenAI API. Check your network connection")
        except APIError as e:
            raise Exception(f"OpenAI API error: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error during analysis: {str(e)}")

    def _format_issues(self, issues: List[Issue]) -> str:
        formatted = []
        for issue in issues:
            body = issue.body if issue.body else "No description provided"
            formatted.append(f"""
Issue #{issue.id}: {issue.title}
URL: {issue.html_url}
Created: {issue.created_at}
Description: {body}
---
""")
        return "\n".join(formatted)

    def _chunk_issues(self, issues: List[Issue], max_chars: int) -> str:
        result = []
        current_length = 0

        for issue in issues:
            body = issue.body if issue.body else "No description provided"
            issue_text = f"""
Issue #{issue.id}: {issue.title}
URL: {issue.html_url}
Created: {issue.created_at}
Description: {body[:500]}...
---
"""
            if current_length + len(issue_text) > max_chars:
                break

            result.append(issue_text)
            current_length += len(issue_text)

        if len(result) < len(issues):
            result.append(f"\n[Note: Showing {len(result)} of {len(issues)} issues due to context limitations]")

        return "\n".join(result)

    def _estimate_tokens(self, text: str) -> int:
        return len(text) // 4
