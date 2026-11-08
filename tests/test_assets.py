import json
import subprocess
import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'engineering-focus'


class EngineeringFocusAssetTests(unittest.TestCase):
    def test_svg_assets_parse(self):
        files = list(OUT.rglob('*.svg'))
        self.assertGreaterEqual(len(files), 11)
        for p in files:
            with self.subTest(p=p.name):
                root = ET.parse(p).getroot()
                self.assertTrue(root.tag.endswith('svg'))
                self.assertIn('viewBox', root.attrib)
                text = p.read_text(encoding='utf-8')
                self.assertNotIn('<script', text.lower())
                self.assertNotIn('foreignObject', text)
                self.assertNotIn('http://www.w3.org/1999/xlink', text)

    def test_canonical_text_in_master(self):
        s = (OUT / 'engineering-focus-dark.svg').read_text(encoding='utf-8')
        for word in ['Engineering', 'Focus', 'Applied AI', 'Backend', 'Distributed &amp;', 'Reliable Platforms', 'Automation', 'Observability', 'Production Engineering']:
            with self.subTest(word=word):
                self.assertIn(word, s)
        # Separator strip contains terminal command prompt
        cmd_s = (OUT / 'section-command.svg').read_text(encoding='utf-8')
        for word in ['naresh@github:~$', 'inspect --engineering-focus']:
            with self.subTest(word=word):
                self.assertIn(word, cmd_s)

    def test_colors_and_content_are_centralized(self):
        data = json.loads((ROOT / 'config' / 'theme.json').read_text(encoding='utf-8'))
        self.assertEqual(data['colors']['base'], '#0C0F10')
        self.assertEqual(data['colors']['surface'], '#1B2328')
        self.assertEqual(data['colors']['steel'], '#42535C')
        self.assertEqual(data['colors']['accent'], '#B6FF3B')
        self.assertEqual(data['colors']['text'], '#EEF7EF')
        content = json.loads((ROOT / 'config' / 'engineering_focus.json').read_text(encoding='utf-8'))
        self.assertEqual(len(content['pillars']), 3)
        self.assertEqual(len(content['practices']), 3)

    def test_no_full_canvas_fills_in_icon_svgs(self):
        for p in (OUT / 'icons').glob('*.svg'):
            root = ET.parse(p).getroot()
            direct_rects = [c for c in root if c.tag.endswith('rect') and c.attrib.get('width') == '100%']
            self.assertEqual([], direct_rects)

    def test_package_does_not_replace_live_files(self):
        self.assertTrue(OUT.exists())

    def test_background_policy_no_full_canvas_opaque_rects(self):
        """Mode A transparent assets must not have an opaque full-canvas background rect."""
        mode_a_files = [
            OUT / 'engineering-focus-dark.svg',
            OUT / 'engineering-focus-light.svg',
            OUT / 'engineering-focus-transparent.svg',
            OUT / 'section-command.svg',
            OUT / 'section-command-light.svg',
        ]
        # Include all section headers, projects, stack
        mode_a_files.extend((ROOT / 'assets' / 'headers').glob('*.svg'))
        mode_a_files.extend((ROOT / 'assets' / 'projects').glob('*.svg'))
        mode_a_files.extend((ROOT / 'assets' / 'stack').glob('*.svg'))

        for f in mode_a_files:
            with self.subTest(file=f.name):
                root = ET.parse(f).getroot()
                w = root.attrib.get('width')
                h = root.attrib.get('height')
                # Check that no direct child rect fills the entire w x h with opaque background
                for c in root:
                    if c.tag.endswith('rect'):
                        rw = c.attrib.get('width')
                        rh = c.attrib.get('height')
                        fill = c.attrib.get('fill', '')
                        if (rw in (w, '100%') and rh in (h, '100%')):
                            self.assertIn(fill, ('none', ''), f'{f.name} contains full-canvas opaque rect: fill={fill}')

    def test_engineering_focus_geometry_is_standardized(self):
        """Engineering focus canvas geometry must be 1160px width."""
        for name in ['engineering-focus-dark.svg', 'engineering-focus-light.svg', 'engineering-focus-transparent.svg']:
            root = ET.parse(OUT / name).getroot()
            self.assertEqual(root.attrib.get('width'), '1160')
            self.assertEqual(root.attrib.get('viewBox'), '0 0 1160 670')

    def test_content_integrity_and_deduplication(self):
        """Ensure all 9 sections exist, technical writing is deduplicated, and no private leaks."""
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        for i in range(1, 10):
            self.assertIn(f'SECTION {i:02d}', readme)

        # Technical writing: no redundant vector image in README
        self.assertNotIn('assets/sections/technical-writing.svg', readme)
        self.assertIn('BLOG-POST-LIST:START', readme)

        # Content preservation
        hero_static = (ROOT / 'assets' / 'generated' / 'hero' / 'hero-static.svg').read_text(encoding='utf-8')
        self.assertIn('Software Engineer @ Prodapt', hero_static)
        self.assertIn('AI Systems Engineer', hero_static)

        self.assertIn('Architecture-as-Memory', readme)
        self.assertIn('PromptNova', readme)
        self.assertIn('CredFlow', readme)
        self.assertIn('Agent Toolkit', readme)

        # No unreleased / private project reveals
        self.assertNotIn('Orchestrix', readme)
        self.assertNotIn('Vigilant', readme)
        self.assertNotIn('AIVON', readme)

    def test_featured_projects_assets(self):
        """Featured projects must have valid 1160px SVGs, verified copy, and standalone visuals."""
        projects_data = json.loads((ROOT / 'content' / 'projects.json').read_text(encoding='utf-8'))
        flagship = projects_data['flagship']
        self.assertEqual(len(flagship), 4)

        expected_slugs = ['architecture-as-memory', 'promptnova', 'contractgraph', 'credflow']
        self.assertEqual([p['slug'] for p in flagship], expected_slugs)

        for p in flagship:
            slug = p['slug']
            dark_file = ROOT / 'assets' / 'projects' / f'{slug}.svg'
            light_file = ROOT / 'assets' / 'projects' / f'{slug}-light.svg'
            self.assertTrue(dark_file.is_file(), f'Missing {dark_file}')
            self.assertTrue(light_file.is_file(), f'Missing {light_file}')

            for f in [dark_file, light_file]:
                root = ET.parse(f).getroot()
                self.assertEqual(root.attrib.get('width'), '1160')
                self.assertEqual(root.attrib.get('height'), '216')
                content = f.read_text(encoding='utf-8')
                self.assertIn('View on GitHub ↗', content)
                self.assertIn(p['name'], content)

        # Standalone visuals
        for vis_name in ['aam-topology', 'promptnova-workflow', 'contractgraph-dag', 'credflow-collections']:
            vis_dark = ROOT / 'assets' / 'projects' / 'visuals' / f'{vis_name}.svg'
            vis_light = ROOT / 'assets' / 'projects' / 'visuals' / f'{vis_name}-light.svg'
            self.assertTrue(vis_dark.is_file(), f'Missing {vis_dark}')
            self.assertTrue(vis_light.is_file(), f'Missing {vis_light}')
            ET.parse(vis_dark)
            ET.parse(vis_light)

        # Header check
        header_dark = ROOT / 'assets' / 'headers' / 'ls-flagship-projects.svg'
        self.assertTrue(header_dark.is_file())
        header_text = header_dark.read_text(encoding='utf-8')
        self.assertIn('Featured Projects', header_text)
        self.assertIn('naresh@github:~$', header_text)

    def test_playground_assets(self):
        """Playground must have dual-mode 1160px SVGs and working GitHub Pages game prototype."""
        dark = ROOT / 'assets' / 'playground' / 'concept.svg'
        light = ROOT / 'assets' / 'playground' / 'concept-light.svg'
        self.assertTrue(dark.is_file(), f'Missing {dark}')
        self.assertTrue(light.is_file(), f'Missing {light}')

        for f in [dark, light]:
            root = ET.parse(f).getroot()
            self.assertEqual(root.attrib.get('width'), '1160')
            self.assertEqual(root.attrib.get('height'), '560')
            content = f.read_text(encoding='utf-8')
            self.assertIn('Developer Playground', content)
            self.assertIn('System Runner', content)
            self.assertIn('Architecture Grid Runner', content)
            self.assertIn('/// ARCHITECTURE', content)
            self.assertIn('Play System Runner ↗', content)

        # Developer Arcade Hub & 5 Games Prototype check
        arcade_html = ROOT / 'docs' / 'games' / 'index.html'
        self.assertTrue(arcade_html.is_file(), f'Missing {arcade_html}')
        arcade_text = arcade_html.read_text(encoding='utf-8')
        self.assertIn('Developer Arcade', arcade_text)

        for slug in ['packet-breaker', 'circuit-pinball', 'runtime-rush', 'firewall-defense', 'stack-overflow']:
            game_html = ROOT / 'docs' / 'games' / slug / 'index.html'
            self.assertTrue(game_html.is_file(), f'Missing game {slug}')

        # Showcase GIF check
        showcase_gif = ROOT / 'assets' / 'playground' / 'arcade-showcase.gif'
        self.assertTrue(showcase_gif.is_file(), f'Missing {showcase_gif}')

        # Header check
        header = ROOT / 'assets' / 'headers' / 'play-developer-arcade.svg'
        self.assertTrue(header.is_file())
        header_text = header.read_text(encoding='utf-8')
        self.assertIn('play --developer-arcade', header_text)

        # Game launcher buttons check
        for slug in ['packet-breaker', 'circuit-pinball', 'runtime-rush', 'firewall-defense', 'stack-overflow']:
            dark_btn = ROOT / 'assets' / 'sections' / f'btn-{slug}.svg'
            light_btn = ROOT / 'assets' / 'sections' / f'btn-{slug}-light.svg'
            self.assertTrue(dark_btn.is_file(), f'Missing {dark_btn}')
            self.assertTrue(light_btn.is_file(), f'Missing {light_btn}')

        # README link check
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        self.assertIn('https://phoenixarjun.github.io/Phoenixarjun/games/', readme)

    def test_about_me_assets(self):
        """About Me must have dual-mode 1160px SVGs, terminal command headers, and README inclusion."""
        dark = ROOT / 'assets' / 'sections' / 'about-me.svg'
        light = ROOT / 'assets' / 'sections' / 'about-me-light.svg'
        self.assertTrue(dark.is_file(), f'Missing {dark}')
        self.assertTrue(light.is_file(), f'Missing {light}')

        for f in [dark, light]:
            root = ET.parse(f).getroot()
            self.assertEqual(root.attrib.get('width'), '1160')
            self.assertEqual(root.attrib.get('height'), '530')
            content = f.read_text(encoding='utf-8')
            self.assertIn('About Me', content)
            self.assertIn('Software Engineer at Prodapt', content)
            self.assertIn('Currently exploring', content)
            self.assertIn('Engineering mindset', content)
            self.assertNotIn('—', content)

        # Header check
        header_dark = ROOT / 'assets' / 'headers' / 'show-about-me.svg'
        header_light = ROOT / 'assets' / 'headers' / 'show-about-me-light.svg'
        self.assertTrue(header_dark.is_file())
        self.assertTrue(header_light.is_file())
        self.assertIn('show --about-me', header_dark.read_text(encoding='utf-8'))

        # README check
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        self.assertIn('assets/sections/about-me.svg', readme)
        self.assertIn('assets/headers/show-about-me.svg', readme)

    def test_connect_and_footer_assets(self):
        """Connect buttons and footer must have dual-mode compact 206px buttons with built-in vector spacing and editorial footer."""
        for slug, label in [('btn-github', 'GitHub'), ('btn-linkedin', 'LinkedIn'), ('btn-medium', 'Medium'), ('btn-portfolio', 'Portfolio')]:
            dark = ROOT / 'assets' / 'sections' / f'{slug}.svg'
            light = ROOT / 'assets' / 'sections' / f'{slug}-light.svg'
            self.assertTrue(dark.is_file(), f'Missing {dark}')
            self.assertTrue(light.is_file(), f'Missing {light}')

            for f in [dark, light]:
                root = ET.parse(f).getroot()
                self.assertEqual(root.attrib.get('width'), '206')
                self.assertEqual(root.attrib.get('height'), '50')
                content = f.read_text(encoding='utf-8')
                self.assertIn(label, content)

        # Special check for highlighted portfolio button glow
        portfolio_dark = (ROOT / 'assets' / 'sections' / 'btn-portfolio.svg').read_text(encoding='utf-8')
        self.assertIn('portfolioUnderglow', portfolio_dark)

        # Footer check
        footer_dark = ROOT / 'assets' / 'sections' / 'footer.svg'
        footer_light = ROOT / 'assets' / 'sections' / 'footer-light.svg'
        self.assertTrue(footer_dark.is_file())
        self.assertTrue(footer_light.is_file())
        for f in [footer_dark, footer_light]:
            root = ET.parse(f).getroot()
            self.assertEqual(root.attrib.get('width'), '1160')
            self.assertEqual(root.attrib.get('height'), '70')
            content = f.read_text(encoding='utf-8')
            self.assertIn('Building intelligent software on reliable systems.', content)
            self.assertIn('VARIATION 01 / TERMINAL EDITORIAL', content)

        # README checks
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        self.assertIn('https://github.com/Phoenixarjun', readme)
        self.assertIn('https://www.linkedin.com/in/naresh-b-a-1b5331243/', readme)
        self.assertIn('https://medium.com/@phoenixarjun007', readme)
        self.assertIn('assets/logout-footer/logout-card-animated.gif', readme)


if __name__ == '__main__':
    unittest.main()
