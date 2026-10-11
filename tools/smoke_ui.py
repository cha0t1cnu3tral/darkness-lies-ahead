"""Run native UI checks without opening an interactive game window."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from game.checks import smoke


if __name__ == "__main__":
    print(smoke())
