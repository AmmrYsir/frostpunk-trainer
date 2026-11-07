"""Main entry point for Frostpunk Trainer."""

import sys
import os

# Add src to python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from gui.trainer_window import run_gui

if __name__ == "__main__":
    sys.exit(run_gui())
