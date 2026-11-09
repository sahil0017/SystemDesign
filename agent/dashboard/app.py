"""
Streamlit Dashboard for SystemDesign Repository — v3

Green + black themed, mobile-first, dynamic and resilient dashboard for
tracking system design problems, wikis, notes, the automation agent, and
your staff-engineer progress.

Resilience:
- Cached loaders (st.cache_data with TTL) so the UI stays responsive
- Every loader returns empty structures instead of raising
- Missing dirs / corrupt files / absent git binary are all tolerated
- All insights computed defensively with graceful empty states
"""

import json
import os
import random
import subprocess
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st

# ------------------------------------------------------------------ #
#  Page config + THEME (green on black, mobile friendly)
# ------------------------------------------------------------------ #

st.set_page_config(
    page_title="SystemDesign — Staff Engineer Roadmap",
    page_icon="🌿",
    layout="centered",  # centered reads better on phones than ultra-wide
    initial_sidebar_state="collapsed",
)

ACCENT = "#22c55e"      # green-500
ACCENT_DARK = "#16a34a"
BG = "#0b0f0c"
SURFACE = "#111a13"
TEXT = "#e6f4ea"
MUTED = "#8fae9b"

st.markdown(f"""
<style>
/* ---------- Green + Black theme ---------- */
html, body, [data-testid="stAppViewContainer"] {{
    background: {BG};
    color: {TEXT};
}}
section.main > div {{ background: {BG}; }}
[data-testid="stHeader"] {{ background: rgba(11,15,12,.85); }}

h1, h2, h3, h4 {{ color: {ACCENT}; font-weight: 700; letter-spacing: -.02em; }}
a {{ color: {ACCENT}; }}

/* Metrics as dark cards */
[data-testid="stMetric"] {{
    background: {SURFACE};
    border: 1px solid #1d2b20;
    border-radius: 14px;
    padding: 12px 14px;
}}
[data-testid="stMetricLabel"] p {{ color: {MUTED}; font-size: .78rem; }}
[data-testid="stMetricValue"] {{ color: {ACCENT}; font-weight: 700; }}
[data-testid="stMetricDelta"] svg {{ fill: {ACCENT}; }}

/* Expanders & inputs */
[data-testid="stExpander"] {{
    background: {SURFACE};
    border: 1px solid #1d2b20;
    border-radius: 12px;
    border-color: #1d2b20;
}}
details summary {{ color: {TEXT}; }}
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] > div:first-child,
[data-testid="stNumberInput"] > div > input {{
    background: {SURFACE} !important; color: {TEXT} !important;
    border: 1px solid #1d2b20 !important; border-radius: 10px;
}}
[data-baseliner="radio"] span, div[role="radiogroup"] label {{ color: {TEXT}; }}
div[role="radiogroup"] label:hover p {{ color: {ACCENT}; }}

/* Buttons */
.stButton > button, [data-testid="stDownloadButton"] > button {{
    background: {ACCENT}; color: #04140a; font-weight: 700;
    border: none; border-radius: 10px;
}}
.stButton > button:hover {{ background: {ACCENT_DARK}; color: #fff; }}

/* Dataframes */
[data-testid="stDataFrame"] {{ border-radius: 12px; }}

/* Progress bars green */
[data-testid="stProgress"] > div > div {{ background-color: {ACCENT} !important; }}

/* ---------- Mobile-first layout ---------- */
.block-container {{ padding: 1rem .8rem 4rem; }}
@media (max-width: 720px) {{
    .block-container {{ padding: .8rem .6rem 5rem; }}
    h1 {{ font-size: 1.4rem !important; }}
    h2 {{ font-size: 1.05rem !important; }}
    /* stack metric columns tight */
    [data-testid="stMetricValue"] {{ font-size: 1.3rem; }}
    /* full-width buttons on phones */
    .stButton > button {{ width: 100%; }}
}}
/* pill badges */
.badge {{
    display:inline-block; padding:2px 10px; border-radius:999px;
    font-size:.72rem; font-weight:600;
    background:#13251a; color:{ACCENT}; border:1px solid #1d3a26;
}}
.hero {{
    background: linear-gradient(135deg, {SURFACE} 0%, #0e1f14 100%);
    border: 1px solid #1d3a26; border-radius: 16px;
    padding: 18px; margin-bottom: 8px;
}}
.hero h1 {{ margin: 0 0 6px; }}
</style>
""", unsafe_allow_html=True)

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
    "L5-Senior": {"target": 0.35, "description": "Can solve medium-complexity problems independently."},
    "L6-Staff": {"target": 0.75, "description": "Can solve hard problems and mentor others."},
    "L7-Senior Staff": {"target": 0.9, "description": "Can design novel solutions and drive technical strategy."},
}

