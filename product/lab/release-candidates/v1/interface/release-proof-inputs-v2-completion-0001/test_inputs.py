"""Owned technical custody fixtures; never genuine owner/source approval."""
import base64
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import time
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
RUN = ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T08/revision-0002'
name = '_cal_completion_protected_inputs_v2'
spec = importlib.util.spec_from_file_location(name, HERE/'__init__.py',
                                            submodule_search_locations=[str(HERE)])
component = importlib.util.module_from_spec(spec); sys.modules[name] = component
spec.loader.exec_module(component)
P = sys.modules[name+'.protected_inputs']; G = sys.modules[name+'.semantic_graph']

def save(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.write_bytes(raw); path.chmod(0o600)

def locator(path, root_id='scratch'):
    info = path.stat()
    return dict(root_id=root_id, path=path.name, size=info.st_size, **P.metadata(info))

class Fixture:
    def __init__(self, parent):
        self.root = parent; self.payloads = {}; self.kinds = {}; self.tables = []
        self.private = Ed25519PrivateKey.generate()  # Own ephemeral technical key only.
        self.public = base64.b64encode(self.private.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)).decode()
        self.principal = 'technical-principal:T08-owned-custody'
        source_raw = P.canonical({'schema_version': 'technical-source-table/v1', 'files': []})
        profile_raw = P.canonical({'schema_version': 'technical-profile-table/v1', 'files': []})
        self.add('source', 'source-manifest', source_raw)
        self.add('profile', 'contract-profile', profile_raw)
        self.source = {'ref': 'technical:owned/source', 'sha256': P.digest(source_raw)}
        self.profile = {'ref': 'technical:owned/profile', 'sha256': P.digest(profile_raw)}
        self.cut = {'branch_ref': 'technical:branch', 'store_ref': 'technical:owned-store',
            'commit_sequence': 1, 'commit_sha256': P.digest(b'technical-own-cut'),
            'source_profile_sha256': P.digest(profile_raw), 'streams': []}
        self.add('state', 'custody-state', P.canonical({
            'schema_version': 'lab-protected-input-custody-state/v1-candidate',
            'principal_ref': self.principal, 'revoked': False, 'authority_effect': 'none'}))

    def add(self, identity, kind, raw):
        self.payloads[identity] = raw; self.kinds[identity] = kind
        save(self.root/identity, raw)

    def reader(self, seconds=300, selector_edit=None, signer=None):
        rows = []
        for identity in sorted(self.payloads):
            path = self.root/identity; info = path.stat()
            rows.append(dict(id=identity, root_id='scratch', path=identity,
                logical_path='technical:owned/'+identity, kind=self.kinds[identity],
                sha256=P.digest(path.read_bytes()), size=info.st_size, **P.metadata(info)))
        selector = {'schema_version': 'lab-protected-input-selector/v1-candidate',
            'source_binding': self.source, 'profile_binding': self.profile,
            'source_cut': self.cut, 'principal_ref': self.principal,
            'operation': 'release.prepare',
            'roots': [dict(id='scratch', path=str(self.root), **P.metadata(self.root.stat()))],
            'files': rows, 'proof_tables': self.tables + [
                {'file_id': 'source', 'row_selector': '/files', 'coverage_file_ids': []},
                {'file_id': 'profile', 'row_selector': '/files', 'coverage_file_ids': []}],
            'custody_state_file_id': 'state',
            'authority_effect': 'none'}
        if selector_edit: selector_edit(selector)
        raw = P.canonical(selector); save(self.root/'selector-control', raw)
        selected = {'ref': 'technical:owned/selector-control', 'sha256': P.digest(raw)}
        clock = datetime.now(timezone.utc)
        payload = {'schema_version': 'lab-protected-input-custody-grant/v1-candidate',
            'selector_binding': selected, 'source_binding': self.source,
            'profile_binding': self.profile, 'source_cut': self.cut,
            'principal_ref': self.principal, 'operation': 'release.prepare',
            'not_before': (clock-timedelta(seconds=1)).isoformat(),
            'expires_at': (clock+timedelta(seconds=seconds)).isoformat(), 'authority_effect': 'none'}
        grant = P.canonical({'payload': payload, 'signature_b64': base64.b64encode(
            (signer or self.private).sign(P.canonical(payload))).decode()})
        save(self.root/'grant-control', grant)
        anchor = P.CustodyAnchor(self.principal, self.public, self.source, self.profile,
            self.cut, 'release.prepare', selected,
            {'ref': 'technical:owned/grant-control', 'sha256': P.digest(grant)},
            locator(self.root/'selector-control'), locator(self.root/'grant-control'))
        return P.ProtectedReader(raw, grant, anchor)

    def graph(self, cycle=False, omitted_field=False):
        for identity, relative, kind in (
            ('schema', 'authority/artifact-types/governed-model/v1/schema.json', 'governed-schema'),
            ('descriptor', 'authority/artifact-types/governed-model/v1/artifact.json', 'governed-descriptor')):
            self.add(identity, kind, (ROOT/relative).read_bytes())
        for identity, other, direction in [('A', 'B', 'source'), ('B', 'A', 'source' if cycle else 'target')]:
            value = {'schema_version': 'cyberalchemy-lab-governed-model/v1',
                'node_id': identity, 'kind': 'governed-model', 'name': 'Owned technical '+identity,
                'lifecycle_state': 'candidate', 'authority_effect': 'none',
                'owner_ref': 'role:technical-fixture-only', 'scope_ref': 'scope:T08-owned',
                'evidence_refs': [], 'challenge_route': 'technical:challenge', 'successor_refs': [],
                'relation_refs': [{'relation_kind_ref': 'relation.successor-of',
                    'direction': direction, 'counterpart_kind': 'governed-model',
                    'counterpart_ref': other}],
                'payload': {'model_kind': 'technical-fixture', 'contract_ref': 'proof:schema',
                    'version_ref': identity+'@technical.1', 'rule_refs': ['proof:schema'],
                    'extension_policy_ref': 'proof:descriptor'},
                'claim_ceiling': 'Original schema/role validation of technical graph; no actual owner or admission.'}
            self.add(identity, 'governed-record', P.canonical(value))
        fields = []
        mapping = {'/owner_ref': 'current-context', '/scope_ref': 'current-context',
            '/evidence_refs': 'verified-proof', '/successor_refs': 'semantic-node',
            '/payload/contract_ref': 'verified-proof', '/payload/version_ref': 'self-identity',
            '/payload/rule_refs': 'verified-proof', '/payload/extension_policy_ref': 'verified-proof'}
        for pointer, disposition in mapping.items():
            fields.append({'instance_pointer': pointer,
                'schema_pointer': G.expected_schema_pointer(pointer), 'disposition': disposition})
        if omitted_field: fields.pop()
        policy = {'schema_version': 'lab-schema-declared-semantic-graph/v1-candidate',
            'profiles': [{'kind': 'governed-model', 'schema_file_id': 'schema',
                          'descriptor_file_id': 'descriptor', 'fields': fields}],
            'node_file_ids': ['A', 'B'], 'proof_references': [
                {'reference': 'proof:schema', 'file_id': 'schema'},
                {'reference': 'proof:descriptor', 'file_id': 'descriptor'}],
            'context_references': ['role:technical-fixture-only', 'scope:T08-owned'],
            'authority_effect': 'none'}
        self.add('policy', 'semantic-policy', P.canonical(policy))
        return self.reader()

