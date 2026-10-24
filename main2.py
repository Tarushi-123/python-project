"""
RailMotion — Animated Railway Booking Desktop Application
=========================================================

A modern railway booking demo built with Python and Tkinter, featuring an
animated train navigation, a dark/light theme toggle, a multi-passenger
booking flow with CAPTCHA-protected simulated payment, and cancellation
with a 7-day simulated refund notice.

Run it with:

    python main.py

Optional self test (runs an automated navigation / validation test and exits):

    python main.py --smoke

DEMO NOTICE
-----------
All accounts, train schedules, fares and bookings in this project are
FICTIONAL and live only in memory. Nothing is written to disk, no real
ticket can be purchased, and accounts disappear when the program closes.
This is NOT production authentication and must never be used for real data.

Project sections
----------------
  1.  Imports
  2.  Theme, fonts and shared styling helpers
  3.  Demo data (cities, trains, classes)
  4.  Reusable widgets (buttons, cards, scrollable frame, form helpers)
  5.  TrainRenderer — draws the train, tracks and background on a Canvas
  6.  Pages — Intro, Home, Login, Sign Up, Tickets, Bookings, Offers
  7.  RailMotionApp — window shell, navigation and animation state machine
  7b. BookingFlow / PaymentWindow / cancellation windows
  8.  Automated smoke test
  9.  Entry point
"""

from __future__ import annotations

import argparse
import datetime as dt
import math
import random
import re
import sys
import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox, ttk


# =====================================================================
# 2. THEME, FONTS AND SHARED STYLING HELPERS
# =====================================================================

# --- colour palettes (dark is the default, light is IRCTC-inspired) ----
# Every key below is exported as a module-level global, so widgets created
# at any time always read the colours of the theme that is active right now.
THEMES = {
    "dark": {
        "BG": "#07111F", "PANEL": "#111F32", "PANEL2": "#1B2C42",
        "CYAN": "#45E6D0", "TEXT": "#F2F7FC", "MUTED": "#94A9C0",
        "PURPLE": "#BBA4FF", "ORANGE": "#FFB866", "LINE": "#24405C",
        "DANGER": "#FF8FA3",
        # buttons
        "BTN_PRIMARY_BG": "#45E6D0", "BTN_PRIMARY_FG": "#05201C",
        "BTN_PRIMARY_HOVER": "#7BF2E3",
        "BTN_GHOST_BG": "#1B2C42", "BTN_GHOST_FG": "#F2F7FC",
        "BTN_GHOST_HOVER": "#27455F",
        "BTN_DANGER_BG": "#3A2030", "BTN_DANGER_FG": "#FFD3DA",
        "BTN_DANGER_HOVER": "#4E2740",
        "SEG_ON_BG": "#45E6D0", "SEG_ON_FG": "#05201C",
        "SEG_ON_HOVER": "#7BF2E3",
        "SEG_OFF_BG": "#1B2C42", "SEG_OFF_FG": "#94A9C0",
        "SEG_OFF_HOVER": "#27455F",
        # train canvas
        "SKY_TOP": "#07111F", "SKY_BOTTOM": "#12283D",
        "STARS": ("#94A9C0", "#94A9C0", "#CFE3F5", "#45E6D0"),
        "MOON_GLOW": "#14314A", "MOON": "#DCEBF8",
        "SKYLINE": "#0B1B2E", "SKYLINE_WIN": "#1B3E5E",
        "SLEEPER": "#152840", "SLEEPER_EDGE": "#1F3A57",
        "RAIL_GLOW": "#45E6D0", "RAIL": "#2E4F6B",
        "BODY": "#1B2C42", "WIN_FILL": "#0B2436", "WIN_LINE": "#2A4A66",
        "WHEEL": "#0A1522", "WHEEL_HUB": "#94A9C0",
        "WINDSCREEN": "#0E3A44", "COUPLER": "#2A425C",
        "HEADLIGHT": "#FFF6D8", "HEADLIGHT_DIM": "#6E5A38",
        "BEAM": "#FFE7A8",
    },
    "light": {
        "BG": "#EDF1F6", "PANEL": "#FFFFFF", "PANEL2": "#F4F7FB",
        "CYAN": "#12A5B8", "TEXT": "#12263F", "MUTED": "#5A6B80",
        "PURPLE": "#6A5AE0", "ORANGE": "#D97706", "LINE": "#D7DFEA",
        "DANGER": "#C62828",
        # buttons (professional railway blue)
        "BTN_PRIMARY_BG": "#1565C0", "BTN_PRIMARY_FG": "#FFFFFF",
        "BTN_PRIMARY_HOVER": "#1E7BE5",
        "BTN_GHOST_BG": "#E8EDF5", "BTN_GHOST_FG": "#12263F",
        "BTN_GHOST_HOVER": "#D8E0EC",
        "BTN_DANGER_BG": "#FDECEC", "BTN_DANGER_FG": "#B3261E",
        "BTN_DANGER_HOVER": "#F8D9D9",
        "SEG_ON_BG": "#1565C0", "SEG_ON_FG": "#FFFFFF",
        "SEG_ON_HOVER": "#1E7BE5",
        "SEG_OFF_BG": "#E8EDF5", "SEG_OFF_FG": "#5A6B80",
        "SEG_OFF_HOVER": "#D8E0EC",
        # train canvas
        "SKY_TOP": "#DCE7F4", "SKY_BOTTOM": "#F7FAFD",
        "STARS": ("#9FB3CB", "#9FB3CB", "#7E93AD", "#12A5B8"),
        "MOON_GLOW": "#EAF1FA", "MOON": "#FFFFFF",
        "SKYLINE": "#D5DFEC", "SKYLINE_WIN": "#C0CEDF",
        "SLEEPER": "#E9EEF5", "SLEEPER_EDGE": "#CBD6E4",
        "RAIL_GLOW": "#12A5B8", "RAIL": "#8FA1B6",
        "BODY": "#FFFFFF", "WIN_FILL": "#E3EEF6", "WIN_LINE": "#BCCCDD",
        "WHEEL": "#44556B", "WHEEL_HUB": "#6B7C91",
        "WINDSCREEN": "#D3E9F0", "COUPLER": "#93A3B8",
        "HEADLIGHT": "#FFFDF5", "HEADLIGHT_DIM": "#D9CDA8",
        "BEAM": "#FFF3C9",
    },
}

PALETTE_KEYS = list(THEMES["dark"].keys())
THEME_NAME = "dark"        # current theme (session preference)


def apply_theme_globals(name: str) -> None:
    """Publish every colour of *name* as a module-level global."""
    for _key, _value in THEMES[name].items():
        globals()[_key] = _value
    # carriage accents follow the active palette
    globals()["CARRIAGE_ACCENTS"] = [
        globals()["CYAN"], globals()["PURPLE"], globals()["ORANGE"],
        globals()["CYAN"], globals()["PURPLE"], globals()["ORANGE"],
    ]


apply_theme_globals(THEME_NAME)


def button_palette(kind: str):
    """(background, foreground, hover) for a themed button kind."""
    if kind == "ghost":
        return (BTN_GHOST_BG, BTN_GHOST_FG, BTN_GHOST_HOVER)
    if kind == "danger":
        return (BTN_DANGER_BG, BTN_DANGER_FG, BTN_DANGER_HOVER)
    if kind == "seg_on":
        return (SEG_ON_BG, SEG_ON_FG, SEG_ON_HOVER)
    if kind == "seg_off":
        return (SEG_OFF_BG, SEG_OFF_FG, SEG_OFF_HOVER)
    return (BTN_PRIMARY_BG, BTN_PRIMARY_FG, BTN_PRIMARY_HOVER)


FONT_FAMILY = "Segoe UI"  # replaced at start-up when unavailable

# Carriage accents shown on the train, in carriage order.
CARRIAGE_ACCENTS = [CYAN, PURPLE, ORANGE, CYAN, PURPLE, ORANGE]


def init_font_family(root: tk.Tk) -> None:
    """Pick the best available UI font (Segoe UI on Windows)."""
    global FONT_FAMILY
    try:
        available = {f.lower(): f for f in tkfont.families(root)}
    except tk.TclError:
        return
    for candidate in (
        "segoe ui",
        "sf pro display",
        "helvetica neue",
        "helvetica",
        "arial",
        "liberation sans",
        "dejavu sans",
    ):
        if candidate in available:
            FONT_FAMILY = available[candidate]
            return


def fnt(size: int, weight: str = "normal"):
    """Shorthand for a themed font tuple."""
    return (FONT_FAMILY, size, weight)


def mix(colour_a: str, colour_b: str, t: float) -> str:
    """Linearly blend two #RRGGBB colours (used for the sky gradient)."""
    a = [int(colour_a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(colour_b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02X%02X%02X" % tuple(
        int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3)
    )


def rounded_rect(canvas: tk.Canvas, x1, y1, x2, y2, radius=10, **kwargs):
    """Draw a rounded rectangle using a smooth Canvas polygon."""
    r = min(radius, abs(x2 - x1) / 2.0, abs(y2 - y1) / 2.0)
    points = [
        x1 + r, y1,
        x2 - r, y1,
        x2, y1,
        x2, y1 + r,
        x2, y2 - r,
        x2, y2,
        x2 - r, y2,
        x1 + r, y2,
        x1, y2,
        x1, y2 - r,
        x1, y1 + r,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, splinesteps=12, **kwargs)


class RailButton(tk.Button):
    """Themed button with hover feedback (colours follow the active theme)."""

    def __init__(self, parent, text, command=None, kind="primary", **kwargs):
        self.kind = kind
        bg, fg, hover_bg = button_palette(kind)
        kwargs.setdefault("padx", 18)
        kwargs.setdefault("pady", 8)
        super().__init__(
            parent,
            text=text,
            command=command,
            font=fnt(10, "bold"),
            bg=bg,
            fg=fg,
            activebackground=hover_bg,
            activeforeground=fg,
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            takefocus=True,
            **kwargs,
        )
        self._normal_bg = bg
        self._hover_bg = hover_bg
        self.bind("<Enter>", lambda _e: self.configure(bg=self._hover_bg))
        self.bind("<Leave>", lambda _e: self.configure(bg=self._normal_bg))

    def apply_theme(self) -> None:
        """Re-read the palette (called when the theme changes)."""
        bg, fg, hover_bg = button_palette(self.kind)
        self._normal_bg = bg
        self._hover_bg = hover_bg
        self.configure(bg=bg, fg=fg, activebackground=hover_bg,
                       activeforeground=fg)


class Card(tk.Frame):
    """Clean rectangular card with a coloured accent strip."""

    def __init__(self, parent, accent=None, bg=None, pad=16):
        accent = CYAN if accent is None else accent
        bg = PANEL if bg is None else bg
        super().__init__(parent, bg=bg, highlightthickness=1, highlightbackground=LINE)
        self.strip = tk.Frame(self, bg=accent, width=4)
        self.strip.pack(side="left", fill="y")
        self.body = tk.Frame(self, bg=bg)
        self.body.pack(side="left", fill="both", expand=True, padx=pad, pady=pad)


class ScrollableFrame(tk.Frame):
    """A vertically scrollable page body (Canvas + inner Frame).

    Mouse-wheel scrolling is handled by the application-wide handler
    (``RailMotionApp._global_wheel``), which finds the innermost
    ScrollableFrame under the pointer — so the wheel works over labels,
    cards, entries and every other child widget, and nested scroll areas
    never react twice.
    """

    def __init__(self, parent, bg=None):
        bg = BG if bg is None else bg
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.bar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.bar.set)
        self.bar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.body = tk.Frame(self.canvas, bg=bg)
        self._window = self.canvas.create_window((0, 0), window=self.body, anchor="nw")
        self.body.bind(
            "<Configure>",
            lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfigure(self._window, width=e.width),
        )

    def _on_wheel(self, event):
        delta = 0
        if getattr(event, "num", None) == 4:
            delta = 1
        elif getattr(event, "num", None) == 5:
            delta = -1
        elif event.delta:
            delta = int(event.delta / 120) or (1 if event.delta > 0 else -1)
        if delta:
            self.canvas.yview_scroll(-delta, "units")

    def scroll_by_event(self, event) -> None:
        """Scroll only when the content actually overflows the viewport."""
        region = self.canvas.bbox("all")
        if not region:
            return
        if region[3] - region[1] <= self.canvas.winfo_height() + 1:
            return                      # fits on screen — do not force scroll
        self._on_wheel(event)


def make_label(parent, text, size=12, colour=None, weight="normal", bg=None,
                **kwargs):
    colour = TEXT if colour is None else colour
    bg = BG if bg is None else bg
    return tk.Label(
        parent, text=text, font=fnt(size, weight), fg=colour, bg=bg, **kwargs
    )


def make_adaptive_label(parent, text, size=12, colour=None, weight="normal",
                        bg=None, margin=8, **kwargs):
    """A label that re-wraps its text to the width it is actually given.

    The wrap width is measured on the parent frame (not the label itself),
    so a long notice can never be clipped at any window size or theme.
    """
    kwargs.pop("wraplength", None)
    label = make_label(parent, text, size, colour, weight, bg, **kwargs)

    def _fit(event):
        wanted = max(80, int(event.width) - margin)
        try:
            current = int(float(label.cget("wraplength") or 0))
        except (TypeError, ValueError):
            current = 0
        if abs(current - wanted) > 6:          # avoid Configure loops
            label.configure(wraplength=wanted)

    parent.bind("<Configure>", _fit, add="+")
    return label


def make_entry(parent, textvariable=None, show=None):
    return tk.Entry(
        parent,
        textvariable=textvariable,
        show=show or "",
        font=fnt(11),
        bg=PANEL2,
        fg=TEXT,
        insertbackground=TEXT,
        relief="flat",
        bd=7,
        highlightthickness=1,
        highlightbackground=LINE,
        highlightcolor=CYAN,
    )


# =====================================================================
# 3. DEMO DATA (fictional — never a real railway service)
# =====================================================================

CITIES = [
    "Chennai",
    "Bengaluru",
    "Coimbatore",
    "Mysuru",
    "Hyderabad",
    "Mumbai",
    "Pune",
]

TRAVEL_CLASSES = ["AC First Class", "AC Sleeper", "Sleeper", "General"]

SAMPLE_TRAINS = [
    {"name": "Coastal Express", "number": "90011", "source": "Chennai", "dest": "Bengaluru",
     "time": "06:30 AM", "fare": 450},
    {"name": "Southern Star", "number": "90022", "source": "Chennai", "dest": "Coimbatore",
     "time": "08:45 AM", "fare": 620},
    {"name": "City Link", "number": "90033", "source": "Bengaluru", "dest": "Mysuru",
     "time": "10:15 AM", "fare": 280},
    {"name": "Deccan Runner", "number": "90044", "source": "Hyderabad", "dest": "Chennai",
     "time": "07:20 PM", "fare": 700},
    {"name": "Western Connect", "number": "90055", "source": "Mumbai", "dest": "Pune",
     "time": "09:00 AM", "fare": 350},
]

DEMO_EMAIL = "demo@railmotion.in"
DEMO_PASSWORD = "rail123"
DEMO_NAME = "Demo Traveller"

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

PAGE_TITLES = {
    "intro": "Start",
    "home": "Home",
    "tickets": "Tickets",
    "bookings": "Bookings",
    "login": "Login",
    "signup": "Sign Up",
    "offers": "Offers",
}
CARRIAGE_PAGES = ["home", "tickets", "bookings", "login", "signup", "offers"]


