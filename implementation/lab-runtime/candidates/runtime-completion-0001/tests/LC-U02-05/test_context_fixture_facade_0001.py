"""In-memory fixture facade tests; no role, transport, key or scratch creation."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

R=Path(__file__).resolve().parents[6]
sys.path.insert(0,str(R/'implementation/lab-runtime/candidates/runtime-completion-0001'))
from t35_external_v1.phase_scoped_v2 import context_fixture_facade_0001 as f
from t35_external_v1.phase_scoped_v2 import context_fixture_provider_0001 as p
E=R/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U02-05'
PACKAGE=E/'mapper-integration-normal-0003-fixture-evidence/positive/synthetic-package'
NOW='2026-10-20T12:00:00Z'


def digest(raw):return hashlib.sha256(raw).hexdigest()


def setup_values():
    inputs={role:(PACKAGE/name).read_bytes() for role,name in [('mapper_manifest','manifest.json'),('mapping','mapping.json'),('native_output','native-output.json')]}
    source={'schema_version':'lab-context-fixture-source/v1-inert','fixture_only':True,
            'principal_ref':'fixture:principal','scope_ref':'fixture:scope','assignment_ref':'fixture:assignment@1',
            'work_ref':'fixture:work@1','coordination_ref':'fixture:coordination@1',
            'source_cut':json.loads(inputs['mapping'])['source_cut'],'not_before':'2026-10-20T11:59:00Z',
            'expires_at':'2026-10-20T12:15:00Z','authority_effect':'none','actual_owner_outcome':None}
    inputs['source']=f.encoded(source);inputs['profile']=f.encoded(f.PROFILE)
    channel={'schema_version':'lab-context-fixture-channel/v1-inert','fixture_only':True,
             'principal_ref':'fixture:principal','scope_ref':'fixture:scope','source_sha256':digest(inputs['source']),
             'profile_sha256':digest(inputs['profile']),'allowed_operations':['context.get','session.open'],
             'not_before':'2026-10-20T11:59:00Z','expires_at':'2026-10-20T12:10:00Z','revoked':False,
             'max_input_bytes':1048576,'max_output_bytes':2097152,'max_session_seconds':900,
             'authority_effect':'none','actual_owner_outcome':None}
    inputs['channel']=f.encoded(channel)
    logical='/work/out/legacy-fixture-source/mapped/packages/0001/'
    names={'mapping':logical+'mapping.json','native_output':logical+'native-output.json','mapper_manifest':logical+'manifest.json'}
    bindings={role:{'path':names.get(role,'fixture-input/'+role+'.json'),'sha256':digest(raw),'size_bytes':len(raw)} for role,raw in inputs.items()}
    raw_bodies=p.make_bodies(mapper_manifest_sha256=digest(inputs['mapper_manifest']),mapping_sha256=digest(inputs['mapping']))
    selection={'schema_version':'lab-context-fixture-facade-selection/v1-inert','fixture_only':True,'attempt_id':'pure-facade-0001',
               'bindings':bindings,'body_rows':[{'fixture_id':f'fixture:context:{i:02d}','sha256':digest(raw),'size_bytes':len(raw)} for i,raw in enumerate(raw_bodies)],
               'deadline':'2026-10-20T12:05:00Z','authority_effect':'none','actual_owner_outcome':None}
    return selection,inputs,raw_bodies


class Facade(unittest.TestCase):
    def setUp(self):self.selection,self.inputs,self.bodies=setup_values()

    def repin(self,role,value):
        self.inputs[role]=f.encoded(value)
        row=self.selection['bindings'][role];row['sha256']=digest(self.inputs[role]);row['size_bytes']=len(self.inputs[role])

    def make(self,**overrides):
        raw=f.encoded(self.selection);kw={'expected_selection_sha256':digest(raw),'selection_path':'fixture-input/facade-selection.json',
                                         'inputs':self.inputs,'body_bytes':self.bodies,'evaluation_time':NOW};kw.update(overrides)
        return f.FixtureFacade(raw,**kw)

    def invoke(self,facade=None):
        facade=facade or self.make();source,channel,schemas=facade.handles();query=facade.fixture_query(source,channel)
        return facade.generate(source,channel,query,f.compact(query),self.selection['bindings']['mapper_manifest']['sha256'],schemas)

    def test_query_is_exact_fixture_shape(self):
        facade=self.make();source,channel,_=facade.handles();q=facade.fixture_query(source,channel)
        self.assertTrue(q['fixture_only']);self.assertEqual(q['freshness_requirement'],'fixture-only')
        self.assertEqual(q['source_cut'],json.loads(self.inputs['mapping'])['source_cut']);self.assertNotIn('branch_ref',q['source_cut'])
        self.assertEqual(q['actor']['role_assignment_refs'],[]);self.assertEqual(q['selectors'],[])

    def test_generate_30_and_all_original_hash_joins(self):
        values,refs,delivery,provenance,lesson=self.invoke()
        self.assertEqual(len(values),30);self.assertEqual(len(refs),30)
        for identity,body in values.items():self.assertEqual(refs[identity]['byte_sha256'],digest(f.encoded(body)))
        self.assertEqual(delivery['artifact_refs'],list(refs.values()));self.assertEqual(delivery['posture'],'fixture-only')
        self.assertEqual(provenance['fixture_input_binding']['sha256'],digest(f.encoded(self.selection)))
        self.assertEqual(provenance['native_output_binding']['sha256'],digest(self.inputs['native_output']))
        self.assertFalse(provenance['original_generation_executed']);self.assertFalse(lesson['catalog_evaluated'])
        self.assertEqual(lesson['selected_lessons'],[]);self.assertNotIn('verified_original_binding',provenance)

    def test_handles_and_returned_mutation_do_not_change_selected_values(self):
        facade=self.make();source,channel,_=facade.handles();q=facade.fixture_query(source,channel);q['source_cut']['sha256']='0'*64
        self.inputs['source']=b'changed';self.selection['attempt_id']='changed'
        self.assertNotEqual(facade.fixture_query(source,channel)['source_cut'],q['source_cut'])

    def test_wrong_selection_pin_and_unknown_roles(self):
        with self.assertRaisesRegex(f.Refusal,'SELECTION_DIGEST'):self.make(expected_selection_sha256='0'*64)
        self.inputs['other']=b'{}'
        with self.assertRaisesRegex(f.Refusal,'INPUT_ROLES'):self.make()

    def test_wrong_source_channel_and_schema_handles(self):
        facade=self.make();source,channel,schemas=facade.handles();query=facade.fixture_query(source,channel)
        for a,b,c in [(f.FixtureSource(b'{}'),channel,schemas),(source,f.FixtureChannel(b'{}'),schemas),(source,channel,f.FixtureSchemas(b'{}')),(source,channel,None)]:
            with self.subTest(handle=c),self.assertRaises(f.Refusal):facade.generate(a,b,query,f.compact(query),self.selection['bindings']['mapper_manifest']['sha256'],c)

    def test_mismatched_cut_refuses_even_with_fresh_source_channel_pins(self):
        source=json.loads(self.inputs['source']);source['source_cut']['sha256']='9'*64;self.repin('source',source)
        channel=json.loads(self.inputs['channel']);channel['source_sha256']=digest(self.inputs['source']);self.repin('channel',channel)
        with self.assertRaisesRegex(f.Refusal,'SOURCE_CUT_JOIN'):self.make()

    def test_profile_schema_substitution_refuses_when_repinned(self):
        profile=json.loads(self.inputs['profile']);profile['body_schema']='actual-carrier';self.repin('profile',profile)
        channel=json.loads(self.inputs['channel']);channel['profile_sha256']=digest(self.inputs['profile']);self.repin('channel',channel)
        with self.assertRaisesRegex(f.Refusal,'FIXTURE_SCHEMA'):self.make()

    def test_scope_principal_and_operations_refuse(self):
        for key,value in [('scope_ref','fixture:other'),('principal_ref','fixture:other'),('allowed_operations',['context.get','session.open','write'])]:
            self.setUp();channel=json.loads(self.inputs['channel']);channel[key]=value;self.repin('channel',channel)
            with self.subTest(key=key),self.assertRaisesRegex(f.Refusal,'PERMISSION_JOIN'):self.make()

    def test_revocation_and_actual_posture_refuse(self):
        for key,value in [('revoked',True),('fixture_only',False),('authority_effect','grant'),('actual_owner_outcome','approve')]:
            self.setUp();channel=json.loads(self.inputs['channel']);channel[key]=value;self.repin('channel',channel)
            with self.subTest(key=key),self.assertRaisesRegex(f.Refusal,'FIXTURE_PERMISSION'):self.make()

    def test_closed_source_and_channel_fields(self):
        for role in ['source','channel']:
            self.setUp();v=json.loads(self.inputs[role]);v['extra']='marker';self.repin(role,v)
            with self.assertRaisesRegex(f.Refusal,'CLOSED_FIELDS'):self.make()

    def test_exact_interval_boundary_and_later_expiry_refuse(self):
        facade=self.make();source,channel,_=facade.handles()
        for now in ['2026-10-20T11:58:59Z','2026-10-20T12:05:00Z','2026-10-20T12:10:00Z']:
            with self.subTest(now=now),self.assertRaisesRegex(f.Refusal,'FIXTURE_INTERVAL'):facade.fixture_query(source,channel,evaluation_time=now)
        self.assertTrue(facade.fixture_query(source,channel,evaluation_time='2026-10-20T12:04:59Z')['fixture_only'])

    def test_permission_shorter_than_selected_deadline_refuses(self):
        channel=json.loads(self.inputs['channel']);channel['expires_at']='2026-10-20T12:04:59Z';self.repin('channel',channel)
        with self.assertRaisesRegex(f.Refusal,'FIXTURE_INTERVAL'):self.make()

    def test_boolean_limit_and_small_request_budget_refuse(self):
        channel=json.loads(self.inputs['channel']);channel['max_input_bytes']=True;self.repin('channel',channel)
        with self.assertRaisesRegex(f.Refusal,'PERMISSION_BOUND'):self.make()
        self.setUp();channel=json.loads(self.inputs['channel']);channel['max_input_bytes']=1;self.repin('channel',channel)
        facade=self.make();source,channel,_=facade.handles()
        with self.assertRaisesRegex(f.Refusal,'REQUEST_BUDGET'):facade.fixture_query(source,channel)

    def test_output_aggregate_budget_refuses(self):
        channel=json.loads(self.inputs['channel']);channel['max_output_bytes']=sum(map(len,self.bodies))+1;self.repin('channel',channel)
        with self.assertRaisesRegex(f.Refusal,'OUTPUT_BUDGET'):self.invoke()

    def test_wrong_request_body_bytes_extra_fields_and_pin(self):
        facade=self.make();source,channel,schemas=facade.handles();q=facade.fixture_query(source,channel);pin=self.selection['bindings']['mapper_manifest']['sha256']
        changed=copy.deepcopy(q);changed['selectors']=['invented']
        for message,raw,mapped in [(changed,f.compact(changed),pin),(q,f.compact(q)+b' ',pin),(q,f.compact(q),'0'*64),(dict(q,extra=True),f.compact(q),pin)]:
            with self.assertRaises(f.Refusal):facade.generate(source,channel,message,raw,mapped,schemas)

    def test_wrong_original_bytes_without_repin_refuse(self):
        self.inputs['native_output']+=b' '
        with self.assertRaisesRegex(f.Refusal,'SELECTED_BYTES'):self.make()

    def test_enriched_native_refuses_even_when_manifest_and_bodies_repinned(self):
        native=json.loads(self.inputs['native_output']);native['context']={'selected_node_ids':[]};self.repin('native_output',native)
        with self.assertRaisesRegex(f.Refusal,'NATIVE_FIXTURE_ENRICHMENT'):self.make()

    def test_wrong_manifest_member_binding_refuses(self):
        manifest=json.loads(self.inputs['mapper_manifest']);row=next(r for r in manifest['files'] if r['path'].endswith('/mapping.json'));row['sha256']='0'*64;self.repin('mapper_manifest',manifest)
        with self.assertRaisesRegex(f.Refusal,'MAPPER_MEMBER_JOIN'):self.make()

    def test_body_selection_and_duplicates_refuse(self):
        self.bodies=(self.bodies[0],)*30
        with self.assertRaisesRegex(f.Refusal,'BODY_SELECTION'):self.make()

    def test_mutated_internal_input_is_rechecked(self):
        facade=self.make();source,channel,schemas=facade.handles();q=facade.fixture_query(source,channel)
        facade._inputs=tuple((k,b'{}' if k=='source' else raw) for k,raw in facade._inputs)
        with self.assertRaises(f.Refusal):facade.generate(source,channel,q,f.compact(q),self.selection['bindings']['mapper_manifest']['sha256'],schemas)


if __name__=='__main__':unittest.main(verbosity=2)
