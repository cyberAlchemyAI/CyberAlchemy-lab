"""Exact-statement proof submissions under an independently selected policy."""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]/'inference/integration'))
import integration as i
sys.path.insert(0, str(i.s.BASE/'replay'))
import replay_engine as replay
import isolation
s=i.s; g=i.g
MAX_SOURCE=1024*1024
SCHEMA='relational.proof-submission/v1-candidate'

MODULES=[
 ('RelationalInput','formal/core/RelationalInput.lean'),
 ('RelationalSemantics','formal/core/RelationalSemantics.lean'),
 ('SemanticLogic','formal/semantic-logic/v1/SemanticLogic.lean'),
 ('RegistryChecker','registry/RegistryChecker.lean'),
 ('Preservation','evolution/preservation/Preservation.lean'),
 ('ConservativeExpansion','evolution/models/ConservativeExpansion.lean'),
 ('InferenceCore','inference/derivations/InferenceCore.lean'),
 ('DerivationSoundness','inference/derivations/DerivationSoundness.lean'),
 ('ClosureAdequacy','inference/closure/ClosureAdequacy.lean'),
 ('ProtectedLineage','inference/protected/ProtectedLineage.lean'),
 ('ModelSemantics','inference/independence/ModelSemantics.lean'),
 ('RuleConservativity','inference/integration/RuleConservativity.lean')]
CATALOG={
 'invariant-preservation':('Preservation','Registry.Evolution.RequiredPreservation','definition-value'),
 'conservative-expansion':('ConservativeExpansion','Registry.Models.RequiredConservativity','definition-value'),
 'protected-root-independence':('SemanticLogic','Relational.Logic.admission_roots_do_not_change_instance_meaning','theorem-type'),
 'typed-rule-profile':('InferenceFixture','Inference.Captured.theory_valid','theorem-type'),
 'derivation-soundness':('DerivationSoundness','Inference.RequiredDerivationSoundness','definition-value'),
 'closure-adequacy':('ClosureAdequacy','Inference.RequiredClosureAdequacy','definition-value'),
 'protected-lineage':('ProtectedLineage','Inference.RequiredProtectedLineage','definition-value'),
 'independence-witnesses':('ModelSemantics','Inference.RequiredCountermodelSoundness','definition-value'),
 'rule-extension-compatibility':('RuleConservativity','Inference.Extension.RequiredRuleConservativity','definition-value')}


def policy():
 return {'schema':'relational.proof-verifier-policy/v1-candidate','toolchain':'leanprover/lean4:v4.33.1',
  'source_schema':SCHEMA,'allowed_imports':['Init',*[name for name,_ in MODULES],'InferenceFixture'],'allowed_axioms':['Classical.choice','Quot.sound','propext'],
  'catalog':{k:{'module':v[0],'required_statement':v[1],'mode':v[2]} for k,v in CATALOG.items()},
  'limits':{'source_bytes':MAX_SOURCE,'scratch_bytes':128*1024*1024,'archive_bytes':isolation.MAX_ARCHIVE,
   'process_thread_limit':1024,'log_bytes':isolation.MAX_LOG,'wall_seconds':{'elaboration':60,'audit':90},'cpu_seconds':90,'address_space_bytes':8*1024**3,'threads':1},
  'isolation':'Bubblewrap unshare-all, capability drop, cleared environment, read-only trusted mounts; no writable host mount and no network namespace access to host',
  'statement_selection':'Independently generated obligation identity selects the catalog. Definition VALUE is required for proposition aliases, theorem TYPE for concrete statements.',
  'verification':'Compiled data loaded with loadExts=false, required semantic definition dependencies compared, pure proof/type dependency closure replayed into empty pinned kernel, exact type checked by a new kernel declaration, transitive proof axioms independently traversed.',
  'currency':'Exact proposal, baseline, source, complete trusted module closure, policy, runtime and submitted artifact identities before and after replay. Old receipts cannot migrate to changed semantics.',
  'scope':'A generic checked lemma does not discharge its actual extension assumptions, model witness or full obligation set. R03 must verify those separately.',
  'trust':['pinned Lean kernel and compiled-data parser','trusted verifier implementation and host projection','Python runtime, Bubblewrap, OS and namespace enforcement','hash function','source interpretation and supplied independent assessment truth'],
  'resource_boundary':'Address-space/CPU/process limits are OS per-process/per-user limits, not an aggregate cgroup memory or CPU quota; this candidate does not claim production multi-tenant DoS isolation.',
  'independent_kernel_implementation':False,'authority_effect':'none',
  'primary_sources':['https://github.com/leanprover/lean4/blob/v4.33.1/src/Lean/Replay.lean','https://github.com/leanprover/lean4/blob/v4.33.1/src/LeanChecker.lean']}


