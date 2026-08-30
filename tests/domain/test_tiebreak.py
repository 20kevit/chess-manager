"""Tiebreak calculators — domain/tiebreak/calculators.py"""
import pytest
from domain.tiebreak.calculators import (
    buchholz, buchholz_cut1, buchholz_cut2, median_buchholz,
    sonneborn_berger, progressive, wins_count, wins_with_black,
    games_with_black, average_rating_opponents, koya, direct_encounter,
    buchholz_sum, arpo, calculate_all, ALL_TIEBREAKS, TIEBREAK_REGISTRY
)
from domain.tiebreak.models import PlayerTiebreakData, GameRecord

def rec(opp, score, color='white', rnd=1, opp_rating=1500):
    return GameRecord(opponent_id=opp, opponent_rating=opp_rating, score=score, color=color, round_number=rnd)

def pdata(pid, rating, points, games, wins_bb=None):
    return PlayerTiebreakData(player_id=pid, rating=rating, points=points, games=games)

# Helper to create 4-player round robin after 3 rounds
def four_player_fixture():
    # ratings and points
    # P1: 2.5 vs 2(1),3(0.5),4(1)
    # P2: 1.5 vs 1(0),3(1),4(0.5)
    # P3: 1.0 vs etc
    # Use simple full data
    p1 = pdata(1, 2000, 2.5, [rec(2,1,rnd=1), rec(3,0.5,rnd=2), rec(4,1,rnd=3)])
    p2 = pdata(2, 1900, 1.0, [rec(1,0,rnd=1), rec(3,0.5,rnd=2), rec(4,0.5,rnd=3)])
    p3 = pdata(3, 1800, 1.5, [rec(1,0.5,rnd=1), rec(2,0.5,rnd=2), rec(4,0.5,rnd=3)])
    p4 = pdata(4, 1700, 1.0, [rec(1,0,rnd=1), rec(2,0.5,rnd=2), rec(3,0.5,rnd=3)])
    allp = {1:p1,2:p2,3:p3,4:p4}
    return p1,p2,p3,p4,allp

class TestBuchholzFamily:
    def test_buchholz_basic(self):
        p1,p2,p3,p4,allp = four_player_fixture()
        # p1 opps: p2(1),p3(1.5),p4(1) => sum 3.5
        assert buchholz(p1, allp) == pytest.approx(3.5)
        # p2 opps: p1(2.5),p3(1.5),p4(1) => 5.0
        assert buchholz(p2, allp) == pytest.approx(5.0)

    def test_buchholz_cut1(self):
        p1,p2,p3,p4,allp = four_player_fixture()
        # p1: scores [1,1.5,1] -> total 3.5 - min 1 =2.5
        assert buchholz_cut1(p1, allp) == pytest.approx(2.5)
        # single game: cut1 should not cut
        p = pdata(10,1500,1.0,[rec(2,1)])
        ap = {2: pdata(2,1600,1.0,[]), 10:p}
        assert buchholz_cut1(p, ap) == pytest.approx(1.0)

    def test_buchholz_cut2(self):
        p1,p2,p3,p4,allp = four_player_fixture()
        # p2: scores [2.5,1.5,1] sorted => total 5 -0.9? let's compute: cut2 remove 2 lowest: 1 and 1.5 => 2.5
        assert buchholz_cut2(p2, allp) == pytest.approx(2.5)
        # two games: cut2 should remove only 1 (min(len-1,2))
        p = pdata(10,1500,1.0,[rec(2,1), rec(3,0.5)])
        ap = {2:pdata(2,1600,0.5,[]),3:pdata(3,1600,1.0,[]),10:p}
        # scores 0.5,1.0 => total 1.5 -0.5 =1.0
        assert buchholz_cut2(p, ap) == pytest.approx(1.0)

    def test_median_buchholz(self):
        p1,p2,p3,p4,allp = four_player_fixture()
        # p1: [1,1.5,1] -> sum 3.5 -1 -1.5=1.0
        assert median_buchholz(p1, allp) == pytest.approx(1.0)
        # <3 games should return buchholz
        p = pdata(10,1500,1.0,[rec(2,1)])
        ap = {2:pdata(2,1600,2.0,[]),10:p}
        assert median_buchholz(p, ap) == buchholz(p, ap)

    def test_buchholz_zero_games(self):
        p = pdata(1,1500,0.0,[])
        assert buchholz(p, {}) == 0.0
        assert buchholz_cut1(p, {}) == 0.0
        assert buchholz_cut2(p, {}) == 0.0
        assert median_buchholz(p, {}) == 0.0

    def test_buchholz_virtual_opponent(self):
        # opponent_id -1 uses points - score
        p = pdata(1,1500,2.0,[rec(-1,1,rnd=1), rec(2,1,rnd=2)])
        allp = {2:pdata(2,1600,1.0,[]),1:p}
        # virtual: max(0, 2-1)=1
        # second: p2 1.0 => total 2.0
        assert buchholz(p, allp) == pytest.approx(2.0)

    def test_buchholz_sum(self):
        p1,p2,p3,p4,allp = four_player_fixture()
        # p1 buchholz_sum = sum buchholz of opps 2,3,4
        b2 = buchholz(p2, allp)
        b3 = buchholz(p3, allp)
        b4 = buchholz(p4, allp)
        assert buchholz_sum(p1, allp) == pytest.approx(round(b2+b3+b4,1))

