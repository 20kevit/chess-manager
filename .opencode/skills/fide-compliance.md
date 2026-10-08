# FIDE Compliance — Guardrail Card

## Purpose

Keep chess-manager on the correct side of its three FIDE-related boundaries.
This is a guardrail card, not a rulebook: it tells you **when to stop**, not how
the Dutch system works. For engine APIs and calculation details, read the linked
sources instead of guessing.

## When to use

Touching anything in: round lifecycle / pairing generation / result recording /
standings / tiebreak config / rating display / result vocabulary / bye handling /
Coronate import-export of results. If none of those are involved, skip this Skill.

## Source of truth

- Ownership and data flow: `docs/ARCHITECTURE.md` (authoritative boundary map)
- Engine contracts: `docs/DOMAIN.md` §4 (entry points, input/output contracts)
- Invariants map: `AGENTS.md` §Critical Invariants
- External libraries (canonical implementations — read them, don't copy them):
  `pairing-core` pinned `v0.4.1`, `tiebreak-core` pinned `v1.2.0`
  (`requirements.txt`; upgrade rules: `external-integrations.md`)

## The three ownerships — do not conflate them

1. **Generic FIDE rules** (owned by the game, implemented by the external cores):
   Dutch-system pairing constraints (no repeats, color balance, float handling),
   tiebreak mathematics. Lives in `pairing-core` / `tiebreak-core`. Never
   reimplemented in chess-manager.
2. **chess-manager invariants** (owned by this repo, application-level):
   - Result vocabulary is exactly 9 strings: `"1-0" "0-1" "1/2" "+/-" "-/+"
     "+/+" "bye" "half-bye" "zero-bye"` (everywhere, incl. Coronate mapping).
   - `pairing_no` is fixed at Round 1 creation (rating DESC, `start_number` ASC)
     and never changes mid-tournament.
   - Lifecycle: `Tournament.status` `setup→ongoing→finished`; `Round.status`
     `pending→ongoing→finished`. Normal progress is incremental
     (`finish_round` updates `points`/`color_history`/`float_history`); only
     `delete_round` / `rebuild_swiss_state` do full recompute.
   - Tiebreak evaluation order comes from `tournament.tiebreak_rules` (JSON).
3. **External core contracts** (owned by the libraries, consumed here):
   `RoundLifecycleService` builds `PlayerData` → `pairing_core.SwissEngine` /
   `validate_round` → `PairingModel`/`RoundModel` rows
   (`application/round/round_lifecycle_service.py`);
   `tiebreak_adapter.build_tiebreak_data` is the ONLY place allowed to read DB
   rows for tiebreak purposes → `tiebreak_core.calculate_all` /
   `rank_standings` → `StandingsService`
   (`application/tournament/tiebreak_adapter.py`, `standings_service.py`).

Ownership-sensitive notes (chess-manager invariants, NOT generic FIDE rules):
- **Koya display quirk:** the adapter passes `tournament.current_round` where the
  calculator semantically expects total rounds; converges at tournament end.
  Correction belongs to a future ruleset, never to the legacy path.
- **Legacy tiebreak ruleset** (`legacy-0.1.0`) is frozen and byte-stable, pinned by
  `tests/application/test_standings_ranking_equivalence.py`. FIDE corrections are
  never silently applied to it; a new ruleset would be a per-tournament config
  decision, never a global switch.
- **Coronate interchange is lossy** for forfeits (`+/-`→`1-0`, `-/+`→`0-1`,
  `+/+`→`bye` on round-trip). Never treat it as a lossless backup
  (`docs/INFRASTRUCTURE.md` §6).

## Prohibitions

- No `random`/`shuffle` anywhere in the pairing path — pairing is deterministic.
- No pairing/tiebreak/rating math added to `domain/` (rating/pricing helpers
  excepted), `application/`, or `infrastructure/`.
- No local wrappers around `pairing_core` / `tiebreak_core` (removed shims stay
  removed). Import the cores directly.
- No silent "corrections" to legacy tiebreak behavior or Koya handling.

## Validation

- `beta/.venv/bin/python -m pytest tests/domain tests/application/test_standings_ranking_equivalence.py tests/application/test_round_lifecycle.py -q`
- Pairing changes additionally require the pairing validator path
  (`validate_round`) and the round-lifecycle + web round suites
  (`testing-validation.md`).

## Escalation

Stop, mark `UNVERIFIED`, and escalate when: a FIDE rule is ambiguous; a task asks
to change pairing/tiebreak outcomes without a cited core version; a new tiebreak
ruleset is proposed; or any statement above cannot be confirmed against
`docs/ARCHITECTURE.md` / the core libraries. Never convert an assumption into a
pairing or tiebreak instruction.
