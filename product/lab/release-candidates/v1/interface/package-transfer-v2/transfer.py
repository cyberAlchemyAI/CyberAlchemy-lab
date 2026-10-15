"""Exact byte package construction and complete candidate import accounting.

All facts and original controls are selected by the host. These values do not
authenticate an Actor, prove source admission, grant export permission, or
validate a target model. The transport adapter must establish those obligations
before using this pure calculation. No path, signer or filesystem writer exists.
"""
import base64
import copy
from dataclasses import dataclass
import hashlib
import importlib.util
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
SCHEMAS = ROOT / 'docs/proposals/0007-lab-integrated-schema-package/schemas'
COMMON = 'urn:cyberalchemy-lab:protocol:common:v1-candidate'
MAX_BYTES = 1024 * 1024


def require(value, reason):
    if not value:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()


def parse(raw):
    require(type(raw) is bytes and len(raw) <= MAX_BYTES, 'bounded original bytes required')
    def pairs(rows):
        result = {}
        for key, value in rows:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    def constant(value):
        raise ValueError('nonfinite JSON number')
    # Bound nesting before the JSON decoder can exhaust its Python stack.
    depth, quoted, escaped = 0, False, False
    text = raw.decode('utf-8', errors='strict')
    for char in text:
        if quoted:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in '[{':
            depth += 1
            require(depth <= 32, 'JSON nesting budget')
        elif char in ']}':
            depth -= 1
    value = json.loads(text, object_pairs_hook=pairs, parse_constant=constant)
    encoded(value)
    return value


def pin(ref, raw):
    return {'ref': ref, 'sha256': sha(raw)}


def privacy(value):
    if isinstance(value, dict):
        for key, item in value.items():
            require(not (key.lower() in {'session_memory', 'short_memory', 'private_key', 'private_credentials',
                'access_token', 'refresh_token', 'password', 'secret'} and item not in (None, False, '', [], {})),
                'private credential or Session memory')
            privacy(item)
    elif isinstance(value, list):
        for item in value:
            privacy(item)
    elif isinstance(value, str):
        require('PRIVATE KEY-----' not in value, 'private key')


@dataclass(frozen=True)
class Material:
    binding_json: bytes
    original: bytes
    dependencies_json: bytes
    artifact_json: bytes | None = None
    encoding: str = "json-utf8"


@dataclass(frozen=True)
class ExportFacts:
    actor_json: bytes
    cut_json: bytes
    contract_binding_json: bytes
    privacy_binding_json: bytes
    materials: tuple[Material, ...]


@dataclass(frozen=True)
class ImportFacts:
    actor_json: bytes
    target_cut_json: bytes
    package_binding_json: bytes
    mapping_binding_json: bytes
    disposition_binding_json: bytes
    workspace_binding_json: bytes
    target_scope_ref: str
    existing_identity_refs: tuple[str, ...]


