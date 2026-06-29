from board import Board
from chessdk import (
    tapered_eval,
    tapered_pst,
    game_phase,
    WHITE,
    MG_VALUE,
    EG_VALUE,
    MG_PST,
    EG_PST,
    PHASE_MAX,
    rank_of,
    file_of,
    sq,
)


def perft(board: Board, depth: int) -> int:
    if depth == 0:
        return 1
    total = 0
    for move in board.legal_moves():
        board.make_move(move)
        total += perft(board, depth - 1)
        board.undo_move()
    return total


board = Board().from_fen("8/8/8/8/8/4k3/8/4K2R w K - 0 1")

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

print(e)
print(tapered_eval(board))
