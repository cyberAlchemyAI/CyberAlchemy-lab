"""Bind prepared-open API65 to a genuinely new durable installed source family."""
import ast,hashlib,json,os,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
OLD=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v65-t16-prepared-open-0001'
NEW=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v66-t16-durable-open-0001'
OLD_FAMILY=ROOT/'implementation/lab-runtime/local-host/t16-abi-coherent-successor-0001/instances/legacy-local-e084574c6d149cf0'
FAMILY=ROOT/'implementation/lab-runtime/local-host/t16-durable-abi-successor-0002/instances/legacy-local-83f9427adb0c1e65'
SOURCE_SHA='4736074040fab7e5d0a1f7902c11cdfc799fddcba5ca27f750ad711dba124731'
PROFILE_SHA='f5bedc77377c4a5d3f46e1478c21bea5162ed02861f4ce5c5bbe4641c5221392'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
enc=lambda v:(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def binding(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)}
def methods(path):
 out={}
 for p in [*path.glob('test_*.py'),*path.glob('run_*checks.py')]:
  for c in ast.parse(p.read_text()).body:
   if isinstance(c,ast.ClassDef):
    for n in c.body:
     if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name.startswith('test_'):out[p.name+':'+c.name+'.'+n.name]=ast.dump(n,include_attributes=False)
 return out