NAV_PAGES = [
    "🏠 Home", "📈 Insights", "✅ Progress", "🔍 Browse",
    "🤖 Agent", "🎯 Levels", "🎲 Pick One",
]


def badge(text: str) -> str:
    return f'<span class="badge">{text}</span>'


# ------------------------------------------------------------------ #
#  Data model
# ------------------------------------------------------------------ #

@dataclass
class Problem:
    name: str
    category: str
    category_key: str
    difficulty: Optional[str] = None
    readme_path: Optional[str] = None
    slug: str = ""
    added_by_agent: bool = False
    added_on: str = ""

    def as_dict(self) -> dict:
        """Plain-dict form (picklable for st.cache_data)."""
        return {
            "name": self.name,
            "category": self.category,
            "category_key": self.category_key,
            "difficulty": self.difficulty,
            "readme_path": self.readme_path,
            "slug": self.slug,
            "added_by_agent": self.added_by_agent,
            "added_on": self.added_on,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Problem":
        return cls(**{k: d.get(k, v.default) if hasattr(v, "default") else d.get(k)
                      for k, v in cls.__dataclass_fields__.items()})


def _problems_to_dicts(problems: dict) -> dict:
    return {k: [p.as_dict() for p in v] for k, v in problems.items()}


def _dicts_to_problems(dicts: dict) -> dict:
    return {k: [Problem.from_dict(d) for d in v] for k, v in dicts.items()}


# ------------------------------------------------------------------ #
#  Resilient loaders (all cached, all failure-tolerant)
# ------------------------------------------------------------------ #

def _pretty(name: str) -> str:
    return name.replace("-", " ").title()


@st.cache_data(ttl=120, show_spinner="Scanning repository…")
def _discover_problems_impl(repo_root_str: str) -> dict:
    """Scan the repository; returns plain-dict problems grouped by category key. Never raises."""
    root = Path(repo_root_str)
    problems: dict = {}

    def _add(key: str, path: Path, display: str, difficulty: Optional[str] = None):
        readme = path / "README.md"
        if readme.exists():
            try:
                problems.setdefault(key, []).append(Problem(
                    name=_pretty(path.name), category=display, category_key=key,
                    difficulty=difficulty, readme_path=str(readme), slug=path.name,
                ))
            except OSError:
                pass

    for sub, disp_diff in (("problems", None), ("case-studies", "case-study")):
        d = root / "hld" / sub
        if d.is_dir():
            for f in sorted(d.iterdir()):
                if f.is_dir():
                    _add("hld", f, "System Design (HLD)", disp_diff)

    lld_dir = root / "lld" / "problems"
    if lld_dir.is_dir():
        for difficulty_dir in sorted(lld_dir.iterdir()):
            if difficulty_dir.is_dir():
                for f in sorted(difficulty_dir.iterdir()):
                    if f.is_dir():
                        _add("lld", f, "Object-Oriented Design (LLD)", difficulty_dir.name)

    db_dir = root / "db-design" / "problems"
    if db_dir.is_dir():
        for cat_dir in sorted(db_dir.iterdir()):
            if cat_dir.is_dir():
                for f in sorted(cat_dir.iterdir()):
                    if f.is_dir():
                        _add("db_design", f, "Database Design", cat_dir.name)

    ds_dir = root / "distributed-systems" / "problems"
    if ds_dir.is_dir():
        for cat_dir in sorted(ds_dir.iterdir()):
            if cat_dir.is_dir():
                for f in sorted(cat_dir.iterdir()):
                    if f.is_dir():
                        _add("distributed_systems", f, "Distributed Systems", cat_dir.name)

    api_dir = root / "api-modeling" / "problems"
    if api_dir.is_dir():
        for f in sorted(api_dir.rglob("README.md")):
            if f.parent.name != "problems":
                _add("api_modeling", f.parent, "API Design", f.parent.parent.name)

    to_dir = root / "tradeoffs"
    if to_dir.is_dir():
        for f in sorted(to_dir.iterdir()):
            if f.is_dir() and (f / "README.md").exists():
                _add("tradeoffs", f, "Trade-offs Analysis")

    java_dir = root / "java" / "problems"
    if java_dir.is_dir():
        for f in sorted(java_dir.rglob("README.md")):
            rel = f.parent.relative_to(java_dir)
            difficulty = str(rel.parent) if rel.parent != Path(".") else None
            _add("java", f.parent, "Java Concurrency & Advanced", difficulty or None)

    return _problems_to_dicts(problems)


@st.cache_data(ttl=120, show_spinner="Scanning repository…")
def discover_problems_raw(repo_root_str: str) -> dict:
    """Cached, picklable problem discovery (plain dicts, not dataclasses)."""
    return _discover_problems_impl(repo_root_str)


def discover_problems(repo_root_str: str) -> dict:
    """Public API: problems as Problem objects, rebuilt cheaply from cached dicts."""
    return _dicts_to_problems(discover_problems_raw(repo_root_str))


@st.cache_data(ttl=120, show_spinner="Inventorying wiki content…")
def discover_wiki_content(repo_root_str: str) -> dict:
    """Inventory notes / books / blogs / interview material. Never raises."""
    root = Path(repo_root_str)
    content = {"notes": [], "books": [], "blogs": [], "misc_md": 0}

    def _count_readmes(d: Path, bucket: str, skip_self: bool = False):
        try:
            for f in sorted(d.rglob("README.md")):
                if skip_self and f.parent == d:
                    continue
                content[bucket].append(_pretty(f.parent.name))
        except OSError:
            pass

    for bucket, dirname in (("notes", "notes"), ("books", "recommended-books"), ("blogs", "blogs-articles")):
        d = root / dirname
        if d.is_dir():
            _count_readmes(d, bucket)

    # misc top-level md files worth counting
    for extra in ("notes/interview-questions.md", "notes/revision-checklist.md", "notes/trade-offs.md"):
        if (root / extra).exists():
            content["misc_md"] += 1

    # rough word count across all collected readmes (cheap heuristic of "study material size")
    words = 0
    for dirname in ("hld", "lld", "db-design", "distributed-systems", "api-modeling",
                    "tradeoffs", "java", "notes", "recommended-books", "blogs-articles"):
        d = root / dirname
        if not d.is_dir():
            continue
        try:
            for f in list(d.rglob("README.md"))[:400]:
                try:
                    words += len(f.read_text(errors="ignore").split())
                except OSError:
                    pass
        except OSError:
            pass
    content["words"] = words
    return content


@st.cache_data(ttl=60, show_spinner="Reading ledger…")
def load_ledger(repo_root_str: str) -> pd.DataFrame:
    """Read the in-repo agent ledger (.agent/Problem-Ledger.md). Tolerant of missing/malformed data."""
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
                        "slug": parts[0], "name": parts[1], "category": parts[2],
                        "source": parts[3], "added": parts[4],
                    })
        except OSError:
            pass

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


