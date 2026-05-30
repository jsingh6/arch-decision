#!/usr/bin/env python3
"""
Generate DASHBOARD.md from ADR frontmatter metrics.
Run manually or via GitHub Action on every ADR merge.
"""

import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

DECISIONS_DIR = Path("example-output")   # demo repo; real projects use docs/decisions
OUTPUT_FILE   = Path("README.md")
HOURLY_RATE   = 150                      # $/hr — used for $ value estimate
# Claude Sonnet 4.6 pricing (per million tokens)
INPUT_TOKEN_COST_PER_M  = 3.00
OUTPUT_TOKEN_COST_PER_M = 15.00

APPROACH_LABELS = {
    "A": "Minimal",
    "B": "Clean",
    "C": "Pragmatic",
}

# ── Frontmatter parser ────────────────────────────────────────────────────────

def parse_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}
    fm = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip().strip('"')
            if val.lower() == "true":
                val = True
            elif val.lower() == "false":
                val = False
            elif key != "id":          # preserve id as string (e.g. "0001")
                try:
                    val = int(val)
                except ValueError:
                    pass
            fm[key] = val
    return fm

# ── Helpers ───────────────────────────────────────────────────────────────────

def fmt_seconds(s: int) -> str:
    if s < 60:
        return f"{s}s"
    return f"{s // 60}m {s % 60:02d}s"

def fmt_hours(h: float) -> str:
    if h < 1:
        return f"{int(h * 60)}m"
    return f"{h:.1f}h"

def bar(pct: float, width: int = 10) -> str:
    filled = round(pct / 100 * width)
    return "█" * filled + "░" * (width - filled)

