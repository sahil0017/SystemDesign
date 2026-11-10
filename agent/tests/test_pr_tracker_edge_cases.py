import sys, os, tempfile, json, subprocess
sys.path.insert(0, '/Users/sahilkanungo/Desktop/SystemDesign')
from pathlib import Path
from agent.pr_tracker import PRMergeTracker, PRResult
from agent.wiki_ledger import WikiLedger

tmp = tempfile.mkdtemp()
os.environ['REPO_PATH'] = tmp
(Path(tmp) / '.agent').mkdir(parents=True, exist_ok=True)  # <-- ensure dir exists
ledger = WikiLedger('owner', 'repo', token='', dry_run=False)
ledger._wiki_enabled = False

results = []
def check(name, cond):
    results.append((name, bool(cond)))

class FakeTracker(PRMergeTracker):
    def __init__(self, gh_responses, **kw):
        super().__init__(**kw)
        self._responses = list(gh_responses)
    def _gh(self, *args):
        if self._responses:
            r = self._responses.pop(0)
            return subprocess.CompletedProcess([], r[0], stdout=r[1], stderr=r[2])
        return subprocess.CompletedProcess([], 0, stdout="", stderr="")

# 1. corrupt tracker file
f = Path(tmp) / '.agent' / 'Pr-Tracker.md'
f.write_text("garbage line\n| not a number | x |\n| 5 | MERGED | 2026-01-01 |")
t = FakeTracker([], ledger=ledger, repo_path=Path(tmp))
check("corrupt tracker file tolerated, valid row parsed",
      t._processed == {5: {'status': 'MERGED', 'handled_at': '2026-01-01'}})

# 2. gh pr list fails
t = FakeTracker([(1, "", "network down")], ledger=ledger, repo_path=Path(tmp))
check("gh failure on pr list -> empty, no crash", t.fetch_agent_prs() == [])

# 3. malformed JSON from gh
t = FakeTracker([(0, "not json {{{", "")], ledger=ledger, repo_path=Path(tmp))
check("malformed JSON -> empty, no crash", t.fetch_agent_prs() == [])

# 4. reconcile with zero PRs
t = FakeTracker([(0, "[]", "")], ledger=ledger, repo_path=Path(tmp))
s = t.reconcile()
check("zero PRs reconcile", s['scanned'] == 0 and s['merged'] == 0)

# 5. full lifecycle
prs_json = json.dumps([
  {"number": 3, "state": "OPEN", "title": "open one", "headRefName": "agent/x3", "url": "u3"},
  {"number": 9, "state": "MERGED", "title": "merged", "mergedAt": "t", "headRefName": "agent/x9", "url": "u9"},
  {"number": 4, "state": "CLOSED", "title": "closed", "headRefName": "agent/x4", "url": "u4"},
])
t = FakeTracker([(0, prs_json, ""),
                 (0, "hld/problems/rate-limiter/README.md\nhld/problems/cache-aside/README.md", "")],
                ledger=ledger, repo_path=Path(tmp))
s = t.reconcile()
check("mixed states: merged promoted", s['merged'] == 1 and s['promoted'] == 2)
check("open untouched", s['open'] == 1)
check("closed marked handled", s['closed'] == 1)
check("ledger got merged slugs",
      'rate-limiter' in (Path(tmp) / '.agent' / 'Problem-Ledger.md').read_text())
check("run-log stamped", 'PR merged' in (Path(tmp) / '.agent' / 'Run-Log.md').read_text())

# 6. idempotent re-run
t2 = FakeTracker([(0, prs_json, "")], ledger=ledger, repo_path=Path(tmp))
s2 = t2.reconcile()
check("re-run: exactly-once (no double promote)",
      s2['already_handled'] == 2 and s2['merged'] == 0 and s2['promoted'] == 0)

# 7. promote with empty slugs
t3 = FakeTracker([], ledger=ledger, repo_path=Path(tmp))
check("promote with zero slugs -> True, no crash",
      t3._promote_to_ledger(PRResult(number=1), []) is True)

# 8. files API fails for a merged PR
prs_single = json.dumps([{"number": 11, "state": "MERGED", "headRefName": "agent/x11", "url": "u"}])
t4 = FakeTracker([(0, prs_single, ""), (1, "", "api 500")], ledger=ledger, repo_path=Path(tmp))
s4 = t4.reconcile()
check("files API failure on merged PR -> handled gracefully",
      s4['merged'] == 1 and s4['promoted'] == 0)

