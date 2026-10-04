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

- `domain/pairing/` was a compat shim re-exporting `pairing_core`; it has
  been removed — all code imports `pairing_core` directly.
- Declared dependency: `pairing-core @ git+https://github.com/20kevit/pairing-core.git@v0.4.1`
  (verified installable in a clean environment; released API keeps
  `SwissEngine`, `PlayerData`, `PairingRequest`, `NativeDutchEngine`,
  `validate_round`, color computation, and deterministic behavior).
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

- `domain/tiebreak/` (`calculators.py`, `models.py`) were compat shims
  re-exporting `tiebreak_core`; they have been removed — all code imports
  `tiebreak_core` directly. Declared dependency:
  `tiebreak-core @ git+https://github.com/20kevit/tiebreak-core.git@v1.2.0`
  (verified installable in a clean environment).
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
| `interfaces/web/tournament` | `tiebreak_core.display.ALL_TIEBREAKS_DISPLAY` | display names only (direct core import) |

## Compatibility boundaries

- `domain/pairing/` and `domain/tiebreak/` compat shims: REMOVED (no
  remaining consumers; all imports go directly to `pairing_core` /
  `tiebreak_core`). Do not recreate local wrappers.
- `application/*_service.py` facades (`round_service.py`,
  `tournament_service.py`, …): pre-existing delegation shims, unrelated to
  this audit — do not add logic to them.

## Rulesets (tiebreak-core)

- `legacy-0.1.0`: the frozen behavior-preserving extraction. Byte-stable;
  goldens pin it. All current production standings use it (via the legacy
  `calculate_all` / `rank_standings` entry points with no explicit ruleset).
- The released core additionally ships strict/ruleset APIs (`fide-2024`,
  `fide-2026`, descriptors, team surfaces). Chess-manager does not consume
  them; adopting a new ruleset would be a per-tournament configuration
  decision, never a silent global switch. FIDE corrections must never be
  silently applied to the legacy path.

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

- `pairing-core` is pinned to released git tag `v0.4.1` and `tiebreak-core`
  to released git tag `v1.2.0` in `requirements.txt` (both verified
  installable from GitHub in a clean environment with no `PYTHONPATH`,
  editable installs, or local paths). Production installs run the released
  library code — no local core source tree is required.

## What lives where (quick answers)

- Pairing implemented? → **pairing-core**.
- Tie-break calculations implemented? → **tiebreak-core**.
- DB/application data adapted? → `RoundLifecycleService` (pairing),
  `tiebreak_adapter.build_tiebreak_data` + `StandingsService` (tiebreak).
- Pairing/tiebreak results stored? → **chess-manager**
  (`PairingModel`/`RoundModel`/`TournamentParticipantModel` points+histories).
- Tournament configuration owned by? → **chess-manager**
  (`tournament.tiebreak_rules` JSON, `TournamentConfigService`).
