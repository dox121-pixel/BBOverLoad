"""Kivy UI for BlockOverload.

Screens
-------
MenuScreen  – mode selector (Micro / Classic / Mega)
GameScreen  – live game (board + piece tray + score)

Visual style mirrors Block Blast:
  • Very dark navy background
  • Vibrant rounded block cells
  • Piece tray at the bottom
  • Score + best prominently at the top
"""

from __future__ import annotations

import math
from typing import Optional, Tuple

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Line, Rectangle, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.uix.widget import Widget

from blockoverload.game import GameState, MODES
from blockoverload.pieces import Cells, piece_size, COLORS

# ---------------------------------------------------------------------------
# Palette / sizing constants
# ---------------------------------------------------------------------------
BG_COLOR       = (0.08, 0.08, 0.18, 1)        # dark navy
GRID_LINE      = (0.20, 0.20, 0.35, 1)        # subtle grid lines
EMPTY_CELL     = (0.12, 0.12, 0.25, 1)        # empty cell fill
SHADOW         = (0.00, 0.00, 0.00, 0.35)     # drop shadow for blocks
CORNER_RADIUS  = 6                             # px – rounded block corners
CELL_GAP       = 3                             # px gap between cells
TRAY_SCALE     = 0.55                          # piece preview scale vs board cell


# ===========================================================================
# Helpers
# ===========================================================================

def _draw_block(canvas, x: float, y: float, w: float, h: float,
                colour: Tuple, radius: float = CORNER_RADIUS) -> None:
    """Draw a single rounded coloured block at pixel position (x, y)."""
    # Tiny shadow offset
    with canvas:
        Color(*SHADOW)
        RoundedRectangle(pos=(x + 2, y - 2), size=(w, h), radius=[radius])
        Color(*colour)
        RoundedRectangle(pos=(x, y), size=(w, h), radius=[radius])


# ===========================================================================
# BoardWidget
# ===========================================================================

