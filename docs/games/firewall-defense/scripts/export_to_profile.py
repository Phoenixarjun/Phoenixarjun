"""Add-only export of Game 04 into a separately approved profile repository.
Never writes README.md or GitHub workflow files. No network calls.
"""
from __future__ import annotations
import argparse
import shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FILES=['index.html','style.css','src/engine.mjs','src/renderer.js','src/main.js','assets/arcade-cover.png','assets/firewall-defense-gameplay.gif']

def main():
    ap=argparse.ArgumentParser(description='Copy only Firewall Defense into docs/arcade/firewall-defense/')
    ap.add_argument('profile_repo',type=Path)
    ap.add_argument('--dry-run',action='store_true')
    ap.add_argument('--force',action='store_true',help='Explicitly allow overwriting existing Game 04 files')
    args=ap.parse_args()
    target=(args.profile_repo/'docs'/'arcade'/'firewall-defense').resolve()
    if not args.profile_repo.is_dir():ap.error('Profile repository directory does not exist')
    if not (args.profile_repo/'.git').exists():ap.error('Specified directory is not a Git repository (missing .git)')
    for name in FILES:
        src=ROOT/name;dst=target/name
        if not src.is_file():raise SystemExit(f'Missing source: {src}')
        if dst.exists() and not args.force:raise SystemExit(f'Refusing existing destination: {dst}. Use --force explicitly after review.')
    for name in FILES:
        src=ROOT/name;dst=target/name
        print(('WOULD COPY' if args.dry_run else 'COPY'),name,'→',dst)
        if not args.dry_run:dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
    print('Done; README and GitHub workflows were not touched.')
if __name__=='__main__':main()
