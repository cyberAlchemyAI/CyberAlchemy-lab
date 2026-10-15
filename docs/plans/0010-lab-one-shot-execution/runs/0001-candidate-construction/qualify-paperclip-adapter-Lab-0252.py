"""Additive published Paperclip adapter proof against independently pinned API14.

Original runner3, launcher0141, package0140 and all API sources remain immutable.
Only a new /tmp metadata fixture and this driver's new receipt are written.
"""
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tarfile
import tempfile
import time
import traceback
import unittest

RUN=Path(__file__).resolve().parent; ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
CLIENT=BASE/'paperclip-runner-v3'; API=BASE/'api-integration-v14'
SOURCE='aea84d1d97c2780e8fb172b6dd4d8807f2e89892a02f0fe0e5daab97b3f0c240'
PROFILE='327d3c480168b0008597969e31e11e73f429370a226bd16370245e82ef78fb16'
RUNNER='3bf9c4284c4605c00068e0611b610cc0565bb1927c3f83b310385e43d36076c5'
PACKAGE=Path('/tmp/cal-paperclip-package-inspection-0140')
REPORT=RUN/'Paperclip-adapter-Lab-qualification-0252.json'
ARE=RUN/'ARE-Paperclip-technical-boundary-0187.json'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def path_at(name):return Path(name) if Path(name).is_absolute() else ROOT/name
def bind(path):
    path=Path(path)
    return {'path':path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path), 'sha256':sha(path.read_bytes())}
def install(name,path):
    spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
def published_guard(probe):
    """Exact published archive bytes and the actual extracted first-party files."""
    archives=[];rows=[]
    for selected in probe['archives']:
        archive=PACKAGE/selected['filename'];raw=archive.read_bytes()
        assert 'sha512-'+base64.b64encode(hashlib.sha512(raw).digest()).decode()==selected['integrity']
        name=selected['package'].split('@')[1].split('/')[1]
        destination=PACKAGE/'package' if name=='server' else PACKAGE/'package/node_modules/@paperclipai'/name
        count=0;size=0
        with tarfile.open(archive,'r:gz') as tar:
            for member in tar.getmembers():
                if not member.isfile():continue
                relative=Path(member.name);assert relative.parts[0]=='package' and '..' not in relative.parts
                path=destination.joinpath(*relative.parts[1:]);assert not path.is_symlink()
                expected=tar.extractfile(member).read();assert path.read_bytes()==expected,str(path)
                rows.append({'path':str(path),'sha256':sha(expected)});count+=1;size+=len(expected)
        archives.append({**selected,'archive_binding':bind(archive),'verified_extracted_files':count,'verified_extracted_bytes':size})
    return archives,rows

