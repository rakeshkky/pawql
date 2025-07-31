"""Main evaluation runner script."""

import os
import sys
import time
import yaml
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Union, cast, Dict

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from promptql_api_sdk import PromptQLClient
from promptql_api_sdk.exceptions import PromptQLAPIError
from promptql_api_sdk.types.models import QueryResponse, Artifact, ArtifactType

from .models import (
    EvalSet,
    RunConfig,
    EvalResult,
    EvalSetResult,
    EvalItem,
)
from .markdown_renderer import render_eval_set_results
from .evaluator import LLMEvaluator, load_evaluator_config


console = Console()


def format_raw_response(query_response: QueryResponse) -> str:
    """Format the raw PromptQL response for evaluation."""
    formatted = f"Thread ID: {query_response.thread_id}\n\n"

    formatted += "Assistant Actions:\n"
    for i, action in enumerate(query_response.assistant_actions):
        formatted += f"  Action {i + 1}:\n"
        if action.message:
            formatted += f"    Message: {action.message}\n"
        if action.plan:
            formatted += f"    Plan: {action.plan}\n"
        if action.code:
            formatted += f"    Code: {action.code}\n"
        if action.code_output:
            formatted += f"    Code Output: {action.code_output}\n"
        if action.code_error:
            formatted += f"    Code Error: {action.code_error}\n"
        formatted += "\n"

    if query_response.modified_artifacts:
        formatted += "Modified Artifacts:\n"
        for artifact in query_response.modified_artifacts:
            formatted += f"  - {artifact.identifier} ({artifact.artifact_type.value})\n"
            if artifact.title:
                formatted += f"    Title: {artifact.title}\n"
            if artifact.data:
                formatted += f"    Data: {str(artifact.data)[:200]}...\n"

    return formatted


def load_run_config(run_dir: Path) -> RunConfig:
    """Load run configuration from config.yaml."""
    config_path = run_dir / "config.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r") as f:
        config_data = yaml.safe_load(f)

    return RunConfig(**config_data)


def load_eval_set(eval_sets_dir: Path, eval_set_file: str) -> EvalSet:
    """Load an evaluation set from YAML file."""
    eval_set_path = eval_sets_dir / eval_set_file
    if not eval_set_path.exists():
        raise FileNotFoundError(f"Eval set file not found: {eval_set_path}")

    with open(eval_set_path, "r") as f:
        eval_set_data = yaml.safe_load(f)

    return EvalSet(**eval_set_data)


def run_single_question(
    client: PromptQLClient,
    question: str,
    expected_analysis: Optional[str] = None,
    evaluator: Optional[LLMEvaluator] = None,
) -> EvalResult:
    """Run a single question against the PromptQL API and evaluate the result."""
    start_time = time.time()
    timestamp = datetime.now()

    try:
        # Ensure we get a non-streaming response
        response = client.query(question, stream=False)
        end_time = time.time()
        response_time_ms = int((end_time - start_time) * 1000)

        # Cast to QueryResponse since we're not streaming
        query_response = cast(QueryResponse, response)

        # Store raw response for evaluation in structured format
        raw_response_str = format_raw_response(query_response)

        # Extract the complete response including all assistant actions and artifacts
        response_text = ""
        artifacts_section = ""

        if query_response.assistant_actions:
            # Capture all assistant actions with their details
            for i, action in enumerate(query_response.assistant_actions):
                if len(query_response.assistant_actions) > 1:
                    response_text += f"#### Assistant Action {i + 1}\n\n"

                if action.message:
                    response_text += f"{action.message}\n\n"

                if action.plan:
                    response_text += f"**Plan:**\n{action.plan}\n\n"

                if action.code:
                    response_text += (
                        f"**Generated Code:**\n```sql\n{action.code}\n```\n\n"
                    )

                if action.code_output:
                    response_text += (
                        f"**Code Output:**\n```\n{action.code_output}\n```\n\n"
                    )

                if action.code_error:
                    response_text += (
                        f"**Code Error:**\n```\n{action.code_error}\n```\n\n"
                    )

            # Capture artifacts if they exist
            if query_response.modified_artifacts:
                artifacts_section = "\n\n#### Artifacts\n\n"
                for artifact in query_response.modified_artifacts:
                    artifacts_section += f"<details>\n"
                    artifacts_section += f"<summary><strong>Artifact: {artifact.identifier}</strong> ({artifact.artifact_type.value})</summary>\n\n"

                    if artifact.title:
                        artifacts_section += f"**Title:** {artifact.title}\n\n"

                    if artifact.data:
                        # Determine content type for syntax highlighting
                        if artifact.artifact_type == ArtifactType.TABLE:
                            # For table type, data might be CSV or structured data
                            if isinstance(artifact.data, str):
                                artifacts_section += f"```csv\n{artifact.data}\n```\n"
                            else:
                                artifacts_section += f"```json\n{artifact.data}\n```\n"
                        elif artifact.artifact_type == ArtifactType.TEXT:
                            # For text type, render as plain text
                            artifacts_section += f"```\n{artifact.data}\n```\n"
                        else:
                            # Generic handling for other types
                            artifacts_section += f"```\n{artifact.data}\n```\n"

                    artifacts_section += "\n</details>\n\n"

            # Combine response and artifacts
            response_text = response_text.rstrip() + artifacts_section
        else:
            response_text = str(response)

        # Create base result
        result = EvalResult(
            question=question,
            response=response_text,
            timestamp=timestamp,
            response_time_ms=response_time_ms,
        )

        # Add evaluation if evaluator and expected analysis are provided
        if evaluator and expected_analysis:
            try:
                evaluation = evaluator.evaluate_response(
                    question=question,
                    promptql_response=response_text,
                    expected_analysis=expected_analysis,
                    raw_response=raw_response_str,
                )
                result.evaluation = evaluation
            except Exception as eval_error:
                console.print(
                    f"[yellow]Warning: Evaluation failed: {eval_error}[/yellow]"
                )

        return result

    except PromptQLAPIError as e:
        end_time = time.time()
        response_time_ms = int((end_time - start_time) * 1000)

        # Create base result for API error
        result = EvalResult(
            question=question,
            response="",
            timestamp=timestamp,
            response_time_ms=response_time_ms,
            error=str(e),
        )

        # Skip evaluation for error cases

        return result
    except Exception as e:
        end_time = time.time()
        response_time_ms = int((end_time - start_time) * 1000)

        # Create base result for unexpected error
        result = EvalResult(
            question=question,
            response="",
            timestamp=timestamp,
            response_time_ms=response_time_ms,
            error=f"Unexpected error: {str(e)}",
        )

        # Skip evaluation for error cases

        return result


