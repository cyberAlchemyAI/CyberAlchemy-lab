"""Close exact candidate correction evidence without claiming full R03 completion."""
import re
import time
from episode import *

ATTEMPT=HERE/'receipts/attempts/0004'
CONTEXT=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/context-R03-corrections.json'


def run():
    started=time.perf_counter();checks=[];files={}
    def check(name,value):
        require(value,name);checks.append({'test':name,'result':'PASS'})
    def capture(path):
        b=bind(path);original(b)
        require(b['path'] not in files or files[b['path']]==b['sha256'],'conflicting proof closure')
        files[b['path']]=b['sha256'];return b
    pins=EnginePins(**parse((HERE/'pins.json').read_bytes()));manifest=verify_engine(pins)
    context=parse(CONTEXT.read_bytes());capture(CONTEXT)
    for b in context['source_bindings']:original(b);capture(ROOT/b['path'])
    prior_binding=next(b for b in context['source_bindings'] if b['path'].endswith('R03-0005.json'))
    prior=parse(original(prior_binding));check('exact parent reader evidence remains partial PASS',prior['result']=='PASS' and prior['task_complete'] is False)
    for b in prior['files']:original(b);capture(ROOT/b['path'])
    suites=[('regression',38),('coupling',35),('guards',67),('cache',9),('archive',12)];tests=0
    for name,count in suites:
        raw=(ATTEMPT/(name+'.stderr')).read_text()
        declared=re.findall(r'^test_(\S+) \(([^\n]+)\) \.\.\. ok$',raw,re.M)
        check(name+': terminal complete suite',len(declared)==count and re.search(r'Ran '+str(count)+r' tests in [0-9.]+s\n\nOK\s*$',raw) is not None)
        for test,owner in declared:checks.append({'test':'test_'+test,'suite':name,'result':'PASS'})
        tests+=count
    check('all 161 predecessor and targeted cases pass',tests==161)
    for name,count in [('regression',38),('coupling',35)]:
        outcome=parse((ATTEMPT/(name+'.stdout')).read_bytes())
        check(name+': original assertions preserved',outcome['result']=='PASS' and outcome['tests']==count
            and outcome['errors']==outcome['failures']==0 and outcome['assertions_changed'] is False)
    main=EXAMPLES/'0004';result=parse((main/'result.json').read_bytes());cold=parse((ATTEMPT/'cold.stdout').read_bytes())
    check('actual atomic ten-member application with separate Decisions',result['result']=='PASS' and result['applied_corrections']==result['independent_correction_decisions']==10
        and result['signed_transactions']==2 and result['idempotent_retry'] and result['owned_store_and_key_removed'])
    check('actual owner and canonical effects remain absent',result['actual_owner_outcome'] is None and result['authority_effect']=='none'
        and result['canonical_effects_applied']==result['source_effects_applied']==0 and not result['human_pilot'] and not result['private_keys_exported'])
    selected=[(main,'cold-expected-replay.json',cold)]
    recovery_root=EXAMPLES/'0005-recovery';recovery=parse((recovery_root/'result.json').read_bytes())
    check('three actual interruption/recovery and cold child processes',recovery['result']=='PASS' and recovery['actual_interrupted_processes']==recovery['fresh_cold_processes']==3)
    for case in recovery['cases']:
        stage=case['stage'];out=recovery_root/stage;before=parse((out/'before-public-files.json').read_bytes());interrupted=parse((out/'interrupted-public-files.json').read_bytes())
        check(stage+': actual exit 86 and owned key/store cleanup',case['result']=='PASS' and case['child_exit_code']==86 and case['owned_store_removed'] and case['private_key_removed_before_child'])
        check(stage+': exact retry and wrong HEAD recovery refusal',case['exact_retry_idempotent'] and case['wrong_head_recovery_rejected'] and case['original_committed_prefix_preserved'])
        for name,b in before.items():
            if name.startswith('transactions/'):check(stage+': committed original '+name,interrupted[name]==b)
        h=parse(base64.b64decode(interrupted['HEAD.json']['base64_original_bytes']))
        check(stage+': correct observed commit boundary',h['sequence']==case['committed_sequence_at_interruption']==(2 if stage=='after-head' else 1))
        check(stage+': exact pending original retained','PENDING.json' in interrupted)
        check(stage+': staged transaction boundary',('transactions/0000000002.json' in interrupted)==(stage!='after-pending'))
        selected.append((out,'expected-replay.json',parse((out/'cold.stdout').read_bytes())))
    with engine(pins) as handle:
        for directory,expected_name,cold_result in selected:
            expected=parse((directory/expected_name).read_bytes());archive_path=directory/'branch.snapshot'
            check(directory.name+': independently pinned original archive and expected replay',sha(archive_path.read_bytes())==expected['archive_sha256']
                and cold_result['result']=='PASS' and cold_result['original_archive_sha256']==expected['archive_sha256']
                and cold_result['expected_replay_sha256']==sha((directory/expected_name).read_bytes()) and cold_result['projection_parity']
                and cold_result['signed_transaction_replay'] and not cold_result['keys_restored'] and not cold_result['Session_memory_restored'])
            with tempfile.TemporaryDirectory(prefix='cal-R03-correction-proof-') as temp:
                data=restore(archive_path,expected['archive_sha256'],Path(temp)/'store',pins)
                check(directory.name+': independently reverified projection and transactions',handle.common.digest(data['projection'])==expected['projection_sha256']
                    and [handle.common.digest(t) for t in data['transactions']]==expected['transaction_sha256s'])
                rows=verify_result(handle,data,data,data['transactions'][-1]['proposal'])
                check(directory.name+': ten exact current postimages and unchanged historical predecessors',rows==expected['applied_corrections'])
                for row in rows:
                    check(directory.name+': exact correction '+row['version_ref'],row['correction_proof']['domain_scope_ref']==DOMAIN
                        and row['correction_proof']['carrier_use']=='retained-reviewed-predecessor-carrier')
                check(directory.name+': signed scope distinct from record domain',data['config']['scope_ref']=='project:cyberalchemy-v2-to-lab-migration'
                    and data['config']['authorized_domain_scope_refs']==[DOMAIN] and data['transactions'][-1]['approval']['configuration_digest']==handle.common.digest(data['config']))
    members=parse((HERE/'review-members.json').read_bytes());check('16 separately identified final review members',len(members['members'])==16
        and len({m['member_ref'] for m in members['members']})==16 and not members['complete_final_package'])
    for member in members['members']:
        check(member['member_ref']+': candidate posture and unresolved actual owner',member['actual_owner_outcome'] is None and member['authority_effect']=='none')
        for b in member['bindings']:original(b);capture(ROOT/b['path'])
    for directory in [HERE,EXAMPLES]:
        for path in sorted(directory.rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts and path.name!='R03-0006.json':capture(path)
    drift=[]
    for path,expected_sha in sorted(files.items()):
        if sha((ROOT/path).read_bytes())!=expected_sha:drift.append(path)
    check('all exact candidate and retained parent files have no drift',not drift)
    receipt={'schema_version':'lab-R03-reference-correction-proof/v1-candidate','task':'R03','result':'PASS','task_complete':False,
        'authority_effect':'none','actual_owner_outcome':None,'canonical_effects_applied':0,'source_effects_applied':0,
        'tests':tests,'applied_corrections_per_case':10,'independent_decisions_per_case':10,'atomic_application_cases':4,
        'fresh_cold_processes':4,'actual_interrupted_processes':3,'review_members':16,'private_keys_exported':False,'Session_memory_exported':False,'human_pilot':False,
        'declared_operations':34,'implemented_operations':prior['implemented_operations'],'remaining_operations':30,
        'prior_reader_proof':prior_binding,'engine_manifest_binding':bind(MANIFEST),'review_members_binding':bind(HERE/'review-members.json'),
        'verified_obligation_ids':[o['id'] for o in context['obligations']],'source_drift':drift,'checks':checks,
        'files':[{'path':path,'sha256':digest} for path,digest in sorted(files.items())],
        'preserved_failed_observations':['0001 historical carrier refusal','0002 legacy descriptor lookup and relative adapter path','0003 cache import and missing inherited helper'],
        'remaining_obligations':['Remaining 30 exact API operations and complete candidate/Decision coverage; actual Agent/operator journey.',
            'Reader successor consuming signed correction histories, W07 integration, persistent SQLite/ontology joins and source-backed O03 queries.',
            'Canonical semantic carrier/definition target and publisher closure, complete S02 review package and actual R08 owner response.',
            'Authorized A01 admission, separately scoped A02 operations and observed A03/A04 evidence.'],
        'claim_ceiling':'Exact controlled candidate corrections and replay/recovery only. No original source rewrite, canonical admission, actual human owner outcome or completed R03/full plan.',
        'duration_seconds':time.perf_counter()-started}
    emit(HERE/'receipts/R03-0006.json',receipt)
    print(json.dumps({'result':'PASS','tests':tests,'checks':len(checks),'files':len(files),'corrections_per_case':10,'actual_interrupted_processes':3,
        'fresh_cold_processes':4,'task_complete':False,'authority_effect':'none'},sort_keys=True))


if __name__=='__main__':run()
