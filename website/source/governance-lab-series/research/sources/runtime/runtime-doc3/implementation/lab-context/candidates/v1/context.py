"""Schema-valid candidate views composed with the existing ephemeral Session."""
from __future__ import annotations
import base64
import copy
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
import importlib.metadata
from pathlib import Path
import platform
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[3]
RUNTIME = ROOT/'implementation/lab-runtime/candidates/repeatable-operation'
if str(RUNTIME) not in sys.path: sys.path.insert(0, str(RUNTIME))
from jsonschema import Draft202012Validator
from lab_runtime.common import byte_digest, digest, encoded, load, loads, pointer, require, under
from lab_runtime.session import Session, reference
from native_reader import NativeReadStore, regular

IMPLEMENTATION_ID = 'implementation:lab-exact-context-generator'
IMPLEMENTATION_VERSION = IMPLEMENTATION_ID+'@candidate.2'
CARRIERS = {k: 'cal.artifact-type.'+k+'/v1' for k in ['context-request', 'context-view', 'ontology', 'ontology-cut', 'ontology-view', 'implementation']}
CARRIERS['typed-relation'] = 'cal.artifact-type.typed-relation/v3'


def environment():
    return {'reference_class':'protocol-environment-contract', 'authority_effect':'none',
            'python':platform.python_version(), 'packages':{k:importlib.metadata.version(k) for k in ['jsonschema','cryptography','referencing']},
            'action_permission':'none'}


@dataclass(frozen=True)
class GeneratorPins:
    manifest_sha256: str
    implementation_version_ref: str


def verify_generator(manifest_path, pins):
    require(isinstance(pins, GeneratorPins), 'independent context generator pins required')
    raw = regular(manifest_path)
    require(byte_digest(raw) == pins.manifest_sha256, 'generator manifest pin mismatch')
    m = loads(raw)
    require(set(m) == {'schema_version','authority_effect','package_version','implementation_version_ref','files','native_executable_sha256','environment','implementation_record','realization_record','source_profile_sha256','source_snapshot_digest'}, 'generator manifest must be closed')
    require(m['schema_version'] == 'lab-context-generator-manifest/v1-candidate' and m['authority_effect'] == 'none', 'generator manifest authority mismatch')
    require(m['implementation_version_ref'] == pins.implementation_version_ref == IMPLEMENTATION_VERSION, 'generator Implementation revision mismatch')
    require(m['environment'] == environment(), 'context generator environment changed')
    expected = set()
    for row in m['files']:
        require(set(row) == {'path','sha256'}, 'generator source binding must be closed')
        require(row['path'] not in expected, 'duplicate generator file')
        expected.add(row['path'])
        file = under(ROOT, row['path'])
        require(byte_digest(regular(file)) == row['sha256'], 'context generator source changed: '+row['path'])
    actual = {p.relative_to(ROOT).as_posix() for p in [PACKAGE/'context.py', PACKAGE/'native_reader.py', PACKAGE/'native/Cargo.toml',PACKAGE/'native/Cargo.lock',PACKAGE/'native/src/main.rs', ROOT/'ontology-lifecycle/runtime/Cargo.toml',ROOT/'ontology-lifecycle/runtime/Cargo.lock',ROOT/'ontology-lifecycle/runtime/src/lib.rs']}
    actual |= {p.relative_to(ROOT).as_posix() for p in (RUNTIME/'lab_runtime').rglob('*.py')}
    require(expected == actual, 'generator executable dependency closure changed')
    for key in ['implementation_record','realization_record']:
        row=m[key]
        require(set(row)=={'path','sha256'},'generator artifact binding must be closed')
        file=under(ROOT,row['path'])
        require(file.is_relative_to(PACKAGE/'packages'), 'generator artifact outside selected staging scope')
        require(byte_digest(regular(file))==row['sha256'],'frozen generator artifact changed')
    return m


