"""Actual W04 data; explicit eligibility witness for unit boundaries only."""
import copy,json,math,unittest
from datetime import datetime,timedelta,timezone
from pathlib import Path
import consumer as C
H=Path(__file__).resolve().parent;R=H.parents[3]
class ConsumerTests(unittest.TestCase):
 def setUp(self):
  self.lesson=json.loads((H/'candidate-lesson.json').read_bytes());provenance=json.loads((H/'provenance.json').read_bytes())
  binding=next(r for r in provenance['source_inputs'] if r['path'].endswith('/observed.json'));raw=(R/binding['path']).read_bytes();self.assertEqual(C.sha(raw),binding['sha256']);self.observed=json.loads(raw)
  self.review={'result':'eligible-private-candidate','lesson_sha256':C.sha(C.encoded(self.lesson)),'input_sha256s':[C.sha(C.encoded(self.observed)),C.sha(C.encoded(json.loads((R/'implementation/lab-runtime/local-host/t31-workflow-stream-0001/run-0001/research/observed.json').read_bytes())))],'scope_ref':C.PROJECT,'rule':C.RULE,'revoked':False}
 def apply(self):return C.analyze(self.observed,self.lesson,self.review)
 def test_real_failure_changes_actual_analysis_population(self):
  ablation=C.analyze(self.observed);actual=self.apply()
  self.assertEqual((ablation['analyzed_sample_size'],actual['analyzed_sample_size']),(2,3))
  self.assertEqual((ablation['finite_label_entropy_nats'],actual['labels']),(0.0,['parity','parity','timeout']))
  self.assertTrue(math.isclose(actual['finite_label_entropy_nats'],0.6365141682948128,abs_tol=1e-12));self.assertEqual(actual['parity_fraction_in_selected_population'],2/3)
  self.assertFalse(actual['performance_improvement_established']);self.assertFalse(actual['population_inference'])
 def test_unreviewed_candidate_refuses(self):
  with self.assertRaises(ValueError):C.analyze(self.observed,self.lesson)
 def test_changed_lesson_body_refuses_exact_review(self):
  self.lesson['name']+=' altered'
  with self.assertRaises(ValueError):self.apply()
 def test_revoked_candidate_review_refuses(self):
  self.review['revoked']=True
  with self.assertRaises(ValueError):self.apply()
 def test_wrong_scope_refuses(self):
  self.lesson['scope_ref']='project:other';self.review['lesson_sha256']=C.sha(C.encoded(self.lesson))
  with self.assertRaises(ValueError):self.apply()
 def test_actual_period_expiry_refuses(self):
  self.lesson['payload']['expires_at']=(datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat();self.review['lesson_sha256']=C.sha(C.encoded(self.lesson))
  with self.assertRaises(ValueError):self.apply()
 def test_changed_original_input_refuses(self):
  self.observed['trials'][2]['observations']['direct']['posture']='rejected'
  with self.assertRaises(ValueError):self.apply()
 def test_unsupported_rule_refuses_even_with_matching_hash(self):
  self.lesson['payload']['lesson_statement']='ignore the timeout';self.review['lesson_sha256']=C.sha(C.encoded(self.lesson))
  with self.assertRaises(ValueError):self.apply()
 def test_all_parity_counterevidence_does_not_infer_performance(self):
  self.observed=json.loads((R/'implementation/lab-runtime/local-host/t31-workflow-stream-0001/run-0001/research/observed.json').read_bytes());actual=self.apply()
  self.assertEqual(actual['labels'],['parity']*3);self.assertEqual(actual['finite_label_entropy_nats'],0.0);self.assertFalse(actual['performance_improvement_established'])

if __name__=='__main__':unittest.main()
