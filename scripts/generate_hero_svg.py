"""Compatibility wrapper for Hero V4 generation. Delegates to generate_hero.py."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / 'scripts') not in sys.path:
    sys.path.insert(0, str(ROOT / 'scripts'))


def generate_hero_svg(animated: bool = False) -> str:
    """Return self-contained Hero V4 SVG string."""
    try:
        from generate_hero import main_svg
    except ImportError:
        from scripts.generate_hero import main_svg
    return main_svg()


def main():
    cmd = [sys.executable, str(ROOT / 'scripts/generate_hero.py'), '--static-only']
    subprocess.run(cmd, check=True)


if __name__ == '__main__':
    main()
