# SystemDesign Problem Set Agent

Automated agent that scans trending system design resources, identifies missing problem sets, generates new problem README files, and creates GitHub PRs.

## Features

- **Web Scraping**: Scans AlgoMaster, HelloInterview, DesignGurus, and Educative for trending problems
- **Smart Comparison**: Compares scraped problems with existing repo problems to find gaps
- **README Generation**: Creates staff-level problem READMEs following the existing format
- **GitHub Integration**: Creates branches, commits, pushes, and opens PRs with `sahil0017` as reviewer
- **Scheduled Execution**: Runs every 12 hours automatically when deployed

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌─────────────┐
│  Web Scraper │────►│   Generator  │────►│  Git + GitHub │────►│    PR       │
│  (4 sources) │     │  (README.md) │     │  (gh CLI)     │     │  (reviewer) │
└─────────────┘     └──────────────┘     └──────────────┘     └─────────────┘
       │                   │                    │                    │
       └───────────────────┴────────────────────┴────────────────────┘
                              Scheduler (every 12h)
```

## Project Structure

```
agent/
├── __init__.py          # Package init
├── agent_main.py        # Main orchestrator
├── config.py            # Settings & environment variables
├── models.py            # Data models (TrendingProblem, etc.)
├── scraper.py           # Web scraper for trending problems
├── problem_generator.py # README generation & comparison
├── github_client.py     # GitHub PR creation via gh CLI
├── scheduler.py         # Periodic scheduler (12h interval)
├── requirements.txt     # Python dependencies
├── Dockerfile           # Container image definition
├── railway.json         # Railway deployment config
└── README.md            # This file
```

## Prerequisites

- **Python 3.12+**
- **GitHub CLI** (`gh`) installed and authenticated
- **GitHub Personal Access Token** with `repo` scope

## Local Development

### 1. Install dependencies

```bash
cd agent
pip install -r requirements.txt
```

### 2. Set environment variables

```bash
export GITHUB_TOKEN=ghp_your_token_here
export GITHUB_REPO_OWNER=sahil0017
export GITHUB_REPO_NAME=SystemDesign
export GITHUB_REVIEWER=sahil0017
export REPO_PATH=/path/to/SystemDesign
```

### 3. Run once

```bash
python agent_main.py
```

### 4. Run scheduler (continuous)

```bash
python scheduler.py
```

### 5. Dry run mode

```bash
export DRY_RUN=true
python agent_main.py
```

### 6. Diagnostic mode

```bash
export AGENT_MODE=diagnostic
python agent_main.py
```

## Deployment on Railway

### 1. Create a new project on Railway

Go to [Railway](https://railway.app) and create a new project from this repository.

### 2. Configure environment variables

Add these variables in the Railway project settings:

| Variable | Value |
|----------|-------|
| `GITHUB_TOKEN` | Your GitHub PAT with `repo` scope |
| `GITHUB_REPO_OWNER` | `sahil0017` |
| `GITHUB_REPO_NAME` | `SystemDesign` |
| `GITHUB_REVIEWER` | `sahil0017` |
| `REPO_PATH` | `/repo` |
| `AGENT_RUN_INTERVAL_HOURS` | `12` |

### 3. Deploy

Railway will automatically build the Docker image and start the scheduler.

### 4. Monitor

Check the Railway logs to see agent runs:
```
2024-01-15 12:00:00 [INFO] Starting SystemDesign agent run...
2024-01-15 12:00:05 [INFO] Found 3 missing problems out of 50 trending
2024-01-15 12:00:10 [INFO] Generated 3 new problem files
2024-01-15 12:00:15 [INFO] PR created successfully: https://github.com/...
```

## Configuration

All settings are controlled via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `GITHUB_TOKEN` | (required) | GitHub Personal Access Token |
| `GITHUB_REPO_OWNER` | `sahil0017` | GitHub repository owner |
| `GITHUB_REPO_NAME` | `SystemDesign` | GitHub repository name |
| `GITHUB_REVIEWER` | `sahil0017` | GitHub username to add as PR reviewer |
| `REPO_PATH` | Current directory | Path to the repository |
| `AGENT_BRANCH_PREFIX` | `agent/add-problems` | Branch name prefix for PRs |
| `AGENT_RUN_INTERVAL_HOURS` | `12` | Hours between agent runs |
| `SCRAPER_REQUEST_DELAY` | `2.0` | Delay between HTTP requests (seconds) |
| `SCRAPER_TIMEOUT` | `15.0` | HTTP request timeout (seconds) |
| `SCRAPER_SOURCES` | `algomaster,hellointerview,designgurus,educative` | Comma-separated list of sources |
| `DRY_RUN` | `false` | If true, skip git/gh commands |

## How It Works

### 1. Scraping Phase

The agent scrapes 4 sources:
- **AlgoMaster**: System design and LLD problems
- **HelloInterview**: Interview-focused problem lists
- **DesignGurus**: System design master class
- **Educative**: Grokking system design interview

Each source is parsed for problem names and categories (HLD, LLD, Distributed Systems, etc.).

### 2. Comparison Phase

The generated list is compared with existing problems in the repo:
- Scans `hld/problems/`, `lld/problems/`, `distributed-systems/problems/`, `tradeoffs/`, `java/`
- Uses slug-based and fuzzy name matching to avoid duplicates
- Returns only problems not already present

### 3. Generation Phase

For each missing problem, a README is generated:
- **HLD**: Architecture diagram, staff-level considerations, scalability strategy
- **LLD**: Class diagram, design patterns, SOLID principles
- **Distributed Systems**: Consistency models, fault tolerance, consensus
- **Trade-offs**: Decision framework, comparison table
- **Java**: Concurrency patterns, JVM internals, performance tips

### 4. PR Creation Phase

1. Create a new branch: `agent/add-problems/20240115-120000`
2. Stage and commit all new files
3. Push to GitHub
4. Create a PR with `sahil0017` as reviewer
5. PR body includes summary of all new problems and their sources

## Adding New Sources

To add a new scraping source:

1. Add the source to `SOURCES` dict in `scraper.py`:
```python
"newsource": {
    "url": "https://example.com/problems",
    "type": "html",
}
```

2. Add a parser method:
```python
def _parse_newsource(self, html_text: str, source: str) -> list:
    problems = []
    # Parse HTML and extract problems
    return problems
```

3. Update the dispatcher in `_scrape_source()`:
```python
elif source_name == "newsource":
    return self._parse_newsource(html_text, source_name)
```

4. Add to `SCRAPER_SOURCES` env variable.

## Troubleshooting

### GitHub authentication fails

Ensure `gh auth status` works locally and the `GITHUB_TOKEN` has `repo` scope.

### No new problems found

The scraper uses a known-problems list. If sources add new problems, update the lists in `scraper.py`.

### PR creation fails

Check that the branch name is unique (timestamp-based) and that the remote is correctly configured.

## License

MIT
