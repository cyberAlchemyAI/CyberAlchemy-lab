"""Exact private legacy metadata adaptation; external bodies are never outputs.

The selected schemas validate real carriers. The local profile adds source,
endpoint and vocabulary closure. Native events are sealed and replayed by the
unchanged O02 candidate library in a disposable store outside the repository.
"""
import base64
import collections
import copy
import datetime
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
MIGRATION = HERE.parent
SCOPE = HERE / 'build-scope.json'
PROFILE = HERE / 'translation-profile.json'
sys.path.insert(0, str(ROOT / 'docs/migration-plans/lab-selected-slice'))
from check_inventory import validate_selection, verify_observations, safe
from build_inventory import SOURCE_ROOT, WORKSPACE_ROOT, STANDALONE_ROOT, NAMESPACE
sys.path.insert(0, str(ROOT / 'implementation/lab-ontology/candidates/v1/adapters/lifecycle'))
from native_store import NativeCandidateStore
from translation import (RichTranslation, canonical, check_schema, node_id,
    signed_catalog, CandidateRepresentationAdapter, bind, original, parse, sha,
    require, object_sha, Draft202012Validator)

OUTPUT_REF = 'generated-output:O05-selected-legacy-package@1.0.0-candidate.1'
OWNER = 'protocol:O05-exact-candidate-review'
SCHEMA_REFS = {'source': 'cal.artifact-type.source/v1',
    'ontology-node': 'cal.artifact-type.ontology-node/v2',
    'ontology-edge': 'cal.artifact-type.ontology-edge/v1',
    'generated-output': 'cal.artifact-type.generated-output/v2'}


def record_bytes(record):
    return (json.dumps(record, sort_keys=True, indent=2, ensure_ascii=False,
        allow_nan=False) + '\n').encode()


def pointer(value, selector):
    """JSON Pointer including exact array positions; no discovery aliases."""
    if selector == '':
        return value
    require(type(selector) is str and selector.startswith('/'), 'invalid JSON pointer')
    for token in selector[1:].split('/'):
        require(not re.search(r'~(?![01])', token), 'invalid pointer escape')
        part = token.replace('~1', '/').replace('~0', '~')
        if type(value) is list:
            require(re.fullmatch(r'0|[1-9][0-9]*', part) is not None, 'invalid array position')
            require(int(part) < len(value), 'array selector unresolved')
            value = value[int(part)]
        else:
            require(type(value) is dict and part in value, 'object selector unresolved')
            value = value[part]
    return value


def schema(record, binding):
    check_schema(record, binding)


