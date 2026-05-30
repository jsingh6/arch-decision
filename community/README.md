# Community ADR Submissions

This folder contains Architecture Decision Records submitted by engineers who used **arch-decision** on their own codebases.

Every submission here is a real architectural decision made by a real team. Together they form a public record of how the tool performs across different languages, frameworks, and problem types.

---

## How to submit your ADR

1. **Run `/arch-decision`** on a real issue in your codebase
2. **Copy the generated ADR** from `docs/decisions/` in your repo
3. **Fork this repo** and add your ADR to this `community/` folder
4. **Open a PR** — title it `[Community ADR] Your decision title`

That's it. Once merged, your ADR appears in the [Impact Dashboard](../DASHBOARD.md) automatically.

---

## Submission checklist

Before opening a PR, make sure your ADR frontmatter includes:

```yaml
---
id: "NNNN"
title: "Your decision title"
status: accepted
date: YYYY-MM-DD
submitted_by: your-github-username
repo: owner/repo          # the repo you ran arch-decision against
language: TypeScript       # primary language of the codebase
framework: React           # framework if applicable
time_taken_seconds: 300    # how long the run took
approach_recommended: B    # what the tool recommended (A / B / C)
approach_chosen: B         # what your team actually chose
issue: https://github.com/owner/repo/issues/N   # the issue it addressed
validated: false           # set true if a PR later confirmed the approach
validation_pr: ""          # link to that PR if it exists
estimated_human_hours: 3   # how long this would have taken without the tool
---
```

Not sure about a field? Leave it as the default — the dashboard handles missing values gracefully.

---

## Need the template?

Copy [`TEMPLATE.md`](TEMPLATE.md) as your starting point.
