/** Zero-dependency classic JS bundle for file:// and GitHub Pages. */
import fs from 'node:fs';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'..');
let physics=fs.readFileSync(path.join(root,'src/physics.mjs'),'utf8');
let game=fs.readFileSync(path.join(root,'src/game.js'),'utf8');
physics=physics.replace(/\bexport\s+(?=(?:const|function)\b)/g,'');
game=game.replace(/^import\s+\{[^\n]+\}\s+from\s+['"]\.\/physics\.mjs['"];?\s*\n/,'');
if(game.startsWith('import '))throw new Error('Unresolved imports in game.js');
const output=`/* PACKET BREAKER, generated from src/*.js by node scripts/build.mjs. Do not edit directly. */\n(()=>{\n'use strict';\n${physics}\n${game}\n})();\n`;
fs.writeFileSync(path.join(root,'dist/game.bundle.js'),output);
// Convenience all-in-one HTML for offline sharing / quick demo.
const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
const css=fs.readFileSync(path.join(root,'style.css'),'utf8');
const favicon=fs.readFileSync(path.join(root,'assets/favicon.svg'),'utf8');
const inline=html.replace('<link rel="stylesheet" href="./style.css" />',`<style>\n${css}\n</style>`)
 .replace('<script defer src="./dist/game.bundle.js"></script>','')
 .replace('<link rel="icon" href="./assets/favicon.svg" type="image/svg+xml" />',`<link rel="icon" href="data:image/svg+xml,${encodeURIComponent(favicon)}" type="image/svg+xml" />`)
 .replace('</body>',`<script>\n${output}\n</script>\n</body>`);
fs.writeFileSync(path.join(root,'standalone.html'),inline);
console.log(`Generated standalone.html (${(inline.length/1024).toFixed(1)} KiB)`);
console.log(`Generated dist/game.bundle.js (${(output.length/1024).toFixed(1)} KiB)`);