def badge(label: str, value: str, color: str) -> str:
    label_enc  = label.replace(" ", "_").replace("-", "--")
    value_enc  = value.replace(" ", "_").replace("-", "--").replace("%", "%25")
    return f"![{label}](https://img.shields.io/badge/{label_enc}-{value_enc}-{color}?style=flat-square)"

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    adr_files = sorted(DECISIONS_DIR.glob("*.md"))
    if not adr_files:
        print("No ADR files found. Nothing to generate.")
        sys.exit(0)

    adrs = []
    for f in adr_files:
        fm = parse_frontmatter(f)
        if fm.get("status") in ("accepted", "draft"):
            fm["_file"] = f
            adrs.append(fm)

    if not adrs:
        print("No accepted/draft ADRs found.")
        sys.exit(0)

    # ── Aggregate ─────────────────────────────────────────────────────────────

    total_decisions     = len(adrs)
    total_tool_seconds  = sum(a.get("time_taken_seconds", 0) for a in adrs)
    total_human_hours   = sum(a.get("estimated_human_hours", 3) for a in adrs)
    saved_hours         = total_human_hours - (total_tool_seconds / 3600)
    saved_dollars       = saved_hours * HOURLY_RATE

    total_tokens_in     = sum(a.get("tokens_input", 0) for a in adrs)
    total_tokens_out    = sum(a.get("tokens_output", 0) for a in adrs)
    token_cost          = (total_tokens_in / 1_000_000 * INPUT_TOKEN_COST_PER_M +
                           total_tokens_out / 1_000_000 * OUTPUT_TOKEN_COST_PER_M)

    validated_count     = sum(1 for a in adrs if a.get("validated") is True)
    validation_rate     = round(validated_count / total_decisions * 100) if total_decisions else 0

    accepted_rec        = sum(1 for a in adrs
                              if a.get("approach_recommended") == a.get("approach_chosen"))
    acceptance_rate     = round(accepted_rec / total_decisions * 100) if total_decisions else 0

    avg_seconds         = total_tool_seconds // total_decisions if total_decisions else 0
    avg_files           = round(sum(a.get("files_explored", 0) for a in adrs) / total_decisions, 1)

    approach_counts     = {"A": 0, "B": 0, "C": 0}
    for a in adrs:
        key = a.get("approach_chosen", "")
        if key in approach_counts:
            approach_counts[key] += 1

    # ── Badges ────────────────────────────────────────────────────────────────

    val_color  = "brightgreen" if validation_rate >= 75 else ("yellow" if validation_rate >= 40 else "orange")
    save_color = "brightgreen" if saved_dollars >= 500 else "green"

    badges = " ".join([
        badge("decisions", str(total_decisions), "blue"),
        badge("avg time", fmt_seconds(avg_seconds), "informational"),
        badge("time saved", fmt_hours(saved_hours), save_color),
        badge("value delivered", f"${int(saved_dollars):,}", "brightgreen"),
        badge("validation rate", f"{validation_rate}%", val_color),
        badge("token cost", f"${token_cost:.2f}", "lightgrey"),
    ])

    # ── ADR table rows ────────────────────────────────────────────────────────

    rows = []
    for a in adrs:
        title       = a.get("title", "—")
        repo        = a.get("repo", "—")
        lang        = a.get("language", "—")
        approach    = a.get("approach_chosen", "—")
        approach_lbl= APPROACH_LABELS.get(approach, approach)
        rec         = a.get("approach_recommended", "—")
        match_icon  = "✅" if approach == rec else "🔄"
        t           = fmt_seconds(a.get("time_taken_seconds", 0))
        vpr         = a.get("validation_pr", "")
        validated   = a.get("validated", False)
        val_cell    = f"[✅ PR]({vpr})" if validated and vpr else ("✅" if validated else "—")
        issue       = a.get("issue", "")
        issue_cell  = f"[🔗 Issue]({issue})" if issue and issue != "none" else "—"
        file_link   = a.get("_file").name
        title_link  = f"[{title}](example-output/{file_link})"
        rows.append(
            f"| {title_link} | `{repo}` | {lang} | {approach} — {approach_lbl} {match_icon} | {t} | {issue_cell} | {val_cell} |"
        )

    adr_table = "\n".join(rows)

    # ── Approach distribution ─────────────────────────────────────────────────

    approach_rows = []
    for key, label in APPROACH_LABELS.items():
        count = approach_counts[key]
        pct   = round(count / total_decisions * 100) if total_decisions else 0
        approach_rows.append(
            f"| **{key} — {label}** | {count} | `{bar(pct)}` {pct}% |"
        )
    approach_table = "\n".join(approach_rows)

    # ── Languages ─────────────────────────────────────────────────────────────

    lang_counts: dict[str, int] = {}
    for a in adrs:
        l = a.get("language", "Unknown")
        lang_counts[l] = lang_counts.get(l, 0) + 1

    lang_rows = [
        f"| {lang} | {count} |"
        for lang, count in sorted(lang_counts.items(), key=lambda x: -x[1])
    ]
    lang_table = "\n".join(lang_rows)

    # ── Timestamp ─────────────────────────────────────────────────────────────

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # ── Render ────────────────────────────────────────────────────────────────

    dashboard = f"""\
# 📐 arch-decision — Impact Dashboard

{badges}

> Auto-generated after every ADR merge · Last updated: **{now}**

---

## Summary

| Metric | Value |
|--------|-------|
| Total decisions | **{total_decisions}** |
| Average time per run | **{fmt_seconds(avg_seconds)}** |
| Estimated human time | **{fmt_hours(total_human_hours)}** |
| Total tool time | **{fmt_seconds(total_tool_seconds)}** |
| ⏱ Time saved | **{fmt_hours(saved_hours)}** |
| 💰 Estimated value delivered | **${int(saved_dollars):,}** _(@ ${HOURLY_RATE}/hr)_ |
| 🪙 Total token cost | **${token_cost:.2f}** |
| 💵 Cost per decision | **${token_cost/total_decisions:.2f}** |
| ✅ Validation rate | **{validated_count}/{total_decisions} ({validation_rate}%)** |
| 🎯 Recommendation acceptance | **{accepted_rec}/{total_decisions} ({acceptance_rate}%)** |
| 🔍 Avg files explored | **{avg_files}** |

---

## Approach Distribution

| Approach | Count | Distribution |
|----------|-------|-------------|
{approach_table}

> **A — Minimal:** smallest change, lowest risk
> **B — Clean:** architecturally correct, highest long-term value
> **C — Pragmatic:** balanced, ships sooner without significant debt

---

## All Decisions

| Decision | Repo | Language | Approach | Time | Issue | Validated |
|----------|------|----------|----------|------|-------|-----------|
{adr_table}

_✅ = recommendation accepted · 🔄 = team chose different approach_

---

## Language Breakdown

| Language | Decisions |
|----------|-----------|
{lang_table}

---

## How to read this dashboard

- **Time saved** = `(estimated human hours × decisions) − total tool time`
- **Value delivered** = `time saved × ${HOURLY_RATE}/hr` (blended senior engineer rate)
- **Token cost** uses Claude Sonnet 4.6 pricing: $3/M input · $15/M output
- **Validation rate** = ADRs where a community PR independently chose the same approach
- **Recommendation acceptance** = runs where the team accepted the tool's recommended approach

---

_Generated by [arch-decision](.) — open-source ADR orchestrator for any codebase_
"""

    OUTPUT_FILE.write_text(dashboard, encoding="utf-8")
    print(f"✅ DASHBOARD.md written — {total_decisions} decision(s) logged")
    print(f"   Time saved: {fmt_hours(saved_hours)} · Value: ${int(saved_dollars):,} · Token cost: ${token_cost:.2f}")

if __name__ == "__main__":
    main()