def main():
    assert not REPORT.exists(),'immutable receipt already exists'
    started=datetime.now(timezone.utc);clock=time.monotonic()
    entry_exit={};failure=None;observed=None;actual_adapter=None;owned=None;tests=None
    fixture_evidence=None;archives=None;accounting=None;full_rows=[]
    anchors=[CLIENT/'source-manifest.json',API/'source-manifest.json',API/'contract-profile.json',Path(__file__).resolve(),
        RUN/'launch-paperclip-process-0141.mjs',RUN/'qualify-paperclip-adapter-Lab-0141.py',RUN/'Paperclip-runner-qualification-0141.json',
        RUN/'Paperclip-runner-qualification-0138.json',RUN/'Paperclip-process-adapter-probe-0140.json',ARE,RUN/'authorization.json',RUN/'Paperclip-package-recovery-0251.json']
    anchor_rows=[bind(path) for path in anchors]
    try:
        assert sha((API/'source-manifest.json').read_bytes())==SOURCE
        assert sha((API/'contract-profile.json').read_bytes())==PROFILE
        assert sha((CLIENT/'source-manifest.json').read_bytes())==RUNNER
        api_manifest=json.loads((API/'source-manifest.json').read_bytes())
        entries={row['path']:row for row in api_manifest['files']}
        for filename in ('__init__.py','guard.py'):
            row=entries[(API/filename).relative_to(ROOT).as_posix()];assert bind(API/filename)==row
        install('_cal_paperclip_API14_fixture_action_0148',API)
        G=__import__('_cal_paperclip_API14_fixture_action_0148.guard',fromlist=['verify'])
        G.verify(SOURCE);entry_exit['API14_full_source_entry']='PASS'
        runner_manifest=json.loads((CLIENT/'source-manifest.json').read_bytes())
        G._verify_files(ROOT,runner_manifest['files']);entry_exit['runner3_full_source_entry']='PASS'
        probe=json.loads((RUN/'Paperclip-process-adapter-probe-0140.json').read_bytes());assert probe['result']=='PASS'
        assert json.loads((RUN/'Paperclip-runner-qualification-0141.json').read_bytes())['result']=='PASS'
        assert json.loads((RUN/'Paperclip-runner-qualification-0138.json').read_bytes())['result']=='PASS'
        assert json.loads(ARE.read_bytes())['result']['ok'] is True
        archives,published_rows=published_guard(probe)
        # Preserve every currently installed dependency byte around this episode;
        # the three original published first-party archives are independently pinned above.
        installed=[]
        for directory in (PACKAGE/'node_modules',PACKAGE/'package/node_modules'):
            for path in sorted(directory.rglob('*')):
                if path.is_symlink():
                    assert '.bin' in path.parts,'unexpected installed dependency symlink'
                    continue
                if path.is_file():installed.append(bind(path))
        unique={row['path']:row for row in [*published_rows,*installed]}
        full_rows=[unique[name] for name in sorted(unique)]
        G._verify_files(ROOT,full_rows);entry_exit['published_package_and_installed_dependency_entry']='PASS'
        accounting={'API14_full_source_count':len(api_manifest['files']),
            'API14_full_source_unique_count':len(entries),
            'API14_full_source_bytes':sum(path_at(row['path']).stat().st_size for row in api_manifest['files']),
            'runner3_full_source_count':len(runner_manifest['files']),
            'published_and_dependency_unique_count':len(full_rows),
            'published_and_dependency_bytes':sum(path_at(row['path']).stat().st_size for row in full_rows)}
        install('_cal_paperclip_runner_action_0148',CLIENT)
        T=__import__('_cal_paperclip_runner_action_0148.test_boundaries',fromlist=['*'])
        tests=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(T))
        assert tests.wasSuccessful(),'original runner refusal tests failed'
        P=__import__('_cal_paperclip_API14_fixture_action_0148.protocol',fromlist=['*'])
        F=__import__('_cal_paperclip_API14_fixture_action_0148.fixtures',fromlist=['*'])
        schemas=P.Schemas(PROFILE)
        with tempfile.TemporaryDirectory(prefix='cal-paperclip-API14-action-0148-') as temporary:
            owned=Path(temporary);owned.chmod(0o700)
            key,policy,pin=F.provision(owned,'custody-participation',principal='principal:R03-Paperclip-API14-isolated-metadata-reader');key=None
            policy_value=P.source.parse(policy.read_bytes());authority=RUN/'authorization.json'
            original_period=policy_value['session_control']['period_binding']
            policy_value.update(schema_version='lab-local-metadata-candidate-policy/v1-candidate',session_control=None,
                allowed_operations=list(P.METADATA_SUPPORTED),purpose='durable-metadata-and-exact-candidate-preparation',
                development_authorization_binding=P.binding(str(authority.relative_to(ROOT)),authority.read_bytes()),scope_control=None)
            policy_raw=P.compact(policy_value);policy.write_bytes(policy_raw);pin=P.source.sha(policy_raw)
            fixture_evidence={'principal_ref':policy_value['principal_ref'],'source_name':policy_value['source_name'],
                'allowed_operations':policy_value['allowed_operations'],'selected_operations':['lab.status','lab.status','catalog.get'],
                'expires_at':policy_value['expires_at'],'original_Source5_period_binding':original_period,
                'session_control':None,'policy_binding':{'ref':'owned-private-policy','sha256':pin},'workspace_objects':None,'workspace_journal':None}
            plan=CLIENT/'read-plan.example.json';credential=owned/'reader.pem'
            args=argparse.Namespace(api_root=str(API),source_sha256=SOURCE,profile_sha256=PROFILE,policy=str(policy),policy_sha256=pin,
                reader_key=str(credential),reader_key_sha256=sha(credential.read_bytes()),plan=str(plan),plan_sha256=bind(plan)['sha256'],timeout_seconds=900)
            command_args=['-I','-B',str(CLIENT/'runner.py')]
            for selector in ('api_root','source_sha256','profile_sha256','policy','policy_sha256','reader_key','reader_key_sha256','plan','plan_sha256','timeout_seconds'):
                command_args+=['--'+selector.replace('_','-'),str(getattr(args,selector))]
            config={'command':sys.executable,'args':command_args,'cwd':str(ROOT),'timeoutSec':960,'graceSec':5}
            config_path=owned/'adapter-config.json';config_raw=P.compact(config);config_path.write_bytes(config_raw);config_path.chmod(0o600)
            executed=subprocess.run(['/home/vlad_/.local/bin/node',str(RUN/'launch-paperclip-process-0141.mjs'),str(config_path),P.source.sha(config_raw)],
                capture_output=True,text=True,timeout=990,env={'PATH':'/home/vlad_/.local/bin:/usr/bin:/bin','NODE_ENV':'production'})
            if executed.returncode!=0:
                # Runner emits only an exception class; preserve that real safe cause.
                try:actual_adapter=json.loads(executed.stdout)
                except Exception:actual_adapter={'launcher_exit_code':executed.returncode,'launcher_error_class':'unparseable-result'}
                raise AssertionError('published adapter process failed; see actual_adapter_result')
            actual_adapter=json.loads(executed.stdout)
            assert actual_adapter['result']['exitCode']==0 and not actual_adapter['result']['timedOut']
            observed=json.loads(actual_adapter['result']['resultJson']['stdout'])
            assert observed['result']=='PASS' and [row['operation'] for row in observed['calls']]==['lab.status','lab.status','catalog.get']
            assert all(row['reply']['contract_profile_binding']==schemas.profile_binding for row in observed['calls'])
            assert observed['calls'][0]['reply']['message']['supported_operations']==list(P.SUPPORTED)
            assert len(set(P.SUPPORTED))==34
            fixture_evidence['workspace_journal']=len(list((owned/'workspace/journal').iterdir()))
            fixture_evidence['workspace_objects']=len(list((owned/'workspace/objects').iterdir()))
            assert fixture_evidence['workspace_journal']==fixture_evidence['workspace_objects']==0
            assert observed['Lab_mutations_requested']==0 and observed['Paperclip_API_called'] is False
    except Exception:
        failure=traceback.format_exc()
    finally:
        try:
            assert all(bind(path_at(row['path']))==row for row in anchor_rows),'qualification anchors changed'
            if 'G' in locals():
                G.verify(SOURCE);entry_exit['API14_full_source_exit']='PASS'
                G._verify_files(ROOT,runner_manifest['files']);entry_exit['runner3_full_source_exit']='PASS'
                if full_rows:
                    G._verify_files(ROOT,full_rows)
                    assert published_guard(probe)[0]==archives
                    entry_exit['published_package_and_installed_dependency_exit']='PASS'
        except Exception:
            failure=(failure or '')+'\nEXIT GUARD FAILURE\n'+traceback.format_exc()
    removed=owned is not None and not owned.exists()
    if failure is None and not removed:failure='owned fixture cleanup incomplete'
    value={'schema_version':'lab-published-paperclip-adapter-Lab-integration/v2-candidate','result':'PASS' if failure is None else 'FAIL',
        'started_at':started.isoformat(),'finished_at':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-clock,
        'selected_API_source_sha256':SOURCE,'selected_API_profile_sha256':PROFILE,'implemented_operations':34,
        'fixture_principal_selection':'Fresh independently provisioned metadata-only reader; original closed eight-operation metadata policy, exact three selected authenticated reads; no Agent/Session participation.',
        'fixture_evidence':fixture_evidence,'actual_episode':observed,'actual_adapter_result':actual_adapter,'actual_episode_failure':failure,
        'original_boundary_tests':None if tests is None else tests.testsRun,'boundary_failures':None if tests is None else len(tests.failures),
        'boundary_errors':None if tests is None else len(tests.errors),'full_source_guards':entry_exit,'source_accounting':accounting,
        'published_archives':archives,'published_and_installed_dependency_files':full_rows,'files':anchor_rows,
        'previous_actual_adapter_qualification_binding':bind(RUN/'Paperclip-runner-qualification-0141.json'),
        'ARE_boundary_binding':bind(ARE),'owned_fixture_removed':removed,'private_keys_exported':False,
        'Paperclip_server_started':False,'Paperclip_company_created':False,'human_pilot_complete':False,
        'authority_effect':'none','actual_owner_outcome':None,'task_complete':False,'goal_complete':False,
        'claim_ceiling':'Actual unchanged published Paperclip process adapter and independent original launcher invoke unchanged runner3 for exactly three authenticated reads through frozen34-operation API14. Six original refusal checks and full source entry/exit guards. No server/company installation, human usefulness, owner admission or full goal completion.'}
    with REPORT.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':value['result'],'report_binding':bind(REPORT),'original_boundary_tests':value['original_boundary_tests'],
        'actual_authenticated_reads':0 if observed is None else len(observed['calls']),'owned_fixture_removed':removed,'failure':failure}),flush=True)
    return 0 if value['result']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
