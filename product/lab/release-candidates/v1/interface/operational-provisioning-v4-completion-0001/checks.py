"""Two retained, independently owned cold-process technical rehearsals."""
import copy
from contextlib import contextmanager
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from . import provisioning as P

HERE=Path(__file__).resolve().parent
RUN=P.ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T34'
INSTALL=P.ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'

def write(path,raw):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as out:out.write(raw);out.flush();os.fsync(out.fileno())

def pin(path):return {'identity':P.identity(path.stat()),'sha256':P.sha(path.read_bytes())}

def original_selection():
    manifest=json.loads((P.ORIGINAL/'engine-manifest.json').read_bytes())
    parent=json.loads((P.ROOT/manifest['parent_binding']['path']).read_bytes())
    paths={r['path'] for r in manifest['files']+parent['files']}
    paths|={manifest['parent_binding']['path'],'product/lab/release-candidates/v1/interface/custody-correction-v4/engine-manifest.json','product/lab/release-candidates/v1/interface/custody-correction-v4/loader.py','implementation/lab-provisioning/candidates/v1/provision.py','implementation/lab-provisioning/candidates/v1/OPERATOR.md','product/lab/release-candidates/v1/interface/api-integration-v16/auth.py',str((HERE/'provisioning.py').relative_to(P.ROOT)),str((HERE/'checks.py').relative_to(P.ROOT)),str((HERE/'capture_io.py').relative_to(P.ROOT)),str((HERE/'engine_capture.py').relative_to(P.ROOT))}
    paths|={str(p.relative_to(P.ROOT)) for p in HERE.glob('*.py')}
    return [{'path':p,'sha256':P.sha((P.ROOT/p).read_bytes())} for p in sorted(paths)]

def fixture(number):
    root=Path(tempfile.mkdtemp(prefix='cal-T34-owned-'+str(number)+'-'));os.chmod(root,0o700)
    for name in ['target','custody','channel']:(root/name).mkdir(mode=0o700)
    key=Ed25519PrivateKey.generate()
    write(root/'custody/candidate.pem',key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()))
    public=key.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw).hex()
    source=original_selection();sid='T34-rehearsal-'+str(number)
    policy={'schema_version':'lab-durable-channel-policy/v1-candidate','authority_effect':'none','purpose':'owned-candidate-rehearsal','principal_ref':'principal:T34-owned-'+str(number),'operator_ref':'role:candidate-T34-'+str(number),'scope_ref':'scope:lab-runtime-local:'+sid,'public_key':public,'policy_ref':'policy:T34-owned-'+str(number),'plan_source_sha256':P.sha(P.encoded(source)),'not_before':time.time()-5,'expires_at':time.time()+1800,'revoked':False}
    write(root/'custody/policy.json',P.encoded(policy))
    plan={'schema_version':'lab-operational-provisioning-plan/v1-candidate','purpose':'owned-candidate-rehearsal','operator_ref':policy['operator_ref'],'principal_ref':policy['principal_ref'],'scope_ref':policy['scope_ref'],'store_id':sid,'target_parent':str(root/'target'),'target_parent_identity':P.identity((root/'target').stat()),'target_name':'store','target_preimage':'absent','custody_path':str(root/'custody'),'custody_identity':P.identity((root/'custody').stat()),'key_pin':pin(root/'custody/candidate.pem'),'policy_pin':pin(root/'custody/policy.json'),'public_key':public,'policy_ref':policy['policy_ref'],'channel_state':str(root/'channel'),'channel_state_identity':P.identity((root/'channel').stat()),'source_bindings':source,'engine_pins':json.loads((P.ORIGINAL/'pins.json').read_bytes()),'base_repository_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=P.ROOT,text=True).strip(),'categories':['artifact-instance'],'effects':['admit'],'rollback':{'selection':'retain-all-prior-state','delete_prior':False,'reuse_prior_permissions':False}}
    plan_sha=P.sha(P.encoded(plan));write(root/'plan.json',P.encoded(plan))
    return root,plan,plan_sha

def sign(controller,challenge):
    raw=controller.custody.read('candidate.pem',controller.plan['key_pin'])
    key=serialization.load_pem_private_key(raw,None)
    P.require(key.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw).hex()==controller.plan['public_key'],'signer independent key pin differs')
    return {'challenge':challenge,'signature':key.sign(P.encoded(challenge)).hex()}

