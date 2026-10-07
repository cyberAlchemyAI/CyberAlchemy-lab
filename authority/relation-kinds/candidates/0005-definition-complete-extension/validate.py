#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent; LAB=ROOT.parents[3]
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def main():
 subprocess.run([sys.executable,str(ROOT/'build.py')],check=True);m=load(ROOT/'model.json');ex=load(ROOT/'examples.json');checks=[]
 def ck(i,o,d):checks.append({'check_id':i,'result':'PASS' if o else 'BLOCK','detail':d})
 ck('predecessor-current',sha(LAB/m['predecessor']['path'])==m['predecessor']['sha256'],m['predecessor'])
 rule=m['typed_connection_extension_rule']; reg=load(LAB/'authority/definitions/registry.json'); current=reg['current_lookup'].get(rule['definition_ref'].split('@')[0]);ck('extension-rule-admitted-current',current==rule['definition_ref'] and sha(LAB/rule['path'])==rule['sha256'] and rule['admission_decision_ref']=='CAL-DECISION-0064-TYPED-CONNECTION-EXTENSION-RULE-ADMISSION',rule)
 for item in m['carrier_inputs'].values(): ck('input-'+Path(item['path']).stem,sha(LAB/item['path'])==item['sha256'],item)
 entries=m['entries'];ids=[e['relation_kind_id'] for e in entries];axes=[e['axis_id'] for e in entries];qs=[e['unique_question'] for e in entries]
 ck('40-active-orthogonal-axes',len(ids)==len(set(ids))==40 and len(set(axes))==40 and len(set(qs))==40,{'ids':len(ids),'axes':len(set(axes)),'questions':len(set(qs))})
 pair_rows=[]
 for e in entries:
  ps=[(p['source_kind'],p['target_kind']) for p in e['allowed_endpoint_pairs']]; pair_rows.append({'relation_kind_id':e['relation_kind_id'],'nonempty':bool(ps),'unique':len(ps)==len(set(ps)),'no_wildcards':all('*' not in p for p in ps),'projections':e['source_kinds']==sorted({a for a,b in ps}) and e['target_kinds']==sorted({b for a,b in ps})})
 ck('closed-explicit-pairs',all(all(v for k,v in x.items() if k!='relation_kind_id') for x in pair_rows) and sum(len(e['allowed_endpoint_pairs']) for e in entries)==m['counts']['declared_endpoint_pairs'],pair_rows)
 groups=m['connection_extensions'];ck('extension-rule-gates-complete',len(groups)==m['counts']['extension_groups'] and all(x['added_pairs'] and x['unique_question'] and x['required_qualifier_axes'] and x['forbidden_inferences'] and x['lifecycle_rule'] for x in groups),{'groups':len(groups),'pairs':sum(len(x['added_pairs']) for x in groups)})
 ck('17-new-axes-one-deferred',m['counts']['new_relation_kinds']==17 and m['counts']['deferred_relation_kinds']==1 and m['deferred_axes'][0]['relation_kind_id']=='relation.subclass-of',m['counts'])
 ck('scope-decisions-closed',m['scope_decisions']==[{'candidate':'ontology-node-represents-subject','decision':'ontology-local-binding','reason':'Ontology Node/v2 already carries the exact subject revision binding; no global represents axis is created, avoiding identity collapse and wildcard endpoints.'},{'candidate':'agent-instance-profile-binding','decision':'new-global-axis','relation_kind_id':'relation.profiled-by','reason':'Profile binding is neither classification nor demonstrated conformance.'}],m['scope_decisions'])
 er=[]
 for e in entries:
  x=ex[e['relation_kind_id']];p=(x['source_ref'].split(':',1)[0],x['target_ref'].split(':',1)[0]);allowed={(q['source_kind'],q['target_kind']) for q in e['allowed_endpoint_pairs']};er.append({'id':e['relation_kind_id'],'pair':p in allowed,'qualifiers':set(e['required_qualifier_axes'])<=set(x['qualifiers']),'authority':x['authority_effect']=='none','lifecycle':bool(x['lifecycle_state']),'evidence':bool(x['evidence_refs'])})
 ck('typed-coupling-examples',all(all(v for k,v in x.items() if k!='id') for x in er),er)
 noncollapse=[('member-of','contributes-to'),('uses-tool','realizes'),('profiled-by','conforms-to'),('applies-lesson','uses-method'),('produces','declares-effect-on'),('challenges','evidence-bears-on'),('occurs-during','affects'),('controls','realizes'),('tests-hypothesis','evaluates'),('consumes-view','fulfills-request')]
 ck('no-collapse',all(f'relation.{a}' in ids and f'relation.{b}' in ids and a!=b for a,b in noncollapse),noncollapse)
 ck('canonical-single-relation-identity',m['canonical_instance_rule']=={'allowed_modes':['projects-as','represented-by'],'dual_writable_copies_forbidden':True},m['canonical_instance_rule'])
 before=[(ROOT/x).read_bytes() for x in ('model.json','examples.json','MODEL.md')];subprocess.run([sys.executable,str(ROOT/'build.py')],check=True);after=[(ROOT/x).read_bytes() for x in ('model.json','examples.json','MODEL.md')];ck('deterministic',before==after,{'model_sha256':sha(ROOT/'model.json'),'projection_sha256':sha(ROOT/'MODEL.md')})
 result='PASS' if all(x['result']=='PASS' for x in checks) else 'BLOCK';receipt={'schema_version':'cyberalchemy-lab-definition-complete-relation-validation/v1','result':result,'authority_effect':'none','checks':checks,'materials':{'model_sha256':sha(ROOT/'model.json'),'examples_sha256':sha(ROOT/'examples.json'),'projection_sha256':sha(ROOT/'MODEL.md')},'claim_ceiling':'PASS establishes a closed candidate relation surface with exact pairs, no wildcards, rule-complete extensions, examples, and tested no-collapse distinctions. It admits nothing.'};dump(ROOT/'receipts/validation.json',receipt);print(json.dumps({'result':result,'checks':len(checks),**receipt['materials']},sort_keys=True));return 0 if result=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
