"""Actual original S01 package-local Method catalog, isolated and unadmitted."""
import argparse
import base64
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import build_runtime as B

PACKAGE=B.ROOT/'implementation/lab-bootstrap/candidates/v1'
STAGE=PACKAGE/'packages/0004'
LOCK=B.ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/final-api-regression-0173-0190.execution.lock'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--api-directory',required=True)
    parser.add_argument('--source-sha256',required=True);parser.add_argument('--profile-sha256',required=True)
    parser.add_argument('--output-prefix',required=True);parser.add_argument('--historical-inputs',required=True);parser.add_argument('--historical-inputs-sha256',required=True);args=parser.parse_args()
    prefix=Path(args.output_prefix).resolve();api=Path(args.api_directory).resolve()
    B.need(prefix.parent==B.HERE and all(not Path(str(prefix)+s).exists() for s in ('.json','.snapshot','.log')), 'exclusive owned namespace proof outputs required')
    B.need(api.parent==B.BASE,'actual API family required')
    inherited=os.environ.get('S02_INHERITED_SCOPE_FD');fd=int(inherited) if inherited else os.open(LOCK,os.O_RDWR|os.O_NOFOLLOW);B.need(os.fstat(fd).st_ino==LOCK.stat().st_ino,'actual shared scope descriptor differs');started=datetime.now(timezone.utc).isoformat()
    failure=None;entry=False;exit_guard=False;child=None;archive_binding=None;witness=None;policy=None;outcome=None;owned_root=None
    try:
        if inherited is None:fcntl.flock(fd,fcntl.LOCK_SH)
        guard=B.module('_original_method_namespace_guard',api/'guard.py');source=B.exact(api/'source-manifest.json',args.source_sha256);guard._verify_files(B.ROOT,source['files'])
        B.exact(api/'contract-profile.json',args.profile_sha256);entry=True
        rows={r['path']:r['sha256'] for r in source['files']}
        historical=B.exact(Path(args.historical_inputs),args.historical_inputs_sha256)
        B.need(historical['authority_effect']=='none' and historical['actual_owner_outcome'] is None and historical['caller_binding']==B.bind(Path(__file__)), 'independent historical selection/caller differs')
        receipt=B.exact(B.ROOT/historical['original_receipt_binding']['path'],historical['original_receipt_binding']['sha256'])
        expected={r['path']:r['sha256'] for r in receipt['files']+receipt['source_bindings']}
        B.need(historical['files']==[{'path':p,'sha256':sha} for p,sha in sorted(expected.items())], 'complete original S01 closure required')
        for row in historical['files']+historical['system_runtime_files']:B.need(B.bind(B.ROOT/row['path'])==row, 'original historical S01/runtime input changed: '+row['path'])
        for p in (PACKAGE/'bootstrap.py',STAGE/'selection.json',STAGE/'method/artifact.json',STAGE/'method/schema.json',STAGE/'method/mechanics.json'):
            row=B.bind(p);B.need(expected.get(row['path'])==row['sha256'],'namespace input outside independently pinned historical source')
        sys.path.insert(0,str(PACKAGE));import bootstrap as original
        B.need(Path(original.__file__).resolve()==PACKAGE/'bootstrap.py','wrong original S01 composer origin')
        selection=original.select(B.ROOT,**B.load(STAGE/'selection.json'))
        snapshot,catalog=original.package_materials(B.ROOT,selection)
        contract=catalog['contracts'][original.METHOD_TYPE]
        B.need(contract['lifecycle_state']=='candidate-unadmitted' and contract['admission_decision_ref'] is None,'catalog silently admits Method')
        witness={'composer_binding':B.bind(PACKAGE/'bootstrap.py'),'package_selection_binding':B.bind(STAGE/'selection.json'),
            'original_descriptor_binding':B.bind(STAGE/'method/artifact.json'),
            'original_schema_binding':B.bind(STAGE/'method/schema.json'),'original_mechanics_binding':B.bind(STAGE/'method/mechanics.json'),
            'package_prefix':selection.policy['capture_config']['path'].rsplit('/',1)[0]+'/',
            'package_local_schema_name':contract['schema_path'],'catalog_digest':catalog['digest'],
            'candidate_method_contract':contract,'original_source_profile_sha256':snapshot['source_profile_sha256'],
            'original_source_snapshot_digest':snapshot['snapshot_digest'],
            'registered_item_selector':'#/properties/registered_types/items','candidate_contracts':len(catalog['contracts']),
            'source_subjects':len(catalog['source_subjects']),'candidate_subjects':len(catalog['candidate_subjects'])}
        with tempfile.TemporaryDirectory(prefix='cal-S02-method-original-catalog-0254-') as temporary:
            owned_root=Path(temporary);private=original.Ed25519PrivateKey.generate();key=owned_root/'rehearsal-only.pem'
            key.write_bytes(private.private_bytes(original.serialization.Encoding.PEM,original.serialization.PrivateFormat.PKCS8,original.serialization.NoEncryption()));key.chmod(0o600)
            public=private.public_key().public_bytes(original.serialization.Encoding.Raw,original.serialization.PublicFormat.Raw).hex()
            policy=original.RehearsalPolicy('fixture:S02:method-catalog-only',public,'S02-method-original-catalog-0254',
                str(owned_root/'catalog-branch'),'scope:S01:isolated-fixture',(datetime.now(timezone.utc)+timedelta(minutes=15)).isoformat())
            prepared=original.prepare(selection,policy);response=original.sign(prepared,policy,key)
            outcome=original.apply(selection,prepared,response,policy);pins=original.CatalogPins(**outcome['pins'])
            replay=original.replay(policy.destination,pins,policy)
            B.need(replay['catalog']==catalog and replay['records']=={v:t['record'] for v,t in catalog['candidate_subjects'].items()} and all(t['effective_state']=='candidate-unadmitted' for t in catalog['candidate_subjects'].values()),'isolated records lost candidate posture')
            controls=owned_root/'cold-controls.json';controls.write_bytes(original.encoded({'pins':asdict(pins),'policy':policy.core()}))
            code="import sys;sys.path.insert(0,sys.argv[1]);from bootstrap import *;c=load(sys.argv[2]);r=replay(c['policy']['destination'],CatalogPins(**c['pins']),RehearsalPolicy(**c['policy']));print(digest(r['records']))"
            child_run=subprocess.run([sys.executable,'-B','-c',code,str(PACKAGE),str(controls)],capture_output=True,text=True,timeout=180)
            child={'argv':[sys.executable,'-B','-c',code,str(PACKAGE),str(controls)],'returncode':child_run.returncode,'stdout':child_run.stdout,'stderr':child_run.stderr}
            B.need(child_run.returncode==0 and child_run.stdout.strip()==original.digest(replay['records']),'original cold catalog replay failed')
            B.need(original.apply(selection,prepared,response,policy)['idempotent'] is True,'original catalog retry differs')
            files={p.relative_to(Path(policy.destination)).as_posix():B.read(p) for p in Path(policy.destination).rglob('*') if p.is_file()}
            B.need(set(files)=={'plan.json','snapshot.json','catalog.json','records.json','rehearsal-response.json','HEAD.json'},'archive includes an unselected key or state file')
            archive={'schema_version':'lab-original-S01-candidate-catalog-retention/v1-candidate',
                'policy':policy.core(),'pins':asdict(pins),'original_package_selection_binding':B.bind(STAGE/'selection.json'),
                'files':{name:{'sha256':B.sha(raw),'base64_original_bytes':base64.b64encode(raw).decode()} for name,raw in sorted(files.items())},
                'private_keys_exported':False,'Session_memory_rehydrated':False,'authority_effect':'none','actual_owner_outcome':None}
            B.emit(Path(str(prefix)+'.snapshot'),archive);archive_binding=B.bind(Path(str(prefix)+'.snapshot'))
        B.need(owned_root is not None and not owned_root.exists(),'owned fixture key/branch cleanup failed')
        guard._verify_files(B.ROOT,source['files']);B.exact(api/'contract-profile.json',args.profile_sha256)
        B.exact(Path(args.historical_inputs),args.historical_inputs_sha256)
        for row in historical['files']+historical['system_runtime_files']:B.need(B.bind(B.ROOT/row['path'])==row,'historical S01/runtime exit input changed')
        exit_guard=True
    except Exception as exc:failure={'type':type(exc).__name__,'message':str(exc)}
    finally:
        if inherited is None:fcntl.flock(fd,fcntl.LOCK_UN)
        os.close(fd)
    good=failure is None and entry and exit_guard and child is not None and child['returncode']==0
    B.emit(Path(str(prefix)+'.log'),{'cold_subprocess':child,'failure':failure})
    report={'schema_version':'lab-original-method-native-namespace-rehearsal/v1-candidate','result':'PASS-CANDIDATE-CATALOG' if good else 'FAIL',
        'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'caller_binding':B.bind(Path(__file__)),
        'API_source_binding':B.bind(api/'source-manifest.json'),'API_profile_binding':B.bind(api/'contract-profile.json'),
        'original_API_source_bytes_entry_guard':entry,'original_API_source_bytes_exit_guard':exit_guard,'API14_R02_environment_guard_in_worker':False,'namespace_witness':witness,
        'catalog_policy':policy.core() if policy else None,'actual_isolated_apply':outcome,'retained_candidate_archive_binding':archive_binding,
        'cold_original_subprocess':child,'owned_root_removed':owned_root is not None and not owned_root.exists(),'failure':failure,
        'fixture_only':True,'original_descriptor_schema_mechanics_unchanged':True,'historical_inputs_binding':B.bind(Path(args.historical_inputs)),'historical_inputs_selected_by_API14':False,'schema_namespace_translation_to_O_prepare_implemented':False,
        'source8_projection_modified':False,'actual_native_Store_Method_registration_ready':False,
        'candidate_native_catalog_initialized':outcome is not None,'canonical_admissions':0,'canonical_registry_mutations':0,
        'actual_owner_outcome':None,'human_outcome':None,'runtime_activations':0,'authority_effect':'none',
        'selected_363_member_closure_qualified':False,'release_ready':False,'task_complete':False,'goal_complete':False}
    B.emit(Path(str(prefix)+'.json'),report)
    print(json.dumps({'result':report['result'],'report_binding':B.bind(Path(str(prefix)+'.json')),'failure':failure}),flush=True)
    return 0 if good else 1

if __name__=='__main__':raise SystemExit(main())
