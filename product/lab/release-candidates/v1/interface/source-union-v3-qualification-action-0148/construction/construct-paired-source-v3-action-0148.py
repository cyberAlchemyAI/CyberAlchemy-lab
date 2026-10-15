from pathlib import Path
import hashlib,json,shutil
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');I=ROOT/'product/lab/release-candidates/v1/interface';OLD=I/'api-session-source-v2-action-0148';API=I/'api-session-source-v3-action-0148'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
def load(p):return json.loads(p.read_bytes())
def put(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def own(p):return [bind(x) for x in sorted(p.rglob('*')) if x.is_file() and x.name not in ('source-manifest.json','contract-profile.json','SCHEMA-EXECUTION-DEPENDENCIES.json')]
def union(*groups):
 d={}
 for group in groups:
  for r in group:
   assert r['path'] not in d or d[r['path']]==r
   d[r['path']]=r
 return [d[k] for k in sorted(d)]
shutil.copytree(OLD,API)
p=API/'custody_context_sessions.py';s=p.read_text();original="    def guard(self):D.FACT_SCOPE.parent_guard(self.source);return copy.deepcopy(self.channel.guard())"
paired=(I/'api-policy-source-boundaries-v1/custody_context_sessions.py').read_text();start=paired.index('    def guard(self):',paired.index('class PermissionBridge:'));end=paired.index('    def actor(self):',start)
assert original in s;s=s.replace(original,paired[start:end].rstrip());p.write_text(s)
e=load(API/'SCHEMA-EXECUTION-DEPENDENCIES.json');prefix=str(OLD.relative_to(ROOT))+'/'
e['files']=[bind(API/r['path'][len(prefix):]) if r['path'].startswith(prefix) else r for r in e['files']];e['selection_reasons']={r['path']:['Actual immutable schema/runtime code of source2 plus paired fresh authority API3.'] for r in e['files']};put(API/'SCHEMA-EXECUTION-DEPENDENCIES.json',e)
p=load(API/'contract-profile.json');p['files']=union(load(OLD/'contract-profile.json')['files'],own(API),[bind(API/'SCHEMA-EXECUTION-DEPENDENCIES.json')]);p['schema_execution_dependency_binding']=bind(API/'SCHEMA-EXECUTION-DEPENDENCIES.json');put(API/'contract-profile.json',p)
m=load(API/'source-manifest.json');m['files']=union(load(OLD/'source-manifest.json')['files'],own(API),[bind(API/'contract-profile.json'),bind(API/'SCHEMA-EXECUTION-DEPENDENCIES.json'),bind(OLD/'source-manifest.json')]);m['paired_actual_current_authority']='Fresh complete selectedsource proof followed by original exactReaderChannel source-independent privatepolicy/retainedperiod/nonce/UTC check; Machine original fullguard.';put(API/'source-manifest.json',m)
print(json.dumps({'source':bind(API/'source-manifest.json'),'profile':bind(API/'contract-profile.json')},sort_keys=True))
