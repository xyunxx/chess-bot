"""Your Board class.

This file lives in your own working directory after `chess-cli init`. Edit it
freely. Tests (`chess-cli test`) import `Board` from this file; the UCI
wrapper in later weeks will import your `choose_move` from `bot.py`, which
will in turn use this `Board`.

Square layout: indices 0..63, with 0 = a1 and 63 = h8. See
`chessdk.squares` for helpers (`sq(file, rank)`, `file_of(sq)`, etc.) and
offset constants (`KNIGHT_OFFSETS`, `BISHOP_DIRECTIONS`, etc.).
"""

from __future__ import annotations

from typing import Iterator

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
    MoveRecord,
)
from chessdk.base import BaseBoard


class Board(BaseBoard):
    """A chess board with move generation. You implement the methods below."""

    # === Stage 1: Squares and Pieces ===

    def piece_at(self, square: int) -> Piece | None:
        """Return the Piece on the given square, or None if empty."""
        return self.pieces[square]

    def pieces_of(self, color: Color, kind = None) -> Iterator[tuple[int, Piece]]:
        """Yield (square, piece) pairs for every piece of the given color."""
        for (square, piece) in enumerate(self.pieces):
            if piece and piece.color == color:
                if (kind is None) or piece.kind == kind:
                    yield (square, piece)

    # === Stage 2: Leapers ===

    def _leaper_moves(self, color: Color, kind, offsets):
        pieces = self.pieces_of(color, kind)
        l = list()
        for k, n in pieces:
            f = file_of(k)
            r = rank_of(k)
            for x, y in offsets:
                file = f + x
                rank = r + y
                s = sq(file, rank)
                if on_board(file, rank) and \
                        (self.piece_at(s) is None or self.piece_at(s).color != color):
                    l.append(Move(k, s))
        return l

    def _knight_moves(self, color: Color) -> list[Move]:
        """Pseudo-legal knight moves for `color`."""
        return self._leaper_moves(color, KNIGHT, KNIGHT_OFFSETS)

    def _king_moves(self, color: Color) -> list[Move]:
        """Pseudo-legal king moves for `color`. (No castling yet.)"""
        return self._leaper_moves(color, KING, KING_OFFSETS)

    # === Stage 3: Sliders ===

    def _slide_moves(self, color, piece_kind):
        moves = list()
        pieces = self.pieces_of(color, piece_kind)

        def calculate_moves(f, r, directions):
            moves = list()
            for x, y in directions:
                file = f + x
                rank = r + y
                while on_board(file, rank) and self.piece_at(sq(file, rank)) is None:
                    moves.append(Move(p, sq(file, rank)))
                    file += x
                    rank += y
                if on_board(file, rank) and self.piece_at(sq(file, rank)).color != color:
                    moves.append(Move(p, sq(file, rank)))
            return moves

        for p, n in pieces:
            f, r = file_of(p), rank_of(p)
            if n.kind == QUEEN or n.kind == BISHOP:
                moves += calculate_moves(f, r, BISHOP_DIRECTIONS)
            if n.kind == QUEEN or n.kind == ROOK:
                moves += calculate_moves(f, r, ROOK_DIRECTIONS)

        return moves

    def _bishop_moves(self, color: Color) -> list[Move]:
        """Pseudo-legal bishop moves for `color`."""
        return self._slide_moves(color, BISHOP)
        

    def _rook_moves(self, color: Color) -> list[Move]:
        """Pseudo-legal rook moves for `color`."""
        return self._slide_moves(color, ROOK)

    def _queen_moves(self, color: Color) -> list[Move]:
        """Pseudo-legal queen moves for `color`."""
        return self._slide_moves(color, QUEEN)

    # === Stage 4: Pawns ===

    def _pawn_moves(self, color: Color) -> list[Move]:
        """Pseudo-legal pawn moves for `color`. (No en passant or promotion yet.)"""
        direction = 1 if color == WHITE else -1
        start_rank = 1 if color == WHITE else 6
        moves = list()
        pawns = self.pieces_of(color, PAWN)

        for p, n in pawns:
            rank = rank_of(p)
            np = p + (8 * direction)
            if on_board(file_of(np), rank_of(np)) and self.piece_at(np) is None:
                moves.append(Move(p, np))
                if rank == start_rank:
                    np = p + (16 * direction)
                    if on_board(file_of(np), rank_of(np)) and self.piece_at(np) is None:
                        moves.append(Move(p, np))
            for c in [7, 9]:
                np = p + c * direction
                if on_board(file_of(np), rank_of(np)) and self.piece_at(np) is not None and self.piece_at(np).color != color:
                    moves.append(Move(p, np))

        return moves

    # === Wiring ===

    def pseudo_legal_moves(self) -> list[Move]:
        """All pseudo-legal moves for the side to move."""
        color = self.side_to_move
        return self._knight_moves(color) + self._king_moves(color) + self._bishop_moves(color) + self._rook_moves(color) + self._queen_moves(color) + self._pawn_moves(color)
    
    # === Stage 5: Make and Unmake ===

    def make_move(self, move: Move) -> None:
        """Apply 'move' in place. Saves an undo record."""
        m = MoveRecord(move, self.pieces[move.to_sq], move.to_sq, self.state.castling.copy(), self.state.en_passant, self.state.halfmove_clock)
        self.pieces[move.to_sq] = self.pieces[move.from_sq]
        self.pieces[move.from_sq] = None
        self.state.side_to_move = WHITE if self.state.side_to_move == BLACK else BLACK
        if self.pieces[move.to_sq].kind == PAWN or m.captured is not None:
            self.state.halfmove_clock = 0
        else:
            self.state.halfmove_clock += 1
        if self.state.side_to_move == WHITE: self.state.fullmove_number += 1
        self.state.en_passant = None
        self._history.append(m)

    
    def undo_move(self) -> None:
        """Reverse the last make_move call."""
        m = self._history.pop()
        self.pieces[m.move.from_sq] = self.pieces[m.move.to_sq]
        self.pieces[m.move.to_sq] = m.captured
        self.state.side_to_move = WHITE if self.state.side_to_move == BLACK else BLACK
        self.state.halfmove_clock = m.prev_halfmove
        self.state.en_passant = m.prev_en_passant
        self.state.castling = m.prev_castling
        if self.state.side_to_move == BLACK: self.state.fullmove_number -= 1
    
    def __init__(self, state = None):
        super().__init__(state)
        self._history = []