"""Pure composition regressions. No socket, process, filesystem-effect fixture."""
import ast
import base64
import copy
import hashlib
import json
from pathlib import Path
import sys
import types
import unittest

M=None
N=None
W=None
HISTORY=None
INPUTS=None


def manifest():
    attempt='pure-composition-0006';root='/tmp/lc-u02-05-mapper-writer-'+attempt
    rows=[];roles={};data={}
    for role in M.ROLES:
        raw=('synthetic-selected-'+role).encode();host=root+'/control/'+role+'.py';child='/work/control/'+role+'.py';view='control'
        if role in ('mediator','writer','transport'):host=root+'/host/'+role+'.py';child=host;view='host-only'
        elif role in ('source','source_input','reader'):
            tail={'source':'mapped/source-manifest.json','source_input':'source/source-manifest.json','reader':'reader/package.json'}[role]
            host=root+'/output/legacy-fixture-source/'+tail;child=M.FAMILY+'/'+tail;view='family'
        elif role in ('interpreter','bwrap'):
            host=child='/usr/bin/'+('python3.14' if role=='interpreter' else 'bwrap');view='runtime'
        row={'id':role,'host_path':host,'child_path':child,'sha256':M.digest(raw),'size_bytes':len(raw),'view':view}
        if role=='interpreter':row['sha256']=HISTORY['state']['host_join_summary']['exe_sha256']
        roles[role]=role;rows.append(row);data[role]=raw
    pins={k:next(r['sha256'] for r in rows if r['id']==v) for k,v in {'mapper':'source','source':'source_input','reader':'reader','adapter':'adapter'}.items()}
    return {'schema':'mapper-namespace-package-selection/v1','posture':'synthetic-projection-only','attempt_id':attempt,
            'nonce':'1'*64,'scratch_root':root,'roles':roles,'files':rows,'begin_pins':pins},data


def frames(s,sha):
    # Rebase retained valid identity bytes into a declared synthetic nonce/cut.
    # This is deliberately NOT evidence of a live current process.
    bodies=[json.loads(bytes.fromhex(x['raw_hex']))['body'] for x in HISTORY['wire']]
    out=[];previous=None
    for index,b in enumerate(copy.deepcopy(bodies)):
        if index==2:
            b['hello_sha256']=M.digest(out[1]);b['join_summary']['hello_sha256']=M.digest(out[1]);b['join_sha256']=M.digest(N.encode(b['join_summary']))
        if index==3:
            ob=json.loads(out[2])['body'];b['observation_sha256']=M.digest(out[2]);b['join_summary_sha256']=ob['join_sha256']
        raw=N.frame(index,s['nonce'],sha,previous,b);out.append(raw);previous=M.digest(raw)
    return out


def active():
    s,_=manifest();raw=N.encode(s);sha=M.digest(raw);c=M.Composition(raw,sha)
    activation=c.observe_synthetic(frames(s,sha))
    c.acknowledge_activation_synthetic({'schema':'mapper-namespace-package-activation-ack/v1','activation_sha256':M.digest(activation),'selection_sha256':sha},peer=c.peer)
    return c


def completion(a):
    verb=a.get('verb');kinds={None:'memory-framing','BEGIN':'owned-names','SEAL':'deterministic-seal','COLD_READ':'deterministic-cold','FINISH':'complete-55-leaf-scan','EMIT':'held-leaf'}
    return {'schema':'mapper-synthetic-completion/v1','request_sha256':a['request_sha256'],'kind':kinds[verb],
            'leaf':a['target'] if verb=='EMIT' else None,'sha256':a['blob_sha256'] if verb=='EMIT' else None,
            'size_bytes':a['size_bytes'] if verb=='EMIT' else 0,
            **{k:verb in ('BEGIN','EMIT','FINISH') for k in ('file_fsync','parent_fsync','readback','attached')}}


def request(c,verb,payload,ack=True):
    raw=W.encode(W.envelope(c.selection['attempt_id'],c.selection_sha,c.protocol.ordinal,verb,payload))
    a=c.receive_synthetic(raw,peer=c.peer,current_selection_sha=c.selection_sha)
    if ack:
        c.prepare_reply_synthetic(completion(a));c.acknowledge_reply_synthetic(sent_exactly=True,current_selection_sha=c.selection_sha)
    return a


def upload(c,verb,target,raw):
    blob=c.protocol.ordinal
    request(c,'BLOB_BEGIN',{'size_bytes':len(raw),'sha256':M.digest(raw),'purpose':verb,'target':target})
    request(c,'BLOB_CHUNK',{'blob_id':blob,'offset':0,'data':base64.b64encode(raw).decode()})
    request(c,'BLOB_END',{'blob_id':blob})
    return blob


def full(c):
    for verb,target in W.schedule():
        if verb=='BEGIN':payload=c.selection['begin_pins']
        elif verb in ('SEAL','EMIT'):
            b=upload(c,verb,target,b'{"synthetic":true}');payload={'blob_id':b}
            if verb=='EMIT':payload['leaf']=target
        elif verb=='COLD_READ':payload={'index':target}
        else:payload={'manifest_sha256':c.protocol.manifest_sha256}
        request(c,verb,payload)


