"""Actual carrier closure plus real source/transport/permission negative checks."""
from .build import *
import argparse,unittest,stat

class DeliveryChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        verify_source(PIN);cls.package=load(HERE/'packages/0001/manifest.json')
        require(sha((HERE/'packages/0001/manifest.json').read_bytes())==PACKAGE,'independent delivery package differs')
        for row in cls.package['files']:original(row)
        cls.index=load(HERE/'packages/0001/artifact-index.json');cls.delivery=load(HERE/'packages/0001/delivery.json')
        cls.provenance=load(HERE/'packages/0001/delivery-provenance.json')
        cls.schemas=API.Schemas(API_PROFILE_PIN)
        cls.manager=reader.open_signed(SOURCE_PIN,SOURCE_PACKAGE);cls.source=cls.manager.__enter__()
        cls.tmp=tempfile.TemporaryDirectory(prefix='cal-R03-context-checks-');cls.root=Path(cls.tmp.name);cls.root.chmod(0o700)
        cls.policy=cls.root/'permission.json';cls.key,cls.policy_pin=provision(cls.policy,cls.source)
        cls.channel=HostChannel(cls.policy,cls.policy_pin,PIN,cls.source,cls.schemas)
        cls.proof=wire({'challenge':cls.channel.challenge,'signature':base64.b64encode(cls.key.sign(wire(cls.channel.challenge))).decode()})
        cls.channel.authenticate(cls.proof)
    @classmethod
    def tearDownClass(cls):cls.channel.close();cls.key=None;cls.tmp.cleanup();cls.manager.__exit__(None,None,None)
    def bodies(self,kind):return [load(ROOT/row['original_binding']['path']) for row in self.index if row['artifact']['carrier_ref']=='cal.artifact-type.'+kind+'/'+CARRIERS[kind]]
    def denied(self,mutate,reason):
        m=query(self.source,self.channel);mutate(m)
        with self.assertRaisesRegex(ValueError,reason):generate(self.source,self.channel,m,wire(m),MAPPED_PACKAGE,self.schemas)
    def test_01_actual_thirty_original_carriers(self):
        self.assertEqual(len(self.index),30)
        for row in self.index:
            raw=original(row['original_binding']);body=json.loads(raw);carrier,validator=schema(self.source,body['kind'])
            self.assertTrue(validator.is_valid(body));self.assertEqual(carrier,row['artifact']['carrier_ref'])
            self.assertEqual(sha(raw),row['artifact']['byte_sha256']);self.assertEqual(body['node_id'],row['artifact']['identity_ref'])
    def test_02_actual_ready_original_delivery_contract(self):
        self.assertTrue(self.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:context-delivery:v1-candidate',self.delivery))
        self.assertEqual(self.delivery['posture'],'ready');self.assertTrue(self.delivery['scope_enforced'])
    def test_03_actual_twenty_five_qualified_source_refs(self):self.assertEqual(len(self.delivery['included_refs']),25)
    def test_04_node_definition_layers(self):
        for node in self.bodies('ontology-node'):
            refs=node['payload']['semantic_state']['semantic_definition_refs']
            self.assertIn('cal.definition.ontology-node@1.0.0-candidate.1',refs);self.assertGreaterEqual(len(refs),2)
            self.assertGreaterEqual(len(node['payload']['semantic_state']['semantic_components']),2)
    def test_05_exact_global_typed_edges(self):
        for edge in self.bodies('ontology-edge'):
            p=edge['payload'];b=p['global_typed_relation_binding'];s=self.source.view.subjects[b['typed_relation_version_ref']]
            self.assertEqual(b['typed_relation_ref'],s['identity']);self.assertEqual(b['typed_relation_digest'],reader.adapter.model.artifact_ref(self.source.view,s)['byte_sha256'])
            self.assertEqual(p['closed_qualifiers'],s['record']['payload']['qualifiers']);self.assertEqual(p['edge_mode'],'global-projection');self.assertIsNone(p['local_interpretation'])
    def test_06_exact_native_governance_carrier_joins(self):
        rows=self.provenance['correspondence'];self.assertEqual(len(rows),25)
        for row in rows:self.assertTrue(row['governance_event_ref'].startswith('governance:'));self.assertEqual(row['semantic_event_ref']['semantic_cursor']>=1,True)
    def test_07_enclosing_and_selected_body_hashes_distinct(self):
        values=self.provenance['source_material_provenance'];self.assertEqual(len(values),25)
        self.assertTrue(any(r['original_material']['sha256']!=r['selected_original_body_sha256'] for r in values))
        for row in values:self.assertEqual(row['artifact']['byte_sha256'],row['selected_original_body_sha256'])
    def test_08_same_actual_signed_cut(self):self.assertEqual(self.delivery['source_cut'],self.source.source_cut)
    def test_09_cut_view_and_graph_carriers_close(self):
        nodes={b['node_id'] for b in self.bodies('ontology-node')};edges={b['node_id'] for b in self.bodies('ontology-edge')}
        for edge in self.bodies('ontology-edge'):self.assertIn(edge['payload']['source_node_ref'],nodes);self.assertIn(edge['payload']['target_node_ref'],nodes)
        cut=self.bodies('ontology-cut')[0];view=self.bodies('ontology-view')[0]
        self.assertEqual(set(cut['payload']['node_refs']),nodes);self.assertEqual(set(cut['payload']['edge_refs']),edges)
        self.assertEqual(view['payload']['cut_ref'],cut['node_id']);self.assertEqual(view['payload']['cut_digest'],cut['payload']['calculated_digest'])
    def test_10_no_replay_source(self):
        for kind in ['ontology-node','ontology-edge','ontology-cut','ontology-view']:
            for b in self.bodies(kind):self.assertFalse(b['payload']['replay_source'])
    def test_11_actual_zero_lesson_catalog_selection(self):
        s=load(HERE/'packages/0001/lesson-selection.json');self.assertEqual(s['current_catalog_lessons'],0);self.assertEqual(s['selected_lesson_refs'],[])
        raw=(HERE/'packages/0001/lesson-selection.json').read_bytes();self.assertEqual(self.delivery['lesson_selection_binding']['sha256'],sha(raw))
    def test_12_actual_request_original_bytes(self):
        raw=(HERE/'packages/0001/request.json').read_bytes();self.assertEqual(self.delivery['request_binding']['sha256'],sha(raw))
    def test_13_actual_delivery_original_binding(self):
        raw=(HERE/'packages/0001/delivery.json').read_bytes();self.assertEqual(self.provenance['verified_original_binding']['sha256'],sha(raw))
    def test_14_recorded_authenticated_actor(self):
        request=load(HERE/'packages/0001/request.json');trusted=load(HERE/'packages/0001/trusted-context.json')
        self.assertEqual(request['actor']['principal_ref'],trusted['principal_ref']);self.assertEqual(trusted['origin'],'verified-local-adapter')
        self.assertFalse(trusted['accept_client_supplied_authority_context']);self.assertTrue(self.schemas.valid('trusted-call-context',trusted))
    def test_15_nonce_proof_replay_denied(self):
        with self.assertRaisesRegex(ValueError,'already consumed'):self.channel.authenticate(self.proof)
    def test_16_wrong_key_denied(self):
        c=HostChannel(self.policy,self.policy_pin,PIN,self.source,self.schemas);key=Ed25519PrivateKey.generate()
        try:
            with self.assertRaises(Exception):c.authenticate(wire({'challenge':c.challenge,'signature':base64.b64encode(key.sign(wire(c.challenge))).decode()}))
        finally:c.close()
    def test_17_other_connection_proof_denied(self):
        c=HostChannel(self.policy,self.policy_pin,PIN,self.source,self.schemas)
        try:
            with self.assertRaisesRegex(ValueError,'another challenge'):c.authenticate(self.proof)
        finally:c.close()
    def test_18_unsigned_public_actor_denied(self):self.denied(lambda m:m['actor'].update(principal_ref='principal:other'),'authenticated host')
    def test_19_wrong_cut_denied(self):self.denied(lambda m:m['source_cut'].update(commit_sha256='0'*64),'cut differs')
    def test_20_unknown_selector_denied(self):
        self.denied(lambda m:m.update(selectors=[{**m['assignment'],'version_ref':'agent-assignment:missing@1'}]),'mapped source closure')
    def test_21_wrong_selector_bytes_denied(self):self.denied(lambda m:m.update(selectors=[{**m['assignment'],'byte_sha256':'0'*64}]),'mapped source closure')
    def test_22_required_source_exclusion_denied(self):self.denied(lambda m:m['exclusions'].append(records.GOAL),'required participation closure')
    def test_23_excessive_actions_denied(self):self.denied(lambda m:m['budget'].update(max_actions=1),'read action budget')
    def test_24_expired_deadline_denied(self):self.denied(lambda m:m['budget'].update(deadline=stamp(now()-timedelta(seconds=1))),'deadline expired')
    def test_25_too_small_output_budget_denied(self):self.denied(lambda m:m['budget'].update(max_output_bytes=1),'output byte budget')
    def test_26_wrong_intended_use_denied(self):self.denied(lambda m:m.update(intended_use='Do external effects'),'outside Coordination Context')
    def test_27_public_credential_field_denied(self):self.denied(lambda m:m.update(private_key='credential'),'Query schema invalid')
    def test_28_private_policy_revocation_denied(self):
        original_raw=self.policy.read_bytes();self.policy.write_bytes(original_raw+b' ')
        try:
            with self.assertRaisesRegex(ValueError,'revoked or changed'):self.channel.guard()
        finally:self.policy.write_bytes(original_raw)
    def test_29_closed_channel_denied(self):
        c=HostChannel(self.policy,self.policy_pin,PIN,self.source,self.schemas);c.close()
        with self.assertRaisesRegex(ValueError,'unauthenticated or closed'):c.guard()
    def test_30_recorded_host_key_custody_removed(self):self.assertTrue(load(HERE/'packages/0001/build-result.json')['owned_host_policy_and_transport_key_removed'])
    def test_31_no_Agent_or_API_claim(self):
        r=load(HERE/'packages/0001/build-result.json');self.assertEqual(r['active_Agents_created'],0);self.assertEqual(r['public_API_operations_added'],0);self.assertIsNone(r['actual_owner_outcome'])
    def test_32_recorded_view_expiry_bounded_by_period(self):
        p=load(reader.HERE/'packages/0001/period.json');self.assertLessEqual(EL.instant(self.delivery['expires_at']),EL.instant(p['expires_at']))
    def test_33_body_privacy(self):
        for row in self.index:EL.no_private_memory(load(ROOT/row['original_binding']['path']))
        EL.no_private_memory(self.delivery);EL.no_private_memory(self.provenance)
    def test_34_private_artifact_custody(self):
        for row in self.index:self.assertEqual(stat.S_IMODE((ROOT/row['original_binding']['path']).stat().st_mode),0o600)
    def test_35_request_and_view_Context_version(self):
        for k in ['context-request','context-view']:
            b=self.bodies(k)[0];self.assertEqual(b['context_ref'],records.CONTEXT);self.assertEqual(b['context_version_ref'],records.CONTEXT+'@'+records.VERSION)

    def test_36_request_snapshot_does_not_mutate_reader(self):
        before=copy.deepcopy(self.source.source_cut);m=query(self.source,self.channel)
        m['source_cut']['commit_sha256']='0'*64
        self.assertEqual(self.source.source_cut,before);self.source.guard()
    def test_37_request_refs_do_not_mutate_sources(self):
        before=copy.deepcopy(self.source.sources.resolve(records.ASSIGNMENT+'@'+records.VERSION)[0].artifact)
        m=query(self.source,self.channel);m['assignment']['byte_sha256']='0'*64
        after=self.source.sources.resolve(records.ASSIGNMENT+'@'+records.VERSION)[0].artifact
        self.assertEqual(before,after);self.source.guard()
    def test_38_delivery_snapshot_does_not_mutate_reader(self):
        before=copy.deepcopy(self.source.source_cut);m=query(self.source,self.channel)
        bodies,refs,delivery,proof,lesson=generate(self.source,self.channel,m,wire(m),MAPPED_PACKAGE,self.schemas)
        delivery['source_cut']['commit_sha256']='0'*64
        delivery['included_refs'][0]['byte_sha256']='0'*64
        proof['assignment']['byte_sha256']='0'*64
        self.assertEqual(before,self.source.source_cut)
        self.assertNotEqual(m['assignment']['byte_sha256'],'0'*64)
        self.source.guard();self.channel.guard()

