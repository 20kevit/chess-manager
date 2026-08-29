"""
Infrastructure Layer Package.

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
from infrastructure.repositories import (
    UserRepository,
    PlayerProfileRepository,
    TournamentRepository, RoundRepository, PairingRepository, ManualPairingRepository,
    ParticipantRepository,
    RegistrationRepository, PromoCodeRepository, PaymentRepository,
    TournamentStaffRepository,
    FidePlayerRepository, FideRatingRepository, FideImportRepository,
    PlayerVerificationRepository,
    NotificationRepository, NotificationPreferenceRepository,
)

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