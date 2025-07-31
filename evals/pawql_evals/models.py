"""Data models for PawQL evaluations."""

from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime


class EvalItem(BaseModel):
    """Individual evaluation item (question)."""

    question: str
    expected_analysis: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class EvalSet(BaseModel):
    """Collection of evaluation items."""

    eval_set_name: str
    description: Optional[str] = None
    difficulty: Optional[str] = None
    items: List[EvalItem]


class RunConfig(BaseModel):
    """Configuration for an evaluation run."""

    build_version: str
    description: Optional[str] = None
    eval_sets: List[str]
    timezone: str = Field(default="America/Los_Angeles")


class EvaluatorConfig(BaseModel):
    """Configuration for the LLM evaluator."""

    provider: str = Field(description="LLM provider (only 'anthropic' supported)")
    model: str = Field(description="Model name to use for evaluation")


class EvaluationScore(BaseModel):
    """LLM-as-a-judge evaluation score."""

    score: int = Field(ge=0, le=10, description="Score from 0-10")
    notes: str = Field(description="Concise notes on the evaluation")


class EvalResult(BaseModel):
    """Result of running a single evaluation item."""

    question: str
    response: str
    timestamp: datetime
    response_time_ms: Optional[int] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    evaluation: Optional[EvaluationScore] = None


class EvalSetResult(BaseModel):
    """Results for an entire evaluation set."""

    eval_set_name: str
    description: Optional[str] = None
    difficulty: Optional[str] = None
    results: List[EvalResult]
    total_questions: int
    successful_responses: int
    failed_responses: int
    average_response_time_ms: Optional[float] = None


class EvalRunResult(BaseModel):
    """Complete results for an evaluation run."""

    build_version: str
    run_description: Optional[str] = None
    timestamp: datetime
    eval_set_results: List[EvalSetResult]
    total_questions: int
    total_successful: int
    total_failed: int
    overall_average_response_time_ms: Optional[float] = None
