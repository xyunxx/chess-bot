from board import Board
from chessdk import QUEEN

board = Board.from_fen("8/1P6/8/8/8/8/8/4k1K1 w - - 5 30")
promotion = next(
    m for m in board.legal_moves() if m.from_sq == 49 and m.promotion == QUEEN
)  # b7 -> b8 = Q

board.make_move(promotion)
print("halfmove clock after a quiet promotion:", board.state.halfmove_clock)
