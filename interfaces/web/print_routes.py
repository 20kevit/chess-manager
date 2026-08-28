"""
Print-friendly pages for PDF export.
"""
from flask import Blueprint, render_template, abort, Response

from application.tournament_service import TournamentService

from infrastructure.models.tournament import RoundModel
from infrastructure.repositories.participant import ParticipantRepository
from infrastructure.repositories.tournament import (PairingRepository, TournamentRepository)
print_bp = Blueprint("print", __name__)

def _validate_public_id(public_id):
    if not public_id.isdigit() or len(public_id) != 8:
        abort(404)

@print_bp.route("/<public_id>/print/standings")
def print_standings(public_id):
    _validate_public_id(public_id)
    tournament = TournamentRepository.get_by_public_id(public_id)
    if not tournament:
        abort(404)

    standings = TournamentService.get_standings(tournament)

    return render_template(
        "print/standings.html",
        tournament=tournament,
        **standings,
    )

@print_bp.route("/<public_id>/print/round/<int:round_number>")
def print_round(public_id, round_number):
    _validate_public_id(public_id)
    tournament = TournamentRepository.get_by_public_id(public_id)
    if not tournament:
        abort(404)

    round_obj = RoundModel.query.filter_by(
        tournament_id=tournament.id,
        round_number=round_number,
    ).first()
    if not round_obj:
        abort(404)

    pairings = PairingRepository.get_all_for_round(round_obj.id)
    participants = {p.id: p for p in ParticipantRepository.get_all(tournament.id)}

    return render_template(
        "print/round.html",
        tournament=tournament,
        round=round_obj,
        pairings=pairings,
        players=participants,
    )

@print_bp.route("/<public_id>/print/crosstable")
def print_crosstable(public_id):
    _validate_public_id(public_id)
    tournament = TournamentRepository.get_by_public_id(public_id)
    if not tournament:
        abort(404)

    participants = ParticipantRepository.get_all(tournament.id)
    all_pairings = PairingRepository.get_all_for_tournament(tournament.id)
    rounds = RoundModel.query.filter_by(
        tournament_id=tournament.id
    ).order_by(RoundModel.round_number).all()

    round_map = {r.id: r.round_number for r in rounds}
    participants_map = {p.id: p for p in participants}
    total_rounds = tournament.current_round or 0

    from interfaces.web.helpers import build_cell as _build_cell

    cross_data = {}
    for p in participants:
        cross_data[p.id] = {"player": p, "rounds": {}}

    for pairing in all_pairings:
        round_num = round_map.get(pairing.round_id)
        if not round_num:
            continue
        w_id = pairing.white_participant_id
        b_id = pairing.black_participant_id

        if w_id and w_id in cross_data:
            cross_data[w_id]["rounds"][round_num] = _build_cell(
                pairing.result, "white", b_id, participants_map
            )
        if b_id and b_id in cross_data:
            cross_data[b_id]["rounds"][round_num] = _build_cell(
                pairing.result, "black", w_id, participants_map
            )

    sorted_players = sorted(
        cross_data.values(),
        key=lambda x: (-(x["player"].points or 0), -(x["player"].rating_snapshot or 0))
    )

    return render_template(
        "print/crosstable.html",
        tournament=tournament,
        sorted_players=sorted_players,
        total_rounds=total_rounds,
    )

@print_bp.route("/<public_id>/export/trf")
def export_trf(public_id):
    """خروجی فرمت TRF فیده"""
    _validate_public_id(public_id)
    tournament = TournamentRepository.get_by_public_id(public_id)
    if not tournament:
        abort(404)

    participants = ParticipantRepository.get_all(tournament.id)
    all_pairings = PairingRepository.get_all_for_tournament(tournament.id)
    rounds = RoundModel.query.filter_by(
        tournament_id=tournament.id
    ).order_by(RoundModel.round_number).all()

    round_map = {r.id: r.round_number for r in rounds}
    participants_map = {p.id: p for p in participants}

    lines = []

    # Header
    lines.append(f"012 {tournament.name}")
    lines.append(f"022 {tournament.city or ''}")
    lines.append(f"032 {tournament.federation or 'IRI'}")
    lines.append(f"042 {tournament.start_date or ''}")
    lines.append(f"052 {tournament.end_date or ''}")
    lines.append(f"062 {len(participants)}")
    lines.append(f"072 {len(participants)}")
    lines.append(f"082 {tournament.current_round}")
    lines.append(f"092 {tournament.time_control_type}")

    tc_map = {"standard": "1", "rapid": "2", "blitz": "3"}
    lines.append(f"102 {tournament.chief_arbiter or ''}")
    lines.append(f"112 {tournament.arbiter or ''}")
    lines.append(f"122 {tournament.time_control_description or ''}")

    # Participants
    sorted_participants = sorted(participants, key=lambda p: p.start_number)

    for participant in sorted_participants:
        # Build round results
        round_results = {}
        for pairing in all_pairings:
            rn = round_map.get(pairing.round_id)
            if not rn:
                continue

            if pairing.white_participant_id == participant.id:
                opp = participants_map.get(pairing.black_participant_id)
                opp_num = opp.start_number if opp else 0
                color = "w"
                result = _trf_result(pairing.result, "white")
                round_results[rn] = f"  {opp_num:4d} {color} {result}"
            elif pairing.black_participant_id == participant.id:
                opp = participants_map.get(pairing.white_participant_id)
                opp_num = opp.start_number if opp else 0
                color = "b"
                result = _trf_result(pairing.result, "black")
                round_results[rn] = f"  {opp_num:4d} {color} {result}"

        # Format player line using participant data and profile
        profile = participant.profile
        sex = "m" if profile.gender == "M" else "w"
        title = participant.fide_title_snapshot or ""
        name = f"{profile.last_name}, {profile.first_name}"
        rating = participant.rating_snapshot or 0
        fide_id = profile.fide_id or ""
        birth = ""
        if profile.birth_date:
            birth = profile.birth_date.strftime("%Y/%m/%d")
        points = participant.points or 0

        # TRF line
        line = f"001 {participant.start_number:4d}"
        line += f" {sex:1s}"
        line += f" {title:3s}"
        line += f" {name:33s}"
        line += f" {rating:4d}"
        line += f" {profile.federation or 'IRI':3s}"
        line += f" {fide_id:11s}"
        line += f" {birth:10s}"
        line += f" {points:4.1f}"
        line += f"   "

        for rn in range(1, tournament.current_round + 1):
            if rn in round_results:
                line += round_results[rn]
            else:
                line += "  0000 - Z"

        lines.append(line)

    trf_content = "\n".join(lines)

    response = Response(
        trf_content,
        mimetype="text/plain",
        headers={
            "Content-Disposition": f"attachment; filename={tournament.public_id}.trf"
        }
    )
    return response

def _trf_result(result, color):
    mapping = {
        "1-0": {"white": "1", "black": "0"},
        "0-1": {"white": "0", "black": "1"},
        "1/2": {"white": "=", "black": "="},
        "+/-": {"white": "+", "black": "-"},
        "-/+": {"white": "-", "black": "+"},
        "+/+": {"white": "-", "black": "-"},
        "bye": {"white": "U", "black": "U"},
        "half-bye": {"white": "H", "black": "H"},
        "zero-bye": {"white": "Z", "black": "Z"},
    }
    if result in mapping:
        return mapping[result].get(color, "Z")
    return "Z"