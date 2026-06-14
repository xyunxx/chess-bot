import time
import search
from board import Board
from evaluation import evaluate

fen = "r1bqkb1r/pppp1ppp/2n2n2/4p3/4P3/2N2N2/PPPP1PPP/R1BQKB1R w KQkq - 4 4"
for depth in (1, 2, 3, 4):
    board = Board.from_fen(fen)
    search.nodes_visited = 0
    start = time.perf_counter()
    score, move = search.search(board, depth, evaluate)
    elapsed = time.perf_counter() - start
    print(
        f"depth {depth}: {search.nodes_visited:>9d} nodes "
        f"{elapsed:>6.2f}s {search.nodes_visited / elapsed:>10.0f} nps"
    )
