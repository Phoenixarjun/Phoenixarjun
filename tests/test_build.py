import json
import subprocess
import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from graphics import city, hero, project_card

class BuildSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.themes=json.loads((ROOT/'design/themes.json').read_text())
        cls.profile=json.loads((ROOT/'content/profile.json').read_text())
        cls.projects=json.loads((ROOT/'content/projects.json').read_text())
        cls.data=json.loads((ROOT/'data/contributions.json').read_text())

    def test_every_theme_generates_valid_hero(self):
        for t in self.themes['presets'].values():
            ET.fromstring(hero(self.profile,t))

    def test_project_card_is_valid_svg(self):
        t=self.themes['presets']['titanium-hacker']
        for index,p in enumerate(self.projects['flagship'],1):
            ET.fromstring(project_card(p,t,index))

    def test_contribution_city_is_valid_for_demo_and_real_data(self):
        t=self.themes['presets']['titanium-hacker']
        ET.fromstring(city(self.data,t))
        real={'status':'ok','days':[{'date':'2026-11-06','count':2},{'date':'2026-11-07','count':18}], 'fetched_at_utc':'2026-11-07T00:00:00+00:00'}
        rendered=city(real,t)
        ET.fromstring(rendered)
        self.assertIn('20 contributions',rendered)

    def test_build_preserves_existing_live_readme_and_workflow(self):
        # In a real profile repository these files ALREADY exist. The preview
        # generator must never modify either during an ordinary build.
        readme=ROOT/'README.md'
        workflow=ROOT/'.github'/'workflows'/'profile.yml'
        before_readme=readme.read_bytes() if readme.is_file() else None
        before_workflow=workflow.read_bytes() if workflow.is_file() else None
        subprocess.run([sys.executable, str(ROOT/'scripts'/'build.py'), '--skip-previews'],
                       cwd=ROOT, check=True, capture_output=True, text=True)
        if before_readme is not None:
            self.assertEqual(readme.read_bytes(), before_readme)
        if before_workflow is not None:
            self.assertEqual(workflow.read_bytes(), before_workflow)

if __name__=='__main__':
    unittest.main()
