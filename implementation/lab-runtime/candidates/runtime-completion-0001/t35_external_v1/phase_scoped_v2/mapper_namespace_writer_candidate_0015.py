"""One-shot synthetic namespace/package composition. Effect is NOT run on import."""
import json,os,select,socket,stat,sys,time
from . import mapper_namespace_probe_common_0004 as ns
from . import mapper_namespace_probe_controller_0004 as original
from . import mapper_namespace_writer_resources_0015 as owned
from . import mapper_namespace_writer_pump_0014 as bridge
from . import mapper_namespace_package_runner_0010 as runner
from . import mapper_namespace_package_model_0007 as model
from . import mapper_namespace_package_mediator_0011 as mediator
original.C=ns
Refusal=mediator.Refusal
transport=mediator.transport
SCRATCH=owned.SCRATCH
EVIDENCE=owned.EVIDENCE

def need(ok,code):
    if not ok:raise RuntimeError(code)


def validate_plan(plan):
    ns.closed(plan,'schema scratch evidence manifest_raw_hex manifest_sha256 copies leaves')
    need(plan['schema']=='mapper-namespace-writer-plan/v1' and plan['scratch']==SCRATCH and plan['evidence']==EVIDENCE,'PLAN_DOMAIN')
    raw=bytes.fromhex(plan['manifest_raw_hex']);selected=runner.admit_manifest(raw,plan['manifest_sha256'])
    need(selected['attempt_id']==owned.ATTEMPT and selected['scratch_root']==SCRATCH,'PLAN_ROOT')
    rows={r['id']:r for r in selected['files']};expected={r['host_path']:(r['sha256'],r['size_bytes']) for r in selected['files'] if r['view']!='runtime'}
    expected[SCRATCH+'/control/selection.json']=(ns.sha(raw),len(raw));seen=set()
    need(type(plan['copies'])is list and len(plan['copies'])==len(expected),'COPY_COUNT')
    for row in plan['copies']:
        ns.closed(row,'path raw_hex');data=bytes.fromhex(row['raw_hex'])
        need(row['path'] not in seen and expected.get(row['path'])==(ns.sha(data),len(data)),'COPY_BYTES');seen.add(row['path'])
    leaves={k:bytes.fromhex(v) for k,v in plan['leaves'].items()}
    need(leaves==owned.planned_package(selected['begin_pins']['mapper']),'EXACT_55_LEAVES')
    fixture=rows[selected['roles']['fixture_config']]
    config=json.loads(next(bytes.fromhex(c['raw_hex']) for c in plan['copies'] if c['path']==fixture['host_path']))
    need(config=={'schema':'mapper-fixed-synthetic-leaves/v1','leaves':plan['leaves']},'FIXTURE_CONFIG')
    return selected,raw,leaves


def preflight(plan):
    selected,raw,leaves=validate_plan(plan);owned.single_thread()
    need(sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode,'PARENT_RUNTIME')
    for path in (SCRATCH,EVIDENCE):need(not os.path.lexists(path),'ALREADY_CONSUMED')
    for row in selected['files']:
        if row['view']=='runtime':runner.read_exact(row['host_path'],row['sha256'],row['size_bytes'])
    projection=model.launch_projection(raw,plan['manifest_sha256'])
    need('--bind' not in projection['argv'] and '--dev-bind' not in projection['argv'],'READ_ONLY_CHILD')
    return projection


def live_join(state,pidfd,controller,originals,interpreter):
    fd=state['payload_pidfd'];need(not select.select([fd],[],[],0)[0],'PAYLOAD_DEAD')
    need(not original.exited(pidfd),'WRAPPER_DEAD')
    before=state['payload_before'];wrapper=state['wrapper'];creds=state['payload_credentials']
    current=ns.ancestry(creds[0],wrapper,originals,'package-current')
    ns.join(controller,before,current,state['payload_claim'],creds,interpreter[0],interpreter[1])
    need(original.user_parent(creds[0])==controller['namespaces']['user'],'USER_PARENT_DRIFT')
    return (creds[0],before[0]['start'],creds[1],creds[2])



