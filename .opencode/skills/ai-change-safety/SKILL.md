---
name: ai-change-safety
description: Permanent change policies for autonomous work on chess-manager — audit-first investigation, evidence over assumption, boundary preservation, scope control, validation, and escalation. Load at the start of every implementation task.
---

# AI Change Safety — Permanent Policies

Task-phase instructions (commit rules, release gates, session reservations)
live in the task prompt, never here.

1. **Audit before implementing.** Establish facts from code, imports, routes,
   models, services, config, tests, migrations — never filenames. When docs
   and code disagree, identify the contradiction and the authoritative source;
   never silently "fix" behavior to match docs.
2. **Evidence over assumption.** What cannot be proven is `UNVERIFIED` (fact)
   or `UNRESOLVED` (decision). Assumptions never become instructions, code,
   or migration steps.
3. **Preserve boundaries.** Layer direction and transaction ownership
   (`clean-architecture`); backend-authoritative authorization with
   render-only capabilities (`auth-rbac`); no local pairing/tiebreak
   reimplementation and no silent ruleset switches (`fide-compliance`);
   integration contracts and fallbacks (`external-integrations`).
4. **Smallest safe change.** Reuse existing classes, contracts, and components.
   No unrelated refactors, drive-by rewrites, or dependency changes except
   when required for validation.
5. **Validate before claiming success.** Focused suites plus the gates for the
   risk (`testing-validation`); browser QA for UI (`frontend-conventions`).
   A change is complete only when every claim in the report is evidenced.
6. **Escalate, don't invent.** Stop on conflicting requirements, unavoidable
   boundary violations, insufficient evidence, shifted baselines, or any
   production-data risk. Report hypotheses, evidence, and the decision needed.
7. **Report evidence.** Files read and changed, commands with results, test
   suites with counts (known vs new failures), unresolved items.
8. **Review Skills when sources of truth change.** Rule: `AGENTS.md`
   §Skill Maintenance.

A "verified" without output is not done.
