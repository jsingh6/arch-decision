# arch-decision

A Claude Code plugin that orchestrates the full architecture decision workflow — from a vague problem statement to a formal, team-reviewed Architecture Decision Record (ADR).

Works on **any codebase, any language, any team.**

---

## What it does

When you face a technical decision, `arch-decision`:

1. **Reads your problem** — GitHub issue URL, free text, or a structured intake doc
2. **Explores your codebase** — three parallel agents map prior art, dependencies, and constraints
3. **Asks clarifying questions** — surfaces ambiguity before designing anything
4. **Generates 3 approaches** — Minimal, Clean, and Pragmatic, designed in parallel
5. **Synthesizes a recommendation** — trade-off table with a clear rationale
6. **Waits for your approval** — nothing is written without explicit sign-off
7. **Writes a formal ADR** — to `docs/decisions/`, linkable from your PR
8. **Notifies your team** — optional Slack/Teams webhook

> A senior engineer would spend 2–3 hours on this. `arch-decision` does it in minutes and produces a document that would otherwise never get written.

---

## Demo

> **[▶ Watch a 3-minute demo](https://your-demo-link-here)**
>
> Demo runs against the [fastapi](https://github.com/tiangolo/fastapi) open-source repo,
> taking a real GitHub issue and producing the ADR in `example-output/`.

See [`example-output/0001-rate-limiting-strategy.md`](example-output/0001-rate-limiting-strategy.md) for a sample ADR output.

---

## Install

```bash
# Install the plugin into Claude Code
claude plugin install arch-decision

# Or clone and install locally
git clone https://github.com/your-handle/arch-decision
claude plugin install ./arch-decision
```

---

## Usage

```bash
# From a free-text description
/arch-decision add rate limiting to the public API

# From a GitHub issue URL
/arch-decision https://github.com/owner/repo/issues/42

# Structure a vague problem first, then decide
/arch-intake our API is too slow
# → produces .claude/decisions/intake-*.md
/arch-decision .claude/decisions/intake-api-performance.md
```

---

## Config (optional)

Create `.claude/arch-decision-config.json` in your repo root:

```json
{
  "team": "my-team",
  "decisions_dir": "docs/decisions",
  "notification": {
    "slack_webhook_url": "https://hooks.slack.com/services/...",
    "channel": "#architecture"
  },
  "issue_tracker": {
    "type": "github",
    "repo": "owner/repo"
  }
}
```

Without config, the plugin uses sensible defaults and skips notifications.

---

## Skills

| Skill | Purpose |
|-------|---------|
| `/arch-decision` | Full ADR orchestration — explore, design, recommend, write |
| `/arch-intake` | Structure a vague problem before running `/arch-decision` |

---

## Output

Every run produces a formal ADR at `docs/decisions/NNNN-[slug].md` with:

- Problem context (written for a future engineer with zero context)
- All 3 approaches with honest pros/cons
- Trade-off table across 5 criteria
- The chosen approach with rationale
- Consequences (positive and watch-fors)
- Key files affected
- Links to related ADRs

See [`example-output/`](example-output/) for a real example.

---

## How it works

```
/arch-decision "add rate limiting"
       │
       ├── Phase 0: Detect repo, language, framework, existing ADRs
       ├── Phase 1: Parse problem statement (GitHub issue or free text)
       ├── Phase 2: 3 parallel exploration agents
       │     ├── Agent A: Prior art (how was this solved before?)
       │     ├── Agent B: Impact map (what would this change touch?)
       │     └── Agent C: Constraints (what can't change?)
       ├── Phase 3: Clarifying questions (never skipped)
       ├── Phase 4: 3 parallel approach agents
       │     ├── Agent A: Minimal approach
       │     ├── Agent B: Clean approach
       │     └── Agent C: Pragmatic approach
       ├── Phase 5: Trade-off synthesis + recommendation
       ├── Phase 6: Human approval gate ← nothing written without this
       ├── Phase 7: Write ADR to docs/decisions/
       └── Phase 8: Link back to GitHub issue / Linear / Jira
```

**Human-in-the-loop by design.** The agent cannot write the ADR without explicit approval in Phase 6. Every decision point is auditable.

**Resumable.** If you close the session mid-way, re-running `/arch-decision` will detect the draft and offer to resume from the last completed phase.

---

## Architecture

```
arch-decision/
├── .claude-plugin/
│   └── plugin.json              ← plugin manifest
├── skills/
│   ├── arch-decision/
│   │   └── SKILL.md             ← main orchestrator (8-phase workflow)
│   └── arch-intake/
│       └── SKILL.md             ← problem framing pre-skill
├── agents/
│   ├── arch-explorer/
│   │   └── agent.md             ← codebase exploration agent
│   └── arch-synthesizer/
│       └── agent.md             ← trade-off synthesis agent
├── example-output/
│   └── 0001-rate-limiting-strategy.md  ← sample ADR
└── docs/
    └── decisions/               ← your ADRs live here (gitignored in this repo)
```

---

## Inspired by

The architecture of this plugin is based on patterns developed for the TTMobile iOS team at Intuit — a 13-phase multi-agent engineering lifecycle orchestrator. `arch-decision` extracts the architecture decision layer and makes it generic, open-source, and usable by any team.

---

## License

MIT
