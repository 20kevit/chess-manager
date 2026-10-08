---
name: testing-validation
description: Validation policy for chess-manager — baseline-first workflow, focused-to-full suite strategy, known pre-existing failure classes, and browser-QA triggers. Load before claiming any change complete.
---

# Testing & Validation — Definition of Done

## Policy (permanent — counts live here never)

1. Establish the current baseline **before** implementing (`--collect-only`
   plus the suites below); record exact commands and results.
2. Distinguish pre-existing failures from regressions: same test + same
   assertion/error signature = known condition (record, do not "fix" the test
   to hide it). Anything else — new failure, new error, changed signature —
   is investigated as a regression.
3. A known baseline failure never justifies a new failure.
4. Focused suites first, then the broader relevant suite, then the full gate
   when the change warrants it.
5. Backend tests cannot establish UI correctness — browser QA where required
   (see `frontend-conventions`).
6. Report exact commands, counts, and any omitted scope.

## Known baseline conditions — re-verify before relying on them.

Contract/refactor drift, not product bugs:

- Payment facade `gateway` removal: `test_payment_flow.py` setup errors +
  `test_payment_receipt_flow.py::TestReceiptLifecycle::test_discard_restores_retryable_online_state`
  (`AttributeError` on `PaymentService.gateway`).
- Backup provider gap: `test_data_integrity.py::TestC1BackupSwissState` (3
  tests; `Provider 'custom_json' not found in registry`).
- Model-vs-migration drift: `test_baseline_checkpoint.py::
  test_existing_db_upgrade_adds_p0_columns_without_data_loss`
  (`fide_imports.download/progress` columns).
- Hardened denial contract: `test_fide_import_flow.py::TestRoutes::
  test_status_endpoint_authz_matrix` (expects 302; intended behavior is 403).

## Commands

```bash
python -m pytest tests/ --collect-only -q
pytest tests/test_architecture.py tests/domain -q
pytest tests/application tests/infrastructure tests/integration -q
pytest tests/web tests/test_security_prod_regression.py tests/test_release_candidate_hardening.py -q
# Full gate (~30 min, run at the end when warranted):
python -m pytest tests/ -q --tb=short -p no:warnings
```

Use the venv python (`beta/.venv/bin/python` in this checkout). No pytest
config file exists — plain `tests/` path, no `-k`/`-m`/`--ignore` unless the
task scopes them (then state the omission).

## Conventions

`tests/conftest.py`: in-memory SQLite, `TESTING=True`, `WTF_CSRF_ENABLED=False`,
function-scoped fresh app. Follow the existing class-based integration style
with service-layer fixtures; add unit tests when touching `domain/` areas.

## Source of truth

`tests/conftest.py`, `AGENTS.md` §Testing Conventions,
`docs/PRODUCTION_READINESS.md` §Evidence Commands.

## Escalation

Suite cannot complete, collection count moves without a test-file change,
baseline signatures shift, or SQLite-vs-MySQL behavior differs in ways tests
cannot settle.
