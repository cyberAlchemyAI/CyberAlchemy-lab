"""Owned copies of exactly selected original public carrier/schema fixtures."""
import bootstrap
from bootstrap import R as ROOT, S, E, checked
import copy, json, os, time
from pathlib import Path
from types import SimpleNamespace
from lab_contracts.codec import Refusal, sha
from lab_selectors.anchors import AnchoredReader, RootAnchor, identity, relative
from dependency_graph.reader import RoleReader, ReaderSelection, FixturePermission, ROLE_KINDS
from dependency_graph import semantic as G

P=SimpleNamespace(canonical=G.canonical,digest=sha,Refusal=Refusal)
HERE=S/'dependency_graph'
SOURCE_SELECTION=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T08/revision-0002/attempt-0006.selection.json'
SOURCE_SELECTION_SHA='85bceb67958f916b7b060bec216e2300549dd09f433dafbf43d6d7d6ba76c01f'
selected=json.loads(checked(SOURCE_SELECTION,SOURCE_SELECTION_SHA))
ORIGINALS={}
for row in selected['inputs']:
    if row['path'] in ORIGINALS and ORIGINALS[row['path']]!=row:raise ValueError('conflicting original input')
    ORIGINALS[row['path']]=row
READ_SET={}

def original_bytes(path):
    relative(path)
    if path not in ORIGINALS:raise ValueError('unselected original fixture input')
    row=ORIGINALS[path]
    raw=checked(ROOT/path,row['sha256'])
    if len(raw)!=row['size']:raise ValueError('original size drift')
    READ_SET[path]=copy.deepcopy(row)
    return raw

def final_original_guard():
    checked(SOURCE_SELECTION,SOURCE_SELECTION_SHA)
    for path,row in READ_SET.items():
        if len(checked(ROOT/path,row['sha256']))!=row['size']:raise ValueError('original drift')

class Fixture:
    def __init__(self,parent):
        self.root=parent;self.payloads={};self.kinds={};self.tables=[]
        self.add('source','source-manifest',P.canonical({'schema_version':'owned-source-fixture/v1','files':[]}))
        self.add('profile','contract-profile',P.canonical({'schema_version':'owned-profile-fixture/v1','files':[]}))
        self.source=self.binding('source');self.profile=self.binding('profile')
        self.cut={'branch_ref':'owned-fixture-branch','store_ref':'owned-fixture-store',
            'commit_sequence':1,'commit_sha256':sha(b'owned-fixture-cut'),
            'source_profile_sha256':self.profile['sha256'],'streams':[]}

    def add(self,file_id,role,raw):
        relative(file_id)
        if '/' in file_id or role not in ROLE_KINDS or type(raw) is not bytes:raise ValueError('fixture file')
        self.payloads[file_id]=raw;self.kinds[file_id]=role
        (self.root/file_id).write_bytes(raw)

    def binding(self,file_id):
        role=self.kinds[file_id]
        kind='protected-input' if role=='governed-record' else ROLE_KINDS[role][0]
        raw=self.payloads[file_id]
        return {'kind':kind,'root_id':'fixture','relative_path':file_id,'sha256':sha(raw),'size_bytes':len(raw)}

    def reader(self):
        rows=[{'file_id':name,'binding':self.binding(name),'logical_path':'technical:owned/'+name,
               'kind':self.kinds[name]} for name in sorted(self.payloads)]
        policy={'schema_version':'lab-original-role-selection/v1','source_binding':self.source,
            'profile_binding':self.profile,'source_cut':self.cut,'files':rows,
            'table_descriptors':[],'authority_effect':'none'}
        raw=P.canonical(policy);path=self.root/'_role-control';path.write_bytes(raw)
        policy_binding={'kind':'execution','root_id':'fixture','relative_path':path.name,'sha256':sha(raw),'size_bytes':len(raw)}
        grant={'schema_version':'lab-fixture-reader-permission/v1','posture':'owned-fixture',
            'subject':'owned-semantic-fixture','source_binding':self.source,'profile_binding':self.profile,
            'source_cut':self.cut,'allowed_bindings':[r['binding'] for r in rows if r['binding']['kind']=='protected-input'],
            'not_before_ns':0,'expires_ns':time.time_ns()+180_000_000_000,'authority_effect':'none'}
        raw=P.canonical(grant);path=self.root/'_grant-control';path.write_bytes(raw)
        grant_binding={'kind':'evidence','root_id':'fixture','relative_path':path.name,'sha256':sha(raw),'size_bytes':len(raw)}
        anchor=RootAnchor('fixture',str(self.root),identity(os.stat(self.root)))
        class OwnedProvider:
            def read(self,binding,*,max_bytes):
                selected={**binding,'kind':'public-package'}
                return AnchoredReader([anchor],[selected]).read(selected,max_bytes)
        selected_reader=AnchoredReader([anchor],[r['binding'] for r in rows]+[policy_binding,grant_binding],protected_provider=OwnedProvider())
        selection=ReaderSelection(policy_binding,self.source,self.profile,self.cut,[])
        return RoleReader(selected_reader,selection,posture='owned-fixture',
            permission=FixturePermission(selected_reader,grant_binding,'owned-semantic-fixture'))

