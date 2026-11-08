"""Registration and project-window boundaries must remain independent."""
import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'source/governance-lab-series'))
from event_status import event_state
class EventStatusTests(unittest.TestCase):
 def setUp(self):
  self.config=json.loads((ROOT/'hackathon.json').read_text())
  self.config.update({name+'_url':'https://example.com/'+name for name in ['registration','submission','gallery','voting']})
 def test_independent_windows(self):
  cases=[('2026-10-16T17:59:59-03:00','before',False,False),('2026-10-16T18:00:00-03:00','registration',True,False),('2026-10-23T23:59:59-03:00','registration',True,False),('2026-10-24T00:00:00-03:00','building',False,True),('2026-11-23T23:59:59-03:00','building',False,True),('2026-11-24T00:00:00-03:00','submitted',False,False),('2026-11-24T12:00:00-03:00','voting',False,False),('2026-11-25T18:00:00-03:00','review',False,False),('2026-11-26T00:00:00-03:00','ended',False,False)]
  for at,phase,registration,submission in cases:
   with self.subTest(at=at):
    value=event_state(self.config,at);self.assertEqual(value['phase'],phase);self.assertEqual(value['actions']['registration']['enabled'],registration);self.assertEqual(value['actions']['submission']['enabled'],submission)
 def test_missing_forms_and_unverified_ballot_stay_unavailable(self):
  config=json.loads((ROOT/'hackathon.json').read_text())
  for at in ['2026-10-16T18:00:00-03:00','2026-10-24T00:00:00-03:00','2026-11-24T12:00:00-03:00']:
   for key in ['registration','submission','voting']:self.assertFalse(event_state(config,at)['actions'][key]['enabled'])
  self.assertFalse(event_state(self.config,'2026-11-24T12:00:00-03:00')['actions']['voting']['enabled'])
  self.config['voting_access_verified']=True
  self.assertTrue(event_state(self.config,'2026-11-24T12:00:00-03:00')['actions']['voting']['enabled'])
  self.assertFalse(event_state(self.config,'2026-11-25T18:00:00-03:00')['actions']['voting']['enabled'])
 def test_waiting_window_and_naive_time(self):
  self.config['build_opens_at']='2026-10-24T01:00:00-03:00'
  value=event_state(self.config,'2026-10-24T00:00:00-03:00');self.assertEqual(value['phase'],'waiting-build');self.assertFalse(value['actions']['submission']['enabled'])
  with self.assertRaises(ValueError):event_state(self.config,'2026-10-24T00:00:00')
if __name__=='__main__':unittest.main()
