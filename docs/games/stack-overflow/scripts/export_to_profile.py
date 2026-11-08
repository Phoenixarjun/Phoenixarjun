#!/usr/bin/env python3
"""Safely COPY only Stack Overflow public game assets into an existing GitHub profile's Pages docs folder.
   Does NOT modify README.md, other arcade games, GitHub workflows, nor Pages settings.
"""
import argparse, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FILES=['index.html','standalone.html','style.css','arcade-manifest.json','src/physics.mjs','src/renderer.js','src/main.js','assets/stack-overflow-gameplay.gif','assets/arcade-cover.png']
def main():
 p=argparse.ArgumentParser();p.add_argument('profile_repo',type=Path,help='Clone of Phoenixarjun/Phoenixarjun');p.add_argument('--apply',action='store_true',help='Actually copy files; otherwise dry run');args=p.parse_args();repo=args.profile_repo.expanduser().resolve();
 if not (repo/'.git').exists():p.error('target must be a git repository clone')
 target=repo/'docs'/'arcade'/'stack-overflow'
 if target.exists() and any(target.iterdir()):print('Target already exists. Inspect manually before replacing files.');p.error('Refusing to overwrite existing arcade game directory')
 for rel in FILES:
  src=ROOT/rel;dest=target/rel
  if not src.exists():p.error(f'Missing source: {rel}')
  print(f"{'COPY' if args.apply else 'PLAN'}  {src.relative_to(ROOT)} -> {dest.relative_to(repo)}")
  if args.apply:dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
 print('No README, workflows, Pages settings, or other games modified.')
if __name__=='__main__':main()
