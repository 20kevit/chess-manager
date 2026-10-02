# Architecture Map — pairing / tiebreak boundaries

```
                     chess-manager
                           |
             +-------------+-------------+
             |                           |
             v                           v
       pairing-core                tiebreak-core
       (pairing domain,             (tie-break calculation,
        Swiss engines,               ranking comparator,
        validation)                  rules versioning)
             |                           |
             |                           |
             +-------------+-------------+
                           |
                    tournament workflow
              (orchestration + persistence
               in chess-manager)
```

## Ownership

- **chess-manager** (this repo) is the composition / integration /
  persistence / presentation layer. It owns: tournament lifecycle,
  database models and repositories, configuration (`tiebreak_rules` JSON,
  `total_rounds`, `current_round`), round state, participant state
  (registration, withdrawal, `points`, `color_history`, `float_history`,
  `pairing_no`/`start_number`, `rating_snapshot`), seeding, withdrawal
  filtering, rating/Elo reports, prizes, print/export, UI.
- **pairing-core**: pairing domain — Swiss algorithms, constraints, colors,
  floats, byes, validation, engines, external engine adapters.
- **tiebreak-core**: tie-break calculations, ranking comparator
  (`rank_standings`/`order_ids` over explicitly supplied values),
  tie-break policies/rulesets, domain contracts, conformance logic.
- There is deliberately NO shared `tournament-core` abstraction. If a
  future pairing system needs tie-break-derived ordering, the caller
  passes narrow scalar/vector data (`{player_id: value}`) at the
  boundary — never a library dependency.

## Dependency direction

```
chess-manager ──> pairing-core
chess-manager ──> tiebreak-core
```

- `pairing-core` and `tiebreak-core` are fully independent. Neither
  imports the other; neither imports chess-manager. Both are stdlib-only,
  framework-free domain libraries (verified: no Flask/SQLAlchemy/app
  imports in either core).
- `pairing-core` does not depend on `tiebreak-core` and vice versa.

## Data flow

### Pairing

```
interfaces/web (round routes)
      |
      v
application/round/round_lifecycle_service.py (RoundLifecycleService.create_next_round)
  builds PlayerData from Participant/Round/Pairing rows
      |
      v
pairing_core.SwissEngine.generate() + validate_round()
      |
      v
PairingModel / RoundModel rows (persistence in chess-manager)
```

- `domain/pairing/` is a compat shim re-exporting `pairing_core`; new code
  imports `pairing_core` directly.
- Declared dependency: `pairing-core @ git+https://github.com/20kevit/pairing-core.git@v0.1.0`
  (verified installable in a clean environment).
- `PairingGenerationService` keeps only shared helpers
  (`_initialize_pairing_numbers`, `_get_opponent_ids`/`_have_played`,
  `_validate_color_swap`, `_update_participant_stats_incremental`); the
  former `generate_pairings`/`persist_pairings` duplicate of the lifecycle
  path was removed (zero callers).

### Tiebreak

```
database (Participant / Pairing / Round rows)
      |
application/tournament/tiebreak_adapter.py (build_tiebreak_data — ONLY place
  allowed to read DB rows for tie-break purposes; owns RESULT_SCORES mapping,
  virtual-opponent (-1) convention)
      |
tiebreak_core.calculate_all()  (calculation of values)
      |
application/tournament/standings_service.py (StandingsService.get_standings —
  configuration from tournament.tiebreak_rules, ordering, seeding for Round 0,
  withdrawal filtering, rating changes via domain/rating, presentation dict)
```

- `domain/tiebreak/` (`calculators.py`, `models.py`) are compat shims
  re-exporting `tiebreak_core`; new code imports `tiebreak_core` directly.
- Ordering for active standings comes from the core: `StandingsService`
  calls `rank_standings(core_inputs, criteria, current_round,
  deterministic_keys={pid: pairing_no or start_number or 999})` and maps
  the ordered `PlayerResult`s back to the presentation dict (single source;
  no local comparator — migrated in `cee8787`, pinned by
  `tests/application/test_standings_ranking_equivalence.py`). Initial
  seeding (Round 0 → rating snapshot DESC, start_number ASC) and withdrawal
  filtering (non-active zero-point players never reach the core) stay
  manager-owned by core contract (`tiebreak-core`
  `docs/ADAPTER_CHESS_MANAGER.md`); the core has no status/seeding concept.

