"""
Tournament Admin Service.

Provides tournament listing for admin dashboard.
"""
from typing import List, Dict, Optional

from app.extensions import db

from infrastructure.models.tournament import TournamentModel
from infrastructure.models.participant import TournamentParticipantModel


class TournamentAdminService:
    """Service for tournament administration in admin panel."""

    @staticmethod
    def get_tournaments_paginated(page: int, per_page: int, search: str = '', status_filter: str = '') -> dict:
        """Get paginated tournaments for admin view."""
        query = TournamentModel.query

        if search:
            query = query.filter(TournamentModel.name.ilike(f"%{search}%"))

        if status_filter:
            query = query.filter(TournamentModel.status == status_filter)

        query = query.order_by(TournamentModel.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        # Add participant count for each tournament
        tournaments_with_counts = []
        for t in pagination.items:
            participant_count = TournamentParticipantModel.query.filter_by(tournament_id=t.id).count()
            tournaments_with_counts.append({
                'tournament': t,
                'participant_count': participant_count
            })

        return {
            'tournaments': tournaments_with_counts,
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next,
            'prev_page': page - 1 if pagination.has_prev else None,
            'next_page': page + 1 if pagination.has_next else None,
        }