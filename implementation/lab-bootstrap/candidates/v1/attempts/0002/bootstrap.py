"""Candidate catalog composition and isolated signed genesis rehearsal.

This format is separate from a frozen legacy Store, Project State, ontology
history and repository admission. Every new member stays candidate-unadmitted.
External pins and a fixture policy are required; self-description grants nothing.
"""
from __future__ import annotations
import base64
import copy
import fcntl
from functools import lru_cache
import importlib.metadata
import os
import re
import stat
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from jsonschema import Draft202012Validator

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[3]
RUNTIME = ROOT / 'implementation/lab-runtime/candidates/repeatable-operation'
sys.path.insert(0, str(RUNTIME))
from lab_runtime.common import RuntimeFault, byte_digest, digest, encoded, load, loads, pointer, require, under
from lab_runtime.profiles import select
from lab_runtime.sources import capture, freshness, validate_schema, verify_snapshot
from lab_runtime.transition import _publish
from generator import method_markdown

METHOD_TYPE = 'cal.artifact-type.method/v1'
METHOD_DEFINITION = 'CAV2-D32@1.0.0-candidate.1'
CATALOG_FIELDS = ['schema_version', 'authority_effect', 'source', 'generator', 'contracts', 'source_subjects',
                  'candidate_subjects', 'relation_contracts', 'endpoint_mappings', 'remaining_review_members', 'digest']
INPUT_FIELDS = ['schema_version', 'authority_effect', 'baseline_profile_sha256', 'baseline_snapshot_digest',
                'identity_bindings_sha256', 'generator_manifest_sha256', 'endpoint_mappings', 'targets', 'type_mechanics']


def closed(value, keys):
    require(isinstance(value, dict) and set(value) == set(keys), 'unclosed candidate envelope')


def public(raw):
    value = loads(raw)
    def visit(v):
        if isinstance(v, dict):
            require(not set(v) & {'private_key', 'short_memory', 'session_notes', 'approval_token'}, 'private/session material forbidden')
            for x in v.values(): visit(x)
        elif isinstance(v, list):
            for x in v: visit(x)
        elif isinstance(v, str):
            require('PRIVATE KEY' not in v and '.local/' not in v and '.env' not in Path(v).parts, 'private material forbidden')
    visit(value)
    return value


def file_bytes(path):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, 'rb') as h:
        require(stat.S_ISREG(os.fstat(h.fileno()).st_mode), 'regular original bytes required')
        return h.read()


def time_value(value):
    t = datetime.fromisoformat(value.replace('Z', '+00:00'))
    require(t.tzinfo is not None, 'timezone required')
    return t.astimezone(timezone.utc)


def executable_manifest(repo=ROOT):
    paths = [p for p in (RUNTIME / 'lab_runtime').rglob('*.py') if '__pycache__' not in p.parts]
    paths += [RUNTIME / 'lab.py', PACKAGE / 'bootstrap.py', PACKAGE / 'generator.py']
    return {'schema_version': 'lab-executable-manifest/v1-candidate', 'authority_effect': 'none',
            'files': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': byte_digest(file_bytes(p)),
                       'size_bytes': len(file_bytes(p))} for p in sorted(paths)]}


def environment_contract():
    return {'schema_version':'lab-candidate-generator-environment/v1','authority_effect':'none',
            'contract_ref':'candidate-contract:python-3:jsonschema-and-cryptography',
            'python_version':sys.version,'dependencies':{k:importlib.metadata.version(k) for k in ['jsonschema','cryptography']},
            'posture':'candidate-protocol-contract; no admitted Environment Contract or action authority'}


@lru_cache(maxsize=2)
def verify_baseline_derivation(raw):
    """Parsing memo for identical immutable source bytes, never Store replay.

Every caller still verifies snapshot bytes and external profile pins. A new byte
envelope always reconstructs metadata from the frozen capture provider.
"""
    baseline=loads(raw)
    selected=load(RUNTIME/'profiles/selections.json')['selections']
    d75=next(r for r in selected if r['name']=='d75')
    require(baseline['source_profile_sha256']==d75['profile_sha256'], 'S01 requires the independently bound D75 source profile')
    from lab_runtime._legacy import v2_sources
    with TemporaryDirectory(prefix='lab-source-derivation-') as tmp:
        root=Path(tmp)
        for path,body in baseline['byte_contents'].items():
            p=under(root,path);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(base64.b64decode(body,validate=True))
        result=v2_sources.capture(root,baseline['profile'])
        for field in ['subjects','contracts','relation_contracts','state','histories','profile','admission_as_of']:
            require(result[field]==baseline[field], 'baseline metadata is not derived from original source bytes: '+field)
        require(result['materials']==baseline['materials'], 'baseline source closure differs from frozen derivation')


