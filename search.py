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
from chessdk import MATE_SCORE, Move, WHITE, BLACK, PIECE_VALUE_CLASSIC
import time
from random import randint

global nodes_visited
nodes_visited = 0


def search(
    board: Board,
    depth: int,
    eval_fn: Callable[[Board], int],
    first_move: Move = None,
    alpha: int = -MATE_SCORE,
    beta: int = MATE_SCORE,
    deadline=None,
) -> tuple[int, Move | None]:
    """Return ``(best_score_for_position, best_move)`` after searching to
    the given depth."""

    global nodes_visited
    nodes_visited += 1

    if deadline and randint(0, 100) == 0:
        if time.time() > deadline:
            raise TimeoutError()

    legal_moves = board.legal_moves()

    if not legal_moves and board.is_in_check():
        return (
            (+MATE_SCORE, None) if board.side_to_move == BLACK else (-MATE_SCORE, None)
        )
    elif not legal_moves and not board.is_in_check():
        return (0, None)

    if depth == 0:
        return (eval_fn(board), None)

    best = None
    for m in order_moves(board, legal_moves, first_move):
        board.make_move(m)
        bm = search(board, depth - 1, eval_fn, None, alpha, beta, deadline)
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


def order_moves(board: Board, moves: list[Move], first_move: Move = None) -> list[Move]:
    """Return ``moves`` sorted to put likely-strong moves first."""
    x = 0
    if first_move and first_move in moves:
        moves.remove(first_move)
        first_move_list = []
        first_move_list.append(first_move)
        x = 1

    sorted_moves = sorted(
        moves,
        key=lambda m: (
            (
                PIECE_VALUE_CLASSIC[board.pieces[m.to_sq].kind],
                -PIECE_VALUE_CLASSIC[board.pieces[m.from_sq].kind],
            )
            if board.pieces[m.to_sq] is not None
            else (0, 0)
        ),
        reverse=True,
    )

    if x == 1:
        return first_move_list + sorted_moves

    return sorted_moves


def search_iterative(
    board: Board, eval_fn, max_depth: int, time_budget_ms: int = None
) -> tuple[int, Move | None]:
    start = time.perf_counter()
    best_moves = []
    global nodes_visited
    global last_depth
    global last_score
    nodes_visited = 0
    count = 1
    new_time_budget = int(time_budget_ms / 2) if time_budget_ms else None
    best_moves.append(search(board, 1, eval_fn))
    for n in range(2, max_depth + 1):
        if (
            (time_budget_ms and (time.perf_counter() - start) * 1000 >= new_time_budget)
            or best_moves[-1][0] > 100_000
            or best_moves[-1][0] < -100_000
        ):
            break
        try:
            if new_time_budget:
                best_moves.append(
                    search(
                        board,
                        n,
                        eval_fn,
                        best_moves[-1][1],
                        deadline=time.time() + new_time_budget / 1000
                        if new_time_budget
                        else None,
                    )
                )
            else:
                best_moves.append(
                    search(
                        board,
                        n,
                        eval_fn,
                        best_moves[-1][1],
                    )
                )
        except TimeoutError as te:
            # break out and just use the last depth
            break
        count += 1
    last_depth = count
    last_score = best_moves[-1][0]
    return best_moves[-1]


def quiesce(board: Board, alpha: int, beta: int, eval_fn) -> int:
    global nodes_visited
    nodes_visited += 1

    legal_moves = board.legal_moves()

    if not legal_moves and board.is_in_check():
        return +MATE_SCORE if board.side_to_move == BLACK else -MATE_SCORE
    elif not legal_moves and not board.is_in_check():
        return 0

    opponent = board.side_to_move.other
    captures = []
    for m in legal_moves:
        victim = board.piece_at(m.to_sq)
        if victim is None:
            continue  # not a capture, skip it
        attacker = board.piece_at(m.from_sq)
        wins_or_trades = (
            PIECE_VALUE_CLASSIC[victim.kind] >= PIECE_VALUE_CLASSIC[attacker.kind]
        )
        target_undefended = not board.is_attacked(m.to_sq, opponent)
        if wins_or_trades or target_undefended:
            captures.append(m)

    stand_pat = eval_fn(board)

    if not captures:
        return stand_pat

    if board.side_to_move == WHITE:
        if stand_pat >= beta:
            return stand_pat
        if alpha < stand_pat:
            alpha = stand_pat

        for m in captures:
            board.make_move(m)
            nsp = quiesce(board, alpha, beta, eval_fn)
            board.undo_move()
            stand_pat = max(stand_pat, nsp)
            if alpha < stand_pat:
                alpha = stand_pat
            if alpha >= beta:
                return stand_pat

    else:
        if stand_pat <= alpha:
            return stand_pat
        if stand_pat < beta:
            beta = stand_pat

        for m in captures:
            board.make_move(m)
            nsp = quiesce(board, alpha, beta, eval_fn)
            board.undo_move()
            stand_pat = min(stand_pat, nsp)
            if stand_pat < beta:
                beta = stand_pat
            if alpha >= beta:
                return stand_pat

    return stand_pat
