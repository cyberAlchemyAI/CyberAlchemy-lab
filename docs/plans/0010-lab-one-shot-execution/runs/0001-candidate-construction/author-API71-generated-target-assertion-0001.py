"""Correct the test's target header selector; preserve frozen API70."""
import ast,json,shutil
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4];BASE=ROOT/'product/lab/release-candidates/v1/interface'
OLD=BASE/'api-v70';API=BASE/'api-v71'
def replace(p,a,b):
    s=p.read_text();assert s.count(a)==1,(p,a);p.write_text(s.replace(a,b,1))
def main():
    assert not API.exists() and not (BASE/'lesson-host-composition-v21').exists()
    ignore=shutil.ignore_patterns('receipts','__pycache__','source-manifest.json','contract-profile.json')
    shutil.copytree(OLD,API,ignore=ignore);shutil.copytree(BASE/'lesson-host-composition-v20',BASE/'lesson-host-composition-v21',ignore=ignore)
    replace(BASE/'lesson-host-composition-v21/host.py','api-v70/service.py','api-v71/service.py')
    replace(API/'lesson_selection.py','lesson-host-composition-v20','lesson-host-composition-v21')
    replace(API/'checks_generated_candidate.py','_cal_api70_generated_candidate_checks','_cal_api71_generated_candidate_checks')
    replace(API/'test_generated_candidate.py',"[t['carrier_ref'] for t in proposal['targets']]","[t['artifact']['carrier_ref'] for t in proposal['targets']]")
    for p in API.rglob('*.py'):ast.parse(p.read_bytes())
    print(json.dumps({'result':'AUTHORED','successor':'api-v71','production_validator_changed':False,'authority_effect':'none'}))
if __name__=='__main__':main()
