import time
from board import Board
import search
from chessdk import MATE_SCORE
from evaluation import evaluate_fast


def quiescent_eval(b):
    return search.quiesce(b, -MATE_SCORE, MATE_SCORE, evaluate_fast)


fen = "r2q1rk1/1b1nbppp/p2ppn2/1p6/3NPP2/2N1B3/PPPQB1PP/R4RK1 w - - 0 1"

print("cost of each depth on it's own:")
cumulative = 0.0
for depth in range(1, 4):
    board = Board.from_fen(fen)
    start = time.perf_counter()
    search.search(board, depth, quiescent_eval)
    this_iter = (time.perf_counter() - start) * 1000
    cumulative += this_iter
    print(
        f" depth {depth}: this iter {this_iter:8.0f} ms     cumulative {cumulative:8.0f} ms"
    )

board = Board.from_fen(fen)
start = time.perf_counter()
search.search_iterative(board, quiescent_eval, 3, 3900)  # 3.9 s budget
spent = (time.perf_counter() - start) * 1000
print(
    f"\nwith a 3900 ms budget: reached depth {search.last_depth}, "
    f"spent {spent:.0f} ms ({spent / 3900:.1f}x the budget)"
)
