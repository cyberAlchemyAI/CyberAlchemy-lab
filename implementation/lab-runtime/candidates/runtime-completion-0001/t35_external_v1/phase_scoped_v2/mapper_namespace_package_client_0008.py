"""Synthetic-only runtime client, without a namespace launcher or package writer.

The fixed bootstrap caller must acquire current observations on this same held
socket. Transcript validation is consistency, not authority or kernel provenance.
LocalFixtureClient is deliberately a separate type; the builder bridge refuses it.
"""
from __future__ import annotations

import array
import base64
import os
import hashlib
import math
import socket
import struct
import time

from . import mapper_package_ipc_model_0004 as wire
from . import mapper_namespace_package_model_0007 as composition
from . import mapper_namespace_probe_common_0004 as ns


class Refusal(ValueError):
    pass


def need(ok, code):
    if not ok: raise Refusal(code)


def close_rights(ancillary):
    """Attempt every delivered SCM_RIGHTS FD exactly once; never retry numbers."""
    present, uncertain = False, False
    for level, kind, raw in ancillary:
        if level == socket.SOL_SOCKET and kind == socket.SCM_RIGHTS:
            present = True
            fds = array.array('i')
            usable = len(raw) - len(raw) % fds.itemsize
            fds.frombytes(raw[:usable])
            uncertain |= usable != len(raw)
            for fd in fds:
                try: os.close(fd)
                except BaseException: uncertain = True
    return present, uncertain


