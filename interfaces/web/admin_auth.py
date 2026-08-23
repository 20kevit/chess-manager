"""
Tournament administration authorization helpers.

Authorization model (user-account based):
1. System admin      -> access to every tournament
2. Organizer         -> access to tournaments they created
3. Dedicated arbiter -> access via an ACCEPTED TournamentStaffModel invitation
"""
from flask_login import current_user
from infrastructure.repositories import TournamentRepository


def require_admin(public_id):
    """
    Check if the current user may administer this tournament.
    Returns the TournamentModel or None.
    """
    from infrastructure.db_models import TournamentStaffModel

    tournament = TournamentRepository.get_by_public_id(public_id)
    if not tournament:
        return None

    if not current_user.is_authenticated:
        return None

    # System admin
    if current_user.is_admin:
        return tournament
    # Tournament organizer
    if tournament.organizer_id == current_user.id:
        return tournament
    # Dedicated arbiter for this tournament (accepted invitations only)
    is_assigned = TournamentStaffModel.query.filter_by(
        tournament_id=tournament.id, user_id=current_user.id, status="accepted"
    ).first()
    if is_assigned:
        return tournament

    return None
