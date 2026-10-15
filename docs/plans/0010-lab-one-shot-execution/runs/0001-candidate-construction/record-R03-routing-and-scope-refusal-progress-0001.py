"""Bind new routing contract and original backend refusal; retain open runtime work."""
import hashlib,json
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';API=BASE/'api-v46'
def load(p):return json.loads(p.read_bytes())
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def put(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def main():
 parent=API/'receipts/R03-0081.json';old=load(parent);assert old['result']=='PASS' and old['task_complete'] is False
 refusal=load(RUN/'typed-scope-other-backend-refusal-0001.json');assert refusal['result']=='PASS' and refusal['original_backend_refusal']=='effect outside provisioned authority'
 shape=load(RUN/'typed-host-routing-shape-checks-0001.json');assert shape['result']=='PASS' and shape['actual_cases']==8 and not shape['runtime_qualified']
 assert load(RUN/'typed-scope-other-backend-refusal-terminal-0001.json')['actual_exit_code']==0
 assert load(RUN/'typed-host-routing-shape-terminal-0001.json')['actual_exit_code']==0
 rows={r['path']:r for r in old['files']}
 for r in shape['files']:rows[r['path']]=r
 package=BASE/'typed-host-composition-v1';manifest=load(package/'source-manifest.json')
 for r in manifest['files']+manifest['input_bindings']:rows[r['path']]=r
 extras=[parent,package/'source-manifest.json',RUN/'verify-typed-scope-other-backend-refusal-0001.py',RUN/'typed-scope-other-backend-refusal-0001.json',RUN/'typed-scope-other-backend-refusal-0001.log',RUN/'typed-scope-other-backend-refusal-terminal-0001.json',RUN/'verify-typed-host-routing-shape-0001.py',RUN/'typed-host-routing-shape-checks-0001.json',RUN/'typed-host-routing-shape-0001.log',RUN/'typed-host-routing-shape-terminal-0001.json',RUN/'API46-core-schema-selection-0001.json',RUN/'verify-API46-core-schema-original-cases-0001.py',RUN/'run-API46-core-schema-after-diagnostic-0001.py',Path(__file__).resolve()]
 for p in extras:
  r=bind(p);rows[r['path']]=r
 for r in rows.values():assert hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256']
 remaining=list(old['remaining_obligations']);remaining.insert(3,'Integrate frozen typed host routing into successor signed policy schema and actual host; closed routing shape alone supplies no permission or qualified handler.')
 v={**old,'parent_progress_binding':bind(parent),'files':[rows[k] for k in sorted(rows)],'change':'One original backend authority refusal remains unreinterpreted under typed scope hypothesis. Frozen exact internal typed routing schema/design passes8 offline shape cases. Original API46 cases14/15 are frozen and serialized after the same live CPU diagnostic; no successor runtime result is claimed.',
 'additional_original_backend_refusal_binding':bind(RUN/'typed-scope-other-backend-refusal-0001.json'),'additional_original_backend_refusal_cases':1,'typed_host_routing_source_binding':bind(package/'source-manifest.json'),'typed_host_routing_shape_proof_binding':bind(RUN/'typed-host-routing-shape-checks-0001.json'),'typed_host_routing_shape_cases':8,'typed_host_routing_registered_public_handler':False,'successor_original_case_selection_binding':bind(RUN/'API46-core-schema-selection-0001.json'),'successor_original_case_runner_binding':bind(RUN/'verify-API46-core-schema-original-cases-0001.py'),'successor_original_case_serial_driver_binding':bind(RUN/'run-API46-core-schema-after-diagnostic-0001.py'),'successor_original_case_result_established':False,'remaining_obligations':remaining,'claim_ceiling':'Scoped routing shape and one pure original-backend authority refusal check only, alongside inherited144 pure cases and retained API45 failures. No public typed handler, successor runtime qualification, actual grant, genuine participant evidence, owner outcome or admission.'}
 path=API/'receipts/R03-0082.json';put(path,v)
 print(json.dumps({'result':'PASS','progress_binding':bind(path),'bound_files':len(rows),'original_refusal_cases':1,'routing_shape_cases':8,'task_complete':False}),flush=True)
if __name__=='__main__':main()