class Client:
    def __init__(self, sock, *, selection_raw, selection_sha256, bootstrap_frames, attempt_started):
        # Own the supplied socket from entry, including failed admission. No
        # duplicate/alias is retained and no fd-number retry follows ambiguity.
        self.sock=sock;self.closed=False;self.failed=False;self.cleanup_uncertain=False
        self.activated=False;self.replies=[];self._upload_binding=None
        try:
            need(type(sock) is socket.socket and sock.family==socket.AF_UNIX
                 and sock.type & 0xf==socket.SOCK_SEQPACKET,'SOCKET_TYPE')
            now=time.monotonic()
            need(type(attempt_started) in (int,float) and math.isfinite(attempt_started)
                 and 0<=now-attempt_started<60,'ATTEMPT_DEADLINE')
            self.deadline=attempt_started+60
            model=composition.Composition(selection_raw,selection_sha256)
            self.activation_raw=model.observe_synthetic(bootstrap_frames)
            self.activation_sha=hashlib.sha256(self.activation_raw).hexdigest()
            self.host_peer=model.peer;self.child_peer=model.child_peer
            self.selection_raw=bytes(selection_raw);self.selection_sha256=selection_sha256
            self.attempt_id=model.selection['attempt_id'];self.begin_pins=dict(model.selection['begin_pins'])
            self.package_path=composition.PACKAGE
            self.peer=self._expected_receive_peer()
            self.ordinal=0;self.step=0;self.total=0;self.packets=0
            self.sock.set_inheritable(False);self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1)
        except BaseException:
            self.failed=True
            try:self.close()
            except BaseException:pass
            raise Refusal('CLIENT_ADMISSION') from None

    def _expected_receive_peer(self):
        need(self.child_peer[0]==0,'NAMESPACE_PEER')
        return self.child_peer

    def activate(self):
        try:
            need(not self.activated,'ACTIVATION_ONCE')
            raw=self._receive_packet()
            need(raw==self.activation_raw,'ACTIVATE_BYTES')
            ack=ns.encode({'schema':'mapper-namespace-package-activation-ack/v1',
                'activation_sha256':self.activation_sha,'selection_sha256':self.selection_sha256})
            self._time();self._charge(len(ack));need(self.sock.send(ack,socket.MSG_NOSIGNAL)==len(ack),'ACTIVATE_SHORT_SEND')
            self.activated=True
            return {'activated_for_synthetic_package':True,'authority':False,'host_qualified':False}
        except BaseException:
            self.failed=True;raise Refusal('ACTIVATION_REFUSED') from None

    @classmethod
    def from_fd3(cls, **kwargs):
        fd=3;sock=None
        try:
            sock=socket.socket(fileno=fd)
            return cls(sock,**kwargs)
        except BaseException:
            try:
                if sock is None:os.close(fd)
                else:sock.close()
            except BaseException:pass
            raise Refusal('FD3_ADMISSION') from None

    def close(self):
        if not self.closed:
            self.closed=True
            try:self.sock.close()
            except BaseException:self.cleanup_uncertain=True
        need(not self.cleanup_uncertain,'DESCRIPTOR_CLOSE_UNCERTAIN')

    def _time(self):
        need(not self.failed and not self.closed,'CLIENT_POISONED')
        remaining=self.deadline-time.monotonic();need(remaining>0,'DEADLINE')
        self.sock.settimeout(remaining)

    def _charge(self,n):
        self.total+=n;self.packets+=1
        need(self.total<=wire.TOTAL_MAX and self.packets<=wire.PACKETS_MAX,'TRANSPORT_BUDGET')

    def _receive_packet(self):
        self._time()
        raw,ancillary,flags,_=self.sock.recvmsg(wire.FRAME_MAX,
            socket.CMSG_SPACE(struct.calcsize('3i'))+socket.CMSG_SPACE(64*struct.calcsize('i')),
            socket.MSG_CMSG_CLOEXEC)
        rights,uncertain=close_rights(ancillary);self.cleanup_uncertain |= uncertain
        credentials=[x[2] for x in ancillary if x[:2]==(socket.SOL_SOCKET,socket.SCM_CREDENTIALS)]
        need(bool(raw) and not rights and not uncertain and flags & (socket.MSG_TRUNC|socket.MSG_CTRUNC)==0
             and len(credentials)==1 and len(ancillary)==1 and len(credentials[0])==struct.calcsize('3i')
             and struct.unpack('3i',credentials[0])==self.peer,'PEER_MESSAGE')
        self._charge(len(raw));return raw

    def _recv(self, request_hash, ordinal):
        raw=self._receive_packet();value=wire.decode(raw)
        wire.closed(value,('schema_version','attempt_id','selection_sha256','request_sha256','ordinal','status',
                           'host_peer','child_peer','completion_sha256','payload'))
        need(value['schema_version']=='lab-mapper-namespace-package-response/v1'
             and value['attempt_id']==self.attempt_id and value['selection_sha256']==self.selection_sha256
             and value['request_sha256']==request_hash and type(value['ordinal']) is int
             and value['ordinal']==ordinal and value['status']=='synthetic-projection-only'
             and wire.encode(value['host_peer'])==wire.encode(list(self.host_peer))
             and wire.encode(value['child_peer'])==wire.encode(list(self.child_peer))
             and value['completion_sha256']==self._expected_completion_sha,'RESPONSE_SUBJECT')
        need(type(value['payload']) is dict,'RESPONSE_PAYLOAD')
        self._reply_packets.append(bytes(raw));return value['payload']

    def _completion(self,verb,payload,request_hash):
        kinds={'BEGIN':'owned-names','SEAL':'deterministic-seal','COLD_READ':'deterministic-cold',
               'FINISH':'complete-55-leaf-scan','EMIT':'held-leaf'}
        leaf=sha=None;size=0
        if verb=='EMIT':
            u=self._upload_binding
            need(u is not None and u['verb']==verb and u['target']==payload['leaf']
                 and u['id']==payload['blob_id'],'UPLOAD_SUBJECT')
            leaf=u['target'];sha=u['sha256'];size=u['size_bytes']
        value={'schema':'mapper-synthetic-completion/v1','request_sha256':request_hash,
               'kind':kinds.get(verb,'memory-framing'),'leaf':leaf,'sha256':sha,'size_bytes':size,
               **{k:verb in ('BEGIN','EMIT','FINISH') for k in ('file_fsync','parent_fsync','readback','attached')}}
        return hashlib.sha256(ns.encode(value)).hexdigest()

    def _retain_reply(self,request_hash,ordinal,output):
        self.replies.append({'request_sha256':request_hash,'ordinal':ordinal,
            'packet_sha256':[hashlib.sha256(x).hexdigest() for x in self._reply_packets],
            'packet_sizes':[len(x) for x in self._reply_packets],
            'output_sha256':hashlib.sha256(output).hexdigest() if output is not None else None,
            'output_size_bytes':len(output) if output is not None else 0})
        # Raw packets belong to this request only; the immutable digest record
        # is bounded by the already charged total packet count.
        self._reply_packets=[]

    def exchange(self, verb, payload, *, want_bytes=False):
        try:
            need(self.activated,'NOT_ACTIVATED')
            self._time();raw=wire.encode(wire.envelope(self.attempt_id,self.selection_sha256,self.ordinal,verb,payload))
            h=wire.sha(raw);ordinal=self.ordinal;self._reply_packets=[]
            self._expected_completion_sha=self._completion(verb,payload,h)
            self._charge(len(raw));need(self.sock.send(raw,socket.MSG_NOSIGNAL)==len(raw),'SEND_PARTIAL')
            answer=self._recv(h,ordinal)
            if not want_bytes:
                wire.closed(answer,('kind',));need(answer['kind']=='ACK','RESPONSE_KIND')
                self._retain_reply(h,ordinal,None);self.ordinal+=1;return None
            wire.closed(answer,('kind','size_bytes','sha256'))
            need(answer['kind']=='DATA_BEGIN' and wire.integer(answer['size_bytes'],1,wire.BLOB_MAX)
                 and wire.hexhash(answer['sha256']),'RESPONSE_BLOB')
            expected_size=answer['size_bytes'];expected_sha=answer['sha256'];data=bytearray()
            while len(data)<expected_size:
                chunk=self._recv(h,ordinal);wire.closed(chunk,('kind','offset','data'))
                need(chunk['kind']=='DATA_CHUNK' and type(chunk['offset']) is int
                     and chunk['offset']==len(data) and type(chunk['data']) is str
                     and len(chunk['data'])<=4*((wire.CHUNK_MAX+2)//3),'RESPONSE_CHUNK')
                decoded=base64.b64decode(chunk['data'],validate=True)
                need(0<len(decoded)<=wire.CHUNK_MAX and len(data)+len(decoded)<=expected_size
                     and base64.b64encode(decoded).decode()==chunk['data'],'RESPONSE_CHUNK')
                data.extend(decoded)
            ending=self._recv(h,ordinal);wire.closed(ending,('kind','sha256'))
            need(ending['kind']=='DATA_END' and ending['sha256']==expected_sha==wire.sha(data),'RESPONSE_DIGEST')
            output=bytes(data);self._retain_reply(h,ordinal,output);self.ordinal+=1;return output
        except BaseException:
            self.failed=True
            raise Refusal('IPC_EXCHANGE_REFUSED') from None

    def _action(self, verb, target):
        need(self.activated and not self.failed and self.step<len(wire.schedule()) and wire.schedule()[self.step]==(verb,target),'ACTION_ORDER')

    def _upload(self, verb, target, raw):
        self._action(verb,target)
        cap=wire.EVENT_MAX if verb=='EMIT' and '/' in target else wire.BLOB_MAX
        need(type(raw) is bytes and 0<len(raw)<=cap,'UPLOAD_BOUND')
        blob=self.ordinal
        self.exchange('BLOB_BEGIN',{'size_bytes':len(raw),'sha256':wire.sha(raw),'purpose':verb,'target':target})
        for offset in range(0,len(raw),wire.CHUNK_MAX):
            self.exchange('BLOB_CHUNK',{'blob_id':blob,'offset':offset,
                'data':base64.b64encode(raw[offset:offset+wire.CHUNK_MAX]).decode()})
        self.exchange('BLOB_END',{'blob_id':blob})
        self._upload_binding={'id':blob,'verb':verb,'target':target,'size_bytes':len(raw),'sha256':wire.sha(raw)}
        return blob

    def begin(self,pin,out):
        try:
            self._action('BEGIN','');need(pin==self.begin_pins['mapper'] and str(out)==self.package_path,'BEGIN_SUBJECT')
            self.exchange('BEGIN',self.begin_pins);self.step+=1
        except BaseException:
            self.failed=True;raise Refusal('BEGIN_REFUSED') from None

    def emit(self,leaf,raw):
        try:
            blob=self._upload('EMIT',leaf,raw);self.exchange('EMIT',{'blob_id':blob,'leaf':leaf});self.step+=1
        except BaseException:
            self.failed=True;raise Refusal('EMIT_REFUSED') from None

    def seal(self,raw):
        try:
            target='semantic' if self.step==1 else 'governance'
            blob=self._upload('SEAL',target,raw);value=self.exchange('SEAL',{'blob_id':blob},want_bytes=True);self.step+=1
            return value
        except BaseException:
            self.failed=True;raise Refusal('SEAL_REFUSED') from None

    def cold(self,args):
        try:
            index=2 if self.step==54 else 3
            self._action('COLD_READ',index)
            need(type(args) is list and args==[self.package_path+'/'+x for x in ('semantic','governance','request.json')],'COLD_ARGUMENTS')
            value=self.exchange('COLD_READ',{'index':index},want_bytes=True);self.step+=1;return value
        except BaseException:
            self.failed=True;raise Refusal('COLD_REFUSED') from None

    def finish(self,binding):
        try:
            self._action('FINISH','');wire.closed(binding,('path','sha256'))
            need(binding['path']==self.package_path+'/manifest.json' and wire.hexhash(binding['sha256']),'FINISH_BINDING')
            self.exchange('FINISH',{'manifest_sha256':binding['sha256']});self.step+=1
        except BaseException:
            self.failed=True;raise Refusal('FINISH_REFUSED') from None


class LocalFixtureClient(Client):
    """Same-process/socketpair transport tests ONLY; bridge rejects this type.

    Namespace transcript peer views remain explicitly synthetic in these tests.
    The actual kernel tuple is separately selected to this local process; this
    class never establishes namespace currentness or actual Builder eligibility.
    """
    def _expected_receive_peer(self):
        return (os.getpid(),os.getuid(),os.getgid())

    @classmethod
    def from_fd3(cls,**kwargs):
        raise Refusal('LOCAL_FIXTURE_NO_FD3')
