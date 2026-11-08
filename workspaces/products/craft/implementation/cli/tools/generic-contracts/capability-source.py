"""Finite capability contract data; semantic custody stays with original owners.
Open Questions: ../../docs/GENERIC-CAPABILITIES.md#open-questions.
"""
import json


def definitions():
    def ref(n): return {'$ref': '#/$defs/' + n}
    def obj(p): return {'type': 'object', 'additionalProperties': False, 'properties': p, 'required': list(p)}
    def arr(item, maximum=128, minimum=0): return {'type': 'array', 'items': item, 'minItems': minimum, 'maxItems': maximum, 'uniqueItems': True}
    def enum(*v): return {'enum': list(v)}
    def num(lo=1, hi=1048576): return {'type': 'integer', 'minimum': lo, 'maximum': hi}
    def text(maximum=256): return {'type': 'string', 'minLength': 1, 'maxLength': maximum}
    def nullable(s): return {'oneOf': [s, {'type': 'null'}]}
    name, sha = ref('SourceName'), ref('Sha256')
    identity = {'type': 'string', 'minLength': 1, 'maxLength': 256, 'pattern': '^[^\\x00-\\x1f\\x7f]+$'}
    capabilities = enum('structured-output', 'embeddings', 'text-output', 'readonly-tools', 'local-inspect', 'remote-inspect', 'cancel-ack', 'resume', 'document-parse', 'bounded-search')
    operations = enum('text.generate', 'text.structured', 'vector.embed', 'agent.run', 'document.parse', 'search.query')
    d = {}
    d['GenericNativeVectorType'] = {'const': 'Craft.Native.FiniteVector'}
    d['GenericNativeVectorValue'] = {'type': 'array', 'minItems': 1, 'maxItems': 65536, 'items': {'type': 'number', 'minimum': -1.7976931348623157e308, 'maximum': 1.7976931348623157e308}}
    d['GenericCapabilityBounds'] = obj({'max_input_bytes': num(), 'max_output_bytes': num(), 'max_items': num(1, 4096), 'deadline_ms': num(1, 3600000), 'max_model_attempts': num(0, 128), 'max_tool_calls': num(0, 1024)})
    d['GenericCapabilityTool'] = obj({'name': name, 'entry': name, 'query': name, 'argument_codec': ref('ValueType'), 'result_codec': ref('ValueType'), 'effect': {'const': 'read-only'}})
    common = {'input_type': name, 'result_type': name, 'required_capabilities': arr(capabilities, 16, 1)}
    d['GenericCapabilityContract'] = {'oneOf': [
        obj({'kind': {'const': 'inference/v1'}, 'operation': enum('text.generate', 'text.structured', 'vector.embed'), **common, 'tools': {'const': 'disabled'}, 'embedding': nullable(obj({'dimensions': num(1, 65536), 'preprocessing_ref': name, 'space_generation': name}))}),
        obj({'kind': {'const': 'agent-run/v1'}, 'operation': {'const': 'agent.run'}, **common, 'loop_owner': {'const': 'selected-harness'}, 'tools': arr(ref('GenericCapabilityTool'), 32), 'checkpoint_version': text(64)}),
        obj({'kind': {'const': 'document/v1'}, 'operation': {'const': 'document.parse'}, **common}),
        obj({'kind': {'const': 'search/v1'}, 'operation': {'const': 'search.query'}, **common, 'search': ref('GenericBoundedSearch')})
    ]}
    d['GenericBoundedSearch'] = obj({'technique': enum('keyword', 'vector', 'hybrid'), 'collection': name, 'top_k': num(1, 100), 'max_candidates': num(1, 4096), 'filter_fields': arr(name, 32), 'filter_operators': arr(enum('eq', 'in'), 2), 'tenant_scope': {'const': 'original-owner-required'}, 'source_access': {'const': 'original-owner-required'}, 'embedding_space': nullable(name)})
    d['GenericCapabilityRealization'] = obj({
        'id': name, 'integration_binding_ref': name, 'contract': enum('inference/v1', 'agent-run/v1', 'document/v1', 'search/v1'),
        'implementation': obj({'package': text(), 'version': {'type': 'string', 'pattern': '^[0-9]+\\.[0-9]+\\.[0-9]+(?:-[A-Za-z0-9.-]+)?$', 'maxLength': 128}, 'sha256': sha, 'export': text()}),
        'operations': arr(operations, 6, 1), 'capabilities': arr(capabilities, 16, 1), 'mode': enum('fixture', 'provider'),
        'target': obj({'destination': text(2048), 'api': text(), 'model_or_harness': text(), 'revision': text(), 'mutability': enum('immutable', 'mutable-alias')}),
        'schema': obj({'dialect': {'const': 'https://json-schema.org/draft/2020-12/schema'}, 'subset': enum('checked-business-values/v1', 'finite-vector/v1')}),
        'bounds': ref('GenericCapabilityBounds'),
        'lifecycle': obj({'credential_slot_ref': nullable(name), 'compatibility': {'const': 'exact-contract-and-target'}, 'retention_policy_ref': name, 'credential_lifecycle_ref': name, 'synchronization_ref': name, 'retirement_ref': name, 'fallback': {'const': 'none'}, 'completion': {'const': 'validated-proposal-only'}, 'unknown_effect': {'const': 'reconcile-before-retry'}})
    })
    d['GenericCapabilityBinding'] = obj({'id': name, 'interface': name, 'contract': ref('GenericCapabilityContract'), 'realization_ref': name, 'bounds': ref('GenericCapabilityBounds')})
    d['GenericCapabilitySelection'] = obj({'schema_version': {'const': 'craft.generic-capability-selection/v1'}, 'source_sha256': sha, 'profile_sha256': sha,
        'kernel': obj({'path': ref('RelativePath'), 'sha256': sha}), 'bindings': arr(ref('GenericCapabilityBinding'), 128, 1), 'realizations': arr(ref('GenericCapabilityRealization'), 128, 1), 'authority_effect': {'const': 'none'}})
    d['GenericContextDependency'] = obj({'source': identity, 'revision': text(), 'content_sha256': sha, 'acl_revision': text(), 'policy_revision': text(), 'role': enum('input', 'retrieved', 'tool-result', 'conversation')})
    d['GenericSourceContextManifest'] = obj({'schema_version': {'const': 'craft.source-context-manifest/v1'}, 'tenant': identity, 'dependencies': arr(ref('GenericContextDependency'), 4096), 'context_sha256': sha, 'authority_effect': {'const': 'none'}})
    d['GenericSourceReleaseTicketData'] = obj({'schema_version': {'const': 'craft.source-release-ticket/v1'}, 'manifest_sha256': sha, 'tenant': identity, 'attempt': identity, 'fence': num(), 'output_sha256': sha, 'destination': text(2048), 'recipient': identity, 'expires_at_ms': num(1, 9007199254740991), 'use': {'const': 'single-use'}, 'authority_effect': {'const': 'none'}})
    d['GenericTrustedSearchContextData'] = obj({'schema_version': {'const': 'craft.trusted-search-context/v1'}, 'tenant': identity, 'actor': identity, 'source_scope': arr(identity, 4096), 'grants_revision': text(), 'source_policy_revision': text(), 'fence': num(), 'deadline_ms': num(1, 9007199254740991), 'origin': {'const': 'original-server-owner'}, 'authority_effect': {'const': 'none'}})
    d['GenericContinuationDecision'] = {'oneOf': [
        obj({'kind': enum('advance', 'complete'), 'result_sha256': sha}),
        obj({'kind': {'const': 'business-rejection'}, 'code': ref('FailureCode')}),
        obj({'kind': {'const': 'wait'}, 'condition': name, 'deadline_ms': num(1, 9007199254740991)}),
        obj({'kind': enum('review', 'unknown', 'cancel'), 'reason': ref('FailureCode')}),
        obj({'kind': {'const': 'retry'}, 'attempt': num(1, 128), 'maximum': num(1, 128), 'not_before_ms': num(1, 9007199254740991), 'dispatch_evidence': {'const': 'proven-not-dispatched'}})
    ]}
    return d


