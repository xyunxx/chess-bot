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
)
from chessdk.base import BaseBoard


class Board(BaseBoard):
    """A chess board with move generation. You implement the methods below."""

    # === Stage 1: Squares and Pieces ===

    def piece_at(self, square: int) -> Piece | None:
        """Return the Piece on the given square, or None if empty."""
        return self.pieces[square]

    def pieces_of(self, color: Color) -> Iterator[tuple[int, Piece]]:
        """Yield (square, piece) pairs for every piece of the given color."""
        for i in range(64):
            if self.pieces[i] != None:
                if color == WHITE:
                    if self.pieces[i].char.isupper():
                        yield (i, self.piece_at(i))
                else:
                    if self.pieces[i].char.islower():
                        yield (i, self.piece_at(i))


    # === Stage 2: Leapers ===

    def _knight_moves(self, color: Color) -> list[Move]:
        """Pseudo-legal knight moves for `color`."""
        l = list()
        knights = list()
        for i in range(64):
            if color == WHITE:
                if self.piece_at(i) is not None and self.piece_at(i).char == 'N':
                    knights.append(i)
            else:
                if self.piece_at(i) is not None and self.piece_at(i).char == 'n':
                    knights.append(i)
        
        for k in knights:
            f = file_of(k)
            r = rank_of(k)
            for x, y in KNIGHT_OFFSETS:
                file = f + x
                rank = r + y
                s = sq(file, rank)
                if on_board(file, rank) and self.piece_at(s) is None:
                    l.append(Move(k, s))
                elif on_board(file, rank) and self.piece_at(s).color != color:
                    l.append(Move(k, s))
        return l

    def _king_moves(self, color: Color) -> list[Move]:
        """Pseudo-legal king moves for `color`. (No castling yet.)"""
        l = list()
        for i in range(64):
            if color == WHITE:
                if self.piece_at(i) is not None and self.piece_at(i).char == 'K':
                    king = i
            else:
                if self.piece_at(i) is not None and self.piece_at(i).char == 'k':
                    king = i
        
        f = file_of(king)
        r = rank_of(king)
        for x, y in KING_OFFSETS:
            file = f + x
            rank = r + y
            s = sq(file, rank)
            if on_board(file, rank) and self.piece_at(s) is None:
                l.append(Move(king, s))
            elif on_board(file, rank) and self.piece_at(s).color != color:
                l.append(Move(king, s))
        return l

    # === Stage 3: Sliders ===

    def _bishop_moves(self, color: Color) -> list[Move]:
        """Pseudo-legal bishop moves for `color`."""
        raise NotImplementedError("implement Stage 3 (bishop)")

    def _rook_moves(self, color: Color) -> list[Move]:
        """Pseudo-legal rook moves for `color`."""
        raise NotImplementedError("implement Stage 3 (rook)")

    def _queen_moves(self, color: Color) -> list[Move]:
        """Pseudo-legal queen moves for `color`."""
        raise NotImplementedError("implement Stage 3 (queen)")

    # === Stage 4: Pawns ===

    def _pawn_moves(self, color: Color) -> list[Move]:
        """Pseudo-legal pawn moves for `color`. (No en passant or promotion yet.)"""
        raise NotImplementedError("implement Stage 4 (pawn)")

    # === Wiring ===

    def pseudo_legal_moves(self) -> list[Move]:
        """All pseudo-legal moves for the side to move."""
        raise NotImplementedError("implement Stage 4 (combine all piece moves)")
