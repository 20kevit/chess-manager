"""Shared view helpers for route modules."""

_SCORE_MAP = {
    "1-0": {"white": "+", "black": "-"},
    "0-1": {"white": "-", "black": "+"},
    "1/2": {"white": "=", "black": "="},
    "+/-": {"white": "+", "black": "-"},
    "-/+": {"white": "-", "black": "+"},
    "+/+": {"white": "-", "black": "-"},
}

def build_cell(result, color, opponent_id, participants_map):
    """Builds a cell for the crosstable. Uses participants_map."""
    if result in ("bye", "half-bye", "zero-bye"):
        if result == "bye":
            return {"text": "BYE", "css": "cell-bye", "symbol": "+", "score": 1.0}
        elif result == "half-bye":
            return {"text": "½BY", "css": "cell-half-bye", "symbol": "=", "score": 0.5}
        else:
            return {"text": "0BY", "css": "cell-zero-bye", "symbol": "-", "score": 0.0}

    if result not in _SCORE_MAP:
        return {"text": "-", "css": "cell-pending", "symbol": "", "score": None}

    symbol = _SCORE_MAP[result][color]
    opponent = participants_map.get(opponent_id)
    # Use start_number or pairing_no for display
    opp_num = opponent.start_number if opponent else "?"

    color_short = "W" if color == "white" else "B"
    if symbol == "+":
        css = "cell-win"
    elif symbol == "=":
        css = "cell-draw"
    else:
        css = "cell-loss"

    return {
        "text": f"{symbol}{opp_num}{color_short}",
        "css": css,
        "symbol": symbol,
        "opponent_id": opponent_id,
        "opponent_num": opp_num,
        "color": color_short,
        "score": 1.0 if symbol == "+" else (0.5 if symbol == "=" else 0.0),
    }