## Integration points

| Caller | Callee | What crosses the boundary |
|--------|--------|---------------------------|
| `RoundLifecycleService` | `pairing_core.SwissEngine`, `validate_round`, `compute_color` | `PlayerData` in; `RoundResult`/`PairingCard` out; nothing else |
| `PairingGenerationService` helpers | `pairing_core.models.compute_color` | color-history string → color state (swap validation only) |
| `StandingsService` | `tiebreak_core.calculate_all` (Round-0 seeding branch) + `tiebreak_core.rank_standings` (active standings) | `PlayerTiebreakData` map in; ordered `PlayerResult`s out |
| `interfaces/web/tournament` | `domain.tiebreak.calculators.ALL_TIEBREAKS_DISPLAY` | display names only (via shim) |

## Compatibility boundaries

- `domain/pairing/__init__.py`: shim, no logic. Used only by tests
  (5 files). Migrate tests to `pairing_core` imports when convenient (P2).
- `domain/tiebreak/calculators.py`, `domain/tiebreak/models.py`: shims, no
  logic. Used by tests + one web import (`ALL_TIEBREAKS_DISPLAY`). Keep.
- `application/*_service.py` facades (`round_service.py`,
  `tournament_service.py`, …): pre-existing delegation shims, unrelated to
  this audit — do not add logic to them.

## Rulesets (tiebreak-core)

- `legacy-0.1.0`: the frozen behavior-preserving extraction. Byte-stable;
  goldens pin it. All current production standings use it.
- `fide-2026`: RESERVED name for future FIDE-correct behavior (Handbook
  C.07 effective 1 Mar 2026). Not implemented. Requesting it on the
  strict core path raises `UnsupportedRulesetError`. FIDE corrections
  must never be silently applied to the legacy path.

## Known quirks (preserved, not silently fixed)

- Koya receives `tournament.current_round` where the calculator
  semantically expects total rounds (mid-tournament Koya display only;
  converges at tournament end). Correction belongs to `fide-2026`.
- Coronate interchange tie-break names are translated to registry ids in
  `infrastructure/providers/coronate_parser.py`; names without an exact
  core equivalent pass through and fail closed if consumed. The
  generator's hardcoded export list is export-metadata only.
- Standings read persisted `points` (pre-accumulated at `finish_round`).
  Full state can be rebuilt via `StatsRebuildService.rebuild_swiss_state`
  (imports/restores/round deletion) and points-only via legacy
  `ParticipantRepository.update_points` (repair scripts only). There is
  no automatic corruption detection — a reconcile check is tracked debt.

## Reproducibility

- `pairing-core` is pinned to git tag `v0.1.0` (verified installable from
  GitHub in a clean environment; tag commit `2cb570b`). NOTE: the
  installed editable checkout in dev tracks `origin/main` HEAD (newer
  commits: provider registry, BBP/JaVaFo adapters, TRF interchange,
  deterministic controls, benchmark harness) — dev and prod do NOT run
  the same pairing code. Re-pin or reinstall when new tags are cut.
- `tiebreak-core` integration is BLOCKED on publication: the GitHub repo
  `20kevit/tiebreak-core` exists but is EMPTY (no commits pushed, no
  tags), and `requirements.txt` does not declare it. The test environment
  consumes it from a local editable install. Publication steps: push
  local `master` (6 commits), tag `v0.1.0`, add the pin to
  `requirements.txt`. No push performed in this phase (not authorized).

## What lives where (quick answers)

- Pairing implemented? → **pairing-core**.
- Tie-break calculations implemented? → **tiebreak-core**.
- DB/application data adapted? → `RoundLifecycleService` (pairing),
  `tiebreak_adapter.build_tiebreak_data` + `StandingsService` (tiebreak).
- Pairing/tiebreak results stored? → **chess-manager**
  (`PairingModel`/`RoundModel`/`TournamentParticipantModel` points+histories).
- Tournament configuration owned by? → **chess-manager**
  (`tournament.tiebreak_rules` JSON, `TournamentConfigService`).
