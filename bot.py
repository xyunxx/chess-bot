"""Your bot.

For Week 1, you don't need to fill this in — we aren't ready to play yet. We
come back to this in Week 3 when we integrate UCI and submit to the tournament.
"""

from __future__ import annotations

import random
from board import Board
from chessdk import Move
from chessdk.evaluation import PIECE_VALUE


def choose_move(board: Board, time_left_ms: int) -> Move:
    """Return the move your bot wants to play, given the current board.

    `time_left_ms` is how many milliseconds you have remaining in the match.
    For Week 1 this function is unused; later weeks replace it with real logic.
    """
    moves = board.legal_moves()
    captures = [m for m in moves if board.piece_at(m.to_sq) is not None]
    if captures:
        m = None
        for i in range(len(captures)):
            score = (
                PIECE_VALUE[board.piece_at(captures[i].to_sq).kind]
                - PIECE_VALUE[board.piece_at(captures[i].from_sq).kind]
            )
            m = i if m is None or score > m else m
        return captures[m]
    return random.choice(moves)


# Note will occationally crash, once was an illegal move and most other times is saying None has no attribute Kind
