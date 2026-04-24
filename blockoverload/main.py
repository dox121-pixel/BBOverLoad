"""BlockOverload – Kivy application entry point.

Run locally:
    python -m blockoverload.main

Build Android APK:
    buildozer android debug
"""

from __future__ import annotations

import os

# Keep resolution sensible on desktop during development
os.environ.setdefault("KIVY_WINDOW", "sdl2")

from kivy.app import App
from kivy.core.window import Window
from kivy.config import Config

# Force a phone-like portrait window on desktop
Config.set("graphics", "width",  "400")
Config.set("graphics", "height", "720")
Config.set("graphics", "resizable", "0")

from blockoverload.ui import build_screen_manager


class BlockOverloadApp(App):
    title = "BlockOverload"

    def build(self):
        # Dark status bar colour on Android (harmless on desktop)
        try:
            from android.runnable import run_on_ui_thread  # type: ignore[import]
        except ImportError:
            pass

        Window.clearcolor = (0.08, 0.08, 0.18, 1)
        return build_screen_manager()


def main():
    BlockOverloadApp().run()


if __name__ == "__main__":
    main()
