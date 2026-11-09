"""
Streamlit Dashboard for SystemDesign Repository

Shows all problems added by the agent, their categories, and how they map
to staff software engineer skills. Helps track progress and identify gaps.
"""

import os
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

import streamlit as st

# ------------------------------------------------------------------ #
#  Configuration
# ------------------------------------------------------------------ #

st.set_page_config(
    page_title="SystemDesign — Staff Engineer Roadmap",
    page_icon="🏗️",
    layout="wide",
)

REPO_ROOT = Path(os.environ.get("REPO_PATH", Path(__file__).parent.parent.parent))

# ------------------------------------------------------------------ #
#  Staff engineer skill framework
# ------------------------------------------------------------------ #

SKILL_CATEGORIES = {
    "System Design (HLD)": {
        "icon": "🌐",
        "description": "Design large-scale distributed systems used in production.",
        "staff_expectation": "A staff engineer should be able to design systems handling millions of users, "
            "make trade-off decisions between consistency and availability, and justify architecture choices.",
        "problems_key": "hld",
    },
    "Object-Oriented Design (LLD)": {
        "icon": "🧱",
        "description": "Design clean, extensible, testable object-oriented systems.",
        "staff_expectation": "A staff engineer designs systems using SOLID principles, design patterns, "
            "and can reason about concurrency, thread safety, and API design.",
        "problems_key": "lld",
    },
    "Database Design": {
        "icon": "🗄️",
        "description": "Design efficient data models for relational and NoSQL databases.",
        "staff_expectation": "A staff engineer chooses the right database for the workload, "
            "designs schemas that scale, and understands indexing, partitioning, and replication.",
        "problems_key": "db_design",
    },
    "Distributed Systems": {
        "icon": "⚡",
        "description": "Understand consensus, replication, partitioning, and distributed algorithms.",
        "staff_expectation": "A staff engineer understands Paxos/Raft, consistent hashing, "
            "saga patterns, and can debug distributed system failures.",
        "problems_key": "distributed_systems",
    },
    "API Design": {
        "icon": "🔌",
        "description": "Model RESTful and gRPC APIs for real-world services.",
        "staff_expectation": "A staff engineer designs versioned, idempotent APIs with proper error handling "
            "and can evaluate REST vs gRPC vs GraphQL trade-offs.",
        "problems_key": "api_modeling",
    },
    "Trade-offs Analysis": {
        "icon": "⚖️",
        "description": "Evaluate architectural trade-offs and make informed decisions.",
        "staff_expectation": "A staff engineer can articulate why one approach is better than another "
            "for a given context, considering cost, latency, reliability, and team velocity.",
        "problems_key": "tradeoffs",
    },
    "Java Concurrency & Advanced": {
        "icon": "☕",
        "description": "Master Java concurrency, virtual threads, and advanced patterns.",
        "staff_expectation": "A staff engineer writes lock-free code, uses virtual threads effectively, "
            "and can optimize JVM performance for high-throughput services.",
        "problems_key": "java",
    },
}

STAFF_LEVELS = {
    "L5-Senior": {
        "description": "Can solve medium-complexity problems independently.",
        "target_problems": "30-50% of problems in each category.",
        "color": "#3b82f6",
    },
    "L6-Staff": {
        "description": "Can solve hard problems and mentor others.",
        "target_problems": "70-80% of problems, including hard and advanced topics.",
        "color": "#8b5cf6",
    },
    "L7-Senior Staff": {
        "description": "Can design novel solutions and drive technical strategy.",
        "target_problems": "90%+ of problems, including creating new problem sets.",
        "color": "#f59e0b",
    },
}


# ------------------------------------------------------------------ #
#  Problem discovery
# ------------------------------------------------------------------ #

@dataclass
class Problem:
    name: str
    category: str
    difficulty: Optional[str] = None
    readme_path: Optional[str] = None


