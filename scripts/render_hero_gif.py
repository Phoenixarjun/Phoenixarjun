"""Compatibility wrapper for Hero V4 GIF generation. Delegates to generate_hero.py."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    cmd = [sys.executable, str(ROOT / 'scripts/generate_hero.py')]
    subprocess.run(cmd, check=True)


if __name__ == '__main__':
    main()
