from board import Board
from chessdk import (
    BISHOP,
    BISHOP_DIRECTIONS,
    BLACK,
    Color,
    KING,
    KING_OFFSETS,
    KNIGHT,
    KNIGHT_OFFSETS,
    Kind,
    Move,
    PAWN,
    Piece,
    QUEEN,
    QUEEN_DIRECTIONS,
    ROOK,
    ROOK_DIRECTIONS,
    WHITE,
    file_of,
    on_board,
    rank_of,
    sq,
    parse_square,
    MoveRecord,
)

from evaluation import evaluate
from search import search, order_moves


def perft(board: Board, depth: int) -> int:
    if depth == 0:
        return 1
    total = 0
    for move in board.legal_moves():
        board.make_move(move)
        total += perft(board, depth - 1)
        board.undo_move()
    return total


board = Board().from_fen(
    "rnb1kb1r/pp3ppp/2p2n2/q2pp3/Q2PP3/2P2N2/PP3PPP/RNB1KB1R w KQkq - 0 1"
)

print(order_moves(board, board.legal_moves()))