def safe_binding(value, limit=MAX_SOURCE):
 s.require(isinstance(value,dict) and set(value)=={'path','sha256'},'invalid proof artifact binding')
 s.require(isinstance(value['path'],str) and isinstance(value['sha256'],str) and re.fullmatch('[0-9a-f]{64}',value['sha256']),'invalid artifact identity')
 raw=Path(value['path']);s.require(not raw.is_absolute() and '..' not in raw.parts,'unsafe artifact path')
 path=(s.ROOT/raw).resolve()
 s.require(path.is_relative_to(s.ROOT) and path.is_file(),'artifact escaped the workspace or is missing')
 s.require(path.stat().st_size<=limit,'artifact exceeds byte bound')
 with path.open('rb') as stream:data=stream.read(limit+1)
 s.require(len(data)<=limit and hashlib.sha256(data).hexdigest()==value['sha256'],'stale artifact binding')
 return path,data


def read_json(path):
 # The existing decoder rejects duplicate keys, non-finite numbers and invalid Unicode.
 path=Path(path);limit=4*1024*1024
 s.require(path.is_file() and path.stat().st_size<=limit,'JSON request missing or exceeds byte bound')
 with path.open('rb') as stream:data=stream.read(limit+1)
 s.require(len(data)<=limit,'JSON request exceeds byte bound')
 try:return i.c.d.decode(data)
 except RecursionError as error:raise ValueError('JSON parser depth limit exceeded') from error


def selected(proposal, obligation_id):
 required=g.generate(proposal);s.require(required['supported'],'unsupported extension profile')
 obligation=next((o for o in required['obligations'] if o['id']==obligation_id),None)
 s.require(obligation is not None,'proof does not name an independently required obligation')
 s.require(obligation['name'] in CATALOG,'this obligation requires another evidence method, not a generic theorem submission')
 return obligation,CATALOG[obligation['name']]


def current_dependencies(proposal):
 required=g.generate(proposal);s.require(required['supported'],'unsupported extension profile')
 legacy=s.read(s.BASE/'replay/dependency-manifest.json');replay.verify(legacy)
 pending=[];paths=set()
 for task_id in ['P05','G3']:
  task=s.task(task_id);s.require(task['status']=='accepted','unaccepted verifier prerequisite')
  b=task['validation']['acceptance_ref'];s.check_binding(b);pending.append(s.ROOT/b['path'])
 while pending:
  path=Path(pending.pop()).resolve()
  if path in paths:continue
  paths.add(path)
  if path.suffix=='.json':
   document=s.read(path)
   if document.get('schema')=='relational.task-acceptance/v1':
    for b in document['artifacts']+document['dependency_bindings']:
     s.check_binding(b);pending.append(s.ROOT/b['path'])
 paths.update(s.BASE/p for _,p in MODULES)
 paths.update(HERE/p for p in ['verifier.py','isolation.py','Verifier.lean','compile.sh','proof-replay-runner'])
 lean=s.lean_path();toolchain=lean.parent.parent
 # Current OS executable/library pins supplement the complete C06 runtime closure.
 binaries=[isolation.BWRAP,Path('/usr/bin/bash'),Path('/usr/bin/tar'),Path('/usr/bin/cat')]
 runtime=set(binaries)
 for binary in [*binaries,lean]:
  text=subprocess.check_output(['ldd',str(binary)],text=True)
  runtime.update(Path(match) for match in re.findall(r'(/[^\s()]+)',text) if Path(match).is_file())
 captured=i.capture(proposal) if required['classification']['rule_change'] else None
 result={'schema':'relational.proof-dependencies/v1-candidate','proposal_identity':required['proposal_identity'],
  'baseline_identity':proposal['baseline_identity'],'baseline_dependency_identity':legacy['dependency_identity'],
  'policy_identity':g.c.identity(policy()),'trusted_source_bindings':[s.binding(p) for p in sorted(paths)],
  'host_runtime':[{'absolute_path':str(p),'sha256':s.digest(p)} for p in sorted(runtime)],
  'generated_fixture_sha256':hashlib.sha256(i.c.c.fixture_source(captured['after_normal']).encode()).hexdigest() if captured else None,
  'authority_effect':'none'}
 result['dependency_identity']=g.c.identity(result)
 return result


