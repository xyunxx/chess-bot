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
    square_name,
)
from chessdk.base import BaseBoard


class Board(BaseBoard):
    """A chess board with move generation. You implement the methods below."""

    # === Stage 1: Squares and Pieces ===

    def piece_at(self, square: int) -> Piece | None:
        """Return the Piece on the given square, or None if empty."""
        return self.pieces[square]

    def pieces_of(self, color: Color, kind=None) -> Iterator[tuple[int, Piece]]:
        """Yield (square, piece) pairs for every piece of the given color."""
        for square, piece in enumerate(self.pieces):
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
                if on_board(file, rank) and (
                    self.piece_at(s) is None or self.piece_at(s).color != color
                ):
                    l.append(Move(k, s))
        return l

    def _knight_moves(self, color: Color) -> list[Move]:
        """Pseudo-legal knight moves for `color`."""
        return self._leaper_moves(color, KNIGHT, KNIGHT_OFFSETS)

    def _king_moves(self, color: Color) -> list[Move]:
        """Pseudo-legal king moves for `color`."""
        castling = []
        b1 = self.pieces[1]
        c1 = self.pieces[2]
        d1 = self.pieces[3]
        e1 = self.pieces[4]
        f1 = self.pieces[5]
        g1 = self.pieces[6]
        b8 = self.pieces[57]
        c8 = self.pieces[58]
        d8 = self.pieces[59]
        e8 = self.pieces[60]
        f8 = self.pieces[61]
        g8 = self.pieces[62]
        if color == WHITE:
            if self.state.castling.white_kingside:
                if self.pieces[f1] is None and self.pieces[g1] is None:
                    if not is_in_check(color):
                        if not is_attacked(f1, color.other) and not is_attacked(g1, color.other):
                            castling.append(Move(e1, g1))
            if self.state.castling.white_queenside:
                if self.pieces[b1] is None and self.pieces[c1] is None and self.pieces[d1] is None:
                    if not is_in_check(color):
                        if not is_attacked(c1, color.other) and not is_attacked(d1, color.other):
                            castling.append(Move(e1, c1))
        else:
            if self.state.castling.black_kingside:
                if self.pieces[f8] is None and self.pieces[g8] is None:
                    if not is_in_check(color):
                        if not is_attacked(f8, color.other) and not is_attacked(g8, color.other):
                            castling.append(Move(e8, g8))
            if self.state.castling.black_queenside:
                if self.pieces[b8] is None and self.pieces[c8] is None and self.pieces[d8] is None:
                    if not is_in_check(color):
                        if not is_attacked(c8, color.other) and not is_attacked(d8, color.other):
                            castling.append(Move(e8, c8))

        return self._leaper_moves(color, KING, KING_OFFSETS) + castling

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
                if (
                    on_board(file, rank)
                    and self.piece_at(sq(file, rank)).color != color
                ):
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
                if (
                    on_board(file_of(np), rank_of(np))
                    and self.piece_at(np) is not None
                    and self.piece_at(np).color != color
                ):
                    moves.append(Move(p, np))

        return moves

    # === Wiring ===

    def pseudo_legal_moves(self) -> list[Move]:
        """All pseudo-legal moves for the side to move."""
        color = self.side_to_move
        return (
            self._knight_moves(color)
            + self._king_moves(color)
            + self._bishop_moves(color)
            + self._rook_moves(color)
            + self._queen_moves(color)
            + self._pawn_moves(color)
        )

    # === Stage 5: Make and Unmake ===

    def make_move(self, move: Move) -> None: #castling
        """Apply 'move' in place. Saves an undo record.

        move: must be a pseudo-legal move already
        """
        m = MoveRecord(
            move,
            self.pieces[move.to_sq],
            move.to_sq,
            self.state.castling.copy(),  #
            self.state.en_passant,
            self.state.halfmove_clock,
        )
        self.pieces[move.to_sq] = self.pieces[move.from_sq]
        self.pieces[move.from_sq] = None
        self.state.side_to_move = self.state.side_to_move.other
        if self.pieces[move.to_sq].kind == PAWN or m.captured is not None:
            self.state.halfmove_clock = 0
        else:
            self.state.halfmove_clock += 1
        if self.state.side_to_move == WHITE:
            self.state.fullmove_number += 1
        self.state.en_passant = None  # TODO
        self._history.append(m)

    def undo_move(self) -> None:
        """Reverse the last make_move call."""
        m = self._history.pop()
        self.pieces[m.move.from_sq] = self.pieces[m.move.to_sq]
        self.pieces[m.move.to_sq] = m.captured
        self.state.side_to_move = self.state.side_to_move.other
        self.state.halfmove_clock = m.prev_halfmove
        self.state.en_passant = m.prev_en_passant
        self.state.castling = m.prev_castling
        if self.state.side_to_move == BLACK:
            self.state.fullmove_number -= 1

    def __init__(self, state=None):
        super().__init__(state)
        self._history = []

    # === Stage 6: Attacks and Legality ===

    def is_attacked(self, square: int, by_color: Color) -> bool:
        file = file_of(square)
        rank = rank_of(square)
        direction = 1 if by_color == BLACK else -1

        def leapers(offset, piece: Piece):
            for x, y in offset:
                nf = file + x
                nr = rank + y
                if (
                    on_board(nf, nr)
                    and self.pieces[sq(nf, nr)] is not None
                    and self.pieces[sq(nf, nr)].kind == piece
                    and self.pieces[sq(nf, nr)].color == by_color
                ):
                    return True

        if leapers(KNIGHT_OFFSETS, KNIGHT):
            return True

        if leapers(KING_OFFSETS, KING):
            return True

        def sliders(offset, piece: Piece):
            for x, y in offset:
                nf = file + x
                nr = rank + y

                while on_board(nf, nr) and self.pieces[sq(nf, nr)] is None:
                    nf += x
                    nr += y

                if on_board(nf, nr) and self.pieces[sq(nf, nr)] is not None:
                    if (
                        self.pieces[sq(nf, nr)].kind == piece
                        or self.pieces[sq(nf, nr)].kind == QUEEN
                        and self.pieces[sq(nf, nr)].color == by_color
                    ):
                        return True

        rq = sliders(ROOK_DIRECTIONS, ROOK)  # Rook and Queen

        if rq:
            return True

        bq = sliders(BISHOP_DIRECTIONS, BISHOP)  # Bishop and Queen

        if bq:
            return True

        square1 = square + 7 * direction
        square2 = square + 9 * direction

        if (
            on_board(file_of(square1), rank_of(square1))
            and self.pieces[square1] is not None
            and self.pieces[square1].kind == PAWN
            and self.pieces[square1].color == by_color
        ):
            return True

        if (
            on_board(file_of(square2), rank_of(square2))
            and self.pieces[square2] is not None
            and self.pieces[square2].kind == PAWN
            and self.pieces[square2].color == by_color
        ):
            return True

        return False

    def is_in_check(self, color: Color | None = None) -> bool:
        """True if 'color' (default: side to move) is in check."""
        if color is None:
            color = self.side_to_move
        king = next(self.pieces_of(color, KING))
        return self.is_attacked(king[0], WHITE if color == BLACK else BLACK)

    def legal_moves(self) -> list[Move]:
        """Pseudo-legal moves filtered to those that don't leave own king in check."""
        legal = list()
        for m in self.pseudo_legal_moves():
            self.make_move(m)
            if not self.is_in_check(WHITE if self.side_to_move == BLACK else BLACK):
                legal.append(m)
            self.undo_move()
        return legal
