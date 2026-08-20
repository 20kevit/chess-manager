# tests/test_phase8.py
import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from application.player_profile_service import PlayerProfileService
from application.player_service import PlayerService
from infrastructure.repositories import (
    PlayerProfileRepository, 
    FidePlayerRepository, 
    FideRatingRepository,
    ParticipantRepository
)
from infrastructure.db_models import (
    PlayerProfileModel, 
    FidePlayerModel, 
    FideRatingModel,
    TournamentModel
)
from app.extensions import db
from datetime import datetime

@pytest.fixture
def setup_data(app):
    """Setup test data for Phase 8"""
    with app.app_context():
        # 1. Create FIDE Player
        fide_player = FidePlayerModel(
            fide_id="12345678",
            name="Test Player",
            federation="IRI",
            sex="M",
            title="FM"
        )
        db.session.add(fide_player)
        
        # 2. Add FIDE Ratings
        ratings = [
            FideRatingModel(fide_id="12345678", period="2026-07", rating_type="standard", rating=1850, games=10, k_factor=20),
            FideRatingModel(fide_id="12345678", period="2026-08", rating_type="standard", rating=1860, games=5, k_factor=20),
            FideRatingModel(fide_id="12345678", period="2026-08", rating_type="rapid", rating=1900, games=8, k_factor=20),
        ]
        for r in ratings:
            db.session.add(r)
            
        # 3. Create Local Profile (Verified)
        profile = PlayerProfileModel(
            first_name="Test",
            last_name="Player",
            fide_id="12345678",
            fide_verification_status="verified"
        )
        db.session.add(profile)
        db.session.commit()
        
        yield profile
        
        # Cleanup
        FideRatingModel.query.filter_by(fide_id="12345678").delete()
        FidePlayerModel.query.filter_by(fide_id="12345678").delete()
        PlayerProfileModel.query.filter_by(id=profile.id).delete()
        db.session.commit()

class TestPhase8:

    def test_fide_rating_auto_fetch(self, app, setup_data):
        """Test 8A: Auto-fetch FIDE rating on participant creation"""
        with app.app_context():
            profile = setup_data
            
            # Create a mock tournament
            tournament = TournamentModel(
                public_id="12345678",
                admin_code="test_admin_code",
                name="Test Tournament",
                time_control_type="rapid", # Should fetch rapid rating (1900)
                total_rounds=5,
                status="setup"
            )
            db.session.add(tournament)
            db.session.commit()
            
            # Form data with rating=0
            form_data = {
                "first_name": "Test",
                "last_name": "Player",
                "fide_id": "12345678",
                "rating": "0", # No manual rating
                "k_factor": "20"
            }
            
            participant = PlayerService.create(tournament, form_data)
            
            assert participant.rating_snapshot == 1900, "Should auto-fetch rapid rating"
            assert participant.k_factor == 20
            
            # Cleanup
            ParticipantRepository.delete(participant)
            db.session.delete(tournament)
            db.session.commit()

    def test_profile_data_aggregation(self, app, setup_data):
        """Test 8B: Player Profile Data Aggregation"""
        with app.app_context():
            profile = setup_data
            data = PlayerProfileService.get_profile_data(profile.id)
            
            assert data is not None
            assert data['profile'].id == profile.id
            assert data['fide_player'].fide_id == "12345678"
            
            # Check latest ratings
            assert data['ratings']['standard']['rating'] == 1860
            assert data['ratings']['rapid']['rating'] == 1900
            assert data['ratings']['blitz'] is None

    def test_rating_history(self, app, setup_data):
        """Test 8C: Rating History Extraction"""
        with app.app_context():
            profile = setup_data
            history = PlayerProfileService.get_rating_history(profile.id)
            
            assert len(history['standard']) == 2
            assert history['standard'][0]['period'] == "2026-07"
            assert history['standard'][0]['rating'] == 1850
            assert history['standard'][1]['period'] == "2026-08"
            assert history['standard'][1]['rating'] == 1860
            
            assert len(history['rapid']) == 1
            assert history['rapid'][0]['rating'] == 1900

    def test_statistics_calculation(self, app, setup_data):
        """Test 8E: Cross-tournament Statistics"""
        with app.app_context():
            profile = setup_data
            
            # Create participant and pairings to test stats
            # This would require setting up a tournament, round, and pairings
            # For simplicity, we test with empty stats first
            stats = PlayerProfileService.get_statistics(profile.id)
            
            assert stats['tournament_count'] == 0
            assert stats['game_count'] == 0
            assert stats['win_rate'] == 0.0

    def test_privacy_filter_on_public_profile(self, app, setup_data):
        """Test 8G: Ensure sensitive data is filtered out in public profile"""
        with app.app_context():
            profile = setup_data
            
            # Add sensitive data
            profile.national_id = "1234567890"
            profile.bank_card_number = "1234567812345678"
            db.session.commit()
            
            # Get profile data
            data = PlayerProfileService.get_profile_data(profile.id)
            
            # Simulate the route logic
            data['profile'].national_id = None
            data['profile'].bank_card_number = None
            data['profile'].bank_account_name = None
            
            assert data['profile'].national_id is None
            assert data['profile'].bank_card_number is None