class ModelTests(unittest.TestCase):
    def test_exact_dual_locator_selection_and_ro_launch_projection(self):
        s,_=manifest();raw=N.encode(s);result=M.launch_projection(raw,M.digest(raw))
        self.assertFalse(result['effect_eligible']);self.assertEqual(result['inherited_fd'],3)
        self.assertEqual(result['child_package'],M.PACKAGE)
        self.assertEqual(result['writer_mapped'],s['scratch_root']+'/output/legacy-fixture-source/mapped')
        self.assertNotIn('--bind',result['argv']);self.assertNotIn('--preserve-fds',result['argv'])
        self.assertIn(s['scratch_root']+'/output/legacy-fixture-source',result['argv'])

    def test_selection_wrong_hash_and_selfhash_refuse(self):
        s,_=manifest();raw=N.encode(s)
        with self.assertRaises(Exception):M.selection(raw,'f'*64)
        s['selection_sha256']=M.digest(raw);raw=N.encode(s)
        with self.assertRaises(Exception):M.selection(raw,M.digest(raw))

    def test_host_child_path_substitution_and_alias_refuse(self):
        s,_=manifest()
        for mutate in (lambda x:x['files'][0].update(child_path='/work/control/../escape'),
                       lambda x:x['files'][0].update(host_path='/tmp/unselected/a'),
                       lambda x:x['files'][0].update(child_path=M.PACKAGE+'/extra.py'),
                       lambda x:x['files'][0].update(child_path='/work/control/selection.json'),
                       lambda x:x['files'].append(copy.deepcopy(x['files'][0]))):
            x=copy.deepcopy(s);mutate(x);raw=N.encode(x)
            with self.assertRaises(Exception):M.selection(raw,M.digest(raw))

    def test_source_and_reader_and_adapter_pins_refuse_substitution(self):
        for pin in ('mapper','source','reader','adapter'):
            s,_=manifest();s['begin_pins'][pin]='f'*64;raw=N.encode(s)
            with self.assertRaises(Exception):M.selection(raw,M.digest(raw))

    def test_copy_requires_exact_bytes_locator_and_view(self):
        s,data=manifest();row=s['files'][0]
        self.assertFalse(M.selected_copy(row,data[row['id']],row['child_path'],'child')['authority'])
        for raw,path in ((b'changed',row['child_path']),(data[row['id']],row['host_path'])):
            with self.assertRaises(Exception):M.selected_copy(row,raw,path,'child')
        host=next(r for r in s['files'] if r['view']=='host-only')
        with self.assertRaises(Exception):M.selected_copy(host,data[host['id']],host['child_path'],'child')

    def test_historical_consumed_frames_cannot_activate_new_selection(self):
        s,_=manifest();raw=N.encode(s);c=M.Composition(raw,M.digest(raw))
        with self.assertRaises(Exception):c.observe_synthetic([bytes.fromhex(x['raw_hex']) for x in HISTORY['wire']])
        self.assertEqual(c.phase,'UNKNOWN')

    def test_activation_is_explicit_before_begin_and_keeps_pid0_separate(self):
        s,_=manifest();raw=N.encode(s);c=M.Composition(raw,M.digest(raw));c.observe_synthetic(frames(s,c.selection_sha))
        self.assertEqual(c.phase,'WAIT_ACTIVATION_ACK');self.assertEqual(c.child_peer[0],0);self.assertGreater(c.peer[0],0)
        with self.assertRaises(Exception):c.receive_synthetic(b'{}',peer=c.peer,current_selection_sha=c.selection_sha)

    def test_activation_ack_wrong_peer_and_digest_refuse(self):
        for bad in ('peer','digest'):
            s,_=manifest();raw=N.encode(s);c=M.Composition(raw,M.digest(raw));act=c.observe_synthetic(frames(s,c.selection_sha))
            ack={'schema':'mapper-namespace-package-activation-ack/v1','activation_sha256':M.digest(act),'selection_sha256':c.selection_sha}
            if bad=='digest':ack['activation_sha256']='f'*64
            with self.assertRaises(Exception):c.acknowledge_activation_synthetic(ack,peer=(1,1,1,1) if bad=='peer' else c.peer)

    def test_raw_child_original_and_host_summary_mutation_refuse(self):
        for field in ('originals','join_summary'):
            s,_=manifest();raw=N.encode(s);c=M.Composition(raw,M.digest(raw));f=frames(s,c.selection_sha)
            i=1 if field=='originals' else 2;v=json.loads(f[i]);v['body'][field]={};f[i]=N.encode(v)
            with self.assertRaises(Exception):c.observe_synthetic(f)

    def test_all_61_actions_and_55_leaf_gate(self):
        c=active();full(c);self.assertEqual(c.phase,'WAIT_CHILD_EXIT')
        self.assertEqual([(x['verb'],x['target']) for x in c.protocol.trace],W.schedule())
        result=c.finish_synthetic({k:True for k in ('exit_zero','streams_complete','streams_empty','group_empty','reaped','source_unchanged','attachment_unchanged')})
        self.assertEqual(result['leaves'],55);self.assertFalse(result['effect_eligible']);self.assertFalse(result['host_qualified'])

    def test_package_wrong_credential_and_source_cut_refuse(self):
        for bad in ('peer','cut'):
            c=active();raw=W.encode(W.envelope(c.selection['attempt_id'],c.selection_sha,0,'BEGIN',c.selection['begin_pins']))
            with self.assertRaises(Exception):c.receive_synthetic(raw,peer=(1,1,1,1) if bad=='peer' else c.peer,current_selection_sha='f'*64 if bad=='cut' else c.selection_sha)

    def test_pending_reply_blocks_next_request(self):
        c=active();request(c,'BEGIN',c.selection['begin_pins'],False)
        with self.assertRaises(Exception):request(c,'BEGIN',c.selection['begin_pins'])

    def test_lost_ack_keeps_prepared_original_and_poisoned_state(self):
        c=active();a=request(c,'BEGIN',c.selection['begin_pins'],False);c.prepare_reply_synthetic(completion(a))
        with self.assertRaises(Exception):c.acknowledge_reply_synthetic(sent_exactly=False,current_selection_sha=c.selection_sha)
        self.assertEqual(c.phase,'UNKNOWN');self.assertIsNotNone(c.pending['completion']);self.assertEqual(c.protocol.step,0)

    def test_blob_ack_is_memory_only(self):
        c=active();request(c,'BEGIN',c.selection['begin_pins']);request(c,'BLOB_BEGIN',{'size_bytes':2,'sha256':M.digest(b'{}'),'purpose':'SEAL','target':'semantic'})
        self.assertEqual(c.retained[-1]['kind'],'memory-framing');self.assertFalse(c.retained[-1]['file_fsync'])

    def test_leaf_receipt_wrong_hash_or_missing_fsync_refuses(self):
        for key,value in (('sha256','f'*64),('parent_fsync',False),('attached',False)):
            c=active();request(c,'BEGIN',c.selection['begin_pins'])
            for target in ('semantic','governance'):request(c,'SEAL',{'blob_id':upload(c,'SEAL',target,b'{}')})
            target='semantic/00000001.json';blob=upload(c,'EMIT',target,b'{}');a=request(c,'EMIT',{'blob_id':blob,'leaf':target},False)
            proof=completion(a);proof[key]=value
            with self.assertRaises(Exception):c.prepare_reply_synthetic(proof)
            self.assertEqual(c.protocol.step,3)

    def test_completion_copy_and_source_drift_before_ack(self):
        c=active();a=request(c,'BEGIN',c.selection['begin_pins'],False);proof=completion(a);c.prepare_reply_synthetic(proof);proof['kind']='changed'
        self.assertEqual(c.pending['completion']['kind'],'owned-names')
        with self.assertRaises(Exception):c.acknowledge_reply_synthetic(sent_exactly=True,current_selection_sha='f'*64)

    def test_terminal_false_observation_refuses(self):
        c=active();full(c);ob={k:True for k in ('exit_zero','streams_complete','streams_empty','group_empty','reaped','source_unchanged','attachment_unchanged')};ob['group_empty']=False
        with self.assertRaises(Exception):c.finish_synthetic(ob)
        self.assertEqual(c.phase,'UNKNOWN')

    def test_pure_source_has_no_effect_import_or_call(self):
        tree=ast.parse(Path(INPUTS['model']['path']).read_bytes())
        for n in ast.walk(tree):
            if isinstance(n,ast.Import):self.assertTrue(all(x.name in ('hashlib','re') for x in n.names))
            if isinstance(n,ast.Call):self.assertNotIn(ast.unparse(n.func).split('.')[-1],('open','read_bytes','write_bytes','socket','fork','execve','run','Popen','PackageWriter','Mediator'))


