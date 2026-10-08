---
name: fide-compliance
description: FIDE guardrails for pairing, tiebreak, standings, rating, and result-vocabulary work — what pairing-core and tiebreak-core own, which invariants chess-manager owns, determinism rules, and when to stop and escalate. Load when touching round lifecycle, standings, or results.
---

# FIDE Compliance — Guardrail Card

A guardrail card, not a rulebook. It tells you **when to stop**, not how the
Dutch system works. For engine APIs read the linked sources; never guess.

## When to use

Round lifecycle, pairing generation, result recording, standings, tiebreak
config, rating display, result vocabulary, bye handling, Coronate result
import/export. Otherwise skip this Skill.

## Three ownerships — do not conflate them

1. **FIDE rules** (owned by the game, implemented by the external cores):
   Dutch-system constraints, tiebreak mathematics. Lives in `pairing-core`
   (`v0.4.1`) / `tiebreak-core` (`v1.2.0`). Never reimplemented here.
2. **chess-manager invariants** (owned by this repo):
   - Result vocabulary is exactly 9 strings: `"1-0" "0-1" "1/2" "+/-" "-/+"
     "+/+" "bye" "half-bye" "zero-bye"` — everywhere.
   - `pairing_no` is fixed at Round 1 creation (rating DESC, `start_number` ASC)
     and never changes mid-tournament.
   - Lifecycle: `Tournament.status` `setup→ongoing→finished`; `Round.status`
     `pending→ongoing→finished`. Progress is incremental (`finish_round`
     updates `points`/`color_history`/`float_history`); only `delete_round` /
     `rebuild_swiss_state` do full recompute.
   - Tiebreak evaluation order comes from `tournament.tiebreak_rules` (JSON).
   - **Koya display quirk** (repo-owned, NOT a FIDE rule): the adapter passes
     `current_round` where the calculator expects total rounds; converges at
     tournament end. Correction belongs to a future ruleset, never the legacy
     path.
   - **Legacy tiebreak behavior is frozen** (repo decision, pinned by
     `tests/application/test_standings_ranking_equivalence.py`). FIDE
     corrections are never silently applied to it; a new ruleset is a
     per-tournament config decision, never a global switch.
   - **Coronate interchange is lossy** for forfeits (`+/-`→`1-0`, `-/+`→`0-1`,
     `+/+`→`bye`). Never a lossless backup.
3. **Core contracts** (owned by the libraries, consumed here):
   `RoundLifecycleService` builds `PlayerData` → `pairing_core.SwissEngine` /
   `validate_round` → `PairingModel`/`RoundModel`;
   `tiebreak_adapter.build_tiebreak_data` is the ONLY place allowed to read DB
   rows for tiebreaks → `tiebreak_core.calculate_all` / `rank_standings` →
   `StandingsService`. Import the cores directly; removed shims stay removed.

## Prohibitions

No `random`/`shuffle` in the pairing path (deterministic). No pairing/tiebreak/
rating math outside the cores. No silent "corrections" to legacy behavior.

## Source of truth

`docs/ARCHITECTURE.md` (boundary map), `docs/DOMAIN.md` §4 (contracts),
`AGENTS.md` §Critical Invariants, the core libraries themselves.

## Validation

`pytest tests/domain tests/application/test_standings_ranking_equivalence.py
tests/application/test_round_lifecycle.py -q`, plus the pairing validator path
(`validate_round`) for pairing changes.

## Escalation

Ambiguous rule, requested outcome change without a cited core version, proposed
ruleset change, or any statement above you cannot confirm in
`docs/ARCHITECTURE.md` or the cores → stop, mark `UNVERIFIED`, escalate. Never
invent a pairing or tiebreak rule.
