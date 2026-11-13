#!/usr/bin/env python3
"""
prose_scan.py -- count the prose patterns that research-polish removes.

Usage:
  python3 prose_scan.py FILE [FILE ...] [--lang en|zh|auto] [--max N]

FILE may be .tex, .md, .txt or .pdf (PDF needs `mutool` or `pdftotext`).
Prints a markdown report: a count table per category, then the hit sentences.
A hit is a candidate, not a verdict: each one still needs a human decision
(delete / rephrase positively / keep because it carries content).
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from collections import OrderedDict
from pathlib import Path


def alt(*parts: str) -> str:
    """Join regex alternatives, one per argument."""
    return "|".join(parts)


EN = OrderedDict(
    [
        ("negative_framing", alt(*[
            r"\bnot\b[^.;]{0,80}\bbut\b",
            r"\brather than\b",
            r", not (?:by|for|of|with|to|that|in|a|an|the|on)\b",
            r"^Nor\b",
            r"\bnot only\b",
            r"\bis not the (?:target|point|goal)\b",
        ])),
        ("defensive_phrase", alt(*[
            r"[Ii]t should be noted",
            r"[Nn]ote that",
            r"[Ii]t is (?:important|worth) (?:to note|noting)",
            r"do(?:es)? not (?:mean|imply)",
            r"is not claimed",
            r"cannot be ruled out",
            r"is an inference",
            r"[Aa]dmittedly",
            r"[Ww]e acknowledge",
            r"[Ii]t must be (?:stressed|emphasi[sz]ed)",
        ])),
        ("self_weakening", alt(*[
            r"\b(?:[Tt]his (?:thesis|work|study|paper)|[Ww]e) (?:did|does|do) not (?:evaluate|measure|quantify|test|consider|address)",
            r"remains? (?:unidentified|unclear|unknown|to be)",
            r"not yet (?:established|known)",
            r"\b(?:[Uu]nfortunately|[Rr]egrettably)\b",
            r"\blimited to\b",
            r"\bonly (?:approximately|partially|moderately)\b",
            r"\bno (?:\w+ )?(?:baseline|ablation|control) was run\b",
            r"\bunchecked\b",
        ])),
        ("initial_connective", r"^(?:" + alt(*[
            "Moreover", "Furthermore", "Therefore", "Consequently", "However",
            "Additionally", "In addition", "Thus", "Hence", "Specifically",
            "Accordingly", "Conversely", "Nevertheless", "Notably", "Importantly",
            "Meanwhile", "Indeed", "Overall", "In conclusion", "To sum up",
        ]) + r")\b"),
        ("inflated_word", r"\b(?:" + alt(*[
            r"comprehensive(?:ly)?", r"robust(?:ly)?", r"rigorous(?:ly)?", r"extreme(?:ly)?",
            r"seamless(?:ly)?", "crucial", "pivotal", "paramount", "inherently", "perpetually",
            "strictly", "catastrophic", "irreversible", r"leverag\w+", r"utili[sz]\w+",
            "counterproductive", r"exacerbat\w+", "delve", "groundbreaking", "cutting-edge",
        ]) + r")\b"),
        ("passive_template",
         r"\b[Ii]t (?:is|was|can be|could be) (?:believed|argued|found|shown|noted|observed|seen|concluded) that\b"),
        ("process_narrative", alt(*[
            r"\b[Ii]n this (?:phase|stage)\b",
            r"\b[Tt]his (?:phase|stage) (?:of (?:the )?research )?(?:yields|establishes|enforces|aims)",
            r"\b[Pp]reliminary (?:runs|analysis|experiments)\b",
            r"\bevaluated and rejected\b",
            r"\bwe first tried\b",
            r"\b[Ii]nitially,? we\b",
        ])),
    ]
)

ZH = OrderedDict(
    [
        (
            "negative_framing",
            r"不是[^。；]{0,30}而是|并非[^。；]{0,30}而是|是两回事|不在于[^。；]{0,30}而在于",
        ),
        (
            "defensive_phrase",
            r"需要强调的是|值得注意的是|这并不意味着|并不意味着|不能简单地认为|需要指出的是|应当承认|不可否认",
        ),
        (
            "self_weakening",
            r"遗憾的是|效果有限|仍明显落后|存在(?:严重)?不足|未能超过|性能下降|本文弱于|仅能|只能勉强",
        ),
        (
            "initial_connective",
            r"^(?:此外|另外|而且|因此|然而|综上所述|总之|与此同时|值得一提的是)",
        ),
        ("inflated_word", r"至关重要|极其|全面深入|显著提升|重大突破|前所未有|颠覆性"),
        ("passive_template", r"^(?:人们认为|可以认为|被认为|据认为)"),
        (
            "process_narrative",
            r"首先尝试|后来发现|我们先做了|在这一阶段|这一阶段的研究|初步实验中|最初曾",
        ),
    ]
)


def read_any(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "out.txt"
            if shutil.which("mutool"):
                cmd = ["mutool", "convert", "-F", "text", "-o", str(out), str(path)]
            elif shutil.which("pdftotext"):
                cmd = ["pdftotext", str(path), str(out)]
            else:
                sys.exit("PDF input needs mutool or pdftotext")
            subprocess.run(cmd, check=True, capture_output=True)
            return out.read_text(encoding="utf-8", errors="replace")
    t = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix.lower() == ".tex":
        t = re.sub(r"(?<!\\)%.*", "", t)  # comments
        t = re.sub(r"\\(?:cite|ref|eqref|label)\w*\{[^}]*\}", "[x]", t)
        t = re.sub(r"\$[^$]*\$", "X", t)  # inline math
        t = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?", "", t)  # commands
        t = t.replace("{", "").replace("}", "").replace("~", " ")
    return t


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"-\n(?=[a-z])", "", text)
    text = re.sub(r"\s+", " ", text)
    parts = re.split(
        r"(?<=[.!?;。！？；])\s+(?=[A-Z(\"“\u4e00-\u9fff])|(?<=[。！？；])", text
    )
    return [p.strip() for p in parts if p and p.strip()]


def detect_lang(text: str) -> str:
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    return "zh" if cjk > 0.2 * max(len(text), 1) else "en"


def scan_text(text: str, lang: str = "auto") -> dict:
    lang = detect_lang(text) if lang == "auto" else lang
    pats = EN if lang == "en" else ZH
    sents = split_sentences(text)
    out = {k: [] for k in pats}
    for s in sents:
        for k, p in pats.items():
            if re.search(p, s):
                out[k].append(s)
    if lang == "en":
        out["long_which_that"] = [
            s
            for s in sents
            if len(s.split()) > 30 and len(re.findall(r"\b(?:which|that)\b", s)) >= 2
        ]
        out["very_long"] = [s for s in sents if len(s.split()) > 45]
    else:
        out["very_long"] = [s for s in sents if len(s) > 120]
    out["_sentences"] = sents
    return out


def report(r: dict, name: str, max_n: int) -> str:
    n = len(r["_sentences"])
    lines = [f"## {name}（{n} 句）", "", "| 类别 | 命中 |", "|---|---|"]
    for k, v in r.items():
        if k != "_sentences":
            lines.append(f"| {k} | {len(v)} |")
    for k, v in r.items():
        if k == "_sentences" or not v:
            continue
        lines += ["", f"### {k}"]
        for s in v[:max_n]:
            lines.append(f"- {s[:300]}")
        if len(v) > max_n:
            lines.append(f"- ……另有 {len(v) - max_n} 句")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("files", nargs="+")
    ap.add_argument("--lang", default="auto", choices=["auto", "en", "zh"])
    ap.add_argument(
        "--max", type=int, default=40, help="max sentences listed per category"
    )
    a = ap.parse_args()
    for f in a.files:
        p = Path(f)
        print(report(scan_text(read_any(p), a.lang), p.name, a.max))
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
