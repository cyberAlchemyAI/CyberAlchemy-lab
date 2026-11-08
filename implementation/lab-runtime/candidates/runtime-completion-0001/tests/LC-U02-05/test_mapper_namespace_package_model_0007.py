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


def prepare(c,a):
    return c.prepare_reply_synthetic(completion(a),output=b'{"synthetic_output":true}' if a.get('verb') in ('SEAL','COLD_READ') else None)


def send_observation(prepared):
    record=json.loads(prepared['record_raw'])
    return {'schema':'mapper-synthetic-send-observation/v1','prepared_reply_sha256':prepared['record_sha256'],
            'sent_packets':prepared['packets'],**{k:record[k] for k in ('ordinal','host_peer','child_peer','packet_sha256','packet_sizes','size_bytes','output_sha256')}}


def request(c,verb,payload,ack=True):
    raw=W.encode(W.envelope(c.selection['attempt_id'],c.selection_sha,c.protocol.ordinal,verb,payload))
    a=c.receive_synthetic(raw,peer=c.peer,current_selection_sha=c.selection_sha)
    if ack:
        prepared=prepare(c,a);c.acknowledge_reply_synthetic(send_observation(prepared),current_selection_sha=c.selection_sha)
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
        c=active();a=request(c,'BEGIN',c.selection['begin_pins'],False);prepared=prepare(c,a)
        observed=send_observation(prepared);observed['sent_packets']=()
        with self.assertRaises(Exception):c.acknowledge_reply_synthetic(observed,current_selection_sha=c.selection_sha)
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
        c=active();a=request(c,'BEGIN',c.selection['begin_pins'],False);proof=completion(a);prepared=c.prepare_reply_synthetic(proof);proof['kind']='changed'
        self.assertEqual(c.pending['completion']['kind'],'owned-names')
        with self.assertRaises(Exception):c.acknowledge_reply_synthetic(send_observation(prepared),current_selection_sha='f'*64)

    def test_terminal_false_observation_refuses(self):
        c=active();full(c);ob={k:True for k in ('exit_zero','streams_complete','streams_empty','group_empty','reaped','source_unchanged','attachment_unchanged')};ob['group_empty']=False
        with self.assertRaises(Exception):c.finish_synthetic(ob)
        self.assertEqual(c.phase,'UNKNOWN')

    def test_pure_source_has_no_effect_import_or_call(self):
        tree=ast.parse(Path(INPUTS['model']['path']).read_bytes())
        for n in ast.walk(tree):
            if isinstance(n,ast.Import):self.assertTrue(all(x.name in ('base64','hashlib','re') for x in n.names))
            if isinstance(n,ast.Call):self.assertNotIn(ast.unparse(n.func).split('.')[-1],('open','read_bytes','write_bytes','socket','fork','execve','run','Popen','PackageWriter','Mediator'))