class LiveMediator(mediator.Mediator):
    """Fixed held-lineage adapter, not a worker-supplied currentness callback.

    This is userspace observation immediately before effect/send, not an atomic
    kernel authorization primitive or exclusion of same-UID mutation afterward.
    """
    def __init__(self,*args,state,pidfd,controller,originals,interpreter,**kwargs):
        self._held=(state,pidfd,controller,originals,interpreter)
        super().__init__(*args,**kwargs)
        try:self._live_guard()
        except BaseException:self.abort();raise mediator.Refusal('LIVE_ADMISSION_UNKNOWN') from None

    def _live_guard(self):
        need(live_join(*self._held)==self.peer,'LIVE_PEER_DRIFT')

    def _time(self):
        # Base calls this after blocking receive and before every packet send,
        # then again after send. Keep its deadline/start check as well.
        super()._time();self._live_guard()

    def prepare_one(self):
        try:
            need(self.model.phase=='PACKAGE' and self.pending is None and not self.finished,'PACKAGE_PHASE')
            self._guard();self._time();raw=transport.recv_frame(self.endpoint,self.transport_peer)
            # A blocking receive is a drift window: recheck before any write.
            self._guard();self._time()
            ready=bytes(self.model.protocol.ready['data']) if self.model.protocol.ready else None
            action=self.model.receive_synthetic(raw,peer=self.peer,current_selection_sha=self.sha)
            verb=action.get('verb');receipt=None;output=None
            # Retain the pending original before any writer action. Any failure
            # leaves UNKNOWN; never replay or erase an already durable leaf.
            self.pending={'request':bytes(raw),'action':dict(action),'receipt':None,'prepared':None}
            if verb=='BEGIN':
                need(self.writer is None,'WRITER_ONCE');self._live_guard();self.writer=self._open_writer();self.writer._scan()
                receipt={'kind':'durable-owned-names'}
            elif verb=='EMIT':
                need(self.writer is not None and ready is not None,'WRITER_MISSING')
                self._live_guard();receipt=self.writer.emit(action['target'],ready)
                self.pending['receipt']=receipt
                need(receipt.get('durable_observed') is True and type(receipt.get('size'))is int,'DURABLE_TYPES')
                need(receipt=={'path':action['target'],'sha256':action['blob_sha256'],'size':action['size_bytes'],'durable_observed':True},'DURABLE_RECEIPT')
            elif verb=='FINISH':
                need(self.writer is not None,'WRITER_MISSING');self._live_guard();receipt=self.writer.finish();self.pending['receipt']=receipt
                need(receipt['leaf_count']==55 and receipt['manifest_row_count']==54 and receipt['package_writer_complete'] is True,'FINAL_SCAN')
            elif verb=='SEAL':output=self._seal(ready,action['target'])
            elif verb=='COLD_READ':
                output=(json.dumps({'authority_effect':'none','cut':{'semantic_cursor':25},'governance_cursor':25,
                    'governed_nodes':[{'fixture_only':True} for _ in range(15)]},sort_keys=True,indent=2)+'\n').encode()
            elif verb is not None:raise Refusal('VERB')
            self.pending['receipt']=receipt
            kinds={None:'memory-framing','BEGIN':'owned-names','SEAL':'deterministic-seal','COLD_READ':'deterministic-cold','FINISH':'complete-55-leaf-scan','EMIT':'held-leaf'}
            completion={'schema':'mapper-synthetic-completion/v1','request_sha256':action['request_sha256'],'kind':kinds[verb],
                'leaf':action['target'] if verb=='EMIT' else None,'sha256':action['blob_sha256'] if verb=='EMIT' else None,
                'size_bytes':action['size_bytes'] if verb=='EMIT' else 0,
                **{k:verb in ('BEGIN','EMIT','FINISH') for k in ('file_fsync','parent_fsync','readback','attached')}}
            self._guard()
            self.pending['prepared']=self.model.prepare_reply_synthetic(completion,output=output)
            return {'ordinal':action['ordinal'],'verb':verb,'receipt':receipt}
        except BaseException:self.abort();raise Refusal('PREPARE_UNKNOWN') from None

