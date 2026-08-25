"""
Tournament administration authorization helpers (P1-B tiered model).

Authorization model (user-account based):
1. System admin   -> full access to every tournament (both tiers)
2. Organizer      -> full access to tournaments they created (both tiers)
3. Chief arbiter  -> accepted TournamentStaffModel with role='chief_arbiter'
                     -> BOTH tiers
4. Arbiter        -> accepted TournamentStaffModel with role='arbiter'
                     -> RESULT-EDITOR tier only

Tiers:
- tournament manager : everything administrative (settings, pricing,
  players, registrations/payments, staff, backups, round generation/deletion)
- result editor      : the operational result console (view rounds,
  enter/update results, byes/manual locks, board adjustments)

`require_admin` is kept as the historical entry point and now means the
MANAGER tier; result-side routes call `require_result_editor` explicitly.
Server-side enforcement only — UI flags are cosmetic.
"""
from flask_login import current_user
from infrastructure.repositories import TournamentRepository


def _accepted_staff_role(tournament_id: int, user_id: int):
    """Return the role string of the user's ACCEPTED staff row, or None."""
    from infrastructure.db_models import TournamentStaffModel
    row = TournamentStaffModel.query.filter_by(
        tournament_id=tournament_id, user_id=user_id, status="accepted"
    ).first()
    return row.role if row else None


def _authorize(public_id, chief_only: bool):
    """Shared gate. Returns TournamentModel or None.

    chief_only=False -> result-editor tier (managers + any accepted staff)
    chief_only=True  -> manager tier (system admin/organizer/chief only)
    """
    tournament = TournamentRepository.get_by_public_id(public_id)
    if not tournament:
        return None

    if not current_user.is_authenticated:
        return None

    # System admin: always both tiers.
    if current_user.is_admin:
        return tournament

    # Tournament organizer: always both tiers.
    if tournament.organizer_id == current_user.id:
        return tournament

    # Accepted staff: role decides the tier.
    role = _accepted_staff_role(tournament.id, current_user.id)
    if role == "chief_arbiter":
        return tournament
    if role == "arbiter" and not chief_only:
        return tournament

    return None


def require_tournament_manager(public_id):
    """Manager tier: system admin, organizer, or accepted CHIEF arbiter."""
    return _authorize(public_id, chief_only=True)


def require_result_editor(public_id):
    """Result-editor tier: managers plus every accepted arbiter."""
    return _authorize(public_id, chief_only=False)


def require_admin(public_id):
    """
    Historical entry point — now strictly the MANAGER tier.

    Check order: unauthenticated -> None; system admin -> tournament;
    organizer -> tournament; accepted staff -> only when their staff role
    grants management (chief_arbiter). Plain 'arbiter' staff are NOT
    managers anymore (P1-B).
    """
    return require_tournament_manager(public_id)
