# SystemDesign Problem Set Agent

Automated agent that scans trending system design resources, identifies missing problem sets, generates new problem README files, and creates GitHub PRs.

## Features

- **Concurrent web scraping**: Scrapes 5 sources (AlgoMaster, HelloInterview, DesignGurus, Educative, GitHub Trending) concurrently
- **Response caching**: Caches HTTP responses for 6 hours to avoid redundant fetches
- **Retry with backoff**: Exponential backoff retry for transient failures
- **Fuzzy matching**: Levenshtein distance-based matching to catch near-duplicate problem names
- **Problem-specific templates**: Tailored content for RAG, LLM, fraud detection, streaming, etc.
- **Run history**: Persists added problems to avoid duplicate PRs across restarts
- **PR deduplication**: Checks for existing open agent PRs before creating new ones
- **Health check server**: HTTP endpoints for Railway/container orchestration (`/health`, `/ready`, `/metrics`)
- **Max problems per run**: Limits PRs to 5 problems by default to keep them manageable
- **Graceful shutdown**: Handles SIGTERM/SIGINT for clean container shutdown

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌────────────┐
│  Scheduler  │────►│   Agent      │────►│   Scraper   │────►│  Web Sites │
│  (12h)      │     │  Orchestrator│     │  (5 sources)│     │            │
└─────────────┘     └──────┬───────┘     └─────────────┘     └────────────┘
                           │
                    ┌──────▼───────┐
                    │  Generator   │
                    │  (fuzzy +    │
                    │  templates)  │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  GitHub CLI  │
                    │  (PR +       │
                    │  reviewer)   │
                    └──────────────┘
```

## Configuration

All settings are environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `GITHUB_TOKEN` | *(required)* | GitHub personal access token with `repo` scope |
| `GITHUB_REPO_OWNER` | `sahil0017` | GitHub repository owner |
| `GITHUB_REPO_NAME` | `SystemDesign` | GitHub repository name |
| `GITHUB_REVIEWER` | `sahil0017` | GitHub username to add as PR reviewer |
| `REPO_PATH` | `/repo` | Path to the cloned repository |
| `AGENT_RUN_INTERVAL_HOURS` | `12` | Hours between agent runs |
| `AGENT_MAX_PROBLEMS_PER_RUN` | `5` | Max new problems per PR |
| `AGENT_SIMILARITY_THRESHOLD` | `0.6` | Levenshtein similarity threshold (0-1) |
| `CACHE_DIR` | `/tmp/agent-cache` | Directory for HTTP response cache |
| `CACHE_TTL_HOURS` | `6` | Cache time-to-live in hours |
| `HEALTH_CHECK_PORT` | `8080` | Port for health check HTTP server |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `DRY_RUN` | `false` | If true, skip git/gh commands |

## Deployment

### Railway

1. Create a new project from this repository
2. Set environment variables:
   - `GITHUB_TOKEN`: Your GitHub PAT with `repo` scope
   - `REPO_PATH=/repo`
   - `AGENT_RUN_INTERVAL_HOURS=12`
3. Railway will automatically build from `Dockerfile` and deploy

### Docker

```bash
docker build -f agent/Dockerfile -t systemdesign-agent .
docker run -d \
  -e GITHUB_TOKEN=your_token \
  -e REPO_PATH=/repo \
  -p 8080:8080 \
  --name systemdesign-agent \
  systemdesign-agent
```

### Local Development

```bash
cd agent
pip install -r requirements.txt
export GITHUB_TOKEN=your_token
export REPO_PATH=/path/to/SystemDesign
python scheduler.py
```

### Diagnostic Mode

```bash
cd agent
AGENT_MODE=diagnostic python agent_main.py
```

## Health Check Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health status with run metrics |
| `GET /ready` | Readiness check |
| `GET /metrics` | Prometheus-style metrics |

Example response:
```json
{
  "status": "healthy",
  "uptime_runs": 5,
  "successes": 5,
  "failures": 0,
  "last_run_status": "success",
  "last_run_time": "2025-01-01T12:00:00+00:00"
}
```

## Files

| File | Description |
|------|-------------|
| `agent_main.py` | Main orchestrator and CLI entry point |
| `scraper.py` | Web scraper with caching, retry, and concurrent fetching |
| `problem_generator.py` | README generation with fuzzy matching and templates |
| `github_client.py` | GitHub PR creation via `gh` CLI |
| `scheduler.py` | Periodic scheduler with health check server |
| `config.py` | Environment-based configuration |
| `models.py` | Data models (TrendingProblem, RunHistory, etc.) |
| `Dockerfile` | Container image for Railway deployment |
| `railway.json` | Railway deployment configuration |
| `requirements.txt` | Python dependencies |

## How It Works

1. **Scrape**: Concurrently fetches 5 web sources, caches responses for 6 hours
2. **Detect**: Matches scraped content against 100+ known problem keywords
3. **Filter**: Compares against existing repo problems using fuzzy matching (Levenshtein distance)
4. **Generate**: Creates tailored README files using problem-specific templates
5. **PR**: Creates a GitHub PR with `sahil0017` as reviewer, checks for existing open PRs first
6. **History**: Persists added problem slugs to avoid duplicates across runs
