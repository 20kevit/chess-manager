# Testing & Validation — Definition of Done

## Purpose

Define what "verified" means: which suites to run, what the known baseline is,
and when a failure is a regression versus a documented pre-existing condition.
The full suite takes ~30 minutes — select suites deliberately.

## When to use

Before claiming any change complete; when choosing test commands; when a test
fails and you must decide whether it is yours. Read with the Skill of the layer
changed.

## Source of truth

- Fixture: `tests/conftest.py` (`TestConfig`: in-memory SQLite, `TESTING=True`,
  `WTF_CSRF_ENABLED=False`; function-scoped fresh app).
- Conventions: `AGENTS.md` §Testing Conventions; readiness evidence:
  `docs/PRODUCTION_READINESS.md` §Evidence Commands.
- No linter/formatter config, no CI pipeline — pytest is the gate.

## Baseline (authoritative, measured at HEAD `310a6a6`)

**953 collected: 940 passed, 6 failed, 7 errors.** Do NOT use the stale `856`
figure from `docs/PRODUCTION_READINESS.md` (dated 2026-08-31; predates ~97
added tests). The baseline below is a known repository state, never a license
to ignore new failures.

| # | Cases | Root cause (contract/refactor drift, not product bugs) |
|---|-------|--------------------------------------------------------|
| 1 | 7 ERRORs `tests/test_payment_flow.py` (D1×5, D5×2) + 1 FAILED `test_payment_receipt_flow.py::TestReceiptLifecycle::test_discard_restores_retryable_online_state` | Fixture/tests reference `PaymentService.gateway`, removed in the payment-package refactor (`AttributeError` at fixture setup / attribute access). |
| 2 | 3 FAILED `tests/test_data_integrity.py::TestC1BackupSwissState` | `Provider 'custom_json' not found in registry` during import; Swiss-state assertions fail downstream. |
| 3 | 1 FAILED `tests/test_baseline_checkpoint.py::test_existing_db_upgrade…` | Model-vs-migration drift: model has `fide_imports.download_progress` / `processing_progress`, migration lacks them. |
| 4 | 1 FAILED `test_fide_import_flow.py::TestRoutes::test_status_endpoint_authz_matrix` | Expects 302; hardened route returns 403 for authenticated non-admin. The 403 is the intended contract. |

## Commands

```bash
/opt/projects/chess-manager/beta/.venv/bin/python -m pytest tests/ --collect-only -q  # expect 953
# Focused (preferred during work):
pytest tests/test_architecture.py -q
pytest tests/domain -q
pytest tests/application -q
pytest tests/infrastructure -q
pytest tests/integration -q
pytest tests/web -q
pytest tests/test_security_prod_regression.py tests/test_release_candidate_hardening.py -q
# Full gate (run at the end; ~30 min):
/opt/projects/chess-manager/beta/.venv/bin/python -m pytest tests/ -q --tb=short -p no:warnings
```

No pytest config file exists — plain `tests/` path, no `-k`/`-m`/`--ignore` unless
the task explicitly scopes them (then state what was omitted).

## Strategy

1. Run the focused suites for the touched layer first (fast feedback).
2. Add the cross-cutting gates for the risk: architecture tests for layer moves,
   security regression for auth/money/upload changes, frontend token test for UI
   changes (`tests/test_frontend_tokens.py`), equivalence tests for
   pairing/tiebreak changes.
3. New tests follow the existing class-based integration style with service-layer
   SQLite fixtures. Unit tests for touched `domain/` areas are expected when
   touching those areas.
4. A failure matching one of the four baseline rows exactly (same test, same
   assertion/error) is a known condition — record it, do not "fix" the test to
   hide it. Any other failure, any new error, or any baseline row failing
   differently → investigate as a regression.
5. Browser QA is required for UI changes (3 viewports 360/768/1200, RTL, Print
   Preview for print pages) — see `frontend-conventions.md`. Pytest alone does
   not cover rendering.

## Escalation

Escalate when: a baseline failure's signature changes; the full suite cannot
complete; collection count moves without a test-file change; or DB-backed
behavior differs between SQLite (tests) and MySQL (production) in a way tests
cannot settle.
