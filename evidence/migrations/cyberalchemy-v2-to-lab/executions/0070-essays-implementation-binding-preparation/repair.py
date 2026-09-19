"""Prepare a conservative successor, preserving unverified semantic mappings. See README.md."""
import json,hashlib,shutil,subprocess,os
from pathlib import Path
R=Path.cwd();H=R/'evidence/migrations/cyberalchemy-v2-to-lab/executions/0070-essays-implementation-binding-preparation';W=R/'.local/essays-binding-package-0070';S=R/'.local/essays-binding-successor-0070';BASE='cyberAlchemy-v2/essays/development/agent-runtime/';P=BASE+'conformance/implementation-binding';r=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
shutil.copytree(W,S,dirs_exist_ok=True,ignore=shutil.ignore_patterns('target','__pycache__'))
subprocess.run(['python3',str(S/P/'scripts/materialize_manifest.py')],check=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
b=r(S/P/'BINDING.json');old=r(W/P/'BINDING.json');manifest=r(S/P/'IMPLEMENTATION-MANIFEST.json');files={x['path'] for x in manifest['files']};nodes={x['id'] for x in r(S/BASE/'domainspec/generated/system-ontology.json')['system_nodes']}
deps={'domainspec_predecessors_sha256':BASE+'domainspec/PREDECESSORS.json','compile_receipt_sha256':BASE+'domainspec/generated/compile-receipt.json','compiled_graph_sha256':BASE+'domainspec/generated/domain.graph.json','system_ontology_sha256':BASE+'domainspec/generated/system-ontology.json','obligation_registry_sha256':'cyberAlchemy-v2/essays/capabilities/agent-runtime/obligations/agent-runtime.obligations.json','conformance_bridge_profile_sha256':BASE+'conformance/bridge-ontology/PROFILE.json','conformance_bridge_coverage_sha256':BASE+'conformance/bridge-ontology/COVERAGE.json','conformance_bridge_residue_sha256':BASE+'conformance/bridge-ontology/RESIDUE.json'}
for k,p in deps.items():b['dependency_digests'][k]=sha(S/p)
b['dependency_digests']['source_manifest_sha256']=r(S/BASE/'domainspec/generated/compile-receipt.json')['source_manifest_sha256']
removed=[]
for surface in b['implementation_surfaces']:
 for node in surface['system_nodes']:
  if node not in nodes:removed.append({'surface_id':surface['surface_id'],'node':node})
 surface['system_nodes']=[n for n in surface['system_nodes'] if n in nodes];surface['files']=[f for f in surface['files'] if f in files];surface['posture']='partial-unverified-current-snapshot'
unmapped_nodes=sorted(nodes-{n for s in b['implementation_surfaces'] for n in s['system_nodes']});unmapped_files=sorted(files-{f for s in b['implementation_surfaces'] for f in s['files']})
b['implementation_surfaces'].append({'surface_id':'unassigned-current-source-files','posture':'inventory-only-semantic-mapping-pending','files':unmapped_files,'system_nodes':[],'obligations':[]})
b['implementation_surfaces'].append({'surface_id':'unmapped-current-model-nodes','posture':'unsupported-semantic-mapping-pending','files':[],'system_nodes':unmapped_nodes,'obligations':[]})
dump(S/P/'BINDING.json',b)
t=r(S/P/'TRACEABILITY.json')
for e in t['entries']:e['posture']='partial';e['system_nodes']=[n for n in e['system_nodes'] if n in nodes];e['implementation']=[f for f in e['implementation'] if f in files]
dump(S/P/'TRACEABILITY.json',t)
for name in ['BINDING.json','TRACEABILITY.json','IMPLEMENTATION-MANIFEST.json']:dump(H/'successor'/name,r(S/P/name))
c=subprocess.run(['python3',str(S/P/'scripts/validate.py')],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'});dump(H/'successor-validation.json',{'exit_code':c.returncode,'stdout':c.stdout,'stderr':c.stderr});assert c.returncode==0
report={'authority_effect':'none','imported':False,'original_errors':r(H/'source-validation.json')['stdout'],'changed_files':['BINDING.json','TRACEABILITY.json','IMPLEMENTATION-MANIFEST.json'],'changed_dependency_keys':[k for k,v in b['dependency_digests'].items() if old['dependency_digests'].get(k)!=v],'removed_invalid_surface_references':removed,'unassigned_files':unmapped_files,'unmapped_system_nodes':unmapped_nodes,'trace_posture':'All twenty rows conservatively partial; old complete and unsupported claims are not treated as current evidence.','semantic_mapping':'Unassigned files and nodes are explicitly separate; set coverage is not semantic realization.','historical_residue':'All fourteen original statements retained without endorsement as current facts.','blockers':['Pinned Rust 1.94.0 installation incomplete; local tests cannot start.','Seven current model nodes need supported semantic mappings; inventory placeholders do not supply them.','Sixteen additional implementation files require classification beyond inventory membership.'],'next':'Repair the existing pinned toolchain, run the local runtime checks, then map the remaining source files and model nodes using actual evidence.'};dump(H/'repair-report.json',report)
print(c.stdout)