class SourceTranslation:
    """Separate source profile; no edits to the governed-subject translator."""
    def __init__(self, catalog, operations):
        self.scope_binding = bind(SCOPE)
        self.scope = parse(original(self.scope_binding))
        self.profile_binding = self.scope['profile_binding']
        require(self.profile_binding['path'] == PROFILE.relative_to(ROOT).as_posix(),
            'unselected O05 translation profile')
        self.profile = parse(original(self.profile_binding))
        self.selection = parse(original(self.scope['selection_binding']))
        self.selection_sha = object_sha(self.selection)
        self.scope_sha = object_sha(self.scope)
        self.profile_sha = object_sha(self.profile)
        self.code_bindings = [bind(p) for p in sorted(HERE.glob('*.py'))]
        self.code_bindings += [bind(p) for p in sorted(HERE.glob('*.md'))]
        self.adapter = CandidateRepresentationAdapter(catalog, operations)
        self.definitions = RichTranslation(self.adapter, self.profile['inherited_profile_binding'])
        self.owner = OWNER
        self.source_roots = {'historical-cav2': SOURCE_ROOT,
            'historical-workspace': WORKSPACE_ROOT, 'standalone-cav2': STANDALONE_ROOT}
        self.schema_bindings = {r: c['schema_binding'] for r, c in self.profile['carriers'].items()}
        self.schema_bindings[self.profile['output_carrier']['carrier_ref']] = self.profile['output_carrier']['schema_binding']
        self.definition_witnesses = {r: self.definitions.definition(r)
            for r in self.profile['definition_refs']}
        self.guard()
        validate_selection(self.selection, True)

    def guard(self):
        self.adapter.guard()
        require(object_sha(self.scope) == self.scope_sha
            and parse(original(self.scope_binding)) == self.scope, 'build scope changed')
        require(object_sha(self.profile) == self.profile_sha
            and parse(original(self.profile_binding)) == self.profile, 'source profile changed')
        require(object_sha(self.selection) == self.selection_sha
            and parse(original(self.scope['selection_binding'])) == self.selection, 'source selection changed')
        require(self.scope['authority_effect'] == self.profile['authority_effect'] == 'none'
            and self.scope['actual_owner_outcome'] is self.profile['actual_owner_outcome'] is None,
            'source profile cannot confer authority')
        for flag in ('source_execution_allowed', 'source_mutation_allowed',
                     'source_body_copy_allowed', 'private_body_export_allowed'):
            require(self.scope[flag] is False, 'source boundary violation')
        require(self.profile['namespace'] == self.selection['namespace'] == NAMESPACE,
            'legacy namespace changed')
        require(self.profile['source_selection_binding'] == self.scope['selection_binding'],
            'profile/selection join differs')
        require(self.profile['predicates'] == sorted({i['source_relation_type']
            for i in self.selection['items'] if i['item_kind'] == 'relation'}), 'unclosed local vocabulary')
        inherited = parse(original(self.profile['inherited_profile_binding']))
        require(all(self.profile[k] == inherited[k] for k in ('node_profile_ref',
            'relation_profile_ref', 'property_schema_bindings', 'confidence', 'definition_selector')),
            'undeclared native profile extension')
        require(datetime.datetime.fromisoformat(self.scope['captured_at']).utcoffset()
            == datetime.timedelta(0), 'capture time must be pinned UTC')
        for b in self.code_bindings:
            original(b)
        for ref, b in self.schema_bindings.items():
            original(b)
            contract = self.adapter.catalog['contracts'].get(ref)
            require(contract is not None and contract['lifecycle_state'] in ('admitted-current', 'local-admitted-current')
                and contract['schema_path'] == b['path'] and contract['schema_sha256'] == b['sha256'],
                'current signed carrier/schema join differs')
        for ref, d in self.definition_witnesses.items():
            require(self.definitions.definition(ref) == d, 'Definition selector witness changed')
        verify_observations(self.selection)

    def selected_bytes(self, item):
        """Nominated path and revision only, including previously stale observations."""
        require(item in self.selection['items'], 'unselected source item')
        b = item['source_binding']
        require(b is not None and item['disposition'] != 'block', 'blocked revision has no usable bytes')
        p = safe(self.source_roots[b['root_ref']], b['path'])
        raw = p.read_bytes()
        require(sha(raw) == b['sha256'], 'selected source bytes changed')
        if b['selector']:
            row = pointer(parse(raw), b['selector'])
            require(object_sha(row) == item['record_structure_sha256']
                and row['id'] == item['legacy_identity'], 'selected row structure/identity differs')
        return raw

    def locator(self, item):
        b = item['source_binding']
        return ('legacy-source://' + b['root_ref'] + '/' + quote(b['path'], safe='/')
            + '?sha256=' + b['sha256'] + '&selector=' + quote(b['selector'], safe=''))

    def source_record(self, item):
        self.selected_bytes(item)
        binding = item['source_binding']
        ident = 'source:O05:' + sha(canonical([self.profile['namespace'], item['item_id'], binding]))
        content_digest = (('json-structure-sha256:' + item['record_structure_sha256'])
            if binding['selector'] else 'file-sha256:' + binding['sha256'])
        record = {'schema_version': 'cyberalchemy-lab-source/v1', 'node_id': ident,
            'kind': 'source', 'name': 'Observed legacy ' + item['item_id'],
            'lifecycle_state': 'candidate', 'authority_effect': 'none', 'owner_ref': self.owner,
            'scope_ref': self.profile['namespace'], 'evidence_refs': [self.locator(item)],
            'challenge_route': self.owner, 'successor_refs': [],
            'relation_refs': [{'relation_kind_ref': 'relation.derives-from', 'direction': 'target',
                'counterpart_kind': 'generated-output', 'counterpart_ref': OUTPUT_REF}],
            'payload': {'source_kind': 'legacy-' + item['item_kind'] + '-metadata-reference',
                'locator': self.locator(item), 'content_digest': content_digest,
                'captured_at': self.scope['captured_at'],
                'provenance_refs': [self.scope['selection_binding']['path'] + '#sha256='
                    + self.scope['selection_binding']['sha256'] + '&item=' + quote(item['item_id'], safe='')]},
            'claim_ceiling': self.profile['claim_ceiling']}
        schema(record, self.schema_bindings[SCHEMA_REFS['source']])
        return record

    def node(self, item, source):
        digest = sha(record_bytes(source))
        subject = {'kind': 'source', 'identity': source['node_id'],
            'version_ref': source['node_id'] + '@1.0.0-candidate.1', 'carrier_bytes_sha256': digest}
        ident = node_id(subject, self.profile)
        refs = self.profile['definition_refs'][:2]
        components = [{'component_id': 'ontology-representation', 'type_ref': SCHEMA_REFS['ontology-node'],
            'definition_ref': self.definition_witnesses[refs[0]]['reference']},
            {'component_id': 'represented-source', 'type_ref': SCHEMA_REFS['source'],
                'definition_ref': self.definition_witnesses[refs[1]]['reference']}]
        properties = {'carrier_ref': SCHEMA_REFS['source'], 'carrier_kind': 'source',
            'represented_kind': 'source', 'identity_ref': subject['identity'],
            'version_ref': subject['version_ref'], 'record_sha256': digest,
            'schema_sha256': self.schema_bindings[SCHEMA_REFS['source']]['sha256'],
            'mapping_sha256': self.profile_binding['sha256']}
        schema(properties, self.profile['property_schema_bindings']['node'])
        proposition = ('Records the exact source-qualified observation of ' + item['legacy_identity']
            + '; original source role is metadata, no Lab domain instance or authority inferred.')
        state = {'identity': {'subject_id': ident, 'ontology_id': self.profile['ontology_ref'],
                'subject_kind': 'node', 'type_ref': self.profile['node_type_ref']},
            'lifecycle': 'active', 'label': item['legacy_identity'], 'definition_or_claim': proposition,
            'scope': self.profile['namespace'], 'semantic_components': components,
            'semantic_definition_refs': [self.definition_witnesses[r]['reference'] for r in refs],
            'typed_properties': {'profile_ref': self.profile['node_profile_ref'], 'values': properties},
            'use_obligations': [{'obligation_id': 'use-obligation:' + sha(v.encode()),
                'requirement': v, 'applies_to_use': self.profile['namespace']}
                for v in self.profile['use_obligations']],
            'forbidden_collapse': [{'left_ref': ident, 'right_ref': 'semantic-axis:' + v,
                'context': self.profile['ontology_ref'], 'intended_use': self.profile['namespace']}
                for v in self.profile['forbidden_collapse']], 'profile_ref': self.profile['node_profile_ref']}
        return {'item_id': item['item_id'], 'source_subject': subject, 'state': state,
            'definition_refs': refs, 'proposition': proposition}

    def node_record(self, spec, semantic, governance):
        subject = spec['source_subject']; state = spec['state']
        record = {'schema_version': 'cyberalchemy-lab-ontology-node/v2',
            'node_id': state['identity']['subject_id'], 'kind': 'ontology-node', 'name': state['label'],
            'record_state': 'candidate', 'authority_effect': 'none', 'owner_ref': self.owner,
            'scope_ref': self.profile['namespace'], 'evidence_refs': [subject['version_ref']],
            'challenge_route': self.owner, 'successor_refs': [], 'claim_ceiling': self.profile['claim_ceiling'],
            'payload': {'ontology_ref': self.profile['ontology_ref'],
                'ontology_manifest_ref': self.scope['output_root'] + '/native.snapshot',
                'represented_subject': {'kind': 'source', 'ref': subject['identity'],
                    'version_ref': subject['version_ref'], 'digest': subject['carrier_bytes_sha256']},
                'node_type_ref': self.profile['node_type_ref'], 'profile_ref': self.profile['node_profile_ref'],
                'branch': 'mixed', 'semantic_state': {'lifecycle': 'active', 'label': state['label'],
                    'proposition': spec['proposition'], 'semantic_components': [c['component_id'] for c in state['semantic_components']],
                    'semantic_definition_refs': spec['definition_refs'],
                    'typed_properties': state['typed_properties']['values'],
                    'use_obligations': self.profile['use_obligations'], 'forbidden_collapse': self.profile['forbidden_collapse']},
                'governance_binding': {'semantic_event_ref': NativeCandidateStore.reference(None, semantic),
                    'governance_event_refs': [governance['event_id']],
                    'evidence_confidence_ref': self.profile['confidence']['scheme_ref'] + '#evidence:not-assessed',
                    'commitment_confidence_ref': self.profile['confidence']['scheme_ref'] + '#commitment:not-assessed',
                    'challenge_contract_ref': self.owner, 'authority_effect': 'none'},
                'provenance_refs': [subject['version_ref']], 'replay_source': False}}
        schema(record, self.schema_bindings[SCHEMA_REFS['ontology-node']])
        return record

    def edge(self, item, specs):
        require(item['source_relation_type'] in self.profile['predicates'], 'undeclared local predicate')
        source = specs[item['source_endpoint_id']]; target = specs[item['target_endpoint_id']]
        b = item['source_binding']
        qualifiers = {'source_item_id': item['item_id'], 'source_root_ref': b['root_ref'],
            'source_path': b['path'], 'source_file_sha256': b['sha256'], 'source_selector': b['selector'],
            'source_record_structure_sha256': item['record_structure_sha256'],
            'source_node_version_ref': source['source_subject']['version_ref'],
            'target_node_version_ref': target['source_subject']['version_ref'],
            'blocked_dependency_ids': item['unresolved_dependency_ids']}
        require(set(qualifiers) == set(self.profile['closed_qualifier_keys']), 'local qualifier closure differs')
        ident = 'ontology-relation:' + sha(canonical([self.profile['namespace'], item['source_qualified_identity'], qualifiers]))
        predicate = self.profile['local_predicate_prefix'] + item['source_relation_type'] + '/v1-candidate'
        properties = {'relation_kind_ref': predicate,
            'relation_version_ref': item['source_qualified_identity'] + '@' + b['sha256'],
            'source_version_ref': source['source_subject']['version_ref'],
            'target_version_ref': target['source_subject']['version_ref'],
            'record_sha256': item['record_structure_sha256'], 'qualifiers_sha256': sha(canonical(qualifiers)),
            'mapping_sha256': self.profile_binding['sha256']}
        schema(properties, self.profile['property_schema_bindings']['relation'])
        state = {'identity': {'subject_id': ident, 'ontology_id': self.profile['ontology_ref'],
            'subject_kind': 'relation', 'type_ref': predicate}, 'lifecycle': 'active',
            'source_node_id': source['state']['identity']['subject_id'],
            'target_node_id': target['state']['identity']['subject_id'], 'direction': item['direction'],
            'typed_properties': {'profile_ref': self.profile['relation_profile_ref'], 'values': properties},
            'forbidden_collapse': [{'left_ref': ident, 'right_ref': 'semantic-axis:global-typed-relation',
                'context': self.profile['ontology_ref'], 'intended_use': self.profile['namespace']}]}
        return {'item': item, 'state': state, 'qualifiers': qualifiers}

    def edge_record(self, spec, semantic):
        item = spec['item']; state = spec['state']
        record = {'schema_version': 'cyberalchemy-lab-ontology-edge/v1', 'node_id': state['identity']['subject_id'],
            'kind': 'ontology-edge', 'name': item['legacy_identity'], 'record_state': 'candidate',
            'authority_effect': 'none', 'owner_ref': self.owner, 'scope_ref': self.profile['namespace'],
            'evidence_refs': [self.locator(item)], 'challenge_route': self.owner, 'successor_refs': [],
            'claim_ceiling': self.profile['claim_ceiling'], 'payload': {'ontology_ref': self.profile['ontology_ref'],
                'edge_mode': 'local-interpretation', 'relation_type_ref': state['identity']['type_ref'],
                'source_node_ref': state['source_node_id'], 'target_node_ref': state['target_node_id'],
                'direction': state['direction'], 'closed_qualifiers': spec['qualifiers'],
                'global_typed_relation_binding': None,
                'local_interpretation': {'interpretation': 'Observed original predicate ' + item['source_relation_type']
                    + ' for the exact original source endpoint pair; no global typed axis or Lab domain instance asserted.',
                    'local_scope': self.profile['namespace'], 'owner_ref': self.owner, 'evidence_refs': [self.locator(item)]},
                'lifecycle': 'active', 'forbidden_collapse': self.profile['forbidden_collapse'],
                'semantic_event_ref': {'semantic_event_id': semantic['event_id'],
                    'semantic_event_digest': semantic['event_digest'], 'semantic_cursor': semantic['semantic_cursor']},
                'replay_source': False}}
        schema(record, self.schema_bindings[SCHEMA_REFS['ontology-edge']])
        return record

    def selectors(self):
        """Literal selectors are inert, and match observations confer no semantics."""
        by_id = {i['item_id']: i for i in self.selection['items']}
        results = []
        for item in self.selection['items']:
            for ref in item.get('dependency_resolution', []):
                dep = by_id[ref['item_id']]; selector = ref['selector']; count = 0
                if dep['disposition'] == 'block':
                    status = 'blocked-source-revision'
                else:
                    raw = self.selected_bytes(dep); text = raw.decode('utf-8')
                    if selector.startswith('#'):
                        count = sum(line.strip() == selector for line in text.splitlines())
                        mode = 'exact-markdown-heading-line'
                    else:
                        count = text.count(selector); mode = 'literal-text-occurrence'
                    status = 'literal-locator-observed' if count == 1 else ('ambiguous-literal-locator' if count else 'unresolved-literal-locator')
                results.append({'item_id': item['item_id'], 'dependency_item_id': dep['item_id'],
                    'selector': selector, 'status': status, 'occurrences': count,
                    'resolution_mode': 'unavailable-exact-revision' if dep['disposition'] == 'block' else mode,
                    'source_binding': dep['source_binding'], 'semantic_resolution_claimed': False,
                    'source_body_exported': False})
        return results


