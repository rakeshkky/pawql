# PawQL Evaluation Runner

A Python script to execute PawQL evaluation runs using the PromptQL API.

## Features

- Load evaluation configurations from YAML files
- Execute questions against PromptQL API using specified build versions
- Timezone configuration from config.yaml
- Generate markdown reports for each evaluation set
- Rich console output with progress tracking
- Comprehensive error handling and reporting
- Smart report skipping: automatically skips eval sets with existing reports
- Force re-run option to override existing reports
- Artifact support: renders PromptQL artifacts in collapsible sections with proper formatting
- LLM-as-a-judge evaluation: automatically evaluates PromptQL responses against expected analysis using Anthropic Claude

## Installation

This project uses `uv` as the Python build and run tool. Make sure you have `uv` installed:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Navigate to the evals directory and install the project dependencies:

```bash
cd evals
uv sync
```

## Usage

### Basic Usage

```bash
# Using command line flags
uv run run-eval --run-dir <eval_run_directory> --api-key <promptql_api_key>

# Using environment variables
PROMPTQL_API_KEY=<your_api_key> uv run run-eval --run-dir <eval_run_directory>
```

### Examples

```bash
# Run the first_run evaluation using command line API key
uv run run-eval --run-dir runs/first_run --api-key your-promptql-api-key

# Run using environment variables
PROMPTQL_API_KEY=your-api-key uv run run-eval --run-dir runs/first_run

# Run with DDN token for private DDN authentication
PROMPTQL_API_KEY=your-api-key DDN_TOKEN=your-jwt-token uv run run-eval --run-dir runs/first_run

# Force re-run even if reports already exist
uv run run-eval --run-dir runs/first_run --api-key your-promptql-api-key --force

# Specify a custom eval sets directory
uv run run-eval --run-dir runs/first_run --api-key your-promptql-api-key --eval-sets-dir /path/to/evalsets

# Using command line flags for both tokens
uv run run-eval --run-dir runs/first_run --api-key pk_abc123xyz --ddn-token eyJ0eXAiOiJKV1Q...
```

### Command Line Options

- `--run-dir`: Directory containing the `config.yaml` file for the evaluation run [required]
- `--api-key`: Your PromptQL API key (can also be set via `PROMPTQL_API_KEY` env var)
- `--ddn-token`: DDN JWT token for authentication (can also be set via `DDN_TOKEN` env var)
- `--eval-sets-dir`: Directory containing eval set files (default: `evals/evalsets` relative to run_dir)
- `-f, --force`: Force re-run evaluations even if reports already exist

### Environment Variables

- `PROMPTQL_API_KEY`: PromptQL API key (alternative to `--api-key` flag)
- `DDN_TOKEN`: DDN JWT token for private DDN authentication (alternative to `--ddn-token` flag)
- `ANTHROPIC_API_KEY`: Anthropic API key for LLM-as-a-judge evaluation (optional)

## Configuration Format

### Run Configuration (`config.yaml`)

```yaml
build_version: "771c7676fa"
description: "First run of PawQL evaluation, using default Hasura LLM provider"
timezone: "America/Los_Angeles"
eval_sets:
  - easy_questions.yaml
  - medium_questions.yaml
  - hard_questions.yaml
```

### Evaluator Configuration (`evaluator.yaml`)

```yaml
provider: anthropic
model: claude-3-5-sonnet-latest
```

### Evaluation Set Format

```yaml
eval_set_name: "Easy Questions - Single-table queries with basic filtering"
description: "Basic queries involving single tables with simple filtering operations"
difficulty: "easy"
items:
  - question: "How many active dogs are currently registered in the system?"
    expected_analysis: |
      Simple count with status filtering returning `31094` dogs.

      SQL Reference:
      ```sql
      SELECT COUNT(1) as active_dog_count
      FROM dogs
      WHERE status = 'ACTIVE';
      ```

  - question: "What are the names and locations of all active PawQL locations?"
    expected_analysis: |
      Basic selection with filtering and 8 records returned.

      SQL Reference:
      ```sql
      SELECT location_name, city, state
      FROM locations
      WHERE status = 'ACTIVE'
      ORDER BY location_name;
      ```
```

## Output

The script generates:

1. **Console Output**: Real-time progress tracking and summary statistics
2. **Markdown Reports**: Individual `.md` files for each evaluation set in the run directory

### Markdown Report Format

Each evaluation set generates a markdown file named `<eval_set_filename>.md` (e.g., `easy_questions.md`) containing:

- Run metadata (build version, timestamp, statistics)
- Summary of success/failure rates
- Detailed results for each question including:
  - The original question
  - Complete PromptQL API response with all assistant actions:
    - Assistant messages (shown as-is, including artifact references)
    - Generated SQL code (with syntax highlighting)
    - Execution plans
    - Code output and results
    - Error messages (if any)
  - Collapsible artifacts section with:
    - CSV/table data with proper formatting
    - JSON responses with syntax highlighting
    - SQL queries and other code artifacts
    - Artifact warnings and metadata
  - LLM-as-a-judge evaluation (if enabled):
    - Score (0-10) rating response quality against expected analysis
    - Concise evaluation notes explaining the score
  - Response time and timestamp

## Project Structure

```
evals/
├── pawql_evals/               # Python evaluation package
│   ├── __init__.py
│   ├── models.py              # Pydantic data models
│   ├── runner.py              # Main evaluation runner
│   └── markdown_renderer.py   # Markdown report generation
├── evalsets/                  # Evaluation question sets
│   ├── easy_questions.yaml
│   ├── medium_questions.yaml
│   └── hard_questions.yaml
├── runs/                      # Evaluation run configurations
│   └── first_run/
│       └── config.yaml
├── pyproject.toml             # Python project configuration
└── README.md                  # This file
```

## Development

### Type Checking

```bash
uv run --frozen pyright
```

### Code Formatting

```bash
uv run black pawql_evals/
uv run isort pawql_evals/
```

### Running Tests

```bash
uv run pytest
```

## Dependencies

- `promptql-api-sdk>=0.2.0`: PromptQL API client
- `pyyaml>=6.0`: YAML configuration parsing
- `pydantic>=2.0.0`: Data validation and serialization
- `click>=8.0.0`: Command-line interface
- `rich>=13.0.0`: Rich console output and progress tracking

## Error Handling

The script handles various error conditions:

- Missing configuration files
- Invalid YAML format
- PromptQL API errors
- Network connectivity issues
- File system permissions

All errors are logged with detailed messages and the script exits gracefully with appropriate exit codes.

## License

MIT License