def run_eval_set(
    client: PromptQLClient, eval_set: EvalSet, evaluator: Optional[LLMEvaluator] = None
) -> EvalSetResult:
    """Run all questions in an evaluation set."""
    results: List[EvalResult] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(
            f"Running {eval_set.eval_set_name}...", total=len(eval_set.items)
        )

        for item in eval_set.items:
            result = run_single_question(
                client=client,
                question=item.question,
                expected_analysis=item.expected_analysis,
                evaluator=evaluator,
            )
            results.append(result)
            progress.advance(task)

    # Calculate statistics
    successful_responses = sum(1 for r in results if r.error is None)
    failed_responses = len(results) - successful_responses

    response_times = [
        r.response_time_ms for r in results if r.response_time_ms is not None
    ]
    average_response_time = (
        sum(response_times) / len(response_times) if response_times else None
    )

    return EvalSetResult(
        eval_set_name=eval_set.eval_set_name,
        description=eval_set.description,
        difficulty=eval_set.difficulty,
        results=results,
        total_questions=len(results),
        successful_responses=successful_responses,
        failed_responses=failed_responses,
        average_response_time_ms=average_response_time,
    )


@click.command()
@click.option(
    "--run-dir",
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Directory containing config.yaml for the evaluation run",
)
@click.option(
    "--api-key",
    type=str,
    help="PromptQL API key (can also be set via PROMPTQL_API_KEY env var)",
)
@click.option(
    "--ddn-token",
    type=str,
    help="DDN JWT token for authentication (can also be set via DDN_TOKEN env var)",
)
@click.option(
    "--eval-sets-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Directory containing eval set files (default: evalsets relative to run_dir)",
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Force re-run evaluations even if reports already exist",
)
def main(
    run_dir: str,
    api_key: Optional[str],
    ddn_token: Optional[str],
    eval_sets_dir: Optional[str],
    force: bool,
) -> None:
    """
    Run PawQL evaluations.
    """
    run_path = Path(run_dir)

    # Get API key from environment if not provided
    if not api_key:
        api_key = os.getenv("PROMPTQL_API_KEY")

    if not api_key:
        console.print(
            "[red]Error: PromptQL API key is required. Provide it via --api-key or PROMPTQL_API_KEY env var.[/red]"
        )
        sys.exit(1)

    # Get DDN token from environment if not provided
    if not ddn_token:
        ddn_token = os.getenv("DDN_TOKEN")

    # Determine eval sets directory
    if eval_sets_dir:
        eval_sets_path = Path(eval_sets_dir)
    else:
        # Default to evalsets in the same directory as run_dir's parent
        eval_sets_path = run_path.parent.parent / "evalsets"

    if not eval_sets_path.exists():
        console.print(
            f"[red]Error: Eval sets directory not found: {eval_sets_path}[/red]"
        )
        sys.exit(1)

    try:
        # Load configuration
        config = load_run_config(run_path)
        console.print(
            f"[green]Loaded config for build version: {config.build_version}[/green]"
        )
        console.print(f"[green]Using timezone: {config.timezone}[/green]")

        # Load evaluator configuration
        evaluator = None
        try:
            evaluator_config = load_evaluator_config(run_path.parent.parent)
            evaluator = LLMEvaluator(evaluator_config)
            console.print(
                f"[green]Loaded evaluator: {evaluator_config.provider} ({evaluator_config.model})[/green]"
            )
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load evaluator: {e}[/yellow]")
            console.print("[yellow]Continuing without evaluation...[/yellow]")

        # Initialize PromptQL client
        client_kwargs: Dict[str, Union[str, Dict[str, str]]] = {
            "api_key": api_key,
            "build_version": config.build_version,
            "timezone": config.timezone,
        }

        # Add DDN headers if token is provided
        if ddn_token:
            client_kwargs["ddn_headers"] = {"x-hasura-ddn-token": ddn_token}

        client = PromptQLClient(**client_kwargs)  # type: ignore

        # Run evaluations
        eval_set_results: List[EvalSetResult] = []

        for eval_set_file in config.eval_sets:
            console.print(f"\n[blue]Loading eval set: {eval_set_file}[/blue]")
            eval_set = load_eval_set(eval_sets_path, eval_set_file)

            # Check if report already exists
            # Use eval set file name without extension for cleaner file names
            eval_set_basename = eval_set_file.replace(".yaml", "").replace(".yml", "")
            output_file = run_path / f"{eval_set_basename}.md"

            if output_file.exists() and not force:
                console.print(f"[yellow]Report already exists: {output_file}[/yellow]")
                console.print(
                    f"[yellow]Skipping eval set. Use --force to re-run.[/yellow]"
                )
                continue

            console.print(f"[blue]Running {len(eval_set.items)} questions...[/blue]")
            result = run_eval_set(client, eval_set, evaluator)
            eval_set_results.append(result)

            # Save markdown results immediately
            markdown_content = render_eval_set_results(result, config.build_version)

            with open(output_file, "w") as f:
                f.write(markdown_content)

            console.print(f"[green]Results saved to: {output_file}[/green]")

        # Display summary
        display_summary(eval_set_results)

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