class TestSonnebornBerger:
    def test_sonneborn_basic(self):
        p1,p2,p3,p4,allp = four_player_fixture()
        # p1: 1*1 (p2=1) +0.5*1.5+1*1 =1+0.75+1=2.75
        assert sonneborn_berger(p1, allp) == pytest.approx(2.75)
        # p3: 0.5*2.5+0.5*1+0.5*1 =1.25+0.5+0.5=2.25
        assert sonneborn_berger(p3, allp) == pytest.approx(2.25)

    def test_sonneborn_virtual_opponent(self):
        p = pdata(1,1500,1.5,[rec(-1,1,rnd=1), rec(2,0.5,rnd=2)])
        allp = {2:pdata(2,1600,1.0,[]),1:p}
        # virtual 1* (1.5-1=0.5)=0.5 ; 0.5*1=0.5 =>1.0
        assert sonneborn_berger(p, allp) == pytest.approx(1.0)

    def test_sonneborn_zero(self):
        p = pdata(1,1500,0.0,[])
        assert sonneborn_berger(p,{}) == 0.0

class TestProgressive:
    def test_progressive_cumulative(self):
        p = pdata(1,1500,2.0,[rec(2,1,rnd=1), rec(3,0.5,rnd=2), rec(4,0.5,rnd=3)])
        # cumulative: 1,1.5,2.0 => sum 4.5
        assert progressive(p,{}) == pytest.approx(4.5)

    def test_progressive_unsorted(self):
        p = pdata(1,1500,2.0,[rec(4,0.5,rnd=3), rec(2,1,rnd=1), rec(3,0.5,rnd=2)])
        assert progressive(p,{}) == pytest.approx(4.5)

    def test_progressive_zero(self):
        p = pdata(1,1500,0.0,[])
        assert progressive(p,{}) == 0.0

class TestWinsAndBlack:
    def test_wins_count(self):
        p = pdata(1,1500,2.0,[rec(2,1), rec(3,1), rec(4,0.5)])
        assert wins_count(p,{}) == 2.0
        p0 = pdata(2,1500,0.0,[rec(1,0),rec(3,0)])
        assert wins_count(p0,{}) == 0.0

    def test_wins_with_black(self):
        p = pdata(1,1500,2.0,[rec(2,1,color='black'), rec(3,1,color='white'), rec(4,0.5,color='black')])
        assert wins_with_black(p,{}) == 1.0

    def test_games_with_black(self):
        p = pdata(1,1500,1.0,[rec(2,1,color='black'), rec(3,0,color='black'), rec(4,0.5,color='white')])
        assert games_with_black(p,{}) == 2.0

