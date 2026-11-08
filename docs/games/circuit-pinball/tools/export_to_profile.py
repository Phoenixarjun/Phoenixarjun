#!/usr/bin/env python3
"""Safe additive copy into a GitHub profile's docs/arcade/circuit-pinball folder.
Default is dry-run; never modifies README, GitHub workflows, or another game's files.
"""
import argparse
import shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FILES=['index.html','style.css','assets/favicon.svg','src/physics.js','src/audio.js','src/render.js','src/game.js']

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile-repo',type=Path,required=True,help='path to local checkout of Phoenixarjun/Phoenixarjun')
    parser.add_argument('--apply',action='store_true',help='actually copy files; default is dry-run')
    parser.add_argument('--force',action='store_true',help='allow overwriting existing circuit-pinball files only')
    args=parser.parse_args()
    repo=args.profile_repo.resolve()
    if not (repo/'.git').exists():parser.error('profile-repo must be a Git checkout containing .git')
    destination=repo/'docs'/'arcade'/'circuit-pinball'
    conflicts=[f for f in FILES if (destination/f).exists()]
    if conflicts and not args.force:parser.error(f'existing game files found: {conflicts}; no files changed; review before using --force')
    print('Mode:', 'COPY' if args.apply else 'DRY RUN')
    for relative in FILES:print(f'  {ROOT/relative} -> {destination/relative}')
    if not args.apply:print('Nothing copied. Run with --apply when reviewed.');return
    for relative in FILES:
        target=destination/relative;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/relative,target)
    print('Finished game-only export. No README/workflow/other-game files touched.')

if __name__=='__main__':main()
