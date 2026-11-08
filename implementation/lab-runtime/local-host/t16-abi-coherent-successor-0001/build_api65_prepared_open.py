"""Prepare exact Session metadata once; recheck physical and live facts at commit."""
import ast, hashlib, json, os, shutil, textwrap
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
OLD=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v64-t16-abi423-disposition-0001'
NEW=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v65-t16-prepared-open-0001'
T22=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v60-t22-pinned-family-source-0001'
OLD_SOURCE='440f21c46ec20910e371765c32152bb0a18efead7a147724b762a0a46965a675'
OLD_PROFILE='a4c08349d84a5f8f654eda62fa5ec109ffd6610b5fe8aa474e2197f101aaaf71'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
enc=lambda x:(json.dumps(x,sort_keys=True,indent=2)+'\n').encode()
def binding(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)}
def main():
 os.umask(0o077)
 if NEW.exists() or sha(OLD/'source-manifest.json')!=OLD_SOURCE or sha(OLD/'contract-profile.json')!=OLD_PROFILE:raise ValueError('predecessor differs or successor exists')
 profile=json.loads((OLD/'contract-profile.json').read_bytes());source=json.loads((OLD/'source-manifest.json').read_bytes())
 shutil.copytree(OLD,NEW,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 runtime=NEW/'current_legacy_context_sessions.py';body=runtime.read_text()
 tree=ast.parse(body);cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ContextSessions')
 funcs={n.name:n for n in cls.body if isinstance(n,ast.FunctionDef)}
 original_open=ast.get_source_segment(body,funcs['open'])
 # Metadata construction remains in the exact original sealed fact scope.
 start=original_open.index('                sid,aid=self.allocate_runtime_identities()')
 stop=original_open.index('            # Scope exit')
 construction=textwrap.dedent(original_open[start:stop])
 construction=construction.replace('plan[\'expires_at\']','prepared[\'expires_at\']')
 prepare='''    def prepared_open_plan(self,message,outer,request,raw):
        with BOUNDARIES.read_scope(self.source,EL,self.bridge,producer=D,
                                     package_checks=[(D.verify_source,DELIVERY_PIN)]) as snapshot:
            captured=[]
            def delivered(wanted):
                proof=self.delivery(wanted);captured.append(proof);return proof
            prepared=self._open_plan(message,outer,snapshot,delivered)
            source.require(len(captured)==1,'opening must consume one original delivery')
            proof=captured[0]
'''+textwrap.indent(construction,'            ')+'''            from .session_source_freshness import fresh_selected_source
            family=fresh_selected_source(self.source)
            package={'plan':copy.deepcopy(prepared),'proof':copy.deepcopy(proof),
                'permission':self.bridge.permission(),'message_sha256':source.sha(compact(message)),
                'request':copy.deepcopy(request),'raw_sha256':source.sha(raw),
                'family':family,'sid':sid,'aid':aid,'started':started,
                'agent':agent,'session':session,'classification':classification,
                'connections':connections,'result':result,'source_cut':copy.deepcopy(outer)}
            self._prepared_open=(package,source.sha(compact(package)))
            return package
'''
 commit='''    def open(self,message,request,outer,raw,plan):
        with self.mutex:
            source.require(not self.closed and len(self.live)<32,'Session resource budget exhausted')
            selected=getattr(self,'_prepared_open',None)
            source.require(type(selected) is tuple and selected[0] is plan
                and selected[1]==source.sha(compact(plan)),'unselected or changed preclaim Session plan')
            del self._prepared_open
            source.require(plan['message_sha256']==source.sha(compact(message))
                and plan['request']==request and plan['raw_sha256']==source.sha(raw)
                and plan['source_cut']==outer==self.source.source_cut,'prepared Session inputs changed')
            self.channel.termination_guard()
            source.require(self.channel.policy['principal_ref']==self.channel.context['principal_ref'],
                'Session principal changed')
            from .session_source_freshness import fresh_selected_source
            fresh_selected_source(self.source,plan['family'])
            current=self.delivery(message['context_delivery_binding'])
            source.require(current==plan['proof'],'selected original delivery changed')
            source.require(now()<instant(plan['plan']['expires_at'])
                and now()<instant(current['expires_at']),'Session or delivery expired before allocation')
            # No live resource or write occurs until all fresh checks above pass.
            D.FACT_SCOPE.require_outside_scope()
            sid=plan['sid'];aid=plan['aid'];started=plan['started']
            agent=plan['agent'];session=plan['session'];classification=plan['classification']
            result=plan['result'];connections=plan['connections'];proof=plan['proof']
            self.reserve_runtime_identities(sid,aid,request)
            resource=LiveReader(self.source,self.bridge,plan['plan'],proof,agent,session,classification)
            try:
                resource.guard()
                source.require(now()<resource.expires,'Session expired before persist')
                self.persist(sid,aid,message['assignment'],outer,started,None,'active',False,result,agent,classification,connections)
                self.live[sid]=resource
                timer=threading.Timer(max(0,(resource.expires-now()).total_seconds()),self.expire,args=(sid,))
                timer.daemon=True;self.timers[sid]=timer;timer.start()
                return copy.deepcopy(result),[]
            except BaseException:resource.dispose();raise
'''
 lines=body.splitlines(keepends=True)
 a=funcs['open'].lineno-1;b=funcs['open'].end_lineno
 lines[a:b]=[prepare+'\n'+commit]
 body=''.join(lines);ast.parse(body);runtime.write_text(body)
 # Reuse the audited physical closure verifier as a private module, not the T22 Machine behavior.
 donor=(T22/'machine_transport.py').read_text();node=next(n for n in ast.parse(donor).body if isinstance(n,ast.FunctionDef) and n.name=='fresh_selected_source')
 helper='"""Complete exact signed-family and baseline freshness at Session commit."""\nimport hashlib\nfrom pathlib import Path\nROOT=Path(__file__).resolve().parents[6]\ndef require(value,reason):\n    if not value:raise ValueError(reason)\n\n'+ast.get_source_segment(donor,node)+'\n'
 ast.parse(helper);(NEW/'session_source_freshness.py').write_text(helper)
 service=NEW/'service.py';body=service.read_text();needle="if name=='session.open':session_plan=self.sessions.open_plan(message,call['expected_source_cut'])"
 replacement="if name=='session.open':\n                        prepare=getattr(self.sessions,'prepared_open_plan',None)\n                        session_plan=(prepare(message,call['expected_source_cut'],request,inner) if prepare is not None\n                            else self.sessions.open_plan(message,call['expected_source_cut']))"
 if body.count(needle)!=1:raise ValueError('Session prepare call inventory differs')
 body=body.replace(needle,replacement);ast.parse(body);service.write_text(body)
 for name in ('source_bridge.py','workflow_output_registry.py'):
  p=NEW/name;s=p.read_text().replace(OLD.name,NEW.name).replace('_cal_api64_t16_','_cal_api65_t16_');ast.parse(s);p.write_text(s)
 for p in [*OLD.glob('test_*.py'),*OLD.glob('run_*checks.py')]:
  if sha(p)!=sha(NEW/p.name):raise ValueError('inherited test bytes changed')
 prefix=OLD.relative_to(ROOT).as_posix()+'/'
 def recut(row):return binding(NEW/row['path'][len(prefix):]) if row['path'].startswith(prefix) else row
 profile['files']=sorted([recut(row) for row in profile['files']]+[binding(NEW/'session_source_freshness.py')],key=lambda r:r['path'])
 for k,v in list(profile.items()):
  if k!='files' and isinstance(v,dict) and set(v)=={'path','sha256'}:profile[k]=recut(v)
 profile['claim_ceiling']='Local prepared Session-open candidate; full inherited regression pending.'
 (NEW/'contract-profile.json').write_bytes(enc(profile))
 source['files']=sorted([recut(row) for row in source['files']]+[binding(NEW/'session_source_freshness.py')],key=lambda r:r['path'])
 source['profile_binding']=binding(NEW/'contract-profile.json');source['predecessor_source_manifest_binding']=binding(OLD/'source-manifest.json')
 source['claim_ceiling']='Session-open metadata prepared once with exact pre-effect freshness; inherited qualification pending.'
 (NEW/'source-manifest.json').write_bytes(enc(source))
 receipt={'schema_version':'lab-T16-prepared-open/v1-candidate','predecessor_source_binding':binding(OLD/'source-manifest.json'),'successor_source_binding':binding(NEW/'source-manifest.json'),'successor_package':NEW.relative_to(ROOT).as_posix(),'successor_manifest_sha256':sha(NEW/'source-manifest.json'),'successor_profile_binding':binding(NEW/'contract-profile.json'),'authority_effect':'none','t16_qualified':False,'inherited_test_files_byte_identical':True}
 (NEW/'rebind-receipt.json').write_bytes(enc(receipt));print(json.dumps(receipt,sort_keys=True))
if __name__=='__main__':main()
