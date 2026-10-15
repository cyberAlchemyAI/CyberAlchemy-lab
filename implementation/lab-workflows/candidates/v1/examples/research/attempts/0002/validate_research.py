#!/usr/bin/env python3
"""Freeze current prerequisites, execute declared checks and real archived comparison."""
import os,sys,time,traceback,unittest
from pathlib import Path
from run_episode import *
from test_research import INPUTS

RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
HERE=Path(__file__).resolve().parent


def binding(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':byte_sha(p.read_bytes())}


class Recording(unittest.TextTestResult):
    def __init__(self,*a,**k):super().__init__(*a,**k);self.checks=[];self.passed=False
    def startTest(self,test):self.passed=False;super().startTest(test)
    def addSuccess(self,test):self.passed=True;super().addSuccess(test)
    def stopTest(self,test):
        self.checks.append({'test':test.id(),'result':'PASS' if self.passed else 'FLAG'})
        print(json.dumps(self.checks[-1]),flush=True);super().stopTest(test)


def main():
    started=time.perf_counter();context=read(RUN/'context-W04.json')
    predecessor_paths=[PACKAGE/'examples/engineering/receipts/0002.json',BRIDGE/'receipts/C06/0001.json']
    files=context['source_bindings'][:]
    for p in predecessor_paths:
        predecessor=read(p);require(predecessor['result']=='PASS','W04 prerequisite has not passed')
        files += predecessor['files']+predecessor.get('source_bindings',[])+[binding(p)]
    own=list(HERE.glob('*.py'))+[PACKAGE/'workflows/research.py',HERE/'README.md',RUN/'context-W04.json',RUN/'CONTEXT-W04.md',METHOD_SCHEMA]
    own += list(INPUTS.glob('*'))+[BRIDGE/'tests/test_replay.py',PACKAGE/'schemas/workflow-run.schema.json',
        ROOT/'docs/proposals/0007-lab-integrated-schema-package/schemas/common.schema.json',
        ROOT/'docs/proposals/0006-lab-artifact-storage/schemas/artifact-package-manifest.schema.json',
        ROOT/'implementation/lab-bootstrap/candidates/v1/packages/0004/method/example.json']
    selection=read(INPUTS/'selection.json')
    for row in selection['records']:
        if row['kind']!='method':own.append(ROOT/carrier(row['kind'])[0]['schema_path'])
    for semantic_kind in ['experiment-run','research-run','observation','measurement-result','evidence-set','finding','evaluation','implementation','agent-action','generated-output','typed-relation','work']:
        own += [ROOT/carrier(semantic_kind)[0]['schema_path']]
        template_path=ROOT/f'authority/artifact-types/{semantic_kind}/v1/fixtures/valid/record.json'
        if template_path.exists():own.append(template_path)
    for row in read(PAIRS)['exact_pairs']:
        if row['relation_kind_ref'] in ['relation.tests-hypothesis','relation.evaluates','relation.realizes','relation.uses-method','relation.derives-from','relation.engages-inquiry','relation.member-of','relation.evidence-bears-on','relation.produces','relation.successor-of']:
            own.append(ROOT/row['relation_binding']['path'])
    own += [ROOT/f'authority/artifact-types/{k}/v1/fixtures/valid/record.json' for k in ['research-inquiry','hypothesis','experiment-design','measurement-method']]
    files += [binding(p) for p in own if p.is_file()]
    selected={}
    for row in files:
        if row['path'] in selected:require(row['sha256']==selected[row['path']]['sha256'],'conflicting W04 source bindings')
        selected[row['path']]={'path':row['path'],'sha256':row['sha256']}
    files=list(selected.values())
    for row in files:require(byte_sha((ROOT/row['path']).read_bytes())==row['sha256'],'W04 prerequisite/source changed: '+row['path'])
    require(len(files)>140,'W04 complete source closure missing')
    directory=HERE/'receipts';directory.mkdir(exist_ok=True);index=1
    while (directory/f'{index:04d}.json').exists():index+=1
    output=directory/f'{index:04d}';output.mkdir()
    frozen=output/'manifest.json';frozen.write_bytes(encoded({'authority_effect':'none','files':files}))
    print(json.dumps({'stage':'sources-frozen','files':len(files),'output':str(output.relative_to(ROOT))}),flush=True)
    import test_research
    suite=unittest.defaultTestLoader.loadTestsFromModule(test_research);count=suite.countTestCases()
    with (output/'research-checks.log').open('w') as stream:mechanism=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=Recording).run(suite)
    sys.path.insert(0,str(BRIDGE/'tests'));import test_replay
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(test_replay.ReplayTests)
    with (output/'full-replay-regression.log').open('w') as stream:regression=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=Recording).run(suite)
    (output/'full-replay-regression.json').write_bytes(encoded({'result':'PASS' if regression.wasSuccessful() else 'FLAG',
        'tests':regression.testsRun,'checks':regression.checks,'observations':test_replay.ReplayTests.performance,
        'cache_enabled':False,'actual_owner_outcome':None}))
    episode=None;error=None
    print(json.dumps({'stage':'real-archived-comparison','samples':3,'calls':6,'cache_enabled':False}),flush=True)
    try:episode=execute_episode(INPUTS,byte_sha((INPUTS/'selection.json').read_bytes()),output/'observed')
    except Exception:error=traceback.format_exc();(output/'episode-error.log').write_text(error)
    drift=[r['path'] for r in files if byte_sha((ROOT/r['path']).read_bytes())!=r['sha256']]
    passed=(mechanism.wasSuccessful() and mechanism.testsRun==count==40 and regression.wasSuccessful() and regression.testsRun==14
        and episode is not None and len(episode['candidates'])==11 and len(episode['relations'])==22
        and episode['receipt']['posture']=='completed' and not drift)
    # Every real comparison must reconstruct the exact signed state; otherwise the example is incomplete.
    if episode is not None:passed=passed and episode['assessment']['labels']==['parity']*3
    receipt={'schema_version':'lab-W04-research-suite/v1-candidate','task':'W04','authority_effect':'none',
        'result':'PASS' if passed else 'FLAG','task_complete':passed,'tests':mechanism.testsRun+regression.testsRun,
        'research_tests':mechanism.testsRun,'regression_tests':regression.testsRun,'checks':mechanism.checks+regression.checks,
        'duration_seconds':time.perf_counter()-started,'source_drift':drift,
        'files':files+[binding(p) for p in output.rglob('*') if p.is_file()],
        'source_bindings':context['source_bindings'],'actual_owner_outcome':None,'canonical_effects_applied':0,
        'hypothesis_assessment':episode['assessment'] if episode else None,
        'review_members':episode['review']['selected_candidate_members'] if episode else [],'episode_error':error,
        'remaining_obligations':[] if passed else ['All declared mechanism/regression checks and actual six replay observations must complete with exact verification parity.'],
        'claim_ceiling':'Candidate research mechanism and three finite original signed archive comparisons only. Negative/inconclusive hypothesis outcomes remain valid findings; no performance acceptance, cache optimization, entropy/timing collapse, canonical admission, production authority or human acceptance.'}
    path=directory/f'{index:04d}.json';path.write_bytes(encoded(receipt))
    print(json.dumps({'result':receipt['result'],'task_complete':passed,'tests':receipt['tests'],'receipt':str(path.relative_to(ROOT)),
        'hypothesis_disposition':episode['assessment']['disposition'] if episode else None}),flush=True)
    return 0 if passed else 1


if __name__=='__main__':sys.exit(main())