def _definition(snapshot, version):
    require(version in snapshot['subjects'], 'semantic Definition outside exact source closure')
    row = snapshot['subjects'][version]
    require(row['category'] == 'definition' and row['effective_state'] == 'admitted-current', 'Definition is not current admitted source meaning')
    require(row['source']['sha256'] == snapshot['materials'][row['source']['path']], 'Definition original bytes mismatch')


def compose(materials):
    """Recompute catalog from captured exact input bytes; no registry mutation."""
    require(isinstance(materials, dict) and {'input.json', 'baseline.json', 'identities.json', 'generator-manifest.json'} <= set(materials), 'incomplete catalog inputs')
    inp = public(materials['input.json']); closed(inp, INPUT_FIELDS)
    require(inp['schema_version'] == 'lab-candidate-catalog-input/v1' and inp['authority_effect'] == 'none', 'unsupported catalog inputs')
    baseline = loads(materials['baseline.json'])
    verify_snapshot(baseline, expected_profile_sha256=inp['baseline_profile_sha256'])
    require(baseline['snapshot_digest'] == inp['baseline_snapshot_digest'], 'independent baseline cut mismatch')
    verify_baseline_derivation(materials['baseline.json'])
    require(byte_digest(materials['identities.json']) == inp['identity_bindings_sha256'], 'identity mapping pin mismatch')
    require(byte_digest(materials['generator-manifest.json']) == inp['generator_manifest_sha256'], 'generator binding mismatch')
    identities = loads(materials['identities.json'])
    require(materials.get('environment-contract.json') == encoded(environment_contract()), 'generator environment contract absent or different')
    exe = loads(materials['generator-manifest.json']); closed(exe, ['schema_version', 'authority_effect', 'files'])
    require(exe['schema_version'] == 'lab-executable-manifest/v1-candidate' and exe['authority_effect'] == 'none', 'generator manifest cannot grant authority')
    expected_exe = executable_manifest()
    require(exe == expected_exe, 'catalog does not bind the running composition/generator package')
    contracts = copy.deepcopy(baseline['contracts']); source_subjects = copy.deepcopy(baseline['subjects'])
    # All 143 inherited versions remain exact, including historical write exclusions.
    for ref, c in contracts.items():
        require(c['schema_path'] in baseline['materials'] and baseline['materials'][c['schema_path']] == c['schema_sha256'], 'inherited schema closure mismatch')
        require(c['artifact_path'] in baseline['materials'] and baseline['materials'][c['artifact_path']] == c['artifact_sha256'], 'inherited descriptor closure mismatch')
    mappings = inp['endpoint_mappings']
    require(isinstance(mappings, list) and len(mappings) == 2, 'exact Project/Product mappings required')
    expected = {
        'cal.artifact-type.project-identity/v1': ('project', '/project_id', ['purpose', 'coordination_scope']),
        'cal.artifact-type.product-identity/v2': ('product', '/product_id', ['purpose', 'value_promise', 'scope'])}
    require({r['carrier_ref'] for r in mappings} == set(expected), 'endpoint mapping set changed')
    for m in mappings:
        closed(m, ['carrier_ref', 'descriptor_sha256', 'schema_sha256', 'endpoint_kind', 'identity_selector', 'meaning_fields', 'posture', 'owner_ref', 'authority_effect'])
        c = contracts[m['carrier_ref']]; kind, selector, fields = expected[m['carrier_ref']]
        binding = [r for r in identities['carriers'] if r['carrier_ref'] == m['carrier_ref']]
        require(len(binding) == 1 and binding[0]['identity_selector'] == selector, 'exact endpoint identity selector mismatch')
        require(m['descriptor_sha256'] == c['artifact_sha256'] and m['schema_sha256'] == c['schema_sha256'] == binding[0]['schema_sha256'], 'endpoint contract pin mismatch')
        require((m['endpoint_kind'], m['identity_selector'], m['meaning_fields']) == (kind, selector, fields), 'endpoint meaning mapping changed')
        require(m['posture'] == 'candidate-semantic-review-required' and m['authority_effect'] == 'none' and m['owner_ref'] == 'role:definition-owner', 'endpoint mapping cannot claim semantic admission')
        for s in source_subjects.values():
            if s['carrier_ref'] == m['carrier_ref']:
                require(s['identity'] == pointer(s['record'], selector) and s['kind'] == kind, 'source endpoint representation disagrees')
                require(all(f in s['record'] for f in fields), 'source endpoint meaning fields missing')
    require(isinstance(inp['targets'], list) and 0 < len(inp['targets']) <= 1000, 'candidate target budget exceeded')
    targets = {}; docs = copy.deepcopy(baseline['documents'])
    for path, raw in materials.items():
        if path.endswith('.json') and path not in ['baseline.json', 'catalog.json']:
            docs[path] = loads(raw)
    mechanics = inp['type_mechanics']
    require(set(mechanics) == {METHOD_TYPE}, 'unexpected new type mechanics')
    require(materials.get('method/mechanics.json') == encoded(mechanics[METHOD_TYPE]), 'type mechanics sidecar drift')
    allowed = {'input.json','baseline.json','identities.json','generator-manifest.json','environment-contract.json',
               'method/mechanics.json','method/schema.json','catalog.json','bindings.json'}
    for t in inp['targets']:
        allowed.add(t['path'])
        if t['carrier_ref'] == METHOD_TYPE: allowed.add(t['path'].removesuffix('.json')+'.md')
    require(set(materials) <= allowed, 'unknown material outside declared semantic closure')
    # First install descriptors so coeval instances can be checked against exact contracts.
    for target in inp['targets']:
        closed(target, ['version_ref', 'identity_ref', 'identity_selector', 'category', 'carrier_ref', 'semantic_kind', 'path', 'sha256', 'predecessor_ref'])
        path = target['path']; under(Path('/catalog'), path)
        require(path in materials and byte_digest(materials[path]) == target['sha256'], 'target bytes outside exact catalog')
        record = public(materials[path]); version = target['version_ref']
        require(version not in targets and version not in source_subjects, 'duplicate/source candidate version')
        require(pointer(record, target['identity_selector']) == target['identity_ref'], 'candidate identity differs from exact selector')
        require(record.get('authority_effect') == 'none' or target['category'] == 'artifact-type', 'candidate record authority effect forbidden')
        if target['category'] == 'artifact-type':
            require(target['carrier_ref'] == 'cal.artifact-type.artifact-type/v3' and version == record['artifact_type_ref'] == METHOD_TYPE, 'unsupported raw descriptor carrier')
            meta = contracts[target['carrier_ref']]
            validate_schema(record, meta['schema_path'], '#/properties/registered_types/items', docs)
            require(version not in contracts, 'new type shadows an existing contract')
            _definition(baseline, METHOD_DEFINITION)
            require(record['semantic_definition_refs'] == [METHOD_DEFINITION] and record['semantic_kind'] == 'method', 'Method meaning collapsed')
            schema_path = record['schema_path']
            require(schema_path in materials and byte_digest(materials[schema_path]) == record['schema_sha256'], 'new Method schema closure missing')
            schema = docs[schema_path]; Draft202012Validator.check_schema(schema)
            require(schema.get('additionalProperties') is False and schema['properties']['semantic_definition_ref']['const'] == METHOD_DEFINITION, 'Method instance representation is not closed')
            mech = mechanics[version]
            closed(mech, ['schema_version', 'authority_effect', 'artifact_type_ref', 'owner_ref', 'identity_selector', 'version_selector', 'instance_discriminator', 'lifecycle', 'generator', 'validation', 'relation_surface', 'orthogonality', 'claim_ceiling'])
            require(mech['schema_version'] == 'lab-candidate-type-mechanics/v1' and mech['authority_effect'] == 'none' and mech['artifact_type_ref'] == version, 'type mechanics mismatch')
            require(mech['identity_selector'] == '/method_id' and mech['version_selector'] == '/version' and mech['instance_discriminator'] == {'path':'/schema_version','value':'cyberalchemy-lab-method/v1-candidate'}, 'Method identity/version contract mismatch')
            require(mech['lifecycle'] == {'initial':'candidate-unadmitted', 'revision':'exact predecessor and stable identity', 'admission':'separate R08 owner decision', 'activation':'separate action authorization'}, 'lifecycle collapses admission or activation')
            require(mech['owner_ref'] == 'role:artifact-type-owner' and mech['generator'] == {'path':(PACKAGE/'generator.py').relative_to(ROOT).as_posix(), 'sha256':byte_digest(file_bytes(PACKAGE/'generator.py')), 'mode':'generated-only'}, 'generator binding mismatch')
            require(mech['validation'] == {'schema':'closed exact instance schema','projection':'deterministic canonical-body roundtrip','semantics':'separate owner review'}, 'type validation conflates semantic review')
            require(mech['orthogonality'] == ['Definition meaning != Method instance','Method != Method Binding','Method != Workflow','Method admission != Method application'], 'Method orthogonality declarations missing')
            expected_surface = sorted(k for k, r in baseline['relation_contracts'].items() if any('method' in pair.values() for pair in r['payload']['allowed_endpoint_pairs']))
            require(mech['relation_surface'] == expected_surface, 'new Method relation surface changed')
            contracts[version] = {'artifact_type_ref':version, 'semantic_kind':'method', 'semantic_definition_refs':[METHOD_DEFINITION],
                'schema_path':schema_path, 'schema_sha256':record['schema_sha256'], 'schema_selector':None,
                'artifact_path':path, 'artifact_sha256':target['sha256'], 'instance_discriminator':mech['instance_discriminator'],
                'lifecycle_state':'candidate-unadmitted', 'admission_decision_ref':None, 'mechanics':mech, 'artifact':record}
        else:
            require(target['category'] in ['artifact-instance','typed-relation'], 'unsupported candidate category')
            require(version.startswith(target['identity_ref'] + '@'), 'candidate version does not retain stable identity')
            require(record.get('status',record.get('lifecycle_state')) in ['candidate-unadmitted','candidate'], 'new candidate body claims active or admitted posture')
        require(target['predecessor_ref'] is None, 'initial catalog cannot silently revise a source or candidate')
        targets[version] = {**copy.deepcopy(target), 'record':record, 'effective_state':'candidate-unadmitted', 'decision_ref':None}
    require(METHOD_TYPE in contracts and any(t['carrier_ref'] == METHOD_TYPE for t in targets.values()), 'Method descriptor and instance both required')
    current_ids = {s['identity'] for s in source_subjects.values() if s['effective_state'] == 'admitted-current'}
    new_ids = set()
    for version, t in targets.items():
        require(t['identity_ref'] not in current_ids and t['identity_ref'] not in new_ids, 'candidate identity collision')
        new_ids.add(t['identity_ref'])
        if t['category'] == 'artifact-type': continue
        require(t['carrier_ref'] in contracts, 'candidate carrier not in closure')
        c = contracts[t['carrier_ref']]
        require(c['lifecycle_state'] in ['admitted-current','candidate-unadmitted'], 'historical carrier cannot author a new instance')
        require(c['semantic_kind'] == t['semantic_kind'], 'candidate semantic kind mismatch')
        binding = [r for r in identities['carriers'] if r['carrier_ref'] == t['carrier_ref']]
        selector = '/method_id' if t['carrier_ref'] == METHOD_TYPE else binding[0]['identity_selector'] if len(binding) == 1 else None
        require(selector == t['identity_selector'], 'identity heuristic or carrier substitution forbidden')
        if c.get('instance_discriminator'):
            require(pointer(t['record'], c['instance_discriminator']['path']) == c['instance_discriminator']['value'], 'candidate discriminator mismatch')
        validate_schema(t['record'], c['schema_path'], c.get('schema_selector'), docs)
        if t['carrier_ref'] == METHOD_TYPE:
            require(version == t['identity_ref'] + '@' + t['record']['version'], 'Method version selector mismatch')
            projection_path = t['path'].removesuffix('.json') + '.md'
            require(materials.get(projection_path) == method_markdown(t['record']), 'Method projection drift')
        for r in t['record'].get('relation_refs', []):
            require(r['relation_kind_ref'] in baseline['relation_contracts'], 'embedded relation kind missing')
            counterparts=[s for s in source_subjects.values() if s['identity']==r['counterpart_ref'] and s['effective_state']=='admitted-current']
            counterparts += [s for s in targets.values() if s['identity_ref']==r['counterpart_ref']]
            require(len(counterparts)==1 and counterparts[0].get('kind',counterparts[0].get('semantic_kind'))==r['counterpart_kind'], 'unresolved embedded counterpart identity/kind')
            pair={'source_kind':t['semantic_kind'],'target_kind':r['counterpart_kind']}
            if r['direction']=='target':pair={'source_kind':pair['target_kind'],'target_kind':pair['source_kind']}
            require(pair in baseline['relation_contracts'][r['relation_kind_ref']]['payload']['allowed_endpoint_pairs'], 'undeclared embedded ordered pair')
        if t['category'] == 'typed-relation':
            p = t['record']['payload']; require(p['relation_kind_ref'] in baseline['relation_contracts'], 'new relation kind not declared')
            rc = baseline['relation_contracts'][p['relation_kind_ref']]['payload']
            require({'source_kind':p['source']['kind'],'target_kind':p['target']['kind']} in rc['allowed_endpoint_pairs'], 'undeclared ordered endpoint pair')
            for endpoint in [p['source'],p['target']]:
                require(endpoint['version_ref'] in targets or endpoint['version_ref'] in source_subjects, 'typed endpoint outside exact closure')
                s = targets.get(endpoint['version_ref'], source_subjects.get(endpoint['version_ref']))
                ident = s.get('identity_ref', s.get('identity')); kind = s.get('semantic_kind', s.get('kind'))
                require(endpoint['ref'] == ident and endpoint['kind'] == kind, 'typed endpoint identity/kind mismatch')
                require(s['effective_state'] in ['admitted-current','admitted-historical','candidate-unadmitted'], 'withdrawn endpoint cannot connect')
            qc = rc['qualifier_contract']
            Draft202012Validator({'type':'object','additionalProperties':False,'properties':qc['properties'],'required':qc['required_axes']}).validate(p['qualifiers'])
    generator_instances = [t for t in targets.values() if t['semantic_kind'] == 'implementation']
    require(len(generator_instances) == 1, 'one exact generator Implementation required')
    generator = generator_instances[0]
    require(generator['record']['payload']['execution_entrypoint_ref'] == (PACKAGE/'generator.py').relative_to(ROOT).as_posix(), 'generator Implementation aliases an unrelated executable')
    gp=generator['record']['payload']
    require(gp['environment_contract_ref']==environment_contract()['contract_ref'] and gp['conforms_to_schema_refs']==[docs['method/schema.json']['$id']], 'generator contract references unresolved')
    require(all(any(s['identity']==r and s['kind']=='product-capability' and s['effective_state']=='admitted-current' for s in source_subjects.values()) for r in gp['realizes_capability_refs']), 'generator capability reference unresolved')
    result = {'schema_version':'lab-candidate-catalog/v1','authority_effect':'none',
        'source':{'profile_sha256':inp['baseline_profile_sha256'],'snapshot_digest':baseline['snapshot_digest'],'admission_as_of':baseline['admission_as_of'], 'scope':'independently pinned D75 source cut; not latest repository authority'},
        'generator':{'implementation_ref':generator['version_ref'],'manifest_sha256':inp['generator_manifest_sha256'],'implementation_posture':'candidate-unadmitted'},
        'contracts':contracts,'source_subjects':source_subjects,'candidate_subjects':targets,
        'relation_contracts':copy.deepcopy(baseline['relation_contracts']),'endpoint_mappings':copy.deepcopy(mappings),
        'remaining_review_members':['Method carrier owner admission','Project/Product endpoint semantic review and noncollapse','generator Implementation owner admission','selected instance and connection owner admission']}
    result['digest'] = digest(result)
    return result


