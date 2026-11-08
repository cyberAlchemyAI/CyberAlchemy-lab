"""Bounded real SOCK_SEQPACKET client; this version admits fixture peers only.

No native execution, file writer or host authority. All replies are explicitly
fixture-only; later actual effect admission requires a separately reviewed peer.
"""
from __future__ import annotations

import array
import base64
import os
import socket
import struct
import time

from . import mapper_package_ipc_model_0004 as wire


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
    def __init__(self, sock, *, attempt_id, selection_sha256, begin_pins, peer,
                 package_path, timeout_seconds=30):
        need(type(sock) is socket.socket and sock.family == socket.AF_UNIX
             and sock.type & 0xf == socket.SOCK_SEQPACKET, 'SOCKET_TYPE')
        need(type(peer) is tuple and len(peer) == 3 and all(type(x) is int for x in peer)
             and peer[0] > 0 and all(0 <= x <= 2**32-2 for x in peer[1:]), 'PEER')
        wire.ProtocolModel(attempt_id=attempt_id, selection_sha256=selection_sha256,
                           begin_pins=begin_pins, peer=(peer[0],1,peer[1],peer[2]))
        need(type(package_path) is str and package_path.startswith('/') and
             all(x not in ('','.','..') for x in package_path.split('/')[1:]), 'PACKAGE_PATH')
        need(type(timeout_seconds) in (int,float) and 0 < timeout_seconds <= 180, 'DEADLINE')
        self.sock=sock;self.attempt_id=attempt_id;self.selection_sha256=selection_sha256
        self.begin_pins=dict(begin_pins);self.peer=peer;self.package_path=package_path
        self.deadline=time.monotonic()+timeout_seconds;self.ordinal=0;self.step=0
        self.total=0;self.packets=0;self.failed=False;self.closed=False;self.cleanup_uncertain=False
        self.sock.set_inheritable(False)
        self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1)

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

    def _recv(self, request_hash, ordinal):
        self._time()
        raw,ancillary,flags,_=self.sock.recvmsg(wire.FRAME_MAX,
            socket.CMSG_SPACE(struct.calcsize('3i'))+socket.CMSG_SPACE(64*struct.calcsize('i')),
            socket.MSG_CMSG_CLOEXEC)
        rights,uncertain=close_rights(ancillary)
        self.cleanup_uncertain |= uncertain
        credentials=[x[2] for x in ancillary if x[:2]==(socket.SOL_SOCKET,socket.SCM_CREDENTIALS)]
        need(not rights and not uncertain and flags & (socket.MSG_TRUNC|socket.MSG_CTRUNC)==0
             and len(credentials)==1 and len(ancillary)==1 and len(credentials[0])==struct.calcsize('3i')
             and struct.unpack('3i',credentials[0])==self.peer,'PEER_MESSAGE')
        self._charge(len(raw));value=wire.decode(raw)
        wire.closed(value,('schema_version','attempt_id','selection_sha256','request_sha256','ordinal','status','payload'))
        need(value['schema_version']=='lab-mapper-package-ipc-response/v1'
             and value['attempt_id']==self.attempt_id and value['selection_sha256']==self.selection_sha256
             and value['request_sha256']==request_hash and type(value['ordinal']) is int
             and value['ordinal']==ordinal and value['status']=='fixture-only','RESPONSE_SUBJECT')
        need(type(value['payload']) is dict,'RESPONSE_PAYLOAD')
        return value['payload']

    def exchange(self, verb, payload, *, want_bytes=False):
        try:
            self._time();raw=wire.encode(wire.envelope(self.attempt_id,self.selection_sha256,self.ordinal,verb,payload))
            self._charge(len(raw));need(self.sock.send(raw)==len(raw),'SEND_PARTIAL')
            h=wire.sha(raw);ordinal=self.ordinal;answer=self._recv(h,ordinal)
            if not want_bytes:
                wire.closed(answer,('kind',));need(answer['kind']=='ACK','RESPONSE_KIND')
                self.ordinal+=1;return None
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
            self.ordinal+=1;return bytes(data)
        except Exception:
            self.failed=True
            raise Refusal('IPC_EXCHANGE_REFUSED') from None

    def _action(self, verb, target):
        need(not self.failed and self.step<len(wire.schedule()) and wire.schedule()[self.step]==(verb,target),'ACTION_ORDER')

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
        return blob

    def begin(self,pin,out):
        try:
            self._action('BEGIN','');need(pin==self.begin_pins['mapper'] and str(out)==self.package_path,'BEGIN_SUBJECT')
            self.exchange('BEGIN',self.begin_pins);self.step+=1
        except Exception:
            self.failed=True;raise Refusal('BEGIN_REFUSED') from None

    def emit(self,leaf,raw):
        try:
            blob=self._upload('EMIT',leaf,raw);self.exchange('EMIT',{'blob_id':blob,'leaf':leaf});self.step+=1
        except Exception:
            self.failed=True;raise Refusal('EMIT_REFUSED') from None

    def seal(self,raw):
        try:
            target='semantic' if self.step==1 else 'governance'
            blob=self._upload('SEAL',target,raw);value=self.exchange('SEAL',{'blob_id':blob},want_bytes=True);self.step+=1
            return value
        except Exception:
            self.failed=True;raise Refusal('SEAL_REFUSED') from None

    def cold(self,args):
        try:
            index=2 if self.step==54 else 3
            self._action('COLD_READ',index)
            need(type(args) is list and args==[self.package_path+'/'+x for x in ('semantic','governance','request.json')],'COLD_ARGUMENTS')
            value=self.exchange('COLD_READ',{'index':index},want_bytes=True);self.step+=1;return value
        except Exception:
            self.failed=True;raise Refusal('COLD_REFUSED') from None

    def finish(self,binding):
        try:
            self._action('FINISH','');wire.closed(binding,('path','sha256'))
            need(binding['path']==self.package_path+'/manifest.json' and wire.hexhash(binding['sha256']),'FINISH_BINDING')
            self.exchange('FINISH',{'manifest_sha256':binding['sha256']});self.step+=1
        except Exception:
            self.failed=True;raise Refusal('FINISH_REFUSED') from None
