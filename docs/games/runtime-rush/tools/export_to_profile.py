#!/usr/bin/env python3
"""Safe, additive export to GitHub profile Pages. Dry-run unless --apply.

Does NOT overwrite README, workflows, other games, or existing files.
Does NOT commit, push, or deploy.
"""
import argparse
from pathlib import Path
import shutil, sys
ROOT=Path(__file__).resolve().parents[1]
FILES=['index.html','style.css','src/game.js','src/physics.mjs','src/renderer.js','src/fallback.js','src/audio.js','assets/favicon.svg']
def main():
    p=argparse.ArgumentParser(description='Export Runtime Rush to an existing GitHub Profile repository safely')
    p.add_argument('--profile-repo',required=True,type=Path)
    p.add_argument('--apply',action='store_true')
    args=p.parse_args()
    repo=args.profile_repo.resolve()
    if not (repo/'.git').exists() or not (repo/'README.md').is_file():
        sys.exit('Refusing: --profile-repo must point to a Git checkout with README.md')
    dest=repo/'docs'/'arcade'/'runtime-rush'
    collisions=[str(dest/f) for f in FILES if (dest/f).exists()]
    if collisions:
        sys.exit('Refusing to overwrite existing files:\n'+'\n'.join(collisions))
    print('Mode:', 'APPLY' if args.apply else 'DRY RUN')
    print('Destination:',dest)
    for rel in FILES:
        print(f'{ROOT/rel} -> {dest/rel}')
        if args.apply:
            d=dest/rel;d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,d)
    print('No README/workflows/Pages settings changed. No commit or push performed.')
if __name__=='__main__':main()