def package_materials(repo, selection):
    snap = capture(selection)
    require(snap['domain_posture'] == 'isolated-candidate', 'bootstrap requires an explicit isolated candidate profile')
    prefix = selection.policy['capture_config']['path'].rsplit('/',1)[0] + '/'
    materials = {p[len(prefix):]:base64.b64decode(snap['byte_contents'][p],validate=True) for p in snap['materials'] if p.startswith(prefix)}
    require('catalog.json' in materials, 'candidate catalog not captured')
    catalog = compose(materials)
    require(materials['catalog.json'] == encoded(catalog), 'catalog sidecar differs from independently reconstructed closure')
    # Native capture is a byte capture only. Its subject set must be precisely the new targets.
    require(set(snap['subjects']) == set(catalog['candidate_subjects']), 'native capture subject closure mismatch')
    for ref, t in catalog['candidate_subjects'].items():
        require(snap['subjects'][ref]['record'] == t['record'] and snap['subjects'][ref]['effective_state'] == 'candidate-unadmitted', 'native capture posture mismatch')
    return snap, catalog


@dataclass(frozen=True)
class RehearsalPolicy:
    actor_ref: str
    public_key: str
    branch_id: str
    destination: str
    scope_ref: str
    expires_at: str
    fixture_only: bool = True
    effect: str = 'initialize-or-transition-exact-isolated-catalog'

    def core(self):
        require(self.fixture_only is True and self.effect == 'initialize-or-transition-exact-isolated-catalog', 'rehearsal cannot authorize repository admission')
        require(all(isinstance(getattr(self,k),str) and getattr(self,k) for k in ['actor_ref','public_key','branch_id','destination','scope_ref','expires_at']), 'empty rehearsal policy')
        require(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:-]{0,127}', self.branch_id), 'invalid isolated branch identity')
        require(len(bytes.fromhex(self.public_key)) == 32, 'invalid fixture public key')
        require(str(Path(self.destination).resolve()) == self.destination and not Path(self.destination).is_relative_to(ROOT), 'rehearsal destination must be outside actual repository')
        time_value(self.expires_at)
        return asdict(self)


