import time
from board import Board
import search
from chessdk import MATE_SCORE
from evaluation import evaluate_fast


def quiescent_eval(b):
    return search.quiesce(b, -MATE_SCORE, MATE_SCORE, evaluate_fast)


fen = "r1bqkb1r/pppp1ppp/2n2n2/4p3/4P3/2N2N2/PPPP1PPP/R1BQKB1R w KQkq - 4 4"
for depth in (1, 2, 3):
    board = Board.from_fen(fen)
    start = time.perf_counter()
    search.search(board, depth, quiescent_eval)
    print(f"depth {depth}: {(time.perf_counter() - start) * 1000:.0f} ms")