@lru_cache(maxsize=12)
def compiled_schema(raw):
    schema = loads(raw)
    def closed_refs(value):
        if isinstance(value, dict):
            require('$ref' not in value and '$dynamicRef' not in value, 'context carrier schema requires explicit reference closure')
            for item in value.values(): closed_refs(item)
        elif isinstance(value, list):
            for item in value: closed_refs(item)
    closed_refs(schema)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def validate(record, kind, snapshot):
    contract = snapshot['contracts'][CARRIERS[kind]]
    require(contract['lifecycle_state'] == 'admitted-current', 'selected carrier is not current')
    require(contract['schema_selector'] is None, 'explicit carrier selector not implemented')
    raw = base64.b64decode(snapshot['byte_contents'][contract['schema_path']], validate=True)
    require(byte_digest(raw) == contract['schema_sha256'], 'context carrier schema byte mismatch')
    errors = list(compiled_schema(raw).iter_errors(record))
    require(not errors, 'candidate '+kind+' carrier invalid: '+(errors[0].message if errors else ''))
    return {'carrier_ref':CARRIERS[kind], 'schema_sha256':contract['schema_sha256'], 'artifact_sha256':contract['artifact_sha256']}


def required_reference(subjects, ref, kind):
    row = reference(subjects, ref, kind)
    require(row['governed_claim'] and row['effective_state'] in ['admitted-current','local-admitted-current'], 'required current '+kind+' reference unresolved: '+ref)
    return row


def generator_records(snapshot, manifest, owner, scope, capability):
    """Deterministic package-owned artifacts, independent from Session identity."""
    route='protocol:repository-owner-review:R08'
    evidence='protocol:context-generator:source-closure:'+digest({'files':manifest['files'],'native_executable_sha256':manifest['native_executable_sha256'],'environment':manifest['environment']})
    common={'authority_effect':'none','owner_ref':owner['version_ref'],'scope_ref':scope['version_ref'],'claim_ceiling':'Exact candidate generator realization proposal; no admission, conformance, usefulness, activation or action grant.','challenge_route':route}
    impl={**common,'schema_version':'cyberalchemy-lab-implementation/v1','node_id':IMPLEMENTATION_ID,'kind':'implementation','name':'Exact context generator','lifecycle_state':'candidate','evidence_refs':[evidence],'successor_refs':[],'relation_refs':[{'relation_kind_ref':'relation.realizes','direction':'source','counterpart_kind':'product-capability','counterpart_ref':capability['version_ref']}],'payload':{'implementation_kind':'candidate-context-generator','conforms_to_schema_refs':[snapshot['contracts'][CARRIERS[k]]['artifact']['schema_ref'] for k in ['context-request','context-view','ontology','ontology-cut','ontology-view']],'realizes_capability_refs':[capability['version_ref']],'execution_entrypoint_ref':(PACKAGE/'context.py').relative_to(ROOT).as_posix()+'#ContextSession','environment_contract_ref':'protocol:context-generator:environment:'+digest(manifest['environment'])}}
    relation={**common,'schema_version':'cyberalchemy-lab-typed-relation/v3','node_id':'typed-relation:context-generator-realizes-capability','kind':'typed-relation','name':'Candidate context generator realization','lifecycle_state':'candidate','evidence_refs':[evidence],'successor_refs':[],'relation_refs':[], 'payload':{'relation_kind_ref':'relation.realizes','source':{'ref':IMPLEMENTATION_ID,'version_ref':IMPLEMENTATION_VERSION,'kind':'implementation'},'target':{'ref':capability['identity_ref'],'version_ref':capability['version_ref'],'kind':'product-capability'},'qualifiers':{'realization_role':'candidate-exact-context-generation','exact_target_version_ref':capability['version_ref']},'relation_lifecycle_state':'candidate','relation_evidence_refs':[evidence]}}
    return impl,relation


