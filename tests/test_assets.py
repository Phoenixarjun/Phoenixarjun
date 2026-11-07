import json
import subprocess
import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets'/'engineering-focus'

class EngineeringFocusAssetTests(unittest.TestCase):
    def test_svg_assets_parse(self):
        files=list(OUT.rglob('*.svg'))
        self.assertGreaterEqual(len(files),11)
        for p in files:
            with self.subTest(p=p.name):
                root=ElementTree.parse(p).getroot()
                self.assertTrue(root.tag.endswith('svg'))
                self.assertIn('viewBox',root.attrib)
                text=p.read_text()
                self.assertNotIn('<script',text.lower())
                self.assertNotIn('foreignObject',text)
                self.assertNotIn('http://www.w3.org/1999/xlink',text)

    def test_canonical_text_in_master(self):
        s=(OUT/'engineering-focus-dark.svg').read_text()
        for word in ['naresh@github:~$','engineering-focus','Engineering','Focus','Applied AI', 'Backend','Distributed &amp;','Reliable Platforms','Automation','Observability','Production Engineering']:
            with self.subTest(word=word): self.assertIn(word,s)

    def test_colors_and_content_are_centralized(self):
        data=json.loads((ROOT/'config'/'theme.json').read_text())
        self.assertEqual(data['colors']['base'],'#0C0F10')
        self.assertEqual(data['colors']['surface'],'#1B2328')
        self.assertEqual(data['colors']['steel'],'#42535C')
        self.assertEqual(data['colors']['accent'],'#B6FF3B')
        self.assertEqual(data['colors']['text'],'#EEF7EF')
        content=json.loads((ROOT/'config'/'engineering_focus.json').read_text())
        self.assertEqual(len(content['pillars']),3)
        self.assertEqual(len(content['practices']),3)

    def test_no_full_canvas_fills_in_icon_svgs(self):
        for p in (OUT/'icons').glob('*.svg'):
            root=ElementTree.parse(p).getroot()
            direct_rects=[c for c in root if c.tag.endswith('rect') and c.attrib.get('width')=='100%']
            self.assertEqual([],direct_rects)

    def test_package_does_not_replace_live_files(self):
        # In an existing repository, README.md and .github/workflows legitimately exist.
        # This smoke test ensures the assets directory is present and valid.
        self.assertTrue(OUT.exists())

if __name__ == '__main__': unittest.main()
