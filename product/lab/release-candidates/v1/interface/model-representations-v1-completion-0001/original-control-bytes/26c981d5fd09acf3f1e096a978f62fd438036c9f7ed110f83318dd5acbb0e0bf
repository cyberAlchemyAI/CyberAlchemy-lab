#!/usr/bin/env python3
"""Fresh combined source-bound rich lifecycle proof. Full O02 stays partial."""
import os
import subprocess
import time
import traceback

from translation import *

RUN = ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
RECEIPTS = PACKAGE/'receipts/O02'
NATIVE = PACKAGE/'adapters/native'


def emit(path,value):
    with path.open('xb') as stream:stream.write((json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode())


def native_delta():
    selected = parse((NATIVE/'upstream-bindings.json').read_bytes())
    for row in selected['files']:
        raw = original({k:row[k] for k in ['path','sha256']})
        candidate = (ROOT/row['candidate_path']).read_bytes()
        if row['path'].endswith('/src/lib.rs'):
            left='fn validate_semantic_state(';right='fn validate_governance_state('
            before=raw.decode();after=candidate.decode()
            require(before.split(left)[0]==after.split(left)[0] and before.split(right)[1]==after.split(right)[1],
                'candidate native delta escaped selected validator region')
        else:require(raw==candidate,'inherited native source/fixture bytes changed')
    return {'result':'PASS','original_files_checked':len(selected['files']),
        'only_selected_validator_region_changed':True,'inherited_test_sources_unchanged':True}


def process(args,output,label,env=None,timeout=180):
    with (output/(label+'.stdout')).open('wb') as stdout,(output/(label+'.stderr')).open('wb') as stderr:
        child=subprocess.run(args,cwd=ROOT,env=env,stdout=stdout,stderr=stderr,timeout=timeout)
    require(child.returncode==0,label+' failed; exact original process logs retained')
    return child


def main(executable):
    started=time.perf_counter();executable=Path(executable).resolve();exe_sha=sha(executable.read_bytes())
    context=parse((RUN/'context-O02-v2.json').read_bytes())
    selected={r['path']:{k:r[k] for k in ['path','sha256']} for r in context['source_bindings']}
    predecessor=parse((RECEIPTS/'0002.json').read_bytes())
    require(predecessor['result']=='PASS' and predecessor['task_complete'] is False,'previous partial scope missing')
    for r in predecessor['files']+predecessor['source_bindings']:
        b={k:r[k] for k in ['path','sha256']};original(b)
        require(b['path'] not in selected or selected[b['path']]==b,'conflicting source pins');selected[b['path']]=b
    for path in (PACKAGE/'adapters').rglob('*'):
        if path.is_file() and '__pycache__' not in path.parts:
            selected[bind(path)['path']]=bind(path)
    for path in RECEIPTS.rglob('*'):
        if path.is_file() and '__pycache__' not in path.parts:
            selected[bind(path)['path']]=bind(path)
    selected[bind(RUN/'context-O02-v2.json')['path']]=bind(RUN/'context-O02-v2.json')
    files=list(selected.values())
    for b in files:original(b)
    number=max([int(p.stem) for p in RECEIPTS.iterdir() if p.stem.isdigit()]+[0])+1
    output=RECEIPTS/f'{number:04d}';output.mkdir()
    emit(output/'manifest.json',{'authority_effect':'none','files':files,'native_executable_sha256':exe_sha,
        'native_executable_path':str(executable),'task_complete':False})
    errors=[];checks=[];cold=None;episode=None;delta=None
    try:
        delta=native_delta();emit(output/'native-delta.json',delta)
        process(['cargo','test','--offline','--manifest-path',str(NATIVE/'Cargo.toml'),
            '--target-dir',str(executable.parents[1])],output,'native-regression')
        native_text=(output/'native-regression.stdout').read_text()
        require('test result: ok. 20 passed;' in native_text and 'test result: ok. 3 passed;' in native_text,'all 23 inherited native checks required')
        native_checks=[{'test':line.split(' ... ')[0].removeprefix('test '),'result':'PASS','suite':'native-regression'}
            for line in native_text.splitlines() if line.startswith('test ') and line.endswith(' ... ok')]
        require(len(native_checks)==23,'native check inventory differs');checks.extend(native_checks)
        env=dict(os.environ,O02_NATIVE_EXECUTABLE=str(executable),O02_NATIVE_SHA256=exe_sha)
        for label,directory,pattern,expected in [
            ('representation-guards',PACKAGE/'adapters','test_represented_subjects.py',33),
            ('lifecycle-guards',PACKAGE/'adapters/lifecycle','test_lifecycle.py',26)]:
            process([sys.executable,'-m','unittest','discover','-s',str(directory),'-p',pattern,'-v'],output,label,env=env)
            raw=(output/(label+'.stderr')).read_text()
            require(f'Ran {expected} tests' in raw and raw.rstrip().endswith('OK'),'complete guard suite required')
            entries=[{'test':line.split(' ... ')[0],'result':'PASS','suite':label} for line in raw.splitlines() if line.endswith(' ... ok')]
            require(len(entries)==expected,'guard inventory differs');checks.extend(entries)
        # Fresh owned ontology effects are constructed after package freezing.
        episodes=RECEIPTS/'lifecycle-episodes'
        episode_number=max([int(p.name) for p in episodes.iterdir() if p.is_dir() and p.name.isdigit()]+[0])+1
        episode=episodes/f'{episode_number:04d}'
        process([sys.executable,str(LIFECYCLE/'run_lifecycle.py'),str(executable),exe_sha,str(episode)],output,'actual-lifecycle')
        actual=parse((episode/'result.json').read_bytes());require(actual['result']=='PASS','actual lifecycle incomplete')
        warm=parse((episode/'removed-native-view.json').read_bytes())
        archive=episode/'native.snapshot';witnesses=episode/'mapping-witnesses.json'
        process([sys.executable,str(LIFECYCLE/'cold_lifecycle.py'),str(executable),exe_sha,str(archive),sha(archive.read_bytes()),
            str(witnesses),sha(witnesses.read_bytes()),object_sha(warm)],output,'cold-lifecycle')
        cold=parse((output/'cold-lifecycle.stdout').read_bytes());require(cold['result']=='PASS','cold reconstruction incomplete')
    except Exception as error:errors.append({'error':str(error),'traceback':traceback.format_exc()})
    drift=[b['path'] for b in files if sha((ROOT/b['path']).read_bytes())!=b['sha256']]
    passed=bool(not errors and not drift and len(checks)==82 and cold and sha(executable.read_bytes())==exe_sha)
    outputs=[bind(p) for p in output.rglob('*') if p.is_file()]
    if episode and episode.exists():outputs += [bind(p) for p in episode.rglob('*') if p.is_file()]
    receipt={'schema_version':'lab-O02-rich-native-lifecycle-proof/v1-candidate','task':'O02','authority_effect':'none',
        'result':'PASS' if passed else 'FLAG','task_complete':False,'tests':len(checks),'checks':checks,
        'duration_seconds':time.perf_counter()-started,'files':files+outputs,'source_bindings':context['source_bindings'],
        'source_drift':drift,'errors':errors,'native_delta':delta,'cold_verification':cold,
        'native_executable_binding':{'path':str(executable),'sha256':exe_sha},
        'actual_episode_binding':bind(episode/'result.json') if episode and (episode/'result.json').exists() else None,
        'actual_owner_outcome':None,'canonical_ontology_admissions_applied':0,'source_effects_applied':0,
        'actual_source_withdrawal_observed':False,'signed_transaction_mapping_implemented':False,
        'verified_obligation_ids':['P1','P2','P3','P4','P6','P7'] if passed else [],
        'remaining_obligations':[
            'Implement and observe an actual independently signed source withdrawal; verify source eligibility/governance changes without automatic ontology retire/remove or semantic-byte mutation.',
            'Bind exact candidate native/profile/translation/confidence and governance members for S02/R08; O05/R03 prove actual signed transaction endpoint coupling; rerun W07 completion proof.'],
        'claim_ceiling':'Fresh exact rich native adapter package, actual signed Work source selector, three source-backed nodes/one candidate relation, four challenge revisions with semantic bytes unchanged, independent retire/reactivate/remove and cold full replay. Original reducers/runtimes unchanged. Actual source withdrawal and full O02 completion remain unproven; no ontology adoption, source admission, confirmed global edge, owner outcome or signed transaction mapping.'}
    path=output.with_suffix('.json');emit(path,receipt)
    print(json.dumps({'result':receipt['result'],'task_complete':False,'tests':len(checks),'receipt':str(path.relative_to(ROOT)),
        'source_drift':drift,'errors':[e['error'] for e in errors],'cold_verification':cold}))
    return 0 if passed else 1


if __name__=='__main__':sys.exit(main(Path(sys.argv[1])))