class Transfer:
    def __init__(self, expected_source_sha256):
        self.source_pin = expected_source_sha256
        self.guard()
        spec = importlib.util.spec_from_file_location('_cal_package_transfer_original_resources', SCHEMAS.parent / 'resources.py')
        resources = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(resources)
        registry = resources.build_registry()
        for path in sorted(HERE.glob('*.schema.json')):
            schema = parse(path.read_bytes())
            Draft202012Validator.check_schema(schema)
            registry = registry.with_resource(schema['$id'], Resource.from_contents(schema))
        self.registry = registry.crawl()

    def guard(self):
        manifest_raw = (HERE / 'source-manifest.json').read_bytes()
        manifest = parse(manifest_raw)
        require(manifest['source_sha256'] == self.source_pin, 'independent package source selection differs')
        require(sha(encoded(manifest['files'] + manifest['input_bindings'])) == self.source_pin,
                'package source digest differs')
        for row in manifest['files'] + manifest['input_bindings']:
            path = ROOT / row['path']
            require(not path.is_symlink() and sha(path.read_bytes()) == row['sha256'], 'package source changed')

    def valid(self, uri, value):
        Draft202012Validator({'$ref': uri}, registry=self.registry, format_checker=FormatChecker()).validate(value)

    def closed(self, name, raw):
        value = parse(raw)
        version = 'v2-candidate' if name in ('archive', 'privacy-review') else 'v1-candidate'
        self.valid('urn:cyberalchemy-lab:internal:package-' + name + ':' + version, value)
        return value

    def bound(self, binding, raw):
        self.valid(COMMON + '#/$defs/binding', binding)
        require(sha(raw) == binding['sha256'], 'original material hash differs')
        return raw

    def graph(self, materials):
        require(type(materials) is tuple and 0 < len(materials) <= 1000, 'complete bounded package inventory required')
        graph, artifact_keys, total = {}, set(), 0
        for material in materials:
            require(type(material) is Material, 'selected material type differs')
            binding = parse(material.binding_json)
            self.bound(binding, material.original)
            require(binding['ref'] not in graph, 'duplicate material reference')
            require(material.encoding in ('json-utf8', 'text-utf8', 'binary'), 'unknown dependency encoding')
            require(type(material.original) is bytes and len(material.original) <= MAX_BYTES, 'bounded original material')
            require(b'PRIVATE KEY-----' not in material.original, 'private key')
            if material.encoding == 'json-utf8':
                privacy(parse(material.original))
            elif material.encoding == 'text-utf8':
                text = material.original.decode('utf-8', errors='strict')
                privacy(text)
            else:
                # A binary label cannot hide JSON credentials or Session memory.
                try:
                    structured = parse(material.original)
                except (ValueError, UnicodeError, RecursionError):
                    structured = None
                if structured is not None:
                    privacy(structured)
            dependencies = parse(material.dependencies_json)
            require(type(dependencies) is list and len(dependencies) <= 1000, 'bounded dependency list required')
            require(len({encoded(row) for row in dependencies}) == len(dependencies), 'duplicate dependency')
            for dependency in dependencies:
                self.valid(COMMON + '#/$defs/binding', dependency)
            header = None if material.artifact_json is None else parse(material.artifact_json)
            if header is not None:
                require(material.encoding == 'json-utf8', 'artifact carrier requires original JSON body')
                self.valid(COMMON + '#/$defs/artifact_ref', header)
                require(header['byte_sha256'] == binding['sha256'], 'artifact original bytes differ')
                identity = (header['scope_ref'], header['identity_ref'], header['version_ref'])
                require(identity not in artifact_keys, 'duplicate artifact identity and revision')
                artifact_keys.add(identity)
            total += len(material.original)
            require(total <= MAX_BYTES, 'complete original material byte budget')
            graph[binding['ref']] = {'binding': binding, 'artifact': header, 'dependencies': dependencies,
                'original_bytes_b64': base64.b64encode(material.original).decode('ascii'), 'encoding': material.encoding}
        for row in graph.values():
            for dependency in row['dependencies']:
                require(dependency['ref'] in graph and graph[dependency['ref']]['binding'] == dependency,
                        'missing or conflicting exact dependency')
        return graph

    def closure(self, graph, roots, admission):
        require(type(roots) is list and roots, 'nonempty root artifact selection required')
        require(len({encoded(row) for row in roots}) == len(roots), 'duplicate root artifact')
        require(len({encoded(row) for row in admission}) == len(admission), 'duplicate source admission basis')
        frontier = []
        for header in roots:
            matches = [ref for ref, row in graph.items() if row['artifact'] == header]
            require(len(matches) == 1, 'root artifact is missing or ambiguous')
            frontier.extend(matches)
        for binding in admission:
            require(binding['ref'] in graph and graph[binding['ref']]['binding'] == binding, 'source basis closure missing')
            frontier.append(binding['ref'])
        selected = set()
        while frontier:
            ref = frontier.pop()
            if ref not in selected:
                selected.add(ref)
                frontier.extend(row['ref'] for row in graph[ref]['dependencies'])
        require(selected == set(graph), 'unreachable extra package material')
        root_refs = {ref for ref, row in graph.items() if row['artifact'] in roots}
        return [graph[ref]['binding'] for ref in sorted(selected - root_refs)]

    def export(self, request_raw, facts, contract_raw, review_raw):
        self.guard()
        try:
            require(type(facts) is ExportFacts, 'host-selected export facts required')
            request = parse(request_raw)
            self.valid('urn:cyberalchemy-lab:protocol:package-export-request:v1-candidate', request)
            require(request['actor'] == parse(facts.actor_json), 'Actor differs from selected host facts')
            require(request['source_cut'] == parse(facts.cut_json), 'export source cut differs')
            require(request['export_contract_binding'] == parse(facts.contract_binding_json)
                    and request['privacy_review_binding'] == parse(facts.privacy_binding_json), 'independent controls differ')
            self.bound(request['export_contract_binding'], contract_raw)
            self.bound(request['privacy_review_binding'], review_raw)
            contract = self.closed('export-contract', contract_raw)
            review = self.closed('privacy-review', review_raw)
            require(contract['source_cut'] == request['source_cut'] and contract['artifact_refs'] == request['artifact_refs'],
                    'complete independent export selection differs')
            require(contract['source_posture'] != 'admitted-source' or contract['source_admission_basis'],
                    'admitted source lacks its evidence closure')
            graph = self.graph(facts.materials)
            dependencies = self.closure(graph, request['artifact_refs'], contract['source_admission_basis'])
            require(request['dependency_bindings'] == dependencies == contract['dependency_bindings'],
                    'complete ordered dependency closure differs')
            require(review['source_cut'] == request['source_cut'] and review['export_contract_binding'] == request['export_contract_binding']
                and review['materials'] == [graph[ref]['binding'] for ref in sorted(graph)]
                and review['material_encodings'] == [{'binding': graph[ref]['binding'], 'encoding': graph[ref]['encoding']} for ref in sorted(graph)],
                'privacy review misses package material or encoding')
            package = {'schema_version': 'lab-source-package/v2-candidate', 'source_cut': request['source_cut'],
                'artifact_refs': request['artifact_refs'], 'source_admission_basis': contract['source_admission_basis'],
                'source_posture': contract['source_posture'], 'materials': [graph[ref] for ref in sorted(graph)],
                'export_contract_binding': request['export_contract_binding'], 'privacy_review_binding': request['privacy_review_binding'],
                'export_contract_bytes_b64': base64.b64encode(contract_raw).decode('ascii'),
                'privacy_review_bytes_b64': base64.b64encode(review_raw).decode('ascii'),
                'authority_effect': 'none', 'target_admission_granted': False, 'contains_session_memory': False,
                'contains_private_credentials': False, 'source_admission_verified_by_this_calculation': False}
            self.valid('urn:cyberalchemy-lab:internal:package-archive:v2-candidate', package)
            raw = encoded(package)
            require(len(raw) <= min(MAX_BYTES, contract['maximum_package_bytes']), 'complete encoded package byte budget')
            return raw
        finally:
            self.guard()

    def verify_archive(self, raw, expected_binding):
        self.bound(expected_binding, raw)
        package = self.closed('archive', raw)
        materials = []
        for row in package['materials']:
            original = base64.b64decode(row['original_bytes_b64'], validate=True)
            require(base64.b64encode(original).decode() == row['original_bytes_b64'], 'noncanonical original encoding')
            materials.append(Material(encoded(row['binding']), original, encoded(row['dependencies']),
                None if row['artifact'] is None else encoded(row['artifact']), row['encoding']))
        contract = base64.b64decode(package['export_contract_bytes_b64'], validate=True)
        review = base64.b64decode(package['privacy_review_bytes_b64'], validate=True)
        c = self.closed('export-contract', contract)
        dependencies = self.closure(self.graph(tuple(materials)), package['artifact_refs'], package['source_admission_basis'])
        actor = {'principal_ref': 'internal:pure-archive-verification', 'role_assignment_refs': [],
                 'agent_instance_ref': None, 'session_ref': None, 'assignment_ref': None}
        request = {'schema_version': 'lab-package-export-request/v1-candidate', 'request_ref': 'internal:archive-check',
            'actor': actor, 'source_cut': package['source_cut'], 'artifact_refs': package['artifact_refs'],
            'dependency_bindings': dependencies, 'export_contract_binding': package['export_contract_binding'],
            'privacy_review_binding': package['privacy_review_binding'], 'include_private_credentials': False,
            'include_session_memory': False, 'authority_effect': 'none'}
        facts = ExportFacts(encoded(actor), encoded(package['source_cut']), encoded(package['export_contract_binding']),
                            encoded(package['privacy_review_binding']), tuple(materials))
        rebuilt = parse(self.export(encoded(request), facts, contract, review))
        require(rebuilt == package and c['source_posture'] == package['source_posture'], 'archive metadata or complete closure differs')
        return copy.deepcopy(package)

    def account_import(self, request_raw, facts, package_raw, mapping_raw, disposition_raw):
        self.guard()
        try:
            require(type(facts) is ImportFacts, 'host-selected import facts required')
            request = parse(request_raw)
            self.valid('urn:cyberalchemy-lab:protocol:package-import-request:v1-candidate', request)
            require(request['actor'] == parse(facts.actor_json) and request['target_base_cut'] == parse(facts.target_cut_json),
                    'import Actor or target cut differs')
            for key, original in [('source_package_binding', facts.package_binding_json), ('mapping_binding', facts.mapping_binding_json),
                ('disposition_binding', facts.disposition_binding_json), ('candidate_workspace_binding', facts.workspace_binding_json)]:
                require(request[key] == parse(original), 'independent import control differs')
            package = self.verify_archive(package_raw, request['source_package_binding'])
            require(request['source_admission_basis'] == package['source_admission_basis'], 'source provenance basis differs')
            self.bound(request['mapping_binding'], mapping_raw)
            self.bound(request['disposition_binding'], disposition_raw)
            mapping = self.closed('mapping', mapping_raw)
            dispositions = self.closed('disposition', disposition_raw)
            for selected in (mapping, dispositions):
                require(selected['source_package_binding'] == request['source_package_binding']
                    and selected['target_base_cut'] == request['target_base_cut'], 'import controls select another package or cut')
            artifacts = [row for row in package['materials'] if row['artifact'] is not None]
            require([row['source'] for row in mapping['items']] == [row['artifact'] for row in artifacts]
                == [row['source'] for row in dispositions['items']], 'complete ordered source accounting differs')
            target_ids, result = set(), []
            for source, mapped, disposition in zip(artifacts, mapping['items'], dispositions['items']):
                mode = disposition['disposition']
                target, target_raw = mapped['target'], None
                if mode in ('import-exact', 'adapt'):
                    require(target is not None and mapped['target_bytes_b64'] is not None, 'materialized target required')
                    self.valid(COMMON + '#/$defs/candidate_artifact_ref', target)
                    target_raw = base64.b64decode(mapped['target_bytes_b64'], validate=True)
                    require(base64.b64encode(target_raw).decode() == mapped['target_bytes_b64'], 'noncanonical target encoding')
                    require(sha(target_raw) == target['byte_sha256'], 'target byte hash differs')
                    target_body = parse(target_raw)
                    privacy(target_body)
                    require(target['scope_ref'] == facts.target_scope_ref and target_body.get('node_id') == target['identity_ref'],
                            'target scope or body identity differs')
                    require(target['identity_ref'] not in target_ids and target['identity_ref'] not in facts.existing_identity_refs,
                            'target identity collides; revision needs its own represented preimage')
                    target_ids.add(target['identity_ref'])
                    original = base64.b64decode(source['original_bytes_b64'], validate=True)
                    require((mode == 'import-exact' and target_raw == original) or (mode == 'adapt' and target_raw != original),
                            'disposition does not describe exact target bytes')
                else:
                    require(target is None and mapped['target_bytes_b64'] is None, 'retained/excluded source must not hide a target')
                result.append({'source': source['artifact'], 'source_binding': source['binding'], 'disposition': mode,
                    'reason': disposition['reason'], 'target': target, 'target_bytes_b64': mapped['target_bytes_b64']})
            require(any(row['target'] is not None for row in result), 'candidate import requires a materialized target')
            plan = {'source_package_binding': request['source_package_binding'], 'source_cut': package['source_cut'],
                'target_base_cut': request['target_base_cut'], 'source_admission_basis': package['source_admission_basis'],
                'items': result, 'accounted_source_artifacts': len(result), 'source_retirement': False,
                'accounted_source_materials': len(package['materials']),
                'retained_dependency_bindings': [row['binding'] for row in package['materials'] if row['artifact'] is None],
                'automatic_admission': False, 'target_model_validation_pending': True, 'authority_effect': 'none'}
            require(len(encoded(plan)) <= MAX_BYTES, 'complete import plan byte budget')
            return plan
        finally:
            self.guard()