# =====================================================================
# 5. TRAIN RENDERER — draws tracks, background and the train on a Canvas
# =====================================================================

class TrainRenderer:
    """Draws the whole train as Canvas items sharing the tag ``train``.

    Every component (engine + six carriages) is created with the tag
    ``train`` so a single ``canvas.move("train", dx, 0)`` translates the
    complete train — the engine can never drift away from the carriages.
    Carriage hit boxes are stored relative to the train origin, so click
    detection is ``box + train_x``.
    """

    BASE_CARRIAGE_W = 150
    BASE_CARRIAGE_H = 70
    BASE_GAP = 16
    BASE_ENGINE_W = 195
    BASE_TOTAL = 6 * BASE_CARRIAGE_W + 6 * BASE_GAP + BASE_ENGINE_W  # 1191

    def __init__(self, canvas: tk.Canvas, width: int, height: int, intro: bool):
        self.canvas = canvas
        self.width = max(10, int(width))
        self.height = max(10, int(height))
        self.intro = intro

        if intro:
            scale = (self.width - 48) / float(self.BASE_TOTAL)
            scale = max(0.55, min(1.15, scale))
        else:  # compact header — leave comfortable margins
            scale = (self.width - 48) / 1330.0
            scale = max(0.50, min(1.0, scale))
        self.s = scale

        self.carriage_w = int(self.BASE_CARRIAGE_W * scale)
        self.carriage_h = int(self.BASE_CARRIAGE_H * scale)
        self.gap = int(self.BASE_GAP * scale)
        self.engine_w = int(self.BASE_ENGINE_W * scale)
        self.wheel_r = max(5, int(11 * scale))
        self.rail_y = self.height - 22
        self.sleeper_spacing = max(18, int(34 * scale))
        self.total_w = (6 * self.carriage_w) + (6 * self.gap) + self.engine_w
        self.park_x = max(12.0, (self.width - self.total_w) / 2.0)

        self.angle = 0.0
        self.selected = None
        self.hovered = None
        self.spokes = []        # (item, rel_cx, cy, radius) for wheel rotation
        self.outlines = {}      # page -> body outline item
        self.glows = {}         # page -> highlight glow item
        self.boxes = {}         # page -> (x1, y1, x2, y2) relative to train origin
        self.beam_item = None
        self.headlight_glow = None

    # -----------------------------------------------------------------
    # background
    # -----------------------------------------------------------------
    def draw_background(self) -> None:
        c = self.canvas
        c.delete("bg")
        w, h = self.width, self.height
        rail_y = self.rail_y

        # night-sky gradient
        bands = 40
        for i in range(bands):
            t = i / float(bands - 1)
            y1 = int(h * i / bands)
            y2 = int(h * (i + 1) / bands) + 1
            c.create_rectangle(
                0, y1, w, y2, fill=mix(SKY_TOP, SKY_BOTTOM, t),
                outline="", tags="bg"
            )

        # stars
        rnd = random.Random(int(w) * 7 + int(h))
        for _ in range(max(20, w // 26)):
            x = rnd.randrange(0, max(2, w))
            y = rnd.randrange(3, max(4, int(h * 0.55)))
            r = rnd.choice([1, 1, 1, 2])
            colour = rnd.choice(list(STARS))
            c.create_oval(x, y, x + r, y + r, fill=colour, outline="", tags="bg")

        # moon with soft glow
        mx, my = int(w * 0.82), int(h * 0.17)
        mr = max(10, int(16 * self.s))
        c.create_oval(
            mx - mr * 2, my - mr * 2, mx + mr * 2, my + mr * 2,
            fill=MOON_GLOW, outline="", stipple="gray25", tags="bg",
        )
        c.create_oval(
            mx - mr, my - mr, mx + mr, my + mr,
            fill=MOON, outline="", tags="bg",
        )

        # distant skyline (parallax layer, tag "skyline")
        rnd2 = random.Random(42)
        x = -60
        while x < w + 240:
            bw = rnd2.randrange(26, 62)
            bh = rnd2.randrange(22, 76)
            top = rail_y - 6 - bh
            c.create_rectangle(x, top, x + bw, rail_y - 6,
                               fill=SKYLINE, outline="",
                               tags=("bg", "skyline"))
            for wx in range(x + 5, x + bw - 4, 10):
                for wy in range(top + 6, rail_y - 12, 11):
                    if rnd2.random() < 0.35:
                        c.create_rectangle(wx, wy, wx + 3, wy + 3,
                                           fill=SKYLINE_WIN, outline="",
                                           tags=("bg", "skyline"))
            x += bw + rnd2.randrange(6, 18)

        # sleepers (scroll while the train moves)
        spacing = self.sleeper_spacing
        x = -spacing
        while x < w + spacing:
            c.create_rectangle(
                x, rail_y - 3, x + int(spacing * 0.55), rail_y + 13,
                fill=SLEEPER, outline=SLEEPER_EDGE, tags=("bg", "sleepers"),
            )
            x += spacing

        # rails + rail glow
        c.create_rectangle(0, rail_y - 1, w, rail_y + 2,
                           fill=RAIL_GLOW, outline="", stipple="gray50",
                           tags="bg")
        c.create_rectangle(0, rail_y, w, rail_y + 3,
                           fill=RAIL, outline="", tags="bg")
        c.create_rectangle(0, rail_y + 7, w, rail_y + 10,
                           fill=RAIL, outline="", tags="bg")

    # -----------------------------------------------------------------
    # train
    # -----------------------------------------------------------------
    def draw_train(self, train_x: float) -> None:
        c = self.canvas
        c.delete("train")
        self.spokes = []
        self.outlines = {}
        self.glows = {}
        self.boxes = {}
        self.beam_item = None
        self.headlight_glow = None

        rel = 0.0
        for index, page in enumerate(CARRIAGE_PAGES):
            self._draw_carriage(train_x + rel, rel, page, index)
            rel += self.carriage_w + self.gap
        self._draw_engine(train_x + rel, rel)

    def _draw_carriage(self, abs_x: float, rel_x: float, page: str, index: int) -> None:
        c = self.canvas
        s = self.s
        accent = CARRIAGE_ACCENTS[index % len(CARRIAGE_ACCENTS)]
        cw, ch = self.carriage_w, self.carriage_h

        wheel_cy = self.rail_y - self.wheel_r
        body_bottom = wheel_cy - self.wheel_r + int(6 * s)
        body_top = body_bottom - ch

        # highlight glow (hidden until selected / hovered)
        glow = rounded_rect(
            c, abs_x - 5 * s, body_top - 5 * s, abs_x + cw + 5 * s,
            body_bottom + self.wheel_r + 5 * s, radius=12 * s,
            fill=accent, outline=accent, width=1, stipple="gray25",
            state="hidden", tags="train",
        )
        self.glows[page] = glow

        # body
        body = rounded_rect(
            c, abs_x, body_top, abs_x + cw, body_bottom, radius=9 * s,
            fill=BODY, outline=LINE, width=1, tags="train",
        )
        self.outlines[page] = body

        # roof cap
        rounded_rect(
            c, abs_x + 6 * s, body_top - 3 * s, abs_x + cw - 6 * s,
            body_top + 3 * s, radius=4 * s, fill=accent, outline="",
            tags="train",
        )

        # window band (3 windows)
        win_top = body_top + 8 * s
        win_h = max(6, ch * 0.28)
        usable = cw - 16 * s
        cell_w = (usable - 8 * s) / 3.0
        for i in range(3):
            wx = abs_x + 8 * s + i * (cell_w + 4 * s)
            rounded_rect(
                c, wx, win_top, wx + cell_w, win_top + win_h, radius=3 * s,
                fill=WIN_FILL, outline=WIN_LINE, width=1, tags="train",
            )

        # accent underline
        c.create_rectangle(
            abs_x + 8 * s, body_bottom - 5 * s, abs_x + cw - 8 * s,
            body_bottom - 3 * s, fill=accent, outline="", tags="train",
        )

        # icon + page name
        icon_size = max(10, int(20 * s))
        icon_cx = abs_x + 8 * s + icon_size / 2.0
        icon_cy = body_top + ch * 0.70
        self._draw_icon(page, icon_cx, icon_cy, icon_size, accent)
        c.create_text(
            abs_x + 8 * s + icon_size + 5 * s, icon_cy,
            text=PAGE_TITLES[page].upper(), anchor="w",
            font=fnt(max(8, int(10 * s)), "bold"), fill=TEXT, tags="train",
        )

        # coupler to the next vehicle
        c.create_rectangle(
            abs_x + cw, wheel_cy - 3 * s, abs_x + cw + self.gap, wheel_cy + 2 * s,
            fill=COUPLER, outline="", tags="train",
        )

        # wheels
        for fraction in (0.24, 0.76):
            self._draw_wheel(abs_x + cw * fraction, wheel_cy)

        # clickable hit box (coordinates relative to the train origin)
        self.boxes[page] = (
            rel_x - 4 * s,
            body_top - 6 * s,
            rel_x + cw + self.gap * 0.6,
            body_bottom + self.wheel_r + 5 * s,
        )

    def _draw_engine(self, abs_x: float, rel_x: float) -> None:
        c = self.canvas
        s = self.s
        ew = self.engine_w
        ch = self.carriage_h

        wheel_cy = self.rail_y - self.wheel_r
        body_bottom = wheel_cy - self.wheel_r + int(6 * s)
        cab_h = int(ch * 1.15)
        body_top = body_bottom - cab_h
        cab_w = int(ew * 0.58)

        # main body with a pointed nose facing right
        c.create_polygon(
            abs_x, body_top,
            abs_x + cab_w, body_top,
            abs_x + ew, body_top + int(cab_h * 0.45),
            abs_x + ew, body_bottom,
            abs_x, body_bottom,
            fill=BODY, outline=CYAN, width=1, smooth=False, tags="train",
        )
        # cab roof
        rounded_rect(
            c, abs_x + 5 * s, body_top - 4 * s, abs_x + cab_w - 5 * s,
            body_top + 2 * s, radius=4 * s, fill=CYAN, outline="", tags="train",
        )
        # windscreen
        c.create_polygon(
            abs_x + cab_w - 3 * s, body_top + 8 * s,
            abs_x + cab_w + int(ew * 0.16), body_top + int(cab_h * 0.34),
            abs_x + cab_w - 3 * s, body_top + int(cab_h * 0.34),
            fill=WINDSCREEN, outline=CYAN, width=1, tags="train",
        )
        # side window
        rounded_rect(
            c, abs_x + cab_w * 0.30, body_top + 9 * s,
            abs_x + cab_w * 0.30 + int(ew * 0.064),
            body_top + 9 * s + int(cab_h * 0.24),
            radius=3 * s, fill=WIN_FILL, outline=WIN_LINE, width=1, tags="train",
        )
        # livery stripe
        c.create_rectangle(
            abs_x + 8 * s, body_bottom - 13 * s, abs_x + ew - int(10 * s),
            body_bottom - 9 * s, fill=CYAN, outline="", tags="train",
        )
        # name plate
        c.create_text(
            abs_x + cab_w * 0.55, body_bottom - int(22 * s),
            text="RAILMOTION", font=fnt(max(6, int(8 * s)), "bold"),
            fill=MUTED, tags="train",
        )

        # headlight + glow + beam
        hl_x1 = abs_x + ew - int(15 * s)
        hl_y1 = body_bottom - int(24 * s)
        hl_x2 = abs_x + ew - int(4 * s)
        hl_y2 = body_bottom - int(13 * s)
        self.headlight_glow = c.create_oval(
            hl_x1 - 6 * s, hl_y1 - 6 * s, hl_x2 + 6 * s, hl_y2 + 6 * s,
            fill=ORANGE, outline="", stipple="gray25", tags="train",
        )
        c.create_oval(hl_x1, hl_y1, hl_x2, hl_y2,
                      fill=HEADLIGHT, outline=ORANGE, width=1, tags="train")
        self.beam_item = c.create_polygon(
            hl_x2, hl_y1,
            hl_x2 + int(120 * s), hl_y1 - int(26 * s),
            hl_x2 + int(120 * s), hl_y2 + int(26 * s),
            hl_x2, hl_y2,
            fill=BEAM, outline="", stipple="gray25",
            state="hidden", tags="train",
        )

        # wheels
        for fraction in (0.20, 0.52, 0.82):
            self._draw_wheel(abs_x + ew * fraction, wheel_cy, radius=self.wheel_r * 1.15)

    def _draw_wheel(self, cx: float, cy: float, radius: float = None) -> None:
        c = self.canvas
        r = radius if radius is not None else self.wheel_r
        c.create_oval(cx - r, cy - r, cx + r, cy + r,
                      fill=WHEEL, outline=WHEEL_HUB, width=1, tags="train")
        hub = max(1.5, r * 0.28)
        c.create_oval(cx - hub, cy - hub, cx + hub, cy + hub,
                      fill=WHEEL_HUB, outline="", tags="train")
        spoke = c.create_line(cx - r * 0.7, cy, cx + r * 0.7, cy,
                              fill=CYAN, width=1, tags="train")
        self.spokes.append((spoke, cx, cy, r * 0.7))

    def _draw_icon(self, page: str, cx: float, cy: float, size: int, colour: str) -> None:
        """Small Canvas icon drawn inside each carriage."""
        c = self.canvas
        s = size / 2.0
        w = max(1, int(s * 0.24))
        if page == "home":
            c.create_polygon(cx - s, cy - 0.15 * s, cx, cy - s, cx + s, cy - 0.15 * s,
                             fill=colour, outline="", tags="train")
            c.create_rectangle(cx - 0.7 * s, cy - 0.15 * s, cx + 0.7 * s, cy + s,
                               fill=colour, outline="", tags="train")
            c.create_rectangle(cx - 0.22 * s, cy + 0.25 * s, cx + 0.22 * s, cy + s,
                               fill=BODY, outline="", tags="train")
        elif page == "tickets":
            rounded_rect(c, cx - s, cy - 0.62 * s, cx + s, cy + 0.62 * s,
                         radius=2, fill="", outline=colour, width=w, tags="train")
            c.create_line(cx, cy - 0.62 * s, cx, cy + 0.62 * s,
                          fill=colour, width=w, dash=(2, 2), tags="train")
        elif page == "bookings":
            for dy in (-0.55 * s, 0.0, 0.55 * s):
                c.create_oval(cx - 0.9 * s, cy + dy - 0.14 * s,
                              cx - 0.55 * s, cy + dy + 0.14 * s,
                              fill=colour, outline="", tags="train")
                c.create_line(cx - 0.32 * s, cy + dy, cx + 0.95 * s, cy + dy,
                              fill=colour, width=w, tags="train")
        elif page == "login":
            c.create_rectangle(cx - 0.15 * s, cy - s, cx + 0.85 * s, cy + s,
                               fill="", outline=colour, width=w, tags="train")
            c.create_line(cx - s, cy, cx + 0.25 * s, cy,
                          fill=colour, width=w, tags="train")
            c.create_polygon(cx + 0.8 * s, cy, cx + 0.28 * s, cy - 0.34 * s,
                             cx + 0.28 * s, cy + 0.34 * s,
                             fill=colour, outline="", tags="train")
        elif page == "signup":
            c.create_oval(cx - 0.36 * s, cy - s, cx + 0.36 * s, cy - 0.28 * s,
                          fill=colour, outline="", tags="train")
            c.create_arc(cx - 0.8 * s, cy - 0.30 * s, cx + 0.8 * s, cy + 1.15 * s,
                         start=180, extent=180, style="arc",
                         outline=colour, width=w, tags="train")
        else:  # offers — price tag
            c.create_polygon(cx - s, cy - 0.7 * s, cx + 0.3 * s, cy - 0.7 * s,
                             cx + s, cy, cx + 0.3 * s, cy + 0.7 * s,
                             cx - s, cy + 0.7 * s,
                             fill="", outline=colour, width=w, tags="train")
            c.create_oval(cx - 0.6 * s, cy - 0.16 * s, cx - 0.26 * s,
                          cy + 0.18 * s, fill=colour, outline="", tags="train")

    # -----------------------------------------------------------------
    # animation helpers
    # -----------------------------------------------------------------
    def move_train(self, dx: float) -> None:
        self.canvas.move("train", dx, 0)

    def spin(self, train_x: float, dx: float) -> None:
        """Rotate every wheel spoke while the train rolls."""
        self.angle = (self.angle + dx * 2.2) % 360.0
        rad = math.radians(self.angle)
        cos_a = math.cos(rad) * 1.0
        sin_a = math.sin(rad)
        for item, rel_cx, cy, r in self.spokes:
            cx = rel_cx + train_x
            self.canvas.coords(
                item,
                cx - r * cos_a, cy - r * sin_a,
                cx + r * cos_a, cy + r * sin_a,
            )

    def set_beam(self, visible: bool) -> None:
        if self.beam_item is not None:
            self.canvas.itemconfigure(self.beam_item,
                                      state="normal" if visible else "hidden")
        if self.headlight_glow is not None:
            self.canvas.itemconfigure(
                self.headlight_glow,
                fill=ORANGE if visible else HEADLIGHT_DIM,
            )

    def set_highlight(self, page) -> None:
        self.selected = page
        self._apply_states()

    def set_hover(self, page) -> None:
        self.hovered = page
        self._apply_states()

    def _apply_states(self) -> None:
        for page, body in self.outlines.items():
            if page == self.selected:
                self.canvas.itemconfigure(body, outline=CYAN, width=2)
            elif page == self.hovered:
                self.canvas.itemconfigure(body, outline=PURPLE, width=2)
            else:
                self.canvas.itemconfigure(body, outline=LINE, width=1)
        for page, glow in self.glows.items():
            if page == self.selected:
                self.canvas.itemconfigure(glow, state="normal",
                                          fill=CYAN, outline=CYAN)
            elif page == self.hovered:
                self.canvas.itemconfigure(glow, state="normal",
                                          fill=PURPLE, outline=PURPLE)
            else:
                self.canvas.itemconfigure(glow, state="hidden")


# =====================================================================
# 6. PAGES
# =====================================================================

class PageBase(tk.Frame):
    """Base class for every page of the application."""

    def __init__(self, parent, app: "RailMotionApp"):
        super().__init__(parent, bg=BG)
        self.app = app
        self.build()

    # -- small form helpers ------------------------------------------
    def field(self, parent, row, col, label_text, factory, spans=1):
        parent.grid_columnconfigure(col, weight=1, uniform="form")
        cell = tk.Frame(parent, bg=BG)
        cell.grid(row=row, column=col, columnspan=spans, sticky="ew",
                  padx=10, pady=7)
        make_label(cell, label_text, 9, MUTED, "bold", bg=BG).pack(
            anchor="w", fill="x")
        widget = factory(cell)
        widget.pack(fill="x", pady=(4, 0))
        return widget

    def heading(self, parent, title, subtitle=None):
        make_label(parent, title, 26, TEXT, "bold", bg=BG).pack(
            anchor="w", pady=(0, 4))
        if subtitle:
            make_label(parent, subtitle, 12, MUTED, bg=BG).pack(anchor="w")

    def note(self, parent, text, colour=MUTED, size=9):
        make_label(parent, text, size, colour, bg=BG, justify="left").pack(
            anchor="w", pady=(8, 0))

    def build(self):  # pragma: no cover - overridden
        raise NotImplementedError


class IntroPage(PageBase):
    """Start-up screen: title, subtitle and instruction."""

    def build(self):
        wrap = tk.Frame(self, bg=BG)
        wrap.pack(fill="both", expand=True)

        title_row = tk.Frame(wrap, bg=BG)
        title_row.pack(pady=(36, 2))
        make_label(title_row, "RAIL", 40, TEXT, "bold", bg=BG).pack(side="left")
        make_label(title_row, "MOTION", 40, CYAN, "bold", bg=BG).pack(side="left")

        make_label(wrap, "YOUR JOURNEY STARTS HERE", 14, PURPLE, "bold", bg=BG
                   ).pack(pady=(4, 14))

        divider = tk.Frame(wrap, bg=CYAN, height=2, width=340)
        divider.pack(pady=(0, 14))

        make_label(wrap, "SELECT A CARRIAGE TO BEGIN YOUR JOURNEY", 12, TEXT,
                   "bold", bg=BG).pack(pady=(0, 6))
        make_label(
            wrap,
            "Click any carriage on the train above — or wait for the "
            "animation to finish before clicking again.",
            10, MUTED, bg=BG, justify="center",
        ).pack()

        chips = tk.Frame(wrap, bg=BG)
        chips.pack(pady=16)
        for index, page in enumerate(CARRIAGE_PAGES):
            accent = CARRIAGE_ACCENTS[index % len(CARRIAGE_ACCENTS)]
            chip = tk.Frame(chips, bg=PANEL, highlightthickness=1,
                            highlightbackground=accent)
            chip.pack(side="left", padx=5)
            make_label(chip, PAGE_TITLES[page].upper(), 9, accent, "bold",
                       bg=PANEL).pack(padx=10, pady=5)


class HomePage(PageBase):
    """Landing page with hero panel and quick access cards."""

    def build(self):
        scroll = ScrollableFrame(self)
        scroll.pack(fill="both", expand=True)
        root = tk.Frame(scroll.body, bg=BG)
        root.pack(fill="both", expand=True, padx=34, pady=26)

        self.heading(
            root, "WELCOME ABOARD.",
            "Your next destination is just a click away.",
        )

        # hero panel
        hero = Card(root, accent=CYAN, pad=22)
        hero.pack(fill="x", pady=(20, 10))
        make_label(hero.body, "A NEW WAY TO EXPERIENCE RAIL TRAVEL", 17, TEXT,
                   "bold", bg=PANEL).pack(anchor="w")
        make_label(hero.body, "Choose a route. Start an adventure.", 12, MUTED,
                   bg=PANEL).pack(anchor="w", pady=(6, 14))
        RailButton(
            hero.body, "EXPLORE TICKETS",
            command=lambda: self.app.navigate("tickets"), kind="primary",
        ).pack(anchor="w")

        # decorative route strip
        strip = tk.Canvas(hero.body, height=64, bg=PANEL, highlightthickness=0,
                          bd=0)
        strip.pack(fill="x", pady=(18, 0))
        strip.bind("<Configure>", lambda e: self._draw_strip(strip, e.width))

        # quick access
        quick_head = tk.Frame(root, bg=BG)
        quick_head.pack(fill="x", pady=(26, 10))
        make_label(quick_head, "QUICK ACCESS", 13, TEXT, "bold", bg=BG).pack(
            side="left")
        tk.Frame(quick_head, bg=LINE, height=1).pack(
            side="left", fill="x", expand=True, padx=12, pady=6)

        cards_row = tk.Frame(root, bg=BG)
        cards_row.pack(fill="x")
        for col in range(3):
            cards_row.grid_columnconfigure(col, weight=1, uniform="qa")

        entries = [
            ("TICKETS", "Search fictional sample trains across our demo "
                        "network.", "BROWSE TICKETS", "tickets", CYAN),
            ("LOGIN", "Welcome back — sign in with your demo account.",
             "LOGIN", "login", PURPLE),
            ("SIGN UP", "Create a free demo account stored in memory only.",
             "CREATE ACCOUNT", "signup", ORANGE),
        ]
        for col, (title, body, button, target, accent) in enumerate(entries):
            card = Card(cards_row, accent=accent, pad=18)
            card.grid(row=0, column=col, sticky="nsew", padx=8, pady=4)
            make_label(card.body, title, 13, TEXT, "bold", bg=PANEL).pack(
                anchor="w")
            make_label(card.body, body, 10, MUTED, bg=PANEL,
                       justify="left", wraplength=240).pack(
                anchor="w", pady=(6, 14))
            RailButton(card.body, button,
                       command=lambda t=target: self.app.navigate(t),
                       kind="ghost").pack(anchor="w")

        self.note(root, "All schedules, fares and accounts are fictional demo "
                        "data held in memory for this session.")

    @staticmethod
    def _draw_strip(canvas, width):
        canvas.delete("all")
        if width < 60:
            return
        y = 42
        canvas.create_line(0, y, width, y, fill=LINE, width=3)
        canvas.create_line(0, y + 8, width, y + 8, fill=LINE, width=3)
        for x in range(6, width, 26):
            canvas.create_rectangle(x, y - 3, x + 14, y + 14,
                                    fill=PANEL2, outline="")
        stops = [(0.12, "CHENNAI", CYAN), (0.46, "BENGALURU", PURPLE),
                 (0.80, "MYSURU", ORANGE)]
        for frac, name, colour in stops:
            x = int(width * frac)
            canvas.create_oval(x - 6, y + 2, x + 6, y + 14,
                               fill=colour, outline="")
            canvas.create_text(x, y - 12, text=name, fill=MUTED,
                               font=fnt(9, "bold"))


class LoginPage(PageBase):
    """Demo login form (in-memory authentication)."""

    def build(self):
        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True)
        outer.grid_rowconfigure(0, weight=1)
        outer.grid_columnconfigure(0, weight=1)

        card = Card(outer, accent=PURPLE, pad=26)
        card.grid(row=0, column=0, sticky="n", pady=30)
        card.configure(highlightbackground=PURPLE)

        make_label(card.body, "WELCOME BACK", 22, TEXT, "bold", bg=PANEL).pack(
            anchor="w")
        make_label(card.body, "Sign in to your RailMotion demo account.", 11,
                   MUTED, bg=PANEL).pack(anchor="w", pady=(4, 18))

        form = tk.Frame(card.body, bg=PANEL)
        form.pack(fill="x")

        make_label(form, "EMAIL ADDRESS", 9, MUTED, "bold", bg=PANEL).pack(
            anchor="w")
        self.email_var = tk.StringVar(value="")
        make_entry(form, self.email_var).pack(fill="x", pady=(4, 12))

        make_label(form, "PASSWORD", 9, MUTED, "bold", bg=PANEL).pack(anchor="w")
        self.password_var = tk.StringVar(value="")
        make_entry(form, self.password_var, show="•").pack(
            fill="x", pady=(4, 14))

        button_row = tk.Frame(card.body, bg=PANEL)
        button_row.pack(fill="x")
        RailButton(button_row, "LOGIN", command=self.do_login,
                   kind="primary").pack(side="left")
        RailButton(button_row, "CREATE ACCOUNT",
                   command=lambda: self.app.navigate("signup"),
                   kind="ghost").pack(side="left", padx=10)

        tk.Frame(card.body, bg=LINE, height=1).pack(fill="x", pady=16)
        make_label(
            card.body,
            "DEMO ACCOUNT\nEmail:  {}\nPassword:  {}".format(
                DEMO_EMAIL, DEMO_PASSWORD),
            9, ORANGE, bg=PANEL, justify="left",
        ).pack(anchor="w")
        make_label(
            card.body,
            "Accounts are stored in memory only. They are NOT secure and are "
            "lost when the program closes.",
            9, MUTED, bg=PANEL, justify="left",
        ).pack(anchor="w", pady=(8, 0))

        # keep the card near the top of the page
        tk.Frame(self, bg=BG).pack()

    def do_login(self):
        email = self.email_var.get().strip()
        password = self.password_var.get()
        if not email or not password:
            messagebox.showerror(
                "Missing details",
                "Please enter both your email address and password.",
                parent=self,
            )
            return
        ok, message = self.app.authenticate(email, password)
        if not ok:
            messagebox.showerror("Login failed", message, parent=self)
            return
        messagebox.showinfo("Login successful", message, parent=self)
        self.app.navigate("home")


class SignupPage(PageBase):
    """Demo registration form."""

    def build(self):
        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True)
        outer.grid_rowconfigure(0, weight=1)
        outer.grid_columnconfigure(0, weight=1)

        card = Card(outer, accent=ORANGE, pad=26)
        card.grid(row=0, column=0, sticky="n", pady=26)
        card.configure(highlightbackground=ORANGE)

        make_label(card.body, "CREATE YOUR ACCOUNT", 22, TEXT, "bold",
                   bg=PANEL).pack(anchor="w")
        make_label(card.body, "Demo registration — stored in memory only.", 11,
                   MUTED, bg=PANEL).pack(anchor="w", pady=(4, 16))

        form = tk.Frame(card.body, bg=PANEL)
        form.pack(fill="x")

        make_label(form, "FULL NAME", 9, MUTED, "bold", bg=PANEL).pack(anchor="w")
        self.name_var = tk.StringVar()
        make_entry(form, self.name_var).pack(fill="x", pady=(4, 10))

        make_label(form, "EMAIL ADDRESS", 9, MUTED, "bold", bg=PANEL).pack(
            anchor="w")
        self.email_var = tk.StringVar()
        make_entry(form, self.email_var).pack(fill="x", pady=(4, 10))

        make_label(form, "PASSWORD  (minimum 6 characters)", 9, MUTED, "bold",
                   bg=PANEL).pack(anchor="w")
        self.password_var = tk.StringVar()
        make_entry(form, self.password_var, show="•").pack(
            fill="x", pady=(4, 10))

        make_label(form, "CONFIRM PASSWORD", 9, MUTED, "bold", bg=PANEL).pack(
            anchor="w")
        self.confirm_var = tk.StringVar()
        make_entry(form, self.confirm_var, show="•").pack(
            fill="x", pady=(4, 14))

        button_row = tk.Frame(card.body, bg=PANEL)
        button_row.pack(fill="x")
        RailButton(button_row, "CREATE ACCOUNT", command=self.do_signup,
                   kind="primary").pack(side="left")
        RailButton(button_row, "ALREADY REGISTERED? LOGIN",
                   command=lambda: self.app.navigate("login"),
                   kind="ghost").pack(side="left", padx=10)

        make_label(
            card.body,
            "Validation: every field is required, the email format is "
            "checked, passwords must be at least 6 characters and must match.",
            9, MUTED, bg=PANEL, justify="left",
        ).pack(anchor="w", pady=(14, 0))

    def do_signup(self):
        name = self.name_var.get().strip()
        email = self.email_var.get().strip()
        password = self.password_var.get()
        confirm = self.confirm_var.get()

        if not name or not email or not password or not confirm:
            messagebox.showerror(
                "Missing details",
                "Please fill in every field before creating your account.",
                parent=self,
            )
            return
        if password != confirm:
            messagebox.showerror(
                "Passwords do not match",
                "The password and confirmation password must be identical.",
                parent=self,
            )
            return

        ok, message = self.app.create_account(name, email, password)
        if not ok:
            messagebox.showerror("Registration failed", message, parent=self)
            return
        messagebox.showinfo("Account created", message, parent=self)
        self.app.navigate("login")


