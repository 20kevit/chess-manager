"""
Tournament Rulebook Service.

Handles tournament rulebook management (text, sections, PDF).
"""
from domain.rulebook import parse_sections, serialize_sections
from app.extensions import db

from infrastructure.models.tournament import TournamentModel


class TournamentRulebookService:
    """Service for managing tournament rulebook settings."""

    @staticmethod
    def update_rulebook_settings(tournament: TournamentModel,
                                 form_data: dict) -> None:
        """Update ONLY the rulebook representations.

        Owns all three independent optional forms:
        - rulebook_text (raw long-form)
        - rulebook_sections (ordered {key,title,body} JSON posted as
          sections_json; replace-all semantics — list order is display order)
        - rulebook_pdf_path is file-based and handled by the route
        Pricing, dates, basic settings and registration requirements are
        never touched here.
        """
        from domain.rulebook import parse_sections, serialize_sections

        tournament.rulebook_text = form_data.get("rulebook_text", "").strip()

        sections = parse_sections(
            form_data.get("sections_json", "") or "[]"
        )
        tournament.rulebook_sections = serialize_sections(sections)

        db.session.commit()