def display_summary(eval_set_results: List[EvalSetResult]) -> None:
    """Display a summary table of results."""
    table = Table(title="Evaluation Summary")

    table.add_column("Eval Set", style="cyan")
    table.add_column("Questions", justify="right")
    table.add_column("Successful", justify="right", style="green")
    table.add_column("Failed", justify="right", style="red")
    table.add_column("Success Rate", justify="right")
    table.add_column("Avg Response Time (ms)", justify="right")

    total_questions = 0
    total_successful = 0
    total_failed = 0
    all_response_times = []

    for result in eval_set_results:
        success_rate = (
            (result.successful_responses / result.total_questions * 100)
            if result.total_questions > 0
            else 0
        )
        avg_time = (
            f"{result.average_response_time_ms:.0f}"
            if result.average_response_time_ms
            else "N/A"
        )

        table.add_row(
            result.eval_set_name,
            str(result.total_questions),
            str(result.successful_responses),
            str(result.failed_responses),
            f"{success_rate:.1f}%",
            avg_time,
        )

        total_questions += result.total_questions
        total_successful += result.successful_responses
        total_failed += result.failed_responses

        if result.average_response_time_ms:
            all_response_times.extend(
                [r.response_time_ms for r in result.results if r.response_time_ms]
            )

    # Add totals row
    overall_success_rate = (
        (total_successful / total_questions * 100) if total_questions > 0 else 0
    )
    overall_avg_time = (
        sum(all_response_times) / len(all_response_times)
        if all_response_times
        else None
    )
    avg_time_str = f"{overall_avg_time:.0f}" if overall_avg_time else "N/A"

    table.add_section()
    table.add_row(
        "[bold]TOTAL[/bold]",
        f"[bold]{total_questions}[/bold]",
        f"[bold]{total_successful}[/bold]",
        f"[bold]{total_failed}[/bold]",
        f"[bold]{overall_success_rate:.1f}%[/bold]",
        f"[bold]{avg_time_str}[/bold]",
    )

    console.print("\n")
    console.print(table)


if __name__ == "__main__":
    main()