class BoardWidget(Widget):
    """Draws the grid and handles drag-and-drop placement."""

    def __init__(self, state: GameState, on_placed=None, **kwargs):
        super().__init__(**kwargs)
        self.state = state
        self.on_placed = on_placed  # callable(tray_idx, row, col)

        # Drag state
        self._drag_tray_idx: Optional[int] = None
        self._drag_cells: Optional[Cells] = None
        self._drag_colour: Optional[Tuple] = None
        self._drag_pos: Tuple[float, float] = (0.0, 0.0)

        self.bind(pos=self._redraw, size=self._redraw)

    # ------------------------------------------------------------------
    # Geometry helpers
    # ------------------------------------------------------------------

    def _cell_size(self) -> float:
        n = self.state.size
        return min(self.width, self.height) / n

    def _cell_xy(self, row: int, col: int) -> Tuple[float, float]:
        """Return pixel (x, y) of the bottom-left corner of board cell (row, col)."""
        cs = self._cell_size()
        n = self.state.size
        board_w = cs * n
        board_h = cs * n
        ox = self.x + (self.width - board_w) / 2
        oy = self.y + (self.height - board_h) / 2
        # row 0 is the TOP row; kivy y increases upward
        x = ox + col * cs
        y = oy + (n - 1 - row) * cs
        return x, y

    def _pixel_to_cell(self, px: float, py: float) -> Tuple[int, int]:
        """Convert pixel coords → (row, col); may be out-of-bounds."""
        cs = self._cell_size()
        n = self.state.size
        board_w = cs * n
        board_h = cs * n
        ox = self.x + (self.width - board_w) / 2
        oy = self.y + (self.height - board_h) / 2
        col = int((px - ox) / cs)
        row = n - 1 - int((py - oy) / cs)
        return row, col

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def _redraw(self, *_):
        self.canvas.clear()
        self._draw_grid()
        if self._drag_tray_idx is not None:
            self._draw_drag_ghost()

    def _draw_grid(self):
        cs = self._cell_size()
        gap = CELL_GAP
        inner = cs - gap

        with self.canvas:
            for r in range(self.state.size):
                for c in range(self.state.size):
                    x, y = self._cell_xy(r, c)
                    colour = self.state.board[r][c]
                    if colour is None:
                        Color(*EMPTY_CELL)
                        RoundedRectangle(
                            pos=(x + gap / 2, y + gap / 2),
                            size=(inner, inner),
                            radius=[CORNER_RADIUS],
                        )
                    else:
                        _draw_block(self.canvas, x + gap / 2, y + gap / 2,
                                    inner, inner, colour)

    def _draw_drag_ghost(self):
        if self._drag_cells is None:
            return
        cs = self._cell_size()
        gap = CELL_GAP
        inner = cs - gap
        px, py = self._drag_pos
        anchor_row, anchor_col = self._pixel_to_cell(px, py)

        valid = all(
            self.state.can_place(self._drag_tray_idx, anchor_row, anchor_col)
            for _ in [1]  # single check
        )
        alpha = 0.85 if valid else 0.40
        colour = list(self._drag_colour)  # type: ignore[arg-type]
        colour[3] = alpha

        with self.canvas:
            for dr, dc in self._drag_cells:  # type: ignore[union-attr]
                r, c = anchor_row + dr, anchor_col + dc
                if 0 <= r < self.state.size and 0 <= c < self.state.size:
                    x, y = self._cell_xy(r, c)
                    _draw_block(self.canvas, x + gap / 2, y + gap / 2,
                                inner, inner, tuple(colour))

    # ------------------------------------------------------------------
    # Called by PieceTray when a drag enters the board
    # ------------------------------------------------------------------

    def start_drag(self, tray_idx: int, cells: Cells,
                   colour: Tuple, touch_pos: Tuple[float, float]) -> None:
        self._drag_tray_idx = tray_idx
        self._drag_cells = cells
        self._drag_colour = colour
        self._drag_pos = touch_pos
        self._redraw()

    def update_drag(self, pos: Tuple[float, float]) -> None:
        self._drag_pos = pos
        self._redraw()

    def end_drag(self, pos: Tuple[float, float]) -> bool:
        """Try to drop the dragged piece; return True on success."""
        row, col = self._pixel_to_cell(*pos)
        success = False
        if self._drag_tray_idx is not None:
            success = bool(self.state.place(self._drag_tray_idx, row, col))
        self._drag_tray_idx = None
        self._drag_cells = None
        self._drag_colour = None
        self._redraw()
        if success and self.on_placed:
            self.on_placed()
        return success

    def cancel_drag(self) -> None:
        self._drag_tray_idx = None
        self._drag_cells = None
        self._drag_colour = None
        self._redraw()


# ===========================================================================
# PiecePreview – one draggable piece in the tray
# ===========================================================================

class PiecePreview(Widget):
    """Shows a single piece shape.  Initiates drag on touch-down."""

    def __init__(self, tray_idx: int, piece, board: BoardWidget, **kwargs):
        super().__init__(**kwargs)
        self.tray_idx = tray_idx
        self.piece = piece          # (name, cells, colour)
        self.board = board
        self._dragging = False

        self.bind(pos=self._redraw, size=self._redraw)

    def _redraw(self, *_):
        self.canvas.clear()
        if self.piece is None:
            return
        _, cells, colour = self.piece
        rows, cols = piece_size(cells)
        cs = min(self.width / (cols + 0.5),
                 self.height / (rows + 0.5)) * TRAY_SCALE
        gap = max(2, int(cs * 0.12))
        inner = cs - gap

        ox = self.x + (self.width - cols * cs) / 2
        oy = self.y + (self.height - rows * cs) / 2

        with self.canvas:
            for dr, dc in cells:
                x = ox + dc * cs + gap / 2
                # flip vertically so row-0 is at top
                y = oy + (rows - 1 - dr) * cs + gap / 2
                _draw_block(self.canvas, x, y, inner, inner, colour)

    # Touch -------------------------------------------------------------------

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        if self.piece is None:
            return False
        touch.grab(self)
        self._dragging = True
        _, cells, colour = self.piece
        self.board.start_drag(self.tray_idx, cells, colour, touch.pos)
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is not self:
            return False
        self.board.update_drag(touch.pos)
        return True

    def on_touch_up(self, touch):
        if touch.grab_current is not self:
            return False
        touch.ungrab(self)
        self._dragging = False
        placed = self.board.end_drag(touch.pos)
        if placed:
            self.piece = None
            self._redraw()
        return True