class TicketsPage(PageBase):
    """Search form + fictional sample trains with save-booking buttons."""

    def build(self):
        scroll = ScrollableFrame(self)
        scroll.pack(fill="both", expand=True)
        root = tk.Frame(scroll.body, bg=BG)
        root.pack(fill="both", expand=True, padx=34, pady=26)

        self.heading(
            root, "FIND YOUR RIDE",
            "Search our fictional sample timetable — no real ticket is sold.",
        )

        # --- search card ---
        card = Card(root, accent=CYAN, pad=20)
        card.pack(fill="x", pady=(18, 6))
        form = tk.Frame(card.body, bg=PANEL)
        form.pack(fill="x")
        for col in range(3):
            form.grid_columnconfigure(col, weight=1, uniform="search")

        self.source_var = tk.StringVar(value=CITIES[0])
        self.dest_var = tk.StringVar(value=CITIES[1])
        self.date_var = tk.StringVar(value=dt.date.today().isoformat())
        self.pax_var = tk.StringVar(value="1")
        self.class_var = tk.StringVar(value=TRAVEL_CLASSES[1])

        self.field(form, 0, 0, "SOURCE CITY",
                   lambda p: self.combo(p, CITIES, self.source_var))
        self.field(form, 0, 1, "DESTINATION CITY",
                   lambda p: self.combo(p, CITIES, self.dest_var))
        self.field(form, 0, 2, "TRAVEL DATE  (YYYY-MM-DD)",
                   lambda p: make_entry(p, self.date_var))

        def pax_factory(parent):
            spin = ttk.Spinbox(parent, from_=1, to=6, increment=1, width=8,
                               textvariable=self.pax_var,
                               style="RM.TSpinbox", font=fnt(11))
            return spin

        self.field(form, 1, 0, "PASSENGERS  (1–6)", pax_factory)
        self.field(form, 1, 1, "TRAVEL CLASS",
                   lambda p: self.combo(p, TRAVEL_CLASSES, self.class_var))

        action_cell = tk.Frame(form, bg=PANEL)
        action_cell.grid(row=1, column=2, sticky="ew", padx=10, pady=7)
        make_label(action_cell, " ", 9, MUTED, bg=PANEL).pack()
        RailButton(action_cell, "SEARCH TRAINS", command=self.do_search,
                   kind="primary").pack(fill="x", pady=(4, 0))

        self.note(
            root,
            "Fictional schedules and fares — no real ticket is purchased and "
            "nothing is charged.",
            ORANGE,
        )

        make_label(root, "SEARCH RESULTS", 13, TEXT, "bold", bg=BG).pack(
            anchor="w", pady=(22, 8))
        tk.Frame(root, bg=LINE, height=1).pack(fill="x")

        self.results = tk.Frame(root, bg=BG)
        self.results.pack(fill="x", pady=(12, 0))
        make_label(self.results,
                   "Pick a route above and press SEARCH TRAINS to list the "
                   "sample services.",
                   11, MUTED, bg=BG).pack(anchor="w")

    @staticmethod
    def combo(parent, values, variable):
        widget = ttk.Combobox(parent, textvariable=variable, values=values,
                              state="readonly", style="RM.TCombobox",
                              font=fnt(11))
        widget.configure(background=PANEL2, foreground=TEXT)
        return widget

    def do_search(self):
        ok, message, results = self.app.search_trains(
            self.source_var.get(),
            self.dest_var.get(),
            self.date_var.get(),
            self.pax_var.get(),
            self.class_var.get(),
        )
        if not ok:
            messagebox.showerror("Search error", message, parent=self)
            return
        self.render_results(results)

    def render_results(self, results):
        for child in self.results.winfo_children():
            child.destroy()
        if not results:
            make_label(
                self.results,
                "No sample train runs on that route yet. Try Chennai → "
                "Bengaluru, Chennai → Coimbatore, Bengaluru → Mysuru, "
                "Hyderabad → Chennai or Mumbai → Pune.",
                11, MUTED, bg=BG, justify="left", wraplength=760,
            ).pack(anchor="w", pady=6)
            return

        for item in results:
            accent = CYAN
            card = Card(self.results, accent=accent, pad=16)
            card.pack(fill="x", pady=8)
            top = tk.Frame(card.body, bg=PANEL)
            top.pack(fill="x")
            make_label(top, item["name"].upper(), 14, TEXT, "bold",
                       bg=PANEL).pack(side="left")
            make_label(top, "₹{} total".format(item["total"]), 13, CYAN,
                       "bold", bg=PANEL).pack(side="right")
            make_label(
                card.body,
                "{}  →  {}     Departs {}".format(
                    item["source"], item["dest"], item["time"]),
                11, TEXT, bg=PANEL,
            ).pack(anchor="w", pady=(6, 2))
            make_label(
                card.body,
                "{} · {} passenger(s) · base fare ₹{} × {} = ₹{}".format(
                    item["date"], item["passengers"], item["fare"],
                    item["passengers"], item["total"]),
                10, MUTED, bg=PANEL,
            ).pack(anchor="w")
            make_label(
                card.body,
                "Fictional schedule — saving creates a demo booking only.",
                9, ORANGE, bg=PANEL,
            ).pack(anchor="w", pady=(4, 10))

            button_row = tk.Frame(card.body, bg=PANEL)
            button_row.pack(anchor="w", pady=(10, 0))
            RailButton(
                button_row, "SELECT TRAIN",
                command=lambda it=item: self.select_train(it),
                kind="primary",
            ).pack(side="left")
            RailButton(
                button_row, "SAVE DEMO BOOKING",
                command=lambda it=item: self.save(it), kind="ghost",
            ).pack(side="left", padx=10)

    def select_train(self, item):
        """Open the multi-passenger booking flow for a search result."""
        try:
            pax = int(str(self.pax_var.get()).strip())
        except (TypeError, ValueError):
            pax = 1
        pax = max(1, min(pax, MAX_PASSENGERS_PER_BOOKING))
        BookingFlow(self.app, item, self.class_var.get(), pax)

    def save(self, item):
        booking = self.app.save_booking(
            item["name"], item["source"], item["dest"], item["date"],
            item["passengers"], self.class_var.get(), item["total"],
        )
        messagebox.showinfo(
            "Demo booking saved",
            "Saved to MY JOURNEYS:\n\n{} — {} → {}\nDate: {}\n"
            "Passengers: {}\nTotal: ₹{}\n\nThis is a fictional demo booking; "
            "no real ticket was purchased.".format(
                booking["train"], booking["source"], booking["dest"],
                booking["date"], booking["passengers"], booking["fare"]),
            parent=self,
        )


