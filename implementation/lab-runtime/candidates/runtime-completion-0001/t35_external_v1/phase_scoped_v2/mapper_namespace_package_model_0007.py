"""Pure composition projection, NEVER a launcher, writer or peer capability.

All observations/completions supplied here are synthetic. A successful model
cannot authorize a live Client, Mediator or PackageWriter. Frozen modules are
selected by the external harness; their effectful entrypoints are never called.
"""
import base64
import hashlib
import re

from . import mapper_namespace_probe_common_0004 as ns
from . import mapper_package_ipc_model_0004 as wire

FAMILY='/work/out/legacy-fixture-source'
PACKAGE=FAMILY+'/mapped/packages/0001'
ROLES=('namespace_runner','namespace_client','bridge','adapter','preimage','builder',
       'fixture_base','fixture_config','common','wire','cache','interpreter','bwrap',
       'mediator','writer','transport','source','source_input','reader')


class Refusal(ValueError):pass


def need(ok,code):
    if not ok:raise Refusal(code)


def digest(raw):return hashlib.sha256(raw).hexdigest()


def absolute(path):
    need(type(path) is str and path.startswith('/') and '\\' not in path and '\0' not in path
         and len(path)<=4096 and all(x not in ('','.','..') for x in path.split('/')[1:]),'PATH')
    return path


def under(path,root):return path==root or path.startswith(root+'/')


def selection(raw,expected_sha):
    ns.hex64(expected_sha);need(type(raw) is bytes and digest(raw)==expected_sha,'SELECTION_DIGEST')
    value=ns.decode(raw,1048576)
    ns.closed(value,'schema posture attempt_id nonce scratch_root roles files begin_pins')
    need(value['schema']=='mapper-namespace-package-selection/v1' and value['posture']=='synthetic-projection-only','POSTURE')
    need(type(value['attempt_id']) is str and re.fullmatch('[a-z0-9-]{1,48}',value['attempt_id']),'ATTEMPT')
    ns.hex64(value['nonce'])
    root='/tmp/lc-u02-05-mapper-writer-'+value['attempt_id']
    need(value['scratch_root']==root,'SCRATCH')
    ns.closed(value['roles'],' '.join(ROLES));ns.closed(value['begin_pins'],'mapper source reader adapter')
    for h in value['begin_pins'].values():ns.hex64(h)
    files=value['files'];need(type(files) is list and 19<=len(files)<=2048,'FILE_BOUND')
    ids={};hosts=set();children=set()
    for row in files:
        ns.closed(row,'id host_path child_path sha256 size_bytes view')
        need(type(row['id']) is str and re.fullmatch('[a-z0-9_-]{1,64}',row['id']),'FILE_ID')
        need(row['id'] not in ids,'DUPLICATE_ID');ns.hex64(row['sha256']);ns.number(row['size_bytes'],0,64*1024*1024)
        h=absolute(row['host_path']);c=absolute(row['child_path'])
        need(h not in hosts and c not in children,'LOCATOR_ALIAS');hosts.add(h);children.add(c)
        view=row['view'];need(view in ('control','family','runtime','host-only'),'VIEW')
        if view=='control':need(under(h,root+'/control') and c=='/work/control'+h[len(root+'/control'):],'CONTROL_MAP')
        elif view=='family':need(under(h,root+'/output/legacy-fixture-source') and c==FAMILY+h[len(root+'/output/legacy-fixture-source'):],'FAMILY_MAP')
        elif view=='runtime':need(h==c and any(under(h,x) for x in ('/usr','/lib','/lib64')),'RUNTIME_MAP')
        else:need(under(h,root+'/host') and c==h,'HOST_ONLY')
        # Output is solely the external held writer's destination, never a
        # selected mutable source or control file in either view.
        need(not under(c,PACKAGE) and c!='/work/control/selection.json','OUTPUT_INPUT_ALIAS');ids[row['id']]=row
    for role,key in value['roles'].items():need(type(key) is str and key in ids,'ROLE')
    need(len(set(value['roles'].values()))==len(ROLES),'ROLE_ALIAS')
    def row(role):return ids[value['roles'][role]]
    for role in ('namespace_runner','namespace_client','bridge','adapter','preimage','builder','fixture_base','fixture_config','common','wire','cache'):
        need(row(role)['view']=='control','ROLE_VIEW')
    for role in ('mediator','writer','transport'):need(row(role)['view']=='host-only','ROLE_VIEW')
    for role in ('source','source_input','reader'):need(row(role)['view']=='family','ROLE_VIEW')
    need(row('interpreter')['host_path']=='/usr/bin/python3.14' and row('interpreter')['view']=='runtime','INTERPRETER')
    need(row('bwrap')['host_path']=='/usr/bin/bwrap' and row('bwrap')['view']=='runtime','BWRAP')
    need(row('source')['child_path']==FAMILY+'/mapped/source-manifest.json','SOURCE_PATH')
    for role,pin in (('source','mapper'),('source_input','source'),('reader','reader'),('adapter','adapter')):
        need(row(role)['sha256']==value['begin_pins'][pin],'ROLE_PIN')
    return value


