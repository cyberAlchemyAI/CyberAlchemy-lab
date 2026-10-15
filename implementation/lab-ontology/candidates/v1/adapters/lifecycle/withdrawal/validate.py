"""Freeze and verify the complete O02 candidate lifecycle acceptance package."""
import os
import subprocess
import traceback

from run import emit
from source import *
from validate_lifecycle import native_delta, process

RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
RECEIPTS=PACKAGE/'receipts/O02'
NATIVE=PACKAGE/'adapters/native'


def next_episode(family):
    directory=RECEIPTS/family;directory.mkdir(exist_ok=True)
    number=max([int(p.name) for p in directory.iterdir() if p.is_dir() and p.name.isdigit()]+[0])+1
    return directory/f'{number:04d}'


def main(executable):
    started=time.perf_counter();executable=Path(executable).resolve();exe_sha=sha(executable.read_bytes())
    context=parse((RUN/'context-O02-v3.json').read_bytes())
    predecessor=parse((RECEIPTS/'0003.json').read_bytes())
    require(predecessor['result']=='PASS' and predecessor['task_complete'] is False, 'rich partial predecessor required')
    require(predecessor['native_executable_binding']=={'path':str(executable),'sha256':exe_sha}, 'reviewed executable binding differs')
    files={}
    for row in predecessor['files']+predecessor['source_bindings']+context['source_bindings']:
        b={k:row[k] for k in ('path','sha256')};original(b)
        require(b['path'] not in files or files[b['path']]==b, 'conflicting predecessor source binding');files[b['path']]=b
    for directory in (PACKAGE/'adapters',RECEIPTS):
        for path in directory.rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts:
                b=bind(path);files[b['path']]=b
    b=bind(RUN/'context-O02-v3.json');files[b['path']]=b
    frozen=list(files.values())
    for b in frozen:original(b)
    number=max([int(p.stem) for p in RECEIPTS.iterdir() if p.stem.isdigit()]+[0])+1
    output=RECEIPTS/f'{number:04d}';output.mkdir()
    emit(output/'manifest.json',{'authority_effect':'none','actual_owner_outcome':None,'files':frozen,
        'native_executable_binding':{'path':str(executable),'sha256':exe_sha},'scope':'combined O02 candidate acceptance'})
    errors=[];checks=[];rich=None;withdrawal=None;rich_cold=withdrawal_cold=None;delta=None
    try:
        delta=native_delta();emit(output/'native-delta.json',delta)
        process(['cargo','test','--offline','--manifest-path',str(NATIVE/'Cargo.toml'),
            '--target-dir',str(executable.parents[1])],output,'native-regression')
        raw=(output/'native-regression.stdout').read_text()
        require('test result: ok. 20 passed;' in raw and 'test result: ok. 3 passed;' in raw, '23 inherited native regressions required')
        entries=[{'suite':'native-regression','test':line.split(' ... ')[0].removeprefix('test '),'result':'PASS'}
            for line in raw.splitlines() if line.startswith('test ') and line.endswith(' ... ok')]
        require(len(entries)==23, 'native regression check inventory differs');checks.extend(entries)
        env=dict(os.environ,O02_NATIVE_EXECUTABLE=str(executable),O02_NATIVE_SHA256=exe_sha)
        for label,directory,pattern,count in (
            ('representation-guards',PACKAGE/'adapters','test_represented_subjects.py',33),
            ('rich-lifecycle-guards',LIFECYCLE,'test_lifecycle.py',26)):
            process([sys.executable,'-m','unittest','discover','-s',str(directory),'-p',pattern,'-v'],output,label,env=env)
            raw=(output/(label+'.stderr')).read_text()
            require(f'Ran {count} tests' in raw and raw.rstrip().endswith('OK'), 'complete preserved guard suite required')
            entries=[{'suite':label,'test':line.split(' ... ')[0],'result':'PASS'} for line in raw.splitlines() if line.endswith(' ... ok')]
            require(len(entries)==count,'guard inventory differs');checks.extend(entries)
        rich=next_episode('lifecycle-episodes')
        process([sys.executable,str(LIFECYCLE/'run_lifecycle.py'),str(executable),exe_sha,str(rich)],output,'actual-rich-lifecycle')
        warm=parse((rich/'removed-native-view.json').read_bytes())
        archive=rich/'native.snapshot';witness=rich/'mapping-witnesses.json'
        process([sys.executable,str(LIFECYCLE/'cold_lifecycle.py'),str(executable),exe_sha,str(archive),sha(archive.read_bytes()),
            str(witness),sha(witness.read_bytes()),object_sha(warm)],output,'cold-rich-lifecycle')
        rich_cold=parse((output/'cold-rich-lifecycle.stdout').read_bytes())
        require(rich_cold['result']=='PASS', 'cold rich lifecycle parity failed')
        withdrawal=next_episode('withdrawal-episodes')
        process([sys.executable,str(HERE/'run.py'),str(executable),exe_sha,str(withdrawal)],output,'actual-source-withdrawal')
        actual=parse((withdrawal/'result.json').read_bytes())
        require(actual['result']=='PASS' and actual['actual_source_withdrawal_observed'] is True
            and actual['fixture_private_key_removed'] is True and actual['owned_source_root_removed'] is True
            and actual['owned_native_root_removed'] is True, 'actual withdrawal/cleanup incomplete')
        witness=withdrawal/'witnesses.json'
        process([sys.executable,str(HERE/'cold.py'),str(executable),exe_sha,str(witness),sha(witness.read_bytes())],output,'cold-source-withdrawal')
        withdrawal_cold=parse((output/'cold-source-withdrawal.stdout').read_bytes())
        require(withdrawal_cold['result']=='PASS' and withdrawal_cold['actual_source_withdrawal_verified'] is True,
            'cold independently signed source withdrawal failed')
        env['O02_WITHDRAWAL_EPISODE']=str(withdrawal)
        process([sys.executable,'-m','unittest','discover','-s',str(HERE),'-p','test_withdrawal.py','-v'],
            output,'source-withdrawal-guards',env=env)
        raw=(output/'source-withdrawal-guards.stderr').read_text()
        require('Ran 29 tests' in raw and raw.rstrip().endswith('OK'), 'all 29 source-withdrawal guards required')
        entries=[{'suite':'source-withdrawal-guards','test':line.split(' ... ')[0],'result':'PASS'}
            for line in raw.splitlines() if line.endswith(' ... ok')]
        require(len(entries)==29,'withdrawal guard inventory differs');checks.extend(entries)
    except Exception as error:errors.append({'error':str(error),'traceback':traceback.format_exc()})
    drift=[b['path'] for b in frozen if not (ROOT/b['path']).is_file() or sha((ROOT/b['path']).read_bytes())!=b['sha256']]
    passed=bool(not errors and not drift and len(checks)==111 and rich_cold and withdrawal_cold
        and sha(executable.read_bytes())==exe_sha)
    outputs=[bind(p) for p in output.rglob('*') if p.is_file()]
    for episode in (rich,withdrawal):
        if episode and episode.exists():outputs.extend(bind(p) for p in episode.rglob('*') if p.is_file())
    receipt={'schema_version':'lab-O02-complete-candidate-lifecycle-proof/v1-candidate','task':'O02',
        'authority_effect':'none','actual_owner_outcome':None,'result':'PASS' if passed else 'FLAG',
        'task_complete':passed,'tests':len(checks),'checks':checks,'duration_seconds':time.perf_counter()-started,
        'files':frozen+outputs,'source_bindings':context['source_bindings'],'source_drift':drift,'errors':errors,
        'native_delta':delta,'native_executable_binding':{'path':str(executable),'sha256':exe_sha},
        'rich_lifecycle_episode':bind(rich/'result.json') if rich and (rich/'result.json').exists() else None,
        'source_withdrawal_episode':bind(withdrawal/'result.json') if withdrawal and (withdrawal/'result.json').exists() else None,
        'cold_rich_lifecycle':rich_cold,'cold_source_withdrawal':withdrawal_cold,
        'actual_source_withdrawal_observed':bool(passed),'actual_local_fixture_effects':2 if passed else None,
        'repository_admissions_applied':0,'canonical_ontology_admissions_applied':0,
        'signed_transaction_mapping_implemented':False,
        'verified_obligation_ids':['P1','P2','P3','P4','P5','P6','P7'] if passed else [],
        'remaining_obligations':[] if passed else ['Complete exact combined O02 lifecycle verification; preserve failures.'],
        'downstream_obligations':['O05/R03: implement signed Project/Product represented endpoint transaction coupling; rerun W07 completion proof.',
            'S02/R08: bind exact native extension, profiles, confidence vocabulary, translation/source scope and implementation members for actual owner review.',
            'O06 and later admitted application: ontology event adoption and operational authority remain separate from candidate parity.'],
        'claim_ceiling':'Complete original O02 candidate construction criteria only: exact source and native joins, rich node/relation translation, independent challenge/retire/remove/actual signed source withdrawal, full original-byte cold parity and bounded authority. No canonical ontology/source admission, confirmed global Edge, owner outcome or generic signed transaction coupling.'}
    path=output.with_suffix('.json');emit(path,receipt)
    print(json.dumps({'result':receipt['result'],'task_complete':passed,'tests':len(checks),
        'receipt':path.relative_to(ROOT).as_posix(),'duration_seconds':receipt['duration_seconds'],
        'source_drift':drift,'errors':[e['error'] for e in errors]}))
    return 0 if passed else 1


if __name__=='__main__':sys.exit(main(sys.argv[1]))
