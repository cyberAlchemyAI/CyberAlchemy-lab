#!/usr/bin/env python3
"""Freeze W06, run fresh regressions, signed real episode and cold context proof."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE));sys.path.insert(0,str(HERE.parent))
from adapter import *
sys.path.insert(0,str(PACKAGE/'examples/learning-loop'))
import run_episode
from failures.validate import Recording

RUN = ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'


def binding(path):
    return {'path':path.relative_to(ROOT).as_posix(),'sha256':byte_sha(path.read_bytes())}


def main():
    started = time.perf_counter()
    native = Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/cal-c08-native-build/debug/lab-context-native-reader').resolve()
    native_manifest = run_episode.continuity.MANIFEST
    native_sha = parse(native_manifest.read_bytes())['native_executable_sha256']
    require(native.is_file() and byte_sha(native.read_bytes()) == native_sha,'independent native executable differs')
    os.environ['W02_NATIVE_EXECUTABLE'] = str(native)
    context = parse((RUN/'context-W06.json').read_bytes())
    files = list(context['source_bindings'])
    for path in [W05,ROOT/'implementation/lab-continuity/candidates/v1/receipts/C13/0002.json',
        ROOT/'implementation/lab-context/candidates/v1/receipts/C08/0003.json']:
        receipt = parse(path.read_bytes());require(receipt['result']=='PASS' and receipt['task_complete'],'W06 dependency incomplete')
        files += receipt['files'] + receipt.get('source_bindings',[]) + [binding(path)]
    own = list(HERE.glob('*.py')) + [HERE/'README.md',PACKAGE/'examples/learning-loop/run_episode.py',
        RUN/'context-W06.json',RUN/'CONTEXT-W06.md',native_manifest]
    files += [binding(p) for p in own]
    selected = {}
    for row in files:
        require(row['path'] not in selected or selected[row['path']]['sha256'] == row['sha256'],'conflicting W06 source pins')
        require(byte_sha((ROOT/row['path']).read_bytes()) == row['sha256'],'W06 source drift: '+row['path'])
        selected[row['path']] = {'path':row['path'],'sha256':row['sha256']}
    files = list(selected.values())
    receipts = HERE/'receipts';receipts.mkdir(exist_ok=True)
    number = 1
    while (receipts/f'{number:04d}').exists() or (receipts/f'{number:04d}.json').exists(): number += 1
    output = receipts/f'{number:04d}';output.mkdir()
    (output/'manifest.json').write_bytes(encoded({'authority_effect':'none','files':files}))
    print(json.dumps({'stage':'sources-frozen','sources':len(files),'output':output.relative_to(ROOT).as_posix()}),flush=True)
    import test_learning
    from failures import test_services
    sys.path.insert(0,str(PACKAGE/'receipts/action-boundaries'))
    import test_boundaries
    results = []
    for label, module in [('W06',test_learning),('W05-regression',test_services),('W02-regression',test_boundaries)]:
        with (output/(label+'.log')).open('w') as stream:
            results.append(unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=Recording).run(unittest.defaultTestLoader.loadTestsFromModule(module)))
    (output/'actual-context-regression.json').write_bytes(encoded({'actual_context':test_boundaries.ActualContextTests.observed,
        'Tool_episode':test_boundaries.DispatchTests.observed,'actual_owner_outcome':None}))
    episode = cold = None;error = None
    print(json.dumps({'stage':'real-signed-lesson-and-later-application'}),flush=True)
    try:
        episode = run_episode.perform(output/'observed',native)
        index = output/'observed/episode-index.json'
        print(json.dumps({'stage':'cold-original-replay-and-new-Agent-context'}),flush=True)
        p = subprocess.run([sys.executable,str(PACKAGE/'examples/learning-loop/run_episode.py'),'--cold',str(index),
            byte_sha(index.read_bytes()),str(native)],capture_output=True,timeout=300)
        (output/'cold-stdout.json').write_bytes(p.stdout);(output/'cold-stderr.log').write_bytes(p.stderr)
        require(p.returncode == 0,'actual lesson cold reconstruction failed')
        cold = parse(p.stdout)
    except Exception:
        error = traceback.format_exc();(output/'episode-error.log').write_text(error)
    drift = [r['path'] for r in files if byte_sha((ROOT/r['path']).read_bytes()) != r['sha256']]
    native_current = byte_sha(native.read_bytes()) == native_sha
    passed = all(r.wasSuccessful() for r in results) and [r.testsRun for r in results] == [47,52,42]
    passed = passed and episode is not None and cold is not None and cold['result']=='PASS' and not drift and native_current
    passed = passed and episode['actual_later_application'] and episode['lesson_from_committed_Project_State']['effective_state']=='local-admitted-current'
    passed = passed and episode['outcome_disposition']=='supported-for-this-controlled-case' and test_boundaries.ActualContextTests.observed is not None
    members = []
    if episode:
        for name,ref in episode['implementation_refs'].items():
            row = next(r for r in episode['records'] if r['version_ref']==ref)
            members.append({'identity_ref':ref.split('@')[0],'version_ref':ref,'kind':'implementation','target':binding(output/'observed'/row['path']),
                'owner_outcome':None,'authority_effect':'none','scope':'exact candidate operational-learning adapter and original evidence'})
        row = next(r for r in episode['records'] if r['version_ref']==episode['lesson_ref'])
        members.append({'identity_ref':episode['lesson_ref'].split('@')[0],'version_ref':episode['lesson_ref'],'kind':'operational-lesson',
            'target':binding(output/'observed'/row['path']),'owner_outcome':None,'authority_effect':'none',
            'scope':'exact scoped candidate lesson; local fixture persistence grants no canonical admission'})
    receipt = {'schema_version':'lab-W06-operational-learning-suite/v1-candidate','task':'W06','authority_effect':'none',
        'result':'PASS' if passed else 'FLAG','task_complete':bool(passed),'tests':sum(r.testsRun for r in results),
        'W06_tests':results[0].testsRun,'W05_regression_tests':results[1].testsRun,'W02_regression_tests':results[2].testsRun,
        'checks':[c for r in results for c in r.checks],'duration_seconds':time.perf_counter()-started,'source_drift':drift,
        'files':files+[binding(p) for p in output.rglob('*') if p.is_file()],'source_bindings':context['source_bindings'],
        'cold_verification':cold,'episode_error':error,'review_members':members,
        'native_executable_binding':{'path':str(native),'sha256':native_sha,'current_after_suite':native_current,'independent_source_manifest':binding(native_manifest)},
        'acceptance_checks':[{'obligation':r['id'],'text':r['text'],'result':'PASS' if passed else 'FLAG'} for r in context['obligations']],
        'actual_owner_outcome':None,'canonical_effects_applied':0,'lesson_promoted':False,'general_benefit_established':False,
        'remaining_obligations':[] if passed else ['All 47 guards, 94 regressions and real signed episode/cold reconstruction must pass.'],
        'claim_ceiling':'Candidate exact Lesson drafting, review/selection, actual owned later application and bounded outcome only. Unit reviews/process/timeouts are synthetic. Real signed fixture persistence is distinct from canonical admission. No confirmed general effectiveness, Product benefit, native Artifact mapping, generic API completeness or actual R08 outcome.'}
    path = receipts/f'{number:04d}.json';path.write_bytes(encoded(receipt))
    print(json.dumps({'result':receipt['result'],'task_complete':bool(passed),'tests':receipt['tests'],'receipt':path.relative_to(ROOT).as_posix()}),flush=True)
    return 0 if passed else 1


if __name__ == '__main__': sys.exit(main())