def selected_copy(row,raw,locator,view):
    """Pure byte/locator equality; no read, inode custody or runtime authority."""
    need(view in ('host','child') and not(view=='child' and row['view']=='host-only'),'COPY_VIEW')
    need(locator==row[view+'_path'] and type(raw) is bytes and len(raw)==row['size_bytes']
         and digest(raw)==row['sha256'],'COPY_BINDING')
    return {'verified_bytes_only':True,'authority':False}


def launch_projection(raw,expected_sha):
    s=selection(raw,expected_sha);files={r['id']:r for r in s['files']};root=s['scratch_root']
    def row(role):return files[s['roles'][role]]
    argv=[row('bwrap')['host_path'],'--die-with-parent','--unshare-all','--clearenv','--as-pid-1','--sync-fd','3',
          '--ro-bind','/usr','/usr','--ro-bind','/lib','/lib','--ro-bind','/lib64','/lib64',
          '--ro-bind',root+'/control','/work/control','--ro-bind',root+'/output/legacy-fixture-source',FAMILY,
          '--proc','/proc','--chdir','/','--',row('interpreter')['child_path'],'-I','-B','-S','-X',
          'pycache_prefix='+row('cache')['child_path'],row('namespace_runner')['child_path'],
          '/work/control/selection.json',expected_sha]
    return {'schema':'mapper-namespace-package-launch-projection/v1','argv':argv,'selection_sha256':expected_sha,
            'host_package':root+'/output/legacy-fixture-source/mapped/packages/0001','child_package':PACKAGE,
            'writer_mapped':root+'/output/legacy-fixture-source/mapped','inherited_fd':3,
            'effect_eligible':False,'new_namespace_executions':0,'required_runtime_adapter':'unimplemented-fixed-namespace-package-runner/v1'}


