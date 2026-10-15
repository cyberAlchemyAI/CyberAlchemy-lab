"""Close candidate W08 preparation only after exact current evidence passes."""
import ast
import re
from packet import *

PACKET_SHA='590bcbfb134fccddd2e38341dc94c9f67e2ac83b87c4bceb8c9cf488813d303a'
READER_SHA='13624b0ed1dc9a28bc95d363a2f7b0f559402e64fd7504a45adf3f6b25a3ae4f'


def run():
    files={};checks=[]
    def capture(b):
        raw=bound(b);require(b['path'] not in files or files[b['path']]==b['sha256'],'conflicting evidence source')
        files[b['path']]=b['sha256'];return parse(raw) if b['path'].endswith('.json') else raw
    def check(name,value):require(value,name);checks.append({'test':name,'result':'PASS'})
    prerequisite();context=capture({'path':str((RUN/'context-W08.json').relative_to(ROOT)),'sha256':CONTEXT_SHA})
    for b in context['source_bindings']:
        value=capture(b)
        if isinstance(value,dict):
            for r in value.get('files',[]):capture({'path':r['path'],'sha256':r['sha256']})
    packet=capture({'path':str((HERE/'packages/0001/preparation.json').relative_to(ROOT)),'sha256':PACKET_SHA})
    capture({'path':str((HERE/'packet.py').relative_to(ROOT)),'sha256':READER_SHA})
    check('closed exact prepared packet',validate(packet)['result']=='PASS')
    declared={n.name for n in ast.walk(ast.parse((HERE/'test_packet.py').read_text())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
    log=(HERE/'attempts/guards.stderr').read_text();observed=re.findall(r'^(test_\S+) \(([^\n]+)\) \.\.\. ok$',log,re.M)
    check('all 42 declared guards actually passed',len(declared)==len(observed)==42 and {name for name,_ in observed}==declared
        and re.search(r'Ran 42 tests in [0-9.]+s\n\nOK\s*$',log) is not None)
    build=capture(binding(HERE/'attempts/build-observation.json'));actual=parse((HERE/'attempts/build.stdout').read_bytes())
    check('actual original materialization and producer retained',build['terminal_exit_code']==0 and build['execution_handle']==59298
        and build['output_binding']==binding(HERE/'packages/0001/preparation.json') and actual['result']=='PASS' and actual['preparation']==build['output_binding']
        and actual['models']==10 and actual['transitions']==28 and actual['members']==27 and actual['selected_carrier_postimages']==13)
    capture(build['original_producer_binding'])
    cold=parse((HERE/'attempts/pinned-cold.stdout').read_bytes());capture(binding(HERE/'attempts/pinned-cold.stdout'))
    check('independently pinned fresh original-source reconstruction',cold['result']=='PASS' and cold['packet_binding']['sha256']==PACKET_SHA
        and cold['reader_binding']['sha256']==READER_SHA and cold['members']==27 and cold['selected_carrier_postimages']==13 and cold['collision_dispositions']==6
        and cold['model_execution_gaps_retained']==56 and cold['actual_owner_outcome'] is None and cold['canonical_effects_applied']==0
        and cold['local_transactions_applied']==0 and cold['operational_permissions_granted']==0 and not cold['Session_memory_restored']
        and cold['expired_Lesson_historical_only'] and not cold['runtime_activation'] and not cold['human_pilot'] and not cold['all_workflow_transitions_executed'])
    check('fresh cold process completed with empty stderr',(HERE/'attempts/pinned-cold.stderr').read_bytes()==b'')
    terminals=capture(binding(HERE/'attempts/terminal-observations.json'))
    check('all actual selected process completions recorded',terminals['exit_codes']=={'build':0,'guards':0,'initial-cold-read':0,'pinned-cold-read':0})
    for m in packet['members']:
        for b in m['targets']+m['evidence']:capture(b)
    for r in packet['candidate_collision_dispositions']:
        for w in r['witnesses']:capture(w['binding'])
    for b in capture(binding(HERE/'manifest.json'))['files']:capture(b)
    for p in HERE.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts and 'receipts' not in p.parts:capture(binding(p))
    receipt={'schema_version':'lab-W08-review-preparation-evidence/v1-candidate','task':'W08','result':'PASS','task_complete':True,
        'tests':42,'checks':[{'test':full,'result':'PASS'} for _,full in observed],'validation_checks':checks,
        'files':[{'path':p,'sha256':s} for p,s in sorted(files.items())],'source_bindings':context['source_bindings'],'source_drift':[],
        'preparation_binding':binding(HERE/'packages/0001/preparation.json'),'review_binding':binding(HERE/'REVIEW.md'),
        'members':27,'workflow_models':10,'model_transitions':28,'model_execution_gaps_retained':56,'selected_carrier_postimages':13,
        'canonical_collision_targets':0,'case_qualified_collision_dispositions':6,'expired_Lesson_current_use':False,
        'authority_effect':'none','actual_owner_outcome':None,'canonical_effects_applied':0,'local_transactions_applied':0,
        'operational_permissions_granted':0,'runtime_activation':False,'human_pilot':False,'complete_final_package':False,
        'remaining_obligations':[],'admitted_operation_route':'R08/A01/A03','final_assembly_obligations':packet['final_assembly_obligations'],
        'claim_ceiling':'Complete original candidate workflow review preparation criteria only. Exact independent model/code/scoped historical Lesson members and realistic source-backed examples are prepared. Actual owner authority, final S02 envelope, operative entrypoint/environment/publisher closure and admitted operation remain separate downstream obligations.'}
    receipts=HERE/'receipts';receipts.mkdir(exist_ok=False);p=receipts/'0001.json';put(p,receipt)
    print(encoded({'result':'PASS','task_complete':True,'tests':42,'validation_checks':len(checks),'files':len(files),'members':27,'receipt':binding(p)}).decode(),end='')


if __name__=='__main__':run()
