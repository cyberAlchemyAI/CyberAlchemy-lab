"""Actual closure transactions and negative cases in isolated fixture stores."""
from pathlib import Path
import concurrent.futures
import copy
import json
import os
import uuid
from closure_api import HERE,ROOT,SCOPE,ROLES,ANSWERS,Ledger,binding,encoded,identity,read,durable,implementation_bindings


def fixtures(parent):
    parent.mkdir(parents=True,exist_ok=False)
    audit={'schema':'relational.closure-predecessor-audit/v4','result':'pass',
           'original_counts':{'tasks':35,'working_units':40,'edges':56,'accepted':33},
           'successor_units':19,'extension_final_witnesses':19,'source_bindings':[SCOPE['base_plan']]}
    durable(parent/'audit.json',encoded(audit))
    challenges={}
    for gate in ROLES:
        artifacts={}
        for role in ROLES[gate]:
            path=parent/(gate+'-'+role+'.'+('md' if role in ['packet','recommendation'] else 'json'))
            if role=='audit':path=parent/'audit.json'
            else:durable(path,b'Fixture review material\n' if path.suffix=='.md' else encoded({'fixture':True,'role':role}))
            artifacts[role]=binding(path)
        manifest={'schema':'relational.gate-review-manifest/v4','gate':gate,'scope':SCOPE['scope_ids'][gate],
                  'base_plan':SCOPE['base_plan'],'artifacts':artifacts,'source_audit':binding(parent/'audit.json'),
                  'implementation_bindings':implementation_bindings(),'authority_effect':'none','application_authorized':False}
        path=parent/(gate+'-manifest.json');durable(path,encoded(manifest));challenges[gate]=binding(path)
    return challenges


def feedback(gate,challenges):
    manifest=read(ROOT/challenges[gate]['path'])
    return {'schema':'relational.human-gate-review/v4','gate':gate,'scope':SCOPE['scope_ids'][gate],
            'review_manifest':challenges[gate],'reviewed_artifacts':manifest['artifacts'],
            'answers':{k:'accepted' for k in ANSWERS[gate]},
            'provenance':{'source':'observed-direct-user-response','thread_id':'fixture-only',
                          'message_anchor':'synthetic-control','quote':'Synthetic fixture; not an actual human approval.',
                          'captured_at':'2026-10-10T00:00:00Z'},'capture_kind':'fixture','authority_effect':'none','application_authorized':False}


