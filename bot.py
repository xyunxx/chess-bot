"""Your bot.

For Week 1, you don't need to fill this in — we aren't ready to play yet. We
come back to this in Week 3 when we integrate UCI and submit to the tournament.
"""

from __future__ import annotations

import random
from board import Board
from chessdk import Move, PIECE_VALUE, min_attacker_value, PAWN, WHITE, BLACK
from evaluation import evaluate


def choose_move(board: Board, time_left_ms: int) -> Move:
    """Return the move your bot wants to play, given the current board.

    `time_left_ms` is how many milliseconds you have remaining in the match.
    For Week 1 this function is unused; later weeks replace it with real logic.
    """
    moves = board.legal_moves()
    side = board.side_to_move
    mscore = None
    tied_scores = []
    for i in range(len(moves)):
        board.make_move(moves[i])
        pos_score = evaluate(board)
        if (
            min_attacker_value(board, moves[i].to_sq, side) is None
            or min_attacker_value(board, moves[i].to_sq, side)
            >= PIECE_VALUE[board.piece_at(moves[i].to_sq).kind]
        ):
            hang = 0
        else:
            if moves[i].promotion is not None:
                hang = PIECE_VALUE[PAWN]
            else:
                hang = PIECE_VALUE[board.piece_at(moves[i].to_sq).kind]
        board.undo_move()
        sign = 1 if side == WHITE else -1
        score = pos_score - sign * hang
        if (
            mscore is None
            or (side == WHITE and score > mscore)
            or (side == BLACK and score < mscore)
        ):
            mscore = score
            tied_scores = []
            tied_scores.append(i)
        elif score == mscore:
            tied_scores.append(i)

    return moves[random.choice(tied_scores)]
