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

from chessdk import (
    MATE_SCORE,
    WHITE,
    PIECE_VALUE_KAUFMAN,
    DEFAULT_PSTS,
    PAWN,
    KING,
    sq,
    file_of,
    rank_of,
    DEFAULT_MOBILITY_WEIGHT,
    BLACK,
)


def evaluate(board: Board) -> int:
    """Return a centipawn score for the position from White's point of view."""
    side = board.side_to_move
    if board.legal_moves() == []:
        if board.is_in_check():  # checkmate
            return -MATE_SCORE if side == WHITE else MATE_SCORE
        else:  # stalemate
            return 0

    e = 0
    pst = 0
    for n, p in enumerate(board.pieces):
        if p is not None:
            piece = p.kind
            if p.color == WHITE:
                e += PIECE_VALUE_KAUFMAN[piece]
                pst += DEFAULT_PSTS[piece][n]
            else:
                e -= PIECE_VALUE_KAUFMAN[piece]
                pst -= DEFAULT_PSTS[piece][sq(file_of(n), 7 - rank_of(n))]

    try:
        if side == WHITE:
            w = len(board.legal_moves())
        else:
            b = len(board.legal_moves())
        board.state.side_to_move = side.other
        if board.side_to_move == BLACK:
            b = len(board.legal_moves())
        else:
            w = len(board.legal_moves())
    finally:
        board.state.side_to_move = side

    return e + pst + (w - b) * DEFAULT_MOBILITY_WEIGHT