@dataclass(frozen=True)
class CatalogPins:
    branch_id: str
    head_sha256: str
    profile_sha256: str
    snapshot_digest: str
    catalog_digest: str
    policy_sha256: str


def verify_response(response, plan, policy):
    closed(plan,['schema_version','authority_effect','policy','effect','profile_sha256','snapshot_digest','catalog_digest','parent','selections',
                 'global_admissions','global_registry_changes','project_state_mutations','external_effects'])
    require(plan['schema_version']=='lab-isolated-catalog-plan/v1' and plan['authority_effect']=='none' and plan['policy']==policy.core()
            and plan['effect']==policy.effect and all(plan[k]==0 for k in ['global_admissions','global_registry_changes','project_state_mutations','external_effects']), 'rehearsal plan cannot claim repository effects')
    closed(response,['schema_version','plan_digest','policy_sha256','approved_at','fixture_only','human_outcome','signature'])
    require(response['schema_version']=='lab-isolated-rehearsal-response/v1' and response['plan_digest']==digest(plan)
            and response['policy_sha256']==digest(policy.core()) and response['fixture_only'] is True and response['human_outcome'] is None, 'response is not an exact fixture grant')
    require(time_value(response['approved_at']) < time_value(policy.expires_at), 'response outside policy interval')
    try:
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(policy.public_key)).verify(bytes.fromhex(response['signature']),encoded({k:v for k,v in response.items() if k!='signature'}))
    except (InvalidSignature,ValueError,TypeError) as exc:
        raise RuntimeFault('invalid rehearsal signature') from exc


