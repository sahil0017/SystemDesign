"""
Streamlit Dashboard for SystemDesign Repository — v2

Dynamic, resilient dashboard for tracking system design problems, the
automation agent, and your staff-engineer progress.

Resilience features:
- Cached data loading (st.cache_data with TTL) so the UI stays responsive
- Graceful degradation: every loader returns empty structures instead of
  raising, and the UI renders informative empty states
- Missing directories / corrupt files / absent git binary are all tolerated
- Fallback theme safe for Streamlit Cloud (no custom CSS dependency)

Features:
- Overview KPIs with deltas vs previous run
- Personal progress tracker (checkboxes persisted in session state)
- Category & difficulty coverage charts (built-in plotly-free altair via st.bar_chart)
- Search + multi-filter browsing with pagination
- Agent run history and wiki ledger visualization
- Random "next problem" recommender
- Export your progress as CSV
"""

import json
import os
import random
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st

# ------------------------------------------------------------------ #
#  Configuration
# ------------------------------------------------------------------ #

st.set_page_config(
    page_title="SystemDesign — Staff Engineer Roadmap",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

REPO_ROOT = Path(os.environ.get("REPO_PATH", Path(__file__).resolve().parent.parent.parent))
LEDGER_DIR = REPO_ROOT / ".agent"
HISTORY_FALLBACK = Path(os.environ.get("RUN_HISTORY_FILE", "/tmp/agent-cache/run_history.json"))

SKILL_CATEGORIES = {
    "System Design (HLD)": {
        "icon": "🌐",
        "description": "Design large-scale distributed systems used in production.",
        "staff_expectation": "Design systems for millions of users; make consistency/availability trade-offs; justify architecture choices.",
        "problems_key": "hld",
    },
    "Object-Oriented Design (LLD)": {
        "icon": "🧱",
        "description": "Design clean, extensible, testable object-oriented systems.",
        "staff_expectation": "Apply SOLID and design patterns; reason about concurrency, thread safety, and API design.",
        "problems_key": "lld",
    },
    "Database Design": {
        "icon": "🗄️",
        "description": "Design efficient data models for relational and NoSQL databases.",
        "staff_expectation": "Choose the right database; design schemas that scale; know indexing, partitioning, replication.",
        "problems_key": "db_design",
    },
    "Distributed Systems": {
        "icon": "⚡",
        "description": "Understand consensus, replication, partitioning, and distributed algorithms.",
        "staff_expectation": "Know Paxos/Raft, consistent hashing, saga patterns; debug distributed failures.",
        "problems_key": "distributed_systems",
    },
    "API Design": {
        "icon": "🔌",
        "description": "Model RESTful and gRPC APIs for real-world services.",
        "staff_expectation": "Design versioned, idempotent APIs; evaluate REST vs gRPC vs GraphQL trade-offs.",
        "problems_key": "api_modeling",
    },
    "Trade-offs Analysis": {
        "icon": "⚖️",
        "description": "Evaluate architectural trade-offs and make informed decisions.",
        "staff_expectation": "Articulate why one approach beats another for a given context (cost, latency, reliability, velocity).",
        "problems_key": "tradeoffs",
    },
    "Java Concurrency & Advanced": {
        "icon": "☕",
        "description": "Master Java concurrency, virtual threads, and advanced patterns.",
        "staff_expectation": "Write lock-free code; use virtual threads; optimize JVM performance for high throughput.",
        "problems_key": "java",
    },
}

STAFF_LEVELS = {
    "L5-Senior": {"target": 0.35, "description": "Can solve medium-complexity problems independently.", "color": "#3b82f6"},
    "L6-Staff": {"target": 0.75, "description": "Can solve hard problems and mentor others.", "color": "#8b5cf6"},
    "L7-Senior Staff": {"target": 0.9, "description": "Can design novel solutions and drive technical strategy.", "color": "#f59e0b"},
}

# ------------------------------------------------------------------ #
#  Data model
# ------------------------------------------------------------------ #

@dataclass
class Problem:
    name: str
    category: str          # display category (skill name)
    category_key: str      # problems dict key
    difficulty: Optional[str] = None
    readme_path: Optional[str] = None
    slug: str = ""
    added_by_agent: bool = False
    added_on: str = ""


# ------------------------------------------------------------------ #
#  Resilient loaders (all cached, all failure-tolerant)
# ------------------------------------------------------------------ #

def _safe_slug(folder_name: str) -> str:
    return folder_name


def _pretty(name: str) -> str:
    return name.replace("-", " ").title()


@st.cache_data(ttl=120, show_spinner="Scanning repository…")
def discover_problems(repo_root_str: str) -> dict:
    """Scan the repository and return problems grouped by category key.

    Never raises: unreadable/missing dirs are skipped with a warning dict.
    """
    root = Path(repo_root_str)
    problems: dict = {}

    def _add(key: str, path: Path, display: str, difficulty: Optional[str] = None):
        readme = path / "README.md"
        if readme.exists():
            try:
                problems.setdefault(key, []).append(Problem(
                    name=_pretty(path.name),
                    category=display,
                    category_key=key,
                    difficulty=difficulty,
                    readme_path=str(readme),
                    slug=path.name,
                ))
            except OSError:
                pass

    # HLD: flat problems + case studies
    for sub, disp_diff in (("problems", None), ("case-studies", "case-study")):
        d = root / "hld" / sub
        if d.is_dir():
            for f in sorted(d.iterdir()):
                if f.is_dir():
                    _add("hld", f, "System Design (HLD)", disp_diff)

    # LLD: difficulty subfolders
    lld_dir = root / "lld" / "problems"
    if lld_dir.is_dir():
        for difficulty_dir in sorted(lld_dir.iterdir()):
            if difficulty_dir.is_dir():
                for f in sorted(difficulty_dir.iterdir()):
                    if f.is_dir():
                        _add("lld", f, "Object-Oriented Design (LLD)", difficulty_dir.name)

    # DB design: category subfolders (relational/nosql/hybrid/advanced)
    db_dir = root / "db-design" / "problems"
    if db_dir.is_dir():
        for cat_dir in sorted(db_dir.iterdir()):
            if cat_dir.is_dir():
                for f in sorted(cat_dir.iterdir()):
                    if f.is_dir():
                        _add("db_design", f, "Database Design", cat_dir.name)
            elif cat_dir.suffix == "" :
                pass

    # Distributed systems: category subfolders
    ds_dir = root / "distributed-systems" / "problems"
    if ds_dir.is_dir():
        for cat_dir in sorted(ds_dir.iterdir()):
            if cat_dir.is_dir():
                for f in sorted(cat_dir.iterdir()):
                    if f.is_dir():
                        _add("distributed_systems", f, "Distributed Systems", cat_dir.name)

    # API modeling: subfolders or flat
    api_dir = root / "api-modeling" / "problems"
    if api_dir.is_dir():
        for f in sorted(api_dir.rglob("README.md")):
            if f.parent.name != "problems":
                _add("api_modeling", f.parent, "API Design", f.parent.parent.name)

    # Trade-offs: flat dir
    to_dir = root / "tradeoffs"
    if to_dir.is_dir():
        for f in sorted(to_dir.iterdir()):
            if f.is_dir() and (f / "README.md").exists():
                _add("tradeoffs", f, "Trade-offs Analysis")

    # Java: flat + nested
    java_dir = root / "java" / "problems"
    if java_dir.is_dir():
        for f in sorted(java_dir.rglob("README.md")):
            rel = f.parent.relative_to(java_dir)
            difficulty = str(rel.parent) if rel.parent != Path(".") else None
            _add("java", f.parent, "Java Concurrency & Advanced", difficulty or None)

    return problems


@st.cache_data(ttl=60, show_spinner="Reading ledger…")
def load_ledger(repo_root_str: str) -> pd.DataFrame:
    """Read the in-repo agent ledger (.agent/Problem-Ledger.md).

    Tolerant of: missing file, malformed tables, partial rows.
    Returns a DataFrame with columns: slug, name, category, source, added.
    """
    ledger = Path(repo_root_str) / ".agent" / "Problem-Ledger.md"
    rows = []
    if ledger.exists():
        try:
            for line in ledger.read_text().splitlines():
                line = line.strip()
                if not line.startswith("| `"):
                    continue
                parts = [p.strip().strip("`") for p in line.strip("|").split("|")]
                if len(parts) >= 5:
                    rows.append({
                        "slug": parts[0],
                        "name": parts[1],
                        "category": parts[2],
                        "source": parts[3],
                        "added": parts[4],
                    })
        except OSError:
            pass

    # Fall back to legacy run-history JSON
    if not rows and HISTORY_FALLBACK.exists():
        try:
            data = json.loads(HISTORY_FALLBACK.read_text())
            rows = [{"slug": s, "name": "", "category": "", "source": "legacy", "added": ""}
                    for s in data.get("added_slugs", [])]
        except (OSError, json.JSONDecodeError):
            pass

    return pd.DataFrame(rows, columns=["slug", "name", "category", "source", "added"])


@st.cache_data(ttl=300, show_spinner=True)
def load_pr_history(repo_full_name: str, limit: int = 10) -> list:
    """Fetch PR history via gh CLI; returns [] on any failure."""
    try:
        result = subprocess.run(
            ["gh", "pr", "list", "--repo", repo_full_name,
             "--state", "all", "--json", "number,title,url,createdAt,state",
             "--limit", str(limit)],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
        pass
    return []


@st.cache_data(ttl=300, show_spinner=True)
def load_run_log(repo_root_str: str) -> list:
    """Parse .agent/Run-Log.md into run summaries."""
    path = Path(repo_root_str) / ".agent" / "Run-Log.md"
    runs = []
    if not path.exists():
        return runs
    try:
        current = None
        for line in path.read_text().splitlines():
            if line.startswith("## Run "):
                if current:
                    runs.append(current)
                current = {"when": line.replace("## Run ", "").strip(), "pr": "", "problems": []}
            elif current is not None:
                if line.startswith("- PR:"):
                    current["pr"] = line.replace("- PR:", "").strip()
                elif line.strip().startswith("- ") and "`" in line:
                    current["problems"].append(line.strip("- ").strip("`").strip())
        if current:
            runs.append(current)
    except OSError:
        pass
    return runs


# ------------------------------------------------------------------ #
#  Progress tracking (session state, with CSV export)
# ------------------------------------------------------------------ #

def progress_state() -> dict:
    if "progress" not in st.session_state:
        st.session_state.progress = {}
    return st.session_state.progress


def render_progress_controls(all_problems: list):
    st.markdown("## ✅ My Progress")
    st.caption("Tick problems you've solved. Progress persists during your session and can be exported.")

    prog = progress_state()
    by_key = {p.slug + "|" + (p.category_key or ""): p for p in all_problems}

    left, right = st.columns([1, 3])
    with left:
        done = sum(1 for v in prog.values() if v)
        total = len(all_problems)
        pct = done / total if total else 0.0
        st.metric("Solved", f"{done}/{total}", f"{pct:.0%}")
        st.progress(min(pct, 1.0))
        csv = pd.DataFrame([
            {"problem": by_key[k].name if k in by_key else k, "category": by_key[k].category if k in by_key else "", "solved": True}
            for k, v in prog.items() if v
        ])
        if not csv.empty:
            st.download_button("⬇️ Export CSV", csv.to_csv(index=False), "my-progress.csv", "text/csv")
    with right:
        # Show only unsolved (next up) to keep the list manageable
        unsolved = [p for p in all_problems if not prog.get(p.slug + "|" + (p.category_key or ""))]
        show_n = st.slider("Show next N unsolved", 10, min(100, len(unsolved)) if unsolved else 10, 20)
        for p in unsolved[:show_n]:
            key = p.slug + "|" + (p.category_key or "")
            label = f"{p.name}" + (f" `{p.difficulty}`" if p.difficulty else "")
            prog[key] = st.checkbox(label, key=f"cb_{key}")


# ------------------------------------------------------------------ #
#  Charts
# ------------------------------------------------------------------ #

def render_coverage_charts(problems: dict, ledger: pd.DataFrame):
    st.markdown("## 📈 Coverage")
    col1, col2 = st.columns(2)

    with col1:
        cat_counts = {k: len(v) for k, v in problems.items()}
        if cat_counts:
            df = pd.DataFrame({"Category": list(cat_counts.keys()), "Problems": list(cat_counts.values())})
            st.bar_chart(df.set_index("Category"), height=280)
            st.caption("Problems per module")
        else:
            st.info("No problems discovered in this checkout.")

    with col2:
        # Difficulty distribution across LLD + DB + DS + Java
        diffs = {}
        for lst in problems.values():
            for p in lst:
                if p.difficulty:
                    diffs[p.difficulty] = diffs.get(p.difficulty, 0) + 1
        if diffs:
            df = pd.DataFrame({"Difficulty": list(diffs.keys()), "Count": list(diffs.values())})
            st.bar_chart(df.set_index("Difficulty"), height=280)
            st.caption("Difficulty mix")
        else:
            st.info("No difficulty metadata found.")


def render_level_progress(done: int, total: int):
    st.markdown("## 🎯 Level Progress")
    pct = done / total if total else 0.0
    for level, info in STAFF_LEVELS.items():
        target = info["target"]
        met = pct >= target
        bar = min(pct / target, 1.0) if target else 0
        st.markdown(f"**{level}** — target {target:.0%} of catalogue")
        st.progress(bar)
        st.caption(info["description"] + ("  \n✅ **Met!**" if met else f"  \nSolve {max(0, int(target*total - done))} more"))


# ------------------------------------------------------------------ #
#  Page renderers
# ------------------------------------------------------------------ #

def render_header(ledger: pd.DataFrame):
    last_run = ledger["added"].dropna().max() if not ledger.empty else ""
    st.markdown(f"""
        # 🏗️ SystemDesign — Staff Engineer Roadmap
        An automated agent **discovers trending design problems**, dedups against the
        repository ledger, and opens PRs every 12 hours.
        {f"**Last agent activity:** `{last_run}`" if last_run else ""}
    """)


def render_overview(problems: dict, ledger: pd.DataFrame):
    total = sum(len(v) for v in problems.values())
    cols = st.columns(5)
    cats = [("HLD", "hld", "🌐"), ("LLD", "lld", "🧱"), ("DB", "db_design", "🗄️"),
            ("DS", "distributed_systems", "⚡"), ("Java", "java", "☕")]
    for i, (label, key, icon) in enumerate(cats):
        with cols[i]:
            n_agent = 0 if ledger.empty else ledger[
                ledger["slug"].isin([p.slug for p in problems.get(key, [])])
            ].shape[0]
            st.metric(f"{icon} {label}", len(problems.get(key, [])),
                      delta=f"{n_agent} by agent" if n_agent else None)

    st.metric("📊 Total Problems", total)

    if ledger.empty:
        st.info("🤖 No agent ledger yet — the next scheduled run will populate `.agent/Problem-Ledger.md`.")
    else:
        st.success(f"🤖 Agent ledger active: **{len(ledger)}** problems tracked.")


def render_browser(problems: dict):
    st.markdown("## 🔍 Browse Problems")
    flat = [p for lst in problems.values() for p in lst]

    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        q = st.text_input("🔎 Search", placeholder="e.g. cache, uber, threads")
    with c2:
        cats = ["All"] + list(SKILL_CATEGORIES.keys())
        cat = st.selectbox("Category", cats)
    with c3:
        difficulties = sorted({p.difficulty for p in flat if p.difficulty})
        diff = st.selectbox("Difficulty", ["All"] + difficulties)

    rows = flat
    if cat != "All":
        rows = [p for p in rows if p.category == cat]
    if diff != "All":
        rows = [p for p in rows if p.difficulty == diff]
    if q:
        ql = q.lower()
        rows = [p for p in rows if ql in p.name.lower()]

    st.caption(f"{len(rows)} problems")
    per_page = 30
    page = st.number_input("Page", 1, max(1, (len(rows) + per_page - 1)//per_page), 1)
    chunk = rows[(page-1)*per_page : page*per_page]

    cols = st.columns(3)
    for i, p in enumerate(chunk):
        with cols[i % 3]:
            diff = f" `{p.difficulty}`" if p.difficulty else ""
            with st.expander(f"**{p.name}**{diff}"):
                st.caption(p.category)
                if st.button("📖 View", key=f"view_{p.slug}_{p.category_key}"):
                    st.session_state["open_problem"] = p.readme_path
                if st.session_state.get("open_problem") == p.readme_path:
                    try:
                        st.markdown(Path(p.readme_path).read_text())
                    except OSError:
                        st.error("README unreadable")


def render_agent_page(problems: dict, ledger: pd.DataFrame, run_log: list, pr_history: list):
    st.markdown("## 🤖 Agent Status")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Ledger entries", len(ledger))
    with c2:
        st.metric("Runs logged", len(run_log))
    with c3:
        last = run_log[-1]["when"] if run_log else "never"
        st.metric("Last run", last[:16])

    if run_log:
        st.markdown("### Recent runs")
        df = pd.DataFrame([
            {"When": r["when"], "PR": r["pr"] or "—", "Problems": len(r["problems"])}
            for r in reversed(run_log[-10:])
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)

    if not ledger.empty:
        st.markdown("### Ledger (all agent-added problems)")
        repo_slugs = {p.slug for lst in problems.values() for p in lst}
        show = ledger.copy()
        show["status"] = show["slug"].map(
            lambda s: "✅ merged" if s in repo_slugs else "⏳ in PR/pending")
        st.dataframe(show, use_container_width=True, hide_index=True, height=320)

    st.markdown("### Recent pull requests")
    if pr_history:
        for pr in pr_history[:5]:
            st.markdown(f"- [#{pr.get('number','?')}]({pr.get('url','#')}) "
                        f"**{pr.get('title','')}** `{pr.get('state','')}` — "
                        f"{(pr.get('createdAt') or '')[:10]}")
    else:
        st.caption("PR history unavailable (needs `gh` CLI authenticated locally).")


def render_recommendation(all_problems: list):
    st.markdown("## 🎲 Pick one for me")
    if not all_problems:
        st.info("No problems available.")
        return
    if st.button("🎲 Give me a random unsolved problem"):
        prog = progress_state()
        unsolved = [p for p in all_problems if not prog.get(p.slug + "|" + (p.category_key or ""), False)]
        pool = unsolved or all_problems
        p = random.choice(pool)
        diff = f" `{p.difficulty}`" if p.difficulty else ""
        st.success(f"**{p.name}**{diff} — {p.category}")
        if p.readme_path and Path(p.readme_path).exists():
            st.markdown(Path(p.readme_path).read_text()[:2000])


# ------------------------------------------------------------------ #
#  Main
# ------------------------------------------------------------------ #

def main():
    problems = discover_problems(str(REPO_ROOT))
    ledger = load_ledger(str(REPO_ROOT))
    run_log = load_run_log(str(REPO_ROOT))
    pr_history = load_pr_history("sahil0017/SystemDesign")

    flat = [p for lst in problems.values() for p in lst]
    prog = progress_state()
    done = sum(1 for v in prog.values() if v)

    st.sidebar.markdown("## 🧭 Navigation")
    page = st.sidebar.radio("Go to",
        ["📊 Overview", "📈 Coverage", "✅ My Progress", "🔍 Browse",
         "🤖 Agent", "🎯 Levels", "🎲 Random"],
        index=0, label_visibility="collapsed")
    st.sidebar.markdown(f"**Catalogue:** {len(flat)} problems")
    st.sidebar.markdown(f"**Solved:** {done}")
    st.sidebar.markdown(f"**Ledger:** {len(ledger)} agent entries")
    if st.sidebar.button("🔄 Refresh data"):
        discover_problems.clear()
        load_ledger.clear()
        load_run_log.clear()
        load_pr_history.clear()
        st.rerun()

    if page == "📊 Overview":
        render_header(ledger)
        render_overview(problems, ledger)
        st.markdown("---")
        render_coverage_charts(problems, ledger)

    elif page == "📈 Coverage":
        render_coverage_charts(problems, ledger)
        st.markdown("---")
        render_level_progress(done, len(flat))

    elif page == "✅ My Progress":
        render_progress_controls(flat)

    elif page == "🔍 Browse":
        render_browser(problems)

    elif page == "🤖 Agent":
        render_agent_page(problems, ledger, run_log, pr_history)

    elif page == "🎯 Levels":
        render_level_progress(done, len(flat))
        st.markdown("---")
        for name, info in SKILL_CATEGORIES.items():
            lst = problems.get(info["problems_key"], [])
            with st.expander(f"{info['icon']} {name} ({len(lst)})"):
                st.write(info["description"])
                st.markdown(f"**Staff expectation:** {info['staff_expectation']}")

    elif page == "🎲 Random":
        render_recommendation(flat)


if __name__ == "__main__":
    main()
