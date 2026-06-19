import time
from board import Board
import search
from chessdk import MATE_SCORE
from evaluation import evaluate, evaluate_fast


def quiescent_eval(b):
    return search.quiesce(b, -MATE_SCORE, MATE_SCORE, evaluate_fast)


fen = "8/8/8/4k3/8/8/R7/4K3 w - - 0 1"  # White K+R vs a lone Black king

print("cost of each depth (iterative deepening runs them in turn):")
cumulative = 0.0
for depth in range(1, 6):
    board = Board.from_fen(fen)
    start = time.perf_counter()
    search.search(board, depth, quiescent_eval)
    this_iter = (time.perf_counter() - start) * 1000
    cumulative += this_iter
    print(
        f" depth {depth}: this iter {this_iter:8.0f} ms      cumulative {cumulative:8.0f} ms"
    )

board = board.from_fen(fen)
start = time.perf_counter()
score, move = search.search_iterative(board, quiescent_eval, 5, 1500)
spent = (time.perf_counter() - start) * 1000
print(
    f"\nwith a 1500 ms budget: reached depth {search.last_depth}, "
    f"spent {spent:.0f} ms ({spent / 1500:.1f}x the budget)"
)