def discover_problems() -> dict:
    """Scan the repository and return problems grouped by category."""
    problems = {}

    # HLD problems
    hld_dir = REPO_ROOT / "hld" / "problems"
    if hld_dir.exists():
        problems["hld"] = []
        for folder in sorted(hld_dir.iterdir()):
            if folder.is_dir():
                readme = folder / "README.md"
                if readme.exists():
                    name = folder.name.replace("-", " ").title()
                    problems["hld"].append(Problem(name=name, category="System Design (HLD)", readme_path=str(readme)))

    # LLD problems
    lld_dir = REPO_ROOT / "lld" / "problems"
    if lld_dir.exists():
        problems["lld"] = []
        for difficulty_dir in sorted(lld_dir.iterdir()):
            if difficulty_dir.is_dir():
                difficulty = difficulty_dir.name
                for folder in sorted(difficulty_dir.iterdir()):
                    if folder.is_dir():
                        readme = folder / "README.md"
                        if readme.exists():
                            name = folder.name.replace("-", " ").title()
                            problems["lld"].append(
                                Problem(name=name, category="Object-Oriented Design (LLD)",
                                        difficulty=difficulty, readme_path=str(readme))
                            )

    # DB Design problems
    db_dir = REPO_ROOT / "db-design" / "problems"
    if db_dir.exists():
        problems["db_design"] = []
        for folder in sorted(db_dir.iterdir()):
            if folder.is_dir():
                readme = folder / "README.md"
                if readme.exists():
                    name = folder.name.replace("-", " ").title()
                    problems["db_design"].append(
                        Problem(name=name, category="Database Design", readme_path=str(readme))
                    )

    # Distributed Systems problems
    ds_dir = REPO_ROOT / "distributed-systems" / "problems"
    if ds_dir.exists():
        problems["distributed_systems"] = []
        for folder in sorted(ds_dir.iterdir()):
            if folder.is_dir():
                readme = folder / "README.md"
                if readme.exists():
                    name = folder.name.replace("-", " ").title()
                    problems["distributed_systems"].append(
                        Problem(name=name, category="Distributed Systems", readme_path=str(readme))
                    )

    # API Modeling problems
    api_dir = REPO_ROOT / "api-modeling" / "problems"
    if api_dir.exists():
        problems["api_modeling"] = []
        for folder in sorted(api_dir.iterdir()):
            if folder.is_dir():
                readme = folder / "README.md"
                if readme.exists():
                    name = folder.name.replace("-", " ").title()
                    problems["api_modeling"].append(
                        Problem(name=name, category="API Design", readme_path=str(readme))
                    )

    # Trade-offs problems
    to_dir = REPO_ROOT / "tradeoffs" / "problems"
    if to_dir.exists():
        problems["tradeoffs"] = []
        for folder in sorted(to_dir.iterdir()):
            if folder.is_dir():
                readme = folder / "README.md"
                if readme.exists():
                    name = folder.name.replace("-", " ").title()
                    problems["tradeoffs"].append(
                        Problem(name=name, category="Trade-offs Analysis", readme_path=str(readme))
                    )

    # Java problems
    java_dir = REPO_ROOT / "java" / "problems"
    if java_dir.exists():
        problems["java"] = []
        for sub_dir in sorted(java_dir.iterdir()):
            if sub_dir.is_dir():
                for folder in sorted(sub_dir.iterdir()):
                    if folder.is_dir():
                        readme = folder / "README.md"
                        if readme.exists():
                            name = folder.name.replace("-", " ").title()
                            problems["java"].append(
                                Problem(name=name, category="Java Concurrency & Advanced",
                                        difficulty=sub_dir.name, readme_path=str(readme))
                            )

    return problems


def get_agent_run_history() -> list:
    """Read the run history file to see what problems the agent has added."""
    history_file = Path(os.environ.get("RUN_HISTORY_FILE", "/tmp/agent-cache/run_history.json"))
    if history_file.exists():
        try:
            import json
            data = json.loads(history_file.read_text())
            return data.get("added_slugs", [])
        except Exception:
            return []
    return []


