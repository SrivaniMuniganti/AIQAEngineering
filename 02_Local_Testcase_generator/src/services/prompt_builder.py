"""Build prompts and parse LLM responses for test case generation."""

import json
import re
from dataclasses import dataclass
from typing import Any, List, Optional

from services.jira_client import JiraIssue


class MalformedLLMOutput(Exception):
    """Raised when LLM output cannot be parsed."""
    pass


@dataclass
class TestCase:
    """Represents a generated test case."""
    tc_id: str
    title: str
    case_type: str  # Positive, Negative, Boundary, Edge
    priority: str  # High, Medium, Low
    preconditions: str
    steps: List[str]
    expected_result: str
    ac_reference: str


def build_prompt(issue: JiraIssue) -> List[dict]:
    """Build a prompt for test case generation.

    Args:
        issue: JiraIssue object with details

    Returns:
        List of messages in OpenAI format
    """
    system_prompt = """You are an expert QA engineer specializing in test case generation.
Your task is to generate comprehensive test cases for a Jira issue.

REQUIREMENTS:
1. Generate test cases covering: Positive, Negative, Boundary, and Edge scenarios
2. Each test case MUST be traceable to a specific Acceptance Criteria (AC-1, AC-2, etc.)
3. Return ONLY valid JSON, no markdown, no explanations
4. Steps should be clear, numbered, and executable

JSON SCHEMA (strict):
{
  "test_cases": [
    {
      "tc_id": "TC-001",
      "title": "Brief descriptive title",
      "type": "Positive" | "Negative" | "Boundary" | "Edge",
      "priority": "High" | "Medium" | "Low",
      "preconditions": "State the system state before test",
      "steps": ["Step 1", "Step 2", "Step 3"],
      "expected_result": "Describe the expected outcome",
      "ac_reference": "AC-1" or "AC-1, AC-2"
    }
  ]
}

ACCEPTANCE CRITERIA:
{acceptance_criteria}

ISSUE SUMMARY:
{summary}

ISSUE DESCRIPTION:
{description}

COMMENTS:
{comments}

Generate at least 8 test cases (2-3 per AC if multiple). Ensure diverse coverage."""

    system_prompt = system_prompt.format(
        acceptance_criteria=issue.acceptance_criteria or "See description above",
        summary=issue.summary,
        description=issue.description or "(No description provided)",
        comments=issue.comments or "(No comments)",
    )

    user_prompt = f"""Generate comprehensive test cases for Jira issue {issue.key}.
Issue Type: {issue.issue_type}
Priority: {issue.priority}
Labels: {", ".join(issue.labels) if issue.labels else "None"}

Return ONLY the JSON object, no other text."""

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def parse_response(response_text: str) -> List[TestCase]:
    """Parse LLM response and extract test cases.

    Args:
        response_text: Raw response from LLM

    Returns:
        List of TestCase objects

    Raises:
        MalformedLLMOutput: If response cannot be parsed
    """
    if not response_text or not response_text.strip():
        raise MalformedLLMOutput("Empty LLM response")

    # Remove markdown code fences if present
    text = response_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\n?", "", text)
        text = re.sub(r"\n?```$", "", text)

    # Try to parse JSON
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise MalformedLLMOutput(f"Invalid JSON in response: {str(e)}")

    # Extract test cases
    if not isinstance(data, dict):
        raise MalformedLLMOutput("Response is not a JSON object")

    if "test_cases" not in data:
        raise MalformedLLMOutput("Response does not contain 'test_cases' key")

    test_cases_data = data["test_cases"]
    if not isinstance(test_cases_data, list):
        raise MalformedLLMOutput("'test_cases' is not a list")

    test_cases = []
    for i, tc_data in enumerate(test_cases_data):
        try:
            tc = _parse_test_case(tc_data, i)
            test_cases.append(tc)
        except ValueError as e:
            raise MalformedLLMOutput(f"Invalid test case at index {i}: {str(e)}")

    if not test_cases:
        raise MalformedLLMOutput("No valid test cases in response")

    return test_cases


def _parse_test_case(data: dict, index: int) -> TestCase:
    """Parse a single test case object.

    Args:
        data: Dict representing a test case
        index: Index for fallback tc_id generation

    Returns:
        TestCase object

    Raises:
        ValueError: If required fields are missing or invalid
    """
    tc_id = data.get("tc_id", f"TC-{index + 1:03d}")
    title = data.get("title", "")
    case_type = data.get("type", "").strip()
    priority = data.get("priority", "Medium").strip()
    preconditions = data.get("preconditions", "")
    expected_result = data.get("expected_result", "")
    ac_reference = data.get("ac_reference", "")

    # Validate required fields
    if not title:
        raise ValueError("Missing 'title'")
    if not case_type:
        raise ValueError("Missing 'type'")
    if not expected_result:
        raise ValueError("Missing 'expected_result'")

    # Validate enums
    valid_types = {"Positive", "Negative", "Boundary", "Edge"}
    if case_type not in valid_types:
        case_type = "Positive"  # Default to Positive if invalid

    valid_priorities = {"High", "Medium", "Low"}
    if priority not in valid_priorities:
        priority = "Medium"  # Default to Medium if invalid

    # Parse steps
    steps = data.get("steps", [])
    if isinstance(steps, str):
        # If steps is a single string, split by newlines
        steps = [s.strip() for s in steps.split("\n") if s.strip()]
    elif not isinstance(steps, list):
        steps = [str(steps)]
    else:
        steps = [str(s) for s in steps]

    if not steps:
        steps = ["Execute test as described"]

    return TestCase(
        tc_id=tc_id,
        title=title,
        case_type=case_type,
        priority=priority,
        preconditions=preconditions or "System is in default state",
        steps=steps,
        expected_result=expected_result,
        ac_reference=ac_reference or "Not specified",
    )
