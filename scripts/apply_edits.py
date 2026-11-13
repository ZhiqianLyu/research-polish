#!/usr/bin/env python3
"""
apply_edits.py -- all-or-nothing text replacements with a before/after log.

Usage:
  python3 apply_edits.py EDITS.json [--dry-run] [--log LOG.md] [--backup DIR]

EDITS.json is a list of {"file": path, "old": text, "new": text, "where": label}.
Every "old" must occur exactly once in its file (after the earlier edits to that
file are applied). If any edit fails that check, nothing is written. On success
each file is optionally backed up first, then rewritten, and a markdown table of
every change is appended to LOG.md. An empty "new" deletes the text.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


def _cell(s: str) -> str:
    s = s.replace("\n", " ").replace("|", "\\|").strip()
    return s or "（删去）"


def apply_edits(edits, dry_run=False, log_path=None, backup_dir=None):
    texts: dict[str, str] = {}
    for i, e in enumerate(edits, 1):
        f = e["file"]
        if f not in texts:
            texts[f] = Path(f).read_text(encoding="utf-8")
        n = texts[f].count(e["old"])
        if n != 1:
            return (
                False,
                f"edit {i} ({e.get('where', f)}): count={n}: {e['old'][:80]!r}",
            )
        texts[f] = texts[f].replace(e["old"], e["new"])
    if dry_run:
        return True, f"dry run: {len(edits)} edits would apply to {len(texts)} file(s)"
    for f, t in texts.items():
        if backup_dir is not None:
            Path(backup_dir).mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, Path(backup_dir) / Path(f).name)
        Path(f).write_text(t, encoding="utf-8")
    if log_path is not None:
        rows = ["| # | 位置 | 改前 | 改后 |", "|---|---|---|---|"]
        for i, e in enumerate(edits, 1):
            where = e.get("where") or Path(e["file"]).name
            rows.append(f"| {i} | {where} | {_cell(e['old'])} | {_cell(e['new'])} |")
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write("\n".join(rows) + "\n")
    return True, f"applied {len(edits)} edits to {len(texts)} file(s)"


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("edits")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--log")
    ap.add_argument("--backup")
    a = ap.parse_args()
    edits = json.loads(Path(a.edits).read_text(encoding="utf-8"))
    ok, msg = apply_edits(edits, a.dry_run, a.log, a.backup)
    print(msg)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