def main():
 os.umask(0o077)
 if NEW.exists() or sha(OLD/'source-manifest.json')!=SOURCE_SHA or sha(OLD/'contract-profile.json')!=PROFILE_SHA:raise ValueError('predecessor differs or successor exists')
 for phase in ('source','cold','reader','mapped','context'):
  if not (FAMILY/(phase+'-result.json')).is_file():raise ValueError('new family phase absent: '+phase)
 profile=json.loads((OLD/'contract-profile.json').read_bytes());source=json.loads((OLD/'source-manifest.json').read_bytes())
 digest_map={}
 for p in OLD_FAMILY.rglob('*'):
  dest=FAMILY/p.relative_to(OLD_FAMILY)
  if not p.is_file() or not dest.is_file() or '__pycache__' in p.parts:continue
  a,b=sha(p),sha(dest)
  if a in digest_map and digest_map[a]!=b:raise ValueError('ambiguous family digest map')
  digest_map[a]=b
 old_period=json.loads((OLD_FAMILY/'source/packages/0001/period.json').read_bytes());period=json.loads((FAMILY/'source/packages/0001/period.json').read_bytes())
 replacements={OLD.name:NEW.name,str(OLD_FAMILY.relative_to(ROOT)):str(FAMILY.relative_to(ROOT)),OLD_FAMILY.name:FAMILY.name,'_cal_api65_t16_':'_cal_api66_t16_',**digest_map}
 for key in ('not_before','expires_at'):replacements[old_period[key]]=period[key]
 shutil.copytree(OLD,NEW,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 for p in NEW.rglob('*'):
  if not p.is_file() or p.name in ('source-manifest.json','contract-profile.json','rebind-receipt.json','INPUT-ACCOUNTING.json','SCHEMA-EXECUTION-DEPENDENCIES.json'):continue
  try:s=p.read_text()
  except UnicodeError:continue
  for a,b in replacements.items():s=s.replace(a,b)
  if p.name=='current_legacy_context_sessions.py':
   seal_helper = """from dataclasses import fields as _plan_fields
from datetime import datetime as _PlanDatetime

def _open_plan_digest(value):
    # Closed typed encoding: eligibility plans contain SourceRecord originals
    # and aware datetime values as well as ordinary JSON fields. They are
    # private objects, never accepted from a serialized API caller.
    def frozen(item):
        if item is None:return ['null']
        if type(item) in (str,bool,int):return [type(item).__name__,item]
        if type(item) is bytes:return ['bytes-sha256',source.sha(item)]
        if type(item) is _PlanDatetime:
            source.require(item.tzinfo is not None,'aware prepared plan time required')
            return ['datetime',item.isoformat()]
        if type(item) in (list,tuple):return [type(item).__name__,[frozen(v) for v in item]]
        if type(item) is dict:
            source.require(all(type(k) is str for k in item),'prepared plan key type differs')
            return ['dict',[[k,frozen(item[k])] for k in sorted(item)]]
        source.require(type(item) in (EL.SourceRecord,EL.SignedRevisionWitness),
            'unselected prepared plan object type')
        return ['record',type(item).__name__,[[f.name,frozen(getattr(item,f.name))] for f in _plan_fields(item)]]
    return source.sha(compact(frozen(value)))

"""
   s=s.replace('class ContextSessions:',seal_helper+'class ContextSessions:',1)
   s=s.replace('source.sha(compact(package))','_open_plan_digest(package)').replace('source.sha(compact(plan))','_open_plan_digest(plan)')
   s=s.replace("            self._prepared_open=(package,_open_plan_digest(package))\n            return package","        with self.mutex:\n            pending=getattr(self,'_prepared_opens',None)\n            if pending is None:self._prepared_opens=pending={}\n            key=(request['ref'],request['sha256'])\n            source.require(key not in pending and len(pending)<32,'prepared Session plan budget or duplicate request')\n            pending[key]=(package,_open_plan_digest(package))\n        return package")
   s=s.replace("            selected=getattr(self,'_prepared_open',None)","            pending=getattr(self,'_prepared_opens',{})\n            key=(request['ref'],request['sha256'])\n            selected=pending.get(key)")
   s=s.replace("            del self._prepared_open","            del pending[key]")
   s=s.replace("            self.timers.clear();self.closed=True;self.lease.close()","            getattr(self,'_prepared_opens',{}).clear()\n            self.timers.clear();self.closed=True;self.lease.close()")
   s=s.replace("    def open_plan(self,*args,**kwargs):\n","    def prepared_open_plan(self,*args,**kwargs):\n        raise ApplicationError('unauthorized','Machine read transport cannot prepare another Session.')\n    def open_plan(self,*args,**kwargs):\n")
   # Only JSON-safe immutable facts enter the prepared byte seal. The signed
   # private policy is re-read before commit by termination_guard and delivery.
   s=s.replace("'permission':self.bridge.permission(),'message_sha256':", "'policy_sha256':self.channel.expected_sha,'message_sha256':")
   s=s.replace("self.channel.termination_guard()\n            source.require(self.channel.policy", "self.channel.termination_guard()\n            source.require(plan['policy_sha256']==self.channel.expected_sha,'prepared private policy changed')\n            source.require(self.channel.policy")
  if p.suffix=='.py':ast.parse(s)
  if p.suffix=='.json':json.loads(s)
  p.write_text(s)
 def recut(row):
  oldprefix=OLD.relative_to(ROOT).as_posix()+'/'
  family_prefix=OLD_FAMILY.relative_to(ROOT).as_posix()+'/'
  if row['path'].startswith(oldprefix):return binding(NEW/row['path'][len(oldprefix):])
  if row['path'].startswith(family_prefix):return binding(FAMILY/row['path'][len(family_prefix):])
  return row
 profile['files']=sorted([recut(row) for row in profile['files']],key=lambda r:r['path'])
 for k,v in list(profile.items()):
  if k!='files' and isinstance(v,dict) and set(v)=={'path','sha256'}:profile[k]=recut(v)
 profile['claim_ceiling']='Fresh durable installed 4.23 signed-family and prepared Session-open local candidate; inherited qualification pending.'
 (NEW/'contract-profile.json').write_bytes(enc(profile))
 source['files']=sorted([recut(row) for row in source['files']],key=lambda r:r['path'])
 for k,v in list(source.items()):
  if k!='files' and isinstance(v,dict) and set(v)=={'path','sha256'}:source[k]=recut(v)
 source['profile_binding']=binding(NEW/'contract-profile.json');source['predecessor_source_manifest_binding']=binding(OLD/'source-manifest.json')
 (NEW/'source-manifest.json').write_bytes(enc(source))
 receipt={'schema_version':'lab-T16-durable-open/v1-candidate','successor_package':NEW.relative_to(ROOT).as_posix(),'successor_manifest_sha256':sha(NEW/'source-manifest.json'),'successor_source_binding':binding(NEW/'source-manifest.json'),'successor_profile_binding':binding(NEW/'contract-profile.json'),'predecessor_source_binding':binding(OLD/'source-manifest.json'),'fresh_family_source_binding':binding(FAMILY/'source/source-manifest.json'),'fresh_family_context_binding':binding(FAMILY/'context/source-manifest.json'),'authority_effect':'none','t16_qualified':False}
 (NEW/'rebind-receipt.json').write_bytes(enc(receipt))
 before=methods(OLD);after=methods(NEW)
 if before!=after:raise ValueError('inherited test method AST changed')
 print(json.dumps({'receipt':receipt,'inherited_method_asts_unchanged':len(before)},sort_keys=True))
if __name__=='__main__':main()