class BookingsPage(PageBase):
    """Saved demo bookings ("My Journeys")."""

    def build(self):
        scroll = ScrollableFrame(self)
        scroll.pack(fill="both", expand=True)
        root = tk.Frame(scroll.body, bg=BG)
        root.pack(fill="both", expand=True, padx=34, pady=26)

        self.heading(
            root, "MY JOURNEYS",
            "Demo bookings saved during this session — memory only.",
        )

        body = tk.Frame(root, bg=BG)
        body.pack(fill="x", pady=(18, 0))

        if not self.app.bookings:
            card = Card(body, accent=MUTED, pad=24)
            card.pack(fill="x")
            make_label(card.body, "NO SAVED JOURNEYS YET", 14, TEXT, "bold",
                       bg=PANEL).pack(anchor="w")
            make_label(
                card.body,
                "Search for a sample train on the Tickets page and press "
                "SAVE DEMO BOOKING to see it here.",
                11, MUTED, bg=PANEL, justify="left",
            ).pack(anchor="w", pady=(8, 16))
            RailButton(card.body, "FIND A TRAIN",
                       command=lambda: self.app.navigate("tickets"),
                       kind="primary").pack(anchor="w")
            return

        for index, booking in enumerate(self.app.bookings):
            accent = [CYAN, PURPLE, ORANGE][index % 3]
            card = Card(body, accent=accent, pad=16)
            card.pack(fill="x", pady=8)
            top = tk.Frame(card.body, bg=PANEL)
            top.pack(fill="x")
            make_label(top, booking["train"].upper(), 14, TEXT, "bold",
                       bg=PANEL).pack(side="left")
            RailButton(top, "REMOVE",
                       command=lambda i=index: self.remove(i),
                       kind="danger").pack(side="right")

            make_label(
                card.body,
                "{}  →  {}".format(booking["source"], booking["dest"]),
                12, accent, "bold", bg=PANEL,
            ).pack(anchor="w", pady=(8, 6))
            make_label(
                card.body,
                "REF: {}   ·   status: {}".format(
                    booking.get("ref", "—"),
                    booking.get("status", "active")),
                9, MUTED, bg=PANEL,
            ).pack(anchor="w")

            details = tk.Frame(card.body, bg=PANEL)
            details.pack(fill="x")
            pairs = [
                ("TRAVEL DATE", booking["date"]),
                ("PASSENGERS", str(booking["passengers"])),
                ("CLASS", booking["class"]),
                ("TOTAL FARE", "₹{}".format(booking["fare"])),
            ]
            for col, (label, value) in enumerate(pairs):
                details.grid_columnconfigure(col, weight=1)
                cell = tk.Frame(details, bg=PANEL)
                cell.grid(row=0, column=col, sticky="w", padx=(0, 26))
                make_label(cell, label, 8, MUTED, "bold", bg=PANEL).pack(
                    anchor="w")
                make_label(cell, value, 11, TEXT, "bold", bg=PANEL).pack(
                    anchor="w")

            if booking.get("passenger_details"):
                names = ", ".join(
                    p["name"] for p in booking["passenger_details"])
                make_label(card.body, "Passengers:  {}".format(names),
                           9, MUTED, bg=PANEL).pack(anchor="w", pady=(6, 0))

        make_label(
            body,
            "Bookings are kept only while the application is running.",
            9, ORANGE, bg=BG,
        ).pack(anchor="w", pady=(12, 0))

    def remove(self, index):
        """Open the cancellation confirmation window for a booking."""
        if not (0 <= index < len(self.app.bookings)):
            return
        CancelBookingWindow(
            self.app, self.app.bookings[index],
            on_done=lambda: self.app.refresh_page())


class OffersPage(PageBase):
    """Illustrative promotions."""

    def build(self):
        scroll = ScrollableFrame(self)
        scroll.pack(fill="both", expand=True)
        root = tk.Frame(scroll.body, bg=BG)
        root.pack(fill="both", expand=True, padx=34, pady=26)

        self.heading(
            root, "SEASON OFFERS",
            "Illustrative promotions for this demo — not redeemable with any "
            "real railway service.",
        )

        row = tk.Frame(root, bg=BG)
        row.pack(fill="x", pady=(20, 10))
        for col in range(3):
            row.grid_columnconfigure(col, weight=1, uniform="offers")

        offers = [
            ("FIRST JOURNEY", "WELCOME10",
             "A warm welcome for travellers taking their very first demo "
             "journey on RailMotion.", CYAN),
            ("WEEKEND ESCAPE", "WEEKEND",
             "Plan a relaxed weekend getaway between any two cities on our "
             "fictional network.", PURPLE),
            ("FAMILY TRAVEL", "TOGETHER",
             "Illustrative family offer for groups travelling together in "
             "the same demo booking.", ORANGE),
        ]
        for col, (title, code, description, accent) in enumerate(offers):
            card = Card(row, accent=accent, pad=20)
            card.grid(row=0, column=col, sticky="nsew", padx=8, pady=4)

            make_label(card.body, title, 14, TEXT, "bold", bg=PANEL).pack(
                anchor="w")
            make_label(card.body, "Promotion code", 9, MUTED, bg=PANEL).pack(
                anchor="w", pady=(10, 4))

            chip = tk.Frame(card.body, bg=BG, highlightthickness=1,
                            highlightbackground=accent)
            chip.pack(anchor="w")
            make_label(chip, code, 13, accent, "bold", bg=BG).pack(
                padx=14, pady=6)

            make_label(card.body, description, 10, MUTED, bg=PANEL,
                       justify="left", wraplength=250).pack(
                anchor="w", pady=(14, 0))

            copy_btn = RailButton(card.body, "COPY CODE", kind="ghost")
            copy_btn.configure(
                command=lambda c=code, b=copy_btn: self.copy_code(c, b))
            copy_btn.pack(anchor="w", pady=(14, 0))

        note_card = Card(root, accent=ORANGE, pad=16)
        note_card.pack(fill="x", pady=(14, 0))
        make_label(
            note_card.body,
            "These promotions are illustrative only. No discount can be "
            "redeemed, applied or honoured through a real railway service.",
            10, ORANGE, bg=PANEL, justify="left",
        ).pack(anchor="w")

    def copy_code(self, code, button):
        """Copy a promotion code to the clipboard (demo behaviour)."""
        try:
            self.app.clipboard_clear()
            self.app.clipboard_append(code)
        except tk.TclError:
            messagebox.showerror(
                "Copy failed",
                "Could not copy the promotion code to the clipboard.",
                parent=self)
            return
        button.configure(text="COPIED ✓")
        self.after(1500, lambda: button.configure(text="COPY CODE"))


# =====================================================================
# 7. RAILMOTION APP — shell, navigation and animation state machine
# =====================================================================

PAGE_RENDERERS = {
    "intro": IntroPage,
    "home": HomePage,
    "tickets": TicketsPage,
    "bookings": BookingsPage,
    "login": LoginPage,
    "signup": SignupPage,
    "offers": OffersPage,
}