def run(stage):
    root=HERE/'execution'/stage/('controls-'+uuid.uuid4().hex)
    challenges=fixtures(root/'materials')
    controls=[]
    def test(name,condition):
        assert condition,name
        controls.append({'name':name,'result':'pass'})
    def refuse(name,fn):
        try:fn()
        except (ValueError,KeyError,FileNotFoundError,StopIteration):test(name,True)
        else:raise AssertionError('unexpected acceptance '+name)
    def store(name):return Ledger(root/name,fixture=True,challenges=challenges)
    ledger=store('main')
    test('empty-current-view-is-33-of-35',ledger.resolve()['counts']['accepted']==33)
    f=feedback('R06',challenges)
    refuse('unobserved-response-refuses',lambda:ledger.record_feedback(encoded(f)))
    for name,mutate in [
        ('empty-reviewed-artifacts',lambda x:x.update(reviewed_artifacts={})),
        ('missing-mandatory-pilot',lambda x:x['reviewed_artifacts'].pop('pilot')),
        ('wrong-scope',lambda x:x.update(scope=SCOPE['scope_ids']['G4'])),
        ('unknown-feedback-field',lambda x:x.update(accepted=True)),
        ('wrong-manifest-identity',lambda x:x['review_manifest'].update(sha256='0'*64)),
        ('packet-substitution',lambda x:x['reviewed_artifacts'].update(packet=x['reviewed_artifacts']['matrix'])),
        ('actual-capture-in-fixture-refuses',lambda x:x.update(capture_kind='actual')),
        ('empty-response-provenance',lambda x:x['provenance'].update(quote='')),
        ('deployment-flag-refuses',lambda x:x.update(application_authorized=True))]:
        bad=copy.deepcopy(f);mutate(bad)
        refuse(name,lambda bad=bad:ledger.record_feedback(encoded(bad),observed_direct_response=True))
    refuse('duplicate-json-key',lambda:ledger.record_feedback(encoded(f).replace(b'"gate": "R06"',b'"gate": "G4", "gate": "R06"'),observed_direct_response=True))
    refuse('nonfinite-json',lambda:ledger.record_feedback(b'{"v":NaN}',observed_direct_response=True))
    bad=copy.deepcopy(f);bad['schema']='relational.actual-human-feedback/v3'
    refuse('P11-feedback-schema-does-not-transfer',lambda:ledger.record_feedback(encoded(bad),observed_direct_response=True))
    for answer in ['revisions','undecided']:
        bad=copy.deepcopy(f);bad['answers']['meanings']=answer
        ref=ledger.record_feedback(encoded(bad),observed_direct_response=True)
        refuse(answer+'-does-not-accept-gate',lambda ref=ref:ledger.accept('R06',ref,expected_head=None))
    f4=feedback('G4',challenges);g4ref=ledger.record_feedback(encoded(f4),observed_direct_response=True)
    refuse('G4-before-R06',lambda:ledger.accept('G4',g4ref,expected_head=None))
    test('all-refusals-preserve-empty-log',ledger.resolve()['generation']==0)
    r6=ledger.record_feedback(encoded(f),observed_direct_response=True)
    test('capture-is-idempotent',ledger.record_feedback(encoded(f),observed_direct_response=True)==r6)
    accepted=ledger.accept('R06',r6,expected_head=None)
    test('R06-original-criteria-and-outputs-accepted',accepted['gate']=='R06' and ledger.resolve()['counts']['accepted']==34)
    test('R06-no-fresh-event',not accepted['fresh_event'])
    refuse('stale-null-head',lambda:ledger.accept('G4',g4ref,expected_head=None))
    head=ledger.resolve()['overlay_head'];r4=ledger.accept('G4',g4ref,expected_head=head)
    view=ledger.recover()
    test('all-35-original-tasks-resolve-accepted',view['counts']=={'tasks':35,'working_units':40,'edges':56,'accepted':35})
    test('recovery-never-creates-event',not view['fresh_event'])
    test('recovery-idempotent',ledger.recover()==view)
    test('original-plan-still-33-accepted',sum(t['status']=='accepted' for t in read(ROOT/SCOPE['base_plan']['path'])['tasks'])==33)
    refuse('duplicate-G4-refuses',lambda:ledger.accept('G4',g4ref,expected_head=view['overlay_head']))
    receipt=read(ROOT/r4['receipt']['path']);bad=copy.deepcopy(receipt);bad['criteria'].pop()
    refuse('omitted-original-criterion',lambda:ledger.verify_receipt('G4',bad))
    bad=copy.deepcopy(receipt);bad['source_bindings']=bad['source_bindings'][:1]
    refuse('omitted-source-binding',lambda:ledger.verify_receipt('G4',bad))
    bad=copy.deepcopy(receipt);bad['artifacts'].pop('bounded-use-recommendation.md')
    refuse('omitted-original-deliverable',lambda:ledger.verify_receipt('G4',bad))
    # Tamper an exact reviewed file in an isolated source clone after successful
    # capture, then confirm it cannot be used for new acceptance or recovery.
    stale_ch=fixtures(root/'stale-materials');stale=Ledger(root/'stale',fixture=True,challenges=stale_ch)
    sf=stale.record_feedback(encoded(feedback('R06',stale_ch)),observed_direct_response=True)
    packet=ROOT/read(ROOT/stale_ch['R06']['path'])['artifacts']['packet']['path'];packet.write_text('changed fixture packet')
    refuse('changed-packet-after-capture',lambda:stale.accept('R06',sf,expected_head=None))
    test('stale-packet-preserves-state',stale.resolve()['generation']==0)
    if stage=='h04':
        race=store('race');rr=race.record_feedback(encoded(f),observed_direct_response=True)
        def writer():
            try:race.accept('R06',rr,expected_head=None);return 'accepted'
            except ValueError:return 'conflict'
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(lambda _:writer(),range(2)))
        test('two-real-writers-one-winner',sorted(results)==['accepted','conflict'])
        test('race-one-generation',race.resolve()['generation']==1)
        for point,expected in [('before-publication',0),('after-publication',1)]:
            crash=store(point);ref=crash.record_feedback(encoded(f),observed_direct_response=True)
            pid=os.fork()
            if pid==0:
                crash.accept('R06',ref,expected_head=None,crash_at=point);os._exit(99)
            _,status=os.waitpid(pid,0)
            test(point+'-actual-child-crash',os.WEXITSTATUS(status)==(91 if expected==0 else 92))
            recovered=crash.recover()
            test(point+'-recovers-exact-generation',recovered['generation']==expected)
            test(point+'-no-fresh-event',not recovered['fresh_event'])
            test(point+'-recovery-repeat-safe',crash.recover()==recovered)
        # A committed log remains authoritative if the materialized view is lost.
        (ledger.directory/'current-original-task-view.json').unlink()
        test('lost-view-regenerated-from-validated-log',ledger.recover()==view)
    report={'result':'pass','stage':stage,'fixture_only':True,'controls':controls,
            'fixture_root':str(root.relative_to(ROOT)),'actual_human_approval':False,'authority_effect':'none'}
    (HERE/'execution'/stage/'closure-controls.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['h02','h04']);args=parser.parse_args()
    result=run(args.stage);print(json.dumps({'result':result['result'],'stage':args.stage,'controls':len(result['controls'])},indent=2))
