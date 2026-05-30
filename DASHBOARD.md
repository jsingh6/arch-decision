<div align="center">

# 📐 arch-decision

### Stop losing architectural decisions to Slack threads and forgotten docs.

**arch-decision** is an open-source AI orchestrator that runs inside any codebase, explores it deeply, and produces a formal Architecture Decision Record — in minutes, not days.

[View Example ADR](example-output/0002-usetable-filter-reverse-mapping-refine.md) · [How it works](#how-it-works) · [Install](#install)

</div>

---

## The problem

Every team faces the same gap: a decision gets made, the code gets written, but nobody wrote down *why*. Six months later a new engineer changes it, and the same debate happens all over again.

Architecture Decision Records (ADRs) solve this — but writing them is friction. It takes a senior engineer 2–4 hours to research the codebase, draft approaches, build a trade-off table, and write it up clearly. So it almost never happens.

**arch-decision removes that friction entirely.**

---

## What it does

Give it a GitHub issue, a Jira ticket, or a plain description. It handles the rest:

```
/arch-decision https://github.com/owner/repo/issues/42
```

```
Phase 0   Detects repo language, framework, existing ADRs
Phase 1   Understands the problem from the issue or description
Phase 2   Launches 3 parallel agents — prior art, impact map, constraints
Phase 3   Asks clarifying questions before designing anything
Phase 4   Generates 3 approaches simultaneously (Minimal / Clean / Pragmatic)
Phase 5   Synthesizes a trade-off table and recommends the best path
Phase 6   Waits for your approval — nothing is written without sign-off
Phase 7   Writes a formal ADR to docs/decisions/ with full context
Phase 8   Links the ADR back to the original issue
```

**Works on any language. Any framework. Any team.**

---

## Why it's different

| | GitHub Copilot / Cursor | arch-decision |
|--|--|--|
| What it operates on | Files and lines | The full decision lifecycle |
| Knows *why* you're building | No | Yes — starts from the problem |
| Produces documentation | No | Yes — formal ADR, committed |
| Human approval gate | No | Yes — can't proceed without sign-off |
| Resumable across sessions | No | Yes — checkpoints after every phase |
| Validated by community PRs | — | ✅ independently confirmed |

---

## Real example

Ran against [`refinedev/refine`](https://github.com/refinedev/refine) on issue [#7338](https://github.com/refinedev/refine/issues/7338) — a feature request for reverse filter mapping in `useTable`.

The tool explored the codebase cold, found prior art in `crudFiltersToColumnFilters`, identified the framework-agnostic constraint in `packages/core`, and recommended an `onParse` callback scoped to the antd wrapper.

A community contributor independently opened [PR #7385](https://github.com/refinedev/refine/pull/7385) with the same callback name, same scope, same placement — without seeing this output.

→ [Read the full ADR](example-output/0002-usetable-filter-reverse-mapping-refine.md)

---

## How it works

arch-decision is a [Claude Code](https://claude.ai/code) plugin. It uses a multi-agent architecture:

- **Orchestrator** (`skills/arch-decision/SKILL.md`) — coordinates all phases, maintains context bus, enforces the human approval gate
- **Explorer agents** (`agents/arch-explorer/`) — 3 run in parallel during Phase 2, each focused on a different angle of the codebase
- **Synthesizer agent** (`agents/arch-synthesizer/`) — produces the trade-off table and recommendation from all three approaches

The human approval gate in Phase 6 means the agent **cannot write the ADR without your explicit sign-off**. It is designed to accelerate human judgment, not replace it.

---

## Install

```bash
claude plugin install arch-decision
```

Or clone and install locally:

```bash
git clone https://github.com/jsingh6/arch-decision
claude plugin install ./arch-decision
```

Optional — add `.claude/arch-decision-config.json` to your repo for team-specific settings (Slack webhook, decisions directory, issue tracker):

```json
{
  "team": "my-team",
  "decisions_dir": "docs/decisions",
  "notification": {
    "slack_webhook_url": "https://hooks.slack.com/...",
    "channel": "#architecture"
  }
}
```

---

## Usage

```bash
# From a GitHub issue URL
/arch-decision https://github.com/owner/repo/issues/42

# From a free-text description
/arch-decision add rate limiting to the public API

# Structure a vague problem first
/arch-intake our checkout flow is too slow
```

---

## Impact Dashboard

![decisions](https://img.shields.io/badge/decisions-2-blue?style=flat-square) ![avg time](https://img.shields.io/badge/avg_time-4m_59s-informational?style=flat-square) ![time saved](https://img.shields.io/badge/time_saved-5.8h-brightgreen?style=flat-square) ![validation rate](https://img.shields.io/badge/validation_rate-50%25-yellow?style=flat-square) ![recommendation acceptance](https://img.shields.io/badge/recommendation_acceptance-100%25-brightgreen?style=flat-square)

> Auto-generated after every ADR merge · Last updated: **2026-05-30 21:47 UTC**

---

## Summary

| Metric | Value |
|--------|-------|
| Total decisions | **2** |
| Average time per run | **4m 59s** |
| Estimated human time | **6.0h** |
| Total tool time | **9m 59s** |
| Time saved | **5.8h** |
| Validation rate | **1/2 (50%)** |
| Recommendation acceptance | **2/2 (100%)** |
| Avg files explored per run | **10.5** |

---

## Approach Distribution

| Approach | Count | Distribution |
|----------|-------|-------------|
| **A — Minimal** | 0 | `░░░░░░░░░░` 0% |
| **B — Clean** | 1 | `█████░░░░░` 50% |
| **C — Pragmatic** | 1 | `█████░░░░░` 50% |

> **A — Minimal:** smallest change, lowest risk
> **B — Clean:** architecturally correct, highest long-term value
> **C — Pragmatic:** balanced, ships sooner without significant debt

---

## All Decisions

| Decision | Repo | Language | Approach | Time | Issue | Validated |
|----------|------|----------|----------|------|-------|-----------|
| [Rate Limiting Strategy for Public API](example-output/0001-rate-limiting-strategy.md) | `tiangolo/fastapi` | Python | C — Pragmatic ✅ | 4m 47s | [🔗 Issue](https://github.com/tiangolo/fastapi/issues/1234) | — |
| [useTable Filter Reverse Mapping for syncWithLocation](example-output/0002-usetable-filter-reverse-mapping-refine.md) | `refinedev/refine` | TypeScript | B — Clean ✅ | 5m 12s | [🔗 Issue](https://github.com/refinedev/refine/issues/7338) | [✅ PR](https://github.com/refinedev/refine/pull/7385) |

_✅ = recommendation accepted · 🔄 = team chose different approach_

---

## Language Breakdown

| Language | Decisions |
|----------|-----------|
| Python | 1 |
| TypeScript | 1 |

---

## How to read this dashboard

- **Time saved** — `(estimated human hours per decision × total decisions) − total tool time`
- **Validation rate** — ADRs where a community PR independently arrived at the same approach
- **Recommendation acceptance** — runs where the team accepted the tool's recommended approach without override

---

_Generated by [arch-decision](.) — open-source ADR orchestrator for any codebase_
