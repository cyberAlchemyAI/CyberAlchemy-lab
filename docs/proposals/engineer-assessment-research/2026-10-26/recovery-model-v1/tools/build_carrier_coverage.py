"""Index the existing domain records and carrier status without inventing runs."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
write=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
DOMAIN=ROOT/'model/lab-records'
product=['product/product.json']
research=[str(p.relative_to(ROOT)) for p in sorted(DOMAIN.glob('*.json')) if p.name!='relation-proposals.json']
roles=[str(p.relative_to(ROOT)) for p in sorted((DOMAIN/'roles').glob('*.json'))]
definitions=[str(p.relative_to(ROOT)) for p in sorted((ROOT/'model/definition-records').glob('*/definition.json'))]
concrete=load(ROOT/'model/concrete-records/index.json')
local=[p for x in concrete['families'] if x['carrier_status']=='candidate-requested' for p in x['record_refs']]
recovery=load(ROOT/'model/recovery/index.json')
local+=recovery['record_refs']
requests=[str(p.relative_to(ROOT)) for p in sorted((ROOT/'model/carriers').glob('*/v1/request.json'))]
assert len(product)==1 and len(research)==33 and len(roles)==27 and len(definitions)==81 and len(local)==116 and len(requests)==13
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
 'selected_lab_instance_records':{'count':len(product)+len(research)+len(roles)+len(definitions),'product':product,'research':research,'roles':roles,'definitions':definitions},
 'local_candidate_instance_records':{'count':len(local),'records':local},
 'artifact_type_requests':{'count':len(requests),'records':requests},
 'embedded_or_source_controls':[
  {'source_ref':'model/definitions.json','treatment':'task-local normative source for 81 individual Definition candidates','gap_ref':'AT-G04'},
  {'source_ref':'model/definition-records/index.json','treatment':'generated candidate lookup','gap_ref':'AT-G05'},
  {'source_ref':'model/ontology.json','treatment':'local ontology proposal, no Lab graph standing','gap_ref':'AT-G01'},
  {'source_ref':'model/lab-records/relation-proposals.json','treatment':'114 unapplied relation proposals, not typed relation instances','gap_ref':'AT-G02'},
  {'source_ref':'research/session-studies.json','treatment':'three source entries crosswalked to E05 Experiment Designs','gap_ref':'AT-G03'},
  {'source_ref':'model/concrete-records/index.json','treatment':'generated lookup for extracted rows','gap_ref':'AT-G06'},
  {'source_ref':'model/recovery/rule-source.json','treatment':'task-local source for 20 candidate Recovery Rule records','gap_ref':'AT-G11'},
  {'source_ref':'model/recovery/index.json','treatment':'generated lookup for 20 candidate Recovery Rule records','gap_ref':'AT-G11'},
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
