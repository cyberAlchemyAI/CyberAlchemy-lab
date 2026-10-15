#!/usr/bin/env python3
"""Freeze exact sources, execute real regression/engineering evidence, admit nothing."""
import sys,os,time,tempfile,unittest,traceback
from pathlib import Path
from run_episode import *
from test_engineering import INPUTS,INPUT_SHA
from validate import Recording

RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
HERE=Path(__file__).resolve().parent


def binding(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':byte_sha(path.read_bytes())}


def main(executable):
    started=time.perf_counter();executable=Path(executable).resolve()
    c13=read(ROOT/'implementation/lab-continuity/candidates/v1/packages/0001/generator-manifest.json')
    require(byte_sha(executable.read_bytes())==c13['native_executable_sha256'],'native executable differs')
    os.environ['W02_NATIVE_EXECUTABLE']=str(executable)
    predecessor_path=PACKAGE/'receipts/action-boundaries/0004.json';predecessor=read(predecessor_path)
    require(predecessor['result']=='PASS' and predecessor['task_complete'],'W02 predecessor incomplete')
    context=read(RUN/'context-W03-v2.json')
    files=predecessor['files']+predecessor['source_bindings']+context['source_bindings']
    own=list(HERE.glob('*.py'))+[PACKAGE/'workflows/engineering.py',HERE/'README.md']+list(INPUTS.glob('*'))
    own += [RUN/'context-W03-v2.json',RUN/'CONTEXT-W03-v2.md',predecessor_path,
        ROOT/'docs/proposals/0007-lab-integrated-schema-package/schemas/common.schema.json',
        ROOT/'docs/proposals/0006-lab-artifact-storage/schemas/artifact-package-manifest.schema.json',
        ROOT/'implementation/lab-work/candidates/v1/packages/0002/branch.snapshot',
        ROOT/'implementation/lab-runtime/v2/profile.json',
        ROOT/'authority/admissions/cyberalchemy-lab-operational-foundation/v1/instances/artifacts/project.json',
        ROOT/'authority/admissions/cyberalchemy-lab-operational-foundation/v1/instances/artifacts/product-capability.json']
    for kind in ['goal','intent','work','intent-resolution','coordination-context','implementation','agent-action','generated-output','evidence-set','work-outcome-assessment','typed-relation','project-identity']:
        row,_=carrier(kind);own += [ROOT/row['schema_path']]
    pairs=read(PAIRS)['exact_pairs']
    for row in pairs:
        if row['relation_kind_ref'] in ['relation.successor-of','relation.realizes','relation.produces','relation.evaluates','relation.member-of']:
            own.append(ROOT/row['relation_binding']['path'])
    files+= [binding(p) for p in own if p.is_file()]
    by_path={}
    for row in files:
        if row['path'] in by_path:require(row['sha256']==by_path[row['path']]['sha256'],'conflicting prerequisite binding')
        by_path[row['path']]={'path':row['path'],'sha256':row['sha256']}
    files=list(by_path.values())
    for row in files:require(byte_sha((ROOT/row['path']).read_bytes())==row['sha256'],'source/prerequisite drift '+row['path'])
    root=HERE/'receipts';root.mkdir(exist_ok=True);index=1
    while (root/f'{index:04d}.json').exists():index+=1
    directory=root/f'{index:04d}';directory.mkdir()
    frozen=directory/'manifest.json';frozen.write_bytes(encoded({'authority_effect':'none','files':files}))
    print(json.dumps({'stage':'sources-frozen','files':len(files),'output':str(directory.relative_to(ROOT))}),flush=True)
    manifest=read(INPUTS/'input-manifest.json')
    regression=run_default_regression(INPUTS/'registered_evaluator.py',manifest['output_source_sha256'],directory/'default-regression.log')
    # Record the actual log by relative path in retained public receipts.
    (directory/'default-regression.json').write_bytes(encoded({**regression,'log_path':'default-regression.log'}))
    import test_engineering
    suite=unittest.defaultTestLoader.loadTestsFromModule(test_engineering)
    with (directory/'engineering.log').open('w') as stream:
        result=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=Recording).run(suite)
    episode=None;episode_error=None
    try:
        episode=execute_episode(INPUTS,INPUT_SHA,directory/'observed',regression)
    except Exception:
        episode_error=traceback.format_exc();(directory/'episode-error.log').write_text(episode_error)
    drift=[r['path'] for r in files if byte_sha((ROOT/r['path']).read_bytes())!=r['sha256']]
    passed=(regression['result']=='PASS' and result.wasSuccessful() and result.testsRun==33
        and episode is not None and episode['assessment']['disposition']=='supported'
        and len(episode['candidates'])==7 and len(episode['relations'])==7
        and episode['review']['actual_owner_outcome'] is None and not drift)
    outputs=[binding(p) for p in directory.rglob('*') if p.is_file()]
    receipt={'schema_version':'lab-W03-engineering-suite/v1-candidate','task':'W03','authority_effect':'none',
        'result':'PASS' if passed else 'FLAG','task_complete':passed,
        'tests':regression['tests']+result.testsRun,'regression_tests':regression['tests'],'engineering_tests':result.testsRun,
        'checks':regression['checks']+result.checks,'source_drift':drift,
        'duration_seconds':time.perf_counter()-started,'files':files+outputs,'source_bindings':context['source_bindings'],
        'actual_owner_outcome':None,'canonical_effects_applied':0,
        'review_members':episode['review']['member_records'] if episode else [],
        'remaining_obligations':[] if passed else ['All selected engineering and default regression checks and actual observed episode must pass.'],
        'episode_error':episode_error,
        'claim_ceiling':'Exact isolated candidate source correction, 42 preserved default actor checks and 33 engineering checks. Proposed members remain uncommitted/unadmitted; broad APIs, production authentication, Tool cold recovery, release and human satisfaction remain downstream.'}
    path=root/f'{index:04d}.json';path.write_bytes(encoded(receipt))
    print(json.dumps({'result':receipt['result'],'tests':receipt['tests'],'task_complete':passed,'receipt':str(path.relative_to(ROOT))}),flush=True)
    return 0 if passed else 1


if __name__=='__main__':
    require(len(sys.argv)==2,'exact native executable path required')
    sys.exit(main(sys.argv[1]))
