# SystemDesign Agent Dashboard

A Streamlit-based dashboard that helps you track your progress toward becoming a **Staff Software Engineer**.

## Features

- **📊 Dashboard** — Overview of all problems by category with stats
- **📚 Skills** — Detailed breakdown of each skill category with staff-level expectations
- **🎯 Staff Levels** — L5 (Senior) → L6 (Staff) → L7 (Senior Staff) progression guide
- **🗺️ Learning Path** — 4-phase roadmap from foundation to staff level
- **🤖 Agent Status** — See what problems the agent has added and recent PRs
- **🔍 Browse Problems** — Search and filter all problems, view full details

## How to Run

```bash
cd agent/dashboard
pip install -r ../requirements.txt
streamlit run app.py
```

Or from the project root:

```bash
cd agent/dashboard
streamlit run app.py -- REPO_PATH=/path/to/SystemDesign
```

## Deployment

The dashboard can be deployed on **Streamlit Cloud** by connecting this GitHub repository:

1. Go to https://share.streamlit.app
2. Connect repository `sahil0017/SystemDesign`
3. Set main file to `agent/dashboard/app.py`
4. Add dependencies from `agent/requirements.txt`

## What Makes This Useful for Staff Engineers?

The dashboard maps each problem to a **staff engineer skill framework**:

| Category | Staff Expectation |
|----------|-------------------|
| HLD | Design systems handling millions of users, make trade-off decisions |
| LLD | Design using SOLID principles, handle concurrency and thread safety |
| DB Design | Choose the right database, design schemas that scale |
| Distributed Systems | Understand Paxos/Raft, consistent hashing, saga patterns |
| API Design | Design versioned, idempotent APIs with proper error handling |
| Trade-offs | Articulate why one approach is better for a given context |
| Java | Write lock-free code, use virtual threads, optimize JVM performance |

The **automated agent** runs every 12 hours via GitHub Actions, scraping 5 sources to find new trending problems and adding them as PRs — keeping your practice material always current.