class ReplyBindingRegressionTests(unittest.TestCase):
    def begin(self):
        c=active();a=request(c,'BEGIN',c.selection['begin_pins'],False);prepared=prepare(c,a)
        return c,prepared

    def test_retained_R01_no_reply_bytes_no_advancement(self):
        for observed in (None,True,{'sent_exactly':True}):
            c,_=self.begin()
            with self.assertRaises(Exception):c.acknowledge_reply_synthetic(observed,current_selection_sha=c.selection_sha)
            self.assertEqual(c.protocol.step,0);self.assertEqual(c.phase,'UNKNOWN')

    def test_prepared_ack_packet_binds_all_subjects_and_is_canonical(self):
        c,prepared=self.begin();record=json.loads(prepared['record_raw']);packet=W.decode(prepared['packets'][0])
        self.assertEqual(W.encode(packet),prepared['packets'][0]);self.assertEqual(packet['payload'],{'kind':'ACK'})
        for key in ('request_sha256','ordinal','selection_sha256','host_peer','child_peer','completion_sha256'):
            self.assertEqual(packet[key],record[key])
        self.assertEqual(record['completion_sha256'],M.digest(c.pending['completion_raw']))
        c.acknowledge_reply_synthetic(send_observation(prepared),current_selection_sha=c.selection_sha)
        self.assertEqual(c.protocol.step,1)

    def test_missing_altered_noncanonical_or_extra_packet_refuses(self):
        for mode in ('missing','altered','noncanonical','extra','wrong-type'):
            c,prepared=self.begin();observed=send_observation(prepared);packet=prepared['packets'][0]
            if mode=='missing':observed['sent_packets']=()
            elif mode=='altered':observed['sent_packets']=(packet.replace(b'ACK',b'BAD'),)
            elif mode=='noncanonical':observed['sent_packets']=(packet+b' ',)
            elif mode=='extra':observed['sent_packets']=(packet,packet)
            else:observed['sent_packets']=[packet]
            with self.assertRaises(Exception):c.acknowledge_reply_synthetic(observed,current_selection_sha=c.selection_sha)
            self.assertEqual(c.protocol.step,0)

    def test_metadata_peer_ordinal_digest_size_output_refuse(self):
        changes={'host_peer':[1,1,1,1],'child_peer':[0,1,1],'ordinal':True,'prepared_reply_sha256':'f'*64,
                 'packet_sha256':['f'*64],'packet_sizes':[1],'size_bytes':False,'output_sha256':'f'*64}
        for field,value in changes.items():
            c,prepared=self.begin();observed=send_observation(prepared);observed[field]=value
            with self.assertRaises(Exception):c.acknowledge_reply_synthetic(observed,current_selection_sha=c.selection_sha)
            self.assertEqual(c.protocol.step,0)

    def test_duplicate_ack_cannot_advance_twice(self):
        c,prepared=self.begin();observed=send_observation(prepared)
        c.acknowledge_reply_synthetic(observed,current_selection_sha=c.selection_sha)
        with self.assertRaises(Exception):c.acknowledge_reply_synthetic(observed,current_selection_sha=c.selection_sha)
        self.assertEqual(c.protocol.step,1);self.assertEqual(len(c.reply_records),1)

    def test_old_reply_cannot_ack_next_blob_ordinal(self):
        c,prepared=self.begin();old=send_observation(prepared)
        c.acknowledge_reply_synthetic(old,current_selection_sha=c.selection_sha)
        a=request(c,'BLOB_BEGIN',{'size_bytes':2,'sha256':M.digest(b'{}'),'purpose':'SEAL','target':'semantic'},False)
        prepare(c,a)
        with self.assertRaises(Exception):c.acknowledge_reply_synthetic(old,current_selection_sha=c.selection_sha)
        self.assertEqual(c.protocol.step,1)

    def seal(self,output):
        c=active();request(c,'BEGIN',c.selection['begin_pins']);blob=upload(c,'SEAL','semantic',b'{}')
        a=request(c,'SEAL',{'blob_id':blob},False)
        return c,c.prepare_reply_synthetic(completion(a),output=output)

    def test_multichunk_output_exact_digest_offsets_and_ack(self):
        output=b'x'*(W.CHUNK_MAX+7);c,prepared=self.seal(output)
        payloads=[W.decode(x)['payload'] for x in prepared['packets']]
        self.assertEqual([x['kind'] for x in payloads],['DATA_BEGIN','DATA_CHUNK','DATA_CHUNK','DATA_END'])
        self.assertEqual([x['offset'] for x in payloads[1:-1]],[0,W.CHUNK_MAX])
        self.assertEqual(b''.join(base64.b64decode(x['data']) for x in payloads[1:-1]),output)
        record=json.loads(prepared['record_raw']);self.assertEqual(record['output_sha256'],M.digest(output))
        self.assertEqual(record['output_size_bytes'],len(output))
        c.acknowledge_reply_synthetic(send_observation(prepared),current_selection_sha=c.selection_sha)
        self.assertEqual(c.protocol.step,2)

    def test_maximum_output_and_finite_frame_bounds(self):
        c,prepared=self.seal(b'x'*W.BLOB_MAX)
        self.assertTrue(all(0<len(x)<=W.FRAME_MAX for x in prepared['packets']))
        self.assertEqual(len(prepared['packets']),2+W.BLOB_MAX//W.CHUNK_MAX)
        self.assertGreater(len(prepared['record_raw']),8192)
        c.acknowledge_reply_synthetic(send_observation(prepared),current_selection_sha=c.selection_sha)
        self.assertEqual(c.protocol.step,2)

    def test_output_missing_empty_oversize_and_wrong_verb_refuse(self):
        for output in (None,b'',b'x'*(W.BLOB_MAX+1)):
            with self.assertRaises(Exception):self.seal(output)
        c=active();a=request(c,'BEGIN',c.selection['begin_pins'],False)
        with self.assertRaises(Exception):c.prepare_reply_synthetic(completion(a),output=b'not-allowed')

    def test_changed_output_chunk_refuses_even_with_recomputed_observed_digests(self):
        c,prepared=self.seal(b'x'*40000);observed=send_observation(prepared);packets=list(observed['sent_packets'])
        changed=W.decode(packets[1]);changed['payload']['data']=base64.b64encode(b'y'*W.CHUNK_MAX).decode();packets[1]=W.encode(changed)
        observed['sent_packets']=tuple(packets);observed['packet_sha256']=[M.digest(x) for x in packets]
        observed['packet_sizes']=list(map(len,packets));observed['size_bytes']=sum(map(len,packets));observed['output_sha256']='f'*64
        with self.assertRaises(Exception):c.acknowledge_reply_synthetic(observed,current_selection_sha=c.selection_sha)
        self.assertEqual(c.protocol.step,1)

    def test_reply_aggregate_budget_refuses_before_ready(self):
        c=active();a=request(c,'BEGIN',c.selection['begin_pins'],False);c.reply_bytes=W.TOTAL_MAX
        with self.assertRaises(Exception):prepare(c,a)
        self.assertEqual(c.protocol.step,0)

    def test_retained_R02_runner_client_alias_refuses_coherent_repin(self):
        s,_=manifest();s['roles']['namespace_client']=s['roles']['namespace_runner'];raw=N.encode(s)
        with self.assertRaisesRegex(M.Refusal,'^ROLE_ALIAS$'):M.selection(raw,M.digest(raw))

    def test_other_required_role_alias_refuses(self):
        for role in ('bridge','adapter','fixture_base'):
            s,_=manifest();s['roles'][role]=s['roles']['namespace_runner'];raw=N.encode(s)
            with self.assertRaisesRegex(M.Refusal,'^ROLE_ALIAS$'):M.selection(raw,M.digest(raw))


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
    M=load('mapper_namespace_package_model_0007',inputs['model'])
    HISTORY=json.loads(checked(inputs['namespace_record']))
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    print(json.dumps({'result':'PASS' if result.wasSuccessful() else 'FAIL','checks':result.testsRun,'namespace_executions':0,'native_executions':0,'protected_reads':0,'host_qualified':False,'cleanup':'clean'},sort_keys=True))
    return 0 if result.wasSuccessful() else 1
