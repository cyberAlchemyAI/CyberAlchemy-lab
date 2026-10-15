#!/usr/bin/env python3
"""One domain per fresh process; preserve original evidence in its owned scope."""
from pathlib import Path
import os
import sys
import time
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from integration_support import *


def axes(progress,outcome=None):
    return {'workflow_progress':progress,'carrier_lifecycle':'candidate','admission':'candidate-unadmitted',
        'commitment':None,'outcome_satisfaction':outcome,'action_permission':'separate-explicit-host-development-grant'}


def actors(output,selected):
    dest=Path(output)/'actors';dest.mkdir()
    result=[]
    for selected_row in selected:
        value=selected_row['original_record'];raw=encoded(value)
        require(byte_sha(raw)==selected_row['sha256'],'actor original re-encoding differs')
        p=dest/(byte_sha(selected_row['version_ref'].encode())[:20]+'.json')
        with p.open('xb') as stream:stream.write(raw)
        result.append(row(p,selected_row['version_ref'],value['kind'],'actor'))
    return result


def add_inputs(rows,directory,selection):
    for r in selection['records']:
        rows.append(row(directory/r['path'],r['version_ref'],r['kind'],'input'))


def output_rows(directory,members):
    paths={byte_sha(p.read_bytes()):p for p in Path(directory).glob('*.json')}
    result=[]
    for r in members:
        sha=r.get('record_sha256',r.get('sha256'))
        require(sha in paths,'selected domain output original absent')
        result.append(row(paths[sha],r['version_ref'],r['kind'],'output'))
    return result


def prepare_case(domain,output,*,retained=False):
    """Catalog originals; retained inputs are for structural unit checks only."""
    output=Path(output)
    base={'schema_version':'lab-W07-domain-case/v1-candidate','domain':domain,'case_id':'protocol:W07:'+domain+':'+byte_sha(str(output).encode())[:16],
        'authority_effect':'none','actual_owner_outcome':None,'canonical_effects_applied':0,'records':[],'original_evidence':[]}
    evaluator=PACKAGE/'examples/engineering/packages/0004/registered_evaluator.py'
    facts={'actual_execution':True,'host_evaluator_sha256':byte_sha(evaluator.read_bytes()),'retained_structural_unit_source':retained}
    if domain in {'engineering','research'}:
        source=PACKAGE/('examples/engineering/packages/0004' if domain=='engineering' else 'examples/research/packages/0007')
        selection=parse((source/('input-manifest.json' if domain=='engineering' else 'selection.json')).read_bytes())
        add_inputs(base['records'],source,selection)
        body=output/'workflow' if domain=='engineering' else output
        review=parse((body/'review-effects.json').read_bytes())
        base['records']+=output_rows(body,review.get('member_records',review.get('selected_candidate_members')))
        if domain=='engineering':
            for kind,name in [('project-identity','project'),('product-capability','product-capability')]:
                p=ROOT/'authority/admissions/cyberalchemy-lab-operational-foundation/v1/instances/artifacts'/(name+'.json')
                v=parse(p.read_bytes());ref=contracts.ident(v)+'@'+(v['version'] if 'version' in v else 'foundation.1')
                base['records'].append(row(p,ref,kind,'input'))
            base['generated_source']=binding(body/'tool/registered_evaluator.py')
            assessment=parse((output/'assessment.json').read_bytes())
            facts.update(assessment_disposition=assessment['disposition'],default_regression_tests=42,
                implementation_sha256=byte_sha((body/'tool/registered_evaluator.py').read_bytes()))
            base['status_axes']=axes('assessed','supported')
        else:
            base.update(observations=binding(output/'observed.json'),procedure=binding(source/'procedure.json'),assessment=binding(output/'assessment.json'))
            facts.update(cache_enabled=False,Product_benefit_established=False,
                hypothesis_disposition=parse((output/'assessment.json').read_bytes())['disposition'])
            base['status_axes']=axes('evaluated')
        selected=parse((output/'selected-actor-records.json').read_bytes())
        # Actor originals already exist in selected evidence; emit explicit rows for fresh catalogs.
        if retained:
            # Retained catalog may read those original compound bytes without mutating history.
            base['actor_evidence']=binding(output/'selected-actor-records.json')
        else:base['records']+=actors(output,selected)
        base['workflow_run']=binding(output/'workflow-run.json')
        base['transitions']=binding(output/'transitions.json')
        base['action_receipt']=binding(output/'action-receipt.json')
        base['original_evidence']=[binding(p) for p in output.rglob('*') if p.is_file() and p.suffix not in {'.py'}]
    else:
        index_path=output/'episode-index.json';index=parse(index_path.read_bytes())
        for r in index['records']:
            base['records'].append(row(output/r['path'],r['version_ref'],r['kind'],r['role']))
        base['episode_index']=binding(index_path)
        base['original_evidence']=[binding(output/r['path']) for r in index.get('original_evidence',index.get('blobs',[]))]
        if domain=='failure':
            facts.update(old_builder_sha256=byte_sha((PACKAGE/'examples/research/attempts/0001/build_inputs.py').read_bytes()),
                production_incident_claimed=False,owner_outcome=None)
            base['status_axes']=axes('resolved-for-controlled-revision')
        else:
            facts.update(old_builder_sha256=byte_sha((PACKAGE/'examples/research/attempts/0001/build_inputs.py').read_bytes()),
                lesson_source_W05_receipt_sha256=UPSTREAM['W05'][1],general_effectiveness_established=False)
            base['status_axes']=axes('later-application-assessed','supported-for-this-controlled-case')
            base['signed_archive']=binding(output/'branch.snapshot')
            base['original_evidence'] += [binding(output/p) for p in ['branch.snapshot','context-before.json','context-later.json','native-pins.json']]
    base['facts']=facts
    return base


