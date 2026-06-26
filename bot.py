"""Your bot.

For Week 1, you don't need to fill this in — we aren't ready to play yet. We
come back to this in Week 3 when we integrate UCI and submit to the tournament.
"""

from __future__ import annotations

from board import Board
from chessdk import Move, MATE_SCORE
from evaluation import evaluate_fast
from search import search_iterative, quiesce


def choose_move(board: Board, time_left_ms: int) -> Move:
    """Return the move your bot wants to play, given the current board.

    `time_left_ms` is how many milliseconds you have remaining in the match.
    For Week 1 this function is unused; later weeks replace it with real logic.
    """
    print("time left: ", time_left_ms)
    budget = time_left_ms // 30 - 100
    budget = 100 if budget <= 100 else budget

    def quiescent_eval(board):
        return quiesce(board, -MATE_SCORE, MATE_SCORE, evaluate_fast)

    return search_iterative(board, quiescent_eval, 5, budget)[1]
