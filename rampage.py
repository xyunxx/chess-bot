from board import Board


def longest_capture_line(board: Board, cap=20):
    caps = [m for m in board.legal_moves() if board.piece_at(m.to_sq) is not None]
    if not caps or cap == 0:
        return []
    best = []
    for m in caps:
        board.make_move(m)
        line = longest_capture_line(board, cap - 1)
        board.undo_move()
        if 1 + len(line) > len(best):
            best = [m.uci()] + line
    return best


fen = "r1bqkb1r/pppp1ppp/2n2n2/4p3/4P3/2N2N2/PPPP1PPP/R1BQKB1R w KQkq - 4 4"
line = longest_capture_line(Board.from_fen(fen))
print(f"{len(line)} captures in a row (capped): {' '.join(line)}")
