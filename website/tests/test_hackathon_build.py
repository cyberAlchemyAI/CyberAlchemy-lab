import json,os,shutil,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'source/governance-lab-series'))
from research_pages import hackathon_bindings
class HackathonBuildTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.config=json.loads((ROOT/'hackathon.json').read_text());self.write_config();shutil.copytree(ROOT/'source/governance-lab-series/downloads',self.root/'downloads')
 def tearDown(self):self.temp.cleanup()
 def write_config(self):(self.root/'hackathon.json').write_text(json.dumps(self.config))
 def test_calendar_updates_existing_events_and_separates_windows(self):
  hackathon_bindings(self.root);raw=(self.root/'downloads/hackathon-dates.ics').read_bytes();self.assertTrue(all(len(line)<=75 for line in raw.split(b'\r\n')));text=raw.decode().replace('\r\n ','').replace('\r\n','\n');self.assertEqual(text.count('BEGIN:VEVENT'),7)
  for stamp in ['20261016T210000Z','20261024T025959Z','20261024T030000Z','20261124T025959Z','20261124T150000Z','20261125T210000Z']:self.assertIn('DTSTART:'+stamp,text)
  self.assertIn('UID:craft-lab-hackathon-registration-2026-10-13T21:00:00+00:00@cyberalchemy-lab',text);self.assertEqual(text.count('SEQUENCE:1'),7)
 def test_changed_schedule_rejects_stale_rules(self):
  self.config['submissions_close_at']='2026-11-22T23:59:59-03:00';self.write_config()
  with self.assertRaisesRegex(ValueError,'Rules documents disagree'):hackathon_bindings(self.root)
 def test_changed_download_rejected(self):
  p=self.root/'downloads/hackathon-rules.pdf';p.write_bytes(p.read_bytes()+b'!')
  with self.assertRaisesRegex(ValueError,'Rules download does not match'):hackathon_bindings(self.root)
if __name__=='__main__':unittest.main()