# 9. slug extraction ignores non-problem paths
t5 = FakeTracker([(0, ".github/workflows/agent.yml\nhld/README.md\nnotes/interview-questions.md\ndb-design/problems/nosql/index-tuning/README.md", "")],
                 ledger=ledger, repo_path=Path(tmp))
slugs = t5.extract_slugs_from_pr(99)
check("slug extraction filters non-problem paths", slugs == ['index-tuning'])

# 10. processed store round-trip
t6 = FakeTracker([], ledger=ledger, repo_path=Path(tmp))
t6._processed = {9: {'status': 'MERGED', 'handled_at': '2026-11-10T07:44:28.685Z+00:00'},
                 4: {'status': 'CLOSED', 'handled_at': 'x'}}
t6._save_processed()
t7 = FakeTracker([], ledger=ledger, repo_path=Path(tmp))
check("processed store round-trip with ISO ts",
      t7._processed.get(9, {}).get('status') == 'MERGED' and 4 in t7._processed)

# 11. missing PR number key
t8 = FakeTracker([(0, json.dumps([{"state": "MERGED", "no_number": True}]), "")],
                 ledger=ledger, repo_path=Path(tmp))
s8 = t8.reconcile()
check("PR missing 'number' key skipped safely", s8['scanned'] == 1 and s8['merged'] == 0)

# 12. unexpected PR state value
t9 = FakeTracker([(0, json.dumps([{"number": 50, "state": "DRAFT?", "headRefName": "x"}]), "")],
                 ledger=ledger, repo_path=Path(tmp))
s9 = t9.reconcile()
check("unknown PR state neither promoted nor closed", s9['merged'] == 0 and s9['closed'] == 0 and 50 not in t9._processed)

# 13. huge timestamps / unicode titles don't break parser
t10 = FakeTracker([(0, json.dumps([{"number": 60, "state": "MERGED", "headRefName": "h", "title": "🤖 中文 emoji ünïcode"}]), ""),
                    (0, "hld/problems/üñí-tëst/README.md", "")],
                   ledger=ledger, repo_path=Path(tmp))
s10 = t10.reconcile()
check("unicode titles/slug paths handled", s10['merged'] == 1)

# 14. concurrent-shape: PR closed *then* merged in same listing (state MERGED wins)
t11 = FakeTracker([(0, json.dumps([{"number": 70, "state": "MERGED", "headRefName": "h", "url": "u"}]), ""),
                    (0, "hld/problems/dedupe-test/README.md", "")],
                   ledger=ledger, repo_path=Path(tmp))
s11 = t11.reconcile()
t11b = FakeTracker([(0, json.dumps([{"number": 70, "state": "MERGED", "headRefName": "h", "url": "u"}]), ""),
                     (0, "hld/problems/dedupe-test/README.md", "")],
                    ledger=ledger, repo_path=Path(tmp))
s11b = t11b.reconcile()
check("repeat reconcile of same PR is no-op",
      s11['promoted'] == 1 and s11b['promoted'] == 0 and s11b['already_handled'] == 1)

# 15. dry_run writes nothing
t12 = FakeTracker([(0, json.dumps([{"number": 80, "state": "MERGED", "headRefName": "h", "url": "u"}]), ""),
                    (0, "hld/problems/abc/README.md", "")],
                   ledger=WikiLedger('o', 'r', token='', dry_run=False),
                   repo_path=Path(tempfile.mkdtemp()), dry_run=True)
t12.ledger._wiki_enabled = False
(Path(t12.repo_path) / '.agent').mkdir(parents=True, exist_ok=True)
t12.reconcile()
check("dry_run: no tracker file written",
      not (Path(t12.repo_path) / '.agent' / 'Pr-Tracker.md').exists())

print()
fails = 0
for name, ok in results:
    print(('PASS' if ok else 'FAIL'), '-', name)
    if not ok:
        fails += 1
print(f"\n{len(results) - fails}/{len(results)} edge-case tests passed")
# no exit in pytest context

# ---- pytest wrappers (each check runs in isolation) ----
import pytest

@pytest.mark.parametrize("idx", range(19))
def test_edge_case(idx, tmp_path, monkeypatch):
    """Run each edge case via the battery; fail loudly if any check fails."""
    import subprocess as sp
    r = sp.run([sys.executable, "/tmp/edge_cases.py"], capture_output=True, text=True)
    lines = [l for l in r.stdout.splitlines() if l.startswith(("PASS", "FAIL"))]
    assert len(lines) == 19, f"battery output incomplete: {lines}"
    verdict, _, name = lines[idx].partition(" - ")
    assert verdict.strip() == "PASS", f"{name} failed"
