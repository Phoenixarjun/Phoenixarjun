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


if __name__ == '__main__':
    unittest.main()
