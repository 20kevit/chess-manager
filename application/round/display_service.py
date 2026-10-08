"""
Round Display Service.

Provides formatting and display logic for round results, crosstables,
and score representations. This is pure presentation logic extracted
from the web layer.
"""
from typing import Dict, Optional, Any


_SCORE_MAP = {
    "1-0": {"white": "+", "black": "-"},
    "0-1": {"white": "-", "black": "+"},
    "1/2": {"white": "=", "black": "="},
    "+/-": {"white": "+", "black": "-"},
    "-/+": {"white": "-", "black": "+"},
    "+/+": {"white": "-", "black": "-"},
}

_SCORE_VALUES = {
    "1-0": {"white": 1.0, "black": 0.0},
    "0-1": {"white": 0.0, "black": 1.0},
    "1/2": {"white": 0.5, "black": 0.5},
    "+/-": {"white": 1.0, "black": 0.0},
    "-/+": {"white": 0.0, "black": 1.0},
    "+/+": {"white": 0.0, "black": 0.0},
    "bye": {"white": 1.0, "black": None},
    "half-bye": {"white": 0.5, "black": None},
    "zero-bye": {"white": 0.0, "black": None},
}

_TRF_RESULT_MAP = {
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

_BYE_DISPLAY = {
    "bye": {"text": "BYE", "css": "cell-bye", "symbol": "+", "score": 1.0},
    "half-bye": {"text": "\u00bdBY", "css": "cell-half-bye", "symbol": "=", "score": 0.5},
    "zero-bye": {"text": "0BY", "css": "cell-zero-bye", "symbol": "-", "score": 0.0},
}


class RoundDisplayService:
    """Formatting and display logic for round results and crosstables."""

    @staticmethod
    def get_score_symbol(result: str, color: str) -> str:
        """Get the display symbol (+, -, =) for a result and color."""
        return _SCORE_MAP.get(result, {}).get(color, "")

    @staticmethod
    def get_score_value(result: str, color: str) -> Optional[float]:
        """Get the numeric score value (1.0, 0.5, 0.0) for a result and color."""
        return _SCORE_VALUES.get(result, {}).get(color)

    @staticmethod
    def get_trf_result(result: str, color: str) -> str:
        """Get the TRF format result character for a result and color."""
        return _TRF_RESULT_MAP.get(result, {}).get(color, "Z")

    @staticmethod
    def build_crosstable_cell(
        result: str,
        color: str,
        opponent_id: Optional[int],
        participants_map: Dict[int, Any]
    ) -> Dict:
        """
        Build a crosstable cell dictionary for template rendering.

        Args:
            result: The pairing result string
            color: "white" or "black"
            opponent_id: The opponent's participant ID
            participants_map: Map of participant_id -> ParticipantModel

        Returns:
            Dict with keys: text, css, symbol, score, opponent_id, opponent_num, color
        """
        if result in ("bye", "half-bye", "zero-bye"):
            return _BYE_DISPLAY[result].copy()

        if result not in _SCORE_MAP:
            return {"text": "-", "css": "cell-pending", "symbol": "", "score": None,
                    "opponent_id": opponent_id, "opponent_num": "?", "color": "W" if color == "white" else "B"}

        symbol = _SCORE_MAP[result][color]
        opponent = participants_map.get(opponent_id)
        opp_num = opponent.start_number if opponent else "?"

        color_short = "W" if color == "white" else "B"
        if symbol == "+":
            css = "cell-win"
        elif symbol == "=":
            css = "cell-draw"
        else:
            css = "cell-loss"

        score = 1.0 if symbol == "+" else (0.5 if symbol == "=" else 0.0)

        return {
            "text": f"{symbol}{opp_num}{color_short}",
            "css": css,
            "symbol": symbol,
            "opponent_id": opponent_id,
            "opponent_num": opp_num,
            "color": color_short,
            "score": score,
        }

    @staticmethod
    def get_bye_display(result: str) -> Dict:
        """Get display info for bye results."""
        return _BYE_DISPLAY.get(result, {}).copy()

    @staticmethod
    def count_pending_results(pairings) -> int:
        """Count board pairings still awaiting a recorded result.

        Only real boards count: bye/absent boards (no black player) are
        excluded, as are boards with any recorded result. An empty result
        ("" / None / legacy "pending") on a real board means unplayed.
        """
        pending = 0
        for pairing in pairings:
            if pairing.black_participant_id is None:
                continue
            result = pairing.result or ""
            if result.strip() in ("", "pending"):
                pending += 1
        return pending

    @staticmethod
    def describe_round_status(status: str, pending_count: int = 0) -> Dict:
        """Public-facing round status: label + badge class.

        Derives display text from the round lifecycle status plus the real
        pending-result count — no extra database state is introduced.
        """
        if status == "finished":
            return {"label": "برگزار شد", "badge": "badge-success"}
        if status == "ongoing":
            if pending_count > 0:
                return {
                    "label": f"در حال برگزاری · هنوز {pending_count} نتیجه ثبت نشده",
                    "badge": "badge-info",
                }
            return {"label": "در حال برگزاری", "badge": "badge-info"}
        return {"label": "برگزار نشده", "badge": "badge-neutral"}