class ReaderCases(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='owned-reader-', dir=RUN)
        self.root = Path(self.temp.name); self.fixture = Fixture(self.root)
        self.fixture.add('body', 'host-dependency', b'exact owned technical host bytes')
    def tearDown(self): self.temp.cleanup()
    def test_signed_positive_and_fresh_full_pre_post_boundary(self):
        reader = self.fixture.reader()
        with reader.boundary(): self.assertEqual(reader.read('body', 'host-dependency'), self.fixture.payloads['body'])
        self.assertFalse(reader.verify()['public_export_allowed'])
    def test_closed_published_selector_and_grant_schema_contracts(self):
        from jsonschema import Draft202012Validator, FormatChecker
        reader = self.fixture.reader()
        for file, value in [('protected-selector.schema.json', reader.selector),
                            ('custody-grant.schema.json', reader.grant)]:
            schema = json.loads((HERE/file).read_text())
            Draft202012Validator.check_schema(schema)
            Draft202012Validator(schema, format_checker=FormatChecker()).validate(value)
            wrong = dict(value, extra=True)
            self.assertFalse(Draft202012Validator(schema).is_valid(wrong))
    def test_other_key_signature_cannot_create_custody(self):
        with self.assertRaisesRegex(P.Refusal, 'signature'):
            self.fixture.reader(signer=Ed25519PrivateKey.generate())
    def test_equal_size_tamper_refused(self):
        reader = self.fixture.reader(); path = self.root/'body'; raw = path.read_bytes()
        save(path, raw[:-1]+b'X')
        with self.assertRaisesRegex(P.Refusal, 'bytes'): reader.verify()
    def test_mode_refused(self):
        reader = self.fixture.reader(); (self.root/'body').chmod(0o644)
        with self.assertRaisesRegex(P.Refusal, 'mode'): reader.verify()
    def test_same_bytes_new_inode_refused(self):
        reader = self.fixture.reader(); body = self.root/'body'
        save(self.root/'replacement', body.read_bytes()); os.replace(self.root/'replacement', body)
        with self.assertRaisesRegex(P.Refusal, 'identity'): reader.verify()
    def test_symlink_refused(self):
        reader = self.fixture.reader(); (self.root/'body').unlink()
        (self.root/'body').symlink_to(self.root/'state')
        with self.assertRaisesRegex(P.Refusal, 'no-follow'): reader.verify()
    def test_current_custody_revocation_and_control_tamper_refused(self):
        reader = self.fixture.reader()
        save(self.root/'grant-control', b'{}')
        with self.assertRaises(P.Refusal): reader.read('body')
        reader = self.fixture.reader()
        state = P.parse((self.root/'state').read_bytes()); state['revoked'] = True
        save(self.root/'state', P.canonical(state))
        with self.assertRaises(P.Refusal): reader.read('body')
    def test_real_expiry_between_entry_and_exit(self):
        reader = self.fixture.reader(seconds=1)
        with self.assertRaisesRegex(P.Refusal, 'expired'):
            with reader.boundary(): time.sleep(1.1)
    def test_unknown_kind_duplicate_and_parent_escape_refused(self):
        for edit in (lambda s: s['files'][0].update(kind='unrestricted-private-key'),
                     lambda s: s['files'].append(s['files'][0].copy()),
                     lambda s: s['files'][0].update(path='../outside')):
            with self.assertRaises(P.Refusal): self.fixture.reader(selector_edit=edit)
    def test_runtime_selector_and_index_mutation_refused(self):
        reader = self.fixture.reader(); reader.files.pop('body')
        with self.assertRaisesRegex(P.Refusal, 'indices'): reader.verify()
    def test_missing_original_proof_row_refused(self):
        value = {'files': [{'path': 'technical:owned/body', 'sha256': P.digest(self.fixture.payloads['body'])}]}
        self.fixture.add('table', 'source-manifest', P.canonical(value))
        self.fixture.tables = [{'file_id': 'table', 'row_selector': '/files', 'coverage_file_ids': ['body']}]
        self.assertEqual(self.fixture.reader().verify()['proof_rows'], 1)
        self.fixture.add('table', 'source-manifest', P.canonical({'files': []}))
        with self.assertRaisesRegex(P.Refusal, 'omitted'): self.fixture.reader().verify()
    def test_mandatory_source_profile_coverage_cannot_be_removed(self):
        def edit(selector):
            selector['proof_tables'] = [t for t in selector['proof_tables'] if t['file_id'] != 'source']
        with self.assertRaisesRegex(P.Refusal, 'mandatory complete'):
            self.fixture.reader(selector_edit=edit)
    def test_original_external_dependency_cannot_disappear(self):
        row={'path':'technical:owned/body','sha256':P.digest(self.fixture.payloads['body'])}
        raw=P.canonical({'files':[],'external_execution_dependency_bindings':[row]})
        self.fixture.add('profile','contract-profile',raw);self.fixture.profile['sha256']=P.digest(raw)
        with self.assertRaisesRegex(P.Refusal,'mandatory original external'):self.fixture.reader().verify()
        self.fixture.tables=[{'file_id':'profile','row_selector':'/external_execution_dependency_bindings','coverage_file_ids':['body']}]
        self.assertEqual(self.fixture.reader().verify()['proof_rows'],1)
        self.fixture.tables[0]['coverage_file_ids']=[]
        with self.assertRaisesRegex(P.Refusal,'omitted'):self.fixture.reader().verify()
    def test_original_native_abi_wheel_proof_rows_are_mandatory(self):
        row={'path':'technical:owned/body','sha256':P.digest(self.fixture.payloads['body'])}
        raw=P.canonical({'complete_source_bindings':[],'complete_profile_bindings':[],
            'schema_execution_bindings':[],'host_native_binding':row,
            'host_ABI_library_bindings':[row],'offline_environment_wheel_bindings':[row]})
        self.fixture.add('environment','environment-contract',raw)
        self.fixture.tables=[{'file_id':'environment','row_selector':key,'coverage_file_ids':[]}
            for key in ('/complete_source_bindings','/complete_profile_bindings','/schema_execution_bindings')]
        with self.assertRaisesRegex(P.Refusal,'mandatory original external'):self.fixture.reader().verify()
        self.fixture.tables +=[{'file_id':'environment','row_selector':key,'coverage_file_ids':['body']}
            for key in ('/host_native_binding','/host_ABI_library_bindings','/offline_environment_wheel_bindings')]
        self.assertEqual(self.fixture.reader().verify()['proof_rows'],3)
        self.fixture.tables[-1]['coverage_file_ids']=[]
        with self.assertRaisesRegex(P.Refusal,'omitted'):self.fixture.reader().verify()
    def test_three_actual_composite_environment_tables_verified(self):
        row = {'path': 'technical:owned/body', 'sha256': P.digest(self.fixture.payloads['body'])}
        document = {'schema_version': 'technical-composite-environment/v1',
            'complete_source_bindings': [row], 'complete_profile_bindings': [row],
            'schema_execution_bindings': [row]}
        self.fixture.add('environment', 'environment-contract', P.canonical(document))
        self.fixture.tables = [{'file_id': 'environment', 'row_selector': key,
                               'coverage_file_ids': ['body']} for key in
            ('/complete_source_bindings', '/complete_profile_bindings', '/schema_execution_bindings')]
        self.assertEqual(self.fixture.reader().verify()['proof_rows'], 3)
        self.fixture.tables.pop()
        with self.assertRaisesRegex(P.Refusal, 'complete composite'):
            self.fixture.reader()
    def test_full_size_closed_24497_row_technical_table(self):
        ids = []; rows = []
        for i in range(24497):
            identity = 'row-'+str(i).zfill(5); raw = ('technical-proof-row:'+str(i)).encode()
            self.fixture.add(identity, 'history-proof', raw); ids.append(identity)
            rows.append({'path': 'technical:owned/'+identity, 'sha256': P.digest(raw)})
        value = {'schema_version': 'technical-full-size-proof-table/v1', 'files': rows,
            'size_padding_reason': 'Technical size stress only; no historical source claim.',
            'opaque_history_cycle_annotations': [{'source': 'technical:A', 'dependency': 'technical:B'},
                                                {'source': 'technical:B', 'dependency': 'technical:A'}],
            'technical_padding': 'x'*(27*1024*1024)}
        raw = P.canonical(value); self.fixture.add('table', 'source-manifest', raw)
        self.fixture.tables = [{'file_id': 'table', 'row_selector': '/files', 'coverage_file_ids': ids}]
        reader = self.fixture.reader()
        with reader.boundary():
            observed = reader.verify()
            self.assertEqual(observed['proof_rows'], 24497)
            self.assertGreater(len(reader.read('table')), 27*1024*1024)
        self.assertEqual((self.root/'table').read_bytes(), raw)


