"""OS interruption of real owned Workflow effects behind the common Service.

Fixture preparation creates actual producer outputs. Fresh children authenticate
independently to its private copy. Recovery observes actual immutable effects;
no production callback, crash hook, or clock is replaced.
"""
import argparse
import copy
import ctypes
import importlib
import importlib.util
import json
import os
from pathlib import Path
import select
import shutil
import signal
import struct
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('_t18_process_observer',HERE/'probe.py')
Q=importlib.util.module_from_spec(spec);spec.loader.exec_module(Q)
ROOT=Q.ROOT;need=Q.need;sha=Q.sha;write=Q.write


def fixture_module():
    path=ROOT/'implementation/lab-runtime/local-host/t31-public-owned-transition-0001/public_fixture.py'
    spec=importlib.util.spec_from_file_location('_t18_actual_owned_fixture',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def child(args):
    m=Q.modules(args);P,G,A,F,S,I,H,W=(m[k] for k in ('protocol','guard','auth','fixtures','service','integration_dispatch','handlers','workspace'))
    root=Path(args.root);schemas=P.Schemas(args.profile_sha256)
    fixture=fixture_module()
    with P.source.replay_source(P.source.CURRENT_LEGACY_NAME) as view:
        if args.child=='prepare':
            need(not root.exists(),'fresh private Workflow fixture destination required')
            with fixture.example(view,schemas,api_namespace=S.__package__) as (host,request,witness):
                origin=host.vault.root.parent
                need(not any(p.is_symlink() for p in origin.rglob('*')),'linked fixture original')
                shutil.copytree(origin,root)
                # Use the actual provisioner's policy path, selected by its
                # authenticated immutable policy bytes rather than a filename.
                policies=[p for p in root.iterdir() if p.is_file() and p.read_bytes()==P.compact(host.channel.policy)]
                need(len(policies)==1,'one exact original private Reader policy required')
                policy_path=policies[0];policy=P.frame_parse(policy_path.read_bytes())
                vault=root/host.vault.root.relative_to(origin)
                policy['workspace']['root']=str(vault)
                policy_path.write_bytes(P.compact(policy));policy_path.chmod(0o600)
                selected=request();index=witness['index']
                write(root.parent/'selection.json',{'policy_path':str(policy_path),'policy_sha256':sha(policy_path.read_bytes()),
                    'request':selected,'index_binding':P.binding('owned-fixture:host-input-index',fixture.P.enc(index)),
                    'journal_config_sha256':witness['store'].journal.config_sha256,'source_cut':H.cut(view)})
            return
        selection=json.loads((root.parent/'selection.json').read_bytes())
        from cryptography.hazmat.primitives.serialization import load_pem_private_key
        key=load_pem_private_key(W.read_private(root/'reader.pem'),password=None)
        channel=A.ReaderChannel(selection['policy_path'],selection['policy_sha256'],schemas)
        host=None
        try:
            channel.authenticate(F.proof(key,channel.challenge));key=None
            host=S.Service(view,channel,schemas)
            need(H.cut(view)==selection['source_cut'],'fresh actual Workflow Source cut changed')
            OW=importlib.import_module(S.__package__+'.owned_workflow_transition')
            store=fixture.C.S.OutputJournal(host.vault.root/'workflows/design',selection['journal_config_sha256'])
            index=P.frame_parse(host.vault.material(selection['index_binding']))
            profile=fixture.P.load('engineering')
            producer=P.frame_parse(host.vault.material(index['producer_receipt_bindings'][0]))
            need(host.vault.material(index['producer_receipt_bindings'][1])==profile['original_result_raw']
                 and host.vault.material(index['producer_receipt_bindings'][2])==profile['original_run_raw'],
                 'actual independent original producer evidence differs')
            outputs={t:[row['artifact'] for row in rows] for t,rows in index['outputs'].items()}
            originals={row['artifact']['version_ref']:host.vault.material(row['original_binding']) for rows in index['outputs'].values() for row in rows}
            need(all(producer['transitions'][t]==headers for t,headers in outputs.items()),'actual producer output header correspondence differs')
            proof=fixture.ProducerProof(profile,outputs,originals,producer)
            state=fixture.HostState(host,input_binding=selection['index_binding'],store=store,header_type=fixture.HostHeaders,
                currentness_type=fixture.C.OwnedCurrentness,selection_type=fixture.C.Selection,producer_guard=proof.guard)
            OW.install(host,store=store,kernel=fixture.K,headers=state.headers,semantics=state.semantics_for_call,outputs=state.outputs,guard=state.guard)
            surface=I.IntegrationService(host);request=copy.deepcopy(selection['request'])
            request['caller_context_ref']=channel.context['context_ref']
            request['call_id']+=':'+args.child
            fingerprint=S.jcs.fingerprint(request,channel.context)
            if args.child=='effect':
                write(root.parent/'call-ready.json',{'request_fingerprint':fingerprint,
                    'outer_namespace':S.jcs.namespace(request['operation'],request['idempotency_key'],channel.context),
                    'inner_namespace':store.journal.namespace(request['message']['idempotency_key'])})
                reply=surface.call(P.compact(request));write(root.parent/'normal-return.json',reply)
                return
            def recovery_guard():
                # Reuse the real installed selection's full Source/schema,
                # route/method/host-grant and effective-deadline boundary.
                OW.selected(host).guard(A.instant(request['deadline']))
            original=json.loads((root.parent/'call-ready.json').read_bytes())
            need(fingerprint==original['request_fingerprint'],'fresh common Workflow control fingerprint differs')
            snapshot=lambda:{p.relative_to(host.vault.root).as_posix():sha(p.read_bytes()) for p in host.vault.root.rglob('*') if p.is_file()}
            before=snapshot();reply=surface.call(P.compact(request))
            need(schemas.valid('api-reply',reply),'fresh common Workflow response invalid')
            if args.stage=='result':
                need(reply.get('kind')=='result' and reply['message']['posture']=='applied','completed common Workflow result did not replay')
            else:
                need(reply.get('kind')=='error' and reply['message']['code']=='recovery-required','pending outer Workflow claim was redispatched')
            need(snapshot()==before,'common exact Workflow retry changed durable bytes')
            key=request['message']['idempotency_key']
            claim_path=store.root/'claims'/(original['inner_namespace']+'.json')
            claim=P.frame_parse(fixture.C.S.read_owned(claim_path));tx_path=store.root/'transactions/00000001.json'
            if args.stage=='claim':
                need(not tx_path.exists() and store.replay()[0]['sequence']==0,'claim observer missed its Workflow boundary')
                try:store.recover(key,claim['fingerprint'],host_guard=recovery_guard)
                except ValueError as error:need('no observed immutable' in str(error),'wrong pending Workflow recovery refusal')
                else:raise ValueError('Workflow claim without immutable effect was recovered')
                need(snapshot()==before,'pending Workflow recovery changed durable bytes')
                recovered=False;consumed=[]
            else:
                tx_raw=fixture.C.S.read_owned(tx_path);output_before={p.name:p.read_bytes() for p in (store.root/'outputs').iterdir()}
                tx=store.recover(key,claim['fingerprint'],host_guard=recovery_guard)
                need(fixture.C.S.read_owned(tx_path)==tx_raw and store.replay()[0]['sequence']==1,'observed Workflow recovery changed immutable transaction')
                consumed=store.consume(1)
                need({h['byte_sha256']:raw for h,raw in consumed}==output_before,'recovery lost exact actual producer originals')
                recovered=True
                after_recovery=snapshot()
                need(store.recover(key,claim['fingerprint'],host_guard=recovery_guard)==tx and snapshot()==after_recovery,
                     'exact Workflow recovery retry changed durable bytes')
                again=surface.call(P.compact(request))
                need(again.get('kind')==reply['kind'] and snapshot()==after_recovery,'observing inner Workflow effect falsely completed outer Service claim')
            write(root.parent/'cold-result.json',{'result':'PASS','stage':args.stage,'actual_common_dispatcher':True,
                'fresh_Reader_and_Service':True,'same_control_fingerprint':True,'outer_retry_kind':reply['kind'],
                'outer_retry_code':reply.get('message',{}).get('code'),'actual_inner_transaction_observed':recovered,
                'actual_typed_outputs':[h for h,raw in consumed],'no_outer_completion_invented':True,
                'no_production_crash_hook':True,'canonical_admissions':0,'authority_effect':'none'})
        finally:
            if host is not None:host.close()
            channel.close()
        G.verify(args.source_sha256)


def command(args,mode,root,stage):
    if args.launcher:prefix=[args.launcher,'-I','-B','-S']
    else:
        native=Path(args.native_root);prefix=[str(native/'lib/abi/ld-linux-x86-64.so.2'),'--inhibit-cache','--library-path',str(native/'lib/abi'),str(native/'bin/python'),'-I','-B','-S']
    return [*prefix,str(Path(__file__).resolve()),'--child',mode,'--root',str(root),'--stage',stage,
        '--api',args.api,'--source-sha256',args.source_sha256,'--profile-sha256',args.profile_sha256,'--deps',args.deps]


def run(args):
    rows=[]
    with Q.retained_case_root() as folder:
        control=Path(folder);control.chmod(0o700)
        for stage in ('claim','transaction','head','result'):
            case=control/stage;case.mkdir(mode=0o700);root=case/'fixture'
            prepare=Q.completed(command(args,'prepare',root,stage),1200)
            need(prepare.returncode==0,'actual owned Workflow fixture preparation failed: '+prepare.stderr.decode()[-4000:])
            selection=json.loads((case/'selection.json').read_bytes());policy=json.loads(Path(selection['policy_path']).read_bytes())
            vault=Path(policy['workspace']['root']);journal=vault/'workflows/design'
            libc=ctypes.CDLL(None,use_errno=True);fd=libc.inotify_init1(os.O_CLOEXEC|os.O_NONBLOCK);need(fd>=0,'Workflow observer unavailable')
            watches={}
            for directory in (journal/'claims',journal/'transactions',journal,vault/'journal'):
                wd=libc.inotify_add_watch(fd,os.fsencode(directory),0x08|0x80|0x100)
                need(wd>=0,'Workflow publication watch unavailable');watches[wd]=directory
            process=None
            try:
                process=subprocess.Popen(command(args,'effect',root,stage),stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
                Q.wait_for(process,case/'call-ready.json',1200);ready=json.loads((case/'call-ready.json').read_bytes())
                target={'claim':journal/'claims'/(ready['inner_namespace']+'.json'),
                    'transaction':journal/'transactions/00000001.json','head':journal/'HEAD.json',
                    'result':vault/'journal'/(ready['outer_namespace']+'.result.json')}[stage]
                limit=time.monotonic()+1200;observed=False
                while not observed:
                    need(process.poll() is None,'Workflow completed before requested OS interruption boundary')
                    need(time.monotonic()<limit,'Workflow interruption observer timed out')
                    if not select.select([fd],[],[],.1)[0]:continue
                    events=os.read(fd,65536);position=0
                    while position<len(events):
                        wd,mask,cookie,size=struct.unpack_from('iIII',events,position);position+=16
                        name=os.fsdecode(events[position:position+size].split(b'\0',1)[0]);position+=size
                        # Outer results publish by linking a completed fsynced
                        # temporary file. Inner claim/tx files write directly,
                        # so their CREATE event is too early to observe safely.
                        publication_mask=0x100 if stage=='result' else (0x08|0x80)
                        if watches[wd]/name==target and mask&publication_mask:observed=True
                os.killpg(process.pid,signal.SIGSTOP);pid,status=os.waitpid(process.pid,os.WUNTRACED)
                need(pid==process.pid and os.WIFSTOPPED(status),'actual Workflow child did not stop')
                value=json.loads(target.read_bytes())
                if stage=='claim':need(not (journal/'transactions/00000001.json').exists(),'missed Workflow claim-before-transaction boundary')
                if stage=='transaction':need(json.loads((journal/'HEAD.json').read_bytes())['sequence']==0,'missed Workflow transaction-before-head boundary')
                if stage=='head':need(value['sequence']==1 and not (vault/'journal'/(ready['outer_namespace']+'.result.json')).exists(),'missed Workflow head-before-outer-result boundary')
                digest=sha(target.read_bytes());os.killpg(process.pid,signal.SIGKILL);out,err=process.communicate(timeout=30)
                need(process.returncode==-signal.SIGKILL,'Workflow child not killed by OS signal')
                cold=Q.completed(command(args,'cold',root,stage),1200)
                need(cold.returncode==0,'actual cold Workflow observation failed: '+cold.stderr.decode()[-5000:])
                need(sha(target.read_bytes())==digest,'observed immutable Workflow marker changed')
                row=json.loads((case/'cold-result.json').read_bytes());row.update(actual_child_exit=process.returncode,observed_marker_sha256=digest,
                    child_stdout_bytes=len(out),child_stderr_bytes=len(err),cold_stdout_bytes=len(cold.stdout),cold_stderr_bytes=len(cold.stderr))
                rows.append(row)
            finally:
                os.close(fd)
                if process is not None and process.poll() is None:
                    os.killpg(process.pid,signal.SIGKILL);process.communicate(timeout=30)
    return {'schema_version':'lab-actual-common-owned-Workflow-OS-kill/v1','result':'PASS',
        'source_sha256':args.source_sha256,'profile_sha256':args.profile_sha256,'cases':rows,
        'probe_sha256':sha(Path(__file__).read_bytes()),'owned_cleanup':not Path(folder).exists(),
        'production_callbacks_changed':False,'clock_changed':False,'host_power_loss_qualified':False,'authority_effect':'none'}


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    for key in ('api','source-sha256','profile-sha256','deps'):parser.add_argument('--'+key,required=True)
    parser.add_argument('--launcher');parser.add_argument('--native-root');parser.add_argument('--output')
    parser.add_argument('--child',choices=('prepare','effect','cold'));parser.add_argument('--root')
    parser.add_argument('--stage',choices=('claim','transaction','head','result'))
    args=parser.parse_args()
    if args.child:child(args)
    else:
        need(bool(args.launcher)!=bool(args.native_root),'one selected native bootstrap required')
        need(args.output and not Path(args.output).exists(),'fresh terminal result required')
        result=run(args);write(Path(args.output),result);print(json.dumps({'result':result['result'],'cases':len(result['cases'])}),flush=True)
