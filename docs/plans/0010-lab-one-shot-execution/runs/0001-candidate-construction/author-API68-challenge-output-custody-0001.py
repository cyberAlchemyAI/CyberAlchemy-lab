"""Read actual durable proposal output objects through the output custody API."""
import json
from pathlib import Path
import shutil
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';OLD=BASE/'api-v67';API=BASE/'api-v68'
def replace(p,a,b):
    value=p.read_text();assert value.count(a)==1,(p,a);p.write_text(value.replace(a,b,1))
def main():
    assert not API.exists() and not (BASE/'lesson-host-composition-v18').exists()
    ignore=shutil.ignore_patterns('receipts','__pycache__','source-manifest.json','contract-profile.json')
    shutil.copytree(OLD,API,ignore=ignore)
    shutil.copytree(BASE/'lesson-host-composition-v17',BASE/'lesson-host-composition-v18',ignore=ignore)
    replace(BASE/'lesson-host-composition-v18/host.py','api-v67/service.py','api-v68/service.py')
    replace(API/'lesson_selection.py','lesson-host-composition-v17','lesson-host-composition-v18')
    p=API/'test_challenge_api.py';value=p.read_text();assert value.count('service.vault.material(')==3
    p.write_text(value.replace('service.vault.material(','service.vault.object_read('))
    print(json.dumps({'result':'AUTHORED','successor':'api-v68','revised_test':'test_01_actual_challenge_proposal_preserves_exact_revision_and_original_bytes',
        'reason':'actual API67 successful result reached output inspection; output objects are not selected inputs','authority_effect':'none'}))
if __name__=='__main__':main()