@st.cache_data(ttl=300, show_spinner=True)
def repo_git_stats(repo_root_str: str) -> dict:
    """Git-derived stats; all optional, returns {} on failure."""
    out = {}
    try:
        def _git(*args):
            r = subprocess.run(["git", "-C", repo_root_str, *args],
                               capture_output=True, text=True, timeout=20)
            return r.stdout.strip() if r.returncode == 0 else ""
        out["commits"] = _git("rev-list", "--count", "HEAD")
        out["last_commit"] = (_git("log", "-1", "--format=%cs") or "")[:10]
        out["branch"] = _git("rev-parse", "--abbrev-ref", "HEAD")
    except (OSError, subprocess.TimeoutExpired):
        pass
    return out


# ------------------------------------------------------------------ #
#  Derived insights (dynamic, defensive)
# ------------------------------------------------------------------ #

def compute_insights(problems: dict, ledger: pd.DataFrame, run_log: list, content: dict, git: dict) -> dict:
    flat = [p for lst in problems.values() for p in lst]
    ledger_slugs = set(ledger["slug"]) if not ledger.empty else set()

    added_by_agent = sum(1 for p in flat if p.slug in ledger_slugs)
    sources = Counter(ledger["source"].fillna("unknown")) if not ledger.empty else Counter()
    cats = Counter(p.category for p in flat)
    diffs = Counter(p.difficulty for p in flat if p.difficulty)

    # growth over time from ledger dates
    timeline = []
    if not ledger.empty:
        dates = ledger["added"].dropna().astype(str).str.slice(0, 10)
        parsed = dates[dates.str.match(r"^\d{4}-\d{2}-\d{2}$")]
        if not parsed.empty:
            timeline = parsed.value_counts().sort_index().rename_axis("date").reset_index(name="added")
            timeline.columns = ["date", "added"]

    runs = len(run_log)
    problems_last_run = len(run_log[-1]["problems"]) if run_log else 0
    newest = sorted(flat, key=lambda p: (p.slug in ledger_slugs, p.name), reverse=True)[:5]

    return {
        "total": len(flat),
        "by_category": cats,
        "by_difficulty": diffs,
        "agent_added": added_by_agent,
        "sources": dict(sources),
        "timeline": timeline,
        "runs": runs,
        "problems_last_run": problems_last_run,
        "last_run": run_log[-1]["when"] if run_log else None,
        "wiki": content,
        "git": git,
        "newest": newest,
        "coverage_pct": min(1.0, len(cats) / len(SKILL_CATEGORIES)) if SKILL_CATEGORIES else 0,
    }


