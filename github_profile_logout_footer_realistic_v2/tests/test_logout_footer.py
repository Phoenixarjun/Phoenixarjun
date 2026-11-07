import json, unittest
from pathlib import Path
from PIL import Image,ImageSequence

ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'assets/logout-footer'

class FooterTests(unittest.TestCase):
 def test_robot_real_transparency(self):
  p=A/'robot-realistic-transparent.png';self.assertTrue(p.is_file())
  im=Image.open(p).convert('RGBA')
  alpha=im.getchannel('A')
  self.assertLess(alpha.getextrema()[0],2)
  self.assertEqual(alpha.getextrema()[1],255)
  self.assertGreater(sum(a>0 for a in alpha.get_flattened_data()),25000)
 def test_files(self):
  for name in ['logout-card-animated.gif','logout-card-static.png','logout-terminal-separator.svg']:
   self.assertTrue((A/name).is_file(),name)
 def test_gif_animation(self):
  im=Image.open(A/'logout-card-animated.gif')
  self.addCleanup(im.close)
  self.assertEqual(im.size,(940,300))
  self.assertGreater(im.n_frames,12)
  self.assertEqual(im.info.get('loop'),0)
  self.assertGreater(sum(im.info.get('duration',0) for _ in [1]),0)
  # typing is visible through distinct frames
  samples=[]
  for idx in [0,min(8,im.n_frames-1),min(16,im.n_frames-1),min(27,im.n_frames-1)]:
   im.seek(idx);samples.append(im.convert('RGB').crop((355,75,880,122)).tobytes())
  self.assertGreaterEqual(len(set(samples)),3)
 def test_static_outer_corners_transparent(self):
  with Image.open(A/'logout-card-static.png') as im:
   self.assertEqual(im.convert('RGBA').getpixel((0,0))[3],0)
   self.assertEqual(im.convert('RGBA').getpixel((im.width-1, im.height-1))[3],0)
 def test_content(self):
  d=json.loads((ROOT/'content/logout-footer.json').read_text('utf-8'))
  self.assertEqual(d['title'],'Thanks for stopping by.')
  self.assertEqual(d['closing'],'// Session Closed //')
  self.assertEqual(len(d['principles']),4)
  self.assertEqual(d['command'],'logout')
 def test_no_sensitive_files(self):
  self.assertFalse((ROOT/'.env').exists())
  self.assertFalse((ROOT/'README.md').exists())
if __name__=='__main__':unittest.main()