def materializations(root, repo, all_definitions, closure, ts):
    own = definitions()
    all_definitions.update(own)
    schema = {'$schema': 'https://json-schema.org/draft/2020-12/schema', '$id': 'craft.generic-capability-selection/v1', '$ref': '#/$defs/GenericCapabilitySelection', '$defs': closure(own), '$comment': 'Data only. No runtime custody. Open Questions: docs/GENERIC-CAPABILITIES.md#open-questions.'}
    header = '// GENERATED from Core tools/generic-contracts/capability-source.py via schema-source.py. Data grants no authority.\n// Open Questions: docs/GENERIC-CAPABILITIES.md#open-questions.\n'
    deps = 'import type {SourceNameV1,Sha256V1,RelativePathV1,FailureCodeV1,ValueTypeV1} from \'PATH\';\n'
    body = '\n'.join('export type ' + n + 'V1 = ' + ts(s) + ';' for n, s in own.items()) + '\n'
    body += "export const GENERIC_NATIVE_VECTOR_TYPE_V1 = 'Craft.Native.FiniteVector' as const;\n"
    return {root / 'contracts/generic-capability-v1.schema.json': json.dumps(schema, indent=2) + '\n',
            root / 'src/generic/capability-data-v1.ts': header + deps.replace('PATH', '../commerce/commerce-data-v1.js') + body,
            repo / 'language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/generic-capability-data-v1.ts': header + deps.replace('PATH', './commerce-data-v1.js') + body}
