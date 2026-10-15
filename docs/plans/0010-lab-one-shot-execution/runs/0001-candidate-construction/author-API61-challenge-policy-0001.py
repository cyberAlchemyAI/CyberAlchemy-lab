"""Correct the exact challenge-policy operation list in an immutable successor."""
import ast
import argparse
import hashlib
import json
from pathlib import Path
import shutil
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';OLD=BASE/'api-v60';API=BASE/'api-v61'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def replace(p,a,b):
    value=p.read_text();assert value.count(a)==1;p.write_text(value.replace(a,b,1))
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--resume-owned-partial',action='store_true');args=parser.parse_args()
    if args.resume_owned_partial:
        assert API.is_dir() and (BASE/'lesson-host-composition-v11').is_dir() and not (API/'source-manifest.json').exists()
        assert (RUN/'API60-challenge-policy-static-diagnosis-0001.json').is_file()
    else:assert not API.exists() and not (BASE/'lesson-host-composition-v11').exists()
    schema=json.loads((OLD/'authentication.schema.json').read_bytes())
    branch=next(b for b in schema['oneOf'] if b.get('properties',{}).get('schema_version',{}).get('const')=='lab-local-challenge-candidate-policy/v1-candidate')
    before=branch['properties']['allowed_operations']['const'];assert before[-1]=='proposal.review'
    diagnosis={'schema_version':'lab-authoring-contract-diagnosis/v1-candidate','source_binding':bind(OLD/'source-manifest.json'),
        'schema_binding':bind(OLD/'authentication.schema.json'),'actual_selected_policy_operations':before,
        'required_challenge_policy_operations':before[:-1]+['challenge.submit'],
        'finding':'The new policy branch retained the review policy exact operation-list constant. This is a static contract mismatch; no actual authenticated challenge runtime verdict is established.',
        'runtime_verification_executed':False,'actual_owner_outcome':None,'authority_effect':'none','goal_complete':False}
    if not args.resume_owned_partial:
        with (RUN/'API60-challenge-policy-static-diagnosis-0001.json').open('x') as stream:json.dump(diagnosis,stream,indent=2,sort_keys=True);stream.write('\n')
    ignore=shutil.ignore_patterns('receipts','__pycache__','source-manifest.json','contract-profile.json')
    if not args.resume_owned_partial:
        shutil.copytree(OLD,API,ignore=ignore)
        shutil.copytree(BASE/'lesson-host-composition-v10',BASE/'lesson-host-composition-v11',ignore=ignore)
        replace(BASE/'lesson-host-composition-v11/host.py','api-v60/service.py','api-v61/service.py')
        replace(API/'lesson_selection.py','lesson-host-composition-v10','lesson-host-composition-v11')
    p=API/'authentication.schema.json';schema=json.loads(p.read_bytes())
    branch=next(b for b in schema['oneOf'] if b.get('properties',{}).get('schema_version',{}).get('const')=='lab-local-challenge-candidate-policy/v1-candidate')
    branch['properties']['allowed_operations']['const']=before[:-1]+['challenge.submit'];p.write_text(json.dumps(schema,indent=2,sort_keys=True)+'\n')
    replace(API/'service.py',"'handler_binding':binding(str((HERE/'package_import.py').relative_to(ROOT))",
        "'handler_binding':binding(str((HERE/'challenge_submission.py').relative_to(ROOT)),(HERE/'challenge_submission.py').read_bytes()) if call['operation']=='challenge.submit' else binding(str((HERE/'package_import.py').relative_to(ROOT))")
    freeze=(RUN/'freeze-API60-challenge-submit-0001.py').read_text()
    freeze=freeze.replace("OLD=BASE/'api-v59';API=BASE/'api-v60'","OLD=BASE/'api-v60';API=BASE/'api-v61'")
    freeze=freeze.replace("guard.verify('186837d9d16fc3369aff32862fb98f42d189b33e314e427798dcb5556449783a')", "guard.verify('b1b9e42dd0912339ef4de23fc314733507bf9042a3c03a3f4f28a23d3dae301e')")
    freeze=freeze.replace('assert len(inherited)==305','assert len(inherited)==312').replace("BASE/'lesson-host-composition-v10'","BASE/'lesson-host-composition-v11'")
    freeze=freeze.replace("RUN/'author-API60-challenge-submit-0001.py',", "RUN/'author-API61-challenge-policy-0001.py',RUN/'API60-challenge-policy-static-diagnosis-0001.json',")
    freeze=freeze.replace("profile['implemented_operations'].insert(profile['implemented_operations'].index('files.materialize'),'challenge.submit')", "assert profile['implemented_operations'][12]=='challenge.submit'")
    freeze=freeze.replace("'unchanged_inherited_method_count':305","'unchanged_inherited_method_count':312").replace("'unchanged_inherited_methods':305","'unchanged_inherited_methods':312")
    with (RUN/'freeze-API61-challenge-policy-0001.py').open('x') as stream:stream.write(freeze)
    print('Authored API61 correction; static API60 mismatch preserved; all312 prior methods retained.',flush=True)
if __name__=='__main__':main()
