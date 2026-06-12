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

    def rook_open_semi(file: int, color: Color) -> int:
        if not board.pieces_of_file(file, PAWN):  # open
            return 30
        elif not board.pieces_of_file(file, PAWN, color):  # semi
            return 15
        return 0

    def passed_pawn(file: int, color: Color):
        # Passed pawn bonus
        passed_bonus_w = [0, 5, 10, 20, 40, 80, 160, 0]
        passed_bonus_b = passed_bonus_w[::-1]
        passed_pawn = True
        opposing_pawns = (
            board.pieces_of_file(file, PAWN, color.other)
            + (
                board.pieces_of_file(file - 1, PAWN, color.other)
                if file - 1 >= 0
                else []
            )
            + (
                board.pieces_of_file(file + 1, PAWN, color.other)
                if file + 1 <= 7
                else []
            )
        )
        if opposing_pawns:
            for s, _ in opposing_pawns:
                ranks = rank_of(s) - rank_of(n)
                if (color == WHITE and ranks > 0) or (color == BLACK and ranks < 0):
                    passed_pawn = False
                    break
        if passed_pawn:
            return (
                passed_bonus_w[rank_of(n)]
                if color == WHITE
                else passed_bonus_b[rank_of(n)]
            )
        return 0

    def doubled_pawns(file: int, color: Color) -> int:
        if len(board.pieces_of_file(file, PAWN, color)) >= 2:  # doubled
            return 20
        return 0

    def isolated_pawns(file: int, color: Color) -> int:
        allied_pawns = (
            board.pieces_of_file(file - 1, PAWN, color) if file - 1 >= 0 else []
        ) + (board.pieces_of_file(file + 1, PAWN, color) if file + 1 <= 7 else [])

        if not allied_pawns:
            return 20
        return 0

    def bishop_pair(color: Color) -> int:
        if len(list(board.pieces_of(color, BISHOP))) >= 2:
            return 50
        return 0

    e = 0
    pst = 0
    for n, p in enumerate(board.pieces):
        if p is None:
            continue
        piece = p.kind
        color = p.color
        if p.color == WHITE:
            e += PIECE_VALUE_KAUFMAN[piece]
            pst += DEFAULT_PSTS[piece][n]
        else:
            e -= PIECE_VALUE_KAUFMAN[piece]
            pst -= DEFAULT_PSTS[piece][sq(file_of(n), 7 - rank_of(n))]

        if piece == ROOK:
            # Rook on open file bonus
            file = file_of(n)
            ros = rook_open_semi(file, color)
            e += ros if color == WHITE else -ros

        if piece == PAWN:
            file = file_of(n)
            # Passed pawn bonus
            pp = passed_pawn(file, color)
            e += pp if color == WHITE else -pp

            # Doubled pawn penalty
            dp = doubled_pawns(file, color)
            e += dp if color == BLACK else -dp

            # Isolated pawn penalty
            ip = isolated_pawns(file, color)
            e += ip if color == BLACK else -ip

    # Bishop pair bonus
    e += bishop_pair(WHITE)
    e -= bishop_pair(BLACK)

    s1 = len(board.legal_moves())
    s2 = 1

    if not board.is_in_check(side):
        board.state.side_to_move = side.other
        s2 = len(board.legal_moves())
        board.state.side_to_move = side
    mobility_bonus = (
        (s1 - s2)
        * (1 if board.state.side_to_move == WHITE else -1)
        * DEFAULT_MOBILITY_WEIGHT
    )

    return e + pst + mobility_bonus