class RailMotionApp(tk.Tk):
    """Main window, train navigation and demo data services.

    Animation state machine
    -----------------------
    self.phase is one of:
      * "idle"  — train parked in the header (or on the intro screen),
                  navigation clicks are accepted.
      * "exit"  — train accelerates off the right edge of the window.
      * "enter" — destination page is prepared; the train re-enters from
                  the left while the page slides into view.

    Only one ``root.after`` callback ever exists (``self.anim_job``), so
    overlapping transitions are impossible.
    """

    INTRO_H = 336          # tall canvas for the intro screen
    HEADER_H = 160         # compact canvas used as the navigation header
    TICK_MS = 16           # ~60 fps animation loop
    EXIT_SPEED = 30        # px per frame while leaving
    ENTER_MAX = 34         # eased entry speed bounds
    ENTER_MIN = 12

    def __init__(self):
        super().__init__()
        init_font_family(self)
        self.title("RailMotion — Your Journey Starts Here")
        self.geometry("1150x760")
        self.minsize(1000, 700)
        self.configure(bg=BG)

        # ---- animation state ---------------------------------------
        self.phase = "idle"           # idle | exit | enter
        self.mode = "intro"           # intro (tall) | header (compact)
        self.current_page = "intro"
        self.pending_page = None
        self.page_frame = None
        self.pending_frame = None
        self.train_x = 0.0
        self.park_x = 0.0
        self.page_slide_x = 0.0
        self.anim_job = None
        self.hovered = None
        self.selected = None
        self.renderer = None
        self.canvas = None
        self.skyline_shift = 0.0
        self.sleeper_shift = 0.0
        self._resize_job = None
        self._pending_resize = False
        self._suppress_resize = False
        self._drawn_size = (0, 0)

        # ---- demo data (memory only) -------------------------------
        self.accounts = {
            DEMO_EMAIL: {"name": DEMO_NAME, "password": DEMO_PASSWORD},
        }
        self.bookings = []
        self.cancelled_bookings = []   # history of cancelled demo bookings
        self.current_user = None
        self.theme = THEME_NAME

        # ---- widgets -----------------------------------------------
        self._build_styles()
        self._build_shell()

        # application-wide mouse-wheel scrolling (works over child widgets,
        # inside cards and forms, and across nested scroll areas)
        self.bind_all("<MouseWheel>", self._global_wheel, add="+")
        self.bind_all("<Button-4>", self._global_wheel, add="+")
        self.bind_all("<Button-5>", self._global_wheel, add="+")
        self._create_canvas()
        self._show_page_now("intro")
        self._set_status("READY — CLICK A CARRIAGE TO START")

        self.protocol("WM_DELETE_WINDOW", self.destroy)

    # -----------------------------------------------------------------
    # shell
    # -----------------------------------------------------------------
    def _build_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("RM.TCombobox",
                        fieldbackground=PANEL2, background=PANEL2,
                        foreground=TEXT, arrowcolor=CYAN,
                        bordercolor=PANEL2, lightcolor=PANEL2,
                        darkcolor=PANEL2, insertcolor=TEXT)
        style.map("RM.TCombobox",
                  fieldbackground=[("readonly", PANEL2)],
                  foreground=[("readonly", TEXT)],
                  selectbackground=[("readonly", PANEL2)],
                  selectforeground=[("readonly", TEXT)])
        style.configure("Combobox.Listbox",
                        background=PANEL2, foreground=TEXT,
                        fieldbackground=PANEL2, selectbackground=CYAN,
                        selectforeground=BG)
        style.configure("RM.TSpinbox",
                        fieldbackground=PANEL2, background=PANEL2,
                        foreground=TEXT, arrowcolor=CYAN,
                        bordercolor=PANEL2, lightcolor=PANEL2,
                        darkcolor=PANEL2, insertcolor=TEXT)
        style.map("RM.TSpinbox",
                  fieldbackground=[("readonly", PANEL2)],
                  foreground=[("readonly", TEXT)])

    def _build_shell(self):
        # Row 1 (train header) keeps weight 0 so it stays exactly as tall as
        # its configured height (tall on the intro screen, compact afterwards);
        # only row 2 (page content) expands to fill the window.
        self.grid_columnconfigure(0, weight=1)

        # --- top bar ---
        topbar = tk.Frame(self, bg=PANEL, height=48)
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.grid_propagate(False)
        topbar.grid_columnconfigure(1, weight=1)

        brand = tk.Frame(topbar, bg=PANEL, cursor="hand2")
        brand.grid(row=0, column=0, sticky="nsw", padx=18, pady=8)
        make_label(brand, "RAIL", 16, TEXT, "bold", bg=PANEL).pack(side="left")
        make_label(brand, "MOTION", 16, CYAN, "bold", bg=PANEL).pack(side="left")
        for widget in (brand, *brand.winfo_children()):
            widget.bind("<Button-1>", lambda _e: self.navigate("intro"))

        self.title_label = make_label(topbar, "START", 11, MUTED, "bold",
                                      bg=PANEL)
        self.title_label.grid(row=0, column=1, sticky="n")

        self.user_label = make_label(topbar, "GUEST", 10, PURPLE, "bold",
                                     bg=PANEL)
        self.user_label.grid(row=0, column=2, sticky="ne", padx=(18, 12))

        # --- theme toggle (top-right corner) ---
        toggle = tk.Frame(topbar, bg=PANEL)
        toggle.grid(row=0, column=3, sticky="ne", padx=(0, 18), pady=12)
        self.theme_dark_btn = tk.Label(
            toggle, text="DARK MODE", cursor="hand2", padx=12, pady=3,
            font=fnt(9, "bold"))
        self.theme_light_btn = tk.Label(
            toggle, text="LIGHT MODE", cursor="hand2", padx=12, pady=3,
            font=fnt(9, "bold"))
        self.theme_dark_btn.pack(side="left")
        self.theme_light_btn.pack(side="left")
        self.theme_dark_btn.bind("<Button-1>",
                                 lambda _e: self.set_theme("dark"))
        self.theme_light_btn.bind("<Button-1>",
                                  lambda _e: self.set_theme("light"))
        self._refresh_theme_toggle()

        # --- header area that holds the train canvas ---
        self.header_frame = tk.Frame(self, bg=BG)
        self.header_frame.grid(row=1, column=0, sticky="nsew")
        self.header_frame.grid_propagate(False)
        self.header_frame.grid_rowconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.configure(height=self.INTRO_H)

        # --- content area for the pages ---
        self.content = tk.Frame(self, bg=BG)
        self.content.grid(row=2, column=0, sticky="nsew")
        self.grid_rowconfigure(2, weight=1)

        # --- status bar ---
        status = tk.Frame(self, bg=PANEL, height=26)
        status.grid(row=3, column=0, sticky="ew")
        status.grid_propagate(False)
        self.status_label = make_label(status, "READY", 9, CYAN, "bold",
                                       bg=PANEL)
        self.status_label.pack(side="left", padx=14)
        make_label(
            status,
            "FICTIONAL SCHEDULES · DEMO DATA · NO REAL TICKETS",
            9, MUTED, bg=PANEL,
        ).pack(side="right", padx=14)

    # -----------------------------------------------------------------
    # canvas creation / drawing
    # -----------------------------------------------------------------
    def _create_canvas(self, train_x=None):
        """(Re)build the train canvas for the current header mode."""
        if self.canvas is not None:
            self.canvas.destroy()
            self.canvas = None

        self.update_idletasks()
        width = max(50, self.header_frame.winfo_width())
        height = max(50, self.header_frame.winfo_height())
        self._drawn_size = (width, height)

        self.canvas = tk.Canvas(self.header_frame, bg=BG, highlightthickness=0,
                                bd=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        intro = self.mode == "intro"
        self.renderer = TrainRenderer(self.canvas, width, height, intro)
        self.renderer.draw_background()
        self.park_x = self.renderer.park_x
        self.train_x = self.park_x if train_x is None else float(train_x)
        self.renderer.draw_train(self.train_x)
        self.renderer.set_highlight(self.selected)
        self.renderer.set_hover(None)
        self.renderer.set_beam(self.phase != "idle")
        self.skyline_shift = 0.0
        self.sleeper_shift = 0.0
        self.hovered = None

        # event bindings (re-registered on every redraw)
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<Motion>", self._on_canvas_motion)
        self.canvas.bind("<Leave>", self._on_canvas_leave)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

    # -----------------------------------------------------------------
    # navigation
    # -----------------------------------------------------------------
    def navigate(self, page: str) -> None:
        """Start a train transition to *page* (ignored while animating)."""
        if page not in PAGE_RENDERERS:
            return
        if self.phase != "idle":
            return                      # never start overlapping animations
        if page == self.current_page:
            return

        self.pending_page = page
        self._prepare_page(page)        # build the destination before moving
        self.phase = "exit"
        self.renderer.set_beam(True)
        self.renderer.set_hover(None)
        self.hovered = None
        self._set_status("DEPARTING → {}".format(PAGE_TITLES[page].upper()))
        self._ensure_anim()

    def _prepare_page(self, page: str) -> None:
        width = max(self.content.winfo_width(), 10)
        frame = PAGE_RENDERERS[page](self.content, self)
        self.page_slide_x = -float(width)
        frame.place(relx=0, rely=0, relwidth=1, relheight=1,
                    x=int(self.page_slide_x))
        frame.lift()
        self.pending_frame = frame

    def _show_page_now(self, page: str) -> None:
        """Place a page without any animation (used at start-up)."""
        frame = PAGE_RENDERERS[page](self.content, self)
        frame.place(relx=0, rely=0, relwidth=1, relheight=1, x=0)
        frame.lift()
        self.page_frame = frame
        self.current_page = page
        self.pending_frame = None

    def refresh_page(self) -> None:
        """Rebuild the current page in place (e.g. after removing a booking)."""
        if self.phase != "idle" or self.page_frame is None:
            return
        page = self.current_page
        old = self.page_frame
        frame = PAGE_RENDERERS[page](self.content, self)
        frame.place(relx=0, rely=0, relwidth=1, relheight=1, x=0)
        frame.lift()
        self.page_frame = frame
        old.destroy()

    # -----------------------------------------------------------------
    # animation state machine
    # -----------------------------------------------------------------
    def _ensure_anim(self) -> None:
        if self.phase in ("exit", "enter") and self.anim_job is None:
            self.anim_job = self.after(self.TICK_MS, self._tick)

    def _tick(self) -> None:
        self.anim_job = None
        if self.phase == "exit":
            self._move_train(self.EXIT_SPEED)
            if self.train_x >= self.canvas.winfo_width() + 60:
                self._finish_exit()
            self._ensure_anim()
        elif self.phase == "enter":
            remaining = self.park_x - self.train_x
            speed = max(self.ENTER_MIN,
                        min(self.ENTER_MAX, remaining * 0.18))
            if remaining <= speed:
                self._move_train(remaining)
                self._finish_enter()
            else:
                self._move_train(speed)
            self._slide_page()
            self._ensure_anim()

    def _slide_page(self) -> None:
        if self.page_frame is None or self.page_slide_x >= 0:
            return
        self.page_slide_x += max(18.0, -self.page_slide_x * 0.25)
        if self.page_slide_x > 0:
            self.page_slide_x = 0.0
        self.page_frame.place_configure(x=int(self.page_slide_x))

    def _move_train(self, dx: float) -> None:
        self.renderer.move_train(dx)
        self.train_x += dx
        self.renderer.spin(self.train_x, dx)
        self._scroll_track(dx)

    def _scroll_track(self, dx: float) -> None:
        """Scroll sleepers (full spacing) and the skyline (parallax)."""
        self.sleeper_shift += dx
        spacing = self.renderer.sleeper_spacing
        if self.sleeper_shift >= spacing:
            steps = int(self.sleeper_shift // spacing)
            self.canvas.move("sleepers", -spacing * steps, 0)
            self.sleeper_shift -= spacing * steps
        shift = dx * 0.3
        self.canvas.move("skyline", shift, 0)
        self.skyline_shift += shift

    def _finish_exit(self) -> None:
        """Train is off-screen right: reset geometry and reveal the page."""
        # restore parallax layers exactly
        if self.skyline_shift:
            self.canvas.move("skyline", -self.skyline_shift, 0)
            self.skyline_shift = 0.0
        if self.sleeper_shift:
            self.canvas.move("sleepers", -self.sleeper_shift, 0)
            self.sleeper_shift = 0.0

        target = self.pending_page
        offscreen = -(self.renderer.total_w + 80.0)

        new_mode = "intro" if target == "intro" else "header"
        if new_mode != self.mode:
            # step 5: resize the canvas for the compact navigation header
            self.mode = new_mode
            self.header_frame.configure(
                height=self.INTRO_H if new_mode == "intro" else self.HEADER_H)
            self._suppress_resize = True
            self.update_idletasks()
            # step 6: redraw the train beyond the left edge at the new scale
            self._create_canvas(train_x=offscreen)
            self._suppress_resize = False
        else:
            # step 6: reset beyond the left edge without a redraw
            self.renderer.move_train(offscreen - self.train_x)
            self.train_x = offscreen
            self.renderer.set_beam(True)

        # swap in the prepared page
        if self.page_frame is not None:
            self.page_frame.destroy()
            self.page_frame = None
        self.page_frame = self.pending_frame
        self.pending_frame = None
        self.current_page = target
        width = max(self.content.winfo_width(), 10)
        self.page_slide_x = -float(width)
        self.page_frame.place(relx=0, rely=0, relwidth=1, relheight=1,
                              x=int(self.page_slide_x))
        self.page_frame.lift()

        # step 7/8: enter phase — train rolls into the header
        self.phase = "enter"
        self._set_status("ARRIVING → {}".format(PAGE_TITLES[target].upper()))

    def _finish_enter(self) -> None:
        """Train parked: lock in the final positions and state."""
        self.phase = "idle"
        self.pending_page = None

        if abs(self.train_x - self.park_x) > 0.5:
            self.renderer.move_train(self.park_x - self.train_x)
            self.train_x = self.park_x

        self.page_slide_x = 0.0
        self.page_frame.place_configure(x=0)

        # step 9: highlight the selected carriage
        self.selected = (self.current_page
                         if self.current_page in CARRIAGE_PAGES else None)
        self.renderer.set_highlight(self.selected)
        self.renderer.set_beam(False)

        # step 10: the page is now fully visible and interactive
        self._set_status("READY · {}".format(
            PAGE_TITLES[self.current_page].upper()))
        self._update_user_label()

        if self._pending_resize:
            self._pending_resize = False
            self._redraw_static()

    # -----------------------------------------------------------------
    # canvas interaction
    # -----------------------------------------------------------------
    def _hit_test(self, x, y):
        if self.renderer is None:
            return None
        for page, (x1, y1, x2, y2) in self.renderer.boxes.items():
            if (x1 + self.train_x <= x <= x2 + self.train_x
                    and y1 <= y <= y2):
                return page
        return None

    def _on_canvas_click(self, event):
        if self.phase != "idle":
            return
        page = self._hit_test(event.x, event.y)
        if page:
            self.navigate(page)

    def _on_canvas_motion(self, event):
        if self.phase != "idle":
            return
        page = self._hit_test(event.x, event.y)
        if page != self.hovered:
            self.hovered = page
            self.renderer.set_hover(page)
            self.canvas.configure(cursor="hand2" if page else "")

    def _on_canvas_leave(self, _event):
        if self.hovered is not None:
            self.hovered = None
            if self.renderer is not None:
                self.renderer.set_hover(None)
            if self.canvas is not None:
                self.canvas.configure(cursor="")

    def _on_canvas_configure(self, event):
        if self._suppress_resize:
            return
        if (event.width, event.height) == self._drawn_size:
            return
        if self.phase != "idle":
            self._pending_resize = True
            return
        if self._resize_job is not None:
            try:
                self.after_cancel(self._resize_job)
            except tk.TclError:
                pass
        self._resize_job = self.after(120, self._redraw_static)

    def _redraw_static(self):
        self._resize_job = None
        if self.phase != "idle":
            self._pending_resize = True
            return
        self._create_canvas(train_x=None)   # re-park centred at the new size
        self.renderer.set_highlight(self.selected)
        self._pending_resize = False

    # -----------------------------------------------------------------
    # theme (dark / light) — applied immediately, never resets any state
    # -----------------------------------------------------------------
    _RECOLOR_OPTIONS = (
        "background", "foreground", "activebackground", "activeforeground",
        "highlightbackground", "highlightcolor", "insertbackground",
        "readonlybackground", "troughcolor", "selectbackground",
        "selectforeground",
    )

    # Only the core UI colours take part in the literal remap: buttons are
    # role-aware (RailButton.apply_theme) and the train canvas is redrawn,
    # so derived colours can never hijack a UI colour with the same hex.
    _RECOLOR_KEYS = (
        "BG", "PANEL", "PANEL2", "CYAN", "TEXT", "MUTED", "PURPLE",
        "ORANGE", "LINE", "DANGER",
    )

    _WHEEL_SKIP_CLASSES = (
        "Entry", "Text", "TEntry", "TCombobox", "TSpinbox", "Listbox",
        "Treeview",
    )

    def set_theme(self, name: str) -> None:
        """Switch colour theme in place (no page rebuild, no state loss)."""
        global THEME_NAME
        if name not in THEMES or name == THEME_NAME:
            return
        old = {key: globals()[key] for key in PALETTE_KEYS}
        new = THEMES[name]
        colour_map = {}
        for key in self._RECOLOR_KEYS:      # first mapping wins
            old_value, new_value = old[key], new[key]
            if isinstance(old_value, str) and old_value != new_value:
                colour_map.setdefault(old_value, new_value)
        THEME_NAME = name
        self.theme = name
        apply_theme_globals(name)
        self._recolor(self, colour_map)     # widgets keep their values
        self._build_styles()                # ttk dropdowns / spinboxes
        self._create_canvas(train_x=self.train_x)   # redraw the train nav
        self.renderer.set_highlight(self.selected)
        self.renderer.set_beam(self.phase != "idle")
        self._refresh_theme_toggle()
        self._set_status("{} MODE".format(name.upper()))

    def _walk_widgets(self, widget):
        yield widget
        for child in widget.winfo_children():
            yield from self._walk_widgets(child)

    def _recolor(self, widget, colour_map) -> None:
        """Remap every colour option (and Canvas items) from the old theme."""
        for child in self._walk_widgets(widget):
            if isinstance(child, RailButton):
                child.apply_theme()
                continue
            for option in self._RECOLOR_OPTIONS:
                try:
                    value = child.cget(option)
                except tk.TclError:
                    continue
                if isinstance(value, str) and value in colour_map:
                    try:
                        child.configure(**{option: colour_map[value]})
                    except tk.TclError:
                        pass
            if isinstance(child, tk.Canvas) and child is not self.canvas:
                self._recolor_canvas_items(child, colour_map)

    @staticmethod
    def _recolor_canvas_items(canvas, colour_map) -> None:
        for item in canvas.find_all():
            for option in ("fill", "outline"):
                try:
                    value = canvas.itemcget(item, option)
                except tk.TclError:
                    continue
                if isinstance(value, str) and value in colour_map:
                    try:
                        canvas.itemconfigure(item, **{option: colour_map[value]})
                    except tk.TclError:
                        pass

    def _refresh_theme_toggle(self) -> None:
        dark_on = THEME_NAME == "dark"
        active, inactive = ((self.theme_dark_btn, self.theme_light_btn)
                            if dark_on else
                            (self.theme_light_btn, self.theme_dark_btn))
        active.configure(bg=SEG_ON_BG, fg=SEG_ON_FG)
        inactive.configure(bg=SEG_OFF_BG, fg=SEG_OFF_FG)

    # -----------------------------------------------------------------
    # application-wide mouse-wheel scrolling
    # -----------------------------------------------------------------
    def _global_wheel(self, event) -> None:
        """Scroll the innermost scrollable area under the mouse pointer."""
        widget = event.widget
        try:
            if widget.winfo_class() in self._WHEEL_SKIP_CLASSES:
                return          # entries / dropdowns keep their own behaviour
        except tk.TclError:
            return
        target = widget
        while target is not None and not isinstance(target, ScrollableFrame):
            target = getattr(target, "master", None)
        if target is None:
            return              # pointer is outside every scrollable area
        target.scroll_by_event(event)

    # -----------------------------------------------------------------
    # status / account labels
    # -----------------------------------------------------------------
    def _set_status(self, text):
        self.status_label.configure(text="• " + text)

    def _update_user_label(self):
        if self.current_user:
            self.user_label.configure(
                text="SIGNED IN · {}".format(self.current_user.upper()))
        else:
            self.user_label.configure(text="GUEST")

    # -----------------------------------------------------------------
    # demo data services (no dialogs here — pages own the dialogs)
    # -----------------------------------------------------------------
    def create_account(self, full_name, email, password):
        """Validate and store a demo account. Returns (ok, message)."""
        name = (full_name or "").strip()
        mail = (email or "").strip().lower()
        pwd = password or ""
        if not name or not mail or not pwd:
            return False, "Every field is required to create an account."
        if not EMAIL_RE.match(mail):
            return False, "Please enter a valid email address " \
                          "(for example you@example.com)."
        if len(pwd) < 6:
            return False, "Your password must be at least 6 characters long."
        if mail in self.accounts:
            return False, "An account already exists for {}. Please log in " \
                          "instead.".format(mail)
        self.accounts[mail] = {"name": name, "password": pwd}
        return True, "Account created for {} ({}) — demo data stored in " \
                     "memory only.".format(name, mail)

    def authenticate(self, email, password):
        """Check demo credentials. Returns (ok, message)."""
        mail = (email or "").strip().lower()
        pwd = password or ""
        if not mail or not pwd:
            return False, "Both email and password are required."
        account = self.accounts.get(mail)
        if account is None:
            return False, "No demo account exists for {}. Create one first.".format(mail)
        if account["password"] != pwd:
            return False, "Incorrect password for {}. Please try again.".format(mail)
        self.current_user = account["name"]
        self._update_user_label()
        return True, "Welcome back, {}! Taking you home.".format(account["name"])

    def search_trains(self, source, dest, date_text, passengers, travel_class):
        """Validate the search form and return matching sample trains.

        Returns (ok, message, results).
        """
        src = (source or "").strip()
        dst = (dest or "").strip()
        text = (date_text or "").strip()

        if not src or not dst:
            return False, "Please choose both a source and a destination city.", []
        if src.lower() == dst.lower():
            return False, "Source and destination cities must be different.", []
        if not text:
            return False, "Please enter a travel date in YYYY-MM-DD format.", []
        if not DATE_RE.match(text):
            return False, "Invalid date. Please use YYYY-MM-DD (e.g. {}).".format(
                dt.date.today().isoformat()), []
        try:
            travel_date = dt.date.fromisoformat(text)
        except ValueError:
            return False, "That date does not exist. Please check the travel date.", []
        if travel_date < dt.date.today():
            return False, "Travel date {} is in the past. Please choose today " \
                          "or a future date.".format(text), []
        try:
            pax = int(str(passengers).strip())
        except (TypeError, ValueError):
            return False, "Passenger count must be a whole number from 1 to 6.", []
        if pax < 1 or pax > 6:
            return False, "Passenger count must be between 1 and 6.", []

        matches = []
        for train in SAMPLE_TRAINS:
            if train["source"].lower() == src.lower() and \
                    train["dest"].lower() == dst.lower():
                item = dict(train)
                item["date"] = text
                item["passengers"] = pax
                item["class"] = travel_class
                item["total"] = train["fare"] * pax
                matches.append(item)
        return True, "", matches

    def save_booking(self, name, source, dest, date_text, passengers,
                     travel_class, total, passenger_list=None):
        """Append a demo booking to the in-memory list.

        Every booking gets a unique demo reference (PNR-style) so it can be
        reviewed, displayed and cancelled by reference.
        """
        booking = {
            "train": name,
            "source": source,
            "dest": dest,
            "date": date_text,
            "passengers": int(passengers),
            "class": travel_class,
            "fare": int(total),
            "saved_at": dt.datetime.now(),
            "status": "active",
            "ref": self.new_reference(),
            "passenger_details": list(passenger_list or []),
        }
        self.bookings.append(booking)
        return booking

    def new_reference(self):
        """Generate a unique demo PNR-style reference."""
        used = {b.get("ref") for b in self.bookings}
        used |= {b.get("ref") for b in self.cancelled_bookings}
        while True:
            ref = "RM{}".format(random.randrange(1000000000, 9999999999))
            if ref not in used:
                return ref

    def cancel_booking(self, ref):
        """Cancel the active booking identified by *ref*.

        The booking is marked as cancelled and archived (history preserved)
        instead of being silently destroyed, and returns the booking with its
        simulated refund amount — or ``None`` when nothing changed.
        """
        for index, booking in enumerate(self.bookings):
            if booking.get("ref") != ref:
                continue
            if booking.get("status") == "cancelled":
                return None                  # already cancelled — no repeat
            booking["status"] = "cancelled"
            booking["refund"] = booking["fare"]
            booking["cancelled_at"] = dt.datetime.now()
            self.cancelled_bookings.append(self.bookings.pop(index))
            return booking
        return None

    def remove_booking(self, index):
        """Remove a booking by index (bounds checked)."""
        if 0 <= index < len(self.bookings):
            return self.bookings.pop(index)
        return None


# =====================================================================
# 7b. BOOKING FLOW, PAYMENT (CAPTCHA) AND CANCELLATION WINDOWS
# =====================================================================

MAX_PASSENGERS_PER_BOOKING = 6
GENDER_OPTIONS = ["Male", "Female", "Other"]
BERTH_OPTIONS = ["No Preference", "Lower", "Middle", "Upper",
                 "Side Lower", "Side Upper"]
CAPTCHA_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def place_window(win, width: int, height: int) -> None:
    """Size a Toplevel so it always fits the screen, centred on the display."""
    try:
        screen_w = win.winfo_screenwidth()
        screen_h = win.winfo_screenheight()
    except tk.TclError:
        screen_w, screen_h = 1150, 760
    w = max(420, min(width, screen_w - 40))
    h = max(360, min(height, screen_h - 60))
    x = max(0, (screen_w - w) // 2)
    y = max(0, (screen_h - h) // 2)
    win.geometry("{}x{}+{}+{}".format(w, h, x, y))


class BookingFlow(tk.Toplevel):
    """Passenger details → review window for one selected train.

    The window keeps its own state, so going Back between steps never
    loses anything the user typed.
    """

    def __init__(self, app, item, travel_class, requested_pax=1):
        super().__init__(app)
        self.app = app
        self.item = item
        self.travel_class = travel_class
        self.passenger_rows = []          # live entry rows (step 1)
        self.passenger_details = []       # validated dicts (steps 2–4)
        self.total_amount = 0
        self.step = 1

        self.title("RailMotion — Add Passengers")
        self.configure(bg=BG)
        self.transient(app)
        place_window(self, 840, 640)
        self.minsize(770, 480)
        self.protocol("WM_DELETE_WINDOW", self.close_flow)

        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True)

        header = tk.Frame(outer, bg=PANEL)
        header.pack(fill="x")
        make_label(
            header,
            "BOOKING · {}  ({})".format(
                item["name"].upper(), item.get("number", "—")),
            15, TEXT, "bold", bg=PANEL,
        ).pack(anchor="w", padx=18, pady=(12, 2))
        make_label(
            header,
            "{}  →  {}      Travel date {}      Departs {}".format(
                item["source"], item["dest"], item["date"], item["time"]),
            10, MUTED, bg=PANEL,
        ).pack(anchor="w", padx=18)
        self.step_label = make_label(header, "", 10, CYAN, "bold", bg=PANEL)
        self.step_label.pack(anchor="w", padx=18, pady=(6, 12))

        self.body = tk.Frame(outer, bg=BG)
        self.body.pack(fill="both", expand=True, padx=14, pady=10)

        self.frame_passengers = tk.Frame(self.body, bg=BG)
        self.frame_review = tk.Frame(self.body, bg=BG)
        self._build_passenger_step()
        self._build_review_step()

        footer = tk.Frame(outer, bg=PANEL)
        footer.pack(fill="x", side="bottom")
        self.back_btn = RailButton(footer, "BACK", command=self.go_back,
                                   kind="ghost")
        self.back_btn.pack(side="left", padx=14, pady=10)
        self.next_btn = RailButton(footer, "CONTINUE", command=self.go_next,
                                   kind="primary")
        self.next_btn.pack(side="right", padx=14, pady=10)

        # start with as many rows as the search requested (1–6)
        initial = max(1, min(int(requested_pax or 1),
                             MAX_PASSENGERS_PER_BOOKING))
        for _ in range(initial):
            self.add_passenger()
        self.show_step(1)

    # ------------------------------------------------------------- step 1
    def _build_passenger_step(self):
        info = Card(self.frame_passengers, accent=CYAN, pad=12)
        info.pack(fill="x")
        make_label(
            info.body,
            "ADD PASSENGERS  ·  maximum {} passengers per booking".format(
                MAX_PASSENGERS_PER_BOOKING),
            11, TEXT, "bold", bg=PANEL,
        ).pack(anchor="w")
        make_label(
            info.body,
            "All fields marked * are required  ·  Age 0–120  ·  "
            "Berth preference is optional",
            9, MUTED, bg=PANEL, justify="left",
        ).pack(anchor="w", pady=(4, 0))
        self.count_label = make_label(info.body, "", 10, CYAN, "bold",
                                      bg=PANEL)
        self.count_label.pack(anchor="w", pady=(6, 0))

        self.list_holder = ScrollableFrame(self.frame_passengers)
        self.list_holder.pack(fill="both", expand=True, pady=(8, 6))
        self.list_body = self.list_holder.body

        add_bar = tk.Frame(self.frame_passengers, bg=BG)
        add_bar.pack(fill="x")
        RailButton(add_bar, "ADD PASSENGER", command=self.add_passenger,
                   kind="ghost").pack(side="left")

    def update_count(self):
        self.count_label.configure(
            text="PASSENGERS: {} / {}".format(
                len(self.passenger_rows), MAX_PASSENGERS_PER_BOOKING))

    def _renumber(self):
        for index, row in enumerate(self.passenger_rows, start=1):
            row["label"].configure(text="PASSENGER {}".format(index))

    def add_passenger(self):
        if len(self.passenger_rows) >= MAX_PASSENGERS_PER_BOOKING:
            messagebox.showerror(
                "Passenger limit",
                "A single demo booking can include at most {} "
                "passengers.".format(MAX_PASSENGERS_PER_BOOKING),
                parent=self)
            return
        row_frame = tk.Frame(self.list_body, bg=PANEL, highlightthickness=1,
                             highlightbackground=LINE)
        row_frame.pack(fill="x", pady=6, padx=2)

        label = make_label(row_frame, "PASSENGER {}".format(
            len(self.passenger_rows) + 1), 9, CYAN, "bold", bg=PANEL)
        label.pack(anchor="w", padx=12, pady=(8, 0))

        inner = tk.Frame(row_frame, bg=PANEL)
        inner.pack(fill="x", padx=12, pady=(2, 10))
        for col in range(4):
            inner.grid_columnconfigure(col, weight=1, uniform="pax")

        def cell(col, caption):
            holder = tk.Frame(inner, bg=PANEL)
            holder.grid(row=0, column=col, sticky="ew", padx=(0, 10))
            make_label(holder, caption, 8, MUTED, "bold", bg=PANEL).pack(
                anchor="w")
            return holder

        name_var = tk.StringVar()
        make_entry(cell(0, "FULL NAME *"), name_var).pack(
            fill="x", pady=(4, 0))

        age_var = tk.StringVar()
        make_entry(cell(1, "AGE *"), age_var).pack(fill="x", pady=(4, 0))

        gender_var = tk.StringVar()
        gender = ttk.Combobox(cell(2, "GENDER *"), textvariable=gender_var,
                              values=GENDER_OPTIONS, state="readonly",
                              style="RM.TCombobox", font=fnt(10))
        gender.pack(fill="x", pady=(4, 0))

        berth_var = tk.StringVar(value="No Preference")
        berth = ttk.Combobox(cell(3, "BERTH PREFERENCE"),
                             textvariable=berth_var, values=BERTH_OPTIONS,
                             state="readonly", style="RM.TCombobox",
                             font=fnt(10))
        berth.pack(fill="x", pady=(4, 0))

        remove_btn = RailButton(inner, "REMOVE", kind="danger", padx=12)
        remove_btn.grid(row=0, column=4, sticky="s")
        entry = {"frame": row_frame, "label": label, "name": name_var,
                 "age": age_var, "gender": gender_var, "berth": berth_var}
        remove_btn.configure(
            command=lambda e=entry: self.remove_passenger(e))
        self.passenger_rows.append(entry)
        self.update_count()

    def remove_passenger(self, entry):
        if entry in self.passenger_rows:
            self.passenger_rows.remove(entry)
            entry["frame"].destroy()
            self._renumber()
            self.update_count()

    def validate_passengers(self):
        """Return cleaned passenger dicts, or None after showing an error."""
        if not self.passenger_rows:
            messagebox.showerror(
                "No passengers",
                "Add at least one passenger before continuing.",
                parent=self)
            return None
        details = []
        for index, row in enumerate(self.passenger_rows, start=1):
            name = row["name"].get().strip()
            age_text = row["age"].get().strip()
            gender = row["gender"].get().strip()
            berth = row["berth"].get().strip() or "No Preference"
            if not name:
                messagebox.showerror(
                    "Missing name",
                    "Passenger {}: please enter the full name.".format(index),
                    parent=self)
                return None
            if not age_text:
                messagebox.showerror(
                    "Missing age",
                    "Passenger {}: please enter an age.".format(index),
                    parent=self)
                return None
            if not age_text.isdigit():
                messagebox.showerror(
                    "Invalid age",
                    "Passenger {}: age must be a whole number between 0 and "
                    "120.".format(index),
                    parent=self)
                return None
            age = int(age_text)
            if age > 120:
                messagebox.showerror(
                    "Invalid age",
                    "Passenger {}: age must be between 0 and 120.".format(index),
                    parent=self)
                return None
            if gender not in GENDER_OPTIONS:
                messagebox.showerror(
                    "Missing gender",
                    "Passenger {}: please choose a gender.".format(index),
                    parent=self)
                return None
            if berth not in BERTH_OPTIONS:
                berth = "No Preference"
            details.append({"name": name, "age": age, "gender": gender,
                            "berth": berth})
        return details

    # ------------------------------------------------------------- step 2
    def _build_review_step(self):
        scroll = ScrollableFrame(self.frame_review)
        scroll.pack(fill="both", expand=True)
        self.review_body = tk.Frame(scroll.body, bg=BG)
        self.review_body.pack(fill="both", expand=True, padx=6, pady=6)

    def render_review(self):
        for child in self.review_body.winfo_children():
            child.destroy()
        details = self.passenger_details
        total = self.item["fare"] * len(details)
        self.total_amount = total

        journey = Card(self.review_body, accent=CYAN, pad=14)
        journey.pack(fill="x", pady=(0, 8))
        make_label(journey.body, "JOURNEY", 10, MUTED, "bold",
                   bg=PANEL).pack(anchor="w")
        make_label(journey.body,
                   "{}  ({})".format(self.item["name"],
                                     self.item.get("number", "—")),
                   14, TEXT, "bold", bg=PANEL).pack(anchor="w", pady=(2, 0))
        for line in (
            "Route:  {}  →  {}".format(self.item["source"], self.item["dest"]),
            "Travel date:  {}      Departs:  {}".format(
                self.item["date"], self.item["time"]),
            "Travel class:  {}".format(self.travel_class),
        ):
            make_label(journey.body, line, 10, TEXT, bg=PANEL).pack(
                anchor="w", pady=1)

        pax_card = Card(self.review_body, accent=PURPLE, pad=14)
        pax_card.pack(fill="x", pady=(0, 8))
        make_label(pax_card.body,
                   "PASSENGERS ({})".format(len(details)), 10, MUTED,
                   "bold", bg=PANEL).pack(anchor="w")
        for index, person in enumerate(details, start=1):
            make_label(
                pax_card.body,
                "{}. {}  ·  {} yrs  ·  {}  ·  berth: {}".format(
                    index, person["name"], person["age"], person["gender"],
                    person["berth"]),
                10, TEXT, bg=PANEL,
            ).pack(anchor="w", pady=1)

        fare_card = Card(self.review_body, accent=ORANGE, pad=14)
        fare_card.pack(fill="x", pady=(0, 8))
        make_label(fare_card.body, "FARE BREAKDOWN", 10, MUTED, "bold",
                   bg=PANEL).pack(anchor="w")
        make_label(fare_card.body,
                   "Base fare per passenger:  ₹{}".format(self.item["fare"]),
                   10, TEXT, bg=PANEL).pack(anchor="w", pady=1)
        make_label(fare_card.body,
                   "Passengers:  {}".format(len(details)),
                   10, TEXT, bg=PANEL).pack(anchor="w", pady=1)
        make_label(fare_card.body,
                   "TOTAL PAYABLE:  ₹{}".format(total),
                   14, CYAN, "bold", bg=PANEL).pack(anchor="w", pady=(4, 0))
        make_label(
            fare_card.body,
            "No additional taxes or fees are applied; class and berth "
            "choices do not change the demo fare.",
            9, ORANGE, bg=PANEL, justify="left",
        ).pack(anchor="w", pady=(4, 0))

    # ------------------------------------------------------------- steps
    def show_step(self, number):
        self.step = number
        self.frame_passengers.place_forget()
        self.frame_review.place_forget()
        if number == 1:
            self.frame_passengers.place(relx=0, rely=0, relwidth=1,
                                        relheight=1)
            self.step_label.configure(
                text="STEP 1: PASSENGERS → STEP 2: REVIEW → "
                     "STEP 3: PAYMENT → STEP 4: CONFIRMATION")
            self.back_btn.configure(text="BACK")
            self.next_btn.configure(text="CONTINUE")
            self.update_count()
        else:
            self.frame_review.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.step_label.configure(
                text="STEP 1: PASSENGERS → STEP 2: REVIEW → "
                     "STEP 3: PAYMENT → STEP 4: CONFIRMATION")
            self.back_btn.configure(text="BACK")
            self.next_btn.configure(text="PROCEED TO PAYMENT")
            self.render_review()

    def go_back(self):
        if self.step == 2:
            self.show_step(1)          # passenger rows keep their values
        else:
            self.close_flow()

    def go_next(self):
        if self.step == 1:
            details = self.validate_passengers()
            if details is None:
                return
            self.passenger_details = details
            self.show_step(2)
        else:
            PaymentWindow(self)

    def close_flow(self):
        self.destroy()


class PaymentWindow(tk.Toplevel):
    """CAPTCHA-protected simulated payment for a BookingFlow."""

    def __init__(self, flow):
        super().__init__(flow.app)
        self.flow = flow
        self.app = flow.app
        self.item = flow.item
        self.passenger_details = flow.passenger_details
        self.total = flow.total_amount
        self.code = ""
        self.verified = False
        self.confirmed = False

        self.title("RailMotion — Complete Your Payment")
        self.configure(bg=BG)
        self.transient(flow)
        place_window(self, 620, 680)
        self.minsize(520, 560)
        self.protocol("WM_DELETE_WINDOW", self.cancel_payment)

        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True)

        head = tk.Frame(outer, bg=PANEL)
        head.pack(fill="x")
        make_label(head, "COMPLETE YOUR PAYMENT", 18, TEXT, "bold",
                   bg=PANEL).pack(anchor="w", padx=18, pady=(14, 2))
        make_label(
            head,
            "SIMULATED DEMO PAYMENT — no real money is transferred.",
            9, ORANGE, "bold", bg=PANEL, justify="left",
        ).pack(anchor="w", padx=18, pady=(0, 1))
        make_label(
            head,
            "No card / UPI details are requested or stored.",
            9, ORANGE, bg=PANEL, justify="left",
        ).pack(anchor="w", padx=18, pady=(0, 12))

        body = tk.Frame(outer, bg=BG)
        body.pack(fill="both", expand=True, padx=16, pady=12)

        details_card = Card(body, accent=CYAN, pad=14)
        details_card.pack(fill="x", pady=(0, 10))
        make_label(details_card.body,
                   "{}  ({})".format(self.item["name"],
                                     self.item.get("number", "—")),
                   13, TEXT, "bold", bg=PANEL).pack(anchor="w")
        for line in (
            "Route:  {}  →  {}".format(self.item["source"], self.item["dest"]),
            "Travel date:  {}      Class:  {}".format(
                self.item["date"], self.flow.travel_class),
            "Passengers:  {}".format(len(self.passenger_details)),
        ):
            make_label(details_card.body, line, 10, TEXT, bg=PANEL).pack(
                anchor="w", pady=1)
        make_label(details_card.body,
                   "TOTAL PAYABLE:  ₹{}".format(self.total),
                   15, CYAN, "bold", bg=PANEL).pack(anchor="w", pady=(6, 0))

        # --- CAPTCHA section ---
        self.captcha_card = Card(body, accent=PURPLE, pad=14)
        self.captcha_card.pack(fill="x", pady=(0, 10))
        make_label(self.captcha_card.body,
                   "VERIFY YOU ARE HUMAN — ENTER THE CODE", 10, MUTED,
                   "bold", bg=PANEL).pack(anchor="w")
        self.captcha_canvas = tk.Canvas(self.captcha_card.body, width=280,
                                        height=68, highlightthickness=1,
                                        highlightbackground=LINE, bd=0)
        self.captcha_canvas.pack(anchor="w", pady=(8, 8))

        code_row = tk.Frame(self.captcha_card.body, bg=PANEL)
        code_row.pack(fill="x")
        self.code_var = tk.StringVar()
        self.code_entry = make_entry(code_row, self.code_var)
        self.code_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        RailButton(code_row, "REFRESH CAPTCHA", command=self.refresh_captcha,
                   kind="ghost", padx=12).pack(side="left")

        verify_row = tk.Frame(self.captcha_card.body, bg=PANEL)
        verify_row.pack(fill="x", pady=(10, 0))
        self.verify_btn = RailButton(verify_row, "VERIFY CODE",
                                     command=self.verify_code, kind="primary")
        self.verify_btn.pack(side="left")
        make_label(verify_row, "codes are case-insensitive", 9, MUTED,
                   bg=PANEL).pack(side="left", padx=10)

        # --- confirmation section (after successful verification) ---
        self.confirm_card = Card(body, accent=CYAN, pad=14)
        make_label(self.confirm_card.body, "CONFIRM DEMO PAYMENT", 11, TEXT,
                   "bold", bg=PANEL).pack(anchor="w")
        make_adaptive_label(
            self.confirm_card.body,
            "CAPTCHA verified. Press CONFIRM DEMO PAYMENT to simulate the "
            "payment of ₹{} and generate your demo booking.".format(
                self.total),
            10, MUTED, bg=PANEL, justify="left", margin=32,
        ).pack(anchor="w", pady=(4, 8))
        confirm_row = tk.Frame(self.confirm_card.body, bg=PANEL)
        confirm_row.pack(fill="x")
        self.confirm_btn = RailButton(
            confirm_row, "CONFIRM DEMO PAYMENT",
            command=self.confirm_payment, kind="primary")
        self.confirm_btn.pack(side="left")
        RailButton(confirm_row, "← BACK TO REVIEW",
                   command=self.cancel_payment, kind="ghost").pack(
            side="left", padx=10)

        footer = tk.Frame(outer, bg=PANEL)
        footer.pack(fill="x", side="bottom")
        self.cancel_btn = RailButton(footer, "CANCEL",
                                     command=self.cancel_payment,
                                     kind="ghost")
        self.cancel_btn.pack(side="left", padx=14, pady=10)

        self.refresh_captcha()

    # --- CAPTCHA ------------------------------------------------------
    def refresh_captcha(self):
        self.code = "".join(random.choice(CAPTCHA_ALPHABET)
                            for _ in range(6))
        self._draw_captcha()

    def _draw_captcha(self):
        c = self.captcha_canvas
        c.delete("all")
        width, height = 280, 68
        c.create_rectangle(0, 0, width, height, fill=PANEL2, outline=LINE)
        rnd = random.Random()
        for _ in range(8):                      # noise curves
            c.create_line(rnd.randrange(0, width), rnd.randrange(0, height),
                          rnd.randrange(0, width), rnd.randrange(0, height),
                          fill=rnd.choice([CYAN, PURPLE, ORANGE, MUTED]),
                          width=1)
        for _ in range(30):                     # noise dots
            x = rnd.randrange(0, width - 4)
            y = rnd.randrange(0, height - 4)
            c.create_oval(x, y, x + 3, y + 3,
                          fill=rnd.choice([MUTED, CYAN, PURPLE]), outline="")
        x_pos = 34
        for letter in self.code:                # jittered code letters
            c.create_text(
                x_pos, height / 2 + rnd.randrange(-9, 10), text=letter,
                font=fnt(rnd.choice([19, 21, 23]), "bold"),
                fill=rnd.choice([TEXT, CYAN, PURPLE, ORANGE]),
                angle=rnd.choice([-12, -7, -3, 0, 5, 9, 13]),
            )
            x_pos += rnd.randrange(34, 42)

    def verify_code(self):
        entered = self.code_var.get().strip()
        if not entered:
            messagebox.showerror(
                "Code required",
                "Please enter the verification code shown above the "
                "input box.", parent=self)
            return
        if entered.upper() != self.code.upper():
            messagebox.showerror(
                "Verification failed",
                "The verification code does not match. Please try again "
                "(codes are case-insensitive) or refresh the CAPTCHA.",
                parent=self)
            return
        self.verified = True
        self.captcha_card.pack_forget()
        self.confirm_card.pack(fill="x", pady=(0, 10))
        self.code_entry.configure(state="disabled")
        self.verify_btn.configure(state="disabled")

    def confirm_payment(self):
        if self.confirmed:
            return                      # never create a duplicate booking
        if not self.verified:
            messagebox.showerror(
                "Verify first",
                "Please verify the CAPTCHA code before confirming the "
                "demo payment.", parent=self)
            return
        self.confirmed = True
        self.confirm_btn.configure(state="disabled")
        self.cancel_btn.configure(state="disabled")
        pax = len(self.passenger_details)
        total = self.item["fare"] * pax
        booking = self.app.save_booking(
            self.item["name"], self.item["source"], self.item["dest"],
            self.item["date"], pax, self.flow.travel_class, total,
            passenger_list=self.passenger_details)
        BookingSuccessWindow(self.app, self, booking, self.item)

    def cancel_payment(self):
        """Return to the review step — passengers are never lost."""
        self.flow.deiconify()
        self.flow.lift()
        self.flow.show_step(2)
        self.destroy()


class BookingSuccessWindow(tk.Toplevel):
    """Demo booking confirmation with the generated reference (PNR)."""

    def __init__(self, app, payment, booking, item):
        super().__init__(app)
        self.app = app
        self.payment = payment
        self.booking = booking
        self.title("RailMotion — Booking Confirmed")
        self.configure(bg=BG)
        self.transient(payment)
        place_window(self, 600, 660)
        self.minsize(480, 460)

        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True)

        head = tk.Frame(outer, bg=PANEL)
        head.pack(fill="x")
        make_label(head, "BOOKING CONFIRMED (DEMO)", 17, CYAN, "bold",
                   bg=PANEL).pack(anchor="w", padx=18, pady=(14, 2))
        make_adaptive_label(
            head,
            "Simulated payment of ₹{} received — this is a demonstration, "
            "no real railway ticket has been purchased.".format(
                booking["fare"]),
            9, ORANGE, bg=PANEL, justify="left", margin=64,
        ).pack(anchor="w", padx=18, pady=(0, 12))

        body = tk.Frame(outer, bg=BG)
        body.pack(fill="both", expand=True, padx=16, pady=12)

        ref_card = Card(body, accent=CYAN, pad=14)
        ref_card.pack(fill="x", pady=(0, 10))
        make_label(ref_card.body, "BOOKING REFERENCE (DEMO PNR)", 9, MUTED,
                   "bold", bg=PANEL).pack(anchor="w")
        make_label(ref_card.body, booking["ref"], 22, CYAN, "bold",
                   bg=PANEL).pack(anchor="w", pady=(2, 0))

        info = Card(body, accent=PURPLE, pad=14)
        info.pack(fill="x", pady=(0, 10))
        for line in (
            "Train:  {} ({})".format(booking["train"],
                                     item.get("number", "—")),
            "Route:  {}  →  {}".format(booking["source"], booking["dest"]),
            "Travel date:  {}".format(booking["date"]),
            "Class:  {}".format(booking["class"]),
            "Passengers:  {}".format(booking["passengers"]),
            "Total amount:  ₹{}".format(booking["fare"]),
        ):
            make_label(info.body, line, 10, TEXT, bg=PANEL).pack(
                anchor="w", pady=1)

        if booking.get("passenger_details"):
            pax_card = Card(body, accent=ORANGE, pad=14)
            pax_card.pack(fill="x", pady=(0, 10))
            make_label(pax_card.body, "PASSENGERS", 9, MUTED, "bold",
                       bg=PANEL).pack(anchor="w")
            for index, person in enumerate(booking["passenger_details"],
                                           start=1):
                make_label(
                    pax_card.body,
                    "{}. {}  ·  {} yrs  ·  {}  ·  berth: {}".format(
                        index, person["name"], person["age"],
                        person["gender"], person["berth"]),
                    10, TEXT, bg=PANEL,
                ).pack(anchor="w", pady=1)

        footer = tk.Frame(outer, bg=PANEL)
        footer.pack(fill="x", side="bottom")
        RailButton(footer, "CLOSE", command=self.destroy,
                   kind="ghost").pack(side="left", padx=14, pady=10)
        RailButton(footer, "VIEW MY JOURNEYS", command=self.view_bookings,
                   kind="primary").pack(side="right", padx=14, pady=10)

    def view_bookings(self):
        self.payment.flow.close_flow()
        self.payment.destroy()
        self.destroy()
        self.app.navigate("bookings")


class CancelBookingWindow(tk.Toplevel):
    """Cancellation confirmation with the simulated 7-day refund notice."""

    def __init__(self, app, booking, on_done=None):
        super().__init__(app)
        self.app = app
        self.booking = booking
        self.on_done = on_done
        self.done = False

        self.title("RailMotion — Cancel Your Booking")
        self.configure(bg=BG)
        self.transient(app)
        place_window(self, 640, 640)
        self.minsize(500, 480)

        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True)

        head = tk.Frame(outer, bg=PANEL)
        head.pack(fill="x")
        make_label(head, "CANCEL YOUR BOOKING?", 17, TEXT, "bold",
                   bg=PANEL).pack(anchor="w", padx=18, pady=(14, 2))
        make_adaptive_label(
            head,
            "Are you sure you want to cancel this booking? After "
            "cancellation is confirmed, the refund will be credited to your "
            "account within 7 days.",
            10, MUTED, bg=PANEL, justify="left", margin=64,
        ).pack(anchor="w", padx=18, pady=(0, 12))

        body = tk.Frame(outer, bg=BG)
        body.pack(fill="both", expand=True, padx=16, pady=12)

        info = Card(body, accent=ORANGE, pad=14)
        info.pack(fill="x", pady=(0, 10))
        for line in (
            "Booking reference:  {}".format(booking.get("ref", "—")),
            "Train:  {}".format(booking["train"]),
            "Route:  {}  →  {}".format(booking["source"], booking["dest"]),
            "Travel date:  {}".format(booking["date"]),
            "Passengers:  {}".format(booking["passengers"]),
            "Original booking amount:  ₹{}".format(booking["fare"]),
            "Expected refund:  ₹{} (full demo fare)".format(
                booking["fare"]),
        ):
            make_label(info.body, line, 10, TEXT, bg=PANEL).pack(
                anchor="w", pady=1)

        note = Card(body, accent=PURPLE, pad=14)
        note.pack(fill="x")
        make_adaptive_label(
            note.body,
            "Simulated workflow: the 7-day refund shown here is part of the "
            "demonstration only — no real bank account will be credited and "
            "no railway service is involved.",
            9, ORANGE, bg=PANEL, justify="left", margin=56,
        ).pack(anchor="w")

        footer = tk.Frame(outer, bg=PANEL)
        footer.pack(fill="x", side="bottom")
        self.keep_btn = RailButton(footer, "KEEP BOOKING",
                                   command=self.destroy, kind="ghost")
        self.keep_btn.pack(side="left", padx=14, pady=10)
        self.confirm_btn = RailButton(
            footer, "CONFIRM CANCELLATION", command=self.confirm_cancel,
            kind="danger")
        self.confirm_btn.pack(side="right", padx=14, pady=10)

    def confirm_cancel(self):
        if self.done:
            return                      # never cancel the same booking twice
        ref = self.booking.get("ref")
        cancelled = self.app.cancel_booking(ref)
        if cancelled is None:
            messagebox.showinfo(
                "Already cancelled",
                "Booking {} is no longer active, so it cannot be cancelled "
                "again.".format(ref), parent=self)
            self.destroy()
            return
        self.done = True
        self.keep_btn.configure(state="disabled")
        self.confirm_btn.configure(state="disabled")
        if self.on_done is not None:
            self.on_done()              # refresh My Journeys immediately
        CancelSuccessWindow(self.app, cancelled, on_done=self.on_done)
        self.destroy()


