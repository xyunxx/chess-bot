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
    PAWN,
    sq,
    file_of,
    rank_of,
    DEFAULT_MOBILITY_WEIGHT,
    BLACK,
    BISHOP,
    ROOK,
    Color,
    MG_PST,
    EG_VALUE,
    MG_VALUE,
    EG_PST,
    game_phase,
    PHASE_MAX,
)


def rook_open_semi(board: Board, file: int, color: Color) -> int:
    if not board.pieces_of_file(file, PAWN):  # open
        return 30
    elif not board.pieces_of_file(file, PAWN, color):  # semi
        return 15
    return 0


def passed_pawn(board: Board, file: int, color: Color, n: int):
    # Passed pawn bonus
    passed_bonus_w = [0, 5, 10, 20, 40, 80, 160, 0]
    passed_bonus_b = passed_bonus_w[::-1]
    passed_pawn = True
    opposing_pawns = (
        board.pieces_of_file(file, PAWN, color.other)
        + (board.pieces_of_file(file - 1, PAWN, color.other) if file - 1 >= 0 else [])
        + (board.pieces_of_file(file + 1, PAWN, color.other) if file + 1 <= 7 else [])
    )
    if opposing_pawns:
        for s, _ in opposing_pawns:
            ranks = rank_of(s) - rank_of(n)
            if (color == WHITE and ranks > 0) or (color == BLACK and ranks < 0):
                passed_pawn = False
                break
    if passed_pawn:
        return (
            passed_bonus_w[rank_of(n)] if color == WHITE else passed_bonus_b[rank_of(n)]
        )
    return 0


def doubled_pawns(board: Board, file: int, color: Color) -> int:
    if len(board.pieces_of_file(file, PAWN, color)) >= 2:  # doubled
        return 10  # Once for each pawn
    return 0


def isolated_pawns(board: Board, file: int, color: Color) -> int:
    allied_pawns = (
        board.pieces_of_file(file - 1, PAWN, color) if file - 1 >= 0 else []
    ) + (board.pieces_of_file(file + 1, PAWN, color) if file + 1 <= 7 else [])

    if not allied_pawns:
        return 20
    return 0


def bishop_pair(board: Board, color: Color) -> int:
    if len(list(board.pieces_of(color, BISHOP))) >= 2:
        return 50
    return 0


def evaluate_fast(board: Board):
    """Return a centipawn score for the position from White's point of view. Skips the terminal checks and the mobility score."""

    e = 0
    phase = game_phase(board)
    for n, p in enumerate(board.pieces):
        if p is None:
            continue
        piece = p.kind
        color = p.color
        if color == WHITE:
            mg = MG_VALUE[piece] + MG_PST[piece][n]
            eg = EG_VALUE[piece] + EG_PST[piece][n]
            value = (mg * phase + eg * (PHASE_MAX - phase)) // PHASE_MAX
            e += value
        else:
            new_square = sq(file_of(n), 7 - rank_of(n))
            mg = MG_VALUE[piece] + MG_PST[piece][new_square]
            eg = EG_VALUE[piece] + EG_PST[piece][new_square]
            value = (mg * phase + eg * (PHASE_MAX - phase)) // PHASE_MAX
            e -= value

        if piece == ROOK:
            # Rook on open file bonus
            file = file_of(n)
            ros = rook_open_semi(board, file, color)
            e += ros if color == WHITE else -ros

        if piece == PAWN:
            file = file_of(n)
            # Passed pawn bonus
            pp = passed_pawn(board, file, color, n)
            e += pp if color == WHITE else -pp

            # Doubled pawn penalty
            dp = doubled_pawns(board, file, color)
            e += dp if color == BLACK else -dp

            # Isolated pawn penalty
            ip = isolated_pawns(board, file, color)
            e += ip if color == BLACK else -ip

    # Bishop pair bonus
    e += bishop_pair(board, WHITE)
    e -= bishop_pair(board, BLACK)

    return e


def evaluate(board: Board) -> int:
    """Return a centipawn score for the position from White's point of view."""

    side = board.side_to_move
    if board.legal_moves() == []:
        if board.is_in_check():  # checkmate
            return -MATE_SCORE if side == WHITE else MATE_SCORE
        else:  # stalemate
            return 0

    e = evaluate_fast(board)

    try:
        s1 = 1
        if not board.is_in_check(side.other):
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
    finally:
        board.state.side_to_move = side

    return e + mobility_bonus