class Composition:
    """Two protocol phases over one proposed fd3; synthetic lifecycle only."""
    def __init__(self,raw,sha):
        self.selection=selection(raw,sha);self.selection_sha=sha;self.raw=bytes(raw)
        self.phase='NEW';self.peer=None;self.child_peer=None;self.protocol=None
        self.pending=None;self.retained=[];self.activation=None;self.first_failure=None
        self.reply_bytes=0;self.reply_packets=0;self.reply_records=[]

    def fail(self,code):
        self.phase='UNKNOWN';self.first_failure=self.first_failure or code
        if self.protocol is not None:self.protocol.disconnect()

    def observe_synthetic(self,frames):
        try:
            need(self.phase=='NEW' and type(frames) is list and len(frames)==4,'OBSERVATION_PHASE')
            previous=None;bodies=[]
            for index,raw in enumerate(frames):
                bodies.append(ns.validate_frame(raw,index,self.selection['nonce'],self.selection_sha,previous));previous=ns.sha(raw)
            challenge,hello,observation,receipt=bodies
            ns.closed(challenge,'controller_pid controller_start controller_namespaces')
            ns.closed(hello,'claim controller_tuple fd_census originals')
            ns.closed(observation,'hello_sha256 join_sha256 join_summary claim')
            ns.closed(receipt,'observation_sha256 controller_tuple claim_sha256 fd_census originals join_summary_sha256')
            need(hello['fd_census']==receipt['fd_census']==[[0,8192],[1,4096],[2,4096],[3,49152]],'FD_CENSUS')
            ns.verify_child_originals(hello['originals'],'self-before',hello['claim'])
            ns.verify_child_originals(receipt['originals'],'self-after',hello['claim'])
            summary=observation['join_summary'];hello_sha=digest(frames[1])
            joined=ns.verify_host_join_summary(summary,hello['claim'],challenge,hello['controller_tuple'],hello_sha,{'uid':65534,'gid':65534})
            need(observation['hello_sha256']==hello_sha and observation['join_sha256']==joined
                 and observation['claim']=='fixed-source-consistency-only','OBSERVATION_JOIN')
            need(receipt['observation_sha256']==digest(frames[2]) and receipt['controller_tuple']==hello['controller_tuple']
                 and receipt['claim_sha256']==digest(ns.encode(hello['claim'])) and receipt['join_summary_sha256']==joined,'RECEIPT_JOIN')
            selected={r['id']:r for r in self.selection['files']}
            need(summary['exe_sha256']==selected[self.selection['roles']['interpreter']]['sha256'],'SELECTED_EXE')
            p=summary['before'][0];self.peer=(p['pid'],p['start'],p['uid'][0],p['gid'][0]);self.child_peer=tuple(hello['controller_tuple'])
            need(self.child_peer[0]==0,'CHILD_PEER_PROFILE')
            self.activation={'schema':'mapper-namespace-package-activation/v1','nonce':self.selection['nonce'],
                'selection_sha256':self.selection_sha,'receipt_sha256':digest(frames[3]),'host_join_sha256':joined,
                'host_peer':list(self.peer),'child_peer':list(self.child_peer),'posture':'synthetic-projection-only'}
            self.phase='WAIT_ACTIVATION_ACK'
            return ns.encode(self.activation)
        except BaseException:
            self.fail('OBSERVATION_REFUSED');raise

    def acknowledge_activation_synthetic(self,ack,*,peer):
        try:
            need(self.phase=='WAIT_ACTIVATION_ACK','ACTIVATION_PHASE');ns.closed(ack,'schema activation_sha256 selection_sha256')
            need(ack=={'schema':'mapper-namespace-package-activation-ack/v1','activation_sha256':digest(ns.encode(self.activation)),
                       'selection_sha256':self.selection_sha} and peer==self.peer,'ACTIVATION_JOIN')
            self.protocol=wire.ProtocolModel(attempt_id=self.selection['attempt_id'],selection_sha256=self.selection_sha,
                                            begin_pins=self.selection['begin_pins'],peer=self.peer)
            self.phase='PACKAGE'
        except BaseException:self.fail('ACTIVATION_REFUSED');raise

    def receive_synthetic(self,raw,*,peer,current_selection_sha,**transport_observations):
        try:
            need(self.phase=='PACKAGE' and self.pending is None,'PACKAGE_PHASE')
            need(current_selection_sha==self.selection_sha,'SOURCE_SELECTION_DRIFT')
            action=self.protocol.receive(raw,peer=peer,**transport_observations)
            # Framing-only ACKs are also pending until their modeled send.
            self.pending={'action':action,'completion':None}
            return action
        except BaseException:self.fail('PACKAGE_REFUSED');raise

    def prepare_reply_synthetic(self,completion,*,output=None):
        try:
            need(self.phase=='PACKAGE' and self.pending is not None and self.pending['completion'] is None,'REPLY_PHASE')
            a=self.pending['action'];verb=a.get('verb')
            ns.closed(completion,'schema request_sha256 kind leaf sha256 size_bytes file_fsync parent_fsync readback attached')
            need(completion['schema']=='mapper-synthetic-completion/v1' and completion['request_sha256']==a['request_sha256'],'COMPLETION_SUBJECT')
            kinds={None:'memory-framing','BEGIN':'owned-names','SEAL':'deterministic-seal','COLD_READ':'deterministic-cold','FINISH':'complete-55-leaf-scan','EMIT':'held-leaf'}
            need(completion['kind']==kinds[verb],'COMPLETION_KIND')
            if verb=='EMIT':
                need(completion['leaf']==a['target'] and completion['sha256']==a['blob_sha256'] and completion['size_bytes']==a['size_bytes'],'LEAF_RECEIPT')
                need(all(completion[k] is True for k in ('file_fsync','parent_fsync','readback','attached')),'DURABILITY_OBSERVATION')
            else:
                need(completion['leaf'] is None and completion['sha256'] is None and completion['size_bytes']==0,'NONLEAF_RECEIPT')
                need(all(completion[k] is (verb in ('BEGIN','FINISH')) for k in ('file_fsync','parent_fsync','readback','attached')),'COMPLETION_FLAGS')
            # Exact immutable completion bytes and wire packets are prepared
            # BEFORE the modeled send. No caller boolean can advance the phase.
            completion_raw=ns.encode(completion)
            output_verb=verb in ('SEAL','COLD_READ')
            need((type(output) is bytes and 0<len(output)<=wire.BLOB_MAX) if output_verb else output is None,'REPLY_OUTPUT')
            output_sha=digest(output) if output_verb else None
            payloads=[{'kind':'ACK'}]
            if output_verb:
                payloads=[{'kind':'DATA_BEGIN','size_bytes':len(output),'sha256':output_sha}]
                payloads += [{'kind':'DATA_CHUNK','offset':offset,'data':base64.b64encode(output[offset:offset+wire.CHUNK_MAX]).decode('ascii')}
                             for offset in range(0,len(output),wire.CHUNK_MAX)]
                payloads.append({'kind':'DATA_END','sha256':output_sha})
            packets=tuple(wire.encode({'schema_version':'lab-mapper-namespace-package-response/v1',
                'attempt_id':self.selection['attempt_id'],'selection_sha256':self.selection_sha,
                'request_sha256':a['request_sha256'],'ordinal':a['ordinal'],'status':'synthetic-projection-only',
                'host_peer':list(self.peer),'child_peer':list(self.child_peer),'completion_sha256':digest(completion_raw),
                'payload':payload}) for payload in payloads)
            sizes=tuple(map(len,packets));packet_hashes=tuple(map(digest,packets))
            need(self.reply_bytes+sum(sizes)+self.protocol.total<=wire.TOTAL_MAX
                 and self.reply_packets+len(packets)+self.protocol.ordinal<=wire.PACKETS_MAX,'REPLY_AGGREGATE')
            record={'schema':'mapper-prepared-reply/v1','attempt_id':self.selection['attempt_id'],
                'selection_sha256':self.selection_sha,'request_sha256':a['request_sha256'],'ordinal':a['ordinal'],
                'host_peer':list(self.peer),'child_peer':list(self.child_peer),'completion_sha256':digest(completion_raw),
                'packet_sha256':list(packet_hashes),'packet_sizes':list(sizes),'size_bytes':sum(sizes),
                'output_sha256':output_sha,'output_size_bytes':len(output) if output_verb else 0}
            record_raw=ns.encode(record)
            self.pending.update(completion=ns.decode(completion_raw),completion_raw=completion_raw,
                                packets=packets,record_raw=record_raw,record_sha256=digest(record_raw))
            return {'synthetic_reply_ready':True,'durable_ack':False,'authority':False,
                    'packets':packets,'record_raw':record_raw,'record_sha256':digest(record_raw)}
        except BaseException:self.fail('COMPLETION_REFUSED');raise

    def acknowledge_reply_synthetic(self,observed=None,*,current_selection_sha):
        """Compare exact modeled send bytes; never observe or claim real I/O.

        The future fixed transport must acquire this record from its bounded
        send loop, with fresh peer/currentness checks. This public pure model
        cannot establish the provenance of caller-supplied observations.
        """
        try:
            need(self.phase=='PACKAGE' and self.pending is not None and self.pending['completion'] is not None,'ACK_PHASE')
            ns.closed(observed,'schema prepared_reply_sha256 ordinal host_peer child_peer sent_packets packet_sha256 packet_sizes size_bytes output_sha256')
            need(observed['schema']=='mapper-synthetic-send-observation/v1' and current_selection_sha==self.selection_sha,'ACK_SUBJECT')
            prepared=self.pending;record=ns.decode(prepared['record_raw'],65536)
            need(type(observed['sent_packets']) is tuple and all(type(x) is bytes for x in observed['sent_packets'])
                 and observed['sent_packets']==prepared['packets'],'ACK_BYTES')
            metadata={k:observed[k] for k in ('ordinal','host_peer','child_peer','packet_sha256','packet_sizes','size_bytes','output_sha256')}
            expected={k:record[k] for k in metadata}
            need(ns.encode(metadata)==ns.encode(expected) and observed['prepared_reply_sha256']==prepared['record_sha256'],'ACK_BINDING')
            # Exact canonical packet equality above includes request/selection,
            # both peer views and completion digest; the output hash is fixed
            # before packet construction and covers every ordered data chunk.
            a=prepared['action'];self.retained.append(prepared['completion'])
            self.reply_records.append(prepared['record_raw'])
            self.reply_bytes+=record['size_bytes'];self.reply_packets+=len(prepared['packets'])
            if a.get('verb') is not None:self.protocol.complete_synthetic(a['action_id'],success=True)
            self.pending=None
            if self.protocol.step==61:self.phase='WAIT_CHILD_EXIT'
        except BaseException:self.fail('ACK_REFUSED');raise

    def finish_synthetic(self,observation):
        try:
            ns.closed(observation,'exit_zero streams_complete streams_empty group_empty reaped source_unchanged attachment_unchanged')
            need(self.phase=='WAIT_CHILD_EXIT' and all(x is True for x in observation.values()),'TERMINAL_UNKNOWN')
            need(len([r for r in self.retained if r['kind']=='held-leaf'])==55,'LEAF_COUNT')
            self.phase='SYNTHETIC_COMPLETE'
            return {'synthetic_complete':True,'actions':61,'leaves':55,'effect_eligible':False,'host_qualified':False,
                    'same_uid_excluded':False,'escaped_descendants_excluded':False,'native_executions':0,'protected_reads':0}
        except BaseException:self.fail('TERMINAL_REFUSED');raise
