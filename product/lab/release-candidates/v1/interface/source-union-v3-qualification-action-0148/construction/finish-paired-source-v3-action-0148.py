from pathlib import Path
import hashlib,json
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');I=ROOT/'product/lab/release-candidates/v1/interface';API=I/'api-session-source-v3-action-0148'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
def load(p):return json.loads(p.read_bytes())
def put(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
p=API/'handlers.py';s=p.read_text();old="        if hasattr(self.view,'fresh_signed_sources'):self.view.fresh_signed_sources.guard()"
new="""        # Deduplicate only the same actual source outside any borrowed pure
        # scope: parent_guard just ran its full fresh original callback. Inside
        # a scope preserve the original fresh.guard; distinct sources also keep
        # both original obligations. No result survives this invocation.
        same_full_source=(FACT_SCOPE.active_scope() is None
            and hasattr(self.view,'custody_signed_sources')
            and hasattr(self.view,'fresh_signed_sources')
            and self.view.fresh_signed_sources is self.view.custody_signed_sources)
        if hasattr(self.view,'fresh_signed_sources') and not same_full_source:self.view.fresh_signed_sources.guard()"""
assert old in s;s=s.replace(old,new);p.write_text(s)
e=load(API/'SCHEMA-EXECUTION-DEPENDENCIES.json');e['files']=[bind(ROOT/r['path']) if r['path'].startswith(str(API.relative_to(ROOT))+'/') else r for r in e['files']];put(API/'SCHEMA-EXECUTION-DEPENDENCIES.json',e)
p=load(API/'contract-profile.json');p['files']=[bind(ROOT/r['path']) if r['path'].startswith(str(API.relative_to(ROOT))+'/') else r for r in p['files']];p['schema_execution_dependency_binding']=bind(API/'SCHEMA-EXECUTION-DEPENDENCIES.json');put(API/'contract-profile.json',p)
m=load(API/'source-manifest.json');m['files']=[bind(ROOT/r['path']) if r['path'].startswith(str(API.relative_to(ROOT))+'/') else r for r in m['files']];m['same_source_alias_deduplication']='Only exact same object outside any registered pure scope; original full parent callback just performed fresh proof, native handle/freshness always retained.';put(API/'source-manifest.json',m)
print(json.dumps({'source':bind(API/'source-manifest.json'),'profile':bind(API/'contract-profile.json'),'handlers':bind(API/'handlers.py')},sort_keys=True))
