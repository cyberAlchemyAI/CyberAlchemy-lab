"""Pure synthetic tests; loads only an independently hash-selected source file."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys
import types
import unittest

M = None
H = 'a' * 64
N = 'b' * 64


def fixture():
    selection = dict(schema='lab-mapper-synthetic-identity-selection/v1',
                     nonce=N, selection_sha256=H, observer_pidns=[1, 10],
                     observer_userns=[1, 20], wrapper_pid=100, wrapper_start=7,
                     exe_sha256='c' * 64, exe_identity=[2, 30])
    p = dict(observer_pidns=[1, 10], observer_userns=[1, 20], pid=101,
             start=8, ppid=100, nspid=[101, 1], uid=[1000] * 4, gid=[1001] * 4,
             namespaces={'pid': [1, 11], 'pid_for_children': [1, 11],
                         'user': [1, 21], 'mount': [1, 31]},
             caps={k: '0000000000000001' for k in
                   ('inheritable', 'permitted', 'effective', 'bounding', 'ambient')},
             no_new_privs=1, uid_map=[[0, 1000, 1]], gid_map=[[0, 1001, 1]],
             map_outer_userns=[1, 20], setgroups='deny', exe_sha256='c' * 64,
             exe_identity=[2, 30], pidfd_live=True, original_sha256='d' * 64,
             original_size=1024)
    wrapper = copy.deepcopy(p)
    wrapper.update(pid=100, start=7, ppid=99, nspid=[100])
    claim = {k: copy.deepcopy(p[k]) for k in
             ('namespaces', 'caps', 'no_new_privs', 'uid_map', 'gid_map',
              'map_outer_userns', 'setgroups')}
    claim.update(nonce=N, selection_sha256=H, inner_pid=1, uid=[0]*4, gid=[0]*4)
    before = [p, wrapper]
    return selection, before, copy.deepcopy(before), claim, [101, 1000, 1001]


def transcript():
    args = fixture()
    decision = M.decide(*args)
    identity = M.sha(M.canonical(args[3]))
    namespaces = M.sha(M.canonical(args[3]['namespaces']))
    exchange = M.Exchange(N, H, identity_sha256=identity,
                          namespaces_sha256=namespaces,
                          join_sha256=decision['joined_sha256'])
    bodies = [{}, {'inner_pid': 1, 'parent_pid': 0, 'fd_census': [0, 1, 2, 3],
                  'namespaces_sha256': namespaces, 'identity_sha256': identity,
                  'controller_tuple': [0, 65534, 65534]},
              {'hello_sha256': None, 'join_sha256': decision['joined_sha256'],
               'claim': 'synthetic-identity-consistency-only'},
              {'observation_sha256': None, 'controller_tuple': [0, 65534, 65534]}]
    frames = []
    for i, (sender, kind) in enumerate(exchange.schedule):
        if i == 2: bodies[i]['hello_sha256'] = M.sha(frames[1][1])
        if i == 3: bodies[i]['observation_sha256'] = M.sha(frames[2][1])
        frame = dict(schema='lab-mapper-namespace-probe/v1', kind=kind,
                     ordinal=i, nonce=N, selection_sha256=H,
                     previous_sha256=M.sha(frames[-1][1]) if frames else None,
                     body=bodies[i])
        frames.append((sender, M.canonical(frame)))
    return exchange, frames


class IdentityTests(unittest.TestCase):
    def refuse(self, args):
        with self.assertRaises(M.Refusal): M.decide(*args)

    def test_joined_synthetic_positive_not_host_authority(self):
        out = M.decide(*fixture())
        self.assertFalse(out['host_qualified'])
        self.assertEqual(out['claim'], 'synthetic-identity-consistency-only')

    def test_live_wrong_process_pid_is_not_sender_proof(self):
        a = fixture(); a[-1][0] = 200
        self.refuse(a)

    def test_coherent_wrong_wrapper_cannot_repin_selection(self):
        a = fixture()
        for chain in a[1:3]:
            chain[0]['ppid'] = 200; chain[-1]['pid'] = 200; chain[-1]['nspid'] = [200]
        self.refuse(a)

    def test_start_reuse_and_dead_pidfd_refuse(self):
        for field, value in [('start', 9), ('pidfd_live', False)]:
            a=fixture(); a[2][0][field]=value; self.refuse(a)

    def test_executable_digest_and_inode_join(self):
        for field, value in [('exe_sha256', 'e'*64), ('exe_identity', [2, 99])]:
            a=fixture()
            for chain in a[1:3]: chain[0][field]=value
            self.refuse(a)

    def test_nonce_and_selection_substitution(self):
        for key in ('nonce', 'selection_sha256'):
            a=fixture();a[3][key]='f'*64;self.refuse(a)

    def test_capability_and_no_new_privs_disagreement(self):
        a=fixture();a[3]['caps']['effective']='0000000000000000';self.refuse(a)
        a=fixture();a[3]['no_new_privs']=True;self.refuse(a)

    def test_real_uid_not_effective_uid(self):
        a=fixture()
        for chain in a[1:3]: chain[0]['uid']=[1000, 1002, 1000, 1000]
        a[-1][1]=1002
        self.refuse(a)

    def test_mapping_and_coordinates_cannot_be_asserted(self):
        a=fixture();a[3]['uid_map']=[[0, 1002, 1]];self.refuse(a)
        a=fixture()
        for chain in a[1:3]: chain[0]['map_outer_userns']=[1, 99]
        a[3]['map_outer_userns']=[1, 99]
        self.refuse(a)

    def test_projection_maps_all_four_ids(self):
        a=fixture();a[3]['uid'][3]=2;self.refuse(a)

    def test_namespace_and_observer_drift(self):
        a=fixture();a[3]['namespaces']['mount']=[1, 99];self.refuse(a)
        a=fixture();a[2][0]['observer_pidns']=[1, 99];self.refuse(a)

    def test_cycles_and_missing_ancestry(self):
        a=fixture();a[1][0]['ppid']=9;a[2][0]['ppid']=9;self.refuse(a)
        a=fixture();a[1].append(copy.deepcopy(a[1][-1]));self.refuse(a)

    def test_ancestry_and_evidence_bounds(self):
        a=fixture();a[1][:]=[copy.deepcopy(a[1][0]) for _ in range(33)];self.refuse(a)
        a=fixture()
        for chain in a[1:3]:
            for item in chain:item['original_size']=2*1024*1024
        self.refuse(a)

    def test_changed_raw_observation_with_same_identity_allowed(self):
        a=fixture();a[2][0]['original_sha256']='e'*64
        self.assertFalse(M.decide(*a)['host_qualified'])

    def test_unknown_missing_boolean_pid_and_extra_fields(self):
        for key, value in [('pid', True), ('caps', {}), ('pidfd_live', 1)]:
            a=fixture();a[1][0][key]=value;self.refuse(a)
        a=fixture();a[3]['authority']=True;self.refuse(a)

    def test_map_overlap_overflow_unmapped_and_limit(self):
        for rows in ([[0,1000,2],[1,2000,1]], [[0,1000,2],[2,1001,1]],
                     [[0,(1<<32)-2,2]], [], [[i,i,1] for i in range(65)]):
            with self.assertRaises(M.Refusal):M.id_map(rows)
        with self.assertRaises(M.Refusal):M.project(5, [[0,1000,1]])


class ProtocolTests(unittest.TestCase):
    def test_complete_transcript_and_late_frame_fence(self):
        x,frames=transcript()
        for sender,raw in frames:x.accept(sender,raw)
        self.assertEqual(x.finish()['frames'],4)
        self.assertFalse(x.finish()['host_qualified'])
        with self.assertRaises(M.Refusal):x.accept(*frames[-1])
        with self.assertRaises(M.Refusal):x.finish()

    def test_partial_exchange_is_unknown(self):
        x,frames=transcript();x.accept(*frames[0])
        with self.assertRaises(M.Refusal):x.finish()
        with self.assertRaises(M.Refusal):x.accept(*frames[1])

    def test_replay_out_of_order_and_wrong_sender(self):
        for index,sender in [(1,'payload'),(0,'payload')]:
            x,frames=transcript()
            with self.assertRaises(M.Refusal):x.accept(sender,frames[index][1])
            with self.assertRaises(M.Refusal):x.accept(*frames[0])

    def test_each_security_binding_causal_mutation(self):
        mutations=[(0,'nonce','e'*64),(0,'selection_sha256','e'*64),
                   (1,'previous_sha256','e'*64),(1,'ordinal',True)]
        for index,key,value in mutations:
            x,frames=transcript()
            for frame in frames[:index]:x.accept(*frame)
            obj=json.loads(frames[index][1]);obj[key]=value
            with self.assertRaises(M.Refusal):x.accept(frames[index][0],M.canonical(obj))

    def test_hello_join_and_receipt_cannot_select_themselves(self):
        for index,key in [(1,'identity_sha256'),(1,'namespaces_sha256'),
                          (2,'join_sha256'),(2,'hello_sha256'),(3,'observation_sha256')]:
            x,frames=transcript()
            for frame in frames[:index]:x.accept(*frame)
            obj=json.loads(frames[index][1]);obj['body'][key]='e'*64
            with self.assertRaises(M.Refusal):x.accept(frames[index][0],M.canonical(obj))

    def test_controller_zero_measurement_not_host_tuple_admission(self):
        M.peer([0,65534,65534],measurement=True)
        with self.assertRaises(M.Refusal):M.peer([0,65534,65534])
        x,frames=transcript()
        for frame in frames[:3]:x.accept(*frame)
        obj=json.loads(frames[3][1]);obj['body']['controller_tuple'][1]=1000
        with self.assertRaises(M.Refusal):x.accept('payload',M.canonical(obj))

    def test_packet_duplicate_keys_noncanonical_encoding_and_size(self):
        for raw in (b'{"x":0,"x":1}',b'{"x": 1}',b'\xff',b'[]'*5000,
                    b'{"x":NaN}',b'['*5000+b']'*5000):
            with self.assertRaises(M.Refusal):M.parse(raw)

    def test_extra_field_body_and_fd_boolean(self):
        for mode in ('extra','boolfd'):
            x,frames=transcript();x.accept(*frames[0])
            obj=json.loads(frames[1][1])
            if mode=='extra':obj['body']['authority']=True
            else:obj['body']['fd_census']=[False,1,2,3]
            with self.assertRaises(M.Refusal):x.accept('payload',M.canonical(obj))

    def test_matching_explicit_ancillary_not_wire_distinguishable(self):
        record=[{'kind':'SCM_CREDENTIALS','tuple':[123,1000,1000]}]
        self.assertEqual(M.ancillary(record),(123,1000,1000))
        # Same synthetic record whether kernel-default or explicitly supplied.
        for method,anc in [('sendmsg',record),('send',record),('sendall',[])]:
            with self.assertRaises(M.Refusal):M.outbound_policy(method,anc)
        self.assertEqual(M.outbound_policy('send',[]),'ORDINARY_SEND_NO_ANCILLARY')

    def test_rights_duplicates_unknown_and_truncation_refuse(self):
        good={'kind':'SCM_CREDENTIALS','tuple':[123,1000,1000]}
        for records in ([],[good,good],[{'kind':'SCM_RIGHTS','tuple':[3,4,5]}],
                        [{'kind':'OTHER','tuple':[1,2,3]}]):
            with self.assertRaises(M.Refusal):M.ancillary(records)
        for kwargs in ({'truncated':True},{'control_truncated':True}):
            with self.assertRaises(M.Refusal):M.ancillary([good],**kwargs)

    def test_send_results_no_suffix_or_semantic_retry(self):
        self.assertEqual(M.send_result(10,10),'QUEUED')
        self.assertIn('SAME_UNSENT',M.send_result(10,'EAGAIN_BEFORE_QUEUE'))
        for value in (9,0,True,'EINTR_UNKNOWN','LOST_ACK'):
            with self.assertRaises(M.Refusal):M.send_result(10,value)


def main():
    global M
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',required=True)
    parser.add_argument('--source-sha256',required=True)
    args=parser.parse_args()
    source=Path(args.source).read_bytes()
    if hashlib.sha256(source).hexdigest()!=args.source_sha256:
        raise SystemExit('SELECTED_SOURCE_DRIFT')
    M=types.ModuleType('selected_mapper_namespace_model_0001')
    exec(compile(source,args.source,'exec'),M.__dict__)
    suite=unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    unchanged=Path(args.source).read_bytes()==source
    ok=result.wasSuccessful() and unchanged
    print(json.dumps({'schema_version':'lab-case-command-result/v1',
                      'result':'PASS' if ok else 'FAIL','checks':result.testsRun,
                      'effect_state':'none','cleanup':'clean',
                      'source_unchanged':unchanged,'host_qualified':False},sort_keys=True))
    return 0 if ok else 1


if __name__=='__main__':
    raise SystemExit(main())
