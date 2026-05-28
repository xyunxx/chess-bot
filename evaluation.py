"""Your evaluation function.

``evaluate(board)`` returns a centipawn score for the given position, from
White's point of view: positive means White is winning, negative means
Black is winning, zero means the position is even. Your bot calls this
function from ``bot.py`` to compare candidate moves; Phase 5's search code
will call it at the leaves of its lookahead tree.

Phase 4 builds this up incrementally: material counting, piece-square
tables, mobility, and any extra features you want to add for personality.
The kit ships canonical starting values for piece values and PSTs in
``chessdk`` that you may import and tune.
"""

from __future__ import annotations

from board import Board

from chessdk import MATE_SCORE, WHITE, PIECE_VALUE_KAUFMAN


def evaluate(board: Board) -> int:
    """Return a centipawn score for the position from White's point of view."""
    if board.legal_moves() == []:
        if board.is_in_check():  # checkmate
            return -MATE_SCORE if board.side_to_move == WHITE else MATE_SCORE
        else:  # stalemate
            return 0

    e = 0
    for p in board.pieces:
        if p is not None:
            if p.color == WHITE:
                e += PIECE_VALUE_KAUFMAN[p.kind]
            else:
                e -= PIECE_VALUE_KAUFMAN[p.kind]
    return e
