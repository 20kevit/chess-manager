"""
Infrastructure Package.

This package contains all database models, repositories, and external integrations.
"""
# Models - exported from models package
from infrastructure.models import (
    UserModel, UserRoleModel,
    PlayerProfileModel,
    TournamentModel, RoundModel, PairingModel, ByeRequestModel, ManualPairingModel,
    TournamentParticipantModel,
    RegistrationModel, PaymentModel, PromoCodeModel,
    TournamentStaffModel,
    FidePlayerModel, FideRatingModel, FideImportModel,
    PlayerVerificationModel,
    NotificationModel, NotificationPreferenceModel,
    TournamentPrizeModel, PrizeAllocationModel,
    TempImportDataModel,
)

# Repositories - exported from repositories package

# File Storage
from infrastructure.file_storage import (
    FileStorageError,
    MAX_IMAGE_BYTES,
    MAX_PDF_BYTES,
    PDF_MIMETYPE,
    IMAGE_MIMETYPES,
    IMAGE_EXTENSIONS,
    PDF_EXTENSIONS,
    detect_image_type,
    save_image,
    remove_image,
    resolve_private_file,
    detect_pdf,
    save_pdf,
    remove_pdf,
)

# FIDE Storage
from infrastructure.fide.storage import (
    FideStorageError,
    get_period_string,
    extract_players_zip,
    ensure_players_xml,
    download_and_extract_xml,
    count_players_in_xml,
    cleanup_old_files,
    FideStorageManager,
)

# Gateways
from infrastructure.gateways.zarinpal_gateway import ZarinpalGateway

# Providers
from infrastructure.providers.coronate_provider import CoronateProvider

from infrastructure.models.fide import (FideImportModel, FidePlayerModel, FideRatingModel)
from infrastructure.models.notification import (NotificationModel, NotificationPreferenceModel)
from infrastructure.models.participant import TournamentParticipantModel
from infrastructure.models.prize import (PrizeAllocationModel, TournamentPrizeModel)
from infrastructure.models.profile import PlayerProfileModel
from infrastructure.models.registration import (PaymentModel, PromoCodeModel, RegistrationModel)
from infrastructure.models.staff import TournamentStaffModel
from infrastructure.models.temp import TempImportDataModel
from infrastructure.models.tournament import (ByeRequestModel, ManualPairingModel, PairingModel, RoundModel, TournamentModel)
from infrastructure.models.user import (UserModel, UserRoleModel)
from infrastructure.models.verification import PlayerVerificationModel
from infrastructure.repositories.fide import (FideImportRepository, FidePlayerRepository, FideRatingRepository)
from infrastructure.repositories.notification import (NotificationPreferenceRepository, NotificationRepository)
from infrastructure.repositories.participant import ParticipantRepository
from infrastructure.repositories.profile import PlayerProfileRepository
from infrastructure.repositories.registration import (PaymentRepository, PromoCodeRepository, RegistrationRepository)
from infrastructure.repositories.staff import TournamentStaffRepository
from infrastructure.repositories.tournament import (ManualPairingRepository, PairingRepository, RoundRepository, TournamentRepository)
from infrastructure.repositories.user import UserRepository
from infrastructure.repositories.verification import PlayerVerificationRepository
__all__ = [
    # Models
    "UserModel", "UserRoleModel",
    "PlayerProfileModel",
    "TournamentModel", "RoundModel", "PairingModel", "ByeRequestModel", "ManualPairingModel",
    "TournamentParticipantModel",
    "RegistrationModel", "PaymentModel", "PromoCodeModel",
    "TournamentStaffModel",
    "FidePlayerModel", "FideRatingModel", "FideImportModel",
    "PlayerVerificationModel",
    "NotificationModel", "NotificationPreferenceModel",
    "TournamentPrizeModel", "PrizeAllocationModel",
    "TempImportDataModel",
    # Repositories
    "UserRepository",
    "PlayerProfileRepository",
    "TournamentRepository", "RoundRepository", "PairingRepository", "ManualPairingRepository",
    "ParticipantRepository",
    "RegistrationRepository", "PromoCodeRepository", "PaymentRepository",
    "TournamentStaffRepository",
    "FidePlayerRepository", "FideRatingRepository", "FideImportRepository",
    "PlayerVerificationRepository",
    "NotificationRepository", "NotificationPreferenceRepository",
    # File Storage
    "FileStorageError",
    "MAX_IMAGE_BYTES",
    "MAX_PDF_BYTES",
    "PDF_MIMETYPE",
    "IMAGE_MIMETYPES",
    "IMAGE_EXTENSIONS",
    "PDF_EXTENSIONS",
    "detect_image_type",
    "save_image",
    "remove_image",
    "resolve_private_file",
    "detect_pdf",
    "save_pdf",
    "remove_pdf",
    # FIDE Storage
    "FideStorageError",
    "get_period_string",
    "extract_players_zip",
    "ensure_players_xml",
    "download_and_extract_xml",
    "count_players_in_xml",
    "cleanup_old_files",
    "FideStorageManager",
    # Gateways
    "ZarinpalGateway",
    # Providers
    "CoronateProvider",
]