import os
from pathlib import Path
import sys

ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
USER = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "DarknessLiesAhead"
DATA = ROOT / "data"
ASSETS = ROOT / "assets"
