"""Index the existing domain records and carrier status without inventing runs."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
write=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
DOMAIN=ROOT/'model/lab-records'
product=['product/product.json']
research=[str(p.relative_to(ROOT)) for p in sorted(DOMAIN.glob('*.json')) if p.name not in ('relation-proposals.json','integration-choice-challenge-contract.json')]
governance=['model/lab-records/integration-choice-challenge-contract.json']
policies=[str(p.relative_to(ROOT)) for p in sorted((ROOT/'model/policies/records').glob('*/policy.json'))]
roles=[str(p.relative_to(ROOT)) for p in sorted((DOMAIN/'roles').glob('*.json'))]
definitions=[str(p.relative_to(ROOT)) for p in sorted((ROOT/'model/definition-records').glob('*/definition.json'))]
concrete=load(ROOT/'model/concrete-records/index.json')
local=[p for x in concrete['families'] if x['carrier_status']=='candidate-requested' for p in x['record_refs']]
recovery=load(ROOT/'model/recovery/index.json')
local+=recovery['record_refs']
local+=['model/recovery/administration-policy-candidate.json']
integration=load(ROOT/'model/integration/index.json')
local+=integration['record_refs']
components=load(ROOT/'model/integration/component-index.json')
local+=components['record_refs']
boundaries=load(ROOT/'model/integration/boundary-index.json')
local+=boundaries['record_refs']
policy_index=load(ROOT/'model/policies/index.json')
local+=policy_index['clause_refs']+[policy_index['retention_ref'],policy_index['assistance_ref']]
ux=load(ROOT/'design/index.json')
local+=ux['record_refs']
requests=[str(p.relative_to(ROOT)) for p in sorted((ROOT/'model/carriers').glob('*/v1/request.json'))]
assert len(product)==1 and len(research)==36 and len(governance)==1 and len(policies)==14 and len(roles)==27 and len(definitions)==94 and len(local)==263 and len(requests)==28
study=load(ROOT/'research/session-studies.json')['studies']
crosswalk=[]
for row in study:
 suffix=row['experiment_id'].lower().removeprefix('ea-')
 design=DOMAIN/('experiment-design-'+suffix+'.json')
 d=load(design)
 assert d['node_id']=='experiment-design:ea:'+suffix
 assert d['protocol_ref']==row['protocol']
 crosswalk.append({'study_id':row['experiment_id'],'source_ref':'research/session-studies.json',
                   'design_ref':str(design.relative_to(ROOT)),'protocol_ref':row['protocol'],
                   'source_posture':'authored-register','design_posture':'candidate-unadmitted','run_count':len(row['run_refs'])})
write(ROOT/'model/concrete-records/study-design-crosswalk.json',{'schema_version':'ea.study-design-crosswalk/v1','status':'candidate-source-map','authority_effect':'none','count':len(crosswalk),'entries':crosswalk})
coverage={'schema_version':'ea.carrier-coverage/v1','status':'candidate-audit','authority_effect':'none',
 'selected_lab_instance_records':{'count':len(product)+len(research)+len(governance)+len(policies)+len(roles)+len(definitions),'product':product,'research':research,'governance':governance,'policies':policies,'roles':roles,'definitions':definitions},
 'local_candidate_instance_records':{'count':len(local),'records':local},
 'artifact_type_requests':{'count':len(requests),'records':requests},
 'embedded_or_source_controls':[
  {'source_ref':'model/definitions.json','treatment':'task-local normative source for 94 individual Definition candidates','gap_ref':'AT-G04'},
  {'source_ref':'model/definition-records/index.json','treatment':'generated candidate lookup','gap_ref':'AT-G05'},
  {'source_ref':'model/ontology.json','treatment':'local ontology proposal, no Lab graph standing','gap_ref':'AT-G01'},
  {'source_ref':'model/lab-records/relation-proposals.json','treatment':'114 unapplied relation proposals, not typed relation instances','gap_ref':'AT-G02'},
  {'source_ref':'research/session-studies.json','treatment':'three source entries crosswalked to E05 Experiment Designs','gap_ref':'AT-G03'},
  {'source_ref':'model/concrete-records/index.json','treatment':'generated lookup for extracted rows','gap_ref':'AT-G06'},
  {'source_ref':'model/recovery/rule-source.json','treatment':'task-local source for 21 candidate Recovery Rule records','gap_ref':'AT-G11'},
  {'source_ref':'model/recovery/index.json','treatment':'generated lookup for 21 candidate Recovery Rule records','gap_ref':'AT-G11'},
  {'source_ref':'model/integration/choices.json','treatment':'source for six candidate option reviews; recommendations are provisional','gap_ref':'AT-G14'},
  {'source_ref':'model/integration/contracts.json','treatment':'source for six unexecuted integration verification contracts','gap_ref':'AT-G14'},
  {'source_ref':'model/integration/index.json','treatment':'generated lookup for twelve candidate integration records','gap_ref':'AT-G14'},
  {'source_ref':'model/integration/challenge-triggers.json','treatment':'seven future reconsideration grounds for the candidate Lab Challenge Contract','gap_ref':'AT-G14'},
  {'source_ref':'model/integration/RECONSIDERATION-POLICY.md','treatment':'draft policy source for challenge timing, evidence and resolution; not issued','gap_ref':'AT-G14'},
  {'source_ref':'model/integration/components.json','treatment':'source for 24 candidate technology identities; no selected versions or vendor approval','gap_ref':'AT-G15'},
  {'source_ref':'model/integration/component-index.json','treatment':'generated lookup for 24 candidate components; binding list empty','gap_ref':'AT-G15'},
  {'source_ref':'model/integration/boundaries.json','treatment':'source for six stable integration boundary specifications','gap_ref':'AT-G16'},
  {'source_ref':'model/integration/boundary-index.json','treatment':'generated lookup for six candidate boundary records','gap_ref':'AT-G16'},
  {'source_ref':'model/policies/policy-set.json','treatment':'source register for fourteen unissued Lab Policy/v2 candidates','gap_ref':'AT-G17'},
  {'source_ref':'model/policies/clauses.json','treatment':'source for forty-six candidate policy clauses','gap_ref':'AT-G17'},
  {'source_ref':'model/policies/retention-source.json','treatment':'ten data-class draft schedule with unresolved durations','gap_ref':'AT-G17'},
  {'source_ref':'model/policies/assistance-source.json','treatment':'twenty-four proposed per-session help allowances','gap_ref':'AT-G17'},
  {'source_ref':'model/policies/index.json','treatment':'generated lookup for policy and clause candidates','gap_ref':'AT-G17'},
  {'source_ref':'design/source.json','treatment':'source for 55 candidate UX contracts across six families','gap_ref':'AT-G18'},
  {'source_ref':'design/index.json','treatment':'generated lookup for 55 candidate UX records','gap_ref':'AT-G18'},
  {'source_ref':'design/tokens.json','treatment':'candidate visual token source, not a validated or approved brand','gap_ref':'AT-G18'},
  {'source_ref':'model/concrete-records/role-source-index.json','treatment':'source crosswalk for 27 Lab Role/v1 candidates','gap_ref':None},
  {'source_ref':'model/concrete-records/study-design-crosswalk.json','treatment':'source crosswalk, no additional study or run instance','gap_ref':'AT-G03'}],
 'embedded_subjects':[
  {'source_ref':'model/lab-records/product-thesis.json','count':6,'subject':'untested thesis hypotheses','treatment':'embedded; standalone carrier blocked','gap_ref':'AT-G10'},
  {'source_ref':'model/lab-records/product-thesis.json','count':5,'subject':'thesis intended outcomes','treatment':'embedded in selected Product Thesis/v1 carrier','gap_ref':None},
  {'source_ref':'model/lab-records/relation-proposals.json','count':114,'subject':'unapplied relation proposals','treatment':'manifest entries only','gap_ref':'AT-G02'}],
 'absent_executions':['experiment-run','research-run','evidence-set','measurement-result','finding','decision','participant','candidate-response','scoring-run','criterion-rating','released-case-version','active-permission','live-upload-attempt','live-recovery-decision'],
 'claim_ceiling':'Inventory and candidate carrier preparation only; no admission, run, observed value, participant data or employment use.'}
write(ROOT/'model/carriers/coverage.json',coverage)
print('Coverage:',coverage['selected_lab_instance_records']['count'],'selected-carrier candidates,',len(local),'local-carrier candidates,',len(requests),'type requests,',len(crosswalk),'study crosswalks')
