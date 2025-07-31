"""Markdown rendering utilities for evaluation results."""

from datetime import datetime
from typing import Optional

from .models import EvalSetResult, EvalResult


def render_eval_set_results(result: EvalSetResult, build_version: str) -> str:
    """Render evaluation set results as markdown."""

    # Header
    markdown = f"# {result.eval_set_name}\n\n"

    # Metadata
    markdown += "## Run Information\n\n"
    markdown += f"- **Build Version**: `{build_version}`\n"
    markdown += f"- **Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
    if result.description:
        markdown += f"- **Description**: {result.description}\n"
    if result.difficulty:
        markdown += f"- **Difficulty**: {result.difficulty}\n"
    markdown += f"- **Total Questions**: {result.total_questions}\n"
    markdown += f"- **Successful Responses**: {result.successful_responses}\n"
    markdown += f"- **Failed Responses**: {result.failed_responses}\n"

    success_rate = (
        (result.successful_responses / result.total_questions * 100)
        if result.total_questions > 0
        else 0
    )
    markdown += f"- **Success Rate**: {success_rate:.1f}%\n"

    if result.average_response_time_ms:
        markdown += (
            f"- **Average Response Time**: {result.average_response_time_ms:.0f}ms\n"
        )

    markdown += "\n"

    # Summary Statistics
    markdown += "## Summary\n\n"
    if result.failed_responses == 0:
        markdown += "✅ **All questions answered successfully!**\n\n"
    else:
        markdown += f"⚠️ **{result.failed_responses} out of {result.total_questions} questions failed**\n\n"

    # Results by question
    markdown += "## Detailed Results\n\n"

    for i, eval_result in enumerate(result.results, 1):
        markdown += f"### Question {i}\n\n"
        markdown += f"**Question**: {eval_result.question}\n\n"

        if eval_result.error:
            markdown += f"❌ **Error**: {eval_result.error}\n\n"
        else:
            markdown += "✅ **PromptQL Response**:\n\n"
            # The response now contains formatted markdown with all assistant actions
            markdown += f"{eval_result.response}\n\n"

        # Evaluation (if available)
        if eval_result.evaluation:
            markdown += "### 🔍 Evaluation\n\n"
            markdown += f"**Score (0-10)**: {eval_result.evaluation.score}\n\n"
            markdown += f"**Notes**: {eval_result.evaluation.notes}\n\n"

        # Metadata
        markdown += "**Metadata**:\n"
        markdown += (
            f"- Timestamp: {eval_result.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        )
        if eval_result.response_time_ms:
            markdown += f"- Response Time: {eval_result.response_time_ms}ms\n"

        markdown += "\n---\n\n"

    return markdown


def render_comparison_results(
    results: list[EvalSetResult], build_versions: list[str]
) -> str:
    """Render comparison results across multiple builds (future enhancement)."""
    # This could be implemented later for comparing results across different builds
    return "# Comparison Results\n\nNot yet implemented."
