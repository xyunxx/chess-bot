"""Your search function.

``search(board, depth, eval_fn, alpha, beta)`` runs minimax with alpha-beta
pruning. It returns ``(score, best_move)``: a White-relative centipawn score
for the position under optimal play to the given depth, and the move that
achieves that score (or ``None`` at terminal or leaf nodes).

The search handles terminal positions itself (a side with no legal moves
that's in check is mated; not in check is stalemated), so the ``eval_fn``
parameter only ever sees positions with legal moves left to play. Phase 5
builds this up across four stages: Stage 17 introduces minimax with mate
distance, Stage 18 adds alpha-beta cutoffs, Stage 19 adds the move-ordering
helper below, and Stage 20 instruments the whole thing.
"""

from __future__ import annotations

from typing import Callable

from board import Board
from chessdk import MATE_SCORE, Move, WHITE, BLACK


def search(
    board: Board,
    depth: int,
    eval_fn: Callable[[Board], int],
    alpha: int = -MATE_SCORE,
    beta: int = MATE_SCORE,
) -> tuple[int, Move | None]:
    """Return ``(best_score_for_position, best_move)`` after searching to
    the given depth."""
    if not board.legal_moves() and board.is_in_check():
        return (
            (+MATE_SCORE, None) if board.side_to_move == BLACK else (-MATE_SCORE, None)
        )
    elif not board.legal_moves() and not board.is_in_check():
        return (0, None)

    if depth == 0:
        return (eval_fn(board), None)

    best = None
    for m in board.legal_moves():
        board.make_move(m)
        bm = search(board, depth - 1, eval_fn, alpha, beta)
        board.undo_move()

        if bm[0] > 100_000:
            bm = (bm[0] - 1, bm[1])
        elif bm[0] < -100_000:
            bm = (bm[0] + 1, bm[1])

        best = (
            (bm[0], m)
            if best is None
            or (bm[0] > best[0] and board.side_to_move == WHITE)
            or (bm[0] < best[0] and board.side_to_move == BLACK)
            else best
        )

        if board.side_to_move == WHITE:
            alpha = max(alpha, bm[0])
        else:
            beta = min(beta, bm[0])
        if alpha >= beta:
            break

    return best


def order_moves(board: Board, moves: list[Move]) -> list[Move]:
    """Return ``moves`` sorted to put likely-strong moves first."""
    raise NotImplementedError("order_moves: implement in Phase 5 (Stage 19)")
