"""Exact Stage2 pump projection; transfer live socket/pidfd after receipt, no EOF."""
import os,select,selectors,time
from . import mapper_namespace_probe_common_0004 as C
from . import mapper_namespace_probe_controller_0004 as original
original.C=C
exited=original.exited
append_stream=original.append_stream
snapshot_streams=original.snapshot_streams
census_valid=original.census_valid
user_parent=original.user_parent
check_overflow=original.check_overflow

def retain_child_originals(root,phase,originals):
    C.need(phase in ('before','after'),'RETAIN_PHASE');bindings={};readback={}
    for name,raw in originals.items():
        C.need(name in C.CHILD_FILES,'RETAIN_NAME');leaf='child-'+phase+'-'+name
        root.write(leaf,raw);data,inode=original.retained_read(root.fds[''],leaf,C.CHILD_FILES[name]);readback[name]=data
        bindings[name]={'name':leaf,'sha256':C.sha(data),'size_bytes':len(data),'inode':inode}
    C.validate_child_readback(originals,readback);return bindings

def pump(sock,ready,out,err,pid,pidfd,controller,manifest_sha,nonce,exe_binding,deadline,originals,trace,state,root,overflow,streams):
    sel=selectors.DefaultSelector();payload_fd=-1
    received=0;queued=None;previous=None;claim=None;hello=None;joined=None;before=None;wrapper=None
    try:
        for fd,name in ((ready,'ready'),(out,'stdout'),(err,'stderr'),(sock.fileno(),'wire')):
            os.set_blocking(fd,False);sel.register(fd,selectors.EVENT_READ,name)
        while time.monotonic()<deadline:
            C.need(not exited(pidfd),'WRAPPER_EARLY_EXIT')
            for key,mask in sel.select(min(.02,max(0,deadline-time.monotonic()))):
                name=key.data
                if name in streams:
                    data=os.read(key.fd,4096)
                    if not data:sel.unregister(key.fd)
                    else:
                        try:append_stream(streams,name,data)
                        except C.Refusal:
                            state['pump_stream_overflow']=True;raise
                elif name=='ready':
                    C.need(os.read(ready,2)==b'S' and not state['established'],'READY')
                    state['established']=True;sel.unregister(ready)
                    r=C.parse_stat(C.read_regular(f'/proc/{pid}/stat',4096)[0])
                    C.need(r['pgrp']==pid and r['session']==pid,'SESSION')
                    wrapper={'pid':pid,'start':r['start']};state['wrapper']=wrapper
                    queued=C.frame(0,nonce,manifest_sha,None,{'controller_pid':controller['pid'],'controller_start':controller['start'],'controller_namespaces':controller['namespaces']})
                    sel.modify(sock.fileno(),selectors.EVENT_READ|selectors.EVENT_WRITE,'wire')
                elif name=='wire':
                    if mask & selectors.EVENT_WRITE and queued is not None:
                        try:C.send_packet(sock,queued)
                        except BlockingIOError:continue
                        trace.append({'direction':'controller','raw_hex':queued.hex()});previous=C.sha(queued);queued=None
                        sel.modify(sock.fileno(),selectors.EVENT_READ,'wire')
                    if mask & selectors.EVENT_READ:
                        C.need(state['established'] and queued is None,'UNEXPECTED_EARLY_FRAME')
                        raw,creds=C.recv_packet(sock);trace.append({'direction':'payload','raw_hex':raw.hex(),'credentials':creds})
                        C.need(sum(len(bytes.fromhex(t['raw_hex'])) for t in trace)<=49152 and len(trace)<=4,'WIRE_BUDGET')
                        if received==0:
                            b=C.validate_frame(raw,1,nonce,manifest_sha,previous);C.closed(b,'claim controller_tuple fd_census originals')
                            claim=b['claim'];census_valid(b['fd_census'])
                            child_before=C.verify_child_originals(b['originals'],'self-before',claim)
                            C.need(type(b['controller_tuple']) is list and len(b['controller_tuple'])==3 and b['controller_tuple'][0]==0,'CONTROLLER_MEASUREMENT')
                            for x in b['controller_tuple']:C.number(x,0,(1<<32)-2)
                            # Host UID/GID mapping into child, including unmapped overflow IDs,
                            # is measured, not treated as authenticated controller authority.
                            state['controller_tuple']=b['controller_tuple']
                            C.number(creds[0],1,(1<<31)-1)
                            pre=C.parse_stat(C.read_regular(f'/proc/{creds[0]}/stat',4096)[0]);payload_fd=os.pidfd_open(creds[0])
                            post=C.parse_stat(C.read_regular(f'/proc/{creds[0]}/stat',4096)[0])
                            C.need(pre['start']==post['start'] and not select.select([payload_fd],[],[],0)[0],'PAYLOAD_PIDFD')
                            C.need(user_parent(creds[0])==controller['namespaces']['user'],'USER_PARENT')
                            before=C.ancestry(creds[0],wrapper,originals,'hello-before')
                            after=C.ancestry(creds[0],wrapper,originals,'hello-after')
                            C.need(before[0]['start']==pre['start'],'PAYLOAD_START')
                            hello=C.sha(raw)
                            summary=C.host_join_summary(controller,before,after,claim,creds,exe_binding[0],exe_binding[1],
                                                        user_parent(creds[0]),overflow,b['controller_tuple'],hello)
                            joined=C.sha(C.encode(summary))
                            state['child_before']=retain_child_originals(root,'before',child_before)
                            state['host_join_summary']=summary
                            state['payload_credentials']=creds
                            state['payload_before']=before;state['payload_claim']=claim
                            queued=C.frame(2,nonce,manifest_sha,hello,{'hello_sha256':hello,'join_sha256':joined,'join_summary':summary,'claim':'fixed-source-consistency-only'})
                            received=1;sel.modify(sock.fileno(),selectors.EVENT_READ|selectors.EVENT_WRITE,'wire')
                        else:
                            C.need(received==1,'EXTRA_FRAME')
                            b=C.validate_frame(raw,3,nonce,manifest_sha,previous)
                            C.closed(b,'observation_sha256 controller_tuple claim_sha256 fd_census originals join_summary_sha256')
                            C.need(b['observation_sha256']==previous and b['controller_tuple']==state['controller_tuple']
                                   and b['claim_sha256']==C.sha(C.encode(claim)) and b['join_summary_sha256']==joined,'RECEIPT_JOIN')
                            census_valid(b['fd_census'])
                            child_after=C.verify_child_originals(b['originals'],'self-after',claim)
                            C.need(not select.select([payload_fd],[],[],0)[0],'PAYLOAD_DEAD')
                            repeat=C.ancestry(creds[0],wrapper,originals,'receipt-after')
                            C.need(creds==state['payload_credentials'],'CREDENTIAL_DRIFT')
                            C.join(controller,before,repeat,claim,creds,exe_binding[0],exe_binding[1])
                            C.need(user_parent(creds[0])==controller['namespaces']['user'],'USER_PARENT_DRIFT')
                            current=C.proc_observation(os.getpid(),originals,'controller-after')
                            C.need(controller==current,'CONTROLLER_DRIFT')
                            C.validate_controller_tuple(b['controller_tuple'],current,repeat[0],overflow)
                            check_overflow(overflow,originals,'after')
                            state['child_after']=retain_child_originals(root,'after',child_after)
                            original.verify_retained_child(root.fds[''],state['child_before']);original.verify_retained_child(root.fds[''],state['child_after'])
                            # Child remains alive waiting for this EOF until all repeated joins pass.
                            state['payload_pidfd']=payload_fd;payload_fd=-1
                            state['received_complete']=True;state['join_sha256']=joined
                            state['child_original_coordinates']={'before':b['originals']['observer_pidns'],'user':b['originals']['observer_userns']}
                            return streams
        raise C.Refusal('ATTEMPT_DEADLINE')
    finally:
        snapshot_streams(state,streams)
        if payload_fd>=0:os.close(payload_fd)
        sel.close()
