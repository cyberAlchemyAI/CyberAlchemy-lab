"""Fixed parent ACTIVATE/codec/writer adapter. No launcher or native authority.

A future fixed controller must supply CURRENT bootstrap frames and independent
host peer lineage on this same socket. No stale transcript is a capability.
"""
import hashlib
import json
import math
from pathlib import Path
import socket
import time
from . import mapper_namespace_probe_common_0004 as ns
from . import mapper_namespace_package_model_0007 as composition
from . import mapper_package_ipc_model_0004 as wire
from . import mapper_package_transport_0001 as transport
from . import mapper_namespace_package_runner_0010 as runner


class Refusal(RuntimeError):pass

def need(ok,code):
    if not ok:raise Refusal(code)


class Mediator:
    def __init__(self,endpoint,*,selection_raw,selection_sha256,selection_binding,bootstrap_frames,host_peer,attempt_started):
        self.endpoint=endpoint;self.writer=None;self.pending=None;self.records=[]
        self.failed=False;self.closed=False;self.finished=False;self.cleanup_uncertain=False
        self.raw=bytes(selection_raw);self.sha=selection_sha256
        try:
            self.selection=runner.admit_manifest(selection_raw,selection_sha256)
            ns.closed(selection_binding,'path sha256 size_bytes')
            need(selection_binding=={'path':self.selection['scratch_root']+'/control/selection.json','sha256':self.sha,'size_bytes':len(self.raw)},'SELECTION_BINDING')
            self.binding=dict(selection_binding)
            need(type(endpoint)is socket.socket and endpoint.family==socket.AF_UNIX
                 and endpoint.getsockopt(socket.SOL_SOCKET,socket.SO_TYPE)==socket.SOCK_SEQPACKET,'SOCKET')
            need(type(attempt_started) in (int,float) and math.isfinite(attempt_started)
                 and 0<=time.monotonic()-attempt_started<600,'DEADLINE')
            self.deadline=attempt_started+600
            self.model=composition.Composition(self.raw,self.sha)
            self.activation=self.model.observe_synthetic(bootstrap_frames)
            need(type(host_peer)is tuple and len(host_peer)==4 and all(type(v)is int for v in host_peer)
                 and host_peer==self.model.peer,'HOST_LINEAGE_JOIN')
            self.peer=host_peer;self.transport_peer=self._transport_peer()
            endpoint.set_inheritable(False);endpoint.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1)
            self._guard()
        except BaseException:
            self.abort();raise Refusal('MEDIATOR_ADMISSION') from None

    def _transport_peer(self):return self.peer

    def _time(self):
        need(not self.failed and not self.closed,'MEDIATOR_UNAVAILABLE')
        left=self.deadline-time.monotonic();need(left>0,'DEADLINE');self.endpoint.settimeout(left)
        need(transport.process_start(self.transport_peer[0])==self.transport_peer[1],'PEER_LIFETIME')

    def _guard(self):
        need(runner.read_exact(self.binding['path'],self.sha,len(self.raw),1048576)==self.raw,'SELECTION_DRIFT')
        for row in self.selection['files']:
            runner.read_exact(row['host_path'],row['sha256'],row['size_bytes'])
        if self.writer is not None:self.writer._scan()

    def _open_writer(self):
        # Fixed body, never a worker-selected factory. The controller must pin
        # this imported module and its complete held-path dependency closure.
        from .mapper_package_writer_0001 import PackageWriter
        return PackageWriter(Path(self.selection['scratch_root'])/'output/legacy-fixture-source/mapped',
            {'path':composition.FAMILY+'/mapped/source-manifest.json','sha256':self.selection['begin_pins']['mapper']})

    def activate(self):
        try:
            need(self.model.phase=='WAIT_ACTIVATION_ACK','ACTIVATION_PHASE')
            self._guard();self._time();transport.send_frame(self.endpoint,self.activation)
            self._time();raw=transport.recv_frame(self.endpoint,self.transport_peer)
            self.model.acknowledge_activation_synthetic(ns.decode(raw),peer=self.peer)
            self._guard()
            self.records.append({'kind':'activation','activation_sha256':ns.sha(self.activation),'ack_sha256':ns.sha(raw)})
        except BaseException:self.abort();raise Refusal('ACTIVATION_UNKNOWN') from None

    @staticmethod
    def _seal(raw,target):
        need(type(raw)is bytes and 0<len(raw)<=wire.BLOB_MAX,'SEAL_BOUND')
        def pairs(items):
            out={}
            for k,v in items:need(k not in out,'SEAL_DUPLICATE');out[k]=v
            return out
        value=json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:need(False,'SEAL_NUMBER'))
        need(type(value)is dict and set(value)=={'semantic','governance'},'SEAL_SCHEMA')
        need(type(value[target])is list and len(value[target])==25 and value['governance' if target=='semantic' else 'semantic']==[],'SEAL_PROJECTION')
        for event in value[target]:
            need(type(event)is dict,'SEAL_EVENT');event['event_digest']=ns.sha(ns.encode(event))
        return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()

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
                need(self.writer is None,'WRITER_ONCE');self.writer=self._open_writer();self.writer._scan()
                receipt={'kind':'durable-owned-names'}
            elif verb=='EMIT':
                need(self.writer is not None and ready is not None,'WRITER_MISSING')
                receipt=self.writer.emit(action['target'],ready)
                self.pending['receipt']=receipt
                need(receipt.get('durable_observed') is True and type(receipt.get('size'))is int,'DURABLE_TYPES')
                need(receipt=={'path':action['target'],'sha256':action['blob_sha256'],'size':action['size_bytes'],'durable_observed':True},'DURABLE_RECEIPT')
            elif verb=='FINISH':
                need(self.writer is not None,'WRITER_MISSING');receipt=self.writer.finish();self.pending['receipt']=receipt
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

    def send_pending(self):
        try:
            need(self.pending is not None and self.pending['prepared'] is not None,'NO_PENDING')
            prepared=self.pending['prepared'];sent=[]
            for packet in prepared['packets']:
                self._guard();self._time();transport.send_frame(self.endpoint,packet);sent.append(bytes(packet))
            self._guard();self._time()
            record=ns.decode(prepared['record_raw'],65536)
            observation={'schema':'mapper-synthetic-send-observation/v1','prepared_reply_sha256':prepared['record_sha256'],
                'sent_packets':tuple(sent),**{k:record[k] for k in ('ordinal','host_peer','child_peer','packet_sha256','packet_sizes','size_bytes','output_sha256')}}
            self.model.acknowledge_reply_synthetic(observation,current_selection_sha=self.sha)
            self.records.append({'kind':'package-reply','request_sha256':ns.sha(self.pending['request']),
                'prepared_reply_sha256':prepared['record_sha256'],'record_raw':prepared['record_raw'],
                'writer_receipt':self.pending['receipt']})
            self.pending=None;self.finished=self.model.phase=='WAIT_CHILD_EXIT'
        except BaseException:self.abort();raise Refusal('SEND_UNKNOWN') from None

    def abort(self):
        self.failed=True
        if hasattr(self,'model'):self.model.fail('PARENT_UNKNOWN')
        if self.writer is not None:self.writer.unknown=True
        self.close()

    def close(self):
        if self.closed:return
        self.closed=True
        if not self.finished:
            self.failed=True
            if hasattr(self,'model'):self.model.fail('PARENT_CLOSED_UNKNOWN')
            if self.writer is not None:self.writer.unknown=True
        # Attempt independent owned resources once; no fd-number retry.
        for resource in (self.endpoint,self.writer):
            if resource is not None:
                try:resource.close()
                except BaseException:self.cleanup_uncertain=True
        if self.writer is not None and getattr(self.writer,'close_errors',0):self.cleanup_uncertain=True
