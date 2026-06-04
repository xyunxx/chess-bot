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
    BISHOP,
    Piece,
    ROOK,
    Color,
)


def evaluate(board: Board) -> int:
    """Return a centipawn score for the position from White's point of view."""

    def pieces_of_file(file: int, piece=None, color=None) -> list[tuple] | None:
        """Returns (Square, Piece) tuples."""
        if file > 7 or file < 0:
            return ValueError
        fp = []
        for i in range(file, file + 7 * 8 + 1, 8):
            p = board.piece_at(i)
            if not p:
                continue
            if piece is not None and p.kind != piece:
                continue
            if color is not None and p.color != color:
                continue
            fp.append((i, p))
        return fp

    side = board.side_to_move
    if board.legal_moves() == []:
        if board.is_in_check():  # checkmate
            return -MATE_SCORE if side == WHITE else MATE_SCORE
        else:  # stalemate
            return 0

    e = 0
    pst = 0
    passed_bonus_w = [0, 5, 10, 20, 40, 80, 160, 0]
    passed_bonus_b = passed_bonus_w[::-1]
    for n, p in enumerate(board.pieces):
        if p is not None:
            piece = p.kind
            if p.color == WHITE:
                e += PIECE_VALUE_KAUFMAN[piece]
                pst += DEFAULT_PSTS[piece][n]
                if piece == ROOK:
                    file = file_of(n)
                    if not pieces_of_file(file, PAWN):  # open
                        e += 30
                    elif not pieces_of_file(file, PAWN, WHITE):  # semi
                        e += 15
                if piece == PAWN:
                    file = file_of(n)
                    if not pieces_of_file(file, PAWN, BLACK):  # passed
                        if file > 0:
                            pf = pieces_of_file(file - 1, PAWN, BLACK)
                            if pf:
                                x = 0
                                for s, pce in pf:
                                    if rank_of(s) > rank_of(n):
                                        x = 1
                                        break
                                if x == 1:
                                    break
                        if file < 7:
                            pf = pieces_of_file(file + 1, PAWN, BLACK)
                            if pf:
                                x = 0
                                for s, pce in pf:
                                    if rank_of(s) > rank_of(n):
                                        x = 1
                                        break
                                if x == 1:
                                    break
                        e += passed_bonus_w[rank_of(n)]
                    if len(pieces_of_file(file, PAWN, WHITE)) == 2:  # doubled
                        e -= 20

            else:
                e -= PIECE_VALUE_KAUFMAN[piece]
                pst -= DEFAULT_PSTS[piece][sq(file_of(n), 7 - rank_of(n))]
                if piece == ROOK:
                    file = file_of(n)
                    if not pieces_of_file(file, PAWN):
                        e -= 30
                    elif not pieces_of_file(file, PAWN, BLACK):
                        e -= 15
                if piece == PAWN:
                    file = file_of(n)
                    if not pieces_of_file(file, PAWN, WHITE):  # passed
                        if file > 0:
                            pf = pieces_of_file(file - 1, PAWN, WHITE)
                            if pf:
                                x = 0
                                for s, pce in pf:
                                    if rank_of(s) < rank_of(n):
                                        x = 1
                                        break
                                if x == 1:
                                    break
                        if file < 7:
                            pf = pieces_of_file(file + 1, PAWN, WHITE)
                            if pf:
                                x = 0
                                for s, pce in pf:
                                    if rank_of(s) < rank_of(n):
                                        x = 1
                                        break
                                if x == 1:
                                    break
                        e -= passed_bonus_b[rank_of(n)]
                    if len(pieces_of_file(file, PAWN, BLACK)) == 2:  # doubled
                        e += 20

    c = 0
    for _ in board.pieces_of(WHITE, BISHOP):
        c += 1
    if c == 2:
        e += 50

    c = 0
    for _ in board.pieces_of(BLACK, BISHOP):
        c += 1
    if c == 2:
        e -= 50

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