REGISTRY='authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json'
CATALOG='product/lab/release-candidates/v1/interface/api-integration-v16/catalog-representations.json'
KERNEL='product/lab/release-candidates/v1/interface/custody-correction-v4/runtime/lab_runtime/'
RELATIONS='authority/admissions/governance-transaction-surface/v1/registries/relation-kind-registry.json'

class VariedFixture(Fixture):
    def __init__(self,parent):
        super().__init__(parent)
        self.registry=json.loads((ROOT/REGISTRY).read_text());self.catalog=json.loads((ROOT/CATALOG).read_text())
        self.add('registry','history-proof',(ROOT/REGISTRY).read_bytes())
        self.add('catalog','history-proof',(ROOT/CATALOG).read_bytes())
        self.add('kernel-identity','host-dependency',(ROOT/(KERNEL+'common.py')).read_bytes())
        self.add('kernel-operations','host-dependency',(ROOT/(KERNEL+'operations.py')).read_bytes())
        self.add('relation-registry','history-proof',(ROOT/RELATIONS).read_bytes())
        self.schema_rows=[];self.profiles=[];self.nodes=[];self.declarations=[];self.relations=[];self.contexts=set();self.subjects={};self.current={};self.edges=[];self.originals=[]

    def document(self,path):
        path=(ROOT/path).resolve().relative_to(ROOT).as_posix()
        if path in {r['path'] for r in self.schema_rows}:return
        identity='schema-'+str(len(self.schema_rows));self.add(identity,'governed-schema',(ROOT/path).read_bytes())
        self.schema_rows.append({'path':path,'file_id':identity})
        def walk(value):
            if type(value)is dict:
                ref=value.get('$ref','')
                if ref and not ref.startswith('#'):
                    self.document((Path(path).parent/ref.split('#')[0]).as_posix())
                for child in value.values():walk(child)
            elif type(value)is list:
                for child in value:walk(child)
        walk(json.loads((ROOT/path).read_text()))

    def carrier(self,ref,registered=False):
        pid=ref+(':registered'if registered else ':instance')
        if any(p['profile_id']==pid for p in self.profiles):return pid
        index,c=next((i,c)for i,c in enumerate(self.registry['admitted_contracts'])if c['artifact_type_ref']==ref)
        row=next(r for r in self.catalog['rows']if r['represented_contract_ref']==ref)
        did='descriptor-'+str(len(self.profiles));self.add(did,'governed-descriptor',(ROOT/c['artifact_path']).read_bytes());self.document(c['schema_path'])
        selector='#/properties/registered_types/items'if registered else c['schema_selector']
        # Schema-resolved locations are asserted against the independent original
        # schema reader. Dispositions here are an explicit technical fixture,
        # not the future final package's production semantic policy.
        docs=G.Schemas(self.reader(),self.schema_rows);slots=docs.slots(c['schema_path'],selector)
        fields=[{'instance_pointer':key,'schema_locations':[list(loc)for loc in locations], 'disposition':'current-context'}for key,locations in slots.items()]
        for field in fields:
            key=field['instance_pointer']
            if key=='/successor_refs/*':field['disposition']='semantic-node'
            if key=='/payload/version_ref':field['disposition']='self-identity'
            if ref.endswith('typed-relation/v3')and key in ('/payload/source/ref','/payload/source/version_ref','/payload/target/ref','/payload/target/version_ref'):field['disposition']='semantic-node'
        self.profiles.append({'profile_id':pid,'carrier_ref':ref,'instance_schema_selector':selector,
            'registry_pointer':'/admitted_contracts/'+str(index),'descriptor_file_id':did,'descriptor_pointer':row['selector'],'fields':fields})
        return pid

    def original(self,file_id,path,carrier,category='artifact-instance',registered=False,body_pointer=None):
        raw=(ROOT/path).read_bytes();value=json.loads(raw)
        if body_pointer is not None:raw=P.canonical(G.pointer(value,body_pointer))
        self.originals.append({'path':path,'sha256':P.digest((ROOT/path).read_bytes()),'body_pointer':body_pointer,'selected_body_sha256':P.digest(raw)})
        return self.node(file_id,raw,carrier,category,registered)

    def node(self,file_id,raw,carrier,category='artifact-instance',registered=False):
        pid=self.carrier(carrier,registered);p=next(p for p in self.profiles if p['profile_id']==pid)
        c=G.pointer(self.registry,p['registry_pointer']);d=G.pointer(json.loads(self.payloads[p['descriptor_file_id']]),p['descriptor_pointer']);record=json.loads(raw)
        field=d.get('instance_contract',{}).get('identity_field')
        if registered:ident=record['artifact_type_ref'].rsplit('/',1)[0];version=record['artifact_type_ref']
        elif field:ident=record[field];version=ident+'@T08-owned-technical.1'
        else:ident=next(record[k]for k in ('definition_id','artifact_type_ref','node_id','record_id','migration_manifest_id','product_id','project_id')if k in record);version=ident+'@T08-owned-technical.1'
        self.add(file_id,'governed-record',raw)
        self.nodes.append({'file_id':file_id,'profile_id':pid,'version_ref':version,'category':category})
        self.subjects[version]={'identity':ident,'version_ref':version,'category':category,'kind':c['semantic_kind'],'effective_state':'candidate-current','carrier_ref':carrier,'source':{'path':'technical:owned/'+file_id,'sha256':P.digest(raw)}}
        self.current[ident]=version
        for f in p['fields']:
            for v in G.values(record,f['instance_pointer']):
                if type(v)is str and f['disposition']=='current-context':self.contexts.add(v)
                elif type(v)is str and f['disposition']=='semantic-node':self.edges.append({'source':ident,'dependency':v})
        return ident,version

    def all_embedded_declarations(self):
        self.document('authority/artifact-types/artifact-type/v1/schema.json')
        did='foundation-declarations';self.add(did,'governed-descriptor',(ROOT/'authority/artifact-types/artifact-type/v1/artifact.json').read_bytes())
        for row in self.catalog['rows']:
            if row['representation_kind']=='embedded-contract-declaration':
                self.declarations.append({'file_id':did,'pointer':row['selector'],'schema_path':'authority/artifact-types/artifact-type/v1/schema.json','schema_selector':'#/properties/registered_types/items'})

    def relation(self,ref):
        reg=json.loads((ROOT/RELATIONS).read_text());i,r=next((i,r)for i,r in enumerate(reg['entries'])if r['relation_kind_ref']==ref)
        rid='relation-'+str(len(self.relations));self.add(rid,'governed-descriptor',(ROOT/r['instance_path']).read_bytes())
        qc=json.loads(self.payloads[rid])['payload']['qualifier_contract']
        docs=G.Schemas(self.reader(),self.schema_rows)
        qschema={'type':'object','additionalProperties':False,'required':qc['required_axes'],'properties':qc['properties']}
        slots=docs.slots(r['instance_path'],'#/payload/qualifier_contract',qschema)
        qfields=[{'instance_pointer':key,'schema_locations':[list(loc)for loc in locations],
            'disposition':'semantic-node' if key=='/definition_version_ref' else 'current-context'}for key,locations in slots.items()]
        self.relations.append({'file_id':rid,'registry_file_id':'relation-registry','registry_pointer':'/entries/'+str(i),'qualifier_fields':qfields})

    def finish(self,edit=None,eligibility_edit=None):
        if not self.declarations:self.all_embedded_declarations()
        eligibility={'schema_version':'lab-native-subject-selection/v1-candidate','source_binding':self.source,'profile_binding':self.profile,'source_cut':self.cut,'current_by_identity':self.current,'subjects':self.subjects,'authority_effect':'none'}
        if eligibility_edit:eligibility_edit(eligibility)
        self.add('eligibility','history-proof',P.canonical(eligibility))
        policy={'schema_version':'lab-schema-declared-semantic-graph/v2-candidate','registry_file_id':'registry','catalog_file_id':'catalog','kernel_identity_file_id':'kernel-identity','kernel_operations_file_id':'kernel-operations','schemas':self.schema_rows,'profiles':self.profiles,'declarations':self.declarations,'nodes':self.nodes,'eligibility_file_id':'eligibility','proof_references':[],'context_references':sorted(self.contexts),'relation_contracts':self.relations,'authority_effect':'none'}
        if edit:edit(policy)
        self.add('policy','semantic-policy',P.canonical(policy));reader=self.reader()
        anchor=G.GraphAnchor({'ref':'technical:owned/policy','sha256':P.digest(self.payloads['policy'])},{'ref':'technical:owned/eligibility','sha256':P.digest(self.payloads['eligibility'])},self.source,self.profile,self.cut,('candidate-current',))
        return reader,anchor

