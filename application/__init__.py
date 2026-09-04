"""
Application Layer - Service Layer Package

This package contains all application services organized by domain.
Services are the exclusive owners of database transactions and orchestrate
business use-cases between the Web/UI layer and Domain/Infrastructure layers.
"""

# Admin services
from application.admin.dashboard_stats_service import DashboardStatsService
from application.admin.system_health_service import SystemHealthService
from application.admin.user_management_service import UserManagementService
from application.admin.tournament_admin_service import TournamentAdminService

# Auth services
from application.auth.authentication_service import AuthenticationService
from application.auth.profile_linking_service import ProfileLinkingService
from application.auth.profile_creation_service import ProfileCreationService

# Roles (Beta: arbiter/organizer requests + auto-approve setting)
from application.roles.role_request_service import RoleRequestService
from application.roles.system_settings_service import SystemSettingsService

# Tournament services
from application.tournament.tournament_config_service import TournamentConfigService
from application.tournament.tournament_pricing_service import TournamentPricingService
from application.tournament.tournament_registration_rules_service import TournamentRegistrationRulesService
from application.tournament.tournament_rulebook_service import TournamentRulebookService
from application.tournament.standings_service import StandingsService

# Round services
from application.round.round_lifecycle_service import RoundLifecycleService
from application.round.pairing_generation_service import PairingGenerationService
from application.round.result_recording_service import ResultRecordingService
from application.round.manual_adjustment_service import ManualAdjustmentService
from application.round.stats_rebuild_service import StatsRebuildService
from application.round.round_notification_service import RoundNotificationService
from application.round.display_service import RoundDisplayService

# Registration services
from application.registration.registration_creator import RegistrationCreator
from application.registration.eligibility_checker import EligibilityChecker
from application.registration.pricing_calculator import PricingCalculator
from application.registration.registration_approver import RegistrationApprover
from application.registration.receipt_handler import ReceiptHandler

# Player services
from application.player.participant_management import ParticipantManagement
from application.player.csv_import_service import PlayerCsvImportService, CsvImportError

# Dashboard services
from application.dashboard_availability_service import DashboardAvailabilityService

# Verification services
from application.verification.verification_request_service import VerificationRequestService
from application.verification.verification_approver import VerificationApprover
from application.verification.verification_status_updater import VerificationStatusUpdater

# FIDE services
from application.fide.fide_import_orchestrator import FideImportOrchestrator
from application.fide.fide_search_service import FideSearchService

# Import/Export services
from application.import_export.export_service import ExportService
from application.import_export.import_service import ImportService
from application.import_export.preview_service import PreviewService

# Prize services
from application.prize.prize_definition_service import PrizeDefinitionService
from application.prize.prize_allocation_service import PrizeAllocationService
from application.prize.prize_summary_service import PrizeSummaryService

# Payment services
from application.payment.payment_initiator import PaymentInitiator

# Telegram/Bale services
from application.telegram.telegram_service import TelegramService
from application.telegram.telegram_link_service import TelegramLinkService
from application.bale.bale_service import BaleService
from application.bale.bale_link_service import BaleLinkService

# Notification services
from application.notification_dispatcher import NotificationDispatcher
from application.notification_service import NotificationService
from application.notification_policy import load_tournament_prefs, tournament_allows, serialize_tournament_prefs
from application.notification_types import NotificationType, FutureNotificationType, NOTIFICATION_TYPE_NAMES_FA
from application.notification_policy import TOURNAMENT_EVENT_TYPES

# Notification provider interfaces
from application.notification_provider_interface import NotificationProviderInterface

# Payment gateway interface
from application.payment_gateway_interface import PaymentGatewayInterface, PaymentRequestResult, PaymentVerifyResult

# Import/Export interfaces
from application.import_export_interface import (
    ImportProvider, ExportProvider,
    PlayerImportExportData, PairingImportExportData,
    TournamentData, BackupFileData, TournamentPreviewData
)

# Provider registry
from application.provider_registry import ProviderRegistry, registry

# Providers
try:
    from application.providers.coronate_provider import CoronateProvider
    from application.providers.coronate_parser import parse_coronate_json, CoronateFormatError
    from application.providers.coronate_generator import generate_coronate_json
except ImportError:
    pass
from application.providers.web_provider import WebProvider
from application.providers.telegram_provider import TelegramProvider
from application.providers.bale_provider import BaleProvider

__all__ = [
    # Admin
    "DashboardStatsService",
    "SystemHealthService",
    "UserManagementService",
    "TournamentAdminService",

    # Auth
    "AuthenticationService",
    "ProfileLinkingService",
    "ProfileCreationService",

    # Roles (Beta)
    "RoleRequestService",
    "SystemSettingsService",

    # Tournament
    "TournamentConfigService",
    "TournamentPricingService",
    "TournamentRegistrationRulesService",
    "TournamentRulebookService",
    "StandingsService",

    # Round
    "RoundLifecycleService",
    "PairingGenerationService",
    "ResultRecordingService",
    "ManualAdjustmentService",
    "StatsRebuildService",
    "RoundNotificationService",
    "RoundDisplayService",

    # Registration
    "RegistrationCreator",
    "EligibilityChecker",
    "PricingCalculator",
    "RegistrationApprover",
    "ReceiptHandler",

    # Player
    "ParticipantManagement",
    "PlayerCsvImportService",
    "CsvImportError",

    # Dashboard
    "DashboardAvailabilityService",

    # Verification
    "VerificationRequestService",
    "VerificationApprover",
    "VerificationStatusUpdater",

    # FIDE
    "FideImportOrchestrator",
    "FideSearchService",

    # Import/Export
    "ExportService",
    "ImportService",
    "PreviewService",

    # Prize
    "PrizeDefinitionService",
    "PrizeAllocationService",
    "PrizeSummaryService",

    # Payment
    "PaymentInitiator",

    # Telegram/Bale
    "TelegramService",
    "TelegramLinkService",
    "BaleService",
    "BaleLinkService",

    # Notification
    "NotificationDispatcher",
    "NotificationService",
    "load_tournament_prefs",
    "tournament_allows",
    "serialize_tournament_prefs",
    "NotificationType",
    "FutureNotificationType",
    "NOTIFICATION_TYPE_NAMES_FA",
    "TOURNAMENT_EVENT_TYPES",
    "NotificationProviderInterface",

    # Payment Gateway
    "PaymentGatewayInterface",
    "PaymentRequestResult",
    "PaymentVerifyResult",

    # Import/Export
    "ImportProvider",
    "ExportProvider",
    "PlayerImportExportData",
    "PairingImportExportData",
    "TournamentData",
    "BackupFileData",
    "TournamentPreviewData",

    # Provider Registry
    "ProviderRegistry",
    "registry",

    # Providers
    "CoronateProvider",
    "parse_coronate_json",
    "CoronateFormatError",
    "generate_coronate_json",
    "WebProvider",
    "TelegramProvider",
    "BaleProvider",
]
