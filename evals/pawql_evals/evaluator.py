"""LLM-as-a-judge evaluator for PromptQL responses."""

import os
import json
from typing import Optional
from pathlib import Path

import yaml
from anthropic import Anthropic

from .models import EvaluatorConfig, EvaluationScore


class LLMEvaluator:
    """LLM-as-a-judge evaluator using Anthropic Claude."""

    def __init__(self, config: EvaluatorConfig):
        """Initialize the evaluator with configuration."""
        self.config = config

        if config.provider != "anthropic":
            raise ValueError(
                f"Unsupported provider: {config.provider}. Only 'anthropic' is supported."
            )

        # Get Anthropic API key from environment
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")

        self.client = Anthropic(api_key=api_key)

    def evaluate_response(
        self,
        question: str,
        promptql_response: str,
        expected_analysis: str,
        error: Optional[str] = None,
        raw_response: Optional[str] = None,
    ) -> EvaluationScore:
        """
        Evaluate a PromptQL response against expected analysis.

        Args:
            question: The original question
            promptql_response: The processed PromptQL response (formatted for markdown)
            expected_analysis: The expected analysis from eval set
            error: Any error that occurred during PromptQL execution
            raw_response: The raw PromptQL API response object (if available)

        Returns:
            EvaluationScore with score (0-10) and notes
        """

        # Skip evaluation if there's an error
        if error:
            return EvaluationScore(
                score=0, notes="Evaluation skipped due to PromptQL API error"
            )

        # Use raw response if available, otherwise use processed response
        response_to_evaluate = raw_response if raw_response else promptql_response
        evaluation_prompt = self._create_success_evaluation_prompt(
            question, response_to_evaluate, expected_analysis
        )

        try:
            # Call Anthropic API
            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=1000,
                temperature=0.1,  # Low temperature for consistent evaluation
                messages=[{"role": "user", "content": evaluation_prompt}],
            )

            # Parse the response
            response_text = ""
            for content_block in response.content:
                text_content = getattr(content_block, "text", None)
                if text_content:
                    response_text += text_content

            return self._parse_evaluation_response(response_text)

        except Exception as e:
            # If evaluation fails, return a default score with error info
            return EvaluationScore(score=0, notes=f"Evaluation failed: {str(e)}")

    def _create_success_evaluation_prompt(
        self, question: str, promptql_response: str, expected_analysis: str
    ) -> str:
        """Create evaluation prompt for successful PromptQL responses."""
        return f"""You are an expert evaluator for PromptQL, a natural language to SQL system. Your task is to evaluate how well a PromptQL response adheres to the expected analysis.

**Question:** {question}

**Expected Analysis:**
{expected_analysis}

**Full PromptQL API Response:**
{promptql_response}

**Evaluation Criteria:**
- Does the response correctly interpret the question?
- Does the generated SQL match the expected approach?
- Are the results accurate and complete?
- Does the response align with the expected analysis?

**Instructions:**
Provide your evaluation in exactly in the following jsonschema format:
```json
{json.dumps(EvaluationScore.model_json_schema(), indent=2)}
```

Don't include any other text or fluff. Your response should be a valid json object that matches the above schema.

Score should be:
- 9-10: Excellent - Fully meets expectations, correct SQL and results
- 7-8: Good - Mostly correct with minor issues
- 5-6: Fair - Partially correct but has notable problems
- 3-4: Poor - Significant issues with approach or results
- 0-2: Very Poor - Incorrect or completely off-target

Keep notes concise and focused on key differences from expected analysis."""

    def _parse_evaluation_response(self, response_text: str) -> EvaluationScore:
        """Parse the LLM evaluation response into structured format."""
        response_text = response_text.strip().lstrip("```json").rstrip("```")
        try:
            evaluation = EvaluationScore.model_validate_json(response_text)
            return evaluation
        except Exception as e:
            raise ValueError(f"Failed to parse evaluation response: {e}")


def load_evaluator_config(evals_dir: Path) -> EvaluatorConfig:
    """Load evaluator configuration from evaluator.yaml."""
    config_path = evals_dir / "evaluator.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Evaluator config not found: {config_path}")

    with open(config_path, "r") as f:
        config_data = yaml.safe_load(f)

    return EvaluatorConfig(**config_data)