class GraphCases(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='owned-graph-',dir=RUN);self.f=VariedFixture(Path(self.temp.name))
    def tearDown(self):self.temp.cleanup()
    def base(self):
        self.f.original('definition','authority/artifact-types/definition/v2/fixtures/valid/definition.json','cal.artifact-type.definition/v2','definition')
        self.f.original('owners','authority/owners/foundation-01/v1/owners.json','cal.artifact-type.owner-registry/v1')
        # Original registered entry, not a generic descriptor/instance wrapper.
        self.f.original('registered','authority/artifact-types/artifact-type/v3/artifact.json','cal.artifact-type.artifact-type/v3','artifact-type',True,'/registered_types/0')
        self.f.all_embedded_declarations()
    def check(self,reader,anchor,edges=None):
        return G.verify_graph(reader,'policy',self.f.edges if edges is None else edges,list(self.f.current),anchor)
    def test_original_varied_carriers_and_seven_original_fragments(self):
        self.base();r,a=self.f.finish();result=self.check(r,a)
        self.assertEqual(result['nodes'],3);self.assertEqual(result['profiles'],3);self.assertEqual(result['declarations'],7)
        self.assertNotIn('kind',json.loads(self.f.payloads['definition']))
        self.assertEqual(self.f.subjects[self.f.current['cal.artifact-type.owner-registry/v1']]['identity'],'cal.artifact-type.owner-registry/v1')
        self.assertFalse(result['admission_or_owner_authority'])
    def test_closed_published_semantic_policy_schema(self):
        from jsonschema import Draft202012Validator
        self.typed();r,a=self.f.finish();schema=json.loads((HERE/'semantic-policy.schema.json').read_text())
        Draft202012Validator.check_schema(schema);validator=Draft202012Validator(schema)
        policy=json.loads(self.f.payloads['policy']);validator.validate(policy)
        policy['profiles'][0]['unselected_extra']=True;self.assertFalse(validator.is_valid(policy))
    def test_original_foundation_empty_roles_and_allof_ref_items_coverage(self):
        self.base();r,a=self.f.finish();result=self.check(r,a)
        p=next(p for p in self.f.profiles if 'owner-registry' in p['carrier_ref'])
        self.assertTrue(any(f['instance_pointer']=='/source_direction/generator_ref' for f in p['fields']))
        self.assertEqual(result['nodes'],3)
        definition=next(p for p in self.f.profiles if p['carrier_ref']=='cal.artifact-type.definition/v2')
        self.assertTrue(any(f['instance_pointer']=='/source_refs/*/source_ref' for f in definition['fields']))
    def test_missing_nested_ref_disposition_refused(self):
        self.base();r,a=self.f.finish(edit=lambda p:p['profiles'][0]['fields'].pop())
        with self.assertRaisesRegex(P.Refusal,'omitted'):self.check(r,a)
    def test_wrong_fragment_selector_refused(self):
        self.base();r,a=self.f.finish(edit=lambda p:p['profiles'][1].update(descriptor_pointer='/registered_types/3'))
        with self.assertRaisesRegex(P.Refusal,'fragment'):self.check(r,a)
    def test_fragment_as_node_without_native_category_refused(self):
        self.base();r,a=self.f.finish(edit=lambda p:p['nodes'][2].update(category='artifact-instance'))
        with self.assertRaisesRegex(P.Refusal,'category'):self.check(r,a)
    def test_native_carrier_category_substitution_refused(self):
        self.base();r,a=self.f.finish(edit=lambda p:p['nodes'][0].update(category='artifact-instance'))
        with self.assertRaisesRegex(P.Refusal,'category/carrier'):self.check(r,a)
    def test_native_version_identity_mismatch_refused(self):
        self.base();r,a=self.f.finish(edit=lambda p:p['nodes'][0].update(version_ref='different-identity@1'))
        with self.assertRaisesRegex(P.Refusal,'qualify exact identity'):self.check(r,a)
    def test_wrong_type_registry_selector_refused(self):
        self.base();r,a=self.f.finish(edit=lambda p:p['profiles'][0].update(registry_pointer='/admitted_contracts/0'))
        with self.assertRaisesRegex(P.Refusal,'contract'):self.check(r,a)
    def test_historical_carrier_refused(self):
        self.f.original('historical-definition','authority/artifact-types/definition/v1/fixtures/valid/definition.json','cal.artifact-type.definition/v1','definition');r,a=self.f.finish()
        with self.assertRaisesRegex(P.Refusal,'historical'):self.check(r,a)
    def test_exact_current_version_changed_refused(self):
        self.base();r,a=self.f.finish(eligibility_edit=lambda e:e['current_by_identity'].update({'CAL-FIXTURE-DEF-001':'CAL-FIXTURE-DEF-001@wrong'}))
        with self.assertRaisesRegex(P.Refusal,'eligible-current'):self.check(r,a)
    def test_withdrawn_subject_refused(self):
        self.base();r,a=self.f.finish(eligibility_edit=lambda e:next(iter(e['subjects'].values())).update(effective_state='withdrawn'))
        with self.assertRaisesRegex(P.Refusal,'eligible-current'):self.check(r,a)
    def test_exact_body_provenance_kind_spoof_refused(self):
        self.base();r,a=self.f.finish(eligibility_edit=lambda e:next(iter(e['subjects'].values())).update(kind='method'))
        with self.assertRaisesRegex(P.Refusal,'provenance'):self.check(r,a)
    def test_wrong_independent_graph_pin_refused(self):
        self.base();r,a=self.f.finish();a.policy_binding['sha256']='0'*64
        with self.assertRaisesRegex(P.Refusal,'policy pin'):self.check(r,a)
    def test_body_kind_discriminator_spoof_refused(self):
        self.base();value=json.loads(self.f.payloads['definition']);value['schema_version']='cyberalchemy-lab-definition/v1';self.f.add('definition','governed-record',P.canonical(value));r,a=self.f.finish()
        with self.assertRaisesRegex(P.Refusal,'discriminator'):self.check(r,a)
    def test_invalid_protected_instance_is_not_in_public_refusal(self):
        self.base();value=json.loads(self.f.payloads['definition']);sentinel='owned-private-sentinel-DO-NOT-EXPORT'
        value['unexpected_private_field']=sentinel;self.f.add('definition','governed-record',P.canonical(value));r,a=self.f.finish()
        try:self.check(r,a)
        except P.Refusal as exc:
            self.assertNotIn(sentinel,str(exc));self.assertIsNone(exc.__cause__)
        else:self.fail('original closed schema must refuse private extra field')
    def typed(self):
        self.base()
        p='authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors/typed-relation/v3/fixtures/valid/record.json'
        value=json.loads((ROOT/p).read_text())
        # Explicitly a NEW owned technical case. Original untouched bytes are
        # independently selected and schema-validated in the next case.
        value['node_id']='technical:typed-carries-definition'
        source='cal.artifact-type.artifact-type';target='CAL-FIXTURE-DEF-001'
        value['payload']['relation_kind_ref']='relation.carries-definition'
        value['payload']['source']={'ref':source,'kind':'artifact-type','version_ref':self.f.current[source]}
        value['payload']['target']={'ref':target,'kind':'definition','version_ref':self.f.current[target]}
        value['payload']['qualifiers']={'definition_version_ref':self.f.current[target],'definition_sha256':P.digest(self.f.payloads['definition'])}
        self.f.node('typed',P.canonical(value),'cal.artifact-type.typed-relation/v3','typed-relation')
        # Fields name version and identity of same endpoint: dependency collapses
        # only after exact current-version validation, without lost provenance.
        self.f.edges=[{'source':'technical:typed-carries-definition','dependency':source},{'source':'technical:typed-carries-definition','dependency':target}]
        self.f.relation('relation.carries-definition')
    def test_original_typed_sample_schema_and_honest_unresolved_endpoints(self):
        p='authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors/typed-relation/v3/fixtures/valid/record.json'
        self.f.original('original-typed',p,'cal.artifact-type.typed-relation/v3','typed-relation');self.f.relation('relation.successor-of');r,a=self.f.finish()
        with self.assertRaisesRegex(P.Refusal,'omitted'):self.check(r,a)
    def test_actual_native_typed_qualifier_version_refs(self):
        self.typed();r,a=self.f.finish();result=self.check(r,a);self.assertEqual(result['edges'],2);self.assertEqual(result['nodes'],4)
        p=next(p for p in self.f.profiles if p['carrier_ref']=='cal.artifact-type.typed-relation/v3')
        self.assertTrue(any(f['instance_pointer']=='/payload/source/ref' for f in p['fields']))
    def test_qualifier_ref_classification_omitted_refused(self):
        self.typed();r,a=self.f.finish(edit=lambda p:p['relation_contracts'][0]['qualifier_fields'].clear())
        with self.assertRaisesRegex(P.Refusal,'qualifier reference omitted'):self.check(r,a)
    def test_invalid_protected_qualifier_is_not_in_public_refusal(self):
        self.typed();v=json.loads(self.f.payloads['typed']);sentinel='owned-qualifier-private-sentinel'
        v['payload']['qualifiers']['unexpected_private_axis']=sentinel
        self.f.add('typed','governed-record',P.canonical(v))
        self.f.subjects[self.f.current[v['node_id']]]['source']['sha256']=P.digest(self.f.payloads['typed']);r,a=self.f.finish()
        try:self.check(r,a)
        except P.Refusal as exc:
            self.assertIn(str(exc),('actual original schema refused','actual qualifier contract refused'))
            self.assertNotIn(sentinel,str(exc));self.assertIsNone(exc.__cause__)
        else:self.fail('original qualifier contract must refuse unknown private axis')
    def test_typed_endpoint_version_substitution_refused(self):
        self.typed();v=json.loads(self.f.payloads['typed']);v['payload']['target']['version_ref']='CAL-FIXTURE-DEF-001@wrong';self.f.add('typed','governed-record',P.canonical(v));self.f.subjects[self.f.current[v['node_id']]]['source']['sha256']=P.digest(self.f.payloads['typed']);r,a=self.f.finish()
        with self.assertRaises(P.Refusal):self.check(r,a)
    def test_omitted_semantic_edge_refused(self):
        self.typed();r,a=self.f.finish()
        with self.assertRaisesRegex(P.Refusal,'edges'):self.check(r,a,[])
    def test_duplicate_semantic_edge_refused(self):
        self.typed();r,a=self.f.finish()
        with self.assertRaisesRegex(P.Refusal,'duplicated'):self.check(r,a,self.f.edges+self.f.edges[:1])
    def governance_pair(self,cycle=False):
        original=json.loads((ROOT/'authority/artifact-types/governed-model/v1/fixtures/valid/record.json').read_text())
        for ident,other,direction in [('technical:A','technical:B','source'),('technical:B','technical:A','source' if cycle else 'target')]:
            value=json.loads(json.dumps(original));value['node_id']=ident;value['payload']['version_ref']=ident+'@technical.1';value['successor_refs']=[]
            value['relation_refs']=[{'relation_kind_ref':'relation.successor-of','direction':direction,'counterpart_kind':'governed-model','counterpart_ref':other}]
            self.f.node(ident.replace(':','-'),P.canonical(value),'cal.artifact-type.governed-model/v1')
        self.f.relation('relation.successor-of')
        self.f.edges=[{'source':'technical:A','dependency':'technical:B'}]+([{'source':'technical:B','dependency':'technical:A'}]if cycle else [])
    def test_real_original_role_pair_semantic_cycle_refused(self):
        self.governance_pair(True);r,a=self.f.finish()
        with self.assertRaisesRegex(P.Refusal,'cycle'):self.check(r,a)
    def test_actual_original_descriptor_direction_pair_positive(self):
        self.governance_pair();r,a=self.f.finish();self.assertEqual(self.check(r,a)['edges'],1)
    def test_duplicate_node_identity_refused(self):
        self.base();n=self.f.nodes[0];raw=self.f.payloads[n['file_id']]
        # Keep the first independently selected subject exact, so the refusal
        # reaches duplicate identity rather than an earlier provenance mismatch.
        self.f.add('duplicate','governed-record',raw);self.f.nodes.append(dict(n,file_id='duplicate'));r,a=self.f.finish()
        with self.assertRaisesRegex(P.Refusal,'duplicate semantic identity'):self.check(r,a)
    def test_semantic_record_misclassified_as_proof_refused(self):
        self.base();self.f.kinds['definition']='history-proof';r,a=self.f.finish()
        with self.assertRaises(P.Refusal):self.check(r,a)
    def test_original_declaration_omission_refused(self):
        self.base();r,a=self.f.finish(edit=lambda p:p['declarations'].pop())
        with self.assertRaisesRegex(P.Refusal,'declaration proof omitted'):self.check(r,a)
    def test_original_declaration_substitution_refused(self):
        self.base();r,a=self.f.finish(edit=lambda p:p['declarations'][0].update(pointer='/registered_types/0'))
        with self.assertRaises(P.Refusal):self.check(r,a)
    def test_disconnected_original_node_refused(self):
        self.base();r,a=self.f.finish()
        with self.assertRaisesRegex(P.Refusal,'disconnected'):G.verify_graph(r,'policy',[],[next(iter(self.f.current))],a)
