"""Actual pinned stdio reads plus refusal tests; no human/Paperclip pilot claim."""
import argparse
import ast
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import traceback
import unittest

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';CLIENT=BASE/'paperclip-runner-v3';API=BASE/'api-v96'
SOURCE='a5c61899e2ec5bd07d098475842848846bdd42d18b82e16d879f835361f44048'
PROFILE='451726c90fdeeff92c2b1f6351698f8bf9bfa4722c9fc395dd0ad36f70461e99'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def install(name,path):
    spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
def main():
    report=RUN/'Paperclip-runner-qualification-0137.json';assert not report.exists()
    selected=CLIENT/'source-manifest.json';manifest=json.loads(selected.read_bytes())
    for row in manifest['files']:assert bind(ROOT/row['path'])==row,row['path']
    install('_cal_paperclip_runner_0137',CLIENT)
    R=__import__('_cal_paperclip_runner_0137.runner',fromlist=['*']);T=__import__('_cal_paperclip_runner_0137.test_boundaries',fromlist=['*'])
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(T))
    install('_cal_paperclip_API96_fixture_0134',API)
    P=__import__('_cal_paperclip_API96_fixture_0134.protocol',fromlist=['*']);F=__import__('_cal_paperclip_API96_fixture_0134.fixtures',fromlist=['*'])
    schemas=P.Schemas(PROFILE);owned=None;observed=None;failure=None
    try:
        with tempfile.TemporaryDirectory(prefix='cal-paperclip-runner-actual-') as temporary:
            owned=Path(temporary);owned.chmod(0o700)
            key,policy,pin=F.provision(owned,'custody-participation',principal=P.source.custody_delivery().records.PRINCIPAL);key=None
            plan=CLIENT/'read-plan.example.json';credential=owned/'reader.pem'
            args=argparse.Namespace(api_root=str(API),source_sha256=SOURCE,profile_sha256=PROFILE,policy=str(policy),policy_sha256=pin,
                reader_key=str(credential),reader_key_sha256=hashlib.sha256(credential.read_bytes()).hexdigest(),
                plan=str(plan),plan_sha256=bind(plan)['sha256'],timeout_seconds=900)
            observed=R.run(args)
            assert observed['result']=='PASS' and len(observed['calls'])==3
            assert all(row['operation'] in ('lab.status','catalog.get') for row in observed['calls'])
            assert not list((owned/'workspace/journal').iterdir()) and not list((owned/'workspace/objects').iterdir())
            assert observed['Lab_mutations_requested']==0 and observed['Paperclip_API_called'] is False
    except Exception:failure=traceback.format_exc()
    for row in manifest['files']:assert bind(ROOT/row['path'])==row,row['path']
    value={'schema_version':'lab-paperclip-runner-qualification/v1-candidate',
        'result':'PASS' if result.wasSuccessful() and failure is None else 'FAIL',
        'fixture_principal_selection':'Exact original current Source5 reader Principal; prior generic fixture-reader policy was correctly refused before authentication.',
        'boundary_tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'actual_episode':observed,
        'actual_episode_failure':failure,'owned_fixture_removed':owned is not None and not owned.exists(),
        'private_keys_exported':False,'Paperclip_server_started':False,'human_pilot_complete':False,
        'files':[bind(p) for p in [selected,API/'source-manifest.json',API/'contract-profile.json',Path(__file__).resolve()]],
        'authority_effect':'none','actual_owner_outcome':None,'task_complete':False,'goal_complete':False,
        'claim_ceiling':'Actual local candidate nonce-authenticated reads and isolated client boundary tests only. No running Paperclip compatibility or human usefulness qualification.'}
    with report.open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'result':value['result'],'fixture_principal_selection':'Exact original current Source5 reader Principal; prior generic fixture-reader policy was correctly refused before authentication.',
        'boundary_tests':result.testsRun,'failure':failure,'report_binding':bind(report)}),flush=True)
    return 0 if value['result']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