# ------------------------------------------------------------------ #
#  Progress tracking
# ------------------------------------------------------------------ #

def progress_state() -> dict:
    if "progress" not in st.session_state:
        st.session_state.progress = {}
    return st.session_state.progress


def key_of(p: Problem) -> str:
    return p.slug + "|" + (p.category_key or "")


# ------------------------------------------------------------------ #
#  Reusable visual blocks
# ------------------------------------------------------------------ #

def mini_stat_row(items: list, cols_per_row: int = 2):
    """Mobile-friendly stat grid: wraps across rows instead of one squeezed row."""
    for i in range(0, len(items), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, (label, value) in enumerate(items[i:i + cols_per_row]):
            with cols[j]:
                st.metric(label, value)


def donut(counts: Counter, title: str, height: int = 280):
    if not counts:
        st.info(f"No {title.lower()} data yet.")
        return
    df = pd.DataFrame({"key": list(counts.keys()), "n": list(counts.values())})
    st.bar_chart(df.set_index("key"), height=height, color=ACCENT)


# ------------------------------------------------------------------ #
#  Pages
# ------------------------------------------------------------------ #

def render_home(ins: dict, ledger: pd.DataFrame):
    last_run = ins["last_run"] or (ledger["added"].dropna().max() if not ledger.empty else "")
    st.markdown(f"""
    <div class="hero">
        <h1>🌿 SystemDesign</h1>
        <p style="color:{MUTED};margin:0">Your staff-engineer roadmap — {ins['total']} problems,
        {ins['wiki'].get('words', 0):,} words of study material, and an agent that adds new
        problems automatically.</p>
        <div style="margin-top:8px">
            {badge(f"📦 {ins['total']} problems")}
            {badge(f"🤖 {ins['agent_added']} by agent")}
            {badge(f"📚 {len(ins['wiki'].get('books', []))} books")}
            {badge(f"📝 {len(ins['wiki'].get('notes', []))} notes")}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if last_run:
        st.caption(f"🔄 Last agent activity: `{last_run}`")

    mini_stat_row([
        ("🌐 HLD", len(ins["by_category"].get("System Design (HLD)", []))),
        ("🧱 LLD", len(ins["by_category"].get("Object-Oriented Design (LLD)", []))),
        ("🗄️ DB Design", len(ins["by_category"].get("Database Design", []))),
        ("⚡ Distributed", len(ins["by_category"].get("Distributed Systems", []))),
        ("🔌 API", len(ins["by_category"].get("API Design", []))),
        ("⚖️ Trade-offs", len(ins["by_category"].get("Trade-offs Analysis", []))),
    ])

    if ins["agent_added"]:
        st.success(f"🤖 Agent ledger active — **{ins['agent_added']}** problems added automatically "
                   f"across **{ins['runs']}** logged runs.")
    else:
        st.info("🤖 No agent ledger yet — the next scheduled run will populate `.agent/Problem-Ledger.md`.")

    st.markdown("### 🔥 Recently touched by the agent")
    if ins["newest"]:
        for p in ins["newest"][:5]:
            tag = " ✨ agent-added" if p.slug in (set(ledger['slug']) if not ledger.empty else set()) else ""
            diff = f" · `{p.difficulty}`" if p.difficulty else ""
            st.markdown(f"- **{p.name}**{diff} — {p.category}{tag}")
    else:
        st.caption("No problems discovered in this checkout.")

    st.markdown("### 📚 Study library")
    w = ins["wiki"]
    mini_stat_row([
        ("📖 Books curated", len(w.get("books", []))),
        ("📝 Notes files", len(w.get("notes", [])) + w.get("misc_md", 0)),
        ("📰 Blog digests", len(w.get("blogs", []))),
        ("✍️ Total words", f"{w.get('words', 0):,}"),
    ])


def render_insights(problems: dict, ins: dict, ledger: pd.DataFrame):
    st.markdown("## 📈 Insights")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Problems per category")
        donut(ins["by_category"], "Categories")
    with c2:
        st.markdown("#### Difficulty mix")
        donut(ins["by_difficulty"], "Difficulty")

    if not ins["timeline"].empty:
        st.markdown("#### ➕ Agent additions over time")
        tl = ins["timeline"].copy()
        tl["date"] = pd.to_datetime(tl["date"])
        tl = tl.set_index("date")
        st.bar_chart(tl, height=240, color=ACCENT)
        first, last = tl.index.min(), tl.index.max()
        total_added = int(tl["added"].sum())
        span_days = max(1, (last - first).days + 1)
        st.caption(f"**{total_added}** problems added across **{span_days}** days "
                   f"(≈ {total_added / span_days:.1f}/day), {first:%b %d} → {last:%b %d}.")
    elif not ledger.empty:
        st.caption("Ledger has entries but no parseable dates yet.")
    else:
        st.info("Agent hasn't run yet — a timeline of additions will appear here.")

    st.markdown("#### 🤖 Agent supply chain")
    if ins["sources"]:
        df = pd.DataFrame({"Source": list(ins["sources"].keys()),
                           "Problems": list(ins["sources"].values())})
        st.dataframe(df, use_container_width=True, hide_index=True)
        total_src = sum(ins["sources"].values())
        top = max(ins["sources"].items(), key=lambda kv: kv[1])
        st.caption(f"Top source: **{top[0]}** contributes **{top[1]/max(total_src,1):.0%}** of tracked problems.")
    else:
        st.caption("No source data yet.")

    st.markdown("#### 🧮 Repository pulse")
    git = ins["git"]
    mini_stat_row([
        ("commits", git.get("commits") or "—"),
        ("last commit", git.get("last_commit") or "—"),
        ("agent runs", str(ins["runs"])),
        ("added last run", str(ins["problems_last_run"])),
        ("modules covered", f"{len(ins['by_category'])}/7"),
        ("library words", f"{ins['wiki'].get('words', 0):,}"),
    ])


def render_progress(flat: list, by_key: dict):
    st.markdown("## ✅ My Progress")
    st.caption("Tick problems you've solved. Persisted during your session; export anytime.")
    prog = progress_state()
    done = sum(1 for v in prog.values() if v)
    total = len(flat)
    pct = done / total if total else 0.0

    mini_stat_row([("Solved", f"{done}/{total}"), ("Completion", f"{pct:.0%}")])
    st.progress(min(pct, 1.0))

    # per-category mini progress
    with st.expander("📊 Per-category breakdown"):
        cat_rows = []
        for cat in SKILL_CATEGORIES:
            items = [p for p in flat if p.category == cat]
            d = sum(1 for p in items if prog.get(key_of(p)))
            cat_rows.append({"Category": f"{SKILL_CATEGORIES[cat]['icon']} {cat}",
                             "Solved": f"{d}/{len(items)}",
                             "%": f"{d/max(len(items),1):.0%}"})
        st.dataframe(pd.DataFrame(cat_rows), use_container_width=True, hide_index=True)

    csv = pd.DataFrame([
        {"problem": by_key[k].name if k in by_key else k,
         "category": by_key[k].category if k in by_key else "", "solved": True}
        for k, v in prog.items() if v
    ])
    if not csv.empty:
        st.download_button("⬇️ Export my progress (CSV)", csv.to_csv(index=False),
                           "my-progress.csv", "text/csv")

    st.markdown("### Next up")
    unsolved = [p for p in flat if not prog.get(key_of(p))]
    if not unsolved:
        st.balloons()
        st.success("🎉 Everything solved. You're a legend.")
        return
    show_n = st.slider("Show next N unsolved", 10, min(60, len(unsolved)), 15,
                       label_visibility="collapsed")
    for p in unsolved[:show_n]:
        label = f"{p.name}" + (f" · `{p.difficulty}`" if p.difficulty else "")
        prog[key_of(p)] = st.checkbox(label, key=f"cb_{key_of(p)}")


def render_browser(problems: dict):
    st.markdown("## 🔍 Browse Problems")
    flat = [p for lst in problems.values() for p in lst]

    q = st.text_input("🔎 Search", placeholder="e.g. cache, uber, threads", label_visibility="collapsed")
    c1, c2 = st.columns(2)
    with c1:
        cats = ["All"] + list(SKILL_CATEGORIES.keys())
        cat = st.selectbox("Category", cats, label_visibility="collapsed")
    with c2:
        difficulties = sorted({p.difficulty for p in flat if p.difficulty})
        diff = st.selectbox("Difficulty", ["All"] + difficulties, label_visibility="collapsed")

    rows = flat
    if cat != "All":
        rows = [p for p in rows if p.category == cat]
    if diff != "All":
        rows = [p for p in rows if p.difficulty == diff]
    if q:
        ql = q.lower()
        rows = [p for p in rows if ql in p.name.lower()]

    st.caption(f"{len(rows)} problems")
    per_page = 20
    pages = max(1, (len(rows) + per_page - 1) // per_page)
    nav1, nav2, nav3 = st.columns([1, 2, 1])
    with nav2:
        page = st.number_input("Page", 1, pages, 1, label_visibility="collapsed")
    chunk = rows[(page - 1) * per_page: page * per_page]

    for p in chunk:
        diff = f" · `{p.difficulty}`" if p.difficulty else ""
        with st.expander(f"**{p.name}**{diff}"):
            st.caption(p.category)
            try:
                text = Path(p.readme_path).read_text(errors="ignore")
                st.markdown(text[:4000] + ("\n\n… *(truncated)*" if len(text) > 4000 else ""))
            except OSError:
                st.error("README unreadable.")


def render_agent_page(problems: dict, ledger: pd.DataFrame, run_log: list, pr_history: list):
    st.markdown("## 🤖 Agent Status")
    mini_stat_row([
        ("Ledger entries", len(ledger)),
        ("Runs logged", len(run_log)),
        ("Last run", (run_log[-1]["when"][:16] if run_log else "never")),
        ("Added last run", str(len(run_log[-1]["problems"]) if run_log else 0)),
    ])

    if run_log:
        st.markdown("### Recent runs")
        df = pd.DataFrame([
            {"When": r["when"], "PR": r["pr"] or "—", "Problems": len(r["problems"])}
            for r in reversed(run_log[-10:])
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)

    if not ledger.empty:
        st.markdown("### Ledger")
        repo_slugs = {p.slug for lst in problems.values() for p in lst}
        show = ledger.copy()
        show["status"] = show["slug"].map(lambda s: "✅ merged" if s in repo_slugs else "⏳ pending")
        st.dataframe(show, use_container_width=True, hide_index=True, height=320)

    st.markdown("### Recent pull requests")
    if pr_history:
        for pr in pr_history[:5]:
            st.markdown(f"- [#{pr.get('number', '?')}]({pr.get('url', '#')}) "
                        f"**{pr.get('title', '')}** `{pr.get('state', '')}` — "
                        f"{(pr.get('createdAt') or '')[:10]}")
    else:
        st.caption("PR history unavailable (needs `gh` CLI authenticated locally).")


def render_levels(done: int, total: int, problems: dict):
    st.markdown("## 🎯 Level Progress")
    pct = done / total if total else 0.0
    for level, info in STAFF_LEVELS.items():
        target = info["target"]
        met = pct >= target
        bar = min(pct / target, 1.0) if target else 0
        st.markdown(f"**{level}** — target {target:.0%} of catalogue")
        st.progress(bar)
        remaining = max(0, int(target * total - done))
        st.caption(info["description"] + ("  \n✅ **Met!**" if met else f"  \nSolve {remaining} more"))

    st.markdown("---")
    st.markdown("## 🧭 Skill map")
    for name, info in SKILL_CATEGORIES.items():
        lst = problems.get(info["problems_key"], [])
        with st.expander(f"{info['icon']} {name} ({len(lst)})"):
            st.write(info["description"])
            st.markdown(f"**Staff expectation:** {info['staff_expectation']}")


def render_recommendation(flat: list):
    st.markdown("## 🎲 Pick One For Me")
    if not flat:
        st.info("No problems available.")
        return
    prog = progress_state()
    filter_cat = st.selectbox("Scope", ["Any category"] + list(SKILL_CATEGORIES.keys()))
    if st.button("🎲 Surprise me", use_container_width=True):
        pool = [p for p in flat if not prog.get(key_of(p))]
        if filter_cat != "Any category":
            pool = [p for p in pool if p.category == filter_cat] or flat
        pool = pool or flat
        p = random.choice(pool)
        st.session_state["picked"] = p
    p = st.session_state.get("picked")
    if p:
        diff = f" · `{p.difficulty}`" if p.difficulty else ""
        st.success(f"**{p.name}**{diff} — {p.category}")
        try:
            text = Path(p.readme_path).read_text(errors="ignore")
            st.markdown(text[:3000] + ("\n\n… *(truncated)*" if len(text) > 3000 else ""))
        except OSError:
            st.caption("README unavailable.")


# ------------------------------------------------------------------ #
#  Main
# ------------------------------------------------------------------ #

def main():
    problems = discover_problems(str(REPO_ROOT))
    ledger = load_ledger(str(REPO_ROOT))
    run_log = load_run_log(str(REPO_ROOT))
    content = discover_wiki_content(str(REPO_ROOT))
    git = repo_git_stats(str(REPO_ROOT))
    pr_history = load_pr_history("sahil0017/SystemDesign")

    ins = compute_insights(problems, ledger, run_log, content, git)
    flat = [p for lst in problems.values() for p in lst]
    by_key = {key_of(p): p for p in flat}
    prog = progress_state()
    done = sum(1 for v in prog.values() if v)

    # ---- Navigation: compact segmented pills in the sidebar, mobile-first ----
    with st.sidebar:
        st.markdown(f"# 🌿 SystemDesign")
        st.caption(f"{ins['total']} problems · {done} solved · {ins['agent_added']} agent-added")
        st.divider()
        page = st.radio("Navigate", NAV_PAGES, index=0, label_visibility="collapsed")
        st.divider()
        if st.button("🔄 Refresh data", use_container_width=True):
            discover_problems_raw.clear()
            load_ledger.clear()
            load_run_log.clear()
            load_pr_history.clear()
            discover_wiki_content.clear()
            repo_git_stats.clear()
            st.toast("Cache cleared — reloading…")
            st.rerun()
        st.caption(f"Repo: `{REPO_ROOT.name}`")

    if page == "🏠 Home":
        render_home(ins, ledger)
    elif page == "📈 Insights":
        render_insights(problems, ins, ledger)
    elif page == "✅ Progress":
        render_progress(flat, by_key)
    elif page == "🔍 Browse":
        render_browser(problems)
    elif page == "🤖 Agent":
        render_agent_page(problems, ledger, run_log, pr_history)
    elif page == "🎯 Levels":
        render_levels(done, len(flat), problems)
    elif page == "🎲 Pick One":
        render_recommendation(flat)


if __name__ == "__main__":
    main()
