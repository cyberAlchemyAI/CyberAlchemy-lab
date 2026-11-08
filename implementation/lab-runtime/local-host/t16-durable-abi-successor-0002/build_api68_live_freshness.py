"""Keep full Session preclaim proof; deduplicate live-reader source verification."""
import ast,hashlib,json,os,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
OLD=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v67-t16-sealed-memory-open-0001'
NEW=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v68-t16-live-source-freshness-0001'
SOURCE='4ae02060e690e7acd1f355d149177b8fca8a1ab42067290dae70dd38eb27f8af'
PROFILE='b7244c3f12405fe15b9173d463e8056e96eb22e4954ef0b8e118d35a7ee7f46a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
enc=lambda x:(json.dumps(x,sort_keys=True,indent=2)+'\n').encode()
def binding(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)}
def main():
 os.umask(0o077)
 if NEW.exists() or sha(OLD/'source-manifest.json')!=SOURCE or sha(OLD/'contract-profile.json')!=PROFILE:raise ValueError('selected predecessor differs or successor exists')
 source=json.loads((OLD/'source-manifest.json').read_bytes());profile=json.loads((OLD/'contract-profile.json').read_bytes());shutil.copytree(OLD,NEW,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 p=NEW/'current_legacy_context_sessions.py';s=p.read_text()
 needle='        self.path=channel.path;self.connection=channel.connection'
 if s.count(needle)!=1:raise ValueError('PermissionBridge constructor differs')
 s=s.replace(needle,needle+'''
        # ContextSessions establishes the full signed proof before constructing
        # this bridge. Preserve exact private captured facts; every live guard
        # rereads all physical family/baseline bytes and actual permission.
        from .session_source_freshness import fresh_selected_source,captured_source_basis
        self._live_source_basis=copy.deepcopy(captured_source_basis(selected))
        self._live_family=copy.deepcopy(fresh_selected_source(selected))
''')
 needle='    def actor(self):\n'
 live='''    def live_guard(self):
        from .session_source_freshness import fresh_selected_source,captured_source_basis
        source.require(captured_source_basis(self.source)==self._live_source_basis,
            'captured Session source facts changed')
        fresh_selected_source(self.source,self._live_family)
        from .auth import ReaderChannel
        # Source-independent termination guard still reopens the exact policy,
        # checks its period/revocation, authenticated principal and actual UTC.
        # Machine channels keep their independently authenticated full guard.
        current=(self.channel.termination_guard() if type(self.channel) is ReaderChannel
                 else self.channel.guard())
        return copy.deepcopy(current)
'''
 if s.count(needle)!=1:raise ValueError('PermissionBridge actor differs')
 s=s.replace(needle,live+needle)
 needle="        source.require(not self.closed,'Session is closed');self.bridge.guard()"
 if s.count(needle)!=1:raise ValueError('LiveReader guard differs')
 s=s.replace(needle,"        source.require(not self.closed,'Session is closed');self.bridge.live_guard()")
 needle="        self.bridge.guard();source.require(set(wanted)=={'ref','sha256'}"
 if s.count(needle)!=1:raise ValueError('delivery guard differs')
 s=s.replace(needle,"        self.bridge.live_guard();source.require(set(wanted)=={'ref','sha256'}")
 ast.parse(s);p.write_text(s)
 for name in ('source_bridge.py','workflow_output_registry.py'):
  p=NEW/name;p.write_text(p.read_text().replace(OLD.name,NEW.name).replace('_cal_api67_t16_','_cal_api68_t16_'))
 for p in [*OLD.glob('test_*.py'),*OLD.glob('run_*checks.py')]:
  if sha(p)!=sha(NEW/p.name):raise ValueError('inherited test bytes changed')
 prefix=OLD.relative_to(ROOT).as_posix()+'/'
 def recut(row):return binding(NEW/row['path'][len(prefix):]) if row['path'].startswith(prefix) else row
 profile['files']=sorted([recut(r) for r in profile['files']],key=lambda r:r['path'])
 for k,v in list(profile.items()):
  if k!='files' and isinstance(v,dict) and set(v)=={'path','sha256'}:profile[k]=recut(v)
 (NEW/'contract-profile.json').write_bytes(enc(profile));source['files']=sorted([recut(r) for r in source['files']],key=lambda r:r['path']);source['profile_binding']=binding(NEW/'contract-profile.json');source['predecessor_source_manifest_binding']=binding(OLD/'source-manifest.json');(NEW/'source-manifest.json').write_bytes(enc(source))
 receipt={'schema_version':'lab-T16-live-source-freshness/v1-candidate','successor_package':NEW.relative_to(ROOT).as_posix(),'successor_manifest_sha256':sha(NEW/'source-manifest.json'),'successor_source_binding':binding(NEW/'source-manifest.json'),'successor_profile_binding':binding(NEW/'contract-profile.json'),'predecessor_source_binding':binding(OLD/'source-manifest.json'),'authority_effect':'none','t16_qualified':False}
 (NEW/'rebind-receipt.json').write_bytes(enc(receipt));print(json.dumps(receipt,sort_keys=True))
if __name__=='__main__':main()
