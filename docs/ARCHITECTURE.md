# Architecture — ownership, dependencies, core integration (Phase 0)

## Dependency direction

```text
                  chess-manager
                  /            \
                 /              \
        pairing-core       tiebreak-core
```

- `pairing-core` and `tiebreak-core` are fully independent. Neither
  imports the other; neither imports chess-manager. Both are stdlib-only,
  framework-free domain libraries.
- `chess-manager` is the composition / integration / persistence /
  presentation layer. It owns: tournament lifecycle, database models and
  repositories, configuration (`tiebreak_rules` JSON, `total_rounds`,
  `current_round`), round state, participant state (registration,
  withdrawal, `points`, `color_history`, `float_history`,
  `pairing_no`/`start_number`, `rating_snapshot`), seeding, withdrawal
  filtering, rating/Elo reports, prizes, print/export, UI.
- There is deliberately NO shared `tournament-core` abstraction. If a
  future pairing system (e.g. Burstein) needs tie-break-derived ordering,
  the caller passes narrow scalar/vector data (`{player_id: value}`) at
  the boundary — never a library dependency.

## Pairing integration

`application/round/pairing_generation_service.py` builds
`pairing_core.PlayerData` (pairing_no, rating, points, color/float
histories, opponents, received_bye) and runs `SwissEngine`
(`pairing-core==0.1.0` pinned via git tag in `requirements.txt`).
FIDE-legality validation (`validate_round`) wraps generation as a
non-mutating safety net. Pairing numbers are assigned at round 1 from
rating DESC + start_number ASC and never change afterwards.

## Tie-break integration

`application/tournament/tiebreak_adapter.py` is the single place allowed
to translate persistence rows into tiebreak-core inputs
(`PlayerTiebreakData` / `GameRecord`, 9-type result table, virtual
opponent `-1` for unplayed/missing-opponent games). Calculation AND
ordering come from `tiebreak-core`:

- active standings → `tiebreak_core.rank_standings` (explicit criteria
  order + `pairing_no or start_number or 999` deterministic keys).
  No local ranking comparator remains in the manager.
- round-0 seeding → manager-owned (`rating_snapshot` DESC,
  `start_number` ASC). The core never seeds.
- withdrawal filtering → manager-owned (non-active zero-point players
  never reach the core). The core has no status concept.
- display (`tiebreak_core.display.TIEBREAK_NAMES_FA`), print, exports,
  prizes → manager-owned.

## Rulesets

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

- `pairing-core` is pinned to git tag `v0.1.0` (verified downloadable;
  tag provides every symbol the manager imports).
- `tiebreak-core` integration is BLOCKED on publication: no GitHub
  repository and no tags exist yet, so it cannot be pinned. The test
  environment currently consumes it from a local install. Publication
  steps: create `20kevit/tiebreak-core`, push, tag, add the pin to
  `requirements.txt`. No push performed in Phase 0 (not authorized).
