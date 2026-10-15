"""Audit captured consumer evidence without interpreting shape as authority."""
from pathlib import Path
import hashlib,json,sys
root=Path.cwd();p=Path(__file__).resolve().parent
u=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.intent'
def load(name):return json.loads((u/name).read_bytes())
checks=[]
def check(name,value):
    assert value,name
    checks.append({'check_id':name,'result':True})
for stem in ['carrier-inspection','profile','reuse','dependency','inventory']:
    r=load(stem+'-command-result.json')
    check(stem+'-actual-terminal0',r['exit_code']==0 and not(u/r['stderr']).read_bytes())
typed=load('types-logic-receipt.json');consumer=load('carrier-consumer-inspection.json');profile=load('authority-profile-checks.json')
refs=typed['inputs']+typed['checker_bindings']+list(consumer['selected_inputs'].values())+profile['checker_bindings']+list(profile['selected_inputs'].values())
for ref in refs:
    check('exact-'+ref['path'],hashlib.sha256((root/ref['path']).read_bytes()).hexdigest()==ref['sha256'])
check('frozen-input-and-checker-denominators',len(typed['inputs'])==17 and len(typed['checker_bindings'])==5)
for index,row in enumerate(consumer['checks']):
    check('consumer-observation-'+str(index+1),row['result'])
check('consumer-254-observations',consumer['check_count']==len(consumer['checks'])==254)
check('coordinate-account',len(consumer['source_coordinate_correspondence'])==16 and consumer['source_coordinate_account_complete'])
check('49-carrier-probes-nine-acceptances',len(consumer['carrier_shape_probes'])==49 and sum(r['schema_accepted'] for r in consumer['carrier_shape_probes'])==9)
check('11-Definition-probes-two-acceptances',len(consumer['definition_shape_probes'])==11 and sum(r['schema_accepted'] for r in consumer['definition_shape_probes'])==2)
check('35-supplied-comparison-models',len(consumer['typed_comparison_models'])==35)
check('18-unresolved-consumer-findings',len(consumer['unresolved_consumer_findings'])==18)
check('40-profiles-39-rejections',len(profile['profiles'])==40 and sum(r['expected_rejection'] for r in profile['profiles'])==39)
check('124-frames-123-rejections',len(profile['finite_comparison_frames'])==124 and sum(r['expected_rejection'] for r in profile['finite_comparison_frames'])==123)
check('39-pending-maps',len(profile['source_map_obligations'])==39)
for name,report in [('consumer',consumer),('profile',profile)]:
    check(name+'-no-fidelity-or-authority-inference',report['source_fidelity']=='pending' and report['semantic_ready'] is False and report['authority_effect']=='none')
check('no-accepted-semantic-correspondence',not consumer['accepted_semantic_map_refs'] and consumer['accepted_semantic_correspondence_complete'] is False)
check('no-actual-Intent-instance-effects',consumer['actual_Intent_instance_effects_established'] is False)
context=load('context.json');check('no-retained-Intent-preparation-failures',not context['retained_preparation_failure_refs'])
record={'result':'PASS-exact-consumer-stage-records-and-bindings','authority_effect':'none','checks':checks,'check_count':len(checks),'retained_failed_consumer_attempts':0,'retained_failed_consumer_comparison_refs':[],'accepted_maps':[],'source_fidelity':'pending','semantic_ready':False}
with(p/'consumer-stage-audit.json').open('x') as f:json.dump(record,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in record.items() if k!='checks'}))
