# application/notification_types.py
import enum

class NotificationType(enum.Enum):
    """Notification types actively dispatched by business logic."""
    WELCOME = "WELCOME"
    REGISTRATION_SUBMITTED = "REGISTRATION_SUBMITTED"
    REGISTRATION_APPROVED = "REGISTRATION_APPROVED"
    REGISTRATION_REJECTED = "REGISTRATION_REJECTED"
    ARBITER_INVITATION = "ARBITER_INVITATION"
    FIDE_VERIFICATION_APPROVED = "FIDE_VERIFICATION_APPROVED"
    FIDE_VERIFICATION_REJECTED = "FIDE_VERIFICATION_REJECTED"
    ROUND_CREATED = "ROUND_CREATED"

class FutureNotificationType(enum.Enum):
    """Reserved types: not yet dispatched by any business logic.
    Kept separate so the preferences UI only shows real, controllable
    notification kinds."""
    FIDE_RATING_UPDATED = "FIDE_RATING_UPDATED"
    TOURNAMENT_STARTED = "TOURNAMENT_STARTED"
    TOURNAMENT_FINISHED = "TOURNAMENT_FINISHED"
    PAYMENT_CONFIRMED = "PAYMENT_CONFIRMED"
    PAIRING_PUBLISHED = "PAIRING_PUBLISHED"
