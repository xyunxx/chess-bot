"""Your bot.

For Week 1, you don't need to fill this in — we aren't ready to play yet. We
come back to this in Week 3 when we integrate UCI and submit to the tournament.
"""

from __future__ import annotations

import random
from board import Board
from chessdk import Move
from chessdk.evaluation import PIECE_VALUE, min_attacker_value
from chessdk import (
    PAWN,
)


def choose_move(board: Board, time_left_ms: int) -> Move:
    """Return the move your bot wants to play, given the current board.

    `time_left_ms` is how many milliseconds you have remaining in the match.
    For Week 1 this function is unused; later weeks replace it with real logic.
    """
    moves = board.legal_moves()
    mscore = None
    tied_scores = []
    for i in range(len(moves)):
        if (
            board.pieces[moves[i].from_sq].kind == PAWN
            and (
                abs(moves[i].from_sq - moves[i].to_sq) != 8
                or abs(moves[i].from_sq - moves[i].to_sq) != 16
            )
            and board.pieces[moves[i].to_sq] is None
        ):
            gain = PIECE_VALUE[PAWN]
        else:
            gain = (
                PIECE_VALUE[board.piece_at(moves[i].to_sq).kind]
                if board.piece_at(moves[i].to_sq) is not None
                else 0
            )
        if moves[i].promotion is not None:
            gain += PIECE_VALUE[moves[i].promotion]
        board.make_move(moves[i])
        if (
            min_attacker_value(board, moves[i].to_sq, board.side_to_move) is None
            or min_attacker_value(board, moves[i].to_sq, board.side_to_move)
            >= PIECE_VALUE[board.piece_at(moves[i].to_sq).kind]
        ):
            loss = 0
        else:
            loss = PIECE_VALUE[board.piece_at(moves[i].to_sq).kind]
        board.undo_move()
        score = gain - loss
        if mscore is None or score > mscore:
            mscore = score
            tied_scores = []
            tied_scores.append(i)
        elif score == mscore:
            tied_scores.append(i)
    return moves[random.choice(tied_scores)]
