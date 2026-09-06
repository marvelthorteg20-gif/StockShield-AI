"""CLI helpers: ANSI color, loading spinner, aligned key/value rows."""

from __future__ import annotations

import sys
import threading
import time
from contextlib import contextmanager
from typing import Iterator

import config

RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
DIM = "\033[2m"


def color_enabled() -> bool:
    """True when THEME is color and stdout looks like a terminal."""
    if str(config.THEME).lower() != "color":
        return False
    return bool(getattr(sys.stdout, "isatty", lambda: False)())


def paint(text: str, code: str) -> str:
    """Wrap *text* in ANSI *code* when color is enabled; otherwise unchanged."""
    if not color_enabled():
        return text
    return f"{code}{text}{RESET}"


def header(title: str, width: int = 45) -> None:
    """Print a section header. Visible characters match classic CLI titles."""
    line = "=" * width
    print(paint(line, CYAN))
    print(paint(title, BOLD + CYAN))
    print(paint(line, CYAN))


def rule(width: int = 45, char: str = "-") -> None:
    """Print a horizontal rule (same character count as the classic CLI)."""
    print(paint(char * width, DIM))


@contextmanager
def spinner(message: str = "Loading") -> Iterator[None]:
    """TTY spinner; no-op when stdout is not a terminal (keeps tests quiet)."""
    if not getattr(sys.stdout, "isatty", lambda: False)():
        yield
        return

    stop = threading.Event()
    frames = "|/-\\"

    def _run() -> None:
        """Write spinner frames until *stop* is set."""
        index = 0
        while not stop.is_set():
            frame = frames[index % 4]
            sys.stdout.write(f"\r{message} {frame}")
            sys.stdout.flush()
            index += 1
            time.sleep(0.08)
        sys.stdout.write("\r" + " " * (len(message) + 4) + "\r")
        sys.stdout.flush()

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    try:
        yield
    finally:
        stop.set()
        thread.join(timeout=1.0)
