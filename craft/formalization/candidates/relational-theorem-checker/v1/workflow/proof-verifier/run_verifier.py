#!/usr/bin/env python3
"""Actual proof audits, isolation probes, and metadata substitution controls."""
from copy import deepcopy
from pathlib import Path
import json
import os
import socket
import tempfile
import time
import verifier as v
s=v.s;HERE=v.HERE
BODIES={
 'invariant-preservation':'Registry.Evolution.audited_preservation',
 'conservative-expansion':'Registry.Models.audited_conservativity',
 'protected-root-independence':'Relational.Logic.admission_roots_do_not_change_instance_meaning',
 'typed-rule-profile':'Inference.Captured.theory_valid',
 'derivation-soundness':'Inference.audited_derivation_soundness',
 'closure-adequacy':'Inference.audited_closure_adequacy',
 'protected-lineage':'Inference.audited_protected_lineage',
 'independence-witnesses':'Inference.audited_countermodel_soundness',
 'rule-extension-compatibility':'Inference.Extension.audited_rule_conservativity'}


def main():
 proposal=s.read(s.BASE/'evolution/proposals/rule-change-proposal.json')
 positives=[];controls=[];examples=HERE/'examples';examples.mkdir(exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='proof-control-trusted-') as temp:
  build=Path(temp);modules=v.prepare(proposal,build)
  for name,descriptor in v.CATALOG.items():
   concrete={'typed-rule-profile':'Inference.TheoryValid Inference.Captured.theory',
    'protected-root-independence':'∀ (g : Relational.Graph) (roots : List Relational.AdmissionRoot) (e : Relational.Assertion), Relational.InstanceValid (Relational.Logic.withAdmissionRoots g roots) e ↔ Relational.InstanceValid g e'}
   target=descriptor[1] if descriptor[2]=='definition-value' else concrete[name]
   source='import '+descriptor[0]+'\ntheorem submitted : '+target+' := '+BODIES[name]+'\n'
   path=examples/(name+'.lean');path.write_text(source)
   report=v.audit_text(source,build,descriptor)
   s.require(report['accepted'],'catalog exact proof failed: '+name+' '+str(report))
   positives.append({'name':name,'source':s.binding(path),'report':report})
   print('positive',name,report['audit_elapsed_seconds'],flush=True)
  descriptor=v.CATALOG['derivation-soundness'];required=descriptor[1]
  good='import DerivationSoundness\ntheorem submitted : '+required+' := Inference.audited_derivation_soundness\n'
  bad_sources={
   'weakened compiled theorem type':'import DerivationSoundness\ntheorem submitted : True := True.intro\n',
   'circular assumed obligation':'import DerivationSoundness\ntheorem submitted (assumed : '+required+') : '+required+' := assumed\n',
   'alias with weaker proposition':'import DerivationSoundness\ndef Weaker : Prop := True\ntheorem submitted : Weaker := True.intro\n',
   'unapproved transitive axiom despite valid kernel typing':'import DerivationSoundness\naxiom cheat : '+required+'\ntheorem submitted : '+required+' := cheat\n',
   'sorry despite valid elaboration':'import DerivationSoundness\ntheorem submitted : '+required+' := by sorry\n',
   'forged successful compiler JSON':'import DerivationSoundness\n#eval IO.println "{\\\"accepted\\\":true,\\\"fresh_kernel_replay\\\":true}"\ntheorem submitted : True := True.intro\n',
   'unapproved module imports':'import Lean\nimport DerivationSoundness\ntheorem submitted : '+required+' := Inference.audited_derivation_soundness\n'}
  for name,source in bad_sources.items():
   report=v.audit_text(source,build,descriptor)
   s.require(not report['accepted'],'hostile proof accepted: '+name)
   controls.append({'name':name,'result':'rejected','independent_driver':report})
   print('rejected',name,flush=True)
  multipart='module\npublic import Init\npublic theorem submitted : True := True.intro\n'
  multipart_report=v.audit_text(multipart,build,descriptor)
  s.require(not multipart_report['accepted'] and len(multipart_report['compilation']['compiled_parts'])>1,'multipart weak proof was not independently rejected')
  controls.append({'name':'exported/server/private parts do not admit a weaker statement','result':'rejected','report':multipart_report})
  wrong=v.audit_text(good,build,descriptor,'missing_identity')
  s.require(not wrong['accepted'],'missing theorem identity accepted')
  controls.append({'name':'wrong theorem identity','result':'rejected','independent_driver':wrong})
  inherited=v.audit_text('import DerivationSoundness\n',build,descriptor,'Inference.audited_derivation_soundness')
  s.require(not inherited['accepted'],'imported theorem claimed as new submission')
  controls.append({'name':'imported identity is not a submitted declaration','result':'rejected','independent_driver':inherited})
  initializer=good+'initialize IO.println "UNTRUSTED_INITIALIZER_MUST_NOT_RUN_IN_DRIVER"\n'
  report=v.audit_text(initializer,build,descriptor)
  s.require(report['accepted'] and 'UNTRUSTED_INITIALIZER' not in report['driver_diagnostics'],'submitted initializer ran in verifier')
  controls.append({'name':'no submitted initializer execution in independent driver','result':'pass','report':report})
  # These probes use newly created harmless sentinel state, never private/live files.
  with tempfile.TemporaryDirectory(prefix='proof-host-sentinel-') as host:
   marker=Path(host)/'marker';marker.write_text('owned isolation sentinel')
   os.environ['PROOF_VERIFIER_HOST_SENTINEL']='owned-host-value'
   with socket.socket() as listener:
    listener.bind(('127.0.0.1',0));listener.listen(1);port=listener.getsockname()[1]
    literal=v.i.c.d.literal
    probes=good+'''#eval (do
  let hostVisible ← (System.FilePath.mk '''+literal(str(marker))+''').pathExists
  let envVisible ← IO.getEnv "PROOF_VERIFIER_HOST_SENTINEL"
  let mut trustedWritable := false
  try
    IO.FS.writeFile "/trusted/DerivationSoundness.lean" "changed"
    trustedWritable := true
  catch _ => pure ()
  let network ← IO.Process.output {cmd := "/runtime/bash", args := #["-c", '''+literal('exec 3<>/dev/tcp/127.0.0.1/'+str(port))+''']}
  if hostVisible || envVisible.isSome || trustedWritable || network.exitCode == 0 then
    throw (IO.userError "isolation boundary failed")
  IO.println "ISOLATION_BOUNDARIES_CHECKED"
 : IO Unit)
'''
    report=v.audit_text(probes,build,descriptor)
    s.require(report['accepted'] and 'ISOLATION_BOUNDARIES_CHECKED' in report['compilation']['untrusted_log'],'isolation probe did not execute successfully')
    controls.append({'name':'host sentinel, environment, trusted writes and host loopback unavailable','result':'pass','report':report})
   del os.environ['PROOF_VERIFIER_HOST_SENTINEL']
  # Compile a proof against a deliberately weaker dependency in an owned
  # temporary fixture, then load its bytes with the real read-only dependency.
  # This exercises imported-module elaboration trust rather than just metadata.
  with tempfile.TemporaryDirectory(prefix='forged-import-fixture-') as fake:
   fake=Path(fake);fake_module=fake/'DerivationSoundness.lean'
   fake_source='import Init\nnamespace Inference\ndef RequiredDerivationSoundness : Prop := True\nend Inference\n'
   fake_module.write_text(fake_source)
   result=v.subprocess.run([str(s.lean_path()),'-j1','-o',str(fake_module.with_suffix('.olean')),str(fake_module)],cwd=fake,capture_output=True,text=True,timeout=60)
   s.require(result.returncode==0,'owned fake-dependency fixture failed')
   untrusted=fake/'untrusted';untrusted.mkdir()
   (untrusted/'Submitted.lean').write_text('import DerivationSoundness\ntheorem submitted : Inference.RequiredDerivationSoundness := True.intro\n')
   files,compilation=v.isolation.compile_submission(s.lean_path().parent.parent,untrusted,fake,HERE)
   for name,data in files.items():(untrusted/name).write_bytes(data)
   result=v.isolation.run(v.isolation.command(s.lean_path().parent.parent,untrusted,build,HERE,
    ['/toolchain/bin/lean','-j1','--run','/driver/Verifier.lean',*descriptor,'submitted']),90,v.isolation.MAX_LOG)
   s.require(result['returncode']!=0,'compiled proof against weaker dependency accepted by fresh kernel')
   controls.append({'name':'compiled proof elaborated against substituted dependency','result':'rejected',
    'diagnostic':result['stderr'].decode('utf-8',errors='replace'),'forged_dependency_sha256':s.digest(fake_module),
    'untrusted_compilation':compilation})
  # Observe an actual live sandbox and enforce a short trusted deadline.
  try:
   argv=v.isolation.command(s.lean_path().parent.parent,build,build,HERE,
    ['/runtime/bash','-c','while :; do :; done'])
   v.isolation.run(argv,timeout=.3,stdout_limit=1024)
  except v.isolation.IsolationError as error:
   s.require(error.execution=='timeout','deadline reported success/failure instead of unknown timeout')
   controls.append({'name':'actual live sandbox timeout','result':'unknown','execution':error.execution})
  else:raise ValueError('sandbox deadline did not stop live process')
  # Verify there is no fallback to unisolated execution when isolation is absent.
  previous=v.isolation.BWRAP;v.isolation.BWRAP=Path('/missing-owned-isolation-probe')
  try:
   v.isolation.command(s.lean_path().parent.parent,build,build,HERE)
  except v.isolation.IsolationError as error:
   s.require(error.execution=='unavailable','missing isolation reported as success')
   controls.append({'name':'isolation unavailable fails closed','result':'unknown','execution':error.execution})
  finally:v.isolation.BWRAP=previous
 # Public proof replay: independent source build, exact metadata and post-check currency.
 proof=examples/'DerivationProof.lean';proof.write_text(good)
 submission=v.make_submission(proposal,'derivation-soundness',proof,'submitted')
 s.write(examples/'derivation-submission.json',submission)
 report=v.check(proposal,submission);s.require(report['accepted'],'public full-bound proof replay failed: '+str(report))
 s.write(examples/'derivation-result.json',report)
 def reject(name,mutate,changed=proposal):
  bad=deepcopy(submission);mutate(bad)
  try:v.validate_submission(changed,bad)
  except (ValueError,UnicodeError) as error:controls.append({'name':name,'result':'rejected','diagnostic':str(error)})
  else:raise ValueError('metadata control accepted: '+name)
 reject('weaker required statement metadata',lambda x:x.update(required_statement='True'))
 reject('missing proof dependency',lambda x:x['dependencies']['trusted_source_bindings'].pop())
 reject('substituted dependency bytes',lambda x:x['dependencies']['trusted_source_bindings'][0].update(sha256='0'*64))
 reject('substituted verifier policy',lambda x:x.update(policy_identity='0'*64))
 reject('substituted proof artifact bytes',lambda x:x['proof'].update(sha256='0'*64))
 reject('unknown submission fields',lambda x:x.update(accepted=True))
 changed=deepcopy(proposal);changed['after']['rules'][0]['version']='v2'
 reject('valid old proof receipt cannot migrate to changed rule semantics',lambda x:None,changed)
 reject('path traversal proof binding',lambda x:x['proof'].update(path='../outside.lean'))
 with tempfile.TemporaryDirectory(prefix='proof-path-controls-') as folder:
  external=Path(folder)/'outside.lean';external.write_text(good)
  link=examples/'owned-symlink-control.lean';link.symlink_to(external)
  try:reject('resolved symlink escapes workspace',lambda x:x.update(proof={'path':str(link.relative_to(s.ROOT)),'sha256':s.digest(external)}))
  finally:link.unlink()
 for name,data in [('duplicate JSON keys',b'{"schema":1,"schema":2}'),('invalid JSON UTF-8',b'\xff'),('oversized JSON request',b' '*(4*1024*1024+1))]:
  path=examples/'owned-invalid-request.json';path.write_bytes(data)
  try:
   try:v.read_json(path)
   except ValueError as error:controls.append({'name':name,'result':'rejected','diagnostic':str(error)})
   else:raise ValueError('invalid request accepted: '+name)
  finally:path.unlink()
 oversized=examples/'owned-oversized-proof.lean';oversized.write_bytes(b' '*(v.MAX_SOURCE+1))
 try:reject('oversized proof source',lambda x:x.update(proof=s.binding(oversized)))
 finally:oversized.unlink()
 invalid=v.check({'schema':'invalid-owned-proposal'},submission)
 s.require(not invalid['accepted'] and invalid['execution']=='not-run','malformed proposal escaped normalized failure')
 controls.append({'name':'malformed proposal normalized to no proof acceptance','result':'rejected','outcome':invalid})
 # Definition mode is fixed by policy, never the user's Prop-valued type alias.
 s.require(v.CATALOG['derivation-soundness'][2]=='definition-value','generic target weakened to Prop')
 controls.append({'name':'generic required aliases use their proposition values','result':'pass'})
 output={'schema':'relational.proof-submission-controls/v1-candidate','result':'pass',
  'positive_catalog_cases':positives,'public_replay':report,'controls':controls,
  'trusted_modules':modules,'validation_script':s.binding(Path(__file__)),'policy_identity':v.g.c.identity(v.policy()),
  'review_mode':'Codex author self-review; candidate proof verifier only',
  'authority_effect':'none','claim_ceiling':v.policy()['scope']}
 s.write(HERE/'proof-verifier-policy.json',v.policy());s.write(HERE/'submission-controls.json',output)
 print('completed',len(positives),'positive catalog cases',len(controls),'controls',flush=True)

if __name__=='__main__':main()
