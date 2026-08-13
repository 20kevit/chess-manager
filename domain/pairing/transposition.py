"""
Systematic transposition generator — FIDE C.04.3.

This module generates all legal transpositions of S2 in the exact
order required by the FIDE Dutch system.

FIDE C.04.3 Transposition Rules:
    1. A transposition is a permutation of the players in S2.
       S1 remains fixed.

    2. Transpositions are tried in LEXICOGRAPHIC ORDER based on
       the pairing numbers of the S2 players.

    3. The first transposition is the identity (original S2 order).

    4. Each subsequent transposition is the next permutation in
       lexicographic order of the S2 pairing numbers.

    5. All n! transpositions are tried before moving to exchanges.

    6. For each transposition, the pairing is S1[i] vs S2_transposed[i].

Example with S2 = [pno=5, pno=7, pno=9]:
    Transposition 0: [5, 7, 9]  (identity)
    Transposition 1: [5, 9, 7]
    Transposition 2: [7, 5, 9]
    Transposition 3: [7, 9, 5]
    Transposition 4: [9, 5, 7]
    Transposition 5: [9, 7, 5]

This is exactly the standard lexicographic permutation sequence.

Performance note:
    For S2 of size n, there are n! transpositions.
    n=8  →      40,320
    n=9  →     362,880
    n=10 → 3,628,800

    For brackets larger than MAX_S2_SIZE, the engine should split
    the bracket before reaching this module (handled by engine.py).

This module is stateless and deterministic. Zero external dependencies.
"""
from typing import Generator, List

from domain.pairing.models import EnginePlayer


# ═══════════════════════════════════════════════════════════════════
#  Constants
# ═══════════════════════════════════════════════════════════════════

# Maximum S2 size for exhaustive transposition search.
# Beyond this, the search space becomes too large.
# The engine must split the bracket before calling this module.
MAX_S2_SIZE = 10


# ═══════════════════════════════════════════════════════════════════
#  Public API
# ═══════════════════════════════════════════════════════════════════

def generate_transpositions(
    s2: List[EnginePlayer],
) -> Generator[List[EnginePlayer], None, None]:
    """
    Generate all transpositions of S2 in FIDE lexicographic order.

    The first yielded value is always the identity (original order).
    Subsequent values follow the next-permutation algorithm.

    Args:
        s2: The S2 half of the bracket, sorted by pairing number.

    Yields:
        Each transposition as a list of EnginePlayer in the
        transposed order.

    Raises:
        ValueError: If S2 is larger than MAX_S2_SIZE.
    """
    n = len(s2)

    if n == 0:
        yield []
        return

    if n == 1:
        yield list(s2)
        return

    if n > MAX_S2_SIZE:
        raise ValueError(
            f"S2 size {n} exceeds maximum {MAX_S2_SIZE}. "
            f"The bracket must be split before transposition generation."
        )

    # Generate permutations of indices in lexicographic order
    for perm_indices in _lexicographic_permutations(n):
        yield [s2[i] for i in perm_indices]


def transposition_count(n: int) -> int:
    """
    Return the number of transpositions for S2 of size n.
    This is simply n! (n factorial).
    """
    return _factorial(n)


def is_identity(
    original: List[EnginePlayer],
    transposed: List[EnginePlayer],
) -> bool:
    """
    Check if a transposition is the identity (same as original order).
    """
    if len(original) != len(transposed):
        return False
    return all(
        original[i].id == transposed[i].id
        for i in range(len(original))
    )


# ═══════════════════════════════════════════════════════════════════
#  Lexicographic Permutation Generator
# ═══════════════════════════════════════════════════════════════════

def _lexicographic_permutations(
    n: int,
) -> Generator[List[int], None, None]:
    """
    Generate all permutations of [0, 1, ..., n-1] in lexicographic order.

    Uses the standard "next permutation" algorithm:
        1. Start with sorted sequence [0, 1, ..., n-1]
        2. Find the rightmost element that is smaller than its successor
        3. Swap it with the smallest element to its right that is larger
        4. Reverse the suffix after the swap position
        5. Repeat until no more permutations exist

    This produces all n! permutations in exactly the order FIDE requires.

    Yields:
        Lists of integers representing index permutations.
    """
    if n == 0:
        yield []
        return

    if n == 1:
        yield [0]
        return

    # Start with identity permutation
    current = list(range(n))
    yield list(current)

    while True:
        # Step 1: Find rightmost i such that current[i] < current[i+1]
        i = n - 2
        while i >= 0 and current[i] >= current[i + 1]:
            i -= 1

        if i < 0:
            # No more permutations — all are exhausted
            return

        # Step 2: Find rightmost j > i such that current[j] > current[i]
        j = n - 1
        while current[j] <= current[i]:
            j -= 1

        # Step 3: Swap current[i] and current[j]
        current[i], current[j] = current[j], current[i]

        # Step 4: Reverse the suffix starting at current[i+1]
        left = i + 1
        right = n - 1
        while left < right:
            current[left], current[right] = current[right], current[left]
            left += 1
            right -= 1

        yield list(current)


# ═══════════════════════════════════════════════════════════════════
#  Utility
# ═══════════════════════════════════════════════════════════════════

def _factorial(n: int) -> int:
    """Compute n! iteratively."""
    if n <= 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result