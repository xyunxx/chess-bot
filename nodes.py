from board import Board
import search
from chessdk import MATE_SCORE
from evaluation import evaluate, evaluate_fast


def quiescent_eval(b):
    return search.quiesce(b, -MATE_SCORE, MATE_SCORE, evaluate_fast)


fen = "r1bqkb1r/pppp1ppp/2n2n2/4p3/4P3/2N2N2/PPPP1PPP/R1BQKB1R w KQkq - 4 4"
for label, leaf in (("plain", evaluate), ("with quiescence", quiescent_eval)):
    search.nodes_visited = 0
    search.search(Board.from_fen(fen), 2, leaf)
    print(f"depth-2 search, {label:16s}: {search.nodes_visited} nodes")