def main(inputs):
    global M,N,W,HISTORY,INPUTS
    INPUTS=inputs
    def checked(row):
        raw=Path(row['path']).read_bytes()
        if len(raw)!=row['size_bytes'] or hashlib.sha256(raw).hexdigest()!=row['sha256']:raise RuntimeError('INPUT_DRIFT')
        return raw
    pkg=types.ModuleType('selected_mapper_pure');pkg.__path__=[];sys.modules[pkg.__name__]=pkg
    def load(name,row):
        mod=types.ModuleType(pkg.__name__+'.'+name);mod.__package__=pkg.__name__;sys.modules[mod.__name__]=mod
        exec(compile(checked(row),row['path'],'exec'),mod.__dict__);setattr(pkg,name,mod);return mod
    N=load('mapper_namespace_probe_common_0004',inputs['common'])
    W=load('mapper_package_ipc_model_0004',inputs['wire'])
    M=load('mapper_namespace_package_model_0006',inputs['model'])
    HISTORY=json.loads(checked(inputs['namespace_record']))
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    print(json.dumps({'result':'PASS' if result.wasSuccessful() else 'FAIL','checks':result.testsRun,'namespace_executions':0,'native_executions':0,'protected_reads':0,'host_qualified':False,'cleanup':'clean'},sort_keys=True))
    return 0 if result.wasSuccessful() else 1
