from board import Board


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

print(board.legal_moves())