def command(root,pin,action,argument=None):
    from . import capture_io
    source_pin=SOURCE_PIN
    manifest=P.parse(capture_io.capture(HERE/'source-manifest.json',source_pin))
    startup_row=next(row for row in manifest['files'] if row['path']==str((HERE/'startup.py').relative_to(P.ROOT)))
    startup=capture_io.capture(HERE/'startup.py',startup_row['sha256'])
    code="import sys;sys.path.insert(0,"+repr(str(INSTALL/'deps'))+");ns={'__file__':"+repr(str(HERE/'startup.py'))+",'__name__':'_T34_selected_startup'};exec(compile("+repr(startup)+","+repr(str(HERE/'startup.py'))+",'exec'),ns);ns['main'](*sys.argv[1:])"
    return [str(INSTALL/'lib/abi/ld-linux-x86-64.so.2'),'--inhibit-cache','--library-path',str(INSTALL/'lib/abi'),str(INSTALL/'bin/python'),'-I','-X','utf8','-B','-S','-c',code,source_pin,'worker',str(root),pin,action,json.dumps(argument)]

def child(root,pin,action,argument=None):
    cmd=command(root,pin,action,argument)
    process=subprocess.run(cmd,env={'PATH':'/usr/bin:/bin','LC_ALL':'C'},capture_output=True,text=True)
    P.require(process.returncode==0,'cold child failed: '+process.stderr);return json.loads(process.stdout)

def worker(root,pin,action,argument):
    plan=P.parse((Path(root)/'plan.json').read_bytes());c=P.Controller(plan,pin);argument=json.loads(argument)
    try:
        if action=='reconcile':result=c.reconcile(argument['id'],argument.get('result_sha256'))
        else:
            def pause(metadata,resume=False):
                write(Path(root)/'observer-ready.json',P.encoded(metadata))
                while not resume or not (Path(root)/'observer-release').exists():time.sleep(0.1)
            if action=='interrupt-intent':
                c.preflight_original=lambda:pause({'observer':'task-local-before-original-preflight','original_engine_modified':False})
            if action in {'interrupt-genesis','interrupt-parent'}:
                original_engine=c.original_engine
                def observer_engine():
                    loader,selected=original_engine()
                    @contextmanager
                    def wrapped():
                        with selected as engine:
                            original_replay=engine.replay_owned
                            if action=='interrupt-parent':
                                original_capture=engine.store_module.capture
                                def observed_capture(*args):
                                    value=original_capture(*args);pause({'observer':'task-local-after-original-constructor-capture-before-target-mkdir','original_engine_modified':False},True);return value
                                engine.store_module.capture=observed_capture
                            def observed_replay(target,config_sha,baseline_sha,head):
                                pause({'observer':'task-local-before-original-replay-after-real-genesis','original_engine_modified':False,'config_sha256':config_sha,'baseline_snapshot_digest':baseline_sha,'expected_head':head})
                                return original_replay(target,config_sha,baseline_sha,head)
                            if action=='interrupt-genesis':engine.replay_owned=observed_replay
                            yield engine
                    return loader,wrapped()
                c.original_engine=observer_engine
            channel=c.channel();proof=sign(c,channel.challenge)
            if action=='stale':
                try:channel.authenticate(argument)
                except ValueError as error:result={'refused':str(error),'new_challenge':channel.challenge}
                else:raise AssertionError('stale proof accepted')
            else:
                context=channel.authenticate(proof)
                result={'proof':proof,'context':context,'result':c.rehearsal(channel,'coldoperation')}
        print(json.dumps(result))
    finally:c.close()

