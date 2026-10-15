"""Preserve API69; inspect actual bound check details in successor API70."""
import ast,json,shutil
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';OLD=BASE/'api-v69';API=BASE/'api-v70'
def replace(p,a,b):
    s=p.read_text();assert s.count(a)==1,(p,a);p.write_text(s.replace(a,b,1))
def main():
    assert not API.exists() and not (BASE/'lesson-host-composition-v20').exists()
    ignore=shutil.ignore_patterns('receipts','__pycache__','source-manifest.json','contract-profile.json')
    shutil.copytree(OLD,API,ignore=ignore)
    shutil.copytree(BASE/'lesson-host-composition-v19',BASE/'lesson-host-composition-v20',ignore=ignore)
    replace(BASE/'lesson-host-composition-v20/host.py','api-v69/service.py','api-v70/service.py')
    replace(API/'lesson_selection.py','lesson-host-composition-v19','lesson-host-composition-v20')
    replace(API/'checks_generated_candidate.py','_cal_api69_generated_candidate_checks','_cal_api70_generated_candidate_checks')
    replace(API/'test_generated_candidate.py',"        self.assertTrue(report['gaps']);self.assertIn('full domain reference resolver',str(report['checks']))",'''        self.assertTrue(report['gaps'])
        unresolved=[c for c in report['checks'] if c['check_ref'].startswith('check:remaining-domain-reference-')]
        self.assertEqual(len(unresolved),2)
        for check in unresolved:
            self.assertEqual(check['result'],'not-evaluable')
            detail=P.frame_parse(service.vault.object_read(check['evidence_bindings'][0]))
            self.assertIn('full domain reference resolver',detail['details']['reason'])
            self.assertIn(detail['details']['carrier_ref'],[t['carrier_ref'] for t in proposal['targets']])''')
    for p in API.rglob('*.py'):ast.parse(p.read_bytes())
    print(json.dumps({'result':'AUTHORED','successor':'api-v70','changed_test_methods':1,'production_validator_changed':False,'authority_effect':'none'}))
if __name__=='__main__':main()
