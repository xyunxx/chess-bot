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


def perft(board: Board, depth: int) -> int:
    if depth == 0:
        return 1
    total = 0
    for move in board.legal_moves():
        board.make_move(move)
        total += perft(board, depth - 1)
        board.undo_move()
    return total


print(
    perft(
        Board().from_fen("rnbqkbnr/1ppppppp/8/p7/8/7P/PPPPPPP1/RNBQKBNR w KQkq - 0 2"),
        1,
    )
)  # a2a3 into h3h4 extra
print(
    perft(
        Board().from_fen(
            "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1"
        ),
        2,
    )
)  # a2a3 into h3a3 extra
# a2a4 into h3a3 extra
# f3h5 into a7h5 extra

# all pawns that cross from the h file into the a file or the other way around
