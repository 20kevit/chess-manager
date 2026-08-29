"""
Round Notification Service.

Extracted from RoundService to separate notification orchestration from round lifecycle logic.
This service is designed to be async-ready for future Celery/RQ integration.
"""
import time
import logging
from typing import List

from infrastructure.models.participant import TournamentParticipantModel
from infrastructure.models.tournament import TournamentModel, RoundModel, PairingModel
from application.notification_policy import tournament_allows
from application.notification_service import NotificationService
from application.notification_types import NotificationType


class _RoundNotificationsDisabled(Exception):
    """Sentinel: tournament-level gate disabled the round fan-out."""
    pass


class RoundNotificationService:
    """Handles notification dispatch for round lifecycle events.
    
    Extracted from RoundService to separate notification orchestration from
    round lifecycle logic. Designed to be async-ready for future Celery/RQ integration.
    """
    
    @staticmethod
    def notify_round_created(round_obj: RoundModel, tournament: TournamentModel, pairing_models: List) -> None:
        """Send round creation notifications to all paired players.
        
        This runs synchronously for now but is designed to be moved to a background
        task queue (Celery/RQ) when scale requires it.
        """
        _fanout_started = time.monotonic()
        try:
            # P1-F: tournament-level gate (organizer toggle) is consulted
            # before any per-player dispatch.
            if not tournament_allows(tournament.notification_prefs, "ROUND_CREATED"):
                logging.info(
                    "Round fan-out skipped for tournament %s: event "
                    "disabled by organizer", tournament.id)
                return

            from application.notification_service import NotificationService
            from application.notification_types import NotificationType
            
            for pm in pairing_models:
                white_p = pm.white_participant
                black_p = pm.black_participant
                
                if not white_p:
                    continue
                    
                white_user_id = white_p.profile.user_id if white_p.profile else None
                
                if black_p:
                    # Notify White Player
                    if white_user_id:
                        msg_white = (
                            f"قرعه‌کشی دور {round_obj.round_number} انجام شد.\n\n "
                            f"شما در میز {pm.board_number} با رنگ سفید در مقابل "
                            f"{black_p.full_name} با رنگ سیاه بازی می‌کنید.\n\n "
                            f"با آرزوی موفقیت!"
                        )
                        NotificationService.create_notification(
                            user_id=white_user_id,
                            type=NotificationType.ROUND_CREATED,
                            title=f"اعلام قرعه‌کشی دور {round_obj.round_number}",
                            message=msg_white,
                            link_url=f"/{tournament.public_id}"
                        )
                    
                    # Notify Black Player
                    black_user_id = black_p.profile.user_id if black_p.profile else None
                    if black_user_id:
                        msg_black = (
                            f"قرعه‌کشی دور {round_obj.round_number} انجام شد.\n\n "
                            f"شما در میز {pm.board_number} با رنگ سیاه در مقابل "
                            f"{white_p.full_name} با رنگ سفید بازی می‌کنید.\n\n "
                            f"با آرزوی موفقیت!"
                        )
                        NotificationService.create_notification(
                            user_id=black_user_id,
                            type=NotificationType.ROUND_CREATED,
                            title=f"اعلام قرعه‌کشی دور {round_obj.round_number}",
                            message=msg_black,
                            link_url=f"/{tournament.public_id}"
                        )
                elif pm.result in ["bye", "half-bye", "zero-bye"]:
                    # Notify Bye Player
                    if white_user_id:
                        msg_bye = (
                            f"قرعه‌کشی دور {round_obj.round_number} انجام شد.\n\n "
                            f"شما در این دور استراحت (Bye) دارید."
                        )
                        NotificationService.create_notification(
                            user_id=white_user_id,
                            type=NotificationType.ROUND_CREATED,
                            title=f"اعلام قرعه‌کشی دور {round_obj.round_number}",
                            message=msg_bye,
                            link_url=f"/{tournament.public_id}"
                        )
                        
        except Exception as e:
            logging.error(f"Failed to send round notifications: {str(e)}")
        finally:
            _fanout_seconds = time.monotonic() - _fanout_started
            logging.info(
                "Notification fan-out for tournament %s round %s took %.2fs (%d boards)",
                tournament.id, round_obj.round_number, _fanout_seconds, len(pairing_models),
            )

    @staticmethod
    def notify_round_finished(round_obj, tournament) -> None:
        """Send round finished notifications (placeholder for future implementation)."""
        # TODO: Implement round finished notifications when needed
        pass