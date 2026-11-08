"""Fixture-only adapter of reviewed packet transport and held scratch writer.

No native launcher or authentic reader. Durable ACK means the selected scratch
writer completed file/parent fsync and readback, not physical power-loss proof.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import time

from . import mapper_package_ipc_model_0004 as wire
from . import mapper_package_transport_0001 as transport
from . import mapper_package_writer_0001 as writer
from .mapper_package_runner_0005 import read


class Refusal(RuntimeError):pass

def need(ok,code):
    if not ok:raise Refusal(code)


def selected_manifest(path,expected_sha256,size):
    raw=read({'path':str(path),'sha256':expected_sha256,'size_bytes':size},1024*1024)
    value=json.loads(raw)
    need(value.get('posture')=='synthetic-only' and 'selection_sha256' not in value,'MANIFEST_DOMAIN')
    need(value.get('integration_version')=='held-writer-fixture/v1','MANIFEST_VERSION')
    need(len(value['bindings'])<=8192 and len({r['path'] for r in value['bindings']})==len(value['bindings']),'INVENTORY')
    for row in value['bindings']:read(row)
    need(value['logical_package']==writer.plan.PACKAGE,'LOGICAL_PACKAGE')
    need(value['logical_source_binding']=={'path':writer.plan.FAMILY+'/mapped/source-manifest.json','sha256':value['begin_pins']['mapper']},'LOGICAL_SOURCE')
    physical=Path(value['package'])
    need(physical.name=='0001' and physical.parent.name=='packages' and physical.parent.parent.name=='mapped','PACKAGE_PATH')
    source=physical.parent.parent/'source-manifest.json'
    need(any(r['path']==str(source) and r['sha256']==value['begin_pins']['mapper'] for r in value['bindings']),'MAPPER_SOURCE_SELECTION')
    return raw,value


class Mediator:
    def __init__(self,endpoint,peer,manifest_path,expected_sha256,size):
        self.raw,self.selection=selected_manifest(manifest_path,expected_sha256,size)
        self.selection_hash=hashlib.sha256(self.raw).hexdigest()
        self.manifest_binding={'path':str(manifest_path),'sha256':expected_sha256,'size_bytes':size}
        self.endpoint=endpoint;self.peer=peer
        self.protocol=wire.ProtocolModel(attempt_id=self.selection['attempt_id'],selection_sha256=self.selection_hash,begin_pins=self.selection['begin_pins'],peer=peer)
        self.writer=None;self.pending=None;self.failed=False;self.closed=False;self.finished=False
        self.records=[];self.deadline=time.monotonic()+60;self.sent_bytes=0;self.sent_packets=0

    def guard(self,*,full=False):
        need(read(self.manifest_binding)==self.raw,'MANIFEST_DRIFT')
        if full:
            for row in self.selection['bindings']:read(row)
        if self.writer is not None:self.writer._scan()

    def _response(self,request,payload):
        return wire.encode({'schema_version':'lab-mapper-package-ipc-response/v1','attempt_id':self.selection['attempt_id'],
            'selection_sha256':self.selection_hash,'request_sha256':wire.sha(request),
            'ordinal':wire.decode(request)['ordinal'],'status':'fixture-only','payload':payload})

    def prepare_one(self):
        need(not self.failed and not self.closed and not self.finished and self.pending is None,'MEDIATOR_UNAVAILABLE')
        try:
            remaining=self.deadline-time.monotonic();need(remaining>0,'DEADLINE');self.endpoint.settimeout(remaining)
            raw=transport.recv_frame(self.endpoint,self.peer)
            # Blob ACKs acknowledge bounded in-memory framing only. Full selected
            # inputs are checked before each semantic action and its reply.
            self.guard(full=wire.decode(raw).get('verb') not in ('BLOB_BEGIN','BLOB_CHUNK','BLOB_END'))
            ready=bytes(self.protocol.ready['data']) if self.protocol.ready else None
            action=self.protocol.receive(raw,peer=self.peer);output=None;receipt=None
            if self.protocol.pending:
                verb,target=action['verb'],action['target']
                if verb=='BEGIN':
                    self.writer=writer.PackageWriter(Path(self.selection['package']).parent.parent,self.selection['logical_source_binding'])
                    receipt={'kind':'DURABLE_PACKAGE_NAMES'}
                elif verb=='SEAL':
                    # Fixed deterministic stand-in; not a native event validator.
                    value=json.loads(ready)
                    need(set(value)=={'semantic','governance'} and len(value[target])==25 and value['governance' if target=='semantic' else 'semantic']==[],'SYNTHETIC_SEAL')
                    for event in value[target]:event['event_digest']=wire.sha(json.dumps(event,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode())
                    output=(json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
                elif verb=='EMIT':
                    need(self.writer is not None and ready is not None,'NO_WRITER')
                    receipt=self.writer.emit(target,ready)
                    need(receipt['durable_observed'] is True and receipt['sha256']==action['blob_sha256'],'DURABLE_ACK')
                elif verb=='COLD_READ':
                    output=(json.dumps({'authority_effect':'none','cut':{'semantic_cursor':25},'governance_cursor':25,'governed_nodes':[{'fixture_only':True} for _ in range(15)]},sort_keys=True,indent=2)+'\n').encode()
                elif verb=='FINISH':
                    receipt=self.writer.finish()
                    need(receipt['leaf_count']==55 and receipt['package_writer_complete'] is True,'COMPLETE_WRITER')
                else:raise Refusal('VERB')
                self.protocol.complete_synthetic(action['action_id'],success=True)
            packets=[]
            if output is None:packets.append(self._response(raw,{'kind':'ACK'}))
            else:
                need(0<len(output)<=wire.BLOB_MAX,'REPLY_BOUND')
                packets.append(self._response(raw,{'kind':'DATA_BEGIN','size_bytes':len(output),'sha256':wire.sha(output)}))
                for offset in range(0,len(output),wire.CHUNK_MAX):packets.append(self._response(raw,{'kind':'DATA_CHUNK','offset':offset,'data':base64.b64encode(output[offset:offset+wire.CHUNK_MAX]).decode()}))
                packets.append(self._response(raw,{'kind':'DATA_END','sha256':wire.sha(output)}))
            need(self.sent_bytes+sum(map(len,packets))+self.protocol.total<=wire.TOTAL_MAX and self.sent_packets+len(packets)+self.protocol.ordinal<=wire.PACKETS_MAX,'REPLY_AGGREGATE')
            self.pending={'packets':tuple(packets),'receipt':receipt,'ordinal':action['ordinal'],'request_sha256':wire.sha(raw),'action':action.get('verb'),'target':action.get('target')}
            self.guard()
            return {'ordinal':action['ordinal'],'action':action.get('verb'),'target':action.get('target'),'durable_receipt':receipt}
        except BaseException:
            self.abort();raise

    def send_pending(self):
        need(not self.failed and not self.closed and self.pending is not None,'NO_PENDING_ACK')
        try:
            self.guard(full=self.pending['action'] is not None)
            need(transport.process_start(self.peer[0])==self.peer[1],'PEER_LIFETIME')
            record=self.pending
            for raw in record['packets']:
                remaining=self.deadline-time.monotonic();need(remaining>0,'DEADLINE');self.endpoint.settimeout(remaining)
                transport.send_frame(self.endpoint,raw);self.sent_packets+=1;self.sent_bytes+=len(raw)
            self.records.append({k:v for k,v in record.items() if k!='packets'})
            self.pending=None
            self.finished=self.protocol.step==61
        except BaseException:
            self.abort();raise

    def abort(self):
        self.failed=True;self.protocol.disconnect()
        if self.writer is not None:self.writer.unknown=True
        self.close()

    def close(self):
        if self.closed:return
        self.closed=True
        if not self.finished:
            self.failed=True;self.protocol.disconnect()
            if self.writer is not None:self.writer.unknown=True
        try:self.endpoint.close()
        finally:
            if self.writer is not None:self.writer.close()
