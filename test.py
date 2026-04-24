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
)

Board = Board().from_fen('8/8/8/8/3B4/8/8/8 w - - 0 1')
print(Board._bishop_moves(WHITE))