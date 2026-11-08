"""Read all selected receipts/current final witnesses; never rewrite accepted units."""
from pathlib import Path
import hashlib,json,os,time
from . import support as s

def audit():
 plan=s.read(s.PLAN);source=s.read(s.SOURCE);s.require(plan['source_plan']==s.binding(s.SOURCE),'source plan drift')
 expected=[t['id'] for t in source['tasks']];s.require(len(expected)==19 and [t['id'] for t in plan['tasks']]==expected,'plan selection drift')
 cache={};rows=[];started=time.monotonic();binding_count=0;witnesses=0
 def verify(ref):
  nonlocal binding_count
  binding_count+=1;rel=Path(ref['path']);s.require(not rel.is_absolute() and '..' not in rel.parts,'unsafe audit reference')
  p=s.ROOT/rel;s.require(p.is_file(),'missing audit input '+str(rel));st=p.stat();stamp=(st.st_size,st.st_mtime_ns,st.st_ino)
  hit=cache.get(str(p))
  if hit is None or hit['stamp']!=stamp:
   digest=hashlib.sha256(p.read_bytes()).hexdigest();s.require(p.stat().st_size==st.st_size and p.stat().st_mtime_ns==st.st_mtime_ns,'audit file changed during read')
   cache[str(p)]={'stamp':stamp,'sha256':digest}
  s.require(cache[str(p)]['sha256']==ref['sha256'],'stale acceptance binding '+str(rel));return p
 for task,original in zip(plan['tasks'],source['tasks']):
  id=task['id'];s.require(task['selected'] and task['status']=='accepted','selected unit incomplete '+id)
  r=s.read(verify(task['receipt']));s.require(r['task']==id and r['result']=='accepted' and [x['criterion'] for x in r['criteria']]==original['acceptance'],'criterion mismatch '+id)
  s.require(all(c['result']=='pass' for c in r['controls']),'failed accepted control '+id)
  for ref in r['artifacts']+r['inputs']:verify(ref)
  h=s.BASE/id.lower();c=s.read(h/'context-pack.json');s.require(c['strict_coverage']=='pass','uncovered context '+id)
  if id.startswith('E') and id!='E06':
   report=s.read(h/'controls.json');s.require(report['result']=='pass','missing final extension controls');full=0
   for case in report['cases']:
    answer=s.read(verify(case['answer']));verify(case['input'])
    if answer['status']=='fresh-extension-candidate':
     full+=1;v=answer['value'];verify(answer['completion']);verify(v['request']);verify(v['witness']);verify(v['supervised_record'])
     for ref in v['imports']+v['worker_sources']:verify(ref)
     for module in v['kernel']:verify(module['source']);verify(module['olean']);s.require('sorryAx' not in module['output'],'admitted current witness')
     s.require(v['value']['authority_effect']=='none' and not v['value']['application_authorized'],'extension authority expansion')
   wanted={'E00':6,'E01':4,'E02':3,'E03':2,'E04':3,'E05':1}[id];s.require(full==wanted,'final full witness count '+id);witnesses+=full
  rows.append({'task':id,'receipt':task['receipt'],'criteria_verified':len(r['criteria']),'control_records':len(r['controls']),'result':'accepted-current'})
 for p,data in cache.items():
  st=Path(p).stat();s.require((st.st_size,st.st_mtime_ns,st.st_ino)==data['stamp'],'file changed after its audit '+p)
 e06=s.read(s.BASE/'e06/sample-check-report.json');s.require(e06['sample_only'] and e06['result']=='sample-checked' and not e06['universal_translation_proved'],'independent sample scope drift')
 s.require(len(s.read(s.BASE/'e06/dependency-closure.json')['declarations'])==18,'sample closure drift')
 result={'schema':'relational.complete-selected-plan-audit/v1','result':'complete','selected_units':19,'accepted_units':19,'criteria_verified':sum(x['criteria_verified'] for x in rows),'extension_full_final_witnesses':witnesses,'extension_control_records':sum(x['control_records'] for x in rows if x['task'].startswith('E')),'independent_checker_scope':'One E00 sample with complete 18-declaration closure; no whole-core or universal translation claim.','binding_checks':binding_count,'unique_current_files':len(cache),'seconds':time.monotonic()-started,'tasks':rows,'original_v1_gates':'R06/G4 separately pending; no deployment or live authority effect','human_feedback':s.binding(s.BASE/'p11/human-feedback.json'),'authority_effect':'none'}
 s.write(s.BASE/'execution/complete-plan-audit.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ['tasks','human_feedback']},indent=2),flush=True);return result
if __name__=='__main__':audit()
