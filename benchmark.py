import time
import search
from board import Board
from evaluation import evaluate
from chessdk import MATE_SCORE

fen = "r1bqkb1r/pppp1ppp/2n2n2/4p3/4P3/2N2N2/PPPP1PPP/R1BQKB1R w KQkq - 4 4"
for depth in (1, 2, 3, 4):
    board = Board.from_fen(fen)
    search.nodes_visited = 0
    start = time.perf_counter()

    def quiescent_eval(board):
        return search.quiesce(board, -MATE_SCORE, MATE_SCORE, evaluate)

    score, move = search.search_iterative(board, quiescent_eval, depth)
    elapsed = time.perf_counter() - start
    print(
        f"depth {depth}: {search.nodes_visited:>9d} nodes "
        f"{elapsed:>6.2f}s {search.nodes_visited / elapsed:>10.0f} nps"
    )