def statement_identity(proposal,obligation,descriptor,dependencies):
 return g.c.identity({'obligation':obligation,'descriptor':descriptor,
  'proposal_identity':g.c.identity(proposal),'dependency_identity':dependencies['dependency_identity']})


def make_submission(proposal,obligation_name,proof,theorem_id):
 required=g.generate(proposal);oid=required['proposal_identity']+':'+obligation_name
 obligation,descriptor=selected(proposal,oid);deps=current_dependencies(proposal)
 return {'schema':SCHEMA,'proposal_identity':required['proposal_identity'],'obligation_id':oid,
  'required_statement':descriptor[1],'statement_identity':statement_identity(proposal,obligation,descriptor,deps),
  'policy_identity':deps['policy_identity'],'dependencies':deps,'proof':s.binding(proof),'theorem_id':theorem_id}


def validate_submission(proposal,submission):
 s.require(isinstance(submission,dict) and set(submission)=={'schema','proposal_identity','obligation_id','required_statement','statement_identity','policy_identity','dependencies','proof','theorem_id'},'unknown or missing proof-submission fields')
 s.require(submission['schema']==SCHEMA,'unsupported proof-submission schema')
 obligation,descriptor=selected(proposal,submission['obligation_id'])
 s.require(submission['proposal_identity']==g.c.identity(proposal),'proof belongs to another proposal')
 s.require(submission['required_statement']==descriptor[1],'weakened or substituted required statement')
 deps=current_dependencies(proposal)
 s.require(submission['dependencies']==deps,'proof dependencies stale, incomplete or substituted')
 s.require(submission['policy_identity']==deps['policy_identity'],'substituted verifier policy')
 s.require(submission['statement_identity']==statement_identity(proposal,obligation,descriptor,deps),'required semantic statement identity changed')
 s.require(isinstance(submission['theorem_id'],str) and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*',submission['theorem_id']),'unsupported theorem identity syntax')
 path,data=safe_binding(submission['proof'])
 text=data.decode('utf-8',errors='strict');s.require(not any(0xD800<=ord(ch)<=0xDFFF for ch in text),'invalid source Unicode')
 # A lexical bypass filter is defense in depth. Acceptance still requires the
 # independent compiled-data exact-type and transitive-axiom audit.
 s.require(i.c.c.policy().source_policy(text),'submitted source contains a disallowed proof bypass')
 return obligation,descriptor,deps,text


def prepare(proposal,build):
 logs=s.compile_lean(build,[(name,s.BASE/path) for name,path in MODULES])
 if g.generate(proposal)['classification']['rule_change']:
  captured=i.capture(proposal)
  logs.append(i.c.c.compile_generated(build,'InferenceFixture',i.c.c.fixture_source(captured['after_normal'])))
 return logs


def audit_text(text, trusted, descriptor, theorem_id='submitted'):
 """Low-level audit of untrusted bytes; caller must supply a freshly built trusted closure."""
 with tempfile.TemporaryDirectory(prefix='untrusted-proof-bytes-') as temp:
  source=Path(temp);(source/'Submitted.lean').write_text(text)
  toolchain=s.lean_path().parent.parent
  files,compilation=isolation.compile_submission(toolchain,source,trusted,HERE)
  for name,data in files.items():(source/name).write_bytes(data)
  result=isolation.run(isolation.command(toolchain,source,trusted,HERE,
   ['/toolchain/bin/lean','-j1','--run','/driver/Verifier.lean',*descriptor,theorem_id]),90,isolation.MAX_LOG)
  if result['returncode']:
   return {'accepted':False,'diagnostic':result['stderr'].decode('utf-8',errors='replace')[:16000],
    'compilation':compilation,'audit_elapsed_seconds':result['elapsed_seconds']}
  audit=i.c.d.decode(result['stdout'])
  s.require(audit.get('accepted') is True and audit.get('required_statement')==descriptor[1]
   and audit.get('theorem_id')==theorem_id and audit.get('fresh_kernel_replay') is True,'independent driver returned an invalid audit')
  return {'accepted':True,'audit':audit,'compilation':compilation,
   'audit_elapsed_seconds':result['elapsed_seconds'],
   'driver_diagnostics':result['stderr'].decode('utf-8',errors='replace')[:16000]}


def check(proposal,submission):
 try:
  obligation,descriptor,deps,text=validate_submission(proposal,submission)
 except (ValueError,UnicodeError,KeyError,TypeError,g.c.jsonschema.ValidationError) as error:
  return {'accepted':False,'execution':'not-run','currentness':'unresolved','verdict':'unknown',
   'evidence_method':'none','diagnostic':str(error)[:16000],'authority_effect':'none'}
 try:
  with tempfile.TemporaryDirectory(prefix='isolated-proof-') as temp:
   trusted=Path(temp)/'trusted';trusted.mkdir();prepare(proposal,trusted)
   audited=audit_text(text,trusted,descriptor,submission['theorem_id'])
   if not audited['accepted']:
    validate_submission(proposal,submission)
    return {**audited,'execution':'completed','currentness':'current','verdict':'violated',
     'evidence_method':'none','authority_effect':'none'}
   audit=audited['audit'];compilation=audited['compilation']
  validate_submission(proposal,submission)
  return {'accepted':True,'execution':'completed','currentness':'current','verdict':'satisfied',
   'evidence_method':'kernel-proof','obligation_id':obligation['id'],'required_statement':descriptor[1],
   'statement_identity':submission['statement_identity'],'dependency_identity':deps['dependency_identity'],
   'proposal_identity':submission['proposal_identity'],'proof':submission['proof'],'audit':audit,
   'compilation':compilation,'authority_effect':'none','readiness':'not-applicable',
   'claim_ceiling':policy()['scope']}
 except isolation.IsolationError as error:
  return {'accepted':False,'execution':error.execution,'currentness':'unresolved',
   'verdict':'violated' if error.execution=='completed' else 'unknown',
   'evidence_method':'none','diagnostic':str(error)[:16000],'authority_effect':'none'}
 except (ValueError,subprocess.TimeoutExpired,OSError) as error:
  return {'accepted':False,'execution':'provider-error','currentness':'unresolved','verdict':'unknown',
   'evidence_method':'none','diagnostic':str(error)[:16000],'authority_effect':'none'}


def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('submission',type=Path);parser.add_argument('--proposal',required=True,type=Path)
 args=parser.parse_args()
 try:result=check(read_json(args.proposal),read_json(args.submission))
 except (ValueError,OSError,g.c.jsonschema.ValidationError) as error:result={'accepted':False,'execution':'not-run','diagnostic':str(error)[:16000],'authority_effect':'none'}
 print(json.dumps(result,indent=2,ensure_ascii=False))
 return 0 if result['accepted'] else 1

if __name__=='__main__':raise SystemExit(main())