class ContextSession:
    """A read consumer, with candidate carriers and session-owned short memory."""
    def __init__(self, store, source_snapshot, native_store, *, generator_manifest,
                 generator_pins, owner_ref, context_ref, scope_ref, capability_ref,
                 max_items=32, max_bytes=1048576, **session_options):
        require(isinstance(native_store, NativeReadStore), 'verified native ontology read adapter required')
        require(type(max_items) is int and 1 <= max_items <= 100 and type(max_bytes) is int and 1 <= max_bytes <= 8*1024*1024, 'context request budget exceeded')
        self.closed = False; self.core = None; self._pack = None
        self.native_store = native_store
        self.manifest_path = Path(generator_manifest); self.generator_pins = generator_pins
        self.snapshot = copy.deepcopy(source_snapshot)
        try:
            manifest = verify_generator(self.manifest_path, generator_pins)
            require(manifest['source_profile_sha256']==self.snapshot['source_profile_sha256'] and manifest['source_snapshot_digest']==self.snapshot['snapshot_digest'],'generator selected source cut mismatch')
            require(manifest['native_executable_sha256'] == native_store.pins.executable_sha256, 'native reader differs from generator package')
            native = native_store.read()
            self.core = Session(store, source_snapshot, **session_options)
            base = self.core.context(); data = store.replay(require_current=True); subjects = data['projection']['subjects']
            owner = required_reference(subjects, owner_ref, 'principal')
            context = required_reference(subjects, context_ref, 'context')
            scope = required_reference(subjects, scope_ref, 'project')
            capability = required_reference(subjects, capability_ref, 'product-capability')
            resolved = base['context_view']['selected_governed_references'] + [owner,context,scope,capability]
            resolved = list({r['version_ref']:r for r in resolved}.values())
            materials = [{'source_ref':r['source_binding']['path'], 'selector':'#', 'sha256':r['source_binding']['sha256']} for r in resolved]
            require(len(materials) <= max_items, 'context selection exceeds item budget')
            for row in materials: require(self.snapshot['materials'].get(row['source_ref']) == row['sha256'], 'selected reference original bytes unavailable')
            generated = datetime.fromisoformat(base['generated_at']).astimezone(timezone.utc)
            stamp = generated.strftime('%Y-%m-%dT%H:%M:%SZ')
            expiry = datetime.fromtimestamp(generated.timestamp()+base['ttl_seconds'], timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            suffix = base['session_id'].split(':')[-1]
            # Native event identities are separate from domain Artifact identities.
            identities = [s['identity'] for s in native['cut']['subjects']]
            ids = {i['ontology_id'] for i in identities}
            require(len(ids) == 1, 'native cut must select one ontology identity')
            ontology_id = 'ontology:native-context:'+next(iter(ids))
            nodes = sorted(i['subject_id'] for i in identities if i['subject_kind'] == 'node')
            edges = sorted(i['subject_id'] for i in identities if i['subject_kind'] == 'relation')
            require(nodes and edges, 'candidate context ontology needs explicit node and relation closure')
            selected_nodes = native['context']['selected_node_ids']; selected_edges = native['context']['selected_relation_ids']
            require(len(selected_nodes)+len(selected_edges) <= max_items, 'native selection exceeds item budget')
            cut_id = 'ontology-cut:'+suffix; view_id = 'ontology-view:'+suffix; request_id = 'context-request:'+suffix; context_id = 'context-view:'+suffix
            join_ref = 'protocol:ontology-native:require-exact:pinned-governance-prefix'
            environment_ref = 'protocol:context-generator:environment:'+digest(manifest['environment'])
            evidence_ref = 'protocol:context-generator:manifest:'+generator_pins.manifest_sha256
            route = 'protocol:repository-owner-review:R08'
            ceiling = 'Exact candidate read projection only; no admission, actor permission, action authority or durable Session memory.'
            common = {'authority_effect':'none','owner_ref':owner['version_ref'], 'scope_ref':scope['version_ref'],'claim_ceiling':ceiling,'challenge_route':route}
            ontology = {**common,'node_id':ontology_id,'kind':'ontology','status':'candidate-unadmitted','name':'Native context ontology', 'ontology_version':'1.0.0-candidate.1','purpose':'Bounded native event read context, separate from Project histories and Artifact instances.', 'boundaries':['Actual ontology-lifecycle closed empty-property profile; domain mappings remain O02.'], 'node_refs':nodes,'relation_refs':edges,'branch_refs':[], 'role_assignment_refs':[],'provenance_refs':[evidence_ref], 'confidence_policy_ref':'protocol:native-context:verification-only','promotion_state':'review','governance_rules':['Canonical replay inputs are pinned native event bytes.','Require exact semantic/governance event joins.','Projection has no admission authority.'], 'owner_route':route,'successor_refs':[]}
            wrapper = lambda kind, identity, payload: {**common, 'schema_version':'cyberalchemy-lab-'+kind+'/v1', 'node_id':identity,'kind':kind,'name':'Candidate '+kind,'record_state':'candidate','evidence_refs':[evidence_ref],'successor_refs':[],'payload':payload}
            cut_digest = digest(native['cut'])
            cut = wrapper('ontology-cut',cut_id,{'ontology_ref':ontology_id,'semantic_cursor':native['cut']['semantic_cursor'],'source_event_set_digest':native['cut']['source_event_set_digest'],'calculated_digest':cut_digest,'governance_join_policy_ref':join_ref,'node_refs':nodes,'edge_refs':edges,'integrity_result':'pass','replay_source':False})
            ov = wrapper('ontology-view',view_id,{'ontology_ref':ontology_id,'cut_ref':cut_id,'cut_digest':cut_digest,'selector_ref':request_id,'consumer_ref':base['session_id'],'intended_use':self.native_store.request['selector']['intended_use'],'selected_node_refs':selected_nodes,'selected_edge_refs':selected_edges,'exclusions':sorted(set(nodes+edges)-set(selected_nodes+selected_edges)),'freshness_at':stamp,'expires_at':expiry,'source_event_set_digest':native['context']['source_event_set_digest'],'semantic_cursor':native['cut']['semantic_cursor'],'governance_join_policy_ref':join_ref,'replay_source':False})
            request = {**common,'kind':'context-request','node_id':request_id,'status':'candidate-unadmitted','context_ref':context['identity_ref'],'context_version_ref':context['version_ref'],'consumer_refs':[base['session_id']],'intended_uses':['Read verified Project State and native ontology context'],'selectors':[r['version_ref'] for r in resolved],'freshness_requirement':'Recheck exact source, HEAD, configuration, code and native event bytes before every consumption.','exclusions':['Session short memory','Unselected repository material','Action permission'],'output_constraints':['candidate-unadmitted','bounded read-only'],'budget':{'max_items':max_items,'max_bytes':max_bytes},'requested_at':stamp,'owner_route':route}
            cv = {**common,'kind':'context-view','node_id':context_id,'status':'candidate-unadmitted','request_ref':request_id,'context_ref':context['identity_ref'],'context_version_ref':context['version_ref'],'source_epoch':self.snapshot['snapshot_digest'],'generated_at':stamp,'expires_at':expiry,'included_material':materials,'excluded_material':[{'source_ref':'protocol:session-short-memory','reason':'Private to this ephemeral Session; excluded from every projection.'}],'lineage_refs':[r['version_ref'] for r in resolved]+[view_id,IMPLEMENTATION_VERSION],'limitations':['Candidate carriers have no admission effect.','Native ontology uses the current empty-property profile; no domain mapping is inferred.','Session, environment, policies and routes are explicitly protocol references.'],'selection_basis':'Exact current Context revision, source profile, verified Project State, native cut and bounded request.','owner_route':route}
            expected_impl,expected_relation=generator_records(self.snapshot,manifest,owner,scope,capability)
            impl=load(under(ROOT,manifest['implementation_record']['path']))
            relation=load(under(ROOT,manifest['realization_record']['path']))
            require(impl==expected_impl and relation==expected_relation,'generator artifact revision does not match selected owner, scope, capability and code')
            rc = self.snapshot['relation_contracts']['relation.realizes']['payload']
            require({'source_kind':'implementation','target_kind':'product-capability'} in rc['allowed_endpoint_pairs'], 'generator realization ordered pair undeclared')
            require(Draft202012Validator(rc['qualifier_contract']).is_valid(relation['payload']['qualifiers']), 'generator realization qualifier invalid')
            artifacts = {'ontology':ontology,'ontology-cut':cut,'ontology-view':ov,'context-request':request,'context-view':cv,'implementation':impl,'typed-relation':relation}
            contracts = {k:validate(v,k,self.snapshot) for k,v in artifacts.items()}
            coeval = [{'reference':v['node_id'], 'version_ref':IMPLEMENTATION_VERSION if k=='implementation' else v['node_id']+('@candidate.2' if k=='typed-relation' else '@candidate.1'),'reference_class':'candidate-carrier','governed_claim':False,'authority_effect':'none','carrier_ref':CARRIERS[k],'record_digest':digest(v)} for k,v in artifacts.items()]
            schema_references = [{'reference':self.snapshot['contracts'][CARRIERS[k]]['artifact']['schema_ref'],'reference_class':'bound-schema-label','governed_claim':False,'reason':'Exact schema bytes bound through the carrier; no standalone Schema artifact is claimed.','schema_sha256':contracts[k]['schema_sha256']} for k in artifacts]
            native_references = [{'reference':s['identity']['subject_id'],'reference_class':'verified-native-subject','governed_claim':False,'identity':s['identity'],'semantic_event_digest':s['source_event_digest'],'source_cursor':s['source_cursor']} for s in native['cut']['subjects']]
            protocols = schema_references + copy.deepcopy(base['protocol_references'])+[{'reference':r,'reference_class':'protocol-reference','governed_claim':False} for r in [join_ref,environment_ref,evidence_ref,route,'protocol:native-context:verification-only','protocol:session-short-memory',impl['payload']['execution_entrypoint_ref'],*impl['evidence_refs']]]
            diagnostics = [r for r in base['reference_diagnostics'] if r['reference'] not in ['ontology-native-cut','generator-implementation-realization']]
            self._pack = {**base,'schema_version':'lab-exact-session-context/v1-candidate','context_view':cv,'ontology_view':ov,'ontology_cut':cut,'context_request':request,'candidate_artifacts':artifacts,'carrier_bindings':contracts,'resolved_references':resolved,'candidate_references':coeval,'protocol_references':protocols,'reference_diagnostics':diagnostics,'native_ontology':native,'native_references':native_references,'native_input_pins':dict(vars(native_store.pins)),'generator_provenance':{'implementation_version_ref':IMPLEMENTATION_VERSION,'implementation_record_digest':digest(impl),'implementation_posture':'candidate-unadmitted','package_version':manifest['package_version'],'manifest_sha256':generator_pins.manifest_sha256,'native_executable_sha256':manifest['native_executable_sha256'],'authority_effect':'none'},'claim_ceiling':ceiling}
            self._pack.pop('pack_digest',None)
            require(len(encoded(self._pack)) <= max_bytes, 'context pack exceeds byte budget')
            self._pack['pack_digest'] = digest(self._pack)
            require(len(encoded(self._pack)) <= max_bytes, 'context pack exceeds byte budget')
            self.context()
        except BaseException:
            self.close(); raise

    @property
    def session_id(self): return self.core.session_id

    @property
    def instance_id(self): return self.core.instance_id

    def context(self):
        require(not self.closed, 'session is closed')
        try:
            verify_generator(self.manifest_path, self.generator_pins)
            self.core.context()
            require(self.native_store.read() == self._pack['native_ontology'], 'native projection changed')
            return copy.deepcopy(self._pack)
        except BaseException:
            self.close(); raise

    def note(self, text):
        self.context()
        return self.core.note(text)

    def close(self):
        result = self.core.close() if self.core is not None else {'termination_state':'closed','short_memory_erased':True,'durable_effect':'none'}
        self._pack = None; self.snapshot = None; self.closed = True
        return result