def load_retained_cases():
    return [prepare_case(domain,PACKAGE/path,retained=True) for domain,path in [
        ('engineering','examples/engineering/receipts/0002/observed'),('research','examples/research/receipts/0002/observed'),
        ('failure','failures/receipts/0004/observed'),('learning','learning/receipts/0002/observed')]]


def recording_type():
    class Recording(unittest.TextTestResult):
        def __init__(self,*a,**kw):super().__init__(*a,**kw);self.checks=[];self.passed=False
        def startTest(self,t):self.passed=False;super().startTest(t)
        def addSuccess(self,t):self.passed=True;super().addSuccess(t)
        def stopTest(self,t):self.checks.append({'test':t.id(),'result':'PASS' if self.passed else 'FLAG'});super().stopTest(t)
    return Recording


def run_units(domain,output):
    output=Path(output);output.mkdir()
    if domain=='engineering':
        sys.path.insert(0,str(PACKAGE/'examples/engineering'));import test_engineering as module;case=module.EngineeringTests
    elif domain=='research':
        sys.path.insert(0,str(PACKAGE/'examples/research'));import test_research as module;case=module.ResearchTests
    elif domain=='failure':
        sys.path.insert(0,str(PACKAGE));from failures import test_services as module;case=module.ServicesTests
    elif domain=='learning':
        sys.path.insert(0,str(PACKAGE/'learning'));import test_learning as module;case=None
    else:
        sys.path.insert(0,str(ROOT/'implementation/lab-runtime/candidates/repeatable-operation/tests'));import test_replay as module;case=module.ReplayTests
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(case) if case else unittest.defaultTestLoader.loadTestsFromModule(module)
    with (output/'checks.log').open('w') as stream:
        result=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=recording_type()).run(suite)
    value={'domain':domain,'result':'PASS' if result.wasSuccessful() else 'FLAG','tests':result.testsRun,'checks':result.checks,
        'unit_fixture_claim_ceiling':'Declared unit/negative fixtures only; actual retained replay/context tests retain their original scope.'}
    emit(output/'result.json',value);return value


def execute(domain,output,native):
    output=Path(output)
    require(not output.exists(),'fresh owned scenario required')
    if domain=='engineering':
        sys.path.insert(0,str(PACKAGE/'examples/engineering'));import run_episode as episode
        source=PACKAGE/'examples/engineering/packages/0004';selection=parse((source/'input-manifest.json').read_bytes())
        output.parent.mkdir(exist_ok=True)
        log=output.parent/'engineering-default-regression.log'
        regression=episode.run_default_regression(source/'registered_evaluator.py',selection['output_source_sha256'],log)
        require(regression['result']=='PASS' and regression['tests']==42,'fresh default regression failed')
        emit(output.parent/'engineering-default-regression.json',{**regression,'log_path':log.relative_to(ROOT).as_posix()})
        episode.execute_episode(source,byte_sha((source/'input-manifest.json').read_bytes()),output,regression)
    elif domain=='research':
        sys.path.insert(0,str(PACKAGE/'examples/research'));import run_episode as episode
        source=PACKAGE/'examples/research/packages/0007'
        episode.execute_episode(source,byte_sha((source/'selection.json').read_bytes()),output)
    elif domain=='failure':
        sys.path.insert(0,str(PACKAGE));from failures import episode
        e,_,_,_=episode.prepare_episode(output)
        e.host.session.close()
    else:
        sys.path.insert(0,str(PACKAGE/'examples/learning-loop'));import run_episode as episode
        episode.perform(output,native)
    case=prepare_case(domain,output)
    emit(output/'case.json',case)
    return {'domain':domain,'result':'PASS','case':binding(output/'case.json')}


def cold_join(path,pin,native):
    raw=Path(path).read_bytes();require(byte_sha(raw)==pin,'independent integration index differs')
    index=parse(raw);cases=[parse(bound(r)) for r in index['cases']]
    result=audit_join(cases)
    learning=next(c for c in cases if c['domain']=='learning')
    sys.path.insert(0,str(PACKAGE/'examples/learning-loop'));import run_episode
    episode_path=ROOT/learning['episode_index']['path']
    actual=run_episode.cold(episode_path,learning['episode_index']['sha256'],native)
    return {'result':'PASS','domain_cases_checked':len(cases),'typed_connections_checked':sum(len(c['closure']['typed_connections']) for c in result['cases']),
        'signed_lesson_cold_context':actual,'actual_owner_outcome':None,'global_merge_performed':False,'effects_reexecuted':0}


if __name__=='__main__':
    started=time.perf_counter();mode=sys.argv[1];native=Path(sys.argv[-1]).resolve()
    manifest=ROOT/'implementation/lab-continuity/candidates/v1/packages/0001/generator-manifest.json'
    require(byte_sha(native.read_bytes())==parse(manifest.read_bytes())['native_executable_sha256'],'independent native executable differs')
    os.environ['W02_NATIVE_EXECUTABLE']=str(native)
    if mode=='--unit':value=run_units(sys.argv[2],Path(sys.argv[3]))
    elif mode=='--episode':value=execute(sys.argv[2],Path(sys.argv[3]),native)
    elif mode=='--cold':value=cold_join(Path(sys.argv[2]),sys.argv[3],native)
    else:require(False,'closed worker mode required')
    value['duration_seconds']=time.perf_counter()-started
    sys.stdout.buffer.write(encoded(value))