# ===========================================================================
# PieceTray – row of three PiecePreviews
# ===========================================================================

class PieceTray(BoxLayout):
    def __init__(self, state: GameState, board: BoardWidget, **kwargs):
        kwargs.setdefault("orientation", "horizontal")
        kwargs.setdefault("spacing", 12)
        kwargs.setdefault("padding", [8, 4, 8, 4])
        super().__init__(**kwargs)
        self.state = state
        self.board = board
        self._previews = []
        self._build()

    def _build(self):
        self.clear_widgets()
        self._previews = []
        for i, piece in enumerate(self.state.tray):
            pv = PiecePreview(i, piece, self.board)
            self._previews.append(pv)
            self.add_widget(pv)

    def refresh(self):
        """Sync previews with current tray state."""
        for i, pv in enumerate(self._previews):
            pv.piece = self.state.tray[i]
            pv._redraw()


# ===========================================================================
# ScoreBar
# ===========================================================================

class ScoreBar(BoxLayout):
    def __init__(self, state: GameState, **kwargs):
        kwargs.setdefault("orientation", "horizontal")
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", 64)
        kwargs.setdefault("padding", [16, 4])
        kwargs.setdefault("spacing", 8)
        super().__init__(**kwargs)
        self.state = state

        self._lbl_score = Label(
            text="0",
            font_size="28sp",
            bold=True,
            color=(1, 1, 1, 1),
        )
        self._lbl_best = Label(
            text="BEST: 0",
            font_size="16sp",
            color=(0.7, 0.7, 1.0, 1),
            size_hint_x=0.5,
            halign="right",
            valign="middle",
        )
        self._lbl_best.bind(size=self._lbl_best.setter("text_size"))
        self._lbl_mode = Label(
            text=state.mode.upper(),
            font_size="14sp",
            color=(0.5, 0.8, 1.0, 1),
            size_hint_x=0.4,
            halign="left",
            valign="middle",
        )
        self._lbl_mode.bind(size=self._lbl_mode.setter("text_size"))

        self.add_widget(self._lbl_mode)
        self.add_widget(self._lbl_score)
        self.add_widget(self._lbl_best)

    def refresh(self):
        self._lbl_score.text = f"{self.state.score:,}"
        self._lbl_best.text = f"BEST\n{self.state.best:,}"


# ===========================================================================
# GameOverOverlay
# ===========================================================================

class GameOverOverlay(FloatLayout):
    def __init__(self, on_restart, on_menu, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0, 0, 0, 0.70)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._resize_bg, size=self._resize_bg)

        box = BoxLayout(
            orientation="vertical",
            spacing=16,
            size_hint=(0.7, 0.4),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        box.add_widget(Label(
            text="GAME OVER",
            font_size="32sp",
            bold=True,
            color=(1, 0.3, 0.3, 1),
        ))
        btn_restart = _make_button("PLAY AGAIN", (0.2, 0.7, 0.3, 1))
        btn_restart.bind(on_release=lambda *_: on_restart())
        btn_menu = _make_button("MENU", (0.3, 0.5, 0.9, 1))
        btn_menu.bind(on_release=lambda *_: on_menu())
        box.add_widget(btn_restart)
        box.add_widget(btn_menu)
        self.add_widget(box)

    def _resize_bg(self, *_):
        self._bg.pos = self.pos
        self._bg.size = self.size


# ===========================================================================
# GameScreen
# ===========================================================================

class GameScreen(Screen):
    def __init__(self, mode: str = "Classic", **kwargs):
        super().__init__(**kwargs)
        self.mode = mode
        self._state = GameState(mode)
        self._overlay: Optional[GameOverOverlay] = None
        self._build()

    def _build(self):
        root = BoxLayout(orientation="vertical")

        # Background
        with root.canvas.before:
            Color(*BG_COLOR)
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *_: setattr(self._bg, "pos", root.pos),
                  size=lambda *_: setattr(self._bg, "size", root.size))

        # Score bar
        self._score_bar = ScoreBar(self._state)
        root.add_widget(self._score_bar)

        # Board
        self._board = BoardWidget(
            self._state,
            on_placed=self._on_placed,
            size_hint=(1, 1),
        )
        root.add_widget(self._board)

        # Tray
        self._tray = PieceTray(
            self._state, self._board,
            size_hint=(1, None),
            height=140,
        )
        root.add_widget(self._tray)

        self.add_widget(root)

    def _on_placed(self):
        self._score_bar.refresh()
        self._tray.refresh()
        self._board._redraw()
        if self._state.game_over:
            self._show_game_over()

    def _show_game_over(self):
        if self._overlay:
            return
        self._overlay = GameOverOverlay(
            on_restart=self._restart,
            on_menu=self._go_menu,
        )
        self.add_widget(self._overlay)

    def _restart(self):
        if self._overlay:
            self.remove_widget(self._overlay)
            self._overlay = None
        self._state.reset()
        self._score_bar.refresh()
        self._tray.refresh()
        self._board._redraw()

    def _go_menu(self):
        if self._overlay:
            self.remove_widget(self._overlay)
            self._overlay = None
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "menu"

    def on_pre_enter(self, *_):
        """Called each time this screen becomes active."""
        self._restart()