def get_pr_history() -> list:
    """Get PR history from GitHub via gh CLI."""
    try:
        import subprocess
        result = subprocess.run(
            ["gh", "pr", "list", "--repo", "sahil0017/SystemDesign",
             "--state", "all", "--json", "number,title,url,createdAt,state",
             "--limit", "20"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            import json
            return json.loads(result.stdout)
    except Exception:
        pass
    return []


# ------------------------------------------------------------------ #
#  Streamlit UI
# ------------------------------------------------------------------ #

def render_header():
    st.markdown("""
        # 🏗️ SystemDesign — Staff Engineer Roadmap

        An automated system that **discovers new system design problems** from trending resources
        and adds them to this repository via GitHub Actions (every 12 hours).

        Use this dashboard to **track your progress** toward becoming a **Staff Software Engineer**.
    """)


def render_stats(problems: dict):
    total = sum(len(v) for v in problems.values())
    cols = st.columns(5)
    categories = [
        ("HLD", len(problems.get("hld", [])), "🌐"),
        ("LLD", len(problems.get("lld", [])), "🧱"),
        ("DB", len(problems.get("db_design", [])), "🗄️"),
        ("DS", len(problems.get("distributed_systems", [])), "⚡"),
        ("Java", len(problems.get("java", [])), "☕"),
    ]
    for i, (label, count, icon) in enumerate(categories):
        with cols[i]:
            st.metric(label=f"{icon} {label}", value=count)
    st.metric("📊 Total Problems", total)


def render_skill_breakdown(problems: dict):
    st.markdown("## 📚 Skill Category Breakdown")

    for cat_name, cat_info in SKILL_CATEGORIES.items():
        key = cat_info["problems_key"]
        prob_list = problems.get(key, [])
        count = len(prob_list)

        with st.expander(f"{cat_info['icon']} {cat_name} ({count} problems)", expanded=False):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(cat_info["description"])
                st.markdown(f"**Staff expectation:** {cat_info['staff_expectation']}")
            with col2:
                st.metric("Problems Available", count)
                if count > 0:
                    st.progress(1.0)
                    st.success("✅ Content available")

            st.markdown("### Problem List")
            for p in prob_list:
                diff_badge = f"`{p.difficulty}` " if p.difficulty else ""
                st.markdown(f"- {diff_badge}{p.name}")


def render_staff_levels():
    st.markdown("## 🎯 Staff Engineer Levels")

    for level, info in STAFF_LEVELS.items():
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown(f"""
                    ### {level}
                    **Target:** {info['target_problems']}
                    {info['description']}
                """)


def render_learning_path(problems: dict):
    st.markdown("## 🗺️ Recommended Learning Path")

    st.markdown("""
        ### Phase 1: Foundation (Weeks 1-4)
        Start with **LLD (Easy)** problems to build object-oriented design skills.
        Then move to **HLD** basics like URL Shortener, Rate Limiter, and Web Crawler.

        ### Phase 2: Intermediate (Weeks 5-8)
        Tackle **LLD (Medium)** and **HLD** problems like Twitter, Uber, and Netflix.
        Begin **Database Design** problems to understand data modeling.

        ### Phase 3: Advanced (Weeks 9-12)
        Solve **LLD (Hard)** and complex **HLD** problems.
        Study **Distributed Systems** concepts: consensus, replication, partitioning.

        ### Phase 4: Staff Level (Weeks 13+)
        Master **Trade-offs Analysis** and **Java Concurrency**.
        Design novel solutions and contribute new problem sets to the repository.
    """)


def render_agent_status():
    st.markdown("## 🤖 Agent Status")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### How It Works")
        st.markdown("""
            1. **GitHub Actions Cron** triggers every 12 hours
            2. Agent **scrapes** 5 sources for trending problems
            3. Compares with **existing** problems using fuzzy matching
            4. **Generates** new problem READMEs with staff-level insights
            5. **Creates a PR** with `sahil0017` as reviewer
        """)

    with col2:
        st.markdown("### Sources Scraped")
        st.markdown("""
            - **AlgoMaster** — System design course
            - **HelloInterview** — Interview prep platform
            - **DesignGurus** — System design master class
            - **Educative** — Grokking system design
            - **GitHub Trending** — Popular repositories
        """)

    st.markdown("### Recent PRs")
    prs = get_pr_history()
    if prs:
        for pr in prs[:5]:
            st.markdown(f"- [{pr.get('number', '?')}]({pr.get('url', '#')}) "
                        f"**{pr.get('title', 'No title')}** "
                        f"`{pr.get('state', 'unknown')}` — {pr.get('createdAt', 'N/A')[:10]}")
    else:
        st.info("PR history not available (running locally without GitHub CLI auth).")

    # Run history
    added = get_agent_run_history()
    st.metric("Problems Added by Agent", len(added))
    if added:
        st.markdown(f"**Recently added slugs:** `{', '.join(added[:10])}`")


def render_problem_detail(readme_path: str):
    """Render the full content of a problem's README."""
    path = Path(readme_path)
    if path.exists():
        content = path.read_text()
        st.markdown(content)
    else:
        st.error(f"README not found: {readme_path}")


# ------------------------------------------------------------------ #
#  Main
# ------------------------------------------------------------------ #

def main():
    render_header()

    problems = discover_problems()
    total = sum(len(v) for v in problems.values())

    # Sidebar navigation
    st.sidebar.markdown("## Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["📊 Dashboard", "📚 Skills", "🎯 Staff Levels", "🗺️ Learning Path",
         "🤖 Agent Status", "🔍 Browse Problems"],
        index=0,
    )

    st.sidebar.markdown(f"**Total problems:** {total}")

    if page == "📊 Dashboard":
        render_stats(problems)
        st.markdown("---")
        render_learning_path(problems)
        st.markdown("---")
        render_agent_status()

    elif page == "📚 Skills":
        render_skill_breakdown(problems)

    elif page == "🎯 Staff Levels":
        render_staff_levels()
        st.markdown("---")
        render_learning_path(problems)

    elif page == "🗺️ Learning Path":
        render_learning_path(problems)
        st.markdown("---")
        render_stats(problems)

    elif page == "🤖 Agent Status":
        render_agent_status()

    elif page == "🔍 Browse Problems":
        st.markdown("## 🔍 Browse All Problems")

        # Filter by category
        categories = list(SKILL_CATEGORIES.keys())
        selected_cat = st.selectbox("Filter by category", ["All"] + categories)

        # Search
        search = st.text_input("Search problems...")

        all_problems = []
        for key, prob_list in problems.items():
            all_problems.extend(prob_list)

        # Filter
        if selected_cat != "All":
            all_problems = [p for p in all_problems if p.category == selected_cat]

        if search:
            all_problems = [p for p in all_problems if search.lower() in p.name.lower()]

        # Display
        cols = st.columns(3)
        for i, p in enumerate(all_problems):
            with cols[i % 3]:
                diff = f"`{p.difficulty}`" if p.difficulty else ""
                st.markdown(f"### {p.name} {diff}")
                st.caption(p.category)
                if st.button(f"View details", key=p.readme_path):
                    st.session_state[f"show_{p.readme_path}"] = True

                if st.session_state.get(f"show_{p.readme_path}"):
                    st.markdown("---")
                    render_problem_detail(p.readme_path)
                    if st.button("Close", key=f"close_{p.readme_path}"):
                        st.session_state[f"show_{p.readme_path}"] = False

        st.markdown(f"**{len(all_problems)} problems found**")


if __name__ == "__main__":
    main()