def interruptions():
    evidence=[]
    for point in ['intent','genesis','parent']:
        root,plan,pinsha=fixture('interrupt-'+point)
        process=subprocess.Popen(command(root,pinsha,'interrupt-'+point),env={'PATH':'/usr/bin:/bin','LC_ALL':'C'},stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        deadline=time.monotonic()+45
        try:
            while not (root/'observer-ready.json').exists() and process.poll() is None and time.monotonic()<deadline:time.sleep(0.05)
            P.require((root/'observer-ready.json').exists(),'real interruption observer did not reach selected boundary')
            observed=P.parse((root/'observer-ready.json').read_bytes())
            if point=='parent':
                (root/'target').rename(root/'target-selected-inode-retained');(root/'target').mkdir(mode=0o700)
                write(root/'observer-release',b'release owned observer')
                stdout,stderr=process.communicate(timeout=30)
                P.require(process.returncode!=0,'changed parent locator unexpectedly accepted')
                P.require(list((root/'target').iterdir())==[],'constructor redirected effects into replacement parent')
                P.require((root/'target-selected-inode-retained/store/HEAD.json').is_file(),'original commit did not remain under independently retained parent inode')
                P.require(not (root/'channel/result-coldoperation').exists(),'changed parent manufactured completed result')
                evidence.append({'root':str(root),'plan_sha256':pinsha,'checkpoint':'parent-locator-replacement','observer_variant':observed['observer'],'original_engine_bytes_modified':False,'child_exit':process.returncode,'selected_parent_retained':True,'foreign_replacement_parent_empty':True,'original_genesis_under_selected_inode':True,'result_absent':True,'automatic_redispatch':False})
                continue
            process.kill();stdout,stderr=process.communicate(timeout=5)
            P.require(process.returncode==-9,'child was not SIGKILL interrupted')
            P.require((root/'channel/intent-coldoperation').exists() and not (root/'channel/result-coldoperation').exists(),'uncertain durable intent/result boundary differs')
            if point=='intent':
                result=child(root,pinsha,'reconcile',{'id':'coldoperation'});P.require(result['status']=='uncertain-retain-no-redispatch','interrupted intent redispatched')
                replay=None
            else:
                try:controller=P.Controller(plan,pinsha)
                except ValueError as error:result={'status':'refused-unrecorded-target-retain-no-redispatch','error':str(error)}
                else:controller.close();raise AssertionError('uncertain genesis without result accepted')
                # Independent observer evidence permits read-only original replay,
                # never minting a completed provision result or new authority.
                from . import engine_capture as loader
                with loader.engine(loader.EnginePins(**plan['engine_pins'])) as engine:
                    replay=engine.replay_owned(root/'target/store',observed['config_sha256'],observed['baseline_snapshot_digest'],observed['expected_head'])['freshness']['status']
                P.require(replay=='current','cold original uncertain-genesis reader differs')
            evidence.append({'root':str(root),'plan_sha256':pinsha,'checkpoint':point,'termination':'SIGKILL','observer_variant':observed['observer'],'original_engine_bytes_modified':False,'intent_retained':True,'result_absent':True,'reconciliation':result,'uncertain_genesis_original_cold_replay':replay,'automatic_redispatch':False})
        finally:
            if process.poll() is None:process.kill();process.communicate(timeout=5)
    return evidence

def checks(report_name='focused-evidence-0002.json'):
    results=[];cases=[]
    def refusal(label,fn):
        try:fn()
        except (ValueError,OSError) as error:cases.append({'case':label,'result':'PASS-refused','reason':str(error)})
        else:raise AssertionError(label+' unexpectedly accepted')
    for n in [1,2]:
        root,plan,pinsha=fixture(n);c=P.Controller(plan,pinsha)
        try:
            cold=child(root,pinsha,'rehearse')
            P.require(cold['result']['status']=='original-candidate-genesis-committed' and cold['result']['replay_freshness']=='current','actual original construction/replay failed')
            P.require(cold['context']['role_assignment_bindings']==[] and cold['context']['authority_effect']=='none','technical key conferred authority')
            P.require((root/'target/store').exists(),'original candidate store missing')
            restart=child(root,pinsha,'stale',cold['proof']);P.require(restart['new_challenge']!=cold['proof']['challenge'],'restart reused challenge')
            reconciled=child(root,pinsha,'reconcile',{'id':'coldoperation','result_sha256':P.sha(P.encoded(cold['result']))});P.require(reconciled==cold['result'],'cold reconciliation mismatch')
            # No private material is persisted in the public report.
            results.append({'root':str(root),'plan_sha256':pinsha,'source_count':len(plan['source_bindings']),'channel_context':cold['context'],'original_construction':cold['result'],'restart_stale_proof_refused':restart['refused'],'fresh_nonce':restart['new_challenge']['nonce']!=cold['proof']['challenge']['nonce'],'cold_reconciliation':reconciled['status'],'private_key_published':False,'store_created':True})
            refusal('missing independent result pin '+str(n),lambda:c.reconcile('coldoperation'))
            channel=c.channel();proof=sign(c,channel.challenge);channel.authenticate(proof)
            refusal('consumed nonce '+str(n),lambda:channel.authenticate(proof))
            wrong=c.channel();bad=copy.deepcopy(sign(c,wrong.challenge));bad['challenge']['nonce']='0'*64
            refusal('wrong challenge '+str(n),lambda:wrong.authenticate(bad))
            refusal('failed proof consumes channel '+str(n),lambda:wrong.authenticate(sign(c,wrong.challenge)))
            wrong=c.channel();bad=sign(c,wrong.challenge);bad['signature']=Ed25519PrivateKey.generate().sign(P.encoded(wrong.challenge)).hex()
            try:wrong.authenticate(bad)
            except Exception as error:cases.append({'case':'wrong independent signing key '+str(n),'result':'PASS-refused','reason':type(error).__name__})
            else:raise AssertionError('wrong key accepted')
            # An intent interrupted before a result is retained and never redispatched.
            intent={'schema_version':'lab-provisioning-intent/v1-candidate','plan_sha256':pinsha,'operation_id':'uncertain','principal_ref':plan['principal_ref'],'scope_ref':plan['scope_ref'],'authority_effect':'none','target_preimage':'absent','store_created':False}
            c.state.create('intent-uncertain',P.encoded(intent))
            uncertain=child(root,pinsha,'reconcile',{'id':'uncertain'});P.require(uncertain['status']=='uncertain-retain-no-redispatch','uncertain intent redispatched')
            cases.append({'case':'uncertain cold reconciliation '+str(n),'result':'PASS','status':uncertain['status']})
            (root/'target/store').rename(root/'store-retained-original');(root/'target/store').mkdir(mode=0o700);refusal('occupied target '+str(n),c.guard);(root/'target/store').rmdir();(root/'store-retained-original').rename(root/'target/store')
            (root/'target/store').rename(root/'store-retained-original');(root/'target/store').symlink_to(root/'store-retained-original',target_is_directory=True);refusal('target symlink '+str(n),c.guard);(root/'target/store').unlink();(root/'store-retained-original').rename(root/'target/store')
            os.chmod(root/'custody/candidate.pem',0o644);refusal('private key mode '+str(n),c.guard);os.chmod(root/'custody/candidate.pem',0o600)
            private=root/'custody/candidate.pem';private.rename(root/'key-retained-original.pem');write(private,(root/'key-retained-original.pem').read_bytes());refusal('same-byte private key inode replacement '+str(n),c.guard);private.unlink();(root/'key-retained-original.pem').rename(private)
            os.chmod(root/'channel',0o755);refusal('channel root mode '+str(n),c.guard);os.chmod(root/'channel',0o700)
            policy=root/'custody/policy.json';policy.rename(root/'policy-retained-original.json');policy.symlink_to(root/'policy-retained-original.json')
            refusal('policy symlink '+str(n),c.guard);policy.unlink();(root/'policy-retained-original.json').rename(policy)
            write(root/'channel/challenge-foreign',b'{}');refusal('foreign recognized-prefix residue '+str(n),c.guard)
            (root/'channel/challenge-foreign').rename(root/'foreign-retained.json')
            # Exact independent plan changes cannot be smuggled into an existing handle.
            changed=copy.deepcopy(plan);changed['principal_ref']='principal:foreign'
            refusal('wrong plan selection '+str(n),lambda:P.Controller(changed,pinsha))
            refusal('independently selected wrong policy principal '+str(n),lambda:P.Controller(changed,P.sha(P.encoded(changed))))
            saved=c.plan['purpose'];c.plan['purpose']='prospective-operation'
            try:refusal('operational purpose cannot invoke candidate constructor '+str(n),lambda:c.rehearsal(channel,'admitted'))
            finally:c.plan['purpose']=saved
            policy_raw=policy.read_bytes();policy.write_bytes(P.encoded({**P.parse(policy_raw),'revoked':True}));refusal('revoked current policy '+str(n),channel.guard);policy.write_bytes(policy_raw)
            policy.write_bytes(P.encoded({**P.parse(policy_raw),'expires_at':time.time()-1}));expired=copy.deepcopy(plan);expired['policy_pin']=pin(policy);refusal('independently selected expired period '+str(n),lambda:P.Controller(expired,P.sha(P.encoded(expired))));policy.write_bytes(policy_raw)
            write(root/'custody/REVOKED',b'operator revocation');refusal('revocation marker '+str(n),channel.guard)
            P.require((root/'custody/REVOKED').exists() and (root/'foreign-retained.json').read_bytes()==b'{}','foreign/revocation state lost')
        finally:c.close()
    report={'schema_version':'lab-T34-focused-evidence/v1-candidate','result':'PASS','rehearsals':results,'checks':cases,'interruptions':interruptions(),'authority_effect':'none','task_complete':False,'actual_admitted_provisioning':False,'full_shared_runtime_qualified':False}
    destination=RUN/report_name;write(destination,json.dumps(report,sort_keys=True,indent=2).encode()+b'\n')
    print(json.dumps({'result':'PASS','rehearsals':len(results),'checks':len(cases),'report':str(destination)}))

if __name__=='__main__':checks()
