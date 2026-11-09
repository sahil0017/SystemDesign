# SystemDesign Problem Set Agent v1.0.0

Automated agent that scans trending system design resources, identifies missing problem sets, generates new problem README files, and creates GitHub PRs.

**Version**: 1.0.0 | **Deployed via GitHub Actions** — runs every 12 hours automatically.

## Features

- **Concurrent web scraping**: Scrapes 5 sources (AlgoMaster, HelloInterview, DesignGurus, Educative, GitHub Trending) concurrently
- **Response caching**: Caches HTTP responses for 6 hours to avoid redundant fetches
- **Retry with backoff**: Exponential backoff retry for transient failures
- **Fuzzy matching**: Levenshtein distance-based matching to catch near-duplicate problem names
- **Problem-specific templates**: Tailored content for RAG, LLM, fraud detection, streaming, etc.
- **Run history**: Persists added problems via GitHub Actions artifacts to avoid duplicate PRs
- **PR deduplication**: Checks for existing open agent PRs before creating new ones
- **Max problems per run**: Limits PRs to 5 problems by default to keep them manageable
- **Streamlit dashboard**: Web UI to track problems and staff engineer progress
- **Comprehensive tests**: pytest test suite covering models, fuzzy matching, cache, and generator

## Architecture

```
[GitHub Actions Cron (Every 12h)]
       │
       ▼
 1. Spins up Linux Runner
 2. Checks out target codebase
 3. Runs CI: lint + tests ───► (Validates agent code)
       │
       ▼
 4. Executes agent ───► (Scrapes/Evaluates problem sets)
       │
       ▼
 5. Modifies local project package files
 6. Auto-commits branch & pushes to GitHub
 7. Uses GitHub CLI to create PR & assign sahil0017
```

## Package Structure

```
agent/
├── __init__.py              # Package exports
├── agent_main.py            # Main orchestrator + CLI entry point
├── scheduler.py             # One-shot runner for GitHub Actions
├── requirements.txt         # Python dependencies
├── Dockerfile               # Container image
├── README.md                # This file
├── core/                    # Core shared modules
│   ├── __init__.py          # Version info
│   ├── config.py            # Environment-based settings
│   └── models.py            # Data models (TrendingProblem, RunHistory, etc.)
├── scraper/                 # Web scraping module
│   ├── __init__.py
│   ├── scraper.py           # TrendScraper class
│   ├── cache.py             # ResponseCache class
│   └── sources.py           # Source definitions + problem keywords
├── generator/               # Problem README generation
│   ├── __init__.py
│   ├── generator.py         # ProblemGenerator class
│   ├── fuzzy.py             # Levenshtein distance, similarity, normalize
│   └── templates.py         # Problem-specific content templates
├── github/                  # GitHub integration
│   ├── __init__.py
│   └── client.py            # GitHubClient class (gh CLI)
├── dashboard/               # Streamlit dashboard
│   ├── app.py               # Dashboard application
│   └── README.md            # Dashboard documentation
└── tests/                   # Test suite
    ├── __init__.py
    ├── test_models.py       # Data model tests
    ├── test_fuzzy.py        # Fuzzy matching tests
    ├── test_cache.py        # Response cache tests
    └── test_generator.py    # Problem generator tests
```

## Configuration

All settings are environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `GITHUB_TOKEN` | *(set by Actions)* | GitHub token for auth |
| `GITHUB_REPO_OWNER` | `sahil0017` | GitHub repository owner |
| `GITHUB_REPO_NAME` | `SystemDesign` | GitHub repository name |
| `GITHUB_REVIEWER` | `sahil0017` | GitHub username to add as PR reviewer |
| `REPO_PATH` | `${{ github.workspace }}` | Path to the checked-out repository |
| `AGENT_MAX_PROBLEMS_PER_RUN` | `5` | Max new problems per PR |
| `AGENT_SIMILARITY_THRESHOLD` | `0.6` | Levenshtein similarity threshold (0-1) |
| `CACHE_DIR` | `/tmp/agent-cache` | Directory for HTTP response cache |
| `CACHE_TTL_HOURS` | `6` | Cache time-to-live in hours |
| `RUN_HISTORY_FILE` | `/tmp/agent-cache/run_history.json` | Persisted run history |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `DRY_RUN` | `false` | If true, skip git/gh commands |

## CI/CD Pipeline

The agent has a two-stage CI/CD pipeline (`.github/workflows/agent.yml`):

### Stage 1: Test Agent (CI)
- **Triggers**: Push/PR to `agent/**`, schedule, manual dispatch
- **Steps**: Lint with ruff → Run pytest tests
- **Purpose**: Validate code quality before running the agent

### Stage 2: Run Agent (CD)
- **Triggers**: Schedule (every 12h), manual dispatch
- **Dependency**: Runs only if Stage 1 passes
- **Steps**: Install deps → Run agent → Upload run history

## Deployment

### GitHub Actions (Default)

The agent runs automatically via `.github/workflows/agent.yml`:

- **Schedule**: Every 12 hours (midnight and noon UTC)
- **Manual trigger**: Available via "Run workflow" button in Actions tab
- **Token**: Uses `GITHUB_TOKEN` (automatic, no setup needed)

### Local Development

```bash
cd agent
pip install -r requirements.txt
export GITHUB_TOKEN=your_token
export REPO_PATH=/path/to/SystemDesign
python -m agent.agent_main
```

### Diagnostic Mode

```bash
cd agent
AGENT_MODE=diagnostic python -m agent.agent_main
```

### Run Tests

```bash
cd agent
pip install -r requirements.txt
python -m pytest tests/ -v
```

## Streamlit Dashboard

A web dashboard helps you track problems and your progress toward becoming a Staff Engineer:

```bash
cd agent/dashboard
pip install -r ../requirements.txt
streamlit run app.py
```

### Dashboard Features

| Page | Description |
|------|-------------|
| 📊 Dashboard | Overview of all problems by category with stats |
| 📚 Skills | Skill breakdown with staff-level expectations |
| 🎯 Staff Levels | L5 → L6 → L7 progression guide |
| 🗺️ Learning Path | 4-phase roadmap from foundation to staff |
| 🤖 Agent Status | Agent run history and recent PRs |
| 🔍 Browse Problems | Search, filter, and view problem details |

## How It Works

1. **Scrape**: Concurrently fetches 5 web sources, caches responses for 6 hours
2. **Detect**: Matches scraped content against 100+ known problem keywords
3. **Filter**: Compares against existing repo problems using fuzzy matching (Levenshtein distance)
4. **Generate**: Creates tailored README files using problem-specific templates
5. **PR**: Creates a GitHub PR with `sahil0017` as reviewer, checks for existing open PRs first
6. **History**: Persists added problem slugs via GitHub Actions artifacts to avoid duplicates

## Release Versions

| Version | Date | Changes |
|---------|------|---------|
| **1.0.0** | 2026-11-09 | Initial release: refactored package structure, comprehensive tests, CI/CD pipeline, version tracking |
