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
        if p is None:
            continue
        piece = p.kind
        if p.color == WHITE:
            e += PIECE_VALUE_KAUFMAN[piece]
            pst += DEFAULT_PSTS[piece][n]
            if piece == ROOK:  # Rook on open file bonus
                file = file_of(n)
                if not board.pieces_of_file(file, PAWN):  # open
                    e += 30
                elif not board.pieces_of_file(file, PAWN, WHITE):  # semi
                    # NOTE: Color swap
                    e += 15
            if piece == PAWN:
                # Passed pawn bonus
                file = file_of(n)
                passed_pawn = True
                # NOTE: color swap
                opposing_pawns = (
                    board.pieces_of_file(file, PAWN, BLACK)
                    + (
                        board.pieces_of_file(file - 1, PAWN, BLACK)
                        if file - 1 >= 0
                        else []
                    )
                    + (
                        board.pieces_of_file(file + 1, PAWN, BLACK)
                        if file + 1 <= 7
                        else []
                    )
                )
                # NOTE: color swap
                if opposing_pawns:
                    for s, _ in opposing_pawns:
                        if rank_of(s) > rank_of(n):
                            # NOTE: color swap
                            passed_pawn = False
                            break
                if passed_pawn:
                    e += passed_bonus_w[rank_of(n)]

                # Doubled pawn penalty
                if len(board.pieces_of_file(file, PAWN, WHITE)) >= 2:
                    # NOTE: color swap
                    e -= 20
        else:
            e -= PIECE_VALUE_KAUFMAN[piece]
            pst -= DEFAULT_PSTS[piece][sq(file_of(n), 7 - rank_of(n))]
            if piece == ROOK:
                file = file_of(n)
                if not board.pieces_of_file(file, PAWN):
                    e -= 30
                elif not board.pieces_of_file(file, PAWN, BLACK):
                    e -= 15
            if piece == PAWN:
                file = file_of(n)
                if not board.pieces_of_file(file, PAWN, WHITE):  # passed
                    if file > 0:
                        opposing_pawns = board.pieces_of_file(file - 1, PAWN, WHITE)
                        if opposing_pawns:
                            x = 0
                            for s, pce in opposing_pawns:
                                if rank_of(s) < rank_of(n):
                                    x = 1
                                    break
                            if x == 1:
                                break
                    if file < 7:
                        opposing_pawns = board.pieces_of_file(file + 1, PAWN, WHITE)
                        if opposing_pawns:
                            x = 0
                            for s, pce in opposing_pawns:
                                if rank_of(s) < rank_of(n):
                                    x = 1
                                    break
                            if x == 1:
                                break
                    e -= passed_bonus_b[rank_of(n)]
                if len(board.pieces_of_file(file, PAWN, BLACK)) == 2:  # doubled
                    e += 20

    # Bishop pair bonus
    if len(list(board.pieces_of(WHITE, BISHOP))) >= 2:
        e += 50
    if len(list(board.pieces_of(BLACK, BISHOP))) >= 2:
        e -= 50

    s1 = len(board.legal_moves())
    board.state.side_to_move = side.other
    s2 = len(board.legal_moves())
    board.state.side_to_move = side
    mobility_bonus = (
        (s1 - s2)
        * (1 if board.state.side_to_move == WHITE else -1)
        * DEFAULT_MOBILITY_WEIGHT
    )

    return e + pst + mobility_bonus
