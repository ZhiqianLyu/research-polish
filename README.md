# research-polish（科研润色）

A Claude Code skill for checking and rewriting academic prose: theses, papers, abstracts,
introductions, conclusions and reviewer responses. It targets two things.

1. **Defensive writing**: negative framing ("It is not X, but rather Y", "rather than"),
   sentences that only pre-empt criticism, self-weakening, process narrative, and weaknesses
   exposed for no reason. The narrative rule is that a paper is a press conference, not a
   project log.
2. **Readability in English**: sentence-initial connectives (Furthermore, Moreover…),
   template passives, stacked adjectives, sentences over 30 words with two or more
   which/that, and logic words that carry no logic.

It also keeps an honesty boundary: numbers and conclusions never change; limitations that a
supervisor, journal or rubric requires stay in, rephrased positively; and every rewrite that
drops a hedge is checked against the data so it does not overclaim.

The skill text (`SKILL.md`) is written in Chinese; the examples and scripts work on English
and Chinese text.

## Contents

| Path | What it is |
|---|---|
| `SKILL.md` | Rules, workflow and pre-submission checklist |
| `references/examples.md` | Before/after examples in seven categories (all fictional) |
| `scripts/prose_scan.py` | Counts candidate problems per category in a .pdf/.tex/.md/.txt file and lists the sentences |
| `scripts/apply_edits.py` | All-or-nothing text replacement from a JSON list, with backup and a before/after table |
| `tests/test_scripts.py` | Tests for both scripts |

## Install

```bash
git clone https://github.com/ZhiqianLyu/research-polish ~/.claude/skills/research-polish
```

Claude Code picks the skill up automatically. It triggers on requests such as
"polish my thesis", "check readability", "is this too defensive", 论文润色, 通读性, 防御性写作.

## Scripts

```bash
python3 scripts/prose_scan.py paper.pdf --max 50        # needs mutool or pdftotext for PDF
python3 scripts/apply_edits.py edits.json --dry-run
python3 scripts/apply_edits.py edits.json --backup backup/ --log REVISION_LOG.md
python3 -m pytest tests -q
```

Scan hits are candidates, not verdicts: each one still needs a decision to delete it,
rephrase it positively, or keep it because it carries content.

## License

MIT, see `LICENSE`. Part of the narrative rules is adapted from `anti-defensive-writing-zh`
by Adkid-Zephyr (MIT); see `NOTICE.md`.
