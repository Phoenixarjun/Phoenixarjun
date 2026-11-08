import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
from importlib.util import spec_from_file_location, module_from_spec

ROOT = Path(__file__).resolve().parents[1]

class AssetsTest(unittest.TestCase):
    def test_svgs_valid(self):
        for p in (ROOT/'assets/projects').rglob('*.svg'):
            with self.subTest(file=p.name):
                root=ET.parse(p).getroot()
                self.assertEqual(root.tag,'{http://www.w3.org/2000/svg}svg')
    def test_card_title_number_and_content(self):
        s=(ROOT/'assets/projects/contractgraph.svg').read_text()
        for q in ('ContractGraph','03','Claude Code','JSON Schema','View on GitHub','REPAIR','FINAL'):
            self.assertIn(q,s)
    def test_light_variant_independent(self):
        dark=(ROOT/'assets/projects/contractgraph.svg').read_text()
        light=(ROOT/'assets/projects/contractgraph-light.svg').read_text()
        self.assertNotEqual(dark, light)
        self.assertIn('#B6FF3B', dark)
        self.assertIn('#56890A', light)
    def test_graph_has_distinct_nodes(self):
        s=(ROOT/'assets/projects/visuals/contractgraph-dag.svg').read_text()
        for q in ('N1','N2','N3','SCHEMA','GATES','FINAL','REPAIR'):
            self.assertIn(q,s)
    def test_no_fabricated_metrics(self):
        s=(ROOT/'assets/projects/contractgraph.svg').read_text()
        self.assertNotIn('100%',s)
        self.assertNotIn('production-ready',s)
if __name__ == '__main__': unittest.main()
