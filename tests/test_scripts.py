"""
Tests for research-polish/scripts. Written before the scripts.

Run with:  python3 -m pytest ~/.claude/skills/research-polish/tests -q
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

from apply_edits import apply_edits
from prose_scan import scan_text, split_sentences


# ---------------- prose_scan ----------------
def test_split_sentences_keeps_decimals_and_citations():
    s = split_sentences("The error was 2.17 mm [3]. It fell to 0.58. Then it rose.")
    assert len(s) == 3
    assert s[0].startswith("The error was 2.17")


def test_detects_each_english_category():
    text = (
        "Furthermore, the model is robust. "
        "The benchmark measures robustness, not resistance to real-world noise. "
        "This is not a proof but an argument. "
        "It should be noted that the data are noisy. "
        "In this phase, the model is selected. "
        "This thesis did not evaluate the long-term stability. "
        "We chose the model rather than the baseline. "
        "The sensor, which sits on the arm, reports a value that drifts, "
        "and the filter, which is fixed, uses a window that holds fifty samples "
        "drawn from runs that were recorded in labs that keep a constant temperature."
    )
    r = scan_text(text, lang="en")
    for cat in [
        "negative_framing",
        "defensive_phrase",
        "self_weakening",
        "initial_connective",
        "inflated_word",
        "process_narrative",
        "long_which_that",
    ]:
        assert r[cat], f"category {cat} found nothing"


def test_clean_english_text_has_no_hits():
    text = (
        "The catalyst raises the yield to 82%. "
        "It stays active for 40 cycles at room temperature."
    )
    r = scan_text(text, lang="en")
    assert all(len(v) == 0 for k, v in r.items() if k != "_sentences")


def test_detects_chinese_categories():
    text = (
        "值得注意的是，这并不意味着方法无效。"
        "这不是一个缺陷，而是一种权衡。"
        "遗憾的是，效果有限。"
        "我们首先尝试了残差方法，后来发现失败了。"
    )
    r = scan_text(text, lang="zh")
    assert r["defensive_phrase"]
    assert r["negative_framing"]
    assert r["self_weakening"]
    assert r["process_narrative"]


def test_cli_markdown_report(tmp_path):
    f = tmp_path / "a.txt"
    f.write_text("Moreover, the result is significant. The model works.")
    out = subprocess.run(
        [sys.executable, str(SCRIPTS / "prose_scan.py"), str(f)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert "initial_connective" in out and "| 类别 |" in out


# ---------------- apply_edits ----------------
def test_apply_edits_all_or_nothing(tmp_path):
    f = tmp_path / "x.tex"
    f.write_text("Alpha beta. Gamma delta. Gamma delta.")
    edits = [
        {"file": str(f), "old": "Alpha beta.", "new": "Alpha."},
        {"file": str(f), "old": "Gamma delta.", "new": "Gamma."},
    ]  # appears twice
    ok, msg = apply_edits(edits, dry_run=False)
    assert not ok and "count=2" in msg
    assert f.read_text() == "Alpha beta. Gamma delta. Gamma delta."  # nothing written


def test_apply_edits_writes_and_logs(tmp_path):
    f = tmp_path / "x.tex"
    f.write_text("Alpha beta. Gamma delta.")
    log = tmp_path / "log.md"
    edits = [
        {"file": str(f), "old": "Alpha beta.", "new": "Alpha.", "where": "§1"},
        {"file": str(f), "old": "Gamma delta.", "new": "", "where": "§2"},
    ]
    ok, msg = apply_edits(
        edits, dry_run=False, log_path=log, backup_dir=tmp_path / "bak"
    )
    assert ok, msg
    assert f.read_text() == "Alpha. "
    t = log.read_text()
    assert "| 1 | §1 | Alpha beta. | Alpha. |" in t and "（删去）" in t
    assert (tmp_path / "bak" / "x.tex").read_text() == "Alpha beta. Gamma delta."


def test_apply_edits_cli_json(tmp_path):
    f = tmp_path / "x.txt"
    f.write_text("one two")
    spec = tmp_path / "e.json"
    spec.write_text(json.dumps([{"file": str(f), "old": "one", "new": "1"}]))
    subprocess.run(
        [sys.executable, str(SCRIPTS / "apply_edits.py"), str(spec)],
        check=True,
        capture_output=True,
    )
    assert f.read_text() == "1 two"