def semantic_draft(state, cursor):
    identity = state['identity']
    return {'source_kind': 'canonical_event', 'event_family': 'semantic',
        'event_id': 'ontology-semantic:O05:' + str(cursor), 'event_digest': '0' * 64,
        'stream_id': 'semantic:' + identity['ontology_id'] + ':' + identity['subject_kind'] + ':' + identity['subject_id'],
        'subject_identity': identity, 'previous_event_digest': None, 'semantic_cursor': cursor,
        'complete_resulting_semantic_state': state}


def governance_draft(store, semantic, cursor, provenance):
    state = store.basic_governance(semantic, provenance, 'O05-observe-exact-private-source')
    state['owner_route'] = OWNER; state['drift_owner'] = OWNER; state['invalidation_route'] = OWNER
    state['challenge_contract']['owner_route'] = OWNER
    state['challenge_contract']['resolution_gate'] = 'protocol:O05-exact-R08-review'
    state['challenge_contract']['challenge_residue_route'] = OWNER
    state['provenance'][0]['owner_route'] = OWNER
    identity = semantic['subject_identity']
    return {'source_kind': 'canonical_event', 'event_family': 'governance',
        'event_id': 'ontology-governance:O05:' + str(cursor), 'event_digest': '0' * 64,
        'stream_id': 'governance:' + identity['ontology_id'] + ':' + identity['subject_kind'] + ':' + identity['subject_id'],
        'semantic_ref': store.reference(semantic), 'governance_cursor': cursor,
        'previous_event_digest': None, 'complete_resulting_governance_state': state}


