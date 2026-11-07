/**
 * Export authentic SVG icons from published Iconify icon sets; NEVER redraw brand marks.
 * Requires: npm install --save-dev @iconify-json/devicon @iconify-json/simple-icons
 *           @iconify-json/lucide @iconify/utils
 * Use in the existing README repo, then commit the generated assets.
 * No browser JS / CDN required at README runtime.
 */
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { resolve } from 'node:path';
import { getIconData, iconToSVG } from '@iconify/utils';

const ROOT = resolve(import.meta.dirname, '..');
const data = JSON.parse(readFileSync(resolve(ROOT, 'content/engineering-stack.curated.example.json'), 'utf8'));
const sources = {
  devicon: JSON.parse(readFileSync(resolve(ROOT, 'node_modules/@iconify-json/devicon/icons.json'), 'utf8')),
  'simple-icons': JSON.parse(readFileSync(resolve(ROOT, 'node_modules/@iconify-json/simple-icons/icons.json'), 'utf8')),
  lucide: JSON.parse(readFileSync(resolve(ROOT, 'node_modules/@iconify-json/lucide/icons.json'), 'utf8')),
};
const output = resolve(ROOT, 'assets/stack/vendor');
mkdirSync(output, { recursive: true });
const report = { generated: [], missing: [], notes: [] };
const escape = (s) => s.replaceAll('&','&amp;').replaceAll('"','&quot;').replaceAll('<','&lt;');
const slugify = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
for (const d of data.domains) {
  for (const item of d.items) {
    let selected, icon;
    for (const candidate of item.candidates) {
      const cut = candidate.indexOf(':');
      const setName = candidate.slice(0, cut); const name = candidate.slice(cut+1);
      const raw = sources[setName];
      if (!raw) continue;
      let found = getIconData(raw, name);
      if (!found && name.endsWith('-original')) {
        found = getIconData(raw, name.slice(0, -9));
      }
      if (found) { selected = candidate; icon = found; break; }
    }
    if (!selected) { report.missing.push({ name: item.name, candidates:item.candidates }); continue; }
    const rendered = iconToSVG(icon, {width:'40', height:'40'});
    // Simple Icons and Lucide are monochrome. Set an accessible theme-safe color
    // without inventing or modifying the trademark shape. Original Devicon colors remain.
    const palette = selected.startsWith('lucide:') ? '#B6FF3B' : '#EEF7EF';
    const body = rendered.body.replaceAll('currentColor', palette);
    const attrs = Object.entries(rendered.attributes).map(([k,v])=>`${k}="${escape(String(v))}"`).join(' ');
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" ${attrs} role="img" aria-label="${escape(item.name)} icon from ${escape(selected)}"><title>${escape(item.name)}</title>${body}</svg>`;
    const file = `${slugify(item.name)}.svg`;
    writeFileSync(resolve(output,file),svg,'utf8');
    item.generatedIcon = `assets/stack/vendor/${file}`;
    item.iconSource = selected;
    report.generated.push({name:item.name,source:selected, file:item.generatedIcon});
  }
}
// This is a content partial, not a new replacement README.
// Native GitHub Markdown table keeps labels readable/selectable and all logos sourced from icon sets.
let lines=['<!-- Generated from established icon libraries, not manually drawn brand artwork. -->', '', '<table>', '  <thead><tr><th>Domain</th><th>Technologies</th></tr></thead>', '  <tbody>'];
for (const d of data.domains) {
  const values=d.items.map((i)=>{
    const ico=i.generatedIcon ? `<img src="./${i.generatedIcon}" width="24" height="24" alt="${escape(i.name)} icon" /> ` : '';
    return `${ico}${escape(i.name)}`;
  }).join(' &nbsp;&nbsp; ');
  lines.push(`    <tr><td><strong>${escape(d.label)}</strong></td><td>${values}</td></tr>`);
}
lines.push('  </tbody>','</table>','');
writeFileSync(resolve(ROOT,'assets/stack/engineering-stack.partial.md'), lines.join('\n'),'utf8');
writeFileSync(resolve(ROOT,'assets/stack/icon-source-report.json'),JSON.stringify(report,null,2)+'\n');
console.log(`Found ${report.generated.length} icons; missing ${report.missing.length}.`);
if(report.missing.length) console.warn('Unresolved icons: ',report.missing.map(x=>x.name).join(', '));