class TestAROKoyaArpo:
    def test_aro_average(self):
        p1,p2,p3,p4,allp = four_player_fixture()
        # p1 opps ratings 1900,1800,1700 avg 1800
        assert average_rating_opponents(p1, allp) == 1800

    def test_aro_ignores_zero_rating(self):
        p = pdata(1,1500,1.0,[rec(2,1,opp_rating=0), rec(3,1,opp_rating=1600)])
        allp = {2:pdata(2,0,0,[]),3:pdata(3,1600,0,[]),1:p}
        assert average_rating_opponents(p, allp) == 1600

    def test_aro_virtual(self):
        p = pdata(1,1800,1.0,[rec(-1,1,opp_rating=0)])
        assert average_rating_opponents(p,{1:p}) == 1800

    def test_aro_no_games(self):
        p = pdata(1,1500,0.0,[])
        assert average_rating_opponents(p,{}) == 0.0

    def test_koya_half_score(self):
        p1,p2,p3,p4,allp = four_player_fixture()
        # total_rounds 3 => half 1.5
        # p1: vs 2(1.0 <1.5 no),3(1.5>=1.5 yes 0.5),4(1.0 no) =>0.5
        assert koya(p1, allp, total_rounds=3) == pytest.approx(0.5)
        # zero rounds
        assert koya(p1, allp, total_rounds=0) == 0.0

    def test_arpo_basic(self):
        # Minimal arpo: opp with 50% score -> dp 0, perf = avg opp rating
        opp = pdata(2,1600,1.0,[rec(3,0.5,opp_rating=1500), rec(4,0.5,opp_rating=1700)])
        p = pdata(1,1500,1.0,[rec(2,1)])
        allp = {1:p,2:opp,3:pdata(3,1500,0.5,[]),4:pdata(4,1700,0.5,[])}
        # opp avg rating (1500+1700)/2=1600, percentage 0.5 => dp 0, perf 1600 => arpo 1600
        assert arpo(p, allp) == 1600

    def test_arpo_no_data(self):
        p = pdata(1,1500,0.0,[rec(99,1)])
        assert arpo(p,{}) == 0.0

class TestDirectEncounter:
    def test_direct_encounter_hit(self):
        p = pdata(1,1500,1.0,[rec(2,1), rec(3,0.5)])
        allp = {2:pdata(2,1500,0,[])}
        assert direct_encounter(p, allp, opponent_id=2) == 1.0
        assert direct_encounter(p, allp, opponent_id=3) == 0.5
        assert direct_encounter(p, allp, opponent_id=99) == 0.0

class TestRegistry:
    def test_all_tiebreaks_registered(self):
        expected_names = {n for n,_ in ALL_TIEBREAKS}
        # Ensure registry covers at least the non-special ones; koya/direct not in registry
        for name in expected_names:
            if name in ("koya","direct_encounter"):
                continue
            assert name in TIEBREAK_REGISTRY, f"{name} missing"

    def test_calculate_all_dispatch(self):
        p1,p2,p3,p4,allp = four_player_fixture()
        res = calculate_all(p1, allp, ["buchholz","sonneborn_berger","wins","koya","direct_encounter","nonexistent"], total_rounds=3)
        assert "buchholz" in res
        assert "sonneborn_berger" in res
        assert "wins" in res
        assert res["koya"] == koya(p1, allp, total_rounds=3)
        assert res["direct_encounter"] == 0.0
        assert res["nonexistent"] == 0.0

    def test_deterministic(self):
        p1,p2,p3,p4,allp = four_player_fixture()
        r1 = calculate_all(p1, allp, ["buchholz","progressive","aro"], total_rounds=3)
        r2 = calculate_all(p1, allp, ["buchholz","progressive","aro"], total_rounds=3)
        assert r1 == r2
