"""Block shapes for BlockOverload.

Each shape is a list of (row, col) offsets from the top-left anchor.
Shapes mirror the variety found in classic block-puzzle games:
single dots, 1×N lines, 2×2 / 3×3 squares, L/J/T/S/Z corners.
"""

from __future__ import annotations

import random
from typing import List, Tuple

# ---------------------------------------------------------------------------
# Type alias
# ---------------------------------------------------------------------------
Cells = List[Tuple[int, int]]

# ---------------------------------------------------------------------------
# Palette – vivid colours that pop on a dark background
# ---------------------------------------------------------------------------
COLORS: List[Tuple[float, float, float, float]] = [
    (0.96, 0.26, 0.21, 1.0),   # red
    (0.13, 0.59, 0.95, 1.0),   # blue
    (0.30, 0.85, 0.39, 1.0),   # green
    (1.00, 0.76, 0.03, 1.0),   # amber
    (0.61, 0.15, 0.69, 1.0),   # purple
    (1.00, 0.34, 0.13, 1.0),   # orange
    (0.00, 0.74, 0.83, 1.0),   # cyan
    (0.92, 0.12, 0.39, 1.0),   # pink
]

# ---------------------------------------------------------------------------
# Shape catalogue (name → cell offsets)
# ---------------------------------------------------------------------------
SHAPES: dict[str, Cells] = {
    # Singles
    "dot":    [(0, 0)],

    # Horizontal lines
    "h2":     [(0, 0), (0, 1)],
    "h3":     [(0, 0), (0, 1), (0, 2)],
    "h4":     [(0, 0), (0, 1), (0, 2), (0, 3)],
    "h5":     [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)],

    # Vertical lines
    "v2":     [(0, 0), (1, 0)],
    "v3":     [(0, 0), (1, 0), (2, 0)],
    "v4":     [(0, 0), (1, 0), (2, 0), (3, 0)],
    "v5":     [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)],

    # Squares
    "sq2":    [(0, 0), (0, 1), (1, 0), (1, 1)],
    "sq3":    [(r, c) for r in range(3) for c in range(3)],

    # L-shapes (and their rotations / mirrors)
    "L_dr":   [(0, 0), (1, 0), (2, 0), (2, 1)],   # └
    "L_dl":   [(0, 1), (1, 1), (2, 0), (2, 1)],   # ┘
    "L_ur":   [(0, 0), (0, 1), (1, 0), (2, 0)],   # ┌ (Γ)
    "L_ul":   [(0, 0), (0, 1), (1, 1), (2, 1)],   # ┐

    # Small L (2-long stem)
    "sl_dr":  [(0, 0), (1, 0), (1, 1)],
    "sl_dl":  [(0, 1), (1, 0), (1, 1)],
    "sl_ur":  [(0, 0), (0, 1), (1, 0)],
    "sl_ul":  [(0, 0), (0, 1), (1, 1)],

    # T-shapes
    "T_d":    [(0, 0), (0, 1), (0, 2), (1, 1)],
    "T_u":    [(0, 1), (1, 0), (1, 1), (1, 2)],
    "T_r":    [(0, 0), (1, 0), (1, 1), (2, 0)],
    "T_l":    [(0, 1), (1, 0), (1, 1), (2, 1)],

    # S / Z shapes
    "S":      [(0, 1), (0, 2), (1, 0), (1, 1)],
    "Z":      [(0, 0), (0, 1), (1, 1), (1, 2)],
    "S_v":    [(0, 0), (1, 0), (1, 1), (2, 1)],
    "Z_v":    [(0, 1), (1, 0), (1, 1), (2, 0)],
}

SHAPE_NAMES: List[str] = list(SHAPES.keys())


def random_piece() -> Tuple[str, Cells, Tuple[float, float, float, float]]:
    """Return (name, cells, colour) for a randomly chosen shape."""
    name = random.choice(SHAPE_NAMES)
    colour = random.choice(COLORS)
    return name, SHAPES[name], colour


def piece_size(cells: Cells) -> Tuple[int, int]:
    """Return (rows, cols) bounding box of a piece."""
    rows = [r for r, _ in cells]
    cols = [c for _, c in cells]
    return max(rows) - min(rows) + 1, max(cols) - min(cols) + 1
