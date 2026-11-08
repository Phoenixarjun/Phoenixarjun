/** Safely copy public runtime assets into a local profile repo's docs/packet-breaker. */
import fs from 'node:fs';import path from 'node:path';
const root=path.resolve(import.meta.dirname,'..');
const idx=process.argv.indexOf('--target');
if(idx<0||!process.argv[idx+1]){console.error('Usage: node scripts/export-pages.mjs --target "/path/to/Phoenixarjun"');process.exit(1);}
const repo=path.resolve(process.argv[idx+1]);
if(!fs.existsSync(path.join(repo,'.git'))&&!fs.existsSync(path.join(repo,'README.md'))){console.error('Target must be an existing GitHub profile checkout with README.md or .git');process.exit(1);}
const dest=path.join(repo,'docs','packet-breaker');
const files=['index.html','style.css','dist/game.bundle.js','assets/favicon.svg'];
for(const rel of files){const from=path.join(root,rel),to=path.join(dest,rel);if(!fs.existsSync(from))throw new Error(`Missing runtime file ${rel}`);fs.mkdirSync(path.dirname(to),{recursive:true});fs.copyFileSync(from,to);console.log(`Copied: docs/packet-breaker/${rel}`);}
console.log(`\nExport complete. Pages is NOT deployed. Review local changes and Pages settings before publishing.`);
