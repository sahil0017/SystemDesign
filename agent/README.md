# SystemDesign Problem Set Agent

Automated agent that scans trending system design resources, identifies missing problem sets, generates new problem README files, and creates GitHub PRs.

**Deployed via GitHub Actions Cron** — runs every 12 hours automatically.

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

## Architecture

```
[GitHub Actions Cron (Every 12h)]
       │
       ▼
 1. Spins up Linux Runner
 2. Checks out target codebase
 3. Executes agent_main.py ───► (Scrapes/Evaluates problem sets)
       │
       ▼
 4. Modifies local project package files
 5. Auto-commits branch & pushes to GitHub
 6. Uses GitHub CLI to create PR & assign sahil0017
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

## Deployment

### GitHub Actions (Default)

The agent runs automatically via `.github/workflows/agent.yml`:

- **Schedule**: Every 12 hours (midnight and noon UTC)
- **Manual trigger**: Available via "Run workflow" button in Actions tab
- **Token**: Uses `GITHUB_TOKEN` (automatic, no setup needed)
- **Artifacts**: Run history persisted between runs via GitHub Actions artifacts

To enable:
1. Merge this PR
2. Go to **Actions** → **SystemDesign Agent** → enable workflows if disabled
3. The agent will run automatically every 12 hours

To run manually:
1. Go to **Actions** → **SystemDesign Agent** → **Run workflow**

### Local Development

```bash
cd agent
pip install -r requirements.txt
export GITHUB_TOKEN=your_token
export REPO_PATH=/path/to/SystemDesign
python agent_main.py
```

### Diagnostic Mode

```bash
cd agent
AGENT_MODE=diagnostic python agent_main.py
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

### Deploy Dashboard on Streamlit Cloud

1. Go to https://share.streamlit.app
2. Connect repository `sahil0017/SystemDesign`
3. Set main file to `agent/dashboard/app.py`
4. Add dependencies from `agent/requirements.txt`

## Files

| File | Description |
|------|-------------|
| `agent_main.py` | Main orchestrator and CLI entry point |
| `scraper.py` | Web scraper with caching, retry, and concurrent fetching |
| `problem_generator.py` | README generation with fuzzy matching and templates |
| `github_client.py` | GitHub PR creation via `gh` CLI |
| `scheduler.py` | One-shot runner for GitHub Actions |
| `config.py` | Environment-based configuration |
| `models.py` | Data models (TrendingProblem, RunHistory, etc.) |
| `dashboard/app.py` | Streamlit dashboard for tracking progress |
| `dashboard/README.md` | Dashboard documentation |
| `Dockerfile` | Container image (for local Docker testing) |
| `requirements.txt` | Python dependencies |
| `.gitignore` | Python cache and temp files |

## How It Works

1. **Scrape**: Concurrently fetches 5 web sources, caches responses for 6 hours
2. **Detect**: Matches scraped content against 100+ known problem keywords
3. **Filter**: Compares against existing repo problems using fuzzy matching (Levenshtein distance)
4. **Generate**: Creates tailored README files using problem-specific templates
5. **PR**: Creates a GitHub PR with `sahil0017` as reviewer, checks for existing open PRs first
6. **History**: Persists added problem slugs via GitHub Actions artifacts to avoid duplicates
