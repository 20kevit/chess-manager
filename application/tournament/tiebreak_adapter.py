"""
Chess-manager → tiebreak-core adapter (thin mapper).

Owns ONLY the translation from persistence models to tiebreak-core
inputs, per docs/ADAPTER_CHESS_MANAGER.md in tiebreak-core. Calculation
and ranking live in tiebreak-core; persistence, configuration, seeding
and withdrawal filtering stay here in chess-manager.

tiebreak-core must never query the database; this module is the single
place allowed to read TournamentParticipant/Pairing/Round rows for
tie-break purposes.
"""
from tiebreak_core.models import PlayerTiebreakData, GameRecord

RESULT_SCORES = {
    "1-0": (1.0, 0.0), "0-1": (0.0, 1.0),
    "1/2": (0.5, 0.5), "+/-": (1.0, 0.0),
    "-/+": (0.0, 1.0), "+/+": (0.0, 0.0),
    "bye": (1.0, 0.0), "half-bye": (0.5, 0.0), "zero-bye": (0.0, 0.0),
}

UNPLAYED_RESULTS = frozenset(["+/-", "-/+", "+/+", "bye", "half-bye", "zero-bye"])

VIRTUAL_OPPONENT_ID = -1


def build_tiebreak_data(participants, pairings, round_number_map) -> dict:
    """Build {participant_id: PlayerTiebreakData} from DB models.

    Mapping contract (byte-preserving vs legacy StandingsService):
      - rating = rating_snapshot or 0; points = points or 0.0
      - one GameRecord per side present; unplayed results or missing
        opponent slot -> opponent_id=-1 (virtual), score from table above
      - color = the side the player sat ("white"/"black")
      - round_number from round_number_map (default 0)
    """
    participants_map = {p.id: p for p in participants}
    tb_map = {}
    for p in participants:
        tb_map[p.id] = PlayerTiebreakData(
            player_id=p.id,
            rating=p.rating_snapshot or 0,
            points=p.points or 0.0,
        )

    for pairing in pairings:
        if pairing.result not in RESULT_SCORES:
            continue
        w_score, b_score = RESULT_SCORES[pairing.result]
        w_id = pairing.white_participant_id
        b_id = pairing.black_participant_id
        actual_round_number = round_number_map.get(pairing.round_id, 0)
        is_unplayed = pairing.result in UNPLAYED_RESULTS

        if w_id and w_id in tb_map:
            if is_unplayed or not b_id:
                tb_map[w_id].games.append(GameRecord(
                    opponent_id=VIRTUAL_OPPONENT_ID, opponent_rating=0,
                    score=w_score, color="white",
                    round_number=actual_round_number,
                ))
            elif b_id in participants_map:
                b_rating = participants_map[b_id].rating_snapshot or 0
                tb_map[w_id].games.append(GameRecord(
                    opponent_id=b_id, opponent_rating=b_rating,
                    score=w_score, color="white",
                    round_number=actual_round_number,
                ))

        if b_id and b_id in tb_map:
            if is_unplayed or not w_id:
                tb_map[b_id].games.append(GameRecord(
                    opponent_id=VIRTUAL_OPPONENT_ID, opponent_rating=0,
                    score=b_score, color="black",
                    round_number=actual_round_number,
                ))
            elif w_id in participants_map:
                w_rating = participants_map[w_id].rating_snapshot or 0
                tb_map[b_id].games.append(GameRecord(
                    opponent_id=w_id, opponent_rating=w_rating,
                    score=b_score, color="black",
                    round_number=actual_round_number,
                ))

    return tb_map