REGISTRY='authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json'
CATALOG='product/lab/release-candidates/v1/interface/api-integration-v16/catalog-representations.json'
KERNEL='product/lab/release-candidates/v1/interface/custody-correction-v4/runtime/lab_runtime/'
RELATIONS='authority/admissions/governance-transaction-surface/v1/registries/relation-kind-registry.json'
import posixpath

class VariedFixture(Fixture):

    def __init__(self, parent):
        super().__init__(parent)
        self.registry = json.loads(original_bytes(REGISTRY).decode())
        self.catalog = json.loads(original_bytes(CATALOG).decode())
        self.add('registry', 'history-proof', original_bytes(REGISTRY))
        self.add('catalog', 'history-proof', original_bytes(CATALOG))
        self.add('kernel-identity', 'host-dependency', original_bytes(KERNEL + 'common.py'))
        self.add('kernel-operations', 'host-dependency', original_bytes(KERNEL + 'operations.py'))
        self.add('relation-registry', 'history-proof', original_bytes(RELATIONS))
        self.schema_rows = []
        self.profiles = []
        self.nodes = []
        self.declarations = []
        self.relations = []
        self.contexts = set()
        self.subjects = {}
        self.current = {}
        self.edges = []
        self.originals = []

    def document(self, path):
        path = posixpath.normpath(path); relative(path)
        if path in {r['path'] for r in self.schema_rows}:
            return
        identity = 'schema-' + str(len(self.schema_rows))
        self.add(identity, 'governed-schema', original_bytes(path))
        self.schema_rows.append({'path': path, 'file_id': identity})

        def walk(value):
            if type(value) is dict:
                ref = value.get('$ref', '')
                if ref and (not ref.startswith('#')):
                    self.document((Path(path).parent / ref.split('#')[0]).as_posix())
                for child in value.values():
                    walk(child)
            elif type(value) is list:
                for child in value:
                    walk(child)
        walk(json.loads(original_bytes(path).decode()))

    def carrier(self, ref, registered=False):
        pid = ref + (':registered' if registered else ':instance')
        if any((p['profile_id'] == pid for p in self.profiles)):
            return pid
        index, c = next(((i, c) for i, c in enumerate(self.registry['admitted_contracts']) if c['artifact_type_ref'] == ref))
        row = next((r for r in self.catalog['rows'] if r['represented_contract_ref'] == ref))
        did = 'descriptor-' + str(len(self.profiles))
        self.add(did, 'governed-descriptor', original_bytes(c['artifact_path']))
        self.document(c['schema_path'])
        selector = '#/properties/registered_types/items' if registered else c['schema_selector']
        docs = G.Schemas(self.reader(), self.schema_rows)
        slots = docs.slots(c['schema_path'], selector)
        fields = [{'instance_pointer': key, 'schema_locations': [list(loc) for loc in locations], 'disposition': 'current-context'} for key, locations in slots.items()]
        for field in fields:
            key = field['instance_pointer']
            if key == '/successor_refs/*':
                field['disposition'] = 'semantic-node'
            if key == '/payload/version_ref':
                field['disposition'] = 'self-identity'
            if ref.endswith('typed-relation/v3') and key in ('/payload/source/ref', '/payload/source/version_ref', '/payload/target/ref', '/payload/target/version_ref'):
                field['disposition'] = 'semantic-node'
        self.profiles.append({'profile_id': pid, 'carrier_ref': ref, 'instance_schema_selector': selector, 'registry_pointer': '/admitted_contracts/' + str(index), 'descriptor_file_id': did, 'descriptor_pointer': row['selector'], 'fields': fields})
        return pid

    def original(self, file_id, path, carrier, category='artifact-instance', registered=False, body_pointer=None):
        raw = original_bytes(path)
        value = json.loads(raw)
        if body_pointer is not None:
            raw = P.canonical(G.pointer(value, body_pointer))
        self.originals.append({'path': path, 'sha256': P.digest(original_bytes(path)), 'body_pointer': body_pointer, 'selected_body_sha256': P.digest(raw)})
        return self.node(file_id, raw, carrier, category, registered)

    def node(self, file_id, raw, carrier, category='artifact-instance', registered=False):
        pid = self.carrier(carrier, registered)
        p = next((p for p in self.profiles if p['profile_id'] == pid))
        c = G.pointer(self.registry, p['registry_pointer'])
        d = G.pointer(json.loads(self.payloads[p['descriptor_file_id']]), p['descriptor_pointer'])
        record = json.loads(raw)
        field = d.get('instance_contract', {}).get('identity_field')
        if registered:
            ident = record['artifact_type_ref'].rsplit('/', 1)[0]
            version = record['artifact_type_ref']
        elif field:
            ident = record[field]
            version = ident + '@T08-owned-technical.1'
        else:
            ident = next((record[k] for k in ('definition_id', 'artifact_type_ref', 'node_id', 'record_id', 'migration_manifest_id', 'product_id', 'project_id') if k in record))
            version = ident + '@T08-owned-technical.1'
        self.add(file_id, 'governed-record', raw)
        self.nodes.append({'file_id': file_id, 'profile_id': pid, 'version_ref': version, 'category': category})
        self.subjects[version] = {'identity': ident, 'version_ref': version, 'category': category, 'kind': c['semantic_kind'], 'effective_state': 'candidate-current', 'carrier_ref': carrier, 'source': {'path': 'technical:owned/' + file_id, 'sha256': P.digest(raw)}}
        self.current[ident] = version
        for f in p['fields']:
            for v in G.values(record, f['instance_pointer']):
                if type(v) is str and f['disposition'] == 'current-context':
                    self.contexts.add(v)
                elif type(v) is str and f['disposition'] == 'semantic-node':
                    self.edges.append({'source': ident, 'dependency': v})
        return (ident, version)

    def all_embedded_declarations(self):
        self.document('authority/artifact-types/artifact-type/v1/schema.json')
        did = 'foundation-declarations'
        self.add(did, 'governed-descriptor', original_bytes('authority/artifact-types/artifact-type/v1/artifact.json'))
        for row in self.catalog['rows']:
            if row['representation_kind'] == 'embedded-contract-declaration':
                self.declarations.append({'file_id': did, 'pointer': row['selector'], 'schema_path': 'authority/artifact-types/artifact-type/v1/schema.json', 'schema_selector': '#/properties/registered_types/items'})

    def relation(self, ref):
        reg = json.loads(original_bytes(RELATIONS).decode())
        i, r = next(((i, r) for i, r in enumerate(reg['entries']) if r['relation_kind_ref'] == ref))
        rid = 'relation-' + str(len(self.relations))
        self.add(rid, 'governed-descriptor', original_bytes(r['instance_path']))
        qc = json.loads(self.payloads[rid])['payload']['qualifier_contract']
        docs = G.Schemas(self.reader(), self.schema_rows)
        qschema = {'type': 'object', 'additionalProperties': False, 'required': qc['required_axes'], 'properties': qc['properties']}
        slots = docs.slots(r['instance_path'], '#/payload/qualifier_contract', qschema)
        qfields = [{'instance_pointer': key, 'schema_locations': [list(loc) for loc in locations], 'disposition': 'semantic-node' if key == '/definition_version_ref' else 'current-context'} for key, locations in slots.items()]
        self.relations.append({'file_id': rid, 'registry_file_id': 'relation-registry', 'registry_pointer': '/entries/' + str(i), 'qualifier_fields': qfields})

    def finish(self, edit=None, eligibility_edit=None):
        if not self.declarations:
            self.all_embedded_declarations()
        eligibility = {'schema_version': 'lab-native-subject-selection/v1-candidate', 'source_binding': self.source, 'profile_binding': self.profile, 'source_cut': self.cut, 'current_by_identity': self.current, 'subjects': self.subjects, 'authority_effect': 'none'}
        if eligibility_edit:
            eligibility_edit(eligibility)
        self.add('eligibility', 'history-proof', P.canonical(eligibility))
        policy = {'schema_version': 'lab-schema-declared-semantic-graph/v2-candidate', 'registry_file_id': 'registry', 'catalog_file_id': 'catalog', 'kernel_identity_file_id': 'kernel-identity', 'kernel_operations_file_id': 'kernel-operations', 'schemas': self.schema_rows, 'profiles': self.profiles, 'declarations': self.declarations, 'nodes': self.nodes, 'eligibility_file_id': 'eligibility', 'proof_references': [], 'context_references': sorted(self.contexts), 'relation_contracts': self.relations, 'authority_effect': 'none'}
        if edit:
            edit(policy)
        self.add('policy', 'semantic-policy', P.canonical(policy))
        reader = self.reader()
        anchor = G.GraphAnchor(self.binding('policy'), self.binding('eligibility'), self.source, self.profile, self.cut, ('candidate-current',))
        return (reader, anchor)