def replay(path, pins, policy):
    require(isinstance(pins,CatalogPins) and isinstance(policy,RehearsalPolicy), 'independent pins and trusted fixture policy required')
    root = Path(path); require(root.is_dir() and not root.is_symlink(), 'isolated store root missing or linked')
    raw = {}
    for p in root.rglob('*'):
        require(not p.is_symlink(), 'isolated store symlink forbidden')
        if p.is_file(): raw[p.relative_to(root).as_posix()] = file_bytes(p)
    require('HEAD.json' in raw and byte_digest(raw['HEAD.json']) == pins.head_sha256, 'independent genesis HEAD pin mismatch')
    head = loads(raw['HEAD.json']); closed(head,['schema_version','authority_effect','branch_id','files'])
    require(head['schema_version'] == 'lab-isolated-catalog-head/v1' and head['authority_effect'] == 'none' and head['branch_id'] == pins.branch_id == policy.branch_id, 'genesis branch/policy mismatch')
    require(set(raw) == set(head['files']) | {'HEAD.json'}, 'isolated genesis file closure mismatch')
    require(all(byte_digest(raw[n]) == sha for n,sha in head['files'].items()), 'isolated genesis bytes changed')
    plan = loads(raw['plan.json']); response = loads(raw['rehearsal-response.json'])
    require(plan['policy'] == policy.core() and digest(plan['policy']) == pins.policy_sha256 and plan['effect'] == policy.effect and plan['authority_effect'] == 'none', 'independent rehearsal policy mismatch')
    verify_response(response,plan,policy)
    snapshot = loads(raw['snapshot.json']); verify_snapshot(snapshot, expected_profile_sha256=pins.profile_sha256)
    require(snapshot['snapshot_digest'] == pins.snapshot_digest == plan['snapshot_digest'], 'independent candidate capture mismatch')
    prefix = loads(base64.b64decode(snapshot['control_bytes']['policy']))['capture_config']['path'].rsplit('/',1)[0] + '/'
    materials = {p[len(prefix):]:base64.b64decode(snapshot['byte_contents'][p],validate=True) for p in snapshot['materials'] if p.startswith(prefix)}
    catalog = compose(materials)
    require(encoded(catalog) == raw['catalog.json'] == materials['catalog.json'] and catalog['digest'] == pins.catalog_digest == plan['catalog_digest'], 'genesis catalog is not the verified selected closure')
    require(plan['profile_sha256'] == pins.profile_sha256, 'plan selected a different profile')
    records = loads(raw['records.json'])
    expected_records = _records(catalog,plan)
    require(records == expected_records, 'genesis carry/exclusion records differ from reviewed plan')
    require(all(byte_digest(file_bytes(root/n)) == byte_digest(v) for n,v in raw.items()), 'genesis changed during replay')
    return {'catalog':catalog,'records':records,'plan':plan,'snapshot':snapshot,'head':head,
            'authority_effect':'none','cold_replay':True,'actual_owner_outcome':None}


