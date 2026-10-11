"""Collect dependency license texts from installed distributions into a build."""

import importlib.metadata
from pathlib import Path
import shutil
import sys


def collect(destination):
    destination = Path(destination)
    for name in ("wxPython", "pygame-ce", "pyinstaller"):
        distribution = importlib.metadata.distribution(name)
        for entry in distribution.files or []:
            filename = str(entry).lower()
            if entry.suffix.lower() not in (".txt", ".md") or not any(
                term in filename for term in ("license", "copying", "lgpl", "copyright")
            ):
                continue
            target = destination / name / entry.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(distribution.locate_file(entry), target)
    python_license = Path(sys.base_prefix) / "LICENSE.txt"
    if python_license.exists():
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(python_license, destination / "Python-LICENSE.txt")


if __name__ == "__main__":
    collect(sys.argv[1])