def result_streams(group,pipes,streams,state):
    errors=original.drain_streams(pipes,streams,state)
    need(os.WIFEXITED(group['status']) and os.WEXITSTATUS(group['status'])==0,'CHILD_EXIT')
    need(not errors and not streams['stderr'],'CHILD_STREAMS')
    expected={'schema':'mapper-namespace-runner-result/v1','synthetic_only':True,'actions':61,'host_qualified':False}
    need(bytes(streams['stdout'])==(json.dumps(expected,sort_keys=True)+'\n').encode(),'CHILD_RESULT')


def execute(plan):
    projection=preflight(plan);selected,raw,leaves=validate_plan(plan);started=time.monotonic();end=started+60
    evidence=owned.OwnedTree(EVIDENCE);scratch=None;server=None;parent=child=None
    pid=None;pidfd=-1;exe=-1;fds=[];pipes=[];state={'established':False};streams={'stdout':bytearray(),'stderr':bytearray()}
    trace=[];originals={};group=None;primary=None;uncertain=False;drained=False
    try:
        evidence.write('admission.json',owned.pretty({'selection_sha256':plan['manifest_sha256'],'fixture_only':True,'effect':'one-synthetic-namespace-package'}))
        scratch=owned.OwnedTree(SCRATCH)
        for row in plan['copies']:
            owned.deadline(end);scratch.write(row['path'][len(SCRATCH)+1:],bytes.fromhex(row['raw_hex']))
        rows={r['id']:r for r in selected['files']};bwrap=rows[selected['roles']['bwrap']];python=rows[selected['roles']['interpreter']]
        exe=os.open(bwrap['host_path'],os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
        need(ns.identity(os.fstat(exe))==ns.check_binding({'path':bwrap['host_path'],'sha256':bwrap['sha256'],'size_bytes':bwrap['size_bytes']})[1],'BWRAP_IDENTITY')
        pyraw,pyid=ns.check_binding({'path':python['host_path'],'sha256':python['sha256'],'size_bytes':python['size_bytes']});interp=(ns.sha(pyraw),pyid)
        controller=ns.proc_observation(os.getpid(),originals,'controller-before');overflow={'uid':65534,'gid':65534};original.check_overflow(overflow,originals,'before')
        parent,child=socket.socketpair(socket.AF_UNIX,socket.SOCK_SEQPACKET|socket.SOCK_CLOEXEC)
        for sock in (parent,child):sock.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1)
        ready_r,ready_w=os.pipe2(os.O_CLOEXEC);out_r,out_w=os.pipe2(os.O_CLOEXEC);err_r,err_w=os.pipe2(os.O_CLOEXEC);null=os.open('/dev/null',os.O_RDONLY|os.O_CLOEXEC)
        fds=[ready_r,ready_w,out_r,out_w,err_r,err_w,null];pipes=[(out_r,'stdout'),(err_r,'stderr')]
        scratch.attached();evidence.attached();owned.single_thread();owned.deadline(end)
        pid=original.launch(projection['argv'],exe,child.fileno(),null,out_w,err_w,ready_w);pidfd=os.pidfd_open(pid)
        for fd in (ready_w,out_w,err_w,null):fds.remove(fd);os.close(fd)
        child.close();child=None
        bridge.pump(parent,ready_r,out_r,err_r,pid,pidfd,controller,plan['manifest_sha256'],selected['nonce'],interp,end,originals,trace,state,evidence,overflow,streams)
        need(len(trace)==4 and state['received_complete'],'BOOTSTRAP_COMPLETE')
        frames=[bytes.fromhex(t['raw_hex']) for t in trace]
        peer=live_join(state,pidfd,controller,originals,interp)
        server=LiveMediator(parent,state=state,pidfd=pidfd,controller=controller,originals=originals,interpreter=interp,selection_raw=raw,selection_sha256=plan['manifest_sha256'],selection_binding={'path':SCRATCH+'/control/selection.json','sha256':plan['manifest_sha256'],'size_bytes':len(raw)},bootstrap_frames=frames,host_peer=peer,attempt_started=started)
        server.activate()
        while not server.finished:
            owned.deadline(end);scratch.attached();evidence.attached();live_join(state,pidfd,controller,originals,interp)
            server.prepare_one();owned.deadline(end);live_join(state,pidfd,controller,originals,interp);server.send_pending()
        need(server.writer.finished and server.writer.index==55 and not server.writer.unknown,'WRITER_COMPLETE')
        server.writer._scan()
        for name,data in leaves.items():runner.read_exact(SCRATCH+'/output/legacy-fixture-source/mapped/packages/0001/'+name,ns.sha(data),len(data))
        # Success is not returned while an original-group child remains unaccounted.
        parent.shutdown(socket.SHUT_RDWR)
        group=original.cleanup(pid,pidfd,True,False);pid=None
        result_streams(group,pipes,streams,state);drained=True
        scratch.attached();evidence.attached()
    except BaseException as exc:primary=type(exc).__name__
    finally:
        if pid is not None:
            try:
                if pidfd>=0:group=original.cleanup(pid,pidfd,state['established'],True);pid=None
                else:
                    # Direct unreaped fork child is owned; no foreign PID adoption.
                    os.kill(pid,9);limit=time.monotonic()+3
                    while time.monotonic()<limit:
                        if os.waitpid(pid,os.WNOHANG)[0]==pid:pid=None;break
                        time.sleep(.02)
                    uncertain=True
            except BaseException:uncertain=True
        if pipes and not drained:
            try:uncertain |= bool(original.drain_streams(pipes,streams,state))
            except BaseException:uncertain=True
        if server is not None:
            try:server.close()
            except BaseException:uncertain=True
            uncertain |= server.cleanup_uncertain;parent=None
        for resource in (parent,child,scratch):
            if resource is not None:
                try:resource.close()
                except BaseException:uncertain=True
        uncertain |= bool(scratch and scratch.uncertain)
        for fd in fds+[exe,pidfd,state.get('payload_pidfd',-1)]:
            if fd>=0:
                try:os.close(fd)
                except BaseException:uncertain=True
        records=[] if server is None else [{**r,**({'record_raw':r['record_raw'].hex()} if 'record_raw' in r else {})} for r in server.records]
        seal=None
        try:
            observations={'wire':trace,'proc':{k:v.hex() for k,v in originals.items()},'state':{k:v for k,v in state.items() if k!='payload_pidfd'},'group':group,'receipts':records,'same_uid_excluded':False,'escaped_processes_excluded':False,'host_qualified':False}
            data=owned.pretty(observations);need(len(data)<=4*1024*1024,'OBSERVATION_BOUND');evidence.write('observations.json',data)
            evidence.write('terminal.json',owned.pretty({'result':'UNKNOWN','status':'PROVISIONAL_AWAITING_POSTCLOSE_AND_DISPATCH','primary_type':primary,'cleanup_uncertain':uncertain,'consumed':True,'host_qualified':False}));seal=evidence.snapshot()
        finally:evidence.close()
        uncertain |= evidence.uncertain
    need(primary is None and not uncertain and seal is not None,'NAMESPACE_PACKAGE_UNKNOWN')
    owned.verify_closed_evidence(seal)
    return {'result':'PASS','fixture_only':True,'actions':61,'leaves':55,'host_qualified':False,'same_uid_excluded':False,'escaped_processes_excluded':False}