def _records(catalog, plan):
    candidates = catalog['candidate_subjects']
    if plan['parent'] is None:
        require(plan['selections'] == [], 'initialization cannot carry historical results')
        return {v:t['record'] for v,t in candidates.items()}
    selections = plan['selections']; versions = {r['version_ref'] for r in selections}
    require(len(versions) == len(selections), 'duplicate transition choice')
    require(all(r['disposition'] in ['carry','exclude'] and r['reason'].strip() for r in selections), 'carry/exclusion requires an explicit reason')
    require(versions == set(plan['parent']['record_bindings']), 'every parent candidate needs an explicit disposition')
    carried = {r['version_ref'] for r in selections if r['disposition'] == 'carry'}
    require(carried <= set(candidates), 'carried target missing from successor candidate closure')
    for v in carried:
        require(byte_digest(encoded(candidates[v]['record'])) == plan['parent']['record_bindings'][v], 'carried original candidate bytes changed')
    excluded = versions-carried
    require(not excluded & set(candidates), 'excluded parent result reintroduced by successor profile')
    # New profile members plus selected unchanged carried records; no copied local signatures.
    return {v:t['record'] for v,t in candidates.items()}


def prepare(selection, policy, *, parent_path=None, parent_pins=None, parent_policy=None, selections=None):
    require(isinstance(policy,RehearsalPolicy), 'trusted fixture policy required')
    core = policy.core(); snapshot,catalog = package_materials(selection.repo,selection)
    parent = None
    if parent_path is not None:
        require(parent_pins is not None and parent_policy is not None, 'independent parent verification required')
        old = replay(parent_path,parent_pins,parent_policy)
        require(policy.branch_id != parent_policy.branch_id and policy.public_key != parent_policy.public_key, 'new branch and fresh rehearsal key required')
        require(not Path(policy.destination).is_relative_to(Path(parent_path)) and not Path(parent_path).is_relative_to(Path(policy.destination)), 'branch overlap forbidden')
        require(snapshot['source_profile']['transition_basis']['mode'] == 'reviewed-successor' and snapshot['source_profile']['expected_cut'] != old['snapshot']['source_profile']['expected_cut'], 'new independently selected profile/cut required')
        prior_profile = old['snapshot']['controls']['profile']
        require(prior_profile in snapshot['source_profile']['transition_basis']['basis_refs'], 'successor profile omits exact parent profile basis')
        require(snapshot['executable_materials']==old['snapshot']['executable_materials'], 'profile-only transition must retain the same exact executable')
        parent = {'branch_id':parent_pins.branch_id,'head_sha256':parent_pins.head_sha256,'catalog_digest':parent_pins.catalog_digest,
                  'record_bindings':{v:byte_digest(encoded(r)) for v,r in old['records'].items()},
                  'signatures_copied':False,'authority_effect':'none'}
    else:
        require(parent_pins is None and parent_policy is None and not selections and snapshot['source_profile']['transition_basis']['mode'] == 'initial', 'initial bootstrap has no parent or carries')
    plan = {'schema_version':'lab-isolated-catalog-plan/v1','authority_effect':'none','policy':core,'effect':policy.effect,
            'profile_sha256':snapshot['source_profile_sha256'],'snapshot_digest':snapshot['snapshot_digest'],
            'catalog_digest':catalog['digest'],'parent':parent,'selections':copy.deepcopy(selections or []),
            'global_admissions':0,'global_registry_changes':0,'project_state_mutations':0,'external_effects':0}
    records = _records(catalog,plan)
    return {'plan':plan,'snapshot':snapshot,'catalog':catalog,'records':records}


