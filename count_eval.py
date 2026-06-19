from board import Board
import evaluation

calls = 0
original = Board.legal_moves


def counting(self):
    global calls
    calls += 1
    return original(self)


board = Board.from_fen(
    "r1bqkb1r/pppp1ppp/2n2n2/4p3/4P3/2N2N2/PPPP1PPP/R1BQKB1R w KQkq - 4 4"
)
Board.legal_moves = counting
evaluation.evaluate(board)
Board.legal_moves = original
print(f"legal_moves() calls in ONE evaluate(): {calls}")
