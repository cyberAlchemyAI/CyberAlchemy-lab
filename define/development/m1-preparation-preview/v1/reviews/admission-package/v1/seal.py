#!/usr/bin/env python3
"""Seal local review bytes once; verify the sealed bytes without applying effects."""
import argparse, hashlib, json, re
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[6]

def record(p):
    raw=p.read_bytes();return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--create',action='store_true');args=parser.parse_args()
    seal=OUT/'package-manifest.json'
    if args.create:
        if seal.exists():raise SystemExit('Refuse to replace an existing seal.')
        from verify import main as verify
        report=verify();saved=json.loads((OUT/'verification.json').read_text())
        if report!=saved:raise SystemExit('Saved verification does not match fresh checks.')
        missing=[]
        for p in OUT.rglob('*.md'):
            for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
                if '://' not in target and not (p.parent/target.split('#')[0]).exists():missing.append((str(p),target))
        if missing:raise SystemExit('Broken documentation links: '+str(missing))
        excluded={'package-manifest.json','routing-boundaries.json','final-currentness.json'}
        files=[record(p) for p in sorted(OUT.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name not in excluded]
        obj={'schema_version':'cal.define-complete-admission-review-package/v1','authority_effect':'none','status':'complete conditional review preparation; authority effects unselected; operational qualification outstanding','files':files,'input_manifest':record(OUT/'input-bindings.json'),'fresh_accepted_package':record(ROOT/'define/development/m1-preparation-preview/v1/reviews/consolidated-model/v2/formal-assurance/v1/complete-package-manifest.json'),'selected_meanings':6,'new_profile_contract_proposals':2,'binding_revision_proposals':1,'preparation_checks_passed':report['checks_passed'],'negative_cases_rejected':report['negative_cases_rejected'],'actual_admission_ready':False,'actual_admissions':0,'actual_profile_adoptions':0,'application':False,'current_pointer_changed':False,'exclusions':['this manifest itself','routing-boundaries.json','final-currentness.json','__pycache__','mutable parent navigation/progress','private/live operator state']}
        with seal.open('x') as f:f.write(json.dumps(obj,indent=2)+'\n')
    manifest=json.loads(seal.read_text())
    bad=[i['path'] for i in manifest['files'] if record(ROOT/i['path'])!=i]
    if bad:raise SystemExit('Seal mismatches: '+str(bad))
    # Also re-read every exact external input, without accepting recapture.
    inputs=json.loads((OUT/'input-bindings.json').read_text())['bindings']
    stale=[i['path'] for i in inputs if record(ROOT/i['path'])!=i]
    if stale:raise SystemExit('Stale external inputs: '+str(stale))
    print(json.dumps({'result':'PASS','package_manifest':record(seal),'sealed_files':len(manifest['files']),'exact_external_inputs':len(inputs),'mismatches':0,'actual_admissions':0}))

if __name__=='__main__':main()