def sign(prepared, policy, private_key):
    require(prepared['plan']['policy'] == policy.core(), 'review and policy differ')
    p = Path(private_key)
    require(not p.is_symlink() and stat.S_IMODE(p.stat().st_mode) == 0o600 and not p.resolve().is_relative_to(ROOT)
            and not p.resolve().is_relative_to(Path(policy.destination)), 'fixture key must be external regular mode 0600')
    private = serialization.load_pem_private_key(file_bytes(p),password=None)
    require(isinstance(private,Ed25519PrivateKey) and private.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw).hex() == policy.public_key, 'fixture key differs from trusted adapter')
    now = datetime.now(timezone.utc); require(now < time_value(policy.expires_at), 'fixture policy expired')
    core = {'schema_version':'lab-isolated-rehearsal-response/v1','plan_digest':digest(prepared['plan']),
            'policy_sha256':digest(policy.core()),'approved_at':now.isoformat(),'fixture_only':True,'human_outcome':None}
    return {**core,'signature':private.sign(encoded(core)).hex()}


def apply(selection, prepared, response, policy, *, parent_path=None, parent_pins=None, parent_policy=None, crash_at=None):
    require(crash_at in [None,'after-stage','after-publish'], 'invalid isolated crash hook')
    require(datetime.now(timezone.utc) < time_value(policy.expires_at), 'fixture policy expired')
    dest = Path(policy.destination); require(dest.parent.is_dir() and not dest.parent.is_symlink(), 'existing isolated parent directory required')
    fresh = prepare(selection,policy,parent_path=parent_path,parent_pins=parent_pins,parent_policy=parent_policy,selections=prepared['plan']['selections'])
    require(fresh == prepared, 'candidate proposal changed; fresh review required')
    verify_response(response,prepared['plan'],policy)
    require(time_value(response['approved_at']) <= datetime.now(timezone.utc), 'future rehearsal response cannot authorize effects')
    files = {'plan.json':encoded(prepared['plan']),'snapshot.json':encoded(prepared['snapshot']),
             'catalog.json':encoded(prepared['catalog']),'records.json':encoded(prepared['records']),
             'rehearsal-response.json':encoded(response)}
    head = {'schema_version':'lab-isolated-catalog-head/v1','authority_effect':'none','branch_id':policy.branch_id,
            'files':{n:byte_digest(raw) for n,raw in files.items()}}
    files['HEAD.json'] = encoded(head)
    pins = CatalogPins(policy.branch_id,byte_digest(files['HEAD.json']),prepared['plan']['profile_sha256'],
                       prepared['plan']['snapshot_digest'],prepared['plan']['catalog_digest'],digest(policy.core()))
    if os.path.lexists(dest):
        replay(dest,pins,policy)
        return {'pins':asdict(pins),'idempotent':True,'authority_effect':'none'}
    fd = os.open(dest.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    lock = os.open('.'+dest.name+'.bootstrap.lock',os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600,dir_fd=fd)
    try:
        try: fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError as exc: raise RuntimeFault('isolated branch writer active') from exc
        require(os.path.realpath('/proc/self/fd/'+str(fd)) == str(dest.parent), 'isolated parent moved')
        stage = '.'+dest.name+'.bootstrap-'+digest(prepared['plan'])
        stage_path = Path('/proc/self/fd/'+str(fd))/stage
        if os.path.lexists(stage_path):
            replay(stage_path,pins,policy)
        else:
            os.mkdir(stage,mode=0o700,dir_fd=fd)
            sfd = os.open(stage,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
            try:
                for name,raw in files.items():
                    out = os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=sfd)
                    with os.fdopen(out,'wb') as h: h.write(raw);h.flush();os.fsync(h.fileno())
                os.fsync(sfd);os.fsync(fd)
            finally: os.close(sfd)
        replay(stage_path,pins,policy)
        if crash_at == 'after-stage': os._exit(75)
        require(freshness(selection.repo,prepared['snapshot'])['status'] == 'current' and datetime.now(timezone.utc)<time_value(policy.expires_at), 'candidate source or authority changed before isolated commit')
        require(os.path.realpath('/proc/self/fd/'+str(fd)) == str(dest.parent), 'isolated parent moved before commit')
        _publish(fd,stage,dest.name)
        if crash_at == 'after-publish': os._exit(76)
    finally: os.close(lock);os.close(fd)
    replay(dest,pins,policy)
    return {'pins':asdict(pins),'idempotent':False,'authority_effect':'none'}