# ===========================================================================
# MenuScreen
# ===========================================================================

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build()

    def _build(self):
        root = BoxLayout(orientation="vertical", padding=32, spacing=20)
        with root.canvas.before:
            Color(*BG_COLOR)
            bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *_: setattr(bg, "pos", root.pos),
                  size=lambda *_: setattr(bg, "size", root.size))

        root.add_widget(Label(
            text="BLOCK[color=#4fc3f7]OVERLOAD[/color]",
            markup=True,
            font_size="38sp",
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=0.25,
        ))
        root.add_widget(Label(
            text="Choose a mode",
            font_size="18sp",
            color=(0.7, 0.7, 1, 1),
            size_hint_y=0.1,
        ))

        button_specs = [
            ("Micro",   "6×6  – Lightning fast",     (0.92, 0.26, 0.21, 1)),
            ("Classic", "8×8  – The classic arena",  (0.13, 0.59, 0.95, 1)),
            ("Mega",    "10×10 – Strategic & deep",  (0.30, 0.85, 0.39, 1)),
        ]
        for mode, subtitle, colour in button_specs:
            btn = _make_button(
                f"[b]{mode}[/b]\n[size=14]{subtitle}[/size]",
                colour, markup=True, font_size="20sp",
            )
            btn.bind(on_release=lambda _, m=mode: self._start(m))
            root.add_widget(btn)

        root.add_widget(Widget(size_hint_y=0.15))  # spacer
        self.add_widget(root)

    def _start(self, mode: str):
        sm = self.manager
        gs: GameScreen = sm.get_screen("game")  # type: ignore[assignment]
        gs.mode = mode
        gs._state = GameState(mode)
        gs._score_bar.state = gs._state
        gs._board.state = gs._state
        gs._tray.state = gs._state
        gs._tray._build()
        gs._score_bar.refresh()
        gs._board._redraw()
        sm.transition = SlideTransition(direction="left")
        sm.current = "game"


# ===========================================================================
# Utility – styled button
# ===========================================================================

def _make_button(text: str, colour: tuple, markup: bool = False,
                 font_size: str = "18sp") -> Widget:
    from kivy.uix.button import Button
    btn = Button(
        text=text,
        markup=markup,
        font_size=font_size,
        background_normal="",
        background_color=colour,
        color=(1, 1, 1, 1),
        bold=True,
        size_hint=(1, None),
        height=72,
    )
    return btn


# ===========================================================================
# ScreenManager builder (called from main.py)
# ===========================================================================

def build_screen_manager() -> ScreenManager:
    sm = ScreenManager()
    sm.add_widget(MenuScreen(name="menu"))
    sm.add_widget(GameScreen(name="game"))
    return sm
