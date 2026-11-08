"""Fixed inert namespace payload. Not launched by static/pure tests."""
import hashlib
import json
import os
import socket
import sys
import types


def main():
    # Entry source/interpreter/cache is externally guarded before launch. Fixed
    # child paths are populated from exactly the selected host originals.
    if len(sys.argv)!=2 or len(sys.argv[1])!=64:raise RuntimeError('SELECTION')
    with open('/work/control/selection.json','rb') as f:raw=f.read(1048577)
    if len(raw)>1048576 or hashlib.sha256(raw).hexdigest()!=sys.argv[1]:raise RuntimeError('SELECTION')
    selected=json.loads(raw)
    for name in ('payload','common','cache'):
        row=selected['roles'][name]
        with open('/work/control/'+name,'rb') as f:data=f.read(row['size_bytes']+1)
        if len(data)!=row['size_bytes'] or hashlib.sha256(data).hexdigest()!=row['sha256']:raise RuntimeError('ROLE_DRIFT')
    if not(sys.flags.isolated and sys.flags.no_site and sys.flags.dont_write_bytecode
           and sys.pycache_prefix=='/work/control/cache'):raise RuntimeError('RUNTIME_FLAGS')
    common=types.ModuleType('selected_probe_common')
    with open('/work/control/common','rb') as f:code=f.read(65537)
    exec(compile(code,'/work/control/common','exec'),common.__dict__)
    c=common
    for row in selected['runtime_bindings']:c.check_binding(row)
    sock=socket.socket(fileno=3)
    sock.settimeout(10)
    c.need(sock.getsockopt(socket.SOL_SOCKET,socket.SO_TYPE)==socket.SOCK_SEQPACKET,'SOCKET_TYPE')
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1)
    original={}
    challenge,controller=c.recv_packet(sock)
    envelope=c.decode(challenge);nonce=envelope.get('nonce');c.hex64(nonce)
    body=c.validate_frame(challenge,0,nonce,sys.argv[1],None)
    c.closed(body,'controller_pid controller_start controller_namespaces')
    c.number(body['controller_pid'],1);c.number(body['controller_start'],1)
    # PID0 is measurement-only. No controller admission/authority is minted.
    c.need(controller[0]==0,'UNEXPECTED_VISIBLE_CONTROLLER')
    claim=c.proc_observation(os.getpid(),original,'self-before')
    c.need(claim['pid']==1,'PAYLOAD_PID')
    hello=c.frame(1,nonce,sys.argv[1],c.sha(challenge),
                  {'claim':claim,'controller_tuple':controller,'fd_census':c.census(),
                   'originals':c.pack_child_originals(original,'self-before',claim)})
    c.send_packet(sock,hello)
    observation,controller2=c.recv_packet(sock)
    b=c.validate_frame(observation,2,nonce,sys.argv[1],c.sha(hello))
    c.closed(b,'hello_sha256 join_sha256 join_summary claim')
    c.need(b['hello_sha256']==c.sha(hello) and b['claim']=='fixed-source-consistency-only','OBSERVATION')
    c.hex64(b['join_sha256']);c.need(controller==controller2,'CONTROLLER_DRIFT')
    summary_sha=c.verify_host_join_summary(b['join_summary'],claim,body,controller,c.sha(hello),selected['overflow_ids'])
    c.need(summary_sha==b['join_sha256'],'HOST_SUMMARY_BINDING')
    after=c.proc_observation(os.getpid(),original,'self-after')
    c.need(claim==after,'SELF_DRIFT')
    receipt=c.frame(3,nonce,sys.argv[1],c.sha(observation),
                    {'observation_sha256':c.sha(observation),'controller_tuple':controller2,
                     'claim_sha256':c.sha(c.encode(after)),'fd_census':c.census(),
                     'originals':c.pack_child_originals(original,'self-after',after),
                     'join_summary_sha256':summary_sha})
    c.send_packet(sock,receipt)
    eof,_=c.recv_packet(sock,allow_eof=True);c.need(eof is None,'EXPECTED_FINAL_EOF')
    for row in selected['runtime_bindings']:c.check_binding(row)
    sock.close()


if __name__=='__main__':
    try:main()
    except BaseException:
        os.write(2,b'NAMESPACE_PAYLOAD_UNKNOWN\n')
        raise SystemExit(1)
