"""One complete Reader source proof per Session-open call; fresh effect guards."""
import ast,hashlib,json,os,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
OLD=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v68-t16-live-source-freshness-0001'
NEW=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v69-t16-call-source-scope-0001'
SOURCE='f91edcdba7cb8141405c0931369af02bc6d05c90f03c5cac77ae72165d7e6cb2'
PROFILE='ba389526fa3e9e1c9d840632d3b1c038fcc4a648c4e0ed1767b85fe2cf7c0355'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
enc=lambda x:(json.dumps(x,sort_keys=True,indent=2)+'\n').encode()
def binding(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)}
def main():
 os.umask(0o077)
 if NEW.exists() or sha(OLD/'source-manifest.json')!=SOURCE or sha(OLD/'contract-profile.json')!=PROFILE:raise ValueError('selected predecessor differs or successor exists')
 source=json.loads((OLD/'source-manifest.json').read_bytes());profile=json.loads((OLD/'contract-profile.json').read_bytes());shutil.copytree(OLD,NEW,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 p=NEW/'auth.py';s=p.read_text();s=s.replace('import base64\n','import base64\nimport threading\nfrom contextlib import contextmanager\n',1)
 needle='        self.termination_basis=None'
 if s.count(needle)!=1:raise ValueError('Reader constructor inventory differs')
 s=s.replace(needle,needle+'\n        self._source_call_local=threading.local()')
 needle="    def guard(self):\n        if getattr(self,'bound_termination_call',False):return self.termination_guard()"
 replacement="""    @contextmanager
    def verified_source_call(self,bridge):
        # Only Service's selected current-legacy Session-open branch owns this
        # private scope. Source facts, not permission, are reused within it.
        source.require(type(self) is ReaderChannel and bridge.channel is self,
            'selected Reader source-call scope required')
        source.require(getattr(self._source_call_local,'value',None) is None,
            'source-call scope cannot nest')
        try:
            original=self.guard()  # complete original proof before registration
            bridge.live_guard()   # independent captured/physical source basis
        except Exception:
            yield False
            return
        state={'bridge':bridge,'context':copy.deepcopy(original),
               'connection':self.connection,'policy_sha256':self.expected_sha}
        self._source_call_local.value=state
        try:yield True
        finally:
            # Nothing survives this call, including exceptional effect paths.
            if hasattr(self._source_call_local,'value'):del self._source_call_local.value
    def guard(self):
        if getattr(self,'bound_termination_call',False):return self.termination_guard()
        state=getattr(self._source_call_local,'value',None)
        if state is not None:
            source.require(self.connection==state['connection']
                and self.expected_sha==state['policy_sha256']
                and self.context==state['context'],'authenticated source-call context changed')
            current=state['bridge'].live_guard()
            source.require(current==state['context'],'fresh permission changed authenticated context')
            return copy.deepcopy(current)"""
 if s.count(needle)!=1:raise ValueError('Reader full guard inventory differs')
 s=s.replace(needle,replacement);ast.parse(s);p.write_text(s)
 p=NEW/'service.py';s=p.read_text()
 needle="        try:return self._call(raw)\n        finally:self.channel.bound_termination_call=False"
 replacement="""        try:
            from .auth import ReaderChannel
            selected_open=(isinstance(parsed,dict) and parsed.get('operation')=='session.open'
                and type(self.channel) is ReaderChannel
                and self.channel.policy['schema_version']=='lab-local-candidate-policy/v4-candidate'
                and self.channel.policy['source_name'] in (source.CURRENT_LEGACY_NAME,'custody-participation')
                and self.sessions is not None
                and type(self.sessions).__module__==__package__+'.current_legacy_context_sessions'
                and type(self.sessions).__name__=='ContextSessions'
                and self.sessions.bridge.channel is self.channel)
            if selected_open:
                with self.channel.verified_source_call(self.sessions.bridge) as verified:
                    if not verified:
                        try:self.sessions.dispose_all()
                        except Exception:pass
                        return transport('unauthenticated-channel',raw)
                    return self._call(raw)
            return self._call(raw)
        finally:self.channel.bound_termination_call=False"""
 if s.count(needle)!=1:raise ValueError('Service call boundary differs')
 s=s.replace(needle,replacement);ast.parse(s);p.write_text(s)
 for name in ('source_bridge.py','workflow_output_registry.py'):
  p=NEW/name;p.write_text(p.read_text().replace(OLD.name,NEW.name).replace('_cal_api68_t16_','_cal_api69_t16_'))
 for p in [*OLD.glob('test_*.py'),*OLD.glob('run_*checks.py')]:
  if sha(p)!=sha(NEW/p.name):raise ValueError('inherited test bytes changed')
 prefix=OLD.relative_to(ROOT).as_posix()+'/'
 def recut(row):return binding(NEW/row['path'][len(prefix):]) if row['path'].startswith(prefix) else row
 profile['files']=sorted([recut(r) for r in profile['files']],key=lambda r:r['path'])
 for k,v in list(profile.items()):
  if k!='files' and isinstance(v,dict) and set(v)=={'path','sha256'}:profile[k]=recut(v)
 (NEW/'contract-profile.json').write_bytes(enc(profile));source['files']=sorted([recut(r) for r in source['files']],key=lambda r:r['path']);source['profile_binding']=binding(NEW/'contract-profile.json');source['predecessor_source_manifest_binding']=binding(OLD/'source-manifest.json');(NEW/'source-manifest.json').write_bytes(enc(source))
 receipt={'schema_version':'lab-T16-call-source-scope/v1-candidate','successor_package':NEW.relative_to(ROOT).as_posix(),'successor_manifest_sha256':sha(NEW/'source-manifest.json'),'successor_source_binding':binding(NEW/'source-manifest.json'),'successor_profile_binding':binding(NEW/'contract-profile.json'),'predecessor_source_binding':binding(OLD/'source-manifest.json'),'authority_effect':'none','t16_qualified':False}
 (NEW/'rebind-receipt.json').write_bytes(enc(receipt));print(json.dumps(receipt,sort_keys=True))
if __name__=='__main__':main()
