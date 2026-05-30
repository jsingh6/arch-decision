<div align="center">

# 📐 arch-decision

### Stop losing architectural decisions to Slack threads and forgotten docs.

**arch-decision** is an open-source AI orchestrator that runs inside any codebase, explores it deeply, and produces a formal Architecture Decision Record — in minutes, not hours.

[View Example ADR](example-output/0002-usetable-filter-reverse-mapping-refine.md) · [Impact Dashboard](DASHBOARD.md) · [Install](#install)

</div>

---

## The Problem

Every team faces the same gap: a decision gets made, the code gets written, but nobody wrote down *why*. Six months later a new engineer changes it — and the same debate happens all over again.

Architecture Decision Records (ADRs) solve this. But writing them is friction. It takes a senior engineer 2–4 hours to research the codebase, draft approaches, build a trade-off table, and write it up clearly. So it almost never happens.

**arch-decision removes that friction entirely.**

---

## What It Does

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

Works on any language. Any framework. Any team.

---

## Why It's Different

| | GitHub Copilot / Cursor | arch-decision |
|--|--|--|
| Operates on | Files and lines | The full decision lifecycle |
| Knows *why* you're building | No | Yes — starts from the problem |
| Produces documentation | No | Yes — formal ADR, committed to git |
| Human approval gate | No | Yes — cannot proceed without sign-off |
| Resumable across sessions | No | Yes — checkpoints after every phase |
| Independently validated | — | Yes — community PRs confirm recommendations |

---

## Real Example

Ran against [`refinedev/refine`](https://github.com/refinedev/refine) on issue [#7338](https://github.com/refinedev/refine/issues/7338) — a feature request for reverse filter mapping in `useTable` with `syncWithLocation`.

The tool explored the codebase cold, found prior art in `crudFiltersToColumnFilters`, identified the framework-agnostic constraint in `packages/core`, and recommended an `onParse` callback scoped to the antd wrapper.

A community contributor independently opened [PR #7385](https://github.com/refinedev/refine/pull/7385) with the same callback name, same scope, same placement — without seeing this output.

**The tool reached the same conclusion a human engineer did, from a cold start, in under 5 minutes.**

[Read the full ADR](example-output/0002-usetable-filter-reverse-mapping-refine.md)

---

## How It Works

arch-decision is a [Claude Code](https://claude.ai/code) plugin built on a multi-agent architecture:

- **Orchestrator** (`skills/arch-decision/SKILL.md`) — coordinates all 8 phases, maintains a context bus, enforces the human approval gate
- **Explorer agents** (`agents/arch-explorer/`) — 3 run in parallel during Phase 2, each focused on a different angle: prior art, impact map, and constraints
- **Synthesizer agent** (`agents/arch-synthesizer/`) — produces the trade-off table and recommendation from all three approaches

The human approval gate in Phase 6 means the agent cannot write the ADR without your explicit sign-off. It is designed to accelerate human judgment, not replace it.

---

## Get Started

**Requires [Claude Code](https://claude.ai/code).** Install it first if you haven't already.

Then install the plugin:

```bash
claude plugin install arch-decision
```

Open Claude Code inside any repo and run:

```bash
/arch-decision <GitHub issue URL, Jira description, or plain text>
```

That's it. Examples of what you can pass:

```bash
# GitHub issue
/arch-decision https://github.com/owner/repo/issues/42

# Paste your Jira ticket summary or description directly
/arch-decision We need reverse filter mapping in useTable so URL params sync back to filter state on page load

# Or just describe the problem in plain English
/arch-decision add rate limiting to the public API
```

The tool asks you clarifying questions, shows you 3 approaches with a trade-off table, and waits for your approval before writing anything. The ADR is saved to `docs/decisions/` in your repo.

> If the problem is still vague and you want to frame it first, use `/arch-intake your problem here` before running `/arch-decision`.

---

## Impact Dashboard

Metrics are tracked automatically on every ADR merge.

[View the full Impact Dashboard](DASHBOARD.md)

---

## Repository Structure

```
arch-decision/
├── skills/
│   ├── arch-decision/SKILL.md      — 8-phase orchestrator
│   └── arch-intake/SKILL.md        — problem framing pre-skill
├── agents/
│   ├── arch-explorer/agent.md      — parallel codebase exploration
│   └── arch-synthesizer/agent.md   — trade-off synthesis
├── example-output/                 — real ADR examples
├── scripts/generate_dashboard.py   — auto-generates DASHBOARD.md
└── .github/workflows/              — updates dashboard on every ADR merge
```

---

## License

MIT
