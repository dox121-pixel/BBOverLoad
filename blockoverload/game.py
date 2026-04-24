"""Core game logic for BlockOverload.

Responsibilities
----------------
- Maintain the board state (2-D grid of colour tuples or None).
- Validate and commit piece placements.
- Detect and clear completed rows/columns.
- Track score, best score, combo multiplier.
- Detect game-over condition.
- Manage the tray of three pending pieces.
"""

from __future__ import annotations

import random
from typing import List, Optional, Tuple

from blockoverload.pieces import Cells, random_piece, SHAPES

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCORE_PER_CELL = 10
SCORE_PER_LINE = 100      # multiplied by number of lines cleared at once

MODES = {
    "Micro":   6,
    "Classic": 8,
    "Mega":    10,
}

Color = Tuple[float, float, float, float]


# ---------------------------------------------------------------------------
# Board helpers
# ---------------------------------------------------------------------------

def _empty_board(size: int):
    return [[None] * size for _ in range(size)]


# ---------------------------------------------------------------------------
# GameState
# ---------------------------------------------------------------------------

class GameState:
    """All mutable state for one game session."""

    def __init__(self, mode: str = "Classic") -> None:
        if mode not in MODES:
            raise ValueError(f"Unknown mode '{mode}'. Choose from {list(MODES)}")
        self.mode = mode
        self.size: int = MODES[mode]
        self.board: List[List[Optional[Color]]] = _empty_board(self.size)

        self.score: int = 0
        self.best: int = 0
        self.combo: int = 0          # consecutive clear rounds

        self.tray: List[Optional[Tuple[str, Cells, Color]]] = [None, None, None]
        self._refill_tray()

        self.game_over: bool = False
        self.last_cleared_rows: List[int] = []
        self.last_cleared_cols: List[int] = []

    # ------------------------------------------------------------------
    # Tray management
    # ------------------------------------------------------------------

    def _refill_tray(self) -> None:
        """Replace any empty tray slots with new random pieces."""
        for i in range(3):
            if self.tray[i] is None:
                self.tray[i] = random_piece()

    # ------------------------------------------------------------------
    # Placement
    # ------------------------------------------------------------------

    def can_place(self, tray_idx: int, row: int, col: int) -> bool:
        """Return True if the tray piece can be placed with its top-left at (row, col)."""
        piece = self.tray[tray_idx]
        if piece is None:
            return False
        _, cells, _ = piece
        for dr, dc in cells:
            r, c = row + dr, col + dc
            if r < 0 or r >= self.size or c < 0 or c >= self.size:
                return False
            if self.board[r][c] is not None:
                return False
        return True

    def place(self, tray_idx: int, row: int, col: int) -> bool:
        """
        Place the piece from tray slot *tray_idx* at board position (row, col).

        Returns True on success, False if the placement is invalid.
        After placing, clears completed lines and refills the tray.
        If the tray is exhausted and no piece can be placed, sets game_over.
        """
        if not self.can_place(tray_idx, row, col):
            return False

        _, cells, colour = self.tray[tray_idx]  # type: ignore[misc]
        for dr, dc in cells:
            self.board[row + dr][col + dc] = colour

        self.score += SCORE_PER_CELL * len(cells)

        # Clear lines
        cleared = self._clear_lines()
        if cleared:
            self.combo += 1
            self.score += SCORE_PER_LINE * cleared * self.combo
        else:
            self.combo = 0

        if self.score > self.best:
            self.best = self.score

        # Consume tray slot
        self.tray[tray_idx] = None

        # Refill if all three slots are empty
        if all(t is None for t in self.tray):
            self._refill_tray()

        # Check game-over
        if not self._any_piece_fits():
            self.game_over = True

        return True

    # ------------------------------------------------------------------
    # Line clearing
    # ------------------------------------------------------------------

    def _clear_lines(self) -> int:
        """Clear full rows and columns; return total number cleared."""
        full_rows = [r for r in range(self.size)
                     if all(self.board[r][c] is not None for c in range(self.size))]
        full_cols = [c for c in range(self.size)
                     if all(self.board[r][c] is not None for r in range(self.size))]

        self.last_cleared_rows = full_rows
        self.last_cleared_cols = full_cols

        for r in full_rows:
            for c in range(self.size):
                self.board[r][c] = None
        for c in full_cols:
            for r in range(self.size):
                self.board[r][c] = None

        return len(full_rows) + len(full_cols)

    # ------------------------------------------------------------------
    # Game-over detection
    # ------------------------------------------------------------------

    def _any_piece_fits(self) -> bool:
        """Return True if at least one tray piece can still be placed somewhere."""
        for piece in self.tray:
            if piece is None:
                continue
            _, cells, _ = piece
            for r in range(self.size):
                for c in range(self.size):
                    if self._fits(cells, r, c):
                        return True
        return False

    def _fits(self, cells: Cells, row: int, col: int) -> bool:
        for dr, dc in cells:
            r, c = row + dr, col + dc
            if r < 0 or r >= self.size or c < 0 or c >= self.size:
                return False
            if self.board[r][c] is not None:
                return False
        return True

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """Start a new game keeping the same mode and best score."""
        self.board = _empty_board(self.size)
        self.score = 0
        self.combo = 0
        self.tray = [None, None, None]
        self._refill_tray()
        self.game_over = False
        self.last_cleared_rows = []
        self.last_cleared_cols = []
