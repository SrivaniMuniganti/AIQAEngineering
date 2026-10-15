"""Jira API client for fetching issues and details."""

import base64
from dataclasses import dataclass
from typing import Optional

import requests


class JiraError(Exception):
    """Base exception for Jira errors."""
    pass


class JiraAuthError(JiraError):
    """Raised on 401 or 403 response."""
    pass


class JiraNotFoundError(JiraError):
    """Raised on 404 response."""
    pass


class JiraNetworkError(JiraError):
    """Raised on network connectivity issues."""
    pass


class JiraConfigError(JiraError):
    """Raised when Jira is not configured."""
    pass


@dataclass
class JiraIssue:
    """Represents a Jira issue."""
    key: str
    summary: str
    description: str
    issue_type: str
    priority: str
    labels: list[str]
    acceptance_criteria: str
    comments: str


class JiraClient:
    """Client for interacting with Jira REST API."""

    def __init__(self, jira_url: str, jira_email: str, jira_api_token: str):
        """Initialize the Jira client.

        Args:
            jira_url: Base URL of Jira instance (e.g., https://your-domain.atlassian.net)
            jira_email: Email for basic auth
            jira_api_token: API token for basic auth
        """
        if not jira_url or not jira_email or not jira_api_token:
            raise JiraConfigError("Jira URL, email, and API token are required")

        self.jira_url = jira_url.rstrip("/")
        self.jira_email = jira_email
        self.jira_api_token = jira_api_token
        self.timeout = 10

    def _get_auth_header(self) -> dict:
        """Return the Authorization header for basic auth."""
        credentials = f"{self.jira_email}:{self.jira_api_token}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {"Authorization": f"Basic {encoded}"}

    def test_connection(self) -> bool:
        """Test connection to Jira API.

        Returns:
            True if connection successful

        Raises:
            JiraAuthError: If authentication fails (401/403)
            JiraNetworkError: If network error occurs
            JiraError: For other errors
        """
        try:
            url = f"{self.jira_url}/rest/api/3/myself"
            response = requests.get(
                url,
                headers=self._get_auth_header(),
                timeout=self.timeout,
            )

            if response.status_code == 401 or response.status_code == 403:
                raise JiraAuthError("Invalid Jira credentials (401/403)")

            response.raise_for_status()
            return True

        except requests.exceptions.Timeout:
            raise JiraNetworkError("Jira connection timed out")
        except requests.exceptions.ConnectionError:
            raise JiraNetworkError("Failed to connect to Jira server")
        except requests.exceptions.RequestException as e:
            raise JiraNetworkError(f"Network error: {str(e)}")

    def fetch_issue(self, key: str) -> JiraIssue:
        """Fetch a Jira issue by key.

        Args:
            key: Jira issue key (e.g., PROJ-123)

        Returns:
            JiraIssue object

        Raises:
            JiraAuthError: If authentication fails
            JiraNotFoundError: If issue not found (404)
            JiraNetworkError: If network error occurs
        """
        try:
            url = f"{self.jira_url}/rest/api/3/issue/{key}"
            fields = "summary,description,issuetype,priority,labels,comment"

            response = requests.get(
                url,
                headers=self._get_auth_header(),
                params={"fields": fields},
                timeout=self.timeout,
            )

            if response.status_code == 401 or response.status_code == 403:
                raise JiraAuthError("Invalid Jira credentials (401/403)")

            if response.status_code == 404:
                raise JiraNotFoundError(f"Jira issue {key} not found")

            response.raise_for_status()
            data = response.json()

            # Extract fields
            fields = data.get("fields", {})
            summary = fields.get("summary", "")
            description = self._adf_to_text(fields.get("description"))
            issue_type = fields.get("issuetype", {}).get("name", "Unknown")
            priority = fields.get("priority", {}).get("name", "Unknown")
            labels = fields.get("labels", [])

            # Extract comments
            comments_text = self._extract_comments(fields.get("comment", {}))

            # Extract acceptance criteria
            acceptance_criteria = self._extract_acceptance_criteria(
                description, fields.get("customfield_10000")
            )

            return JiraIssue(
                key=key,
                summary=summary,
                description=description,
                issue_type=issue_type,
                priority=priority,
                labels=labels,
                acceptance_criteria=acceptance_criteria,
                comments=comments_text,
            )

        except requests.exceptions.Timeout:
            raise JiraNetworkError("Jira fetch timed out")
        except requests.exceptions.ConnectionError:
            raise JiraNetworkError("Failed to connect to Jira server")
        except requests.exceptions.RequestException as e:
            if "401" in str(e) or "403" in str(e):
                raise JiraAuthError("Invalid Jira credentials")
            raise JiraNetworkError(f"Network error: {str(e)}")

    def _adf_to_text(self, adf_doc: Optional[dict]) -> str:
        """Convert Atlassian Document Format to plain text.

        Simple conversion: extract text from doc nodes.
        """
        if not adf_doc or not isinstance(adf_doc, dict):
            return ""

        text_parts = []

        def extract_text(node):
            if isinstance(node, dict):
                if "text" in node:
                    text_parts.append(node["text"])
                if "content" in node:
                    for child in node["content"]:
                        extract_text(child)
            elif isinstance(node, list):
                for item in node:
                    extract_text(item)

        extract_text(adf_doc)
        return "\n".join(text_parts)

    def _extract_comments(self, comments_data: dict) -> str:
        """Extract text from Jira comments."""
        if not comments_data or "comments" not in comments_data:
            return ""

        comments_text = []
        for comment in comments_data.get("comments", []):
            body = comment.get("body", {})
            text = self._adf_to_text(body)
            if text:
                comments_text.append(text)

        return "\n".join(comments_text)

    def _extract_acceptance_criteria(
        self, description: str, custom_field: Optional[str]
    ) -> str:
        """Extract acceptance criteria from description or custom field.

        Looks for "Acceptance Criteria" heading in description,
        or returns custom field if available.
        """
        if custom_field:
            return custom_field

        # Look for "Acceptance Criteria" section in description
        if "acceptance criteria" in description.lower():
            lines = description.split("\n")
            in_ac_section = False
            ac_lines = []

            for line in lines:
                if "acceptance criteria" in line.lower():
                    in_ac_section = True
                    continue

                if in_ac_section:
                    if line.startswith("#"):
                        break
                    ac_lines.append(line)

            ac_text = "\n".join(ac_lines).strip()
            if ac_text:
                return ac_text

        # Default to first 500 chars of description
        return description[:500] if description else "No acceptance criteria found"
