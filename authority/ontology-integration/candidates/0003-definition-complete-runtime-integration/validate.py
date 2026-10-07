#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parent;LAB=ROOT.parents[3]
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def main():
 subprocess.run([sys.executable,str(ROOT/'build.py')],check=True);m=load(ROOT/'integrated-model.json');g=load(ROOT/'governed-model-record.json');checks=[]
 def ck(i,o,d):checks.append({'check_id':i,'result':'PASS' if o else 'BLOCK','detail':d})
 states=[]
 for name,x in m['inputs'].items():states.append({'name':name,'current':sha(LAB/x['path'])==x['sha256']})
 ck('all-inputs-current',all(x['current'] for x in states),states)
 ck('exact-definition-partition',m['counts']['admitted_definitions']==60 and m['counts']['carrier_backed_before_actions']==20 and m['counts']['new_durable_carriers']==34 and m['counts']['noncarrier_realizations']==6 and m['counts']['definition_realizations_after_actions']==60, m['counts'])
 ck('projected-admission-counts',m['counts']['projected_artifact_type_admissions']==93 and m['counts']['active_relation_kinds']==40 and m['counts']['new_relation_kinds']==17 and m['counts']['deferred_relation_kinds']==1,m['counts'])
 mem=m['memory_contract'];ck('machine-memory-boundary',mem['machine_agent_durable_memory'] is False and mem['long_term_continuity_owner']=='project-state' and mem['short_term_owner']=='agent-session' and mem['short_term_persistence_allowed'] is False and mem['hidden_cross_session_memory_forbidden'] is True,mem)
 ont=m['ontology_contract'];ck('ontology-source-direction',ont['global_connection_contract']=='relation-kind' and ont['global_connection_instance']=='typed-relation' and ont['subject_representation']=='ontology-node' and set(ont['derived_surfaces'])=={'ontology-cut','ontology-view','context-view'},ont)
 rs={x['subject']:x for x in m['runtime_effective_state']};ck('runtime-ladder-separated',rs['binding-v2']['state']=='admitted' and rs['ontology-lifecycle-rust/v1']['state']=='adopted' and rs['local-cli-instance-0049']['state']=='historically-authorized-and-executed' and rs['source-runtime-v4']['state']=='product-approved-only' and rs['persistent-ontology-service']['state']=='not-established',rs)
 ck('adopted-source-exact',rs['ontology-lifecycle-rust/v1']['source_sha256']=='f1b3f7cf463ebcc6e7b887b374d75adeac29ba38acfec3bafacfe4d3159f3a7b',rs['ontology-lifecycle-rust/v1'])
 ck('no-implicit-admission-or-runtime',m['authority_effect']=='none' and m['status']=='candidate-complete-awaiting-owner-review' and m['admission_sequence']['typed_relation_instances_admitted']==0 and m['admission_sequence']['ordinary_artifact_instances_admitted']==1 and m['admission_sequence']['governed_model_instance_decision_target']==1 and m['admission_sequence']['runtime_change_authorized'] is False,m['admission_sequence'])
 schema=load(LAB/'authority/artifact-types/governed-model/v1/schema.json');errors=sorted(Draft202012Validator(schema).iter_errors(g),key=lambda x:list(x.path));ck('governed-model-instance-valid',not errors, [{'path':'/'.join(map(str,e.path)),'message':e.message} for e in errors])
 contract_path,contract_digest=g['payload']['contract_ref'].split('#sha256=',1);ck('governed-model-contract-exact',g['node_id']=='cal.governed-model.definition-complete-lab/v1' and g['lifecycle_state']=='candidate' and g['authority_effect']=='none' and contract_path==str((ROOT/'integrated-model.json').relative_to(LAB)) and contract_digest==sha(ROOT/'integrated-model.json') and len(g['payload']['rule_refs'])==16,{'contract_ref':g['payload']['contract_ref'],'rule_count':len(g['payload']['rule_refs'])})
 ck('twelve-stage-complete-flow',len(m['integration_stages'])==12 and [x['order'] for x in m['integration_stages']]==list(range(1,13)) and len(m['end_to_end_flow'])==12,{'stages':len(m['integration_stages']),'flow':len(m['end_to_end_flow'])})
 ck('non-collapse-complete',len(m['non_collapse_laws'])==11,m['non_collapse_laws'])
 before=[(ROOT/x).read_bytes() for x in ('integrated-model.json','governed-model-record.json','MODEL.md')];subprocess.run([sys.executable,str(ROOT/'build.py')],check=True);after=[(ROOT/x).read_bytes() for x in ('integrated-model.json','governed-model-record.json','MODEL.md')];ck('deterministic',before==after,{'model_sha256':sha(ROOT/'integrated-model.json'),'governed_model_sha256':sha(ROOT/'governed-model-record.json'),'projection_sha256':sha(ROOT/'MODEL.md')})
 result='PASS' if all(x['result']=='PASS' for x in checks) else 'BLOCK';r={'schema_version':'cyberalchemy-lab-definition-complete-runtime-integration-validation/v1','result':result,'authority_effect':'none','checks':checks,'materials':{'model_sha256':sha(ROOT/'integrated-model.json'),'governed_model_sha256':sha(ROOT/'governed-model-record.json'),'projection_sha256':sha(ROOT/'MODEL.md')},'claim_ceiling':'PASS establishes a current evidence-bound integrated candidate model and schema-valid governed instance candidate. It admits nothing and establishes no live service.'};dump(ROOT/'receipts/validation.json',r);print(json.dumps({'result':result,'checks':len(checks),**r['materials']},sort_keys=True));return 0 if result=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