class CancelSuccessWindow(tk.Toplevel):
    """Cancellation success with the simulated refund notice."""

    def __init__(self, app, booking, on_done=None):
        super().__init__(app)
        self.app = app
        self.on_done = on_done
        self.title("RailMotion — Booking Cancelled")
        self.configure(bg=BG)
        self.transient(app)
        place_window(self, 560, 520)
        self.minsize(480, 430)

        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True)

        head = tk.Frame(outer, bg=PANEL)
        head.pack(fill="x")
        make_label(head, "BOOKING CANCELLED", 17, CYAN, "bold",
                   bg=PANEL).pack(anchor="w", padx=18, pady=(14, 2))
        make_adaptive_label(
            head,
            "This demo booking is no longer active and has been moved out "
            "of your active journeys.",
            9, MUTED, bg=PANEL, justify="left", margin=64,
        ).pack(anchor="w", padx=18, pady=(0, 12))

        body = tk.Frame(outer, bg=BG)
        body.pack(fill="both", expand=True, padx=16, pady=12)

        info = Card(body, accent=CYAN, pad=14)
        info.pack(fill="x", pady=(0, 10))
        for line in (
            "Booking reference:  {}".format(booking.get("ref", "—")),
            "Train:  {}  ({}  →  {})".format(
                booking["train"], booking["source"], booking["dest"]),
            "Travel date:  {}".format(booking["date"]),
            "Refund amount:  ₹{}".format(booking.get("refund",
                                                      booking["fare"])),
        ):
            make_label(info.body, line, 10, TEXT, bg=PANEL).pack(
                anchor="w", pady=1)

        note = Card(body, accent=ORANGE, pad=14)
        note.pack(fill="x")
        make_adaptive_label(
            note.body,
            "The simulated refund is expected within 7 days. This is a "
            "demonstration only — no real money or bank account is involved.",
            9, ORANGE, bg=PANEL, justify="left", margin=56,
        ).pack(anchor="w")

        footer = tk.Frame(outer, bg=PANEL)
        footer.pack(fill="x", side="bottom")
        RailButton(footer, "DONE", command=self.close, kind="primary").pack(
            side="right", padx=14, pady=10)

    def close(self):
        self.destroy()
        if self.on_done is not None:
            self.on_done()


