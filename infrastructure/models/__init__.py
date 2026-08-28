"""
Database Models Package.

This package contains all SQLAlchemy models organized by domain.
"""
# User & Authentication
from infrastructure.models.user import UserModel, UserRoleModel

# Player Profile
from infrastructure.models.profile import PlayerProfileModel

# Tournament & Competition
from infrastructure.models.tournament import (
    TournamentModel,
    RoundModel,
    PairingModel,
    ByeRequestModel,
    ManualPairingModel,
)

# Participant
from infrastructure.models.participant import TournamentParticipantModel

# Registration & Payment
from infrastructure.models.registration import (
    RegistrationModel,
    PaymentModel,
    PromoCodeModel,
)

# Staff
from infrastructure.models.staff import TournamentStaffModel

# FIDE
from infrastructure.models.fide import (
    FidePlayerModel,
    FideRatingModel,
    FideImportModel,
)

# Verification
from infrastructure.models.verification import PlayerVerificationModel

# Notification
from infrastructure.models.notification import (
    NotificationModel,
    NotificationPreferenceModel,
)

# Prizes
from infrastructure.models.prize import (
    TournamentPrizeModel,
    PrizeAllocationModel,
)

# Temporary Import Data
from infrastructure.models.temp import TempImportDataModel

__all__ = [
    # User
    "UserModel",
    "UserRoleModel",
    # Profile
    "PlayerProfileModel",
    # Tournament
    "TournamentModel",
    "RoundModel",
    "PairingModel",
    "ByeRequestModel",
    "ManualPairingModel",
    # Participant
    "TournamentParticipantModel",
    # Registration
    "RegistrationModel",
    "PaymentModel",
    "PromoCodeModel",
    # Staff
    "TournamentStaffModel",
    # FIDE
    "FidePlayerModel",
    "FideRatingModel",
    "FideImportModel",
    # Verification
    "PlayerVerificationModel",
    # Notification
    "NotificationModel",
    "NotificationPreferenceModel",
    # Prizes
    "TournamentPrizeModel",
    "PrizeAllocationModel",
    # Temp
    "TempImportDataModel",
]