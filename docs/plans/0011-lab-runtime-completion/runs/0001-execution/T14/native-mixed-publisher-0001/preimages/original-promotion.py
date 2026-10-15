"""Selected committed-result export and independent repository review cores.

No local approval is copied into a repository authorization. Record/schema
postimages retain their exact legacy committed encoding and source selectors.
"""
from __future__ import annotations
import base64
import copy
from dataclasses import dataclass
from pathlib import Path
import re
from urllib.parse import urljoin, urlparse, unquote

from .common import RuntimeFault, byte_digest, digest, encoded, loads, pointer, require
from .extensions import inspect_bound_extension
from .sources import capture, validate_schema
from .transition import (_closed, _contract, _date, _file_bytes, _record_identity,
                         _selection_again, _target_index, _validate, committed_files)
from .store import VerifiedLegacyReadStore

GOVERNANCE_KINDS = ['project-state', 'project-semantic-event-history', 'project-governance-event-history',
                    'decision', 'decision-scope', 'authority-boundary', 'decision-bundle',
                    'decision-checkpoint', 'admission-transaction', 'generated-output', 'typed-relation']


def public_material(value):
    """Reject private path/key/session payloads; never crawl unrelated store files."""
    if isinstance(value, dict):
        require(not ({'private_key', 'private_key_bytes', 'session_memory', 'short_memory'} & set(value)), 'private/session payload cannot be exported')
        for k, v in value.items(): public_material(k); public_material(v)
    elif isinstance(value, list):
        for v in value: public_material(v)
    elif isinstance(value, str):
        require('PRIVATE KEY-----' not in value, 'private key payload cannot be exported')
        parts = value.replace('\\', '/').split('/')
        require(not any(p == '.local' or p == '.env' or p.startswith('.env.') for p in parts), 'private path cannot be exported')


def relative(value):
    require(isinstance(value, str) and value and '\\' not in value and '\x00' not in value
            and not Path(value).is_absolute() and '..' not in Path(value).parts
            and Path(value).as_posix() == value, 'noncanonical publication path')
    public_material(value)
    require(not value.endswith(('.pem', '.key')), 'private file publication forbidden')
    return value


@dataclass(frozen=True)
class RepositoryAuthority:
    """Independently resolved trusted adapter authority, never a call-body claim.

    Real R08 use requires its actual owner/role resolution. Test fixtures use an
    independent test key and explicit fixture claim ceiling.
    """
    repository_root: str
    principal_ref: str
    public_key: str
    scope_ref: str
    policy_ref: str
    challenge_route: str
    expires_at: str
    bundle_id: str
    bundle_path: str
    owner_roles: tuple
    authority_basis_ref: str
    current_pointer_path: str = 'authority/project-state-transitions/current.json'
    claim_ceiling: str = 'Exact repository bundle admission only; no activation or external effect.'

    def core(self):
        require(str(Path(self.repository_root).resolve()) == self.repository_root, 'canonical repository root required')
        relative(self.bundle_path); relative(self.current_pointer_path)
        require(re.fullmatch(r'authority/admissions/[a-z0-9-]+/v[0-9]+', self.bundle_path), 'immutable admission bundle path required')
        require(self.current_pointer_path == 'authority/project-state-transitions/current.json', 'unsupported current lookup location')
        try: require(len(bytes.fromhex(self.public_key)) == 32, 'invalid repository public key')
        except ValueError as exc: raise RuntimeFault('invalid repository public key') from exc
        _date(self.expires_at)
        roles = dict(self.owner_roles)
        require(len(roles) == len(self.owner_roles) and roles and set(roles) <= {'artifact-instance', 'typed-relation', 'definition', 'artifact-type', 'relation-kind'}, 'closed owner category bindings required')
        value = {k:getattr(self, k) for k in self.__dataclass_fields__ if k != 'owner_roles'}
        require(all(isinstance(v, str) and v for v in value.values()), 'repository authority fields required')
        value['owner_roles'] = roles
        value['authority_boundary'] = 'independently-resolved-repository-owner'
        value['permitted_effect'] = 'one-exact-immutable-repository-bundle'
        return value


def schema_closure(paths, documents):
    needed = list(paths); result = {}
    while needed:
        name = needed.pop()
        if name in result: continue
        require(name in documents, 'schema outside selected committed/canonical closure: ' + name)
        document = documents[name]; result[name] = copy.deepcopy(document)
        def walk(v):
            if isinstance(v, dict):
                for keyword in ['$ref', '$dynamicRef']:
                    ref = v.get(keyword)
                    if ref and not ref.startswith('#'):
                        absolute = urlparse(urljoin('https://lab.invalid/' + name, ref))
                        require(absolute.scheme == 'https' and absolute.netloc == 'lab.invalid', 'remote schema export forbidden')
                        needed.append(unquote(absolute.path.lstrip('/')))
                for x in v.values(): walk(x)
            elif isinstance(v, list):
                for x in v: walk(x)
        walk(document)
    return result


