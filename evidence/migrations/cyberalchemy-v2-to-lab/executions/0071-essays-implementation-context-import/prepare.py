"""Prepare source-backed mappings. Open questions: README.md."""
import json,shutil,hashlib,subprocess,os
from pathlib import Path
R=Path.cwd();H=R/'evidence/migrations/cyberalchemy-v2-to-lab/executions/0071-essays-implementation-context-import';W=R/'.local/essays-implementation-package-0071';BASE='cyberAlchemy-v2/essays/development/agent-runtime/';P=BASE+'conformance/implementation-binding';I=BASE+'implementation';r=lambda p:json.loads(p.read_text())
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
shutil.copytree(R/'.local/essays-binding-successor-0070',W,dirs_exist_ok=True,ignore=shutil.ignore_patterns('target','__pycache__'))
b=r(W/P/'BINDING.json');b['implementation_surfaces']=[s for s in b['implementation_surfaces'] if s['surface_id'] not in ['unassigned-current-source-files','unmapped-current-model-nodes']];surfaces={s['surface_id']:s for s in b['implementation_surfaces']}
classifications={'build-and-documentation':['IMPLEMENTATION-STATUS.md','rust-toolchain.toml'],'tauri-desktop-shell':['desktop/scripts/build-windows.ps1','desktop/scripts/dev-windows.ps1','desktop/scripts/setup-windows.ps1','desktop/src-tauri/Cargo.lock','desktop/src-tauri/icons/icon.ico','desktop/src-tauri/icons/icon.png','desktop/src-tauri/tauri.windows.conf.json','desktop/src-tauri/wdio/capabilities/wdio-smoke.json'],'local-framed-json':['src/bin/essays-ipc.rs'],'semantic-kernel-and-sqlite':['src/error.rs','src/platform.rs','src/security.rs'],'local-runtime-tests':['tests/TEST-CAMPAIGN.md','tests/windows_adapter.rs']}
for sid,files in classifications.items():surfaces[sid]['files']+=files
prefix='system:essays-agent-runtime:'
mappings=[('authenticated-principal','semantic-kernel-and-sqlite','src/store.rs','if !principal.is_verified()', 'Intake rejects an unverified principal.'),('context-sufficient','context-sufficiency-and-correction','src/model.rs','pub fn validate_for(', 'Context validation checks the operation, provenance and sufficiency.'),('effect-envelope-current','playwright-supervisor','src/model.rs','self.expires_at_unix_ms <= now_unix_ms','Effect grants reject expiry, revocation, replay and missing scope.'),('workspace-snapshot','semantic-kernel-and-sqlite','src/model.rs','pub struct WorkspaceSnapshot','Snapshot record represents qualified state.'),('proposal-accepted','semantic-kernel-and-sqlite','src/store.rs','"proposal-accepted"','Owner disposition records acceptance after advancing revision.'),('proposal-rejected','semantic-kernel-and-sqlite','src/store.rs','"proposal-rejected"','Rejection records an event without advancing revision.'),('reject-proposal','semantic-kernel-and-sqlite','src/store.rs','Command::RejectProposal','Reject command enters the owner-controlled disposition path.')]
evidence=[]
for node,sid,file,selector,meaning in mappings:
 text=(W/I/file).read_text();assert selector in text,(file,selector);s=surfaces[sid];s['system_nodes'].append(prefix+node)
 if file not in s['files']:s['files'].append(file)
 evidence.append({'system_node':prefix+node,'surface_id':sid,'file':file,'selector':selector,'sha256':hashlib.sha256((W/I/file).read_bytes()).hexdigest(),'meaning':meaning,'posture':'source-inspected-partial'})
surfaces['context-sufficiency-and-correction']['files']=['src/model.rs','src/store.rs'];surfaces['uncertain-effect-reconciliation']['files']=['src/model.rs','src/store.rs']
# Keep source-backed links partial even when local tests pass.
t=r(W/P/'TRACEABILITY.json');coverage=r(W/BASE/'conformance/bridge-ontology/COVERAGE.json')['coverage'];byob={x['obligation']:x for x in coverage}
for entry in t['entries']:
 entry['implementation']=sorted(set(entry['implementation'])|{f for f in byob[entry['obligation_id']]['implementation'] if not f.startswith('../')})
for s in b['implementation_surfaces']:s['files']=sorted(set(s['files']));s['system_nodes']=sorted(set(s['system_nodes']))
dump(W/P/'BINDING.json',b);dump(W/P/'TRACEABILITY.json',t);dump(H/'mapping-evidence.json',{'new_model_mappings':evidence,'file_classifications':classifications,'authority_effect':'none','claim_ceiling':'Source-inspected candidate mappings; no independent or cross-client conformance.'})
c=subprocess.run(['python3',str(W/P/'scripts/validate.py')],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'});dump(H/'source-validation.json',{'exit_code':c.returncode,'stdout':c.stdout,'stderr':c.stderr});assert c.returncode==0;print(c.stdout)
