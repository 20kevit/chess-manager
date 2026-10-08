# AI Change Safety — Permanent Policies

## Purpose

Permanent rules for any autonomous or assisted change to this repository. These
apply to every task, independent of release phase or deployment target. (Temporary
task instructions — commit/push rules for a given phase, beta runbooks, release
gates, session reservations — live in the task prompt, never here.)

## When to use

Every implementation task, before writing code and before claiming completion.

## Source of truth

- Orientation: `AGENTS.md` (first read) + its Documentation Map
- Boundaries: `clean-architecture.md`, `fide-compliance.md`, `auth-rbac.md`,
  `external-integrations.md`, `database-migrations.md`, `testing-validation.md`,
  `frontend-conventions.md`

## Permanent policies

1. **Audit before implementation.** Establish facts from source code, imports,
   route registration, models, services, config, tests, and migrations — never
   from filenames or assumptions. When docs and code disagree, identify the
   contradiction, determine the authoritative source, record it, and never
   silently "fix" application behavior to match docs.
2. **No guessing.** What cannot be established from evidence is marked
   `UNVERIFIED` (fact) or `UNRESOLVED` (decision). Assumptions never become
   Skill instructions, code, or migration steps.
3. **Preserve architectural ownership.** Web → application → domain +
   infrastructure; transactions owned by `application`; repositories flush-only;
   facades stay thin. No reverse imports, no logic in facades.
4. **Preserve authorization.** Backend-authoritative checks on every mutation;
   `capabilities()` stays render-only; public pages stay capability-free;
   workspace stays disabled-not-hidden. Never rely on hidden/disabled UI for
   security; never introduce parallel auth mechanisms.
5. **Preserve FIDE/core boundaries.** No local pairing/tiebreak reimplementation;
   no randomness in the pairing path; no silent ruleset switches or legacy-path
   corrections; Coronate stays lossy-by-contract.
6. **Scope control.** Smallest change satisfying the requirement; reuse existing
   classes, contracts, and components over new ones. No unrelated refactors,
   no drive-by documentation rewrites, no dependency changes except when
   required for validation (and then reverted if unnecessary).
7. **Validate before completion claims.** Run the focused suites plus the
   cross-cutting gates for the risk; know the 953-test baseline (940/6/7, four
   documented root causes) and investigate anything outside it. UI changes
   require browser QA (viewports + RTL + print where applicable).
8. **Escalate, don't improvise.** Stop when: requirements conflict; a boundary
   must be violated to proceed; FIDE/auth/schema evidence is insufficient; a
   baseline failure's signature changes; or production data could be affected.
   State the hypotheses, the evidence, and the decision needed.
9. **Evidence-based final report.** Every completion report cites: files read
   and changed, commands run with results, tests (which suites, counts, known
   vs new failures), and unresolved items. No "verified" without output.

## Validation

A change is complete only when policies 1–9 are each satisfiable from the
report. If any answer is "assumed" rather than evidenced, the work is not done.

## Maintenance / update triggers

Amend this Skill only for permanent policy changes (new enforced boundary, new
validation gate, new escalation class). Never for phase-specific workflow.
