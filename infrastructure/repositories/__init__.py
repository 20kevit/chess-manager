"""
Repository Package.

This package contains all database repository classes organized by domain.
"""
# User & Authentication
from infrastructure.repositories.user import UserRepository

# Player Profile
from infrastructure.repositories.profile import PlayerProfileRepository

# Tournament & Competition
from infrastructure.repositories.tournament import TournamentRepository, RoundRepository, PairingRepository, ManualPairingRepository

# Participant
from infrastructure.repositories.participant import ParticipantRepository

# Registration & Payment
from infrastructure.repositories.registration import (
    RegistrationRepository,
    PromoCodeRepository,
    PaymentRepository,
)

# Staff
from infrastructure.repositories.staff import TournamentStaffRepository

# FIDE
from infrastructure.repositories.fide import (
    FidePlayerRepository,
    FideRatingRepository,
    FideImportRepository,
)

# Verification
from infrastructure.repositories.verification import PlayerVerificationRepository

# Notification
from infrastructure.repositories.notification import (
    NotificationRepository,
    NotificationPreferenceRepository,
)

__all__ = [
    # User
    "UserRepository",
    # Profile
    "PlayerProfileRepository",
    # Tournament
    "TournamentRepository",
    "RoundRepository",
    "PairingRepository",
    "ManualPairingRepository",
    # Participant
    "ParticipantRepository",
    # Registration
    "RegistrationRepository",
    "PromoCodeRepository",
    "PaymentRepository",
    # Staff
    "TournamentStaffRepository",
    # FIDE
    "FidePlayerRepository",
    "FideRatingRepository",
    "FideImportRepository",
    # Verification
    "PlayerVerificationRepository",
    # Notification
    "NotificationRepository",
    "NotificationPreferenceRepository",
]