def build():
    with signed_catalog() as (catalog, operations):
        translator = SourceTranslation(catalog, operations)
        items = translator.selection['items']; sources = {}; node_specs = {}; edges = []
        for item in items:
            if item['disposition'] == 'block':
                continue
            sources[item['item_id']] = translator.source_record(item)
            if item['item_kind'] == 'node':
                node_specs[item['legacy_identity']] = translator.node(item, sources[item['item_id']])
        for item in items:
            if item['item_kind'] == 'relation':
                edges.append(translator.edge(item, node_specs))
        specs = list(node_specs.values()) + edges
        drafts = [semantic_draft(spec['state'], i + 1) for i, spec in enumerate(specs)]
        pin = translator.scope['native_executable']
        store = NativeCandidateStore(translator, pin['path'], pin['sha256'])
        try:
            semantic = store.seal(drafts)['semantic']
            governance = store.seal(governance=[governance_draft(store, event, i + 1,
                translator.scope['selection_binding']['path'] + '#item=' + quote(specs[i].get('item_id',
                    specs[i].get('item', {}).get('item_id', '')), safe=''))
                for i, event in enumerate(semantic)])['governance']
            replay = store.append(semantic, governance, {'authority_effect': 'none',
                'source_profile_binding': translator.profile_binding, 'actual_owner_outcome': None})
            archive = store.export()
            archive['schema_version'] = 'lab-O05-private-native-archive/v1-candidate'
            archive['visibility'] = 'private-candidate-metadata'
            files = {}
            output_rows = []
            bindings_by_item = collections.defaultdict(list)
            def add(record, item_id=None):
                rel = 'records/' + record['kind'] + '/' + sha(record['node_id'].encode()) + '.json'
                raw = record_bytes(record); files[rel] = raw
                row = {'path': rel, 'sha256': sha(raw), 'kind': record['kind'],
                    'carrier_ref': SCHEMA_REFS[record['kind']], 'node_id': record['node_id'],
                    'version_ref': record['node_id'] + '@1.0.0-candidate.1',
                    'schema_binding': translator.schema_bindings[SCHEMA_REFS[record['kind']]]}
                output_rows.append(row)
                if item_id is not None:
                    bindings_by_item[item_id].append(row)
            for item_id, source in sources.items():
                add(source, item_id)
            for i, spec in enumerate(specs):
                if i < len(node_specs):
                    add(translator.node_record(spec, semantic[i], governance[i]), spec['item_id'])
                else:
                    add(translator.edge_record(spec, semantic[i]), spec['item']['item_id'])
            reconcile = [{'item_id': item['item_id'], 'disposition': item['disposition'],
                'item_kind': item['item_kind'], 'privacy': item['privacy'],
                'public_body_export_allowed': False, 'source_binding': item['source_binding'],
                'record_structure_sha256': item.get('record_structure_sha256'),
                'outputs': bindings_by_item[item['item_id']],
                'blocked_dependency_ids': item.get('unresolved_dependency_ids', []),
                'blocked_expected_sha256': item.get('expected_sha256') if item['disposition'] == 'block' else None,
                'contract_fit': item['contract_fit'], 'original_disposition_reason': item['reason'],
                'domain_instances_conformed': 0, 'actual_owner_outcome': None} for item in items]
            selectors = translator.selectors()
            core = {'schema_version': 'lab-O05-exact-adaptation-core/v1-candidate', 'task': 'O05',
                'authority_effect': 'none', 'actual_owner_outcome': None,
                'scope_binding': translator.scope_binding, 'profile_binding': translator.profile_binding,
                'selection_binding': translator.scope['selection_binding'], 'code_bindings': translator.code_bindings,
                'definition_witnesses': translator.definition_witnesses,
                'record_index': output_rows.copy(), 'dispositions': reconcile, 'selector_observations': selectors,
                'native_archive_sha256': sha(record_bytes(archive)),
                'native_semantic_cursor': len(semantic), 'native_governance_cursor': len(governance),
                'native_checkpoint_parity': replay['checkpoint_parity'],
                'visibility': 'private-candidate-metadata', 'domain_instances_conformed': 0,
                'global_typed_relations_created': 0, 'source_bodies_copied': 0, 'source_effects_applied': 0,
                'outside_references': translator.selection['unresolved_questions'],
                'excluded_packages': translator.selection['excluded_packages'],
                'deferred_source_epoch': translator.selection['standalone_product_successor'],
                'claim_ceiling': translator.profile['claim_ceiling']}
            core_digest = sha(record_bytes(core))
            generator_binding = bind(HERE / 'build.py')
            generated = {'schema_version': 'cyberalchemy-lab-generated-output/v2',
                'kind': 'generated-output', 'node_id': OUTPUT_REF.split('@')[0],
                'name': 'O05 exact selected legacy metadata adaptation', 'lifecycle_state': 'candidate',
                'authority_effect': 'none', 'owner_ref': OWNER, 'scope_ref': translator.profile['namespace'],
                'evidence_refs': [translator.scope['selection_binding']['path']], 'challenge_route': OWNER,
                'successor_refs': [], 'claim_ceiling': translator.profile['claim_ceiling'],
                'payload': {'generator_ref': generator_binding['path'] + '#sha256=' + generator_binding['sha256'],
                    'input_refs': [s['node_id'] + '@1.0.0-candidate.1' for s in sources.values()],
                    'output_digest': 'sha256:' + core_digest,
                    'reproducibility_receipt_ref': translator.scope['output_root'] + '/reproducibility.json'},
                'relation_refs': [{'relation_kind_ref': 'relation.derives-from', 'direction': 'source',
                    'counterpart_kind': 'source', 'counterpart_ref': s['node_id'] + '@1.0.0-candidate.1'}
                    for s in sources.values()]}
            schema(generated, translator.schema_bindings[SCHEMA_REFS['generated-output']]); add(generated)
            files['core.json'] = record_bytes(core)
            files['native.snapshot'] = record_bytes(archive)
            files['record-index.json'] = record_bytes(output_rows)
            files['reproducibility.json'] = record_bytes({'schema_version': 'lab-O05-build-reproduction/v1-candidate',
                'authority_effect': 'none', 'actual_owner_outcome': None, 'core_sha256': core_digest,
                'profile_binding': translator.profile_binding, 'generator_binding': generator_binding,
                'meaning': 'Deterministic construction inputs and digest; independent repeated/cold observations are recorded in the O05 validation receipt, not inferred here.',
                'independent_rebuild_verified': False})
            manifest = {'schema_version': 'lab-O05-package-manifest/v1-candidate',
                'task': 'O05', 'authority_effect': 'none', 'actual_owner_outcome': None,
                'visibility': 'private-candidate-metadata', 'core_sha256': core_digest,
                'counts': dict(collections.Counter(row['kind'] for row in output_rows)),
                'files': [{'path': p, 'sha256': sha(raw)} for p, raw in sorted(files.items())],
                'source_selection_binding': translator.scope['selection_binding'],
                'profile_binding': translator.profile_binding, 'claim_ceiling': translator.profile['claim_ceiling']}
            files['manifest.json'] = record_bytes(manifest)
            translator.guard()
        finally:
            owned_root = store.root; store.close()
            require(not owned_root.exists(), 'owned native store cleanup incomplete')
        return files


def publish(files, destination):
    """Only the selected empty package path; never overwrite existing output."""
    destination = Path(destination)
    scope = parse(SCOPE.read_bytes())
    require(destination == ROOT / scope['output_root'], 'unselected output root')
    require(not destination.is_symlink() and destination.resolve().is_relative_to(MIGRATION.resolve()), 'unsafe output root')
    require(not destination.exists() or not any(destination.iterdir()), 'existing package cannot be overwritten')
    destination.mkdir(parents=True, exist_ok=True)
    for relative, raw in sorted(files.items()):
        path = safe(destination, relative); path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as stream:
            stream.write(raw)


if __name__ == '__main__':
    if len(sys.argv) != 1:
        raise SystemExit('usage: build.py (writes only the selected empty candidate package)')
    output = build(); publish(output, ROOT / parse(SCOPE.read_bytes())['output_root'])
    manifest = parse(output['manifest.json'])
    print(json.dumps({'result': 'PASS', 'authority_effect': 'none', 'counts': manifest['counts'],
        'core_sha256': manifest['core_sha256'], 'output': parse(SCOPE.read_bytes())['output_root']}))
