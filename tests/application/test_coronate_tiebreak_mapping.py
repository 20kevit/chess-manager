"""Coronate tie-break mapping — Phase 0 vocabulary pins.

The Coronate interchange carries its own tie-break names; the parser must
translate them into tiebreak-core registry ids (or leave them unmapped so
a future consumer fails closed). Parsed tiebreaks are currently dropped at
import (defaults applied), so these pins guard vocabulary, not standings.
"""
import json

from infrastructure.providers.coronate_parser import parse_coronate_json


def _coronate_doc(tiebreaks):
    return json.dumps({
        "players": {
            "p1": {"firstName": "A", "lastName": "B", "rating": 1500},
            "p2": {"firstName": "C", "lastName": "D", "rating": 1500},
        },
        "tournaments": {
            "t1": {
                "name": "T",
                "playerIds": ["p1", "p2"],
                "roundList": [[{
                    "whiteId": "p1", "blackId": "p2",
                    "whiteOrigRating": 1500, "blackOrigRating": 1500,
                    "result": "whiteWon",
                }]],
                "tieBreaks": tiebreaks,
            }
        },
    })


class TestCoronateTiebreakMapping:
    def test_exact_mappings_use_registry_ids(self):
        from tiebreak_core import is_known
        data = parse_coronate_json(_coronate_doc(
            ["median", "solkoff", "cumulative"]))
        assert data.tournaments[0].tiebreaks == [
            "median_buchholz", "buchholz", "progressive"]
        for tid in data.tournaments[0].tiebreaks:
            assert is_known(tid), tid

    def test_no_exact_equivalent_passes_through(self):
        # cumulativeOfOpposition has no tiebreak-core equivalent: it must
        # NOT be silently rewritten to a different system.
        data = parse_coronate_json(_coronate_doc(["cumulativeOfOpposition"]))
        assert data.tournaments[0].tiebreaks == ["cumulativeOfOpposition"]

    def test_unknown_names_pass_through(self):
        data = parse_coronate_json(_coronate_doc(["drawingOfLots"]))
        assert data.tournaments[0].tiebreaks == ["drawingOfLots"]