# =====================================================================
# 8. AUTOMATED SMOKE TEST
# =====================================================================

def run_smoke_test(app: RailMotionApp) -> None:
    """Exercise navigation, animation and demo logic, then exit."""
    results = []

    def check(label, condition, extra=""):
        results.append((label, bool(condition), extra))

    def wait_idle(callback, tries=0):
        if app.phase == "idle":
            app.after(40, callback)
        elif tries > 600:
            check("transition finishes", False, "phase={}".format(app.phase))
            app.after(40, callback)
        else:
            app.after(25, lambda: wait_idle(callback, tries + 1))

    # ---- initial state --------------------------------------------
    check("starts on the intro screen",
          app.current_page == "intro" and app.phase == "idle")
    check("train drawn with six carriage hit boxes",
          app.renderer is not None and len(app.renderer.boxes) == 6)
    check("canvas has artwork", len(app.canvas.find_all()) > 150,
          str(len(app.canvas.find_all())))
    home_box = app.renderer.boxes.get("home")
    probe_x = home_box[0] + (home_box[2] - home_box[0]) / 2 + app.train_x
    probe_y = (home_box[1] + home_box[3]) / 2
    check("hit test resolves the HOME carriage",
          app._hit_test(probe_x, probe_y) == "home",
          str(app._hit_test(probe_x, probe_y)))

    sequence = ["home", "tickets", "bookings", "login", "signup",
                "offers", "intro", "home"]

    def after_nav(page, index):
        check("navigate -> {}".format(page),
              app.current_page == page and app.phase == "idle",
              "{} / {}".format(app.current_page, app.phase))
        check("page visible -> {}".format(page),
              app.page_frame is not None and app.page_frame.winfo_ismapped())
        if page in CARRIAGE_PAGES:
            check("carriage highlighted -> {}".format(page),
                  app.selected == page)
        check("train inside window -> {}".format(page),
              0 <= app.train_x <= app.canvas.winfo_width() + 1,
              "train_x={:.0f} w={}".format(app.train_x,
                                           app.canvas.winfo_width()))
        app.after(60, lambda: navigate_next(index + 1))

    def navigate_next(index):
        if index >= len(sequence):
            after_navigation()
            return
        page = sequence[index]
        app.navigate(page)
        wait_idle(lambda: after_nav(page, index))

    def after_navigation():
        # rapid double click must not start overlapping animations
        app.navigate("tickets")
        app.navigate("bookings")
        check("rapid clicks ignored while animating", app.phase == "exit")
        wait_idle(after_rapid)

    def after_rapid():
        check("rapid click sequence settles on first target",
              app.current_page == "tickets" and app.phase == "idle",
              "{} / {}".format(app.current_page, app.phase))
        data_tests()

    def data_tests():
        # --- authentication ---------------------------------------
        ok, msg = app.authenticate("DEMO@RAILMOTION.IN", DEMO_PASSWORD)
        check("login normalises email to lowercase", ok, msg)
        ok, _ = app.authenticate(DEMO_EMAIL, "wrong-password")
        check("login rejects a wrong password", not ok)
        ok, _ = app.authenticate("nobody@example.com", "whatever")
        check("login rejects an unknown account", not ok)

        # --- registration -----------------------------------------
        ok, msg = app.create_account("Ada Lovelace",
                                     "Ada@Example.COM", "secret1")
        check("signup stores a valid account", ok, msg)
        check("signup lowercases the stored email",
              "ada@example.com" in app.accounts)
        ok, _ = app.create_account("Dup", "ADA@example.com", "secret1")
        check("signup rejects duplicate emails", not ok)
        ok, _ = app.create_account("Bad Mail", "not-an-email", "secret1")
        check("signup rejects invalid emails", not ok)
        ok, _ = app.create_account("Short", "short@example.com", "abc")
        check("signup rejects short passwords", not ok)

        # --- search -------------------------------------------------
        ok, msg, _ = app.search_trains("Chennai", "Chennai",
                                       "2030-01-01", "1", "Sleeper")
        check("search rejects identical cities", not ok, msg)
        ok, msg, _ = app.search_trains("Chennai", "Bengaluru",
                                       "2000-01-01", "1", "Sleeper")
        check("search rejects past dates", not ok, msg)
        ok, msg, _ = app.search_trains("Chennai", "Bengaluru",
                                       "someday", "1", "Sleeper")
        check("search rejects malformed dates", not ok, msg)
        ok, msg, _ = app.search_trains("Chennai", "Bengaluru",
                                       "2030-01-01", "9", "Sleeper")
        check("search rejects passenger counts above 6", not ok, msg)
        ok, msg, results = app.search_trains(
            "Chennai", "Bengaluru", "2030-01-01", "2", "AC Sleeper")
        check("search finds Coastal Express",
              ok and len(results) == 1 and results[0]["name"] == "Coastal Express",
              msg or str(results))
        check("fare = base × passengers",
              ok and results[0]["total"] == 450 * 2,
              str(results[0]["total"]) if results else "no results")
        ok, _, results = app.search_trains("Pune", "Mysuru",
                                           "2030-01-01", "1", "Sleeper")
        check("search tolerates routes with no sample train",
              ok and results == [])

        # --- bookings ----------------------------------------------
        _, _, results = app.search_trains("Mumbai", "Pune",
                                          "2030-01-01", "3", "General")
        app.save_booking(results[0]["name"], results[0]["source"],
                         results[0]["dest"], results[0]["date"],
                         results[0]["passengers"], results[0]["class"],
                         results[0]["total"])
        check("booking saved in memory", len(app.bookings) == 1)
        app.remove_booking(0)
        check("booking removed from memory", len(app.bookings) == 0)

        # back to the home page for the final state
        app.navigate("home")
        wait_idle(finish)

    def finish():
        check("final state is idle on home",
              app.current_page == "home" and app.phase == "idle")
        failures = [r for r in results if not r[1]]
        print("=" * 62)
        print("RailMotion smoke test — {} checks, {} failed".format(
            len(results), len(failures)))
        for label, passed, extra in results:
            print("  [{}] {}{}".format(
                "PASS" if passed else "FAIL", label,
                (" — " + str(extra)) if (extra and not passed) else ""))
        print("=" * 62)
        app.exit_code = 1 if failures else 0
        app.destroy()

    navigate_next(0)


# =====================================================================
# 9. ENTRY POINT
# =====================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description="RailMotion — animated railway booking desktop app "
                    "(Python + Tkinter).")
    parser.add_argument("--smoke", action="store_true",
                        help="run an automated self-test, print a report "
                             "and exit")
    args = parser.parse_args()

    try:
        app = RailMotionApp()
    except tk.TclError as exc:
        print("Could not open a display window: {}".format(exc), file=sys.stderr)
        print("Run this application inside a desktop session.", file=sys.stderr)
        return 2

    if args.smoke:
        app.after(250, lambda: run_smoke_test(app))

    app.mainloop()
    return int(getattr(app, "exit_code", 0))


if __name__ == "__main__":
    sys.exit(main())
