"""Exact source owner/role records; labels and identity echoes grant nothing."""
import argparse,base64,hashlib,importlib.util,json,os,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];API=ROOT/'product/lab/release-candidates/v1/interface/api-v19'
PIN='fcd98b74253bc5a7f081faed13c2b4c198df55ff3f6e6772563e1d50a784ff1b'
KINDS={'role','role-assignment','owner-registry','principal','policy','authority-claim','authority-boundary','workflow-decision-profile','user-decision-preference'}
def sha(b):return hashlib.sha256(b).hexdigest()
def guard(pin):
 p=HERE/'owner-routing-inspection-source-0002.json';assert sha(p.read_bytes())==pin
 for row in json.loads(p.read_bytes())['files']:
  p=ROOT/row['path'];assert p.is_file() and not p.is_symlink() and sha(p.read_bytes())==row['sha256'],row['path']
def main():
 p=argparse.ArgumentParser();p.add_argument('--source-sha256',required=True);a=p.parse_args();guard(a.source_sha256)
 name='_cal_actual_owner_routing_inventory';spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)]);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
 def imported(n):return __import__(name+'.'+n,fromlist=['*'])
 P=imported('protocol');M=imported('artifact_model');W=imported('workspace');G=imported('guard');H=imported('handlers');G.verify(PIN);rows=[]
 with P.source.replay_source('custody-participation') as view:
  source_cut=H.cut(view)
  for s in sorted(view.subjects.values(),key=lambda r:r['version_ref']):
   if s['kind'] not in KINDS:continue
   raw,locator,encoding,enclosing=M.record_bytes(view,s);body=P.frame_parse(raw);W.privacy(body);header=M.artifact_ref(view,s);assert sha(raw)==header['byte_sha256']
   rows.append({'artifact':header,'semantic_kind':s['kind'],'effective_admission_state':s['effective_state'],'source':s['source'],'source_locator':locator,'encoding':encoding,'enclosing_source_sha256':enclosing,'original_bytes_base64':base64.b64encode(raw).decode(),'decoded_body':body})
  assert len(view.subjects)==582
 G.verify(PIN);guard(a.source_sha256)
 counts={kind:{state:sum(r['semantic_kind']==kind and r['effective_admission_state']==state for r in rows) for state in sorted({r['effective_admission_state'] for r in rows if r['semantic_kind']==kind})} for kind in sorted(KINDS)}
 current=[r for r in rows if r['effective_admission_state'] in ['admitted-current','local-admitted-current']];principals={r['artifact']['identity_ref']:r['decoded_body']['payload']['stable_subject_ref'] for r in current if r['semantic_kind']=='principal'}
 assignments=[]
 for r in current:
  if r['semantic_kind']!='role-assignment':continue
  b=r['decoded_body'];assignments.append({'artifact':r['artifact'],'role_ref':b.get('role_ref',b.get('payload',{}).get('role_ref')),'assignee_ref':b.get('assignee_ref',b.get('payload',{}).get('assignee_ref')),'scope_ref':b['scope_ref'],'period':b.get('period',b.get('payload',{}).get('period')),'assignment_state':b.get('assignment_state',b.get('payload',{}).get('assignment_state')),'exact_declared_principal_stable_subject_matches':[identity for identity,stable in principals.items() if stable==b.get('assignee_ref',b.get('payload',{}).get('assignee_ref'))],'current_authority_verified':False})
 report={'schema_version':'lab-original-owner-routing-inventory/v1-candidate','result':'OBSERVED','source_API_sha256':PIN,'source_cut':source_cut,'total_source_subjects':582,'selected_records':rows,'kind_state_counts':counts,'current_principal_stable_subjects':principals,'current_role_assignment_declared_links':assignments,'automatic_Principal_aliases':[],'required_governing_role_coverage_verified':False,'current_owner_authority_verified':False,'public_review_adapter_implemented':False,'actual_owner_outcome':None,'authority_effect':'none','task_complete':False}
 W.privacy(report);fd=os.open(HERE/'owner-routing-inspection-result-0002.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'w') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
 print(json.dumps({'result':'OBSERVED','selected_records':len(rows),'kind_state_counts':counts,'principals':principals,'current_role_assignments':len(assignments),'required_role_coverage_verified':False}),flush=True)
if __name__=='__main__':main()