def validate_promotion_record(record, category, carrier, context, identities, subjects):
    # ArtifactType/v3 is a registry wrapper; raw registered descriptors use its
    # registered_types/items selector, not the wrapper instance discriminator.
    if category == 'artifact-type' and carrier == 'cal.artifact-type.artifact-type/v3':
        c = _contract(context, carrier)
        validate_schema(record, c['schema_path'], '#/properties/registered_types/items', context['documents'])
        return _record_identity(record, category, carrier, c, identities), 'artifact-type'
    return _validate(record, category, carrier, context, identities, subjects)


def _current(subjects, identity):
    return [e for e in subjects.values() if e['identity'] == identity and e['effective_state'] == 'admitted-current']


def prepare_promotion(parent, selection, selections, identity_path, identity_sha256, authority,
                      *, extension_packages=None, mirrors=()):
    """Read-only dry review of selected committed bytes; no publication or grant."""
    require(isinstance(parent, VerifiedLegacyReadStore), 'pinned full parent verifier required')
    policy = authority.core(); repo = Path(authority.repository_root)
    require(selection.repo == repo, 'repository authority and selected source root differ')
    snapshot = capture(_selection_again(selection)); data = parent.verify_full()
    bindings = committed_files(parent, data); index = _target_index(data, bindings)
    raw_identity = _file_bytes(identity_path)
    require(byte_digest(raw_identity) == identity_sha256, 'identity mapping pin mismatch')
    identities = loads(raw_identity)
    require(isinstance(selections, list) and 0 < len(selections) <= 1000, 'bounded selected results required')
    extensions = extension_packages or {}; require(set(extensions) <= {s['version_ref'] for s in selections}, 'unselected extension package forbidden')
    context = copy.deepcopy({k:snapshot[k] for k in ['subjects', 'contracts', 'relation_contracts', 'documents', 'state', 'histories']})
    materials, targets, cores, touched, decisions, seen_identities = {}, [], [], set(), set(), set()
    old_decisions = {t['target']['decision_ref'] for t in index.values()}
    old_decisions |= {r['node_id'] for r in (e['record'] for e in snapshot['subjects'].values()) if isinstance(r, dict) and r.get('kind') == 'decision'}
    inspections = {}
    for s in selections:
        _closed(s, ['version_ref', 'carrier_ref', 'operation', 'predecessor_ref', 'decision_ref', 'evidence_selectors'])
        version = s['version_ref']; require(version in index and version not in touched, 'uncommitted or duplicate selected revision')
        touched.add(version); target = index[version]['target']; old = data['projection']['subjects'][version]
        require(old['effective_state'] in ['local-admitted-current', 'local-withdrawn'], 'historical local result cannot be promoted')
        require(s['operation'] in ['admit', 'revise', 'withdraw'], 'unknown repository effect')
        require(s['decision_ref'] not in old_decisions and s['decision_ref'] not in decisions, 'repository Decision must have independent new identity')
        decisions.add(s['decision_ref']); category = target['category']
        require(category in policy['owner_roles'], 'repository owner role for selected category is unresolved')
        require(old['identity'] not in seen_identities, 'multiple selected effects for one identity'); seen_identities.add(old['identity'])
        current = _current(context['subjects'], old['identity'])
        if s['operation'] == 'admit':
            require(version not in snapshot['subjects'] and not current and s['predecessor_ref'] is None, 'revision/identity already present; select exact repository revision effect')
        else:
            require(len(current) == 1 and current[0]['version_ref'] == s['predecessor_ref'], 'repository predecessor mismatch')
            require(s['predecessor_ref'] in data['projection']['subjects'] and current[0]['record'] == data['projection']['subjects'][s['predecessor_ref']]['record'], 'repository predecessor differs from local evidence')
            if s['operation'] == 'revise': require(version not in snapshot['subjects'], 'immutable repository revision already exists')
            else: require(version == s['predecessor_ref'] and target['operation'] == 'withdraw', 'withdrawal must select committed exact withdrawal target')
        record = target['record'] if target['record'] is not None else current[0]['record']
        public_material(record)
        record_path = 'targets/' + byte_digest(encoded({'version_ref': version})) + '.json'
        materials[record_path] = encoded(record)
        target_meta = {**s, 'category': category, 'identity': old['identity'], 'record_path': record_path,
            'record_sha256': byte_digest(encoded(record)), 'kind': old['kind'], 'contract': target['contract'],
            'source_provenance': index[version]['provenance']}
        # Evidence extraction is exact and selected. Whole transaction/config,
        # owner approvals, private keys and Session notes have no export path.
        require(isinstance(s['evidence_selectors'], list) and len(s['evidence_selectors']) <= 20, 'bounded evidence selectors required')
        tx = next(t for t in data['transactions'] if t['digest'] == index[version]['provenance']['transaction_digest'])
        i = index[version]['provenance']['selector'].split('/')[3]
        allowed = {f'/decision_cores/{i}', f'/proposal/targets/{i}/contract'}
        evidence_bindings = []
        for selector in s['evidence_selectors']:
            require(selector in allowed, 'unselected/private/local-approval evidence selector forbidden')
            evidence = pointer(tx, selector); public_material(evidence)
            raw = encoded(evidence); path = 'evidence/' + byte_digest(raw) + '.json'; materials[path] = raw
            evidence_bindings.append({'path': path, 'sha256': byte_digest(raw), 'transaction_sha256': index[version]['provenance']['transaction_sha256'], 'selector': selector})
        target_meta['evidence_bindings'] = evidence_bindings
        # Carry only schemas belonging to a selected newly declared contract.
        if category == 'artifact-type':
            c = target['contract']; require(isinstance(c, dict), 'selected artifact type requires its committed contract')
            require(record['artifact_type_ref'] == version and record['schema_path'] == c['schema_path']
                    and record['schema_sha256'] == c['schema_sha256'] and record['schema_selector'] == c['schema_selector'], 'descriptor/schema binding differs from committed contract')
            docs = schema_closure([c['schema_path']], data['projection']['documents'])
            require(byte_digest(encoded(docs[c['schema_path']])) == c['schema_sha256'], 'selected committed schema digest mismatch')
            for name, document in docs.items():
                require(name not in context['documents'] or context['documents'][name] == document, 'immutable schema path collision')
                context['documents'][name] = document
            descriptor = {**record, 'instance_contract': {'identity_field': c['identity_field'], 'instance_discriminator': c['instance_discriminator']}, 'allowed_relation_kinds': c['allowed_relation_kinds'], 'relation_roles': c['relation_roles']}
            context['contracts'][version] = {**c, 'artifact': descriptor, 'artifact_type_ref': version,
                'artifact_path': authority.bundle_path + '/' + record_path, 'artifact_sha256': target_meta['record_sha256'], 'lifecycle_state': 'admitted-current'}
        targets.append(target_meta)
        if s['operation'] in ['revise', 'withdraw']:
            context['subjects'][s['predecessor_ref']]['effective_state'] = 'withdrawn' if s['operation'] == 'withdraw' else 'admitted-historical'
            if category == 'artifact-type':
                context['contracts'][s['predecessor_ref']]['lifecycle_state'] = 'withdrawn' if s['operation'] == 'withdraw' else 'admitted-historical'
            if category == 'relation-kind' and s['operation'] == 'withdraw':
                context['relation_contracts'].pop(record['payload']['relation_kind_id'], None)
        if s['operation'] != 'withdraw':
            context['subjects'][version] = {**old, 'record': record, 'carrier_ref': s['carrier_ref'], 'effective_state': 'admitted-current'}
    # Validate whole selected closure, including coeval new carriers/endpoints.
    for t in targets:
        record = loads(materials[t['record_path']]); c = _contract(context, t['carrier_ref'])
        ident, kind = validate_promotion_record(record, t['category'], t['carrier_ref'], context, identities, context['subjects'])
        require(ident == t['identity'], 'selected repository carrier changes identity')
        require(t['version_ref'] == record['artifact_type_ref'] if t['category'] == 'artifact-type' else t['version_ref'].startswith(ident + '@'), 'selected exact version mismatch')
        if t['category'] == 'artifact-type' and t['operation'] != 'withdraw':
            for ref in record['semantic_definition_refs']:
                matches = [context['subjects'][ref]] if ref in context['subjects'] else _current(context['subjects'], ref)
                require(len(matches) == 1 and matches[0]['category'] == 'definition'
                        and matches[0]['effective_state'] == 'admitted-current',
                        'selected type has an unselected/unavailable Definition binding: ' + ref)
        t['kind'] = kind
        if t['operation'] != 'withdraw': context['subjects'][t['version_ref']]['kind'] = kind
        # New global connection meanings need the complete C14 structural review.
        if t['category'] == 'relation-kind' and t['operation'] != 'withdraw':
            require(t['version_ref'] in extensions, 'typed-extension review package required')
            package = extensions[t['version_ref']]
            _closed(package, ['proposal', 'candidate_endpoint_contracts', 'evidence_bytes'])
            p = package['proposal']; payload = record['payload']
            require(p['scope'] == 'global' and p['successor_version_ref'] == t['version_ref'] and p['relation_kind_ref'] == payload['relation_kind_id']
                and p['axis_ref'] == payload['axis_id'] and p['unique_question'] == payload['unique_question'], 'extension proof covers another semantic target')
            require([(r['source_kind'], r['target_kind']) for r in p['allowed_endpoint_pairs']] == [(r['source_kind'], r['target_kind']) for r in payload['allowed_endpoint_pairs']], 'extension proof endpoint pairs differ')
            inspections[t['version_ref']] = inspect_bound_extension(p, snapshot=snapshot,
                expected_profile_sha256=snapshot['source_profile_sha256'], expected_snapshot_digest=snapshot['snapshot_digest'],
                candidate_endpoint_contracts=package['candidate_endpoint_contracts'], evidence_bytes=package['evidence_bytes'])
            raw = encoded(p); materials['extension/' + byte_digest(raw) + '.json'] = raw
            for ref, raw in package['evidence_bytes'].items():
                require(isinstance(raw, bytes) and len(raw) <= 8 * 1024**2, 'bounded original extension evidence bytes required')
                public_material(loads(raw)); materials['extension/' + byte_digest(raw) + '.json'] = raw
        core = {'schema_version': 'cyberalchemy-lab-independent-decision-core/v1',
            'decision_ref': t['decision_ref'], 'owner_ref': policy['owner_roles'][t['category']],
            'scope_ref': authority.scope_ref, 'effect_kind': t['category'] + '-' + t['operation'],
            'selected_outcome': t['operation'], 'target_ref': t['version_ref'], 'target_sha256': t['record_sha256'],
            'carrier_ref': t['carrier_ref'], 'predecessor_ref': t['predecessor_ref'],
            'contract_sha256': digest(c), 'evidence_bindings': t['evidence_bindings'],
            'semantic_review_sha256': digest(inspections[t['version_ref']]) if t['version_ref'] in inspections else None,
            'source_snapshot_digest': snapshot['snapshot_digest'],
            'hash_policy': 'stable-core-excludes-generated-consequence-digests'}
        cores.append(core)
    # No withdrawal/revision may silently orphan a previously valid current edge.
    for e in snapshot['subjects'].values():
        if e['category'] != 'typed-relation' or e['effective_state'] != 'admitted-current': continue
        endpoints = e['record']['payload']
        if any(x['version_ref'] in {t['predecessor_ref'] for t in targets if t['operation'] == 'withdraw'} for x in [endpoints['source'], endpoints['target']]):
            require(e['version_ref'] in touched and next(t for t in targets if t['version_ref'] == e['version_ref'])['operation'] == 'withdraw', 'withdrawal would orphan current relation')
    # Closed validation/export context: selected current contracts, their exact
    # schema closure, necessary endpoint subjects and the paired prior histories.
    carrier_refs = {t['carrier_ref'] for t in targets} | {t['version_ref'] for t in targets if t['category'] == 'artifact-type'}
    for kind in GOVERNANCE_KINDS:
        refs = [r for r,c in context['contracts'].items() if c['semantic_kind'] == kind and c['lifecycle_state'] == 'admitted-current']
        require(len(refs) == 1, 'ambiguous/missing generated consequence carrier: ' + kind); carrier_refs.add(refs[0])
    selected_contracts = {r: context['contracts'][r] for r in sorted(carrier_refs)}
    documents = schema_closure([c['schema_path'] for c in selected_contracts.values()], context['documents'])
    for name, document in documents.items():
        raw = base64.b64decode(snapshot['byte_contents'][name]) if name in snapshot['byte_contents'] else encoded(document)
        materials['validation/schemas/' + byte_digest(raw) + '.json'] = raw
    subjects = {}
    needed_refs = {context['state']['node_id'], context['state']['payload']['project_ref']}
    for t in targets:
        r = loads(materials[t['record_path']])
        if r.get('kind') == 'typed-relation': needed_refs.update(x['version_ref'] for x in [r['payload']['source'], r['payload']['target']])
        if t['predecessor_ref']: needed_refs.add(t['predecessor_ref'])
        if t['operation'] != 'withdraw': subjects[t['version_ref']] = context['subjects'][t['version_ref']]
    for ref in needed_refs:
        if ref in context['subjects']: subjects[ref] = context['subjects'][ref]; continue
        matches = _current(context['subjects'], ref); require(len(matches) == 1, 'unresolved required endpoint: ' + ref); subjects[matches[0]['version_ref']] = matches[0]
    predicates = {'relation.member-of', 'relation.successor-of', 'relation.materializes-consequence', 'relation.governed-by', 'relation.scopes-authority-over'}
    for t in targets:
        r = loads(materials[t['record_path']]); predicates.update(x['relation_kind_ref'] for x in r.get('relation_refs', []) if isinstance(x, dict) and 'relation_kind_ref' in x)
        if r.get('kind') == 'typed-relation': predicates.add(r['payload']['relation_kind_ref'])
    minimal = {'subjects': subjects, 'contracts': selected_contracts,
        'relation_contracts': {r: context['relation_contracts'][r] for r in sorted(predicates)},
        'documents': documents, 'state': context['state'], 'histories': context['histories']}
    templates = {}
    for kind in GOVERNANCE_KINDS:
        if kind == 'project-state': templates[kind] = context['state']; continue
        if kind in context['histories']: templates[kind] = context['histories'][kind]; continue
        current_carrier = next(r for r,c in selected_contracts.items() if c['semantic_kind'] == kind and c['lifecycle_state'] == 'admitted-current')
        rows = sorted((e for e in snapshot['subjects'].values() if e['kind'] == kind
                       and e['effective_state'] == 'admitted-current' and e['carrier_ref'] == current_carrier), key=lambda e: e['version_ref'])
        require(rows, 'generated record template unavailable: ' + kind)
        templates[kind] = copy.deepcopy(rows[0]['record'])
    minimal['templates'] = templates
    selected_identities = {'carriers': [r for r in identities['carriers'] if r['carrier_ref'] in carrier_refs]}
    materials['validation/context.json'] = encoded(minimal); materials['validation/identities.json'] = encoded(selected_identities)
    pointer_file = repo / authority.current_pointer_path
    pointer_before = byte_digest(_file_bytes(pointer_file))
    require(pointer_before == snapshot['materials'][authority.current_pointer_path], 'current repository pointer differs from captured source')
    mirror_rows = []
    for row in mirrors:
        _closed(row, ['path', 'source', 'before_sha256']); relative(row['path']); relative(row['source'])
        require(row['path'].startswith(('authority/', 'docs/decisions/', 'runtime/schemas/')) and not row['path'].startswith('authority/admissions/'), 'mirror scope must be managed authority/Decision/schema lookup outside immutable bundles')
        require(row['path'] != authority.current_pointer_path and row['path'] not in {x['path'] for x in mirror_rows}, 'duplicate/ambiguous mirror')
        existing = repo / row['path']; actual = byte_digest(_file_bytes(existing)) if existing.exists() else None
        require(actual == row['before_sha256'], 'mirror baseline mismatch'); mirror_rows.append(copy.deepcopy(row))
    require(committed_files(parent, data) == bindings, 'parent committed bytes changed during export')
    review = {'schema_version': 'lab-promotion-review/v1-candidate', 'authority_effect': 'none',
        'authority': policy, 'authority_sha256': digest(policy), 'bundle_id': authority.bundle_id,
        'bundle_path': authority.bundle_path, 'source_snapshot_digest': snapshot['snapshot_digest'],
        'source_profile_sha256': snapshot['source_profile_sha256'], 'source_cut': snapshot['expected_cut'],
        'expected_pointer_sha256': pointer_before, 'identity_binding_sha256': identity_sha256,
        'parent': {'store_id': data['config']['store_id'], 'head': data['head']['transaction_digest'], 'committed_files': bindings},
        'selections': copy.deepcopy(selections), 'targets': targets, 'independent_cores': cores,
        'core_sha256s': [byte_digest(encoded(c)) for c in cores], 'extension_inspections': inspections,
        'material_sha256s': {p:byte_digest(raw) for p,raw in materials.items()}, 'mirrors': mirror_rows,
        'runtime_activations': 0, 'external_effect_refs': [], 'local_approvals_exported': 0,
        'byte_semantics': 'exact legacy committed record/schema postimages; original transaction SHA/selectors retained; precommit artifact bytes unavailable'}
    # The reviewed generator closure comes from the independently selected profile.
    review['generator_binding'] = {'profile_sha256': snapshot['source_profile_sha256'],
        'executable_manifest_sha256': snapshot['controls']['executable_manifest']['sha256'],
        'files': snapshot['executable_materials'], 'implementation_admission': 'requires-R08-exact-package'}
    return {'review': review, 'materials': materials, 'snapshot': snapshot}
