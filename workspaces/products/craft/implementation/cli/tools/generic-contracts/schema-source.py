#!/usr/bin/env python3
"""Generate the separate generic computation data contract and Alch mirror.

Default checks exact bytes; --write materializes only these generic outputs.
Open Questions: ../../docs/GENERIC-APPLICATIONS.md#open-questions.
"""
from pathlib import Path
import argparse
import copy
import json
import runpy

ROOT = Path(__file__).resolve().parents[2]
REPO = ROOT.parents[4]
PREDECESSOR = ROOT / 'tools/commerce-contracts/schema-source.py'
legacy = runpy.run_path(str(PREDECESSOR))
original = legacy['D']
RENAMES = {name: 'Generic' + name for name in (
    'Expr', 'PolicyAction', 'RecordDefinition', 'ValueSchema',
    'PureDeclaration', 'ComputationContract',
)}


def rewrite(value):
    if isinstance(value, list):
        return [rewrite(x) for x in value]
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            if key == '$ref':
                parts = item.split('/')
                assert parts[:2] == ['#', '$defs']
                parts[2] = RENAMES.get(parts[2], parts[2])
                result[key] = '/'.join(parts)
            else:
                result[key] = rewrite(item)
        return result
    return value


def ref(name):
    return {'$ref': '#/$defs/' + name}


def obj(properties):
    return {'type': 'object', 'additionalProperties': False,
            'properties': properties, 'required': list(properties)}


def arr(items, maximum=256):
    return {'type': 'array', 'items': items, 'minItems': 0, 'maxItems': maximum}


D = copy.deepcopy(original)
for old, new in RENAMES.items():
    D[new] = rewrite(original[old])
E = ref('GenericExpr')
list_type = next(x for x in original['ValueType']['oneOf'] if x['properties']['kind'] == {'const': 'list'})
D['GenericExpr']['oneOf'].append(obj({'op': {'const': 'append'}, 'source': E, 'item': E, 'list_type': copy.deepcopy(list_type)}))
D['GenericExpr']['oneOf'].append(obj({'op': {'const': 'concat'}, 'left': E, 'right': E, 'result_type': ref('ValueType')}))
D['GenericValueSchema']['properties']['schema_version'] = {'const': 'craft.generic-values/v1-candidate'}
cp = D['GenericComputationContract']['properties']
cp['schema_version'] = {'const': 'craft.generic-computation/v1-candidate'}
cp['semantics_revision'] = {'const': 'ordered-metered-generic-v1-candidate'}
POLICIES = {
    'invariant_policy': 'reject-inexact/v1',
    'record_layout': 'canonical-fields/v1',
    'equality_policy': 'typed-structural-metered/v1',
    'append_policy': 'list-item-checkpoint-capacity/v1',
}
for key, value in POLICIES.items():
    cp[key] = {'const': value}
    D['GenericComputationContract']['required'].append(key)
D['GenericRoleExpression'] = obj({
    'result': ref('ValueType'), 'expression': E,
    'local_records': arr(ref('LocalRecordProjection'), 128),
})
R = ref('GenericRoleExpression')
D['GenericOperationAction'] = {'oneOf': [
    obj({'kind': {'const': 'return'}, 'value': R}),
    obj({'kind': {'enum': ['reject', 'fail']}, 'code': ref('FailureCode')}),
]}
A = ref('GenericOperationAction')
S = ref('GenericOperationControlStep')
D['GenericOperationPolicyEnforcement'] = copy.deepcopy(original['OperationPolicyEnforcement'])
D['GenericOperationPolicyEnforcement']['properties']['value'] = R
D['GenericOperationControlStep'] = {'oneOf': [
    ref('GenericOperationPolicyEnforcement'),
    obj({'kind': {'const': 'guard'}, 'condition': R, 'on_false': A}),
    obj({'kind': {'const': 'conditional'}, 'condition': R, 'then': arr(S), 'otherwise': arr(S)}),
    obj({'kind': {'const': 'action'}, 'action': A}),
]}
D['GenericEffectPlan'] = obj({
    'schema_version': {'const': 'craft.generic-effects/v1-candidate'},
    'operation': ref('RoleSelector'), 'service': {'type': 'null'},
    'parameters': arr(ref('Binder'), 128), 'contexts': arr(False, 0),
    'result': ref('ValueType'), 'body': arr(S), 'protocol': {'type': 'null'},
    'qualification': {'const': 'independent-source-role-contract-data-only'},
})
OWNED = tuple(RENAMES.values()) + (
    'GenericRoleExpression', 'GenericOperationAction',
    'GenericOperationControlStep', 'GenericOperationPolicyEnforcement', 'GenericEffectPlan',
)


def references(value):
    found = set()
    if isinstance(value, dict):
        for key, item in value.items():
            if key == '$ref':
                found.add(item.split('/')[2])
            else:
                found.update(references(item))
    elif isinstance(value, list):
        for item in value:
            found.update(references(item))
    return found


def closure(roots):
    names = set(roots)
    pending = list(roots)
    while pending:
        for name in references(D[pending.pop()]):
            if name not in names:
                names.add(name)
                pending.append(name)
    return {name: D[name] for name in sorted(names)}


def ts(schema, inline_records=False):
    if schema is False:
        return 'never'
    if '$ref' in schema:
        parts = schema['$ref'].split('/')
        result = parts[2] + 'V1'
        if len(parts) > 3:
            assert parts[3] == 'properties' and len(parts) == 5
            result += '[' + json.dumps(parts[4]) + ']'
        return result
    if 'const' in schema:
        value = schema['const']
        return ('readonly ' if isinstance(value, list) else '') + json.dumps(value)
    if 'enum' in schema:
        return '(' + ' | '.join(json.dumps(x) for x in schema['enum']) + ')'
    for union in ('oneOf', 'anyOf'):
        if union in schema:
            return '(' + ' | '.join(ts(x, inline_records) for x in schema[union]) + ')'
    kind = schema.get('type')
    if kind in ('string', 'boolean', 'null'):
        return kind
    if kind in ('integer', 'number'):
        return 'number'
    if kind == 'array':
        return 'readonly []' if schema.get('maxItems') == 0 else 'readonly (' + ts(schema['items'], inline_records) + ')[]'
    if kind == 'object':
        if 'properties' not in schema:
            value = ts(schema['additionalProperties'], inline_records)
            return ('{ readonly [key: string]: ' + value + ' }' if inline_records
                    else 'Readonly<Record<string,' + value + '>>')
        return '{ ' + '; '.join('readonly ' + json.dumps(k) + ('' if k in schema['required'] else '?') + ': ' + ts(v, inline_records) for k, v in schema['properties'].items()) + ' }'
    raise ValueError(schema)


def materializations():
    schema = {
        '$schema': 'https://json-schema.org/draft/2020-12/schema',
        '$id': 'craft.generic-computation/v1-candidate',
        '$ref': '#/$defs/GenericComputationContract',
        '$defs': closure(OWNED),
        '$comment': 'Generic data only. GenericValueSchema and GenericEffectPlan are separately addressable definitions; semantic admission and original owner custody remain required. Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions.',
    }
    dependencies = sorted(set().union(*(references(D[n]) for n in OWNED)) - set(OWNED))
    header = '// GENERATED from Core tools/generic-contracts/schema-source.py; data only.\n// Recursive generic expressions have separate versioned semantics; types confer no executable custody.\n// Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions.\n'
    body = '\n'.join('export type ' + name + 'V1 = ' + ts(D[name]) + ';' for name in OWNED) + '\n'
    imports = 'import type {' + ','.join(n + 'V1' for n in dependencies) + "} from 'PATH';\n"
    return {
        ROOT / 'contracts/generic-computation-v1.schema.json': json.dumps(schema, indent=2, ensure_ascii=False) + '\n',
        ROOT / 'src/generic/computation-data-v1.ts': header + imports.replace('PATH', '../commerce/commerce-data-v1.js') + body,
        REPO / 'language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/generic-computation-data-v1.ts': header + imports.replace('PATH', './commerce-data-v1.js') + body,
    }


# C07 separate data contract. Reviewed data004 is the design provenance; this
# generator owns the executable schema source and has no candidate-file dependency.
KEYED_DEFINITIONS = json.loads(r'''{
  "GenericKeyedRoleExpression": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "result": {
        "$ref": "#/$defs/ValueType"
      },
      "expression": {
        "$ref": "#/$defs/GenericExpr"
      },
      "local_records": {
        "type": "array",
        "items": false,
        "minItems": 0,
        "maxItems": 0
      }
    },
    "required": [
      "result",
      "expression",
      "local_records"
    ]
  },
  "GenericContextSlot": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "id": {
        "$ref": "#/$defs/PropertyName"
      },
      "binding": {
        "$ref": "#/$defs/PropertyName"
      },
      "source_type": {
        "$ref": "#/$defs/SourceName"
      },
      "abi": {
        "const": "craft.generic-auth-customer-context/v1-candidate"
      },
      "property": {
        "enum": [
          "customerId",
          "currentActionAllowed"
        ]
      },
      "type": {
        "$ref": "#/$defs/ValueType"
      },
      "expression_path": {
        "type": "string",
        "minLength": 1,
        "maxLength": 2048
      },
      "origin": {
        "enum": [
          "final-ready-authenticated-subject",
          "final-ready-current-action"
        ]
      }
    },
    "required": [
      "id",
      "binding",
      "source_type",
      "abi",
      "property",
      "type",
      "expression_path",
      "origin"
    ]
  },
  "GenericContextRequirement": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "binding": {
        "$ref": "#/$defs/PropertyName"
      },
      "source_type": {
        "const": "Craft.Generated.Auth.CustomerContext"
      },
      "abi": {
        "const": "craft.generic-auth-customer-context/v1-candidate"
      }
    },
    "required": [
      "binding",
      "source_type",
      "abi"
    ]
  },
  "GenericTerminalAction": {
    "oneOf": [
      {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "kind": {
            "const": "return"
          },
          "value": {
            "$ref": "#/$defs/GenericKeyedRoleExpression"
          }
        },
        "required": [
          "kind",
          "value"
        ]
      },
      {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "kind": {
            "enum": [
              "reject",
              "fail"
            ]
          },
          "code": {
            "$ref": "#/$defs/FailureCode"
          }
        },
        "required": [
          "kind",
          "code"
        ]
      }
    ]
  },
  "GenericCallArgument": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "parameter": {
        "$ref": "#/$defs/PropertyName"
      },
      "value": {
        "$ref": "#/$defs/GenericKeyedRoleExpression"
      }
    },
    "required": [
      "parameter",
      "value"
    ]
  },
  "GenericLocalOperationCall": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "target": {
        "$ref": "#/$defs/SourceName"
      },
      "source_callsite": {
        "type": "string",
        "minLength": 1,
        "maxLength": 2048
      },
      "target_contract_sha256": {
        "$ref": "#/$defs/Sha256"
      },
      "arguments": {
        "type": "array",
        "items": {
          "$ref": "#/$defs/GenericCallArgument"
        },
        "minItems": 0,
        "maxItems": 128
      },
      "authorization": {
        "const": "original-local-context-forwarding-required"
      }
    },
    "required": [
      "target",
      "source_callsite",
      "target_contract_sha256",
      "arguments",
      "authorization"
    ]
  },
  "GenericProtectedQueryCall": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "entry": {
        "$ref": "#/$defs/SourceName"
      },
      "query": {
        "$ref": "#/$defs/SourceName"
      },
      "source_callsite": {
        "type": "string",
        "minLength": 1,
        "maxLength": 2048
      },
      "arguments": {
        "type": "array",
        "items": {
          "$ref": "#/$defs/GenericCallArgument"
        },
        "minItems": 0,
        "maxItems": 128
      },
      "authorization": {
        "const": "fresh-original-entry-decision-required"
      }
    },
    "required": [
      "entry",
      "query",
      "source_callsite",
      "arguments",
      "authorization"
    ]
  },
  "GenericReadonlyAction": {
    "oneOf": [
      {
        "$ref": "#/$defs/GenericTerminalAction"
      },
      {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "kind": {
            "const": "invoke-return-local"
          },
          "call": {
            "$ref": "#/$defs/GenericLocalOperationCall"
          }
        },
        "required": [
          "kind",
          "call"
        ]
      }
    ]
  },
  "GenericReadonlyStep": {
    "oneOf": [
      {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "kind": {
            "const": "guard"
          },
          "condition": {
            "$ref": "#/$defs/GenericKeyedRoleExpression"
          },
          "on_false": {
            "$ref": "#/$defs/GenericTerminalAction"
          }
        },
        "required": [
          "kind",
          "condition",
          "on_false"
        ]
      },
      {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "kind": {
            "const": "conditional"
          },
          "condition": {
            "$ref": "#/$defs/GenericKeyedRoleExpression"
          },
          "then": {
            "type": "array",
            "items": {
              "$ref": "#/$defs/GenericReadonlyStep"
            },
            "minItems": 0,
            "maxItems": 256
          },
          "otherwise": {
            "type": "array",
            "items": {
              "$ref": "#/$defs/GenericReadonlyStep"
            },
            "minItems": 0,
            "maxItems": 256
          }
        },
        "required": [
          "kind",
          "condition",
          "then",
          "otherwise"
        ]
      },
      {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "kind": {
            "const": "read-entry"
          },
          "binding": {
            "$ref": "#/$defs/PropertyName"
          },
          "type": {
            "$ref": "#/$defs/ValueType"
          },
          "call": {
            "$ref": "#/$defs/GenericProtectedQueryCall"
          },
          "on_missing": {
            "$ref": "#/$defs/GenericTerminalAction"
          },
          "on_unavailable": {
            "$ref": "#/$defs/GenericTerminalAction"
          }
        },
        "required": [
          "kind",
          "binding",
          "type",
          "call",
          "on_missing",
          "on_unavailable"
        ]
      },
      {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "kind": {
            "const": "action"
          },
          "action": {
            "$ref": "#/$defs/GenericReadonlyAction"
          }
        },
        "required": [
          "kind",
          "action"
        ]
      }
    ]
  },
  "GenericReadonlyControl": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "schema_version": {
        "const": "craft.generic-readonly-control/v1-candidate"
      },
      "semantics_revision": {
        "const": "keyed-query-entry/v1-candidate"
      },
      "operation": {
        "$ref": "#/$defs/SourceName"
      },
      "service": {
        "$ref": "#/$defs/SourceName"
      },
      "parameters": {
        "type": "array",
        "items": {
          "$ref": "#/$defs/Binder"
        },
        "minItems": 0,
        "maxItems": 128
      },
      "contexts": {
        "type": "array",
        "items": {
          "$ref": "#/$defs/GenericContextRequirement"
        },
        "minItems": 0,
        "maxItems": 1
      },
      "context_slots": {
        "type": "array",
        "items": {
          "$ref": "#/$defs/GenericContextSlot"
        },
        "minItems": 0,
        "maxItems": 256
      },
      "result": {
        "$ref": "#/$defs/ValueType"
      },
      "body": {
        "type": "array",
        "items": {
          "$ref": "#/$defs/GenericReadonlyStep"
        },
        "minItems": 0,
        "maxItems": 256
      },
      "limits": {
        "$ref": "#/$defs/ComputationLimits"
      },
      "protocol": {
        "type": "null"
      }
    },
    "required": [
      "schema_version",
      "semantics_revision",
      "operation",
      "service",
      "parameters",
      "contexts",
      "context_slots",
      "result",
      "body",
      "limits",
      "protocol"
    ]
  },
  "GenericLookupKeyField": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "field": {
        "$ref": "#/$defs/PropertyName"
      },
      "type": {
        "$ref": "#/$defs/ValueType"
      },
      "predicate_path": {
        "type": "string",
        "minLength": 1,
        "maxLength": 2048
      },
      "origin": {
        "enum": [
          "parameter",
          "literal",
          "private-context-scalar"
        ]
      },
      "value": {
        "$ref": "#/$defs/GenericKeyedRoleExpression"
      }
    },
    "required": [
      "field",
      "type",
      "predicate_path",
      "origin",
      "value"
    ]
  },
  "GenericLookupKey": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "kind": {
        "enum": [
          "identity",
          "unique"
        ]
      },
      "index": {
        "type": "integer",
        "minimum": 0,
        "maximum": 15
      },
      "fields": {
        "type": "array",
        "items": {
          "$ref": "#/$defs/GenericLookupKeyField"
        },
        "minItems": 1,
        "maxItems": 16
      },
      "selection": {
        "const": "identity-then-declared-unique;first-supported-authored-equality"
      },
      "encoding_order": {
        "const": "declared-key-tuple"
      },
      "predicate_execution": {
        "const": "full-authored-predicate-after-decode"
      }
    },
    "required": [
      "kind",
      "index",
      "fields",
      "selection",
      "encoding_order",
      "predicate_execution"
    ]
  },
  "GenericQueryGuard": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "condition": {
        "$ref": "#/$defs/GenericKeyedRoleExpression"
      },
      "on_false": {
        "$ref": "#/$defs/GenericTerminalAction"
      }
    },
    "required": [
      "condition",
      "on_false"
    ]
  },
  "GenericKeyedQuery": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "schema_version": {
        "const": "craft.generic-keyed-query/v1-candidate"
      },
      "semantics_revision": {
        "const": "keyed-query-entry/v1-candidate"
      },
      "query": {
        "$ref": "#/$defs/SourceName"
      },
      "service": {
        "$ref": "#/$defs/SourceName"
      },
      "parameters": {
        "type": "array",
        "items": {
          "$ref": "#/$defs/Binder"
        },
        "minItems": 0,
        "maxItems": 128
      },
      "contexts": {
        "type": "array",
        "items": {
          "$ref": "#/$defs/GenericContextRequirement"
        },
        "minItems": 0,
        "maxItems": 1
      },
      "context_slots": {
        "type": "array",
        "items": {
          "$ref": "#/$defs/GenericContextSlot"
        },
        "minItems": 0,
        "maxItems": 256
      },
      "source": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "binding": {
            "$ref": "#/$defs/PropertyName"
          },
          "entity": {
            "$ref": "#/$defs/SourceName"
          }
        },
        "required": [
          "binding",
          "entity"
        ]
      },
      "result": {
        "$ref": "#/$defs/ValueType"
      },
      "key": {
        "$ref": "#/$defs/GenericLookupKey"
      },
      "predicate": {
        "$ref": "#/$defs/GenericKeyedRoleExpression"
      },
      "guards": {
        "type": "array",
        "items": {
          "$ref": "#/$defs/GenericQueryGuard"
        },
        "minItems": 0,
        "maxItems": 256
      },
      "projection": {
        "$ref": "#/$defs/GenericKeyedRoleExpression"
      },
      "on_missing": {
        "$ref": "#/$defs/GenericTerminalAction"
      },
      "on_unavailable": {
        "$ref": "#/$defs/GenericTerminalAction"
      },
      "limits": {
        "$ref": "#/$defs/ComputationLimits"
      }
    },
    "required": [
      "schema_version",
      "semantics_revision",
      "query",
      "service",
      "parameters",
      "contexts",
      "context_slots",
      "source",
      "result",
      "key",
      "predicate",
      "guards",
      "projection",
      "on_missing",
      "on_unavailable",
      "limits"
    ]
  },
  "GenericLogicalEntry": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "schema_version": {
        "const": "craft.generic-logical-entry/v1-candidate"
      },
      "entry": {
        "$ref": "#/$defs/SourceName"
      },
      "target": {
        "$ref": "#/$defs/SourceName"
      },
      "target_role": {
        "enum": [
          "Query",
          "Operation"
        ]
      },
      "service": {
        "$ref": "#/$defs/SourceName"
      },
      "interaction": {
        "const": "request-response"
      },
      "parameters": {
        "type": "array",
        "items": {
          "$ref": "#/$defs/Binder"
        },
        "minItems": 0,
        "maxItems": 128
      },
      "result": {
        "$ref": "#/$defs/ValueType"
      },
      "access": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "principal_kind": {
            "const": "customer"
          },
          "caller": {
            "const": "self"
          },
          "permission": {
            "type": "string",
            "minLength": 1,
            "maxLength": 256
          },
          "resource": {
            "type": "string",
            "minLength": 1,
            "maxLength": 256
          },
          "action": {
            "type": "string",
            "minLength": 1,
            "maxLength": 256
          },
          "scope": {
            "type": "string",
            "minLength": 1,
            "maxLength": 256
          },
          "route": {
            "type": "string",
            "minLength": 1,
            "maxLength": 256
          },
          "context_type": {
            "const": "Craft.Generated.Auth.CustomerContext"
          },
          "context_abi": {
            "const": "craft.generic-auth-customer-context/v1-candidate"
          },
          "native_abi": {
            "const": "craft.commerce-auth-ready-bridge/v1-candidate"
          },
          "native_asset": {
            "const": "auth-foundation-ready"
          },
          "current_action": {
            "const": "final-ready-before-protected-read"
          }
        },
        "required": [
          "principal_kind",
          "caller",
          "permission",
          "resource",
          "action",
          "scope",
          "route",
          "context_type",
          "context_abi",
          "native_abi",
          "native_asset",
          "current_action"
        ]
      }
    },
    "required": [
      "schema_version",
      "entry",
      "target",
      "target_role",
      "service",
      "interaction",
      "parameters",
      "result",
      "access"
    ]
  },
  "GenericKeyedService": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "id": {
        "$ref": "#/$defs/SourceName"
      },
      "module": {
        "$ref": "#/$defs/SourceName"
      }
    },
    "required": [
      "id",
      "module"
    ]
  },
  "GenericKeyedApplicationContract": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "schema_version": {
        "const": "craft.generic-keyed-application/v1-candidate"
      },
      "semantics_revision": {
        "const": "keyed-query-entry/v1-candidate"
      },
      "admission_mode": {
        "const": "keyed-query-entry"
      },
      "source_node": {
        "$ref": "#/$defs/SourceName"
      },
      "values": {
        "$ref": "#/$defs/GenericValueSchema"
      },
      "functions": {
        "type": "array",
        "items": {
          "$ref": "#/$defs/GenericPureDeclaration"
        },
        "minItems": 0,
        "maxItems": 256
      },
      "pure_operations": {
        "type": "array",
        "items": {
          "$ref": "#/$defs/GenericEffectPlan"
        },
        "minItems": 0,
        "maxItems": 256
      },
      "queries": {
        "type": "array",
        "items": {
          "$ref": "#/$defs/GenericKeyedQuery"
        },
        "minItems": 0,
        "maxItems": 256
      },
      "readonly_operations": {
        "type": "array",
        "items": {
          "$ref": "#/$defs/GenericReadonlyControl"
        },
        "minItems": 0,
        "maxItems": 256
      },
      "entries": {
        "type": "array",
        "items": {
          "$ref": "#/$defs/GenericLogicalEntry"
        },
        "minItems": 0,
        "maxItems": 64
      },
      "services": {
        "type": "array",
        "items": {
          "$ref": "#/$defs/GenericKeyedService"
        },
        "minItems": 1,
        "maxItems": 16
      },
      "limits": {
        "$ref": "#/$defs/ComputationLimits"
      },
      "pure_semantics_revision": {
        "const": "ordered-metered-generic-v1-candidate"
      },
      "invariant_policy": {
        "const": "reject-inexact/v1"
      },
      "record_layout": {
        "const": "canonical-fields/v1"
      },
      "equality_policy": {
        "const": "typed-structural-metered/v1"
      },
      "append_policy": {
        "const": "list-item-checkpoint-capacity/v1"
      }
    },
    "required": [
      "schema_version",
      "semantics_revision",
      "admission_mode",
      "source_node",
      "values",
      "functions",
      "pure_operations",
      "queries",
      "readonly_operations",
      "entries",
      "services",
      "limits",
      "pure_semantics_revision",
      "invariant_policy",
      "record_layout",
      "equality_policy",
      "append_policy"
    ]
  },
  "GenericKeyedQueryProfile": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "schema_version": {
        "const": "craft.generic-keyed-query-profile/v1-candidate"
      },
      "id": {
        "type": "string",
        "pattern": "^[a-z][a-z0-9-]{0,63}$"
      },
      "target": {
        "const": "node-esm"
      },
      "capabilities": {
        "const": [
          "Rule",
          "record-bool",
          "Operation",
          "Mapping",
          "record-uint64",
          "Calculation",
          "Policy",
          "bounded-values",
          "bounded-collections",
          "StateMachine",
          "Entity",
          "Query",
          "Entry",
          "keyed-sqlite-read",
          "auth-foundation-ready"
        ]
      },
      "limits": {
        "$ref": "#/$defs/ComputationLimits"
      },
      "services": {
        "type": "array",
        "items": {
          "$ref": "#/$defs/GenericKeyedService"
        },
        "minItems": 1,
        "maxItems": 16
      },
      "entry_context": {
        "const": "customer-ready-scalars/v1-candidate"
      },
      "auth_abi": {
        "const": "craft.commerce-auth-ready-bridge/v1-candidate"
      },
      "auth_route_template": {
        "const": "commerce:{logical_entry_id}"
      },
      "storage": {
        "const": "sqlite-keyed-canonical-values/v1-candidate"
      }
    },
    "required": [
      "schema_version",
      "id",
      "target",
      "capabilities",
      "limits",
      "services",
      "entry_context",
      "auth_abi",
      "auth_route_template",
      "storage"
    ]
  },
  "GenericSqlResultColumn": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "name": {
        "type": "string",
        "minLength": 1,
        "maxLength": 2048
      },
      "sql_name": {
        "type": "string",
        "minLength": 1,
        "maxLength": 2048
      },
      "representation": {
        "enum": [
          "text",
          "blob"
        ]
      },
      "nullable": {
        "type": "boolean"
      },
      "role": {
        "enum": [
          "field",
          "canonical-row",
          "key"
        ]
      },
      "type_alias": {
        "type": "string",
        "minLength": 1,
        "maxLength": 2048
      },
      "length_alias": {
        "type": "string",
        "minLength": 1,
        "maxLength": 2048
      },
      "payload_alias": {
        "type": "string",
        "minLength": 1,
        "maxLength": 2048
      },
      "max_bytes": {
        "type": "integer",
        "minimum": 1,
        "maximum": 524288
      }
    },
    "required": [
      "name",
      "sql_name",
      "representation",
      "nullable",
      "role",
      "type_alias",
      "length_alias",
      "payload_alias",
      "max_bytes"
    ]
  },
  "GenericSqlMaterialization": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "schema_version": {
        "const": "craft.generic-sql-materialization/v1-candidate"
      },
      "query": {
        "$ref": "#/$defs/SourceName"
      },
      "entity": {
        "$ref": "#/$defs/SourceName"
      },
      "service": {
        "$ref": "#/$defs/SourceName"
      },
      "selected_key_index": {
        "type": "integer",
        "minimum": 0,
        "maximum": 15
      },
      "sql": {
        "type": "string",
        "minLength": 1,
        "maxLength": 1048576
      },
      "sql_sha256": {
        "$ref": "#/$defs/Sha256"
      },
      "columns": {
        "type": "array",
        "items": {
          "$ref": "#/$defs/GenericSqlResultColumn"
        },
        "minItems": 1,
        "maxItems": 81
      },
      "database_encoding": {
        "const": "UTF-8"
      },
      "rows_max": {
        "const": 2
      },
      "value_bytes_max": {
        "type": "integer",
        "minimum": 1,
        "maximum": 524288
      },
      "data_bytes_max": {
        "type": "integer",
        "minimum": 1,
        "maximum": 524288
      },
      "aggregate_bytes_max": {
        "type": "integer",
        "minimum": 1,
        "maximum": 9437184
      },
      "shape_alias": {
        "const": "m_shape"
      },
      "bound_alias": {
        "const": "m_bound"
      },
      "guard": {
        "const": "whole-row-case-before-js-materialization/v1"
      },
      "length_measure": {
        "const": "octet_length-utf8/v1"
      }
    },
    "required": [
      "schema_version",
      "query",
      "entity",
      "service",
      "selected_key_index",
      "sql",
      "sql_sha256",
      "columns",
      "database_encoding",
      "rows_max",
      "value_bytes_max",
      "data_bytes_max",
      "aggregate_bytes_max",
      "shape_alias",
      "bound_alias",
      "guard",
      "length_measure"
    ]
  },
  "GenericWireValue": {
    "oneOf": [
      {
        "type": "null"
      },
      {
        "type": "boolean"
      },
      {
        "type": "string"
      },
      {
        "type": "array",
        "items": {
          "$ref": "#/$defs/GenericWireValue"
        },
        "minItems": 0,
        "maxItems": 1048576
      },
      {
        "type": "object",
        "additionalProperties": {
          "$ref": "#/$defs/GenericWireValue"
        }
      }
    ]
  },
  "GenericEntryOutcome": {
    "oneOf": [
      {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "kind": {
            "const": "Returned"
          },
          "value": {
            "$ref": "#/$defs/GenericWireValue"
          }
        },
        "required": [
          "kind",
          "value"
        ]
      },
      {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "kind": {
            "enum": [
              "Rejected",
              "Failed"
            ]
          },
          "code": {
            "$ref": "#/$defs/FailureCode"
          }
        },
        "required": [
          "kind",
          "code"
        ]
      }
    ]
  },
  "GenericAuthFault": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "code": {
        "enum": [
          "AuthenticationRequired",
          "PermissionDenied",
          "AuthorizationUnavailable"
        ]
      },
      "entry": {
        "$ref": "#/$defs/SourceName"
      },
      "phase": {
        "enum": [
          "initial-auth",
          "final-auth",
          "child-auth"
        ]
      }
    },
    "required": [
      "code",
      "entry",
      "phase"
    ]
  },
  "GenericStorageFault": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "code": {
        "const": "StorageDataInvalid"
      },
      "site": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "entity": {
            "$ref": "#/$defs/SourceName"
          },
          "query": {
            "$ref": "#/$defs/SourceName"
          },
          "path": {
            "type": "string",
            "minLength": 1,
            "maxLength": 2048
          }
        },
        "required": [
          "entity",
          "query",
          "path"
        ]
      },
      "cause": {
        "oneOf": [
          {
            "$ref": "#/$defs/ExpressionFailure"
          },
          {
            "type": "object",
            "additionalProperties": false,
            "properties": {
              "code": {
                "enum": [
                  "PhysicalShape",
                  "CanonicalMismatch",
                  "Cardinality"
                ]
              },
              "path": {
                "type": "string",
                "minLength": 1,
                "maxLength": 2048
              }
            },
            "required": [
              "code",
              "path"
            ]
          }
        ]
      }
    },
    "required": [
      "code",
      "site",
      "cause"
    ]
  },
  "GenericEntryResult": {
    "oneOf": [
      {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "ok": {
            "const": true
          },
          "outcome": {
            "$ref": "#/$defs/GenericEntryOutcome"
          },
          "fuel_used": {
            "type": "integer",
            "minimum": 0,
            "maximum": 2147483647
          }
        },
        "required": [
          "ok",
          "outcome",
          "fuel_used"
        ]
      },
      {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "ok": {
            "const": false
          },
          "error": {
            "oneOf": [
              {
                "$ref": "#/$defs/ExpressionFailure"
              },
              {
                "$ref": "#/$defs/GenericAuthFault"
              },
              {
                "$ref": "#/$defs/GenericStorageFault"
              }
            ]
          },
          "fuel_used": {
            "type": "integer",
            "minimum": 0,
            "maximum": 2147483647
          }
        },
        "required": [
          "ok",
          "error",
          "fuel_used"
        ]
      }
    ]
  },
  "GenericNativeBuildFile": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "path": {
        "$ref": "#/$defs/RelativePath"
      },
      "sha256": {
        "$ref": "#/$defs/Sha256"
      },
      "bytes": {
        "type": "integer",
        "minimum": 0,
        "maximum": 1073741824
      },
      "mode": {
        "type": "integer",
        "minimum": 0,
        "maximum": 4095
      }
    },
    "required": [
      "path",
      "sha256",
      "bytes",
      "mode"
    ]
  },
  "GenericNativeBuildInput": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "schema_version": {
        "const": "craft.generic-auth-native-build-input/v1-candidate"
      },
      "entry_manifest": {
        "const": "auth-foundation/implementation/commerce-auth-ready-bridge-v1/Cargo.toml"
      },
      "package": {
        "const": "auth-foundation-commerce-auth-ready-bridge-v1"
      },
      "profile": {
        "const": "release"
      },
      "offline": {
        "const": true
      },
      "locked": {
        "const": true
      },
      "target_platform": {
        "const": "linux-x64-glibc-2.43"
      },
      "native_abi": {
        "const": "craft.commerce-auth-ready-bridge/v1-candidate"
      },
      "auth_route_template": {
        "const": "commerce:{logical_entry_id}"
      },
      "files": {
        "type": "array",
        "items": {
          "$ref": "#/$defs/GenericNativeBuildFile"
        },
        "minItems": 1,
        "maxItems": 65536
      },
      "local_manifests": {
        "type": "array",
        "items": {
          "$ref": "#/$defs/RelativePath"
        },
        "minItems": 1,
        "maxItems": 256
      },
      "cargo_locks": {
        "type": "array",
        "items": {
          "$ref": "#/$defs/RelativePath"
        },
        "minItems": 1,
        "maxItems": 256
      },
      "dependency_metadata_sha256": {
        "$ref": "#/$defs/Sha256"
      },
      "include_closure_sha256": {
        "$ref": "#/$defs/Sha256"
      },
      "toolchain_receipt_sha256": {
        "$ref": "#/$defs/Sha256"
      },
      "repository_launcher_sha256": {
        "$ref": "#/$defs/Sha256"
      },
      "binary": {
        "const": "craft-commerce-auth-ready-bridge-v1"
      },
      "source_tree": {
        "const": "repo"
      },
      "dependency_metadata_file": {
        "const": "native-metadata.json"
      },
      "toolchain_receipt_file": {
        "const": "native-toolchain.json"
      }
    },
    "required": [
      "schema_version",
      "entry_manifest",
      "package",
      "profile",
      "offline",
      "locked",
      "target_platform",
      "native_abi",
      "auth_route_template",
      "files",
      "local_manifests",
      "cargo_locks",
      "dependency_metadata_sha256",
      "include_closure_sha256",
      "toolchain_receipt_sha256",
      "repository_launcher_sha256",
      "binary",
      "source_tree",
      "dependency_metadata_file",
      "toolchain_receipt_file"
    ]
  },
  "GenericFixtureRows": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "schema_version": {
        "const": "craft.generic-fixture-rows/v1-candidate"
      },
      "rows": {
        "type": "array",
        "items": {
          "type": "object",
          "additionalProperties": false,
          "properties": {
            "entity": {
              "$ref": "#/$defs/SourceName"
            },
            "value": {
              "$ref": "#/$defs/GenericWireValue"
            }
          },
          "required": [
            "entity",
            "value"
          ]
        },
        "maxItems": 100,
        "minItems": 0
      }
    },
    "required": [
      "schema_version",
      "rows"
    ]
  },
  "GenericNativeTool": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "name": {
        "enum": [
          "cargo",
          "rustc",
          "cc",
          "ld"
        ]
      },
      "path": {
        "type": "string",
        "minLength": 1,
        "maxLength": 4096
      },
      "sha256": {
        "$ref": "#/$defs/Sha256"
      },
      "version": {
        "type": "string",
        "minLength": 1,
        "maxLength": 4096
      }
    },
    "required": [
      "name",
      "path",
      "sha256",
      "version"
    ]
  },
  "GenericNativeToolchainReceipt": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "schema_version": {
        "const": "craft.generic-auth-toolchain/v1-candidate"
      },
      "platform": {
        "const": "linux-x64-glibc-2.43"
      },
      "host_target": {
        "const": "x86_64-unknown-linux-gnu"
      },
      "launcher": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "path": {
            "const": "tools/toolchain/run"
          },
          "sha256": {
            "$ref": "#/$defs/Sha256"
          }
        },
        "required": [
          "path",
          "sha256"
        ]
      },
      "tools": {
        "type": "array",
        "items": {
          "$ref": "#/$defs/GenericNativeTool"
        },
        "maxItems": 4,
        "minItems": 4
      }
    },
    "required": [
      "schema_version",
      "platform",
      "host_target",
      "launcher",
      "tools"
    ]
  }
}''')
KEYED_OWNED = tuple(KEYED_DEFINITIONS)
assert not set(KEYED_OWNED).intersection(D)
D.update(KEYED_DEFINITIONS)


def keyed_materializations():
    schema = {
        '$schema': 'https://json-schema.org/draft/2020-12/schema',
        '$id': 'craft.generic-keyed-query/v1-candidate',
        '$ref': '#/$defs/GenericKeyedApplicationContract',
        '$defs': closure(KEYED_OWNED),
        '$comment': 'Keyed application, Query, logical Entry, readonly control, profile, SQL, fixture and native build data only. Independently reconstructed source, typed semantics and original runtime custody remain required. Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions.',
    }
    dependencies = sorted(set().union(*(references(D[n]) for n in KEYED_OWNED)) - set(KEYED_OWNED))
    generic_dependencies = [n for n in dependencies if n in OWNED]
    legacy_dependencies = [n for n in dependencies if n not in OWNED]
    header = '// GENERATED from Core tools/generic-contracts/schema-source.py; data only.\n// Closed keyed-query data does not confer source, Auth, storage or invocation custody.\n// Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions.\n'
    body = '\n'.join('export type ' + name + 'V1 = ' + ts(D[name], inline_records=True) + ';' for name in KEYED_OWNED) + '\n'
    def imports(generic_path, legacy_path):
        parts = []
        for names, source in [(generic_dependencies, generic_path), (legacy_dependencies, legacy_path)]:
            if names:
                parts.append('import type {' + ','.join(n + 'V1' for n in names) + "} from '" + source + "';\n")
        return ''.join(parts)
    return {
        ROOT / 'contracts/generic-keyed-query-v1.schema.json': json.dumps(schema, indent=2, ensure_ascii=False) + '\n',
        ROOT / 'src/generic/query-data-v1.ts': header + imports('./computation-data-v1.js', '../commerce/commerce-data-v1.js') + body,
        REPO / 'language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/generic-query-data-v1.ts': header + imports('./generic-computation-data-v1.js', './commerce-data-v1.js') + body,
    }


TRANSACTION_DEFINITIONS = json.loads('{\n  "GenericTransactionBounds": {\n    "type": "object",\n    "additionalProperties": false,\n    "properties": {\n      "schema_version": {\n        "const": "craft.generic-transaction-bounds/v1-candidate"\n      },\n      "max_participants": {\n        "type": "integer",\n        "minimum": 1,\n        "maximum": 16\n      },\n      "max_read_observations": {\n        "type": "integer",\n        "minimum": 1,\n        "maximum": 128\n      },\n      "max_mutations": {\n        "type": "integer",\n        "minimum": 1,\n        "maximum": 128\n      },\n      "max_control_depth": {\n        "type": "integer",\n        "minimum": 1,\n        "maximum": 64\n      },\n      "max_command_key_bytes": {\n        "type": "integer",\n        "minimum": 1,\n        "maximum": 128\n      },\n      "max_command_key_scalars": {\n        "type": "integer",\n        "minimum": 1,\n        "maximum": 128\n      },\n      "max_command_tuple_bytes": {\n        "type": "integer",\n        "minimum": 1,\n        "maximum": 4096\n      },\n      "max_command_records": {\n        "type": "integer",\n        "minimum": 1,\n        "maximum": 1024\n      },\n      "max_command_journal_bytes": {\n        "type": "integer",\n        "minimum": 1,\n        "maximum": 16777216\n      },\n      "max_permission_trace_items": {\n        "type": "integer",\n        "minimum": 1,\n        "maximum": 128\n      },\n      "max_permission_trace_bytes": {\n        "type": "integer",\n        "minimum": 1,\n        "maximum": 32768\n      }\n    },\n    "required": [\n      "schema_version",\n      "max_participants",\n      "max_read_observations",\n      "max_mutations",\n      "max_control_depth",\n      "max_command_key_bytes",\n      "max_command_key_scalars",\n      "max_command_tuple_bytes",\n      "max_command_records",\n      "max_command_journal_bytes",\n      "max_permission_trace_items",\n      "max_permission_trace_bytes"\n    ]\n  },\n  "GenericCommandMetadata": {\n    "type": "object",\n    "additionalProperties": false,\n    "properties": {\n      "client_key": {\n        "type": "string",\n        "minLength": 1,\n        "maxLength": 128\n      }\n    },\n    "required": [\n      "client_key"\n    ]\n  },\n  "GenericRootCommandTuple": {\n    "type": "object",\n    "additionalProperties": false,\n    "properties": {\n      "schema_version": {\n        "const": "craft.generic-root-command/v1-candidate"\n      },\n      "application_namespace": {\n        "$ref": "#/$defs/SourceName"\n      },\n      "service": {\n        "$ref": "#/$defs/SourceName"\n      },\n      "principal": {\n        "type": "object",\n        "additionalProperties": false,\n        "properties": {\n          "kind": {\n            "const": "customer"\n          },\n          "subject": {\n            "type": "string",\n            "minLength": 1,\n            "maxLength": 256\n          },\n          "tenant": {\n            "const": null\n          }\n        },\n        "required": [\n          "kind",\n          "subject",\n          "tenant"\n        ]\n      },\n      "root_entry": {\n        "$ref": "#/$defs/SourceName"\n      },\n      "client_key": {\n        "type": "string",\n        "minLength": 1,\n        "maxLength": 128\n      }\n    },\n    "required": [\n      "schema_version",\n      "application_namespace",\n      "service",\n      "principal",\n      "root_entry",\n      "client_key"\n    ]\n  },\n  "GenericTransactionSourceFailure": {\n    "type": "object",\n    "additionalProperties": false,\n    "properties": {\n      "kind": {\n        "enum": [\n          "reject",\n          "fail"\n        ]\n      },\n      "code": {\n        "$ref": "#/$defs/FailureCode"\n      }\n    },\n    "required": [\n      "kind",\n      "code"\n    ]\n  },\n  "GenericPureLocalCall": {\n    "type": "object",\n    "additionalProperties": false,\n    "properties": {\n      "kind": {\n        "const": "call-pure-local"\n      },\n      "binding": {\n        "$ref": "#/$defs/PropertyName"\n      },\n      "target": {\n        "$ref": "#/$defs/SourceName"\n      },\n      "target_contract_sha256": {\n        "$ref": "#/$defs/Sha256"\n      },\n      "arguments": {\n        "type": "array",\n        "items": {\n          "$ref": "#/$defs/GenericCallArgument"\n        },\n        "minItems": 0,\n        "maxItems": 64\n      },\n      "result": {\n        "$ref": "#/$defs/ValueType"\n      },\n      "source_callsite": {\n        "$ref": "#/$defs/GenericTransactionSourceSite"\n      },\n      "authorization": {\n        "const": "original-local-context-forwarding-required"\n      }\n    },\n    "required": [\n      "kind",\n      "binding",\n      "target",\n      "target_contract_sha256",\n      "arguments",\n      "result",\n      "source_callsite",\n      "authorization"\n    ]\n  },\n  "GenericReadOrigin": {\n    "type": "object",\n    "additionalProperties": false,\n    "properties": {\n      "binding": {\n        "$ref": "#/$defs/PropertyName"\n      },\n      "entry": {\n        "$ref": "#/$defs/SourceName"\n      },\n      "query": {\n        "$ref": "#/$defs/SourceName"\n      },\n      "entity": {\n        "$ref": "#/$defs/SourceName"\n      },\n      "projection": {\n        "enum": [\n          "identity-row",\n          "canonical-some-identity-row"\n        ]\n      },\n      "result_type": {\n        "$ref": "#/$defs/ValueType"\n      }\n    },\n    "required": [\n      "binding",\n      "entry",\n      "query",\n      "entity",\n      "projection",\n      "result_type"\n    ]\n  },\n  "GenericStatefulPreflightStep": {\n    "oneOf": [\n      {\n        "type": "object",\n        "additionalProperties": false,\n        "properties": {\n          "kind": {\n            "const": "guard"\n          },\n          "condition": {\n            "$ref": "#/$defs/GenericKeyedRoleExpression"\n          },\n          "on_false": {\n            "$ref": "#/$defs/GenericTransactionSourceFailure"\n          }\n        },\n        "required": [\n          "kind",\n          "condition",\n          "on_false"\n        ]\n      },\n      {\n        "type": "object",\n        "additionalProperties": false,\n        "properties": {\n          "kind": {\n            "const": "conditional"\n          },\n          "condition": {\n            "$ref": "#/$defs/GenericKeyedRoleExpression"\n          },\n          "then": {\n            "type": "array",\n            "items": {\n              "$ref": "#/$defs/GenericStatefulPreflightStep"\n            },\n            "minItems": 0,\n            "maxItems": 128\n          },\n          "otherwise": {\n            "type": "array",\n            "items": {\n              "$ref": "#/$defs/GenericStatefulPreflightStep"\n            },\n            "minItems": 0,\n            "maxItems": 128\n          }\n        },\n        "required": [\n          "kind",\n          "condition",\n          "then",\n          "otherwise"\n        ]\n      },\n      {\n        "type": "object",\n        "additionalProperties": false,\n        "properties": {\n          "kind": {\n            "const": "read-entry"\n          },\n          "binding": {\n            "$ref": "#/$defs/PropertyName"\n          },\n          "type": {\n            "$ref": "#/$defs/ValueType"\n          },\n          "call": {\n            "$ref": "#/$defs/GenericProtectedQueryCall"\n          },\n          "on_missing": {\n            "$ref": "#/$defs/GenericTerminalAction"\n          },\n          "on_unavailable": {\n            "$ref": "#/$defs/GenericTerminalAction"\n          },\n          "row_origin": {\n            "oneOf": [\n              {\n                "$ref": "#/$defs/GenericReadOrigin"\n              },\n              {\n                "const": null\n              }\n            ]\n          }\n        },\n        "required": [\n          "kind",\n          "binding",\n          "type",\n          "call",\n          "on_missing",\n          "on_unavailable",\n          "row_origin"\n        ]\n      },\n      {\n        "$ref": "#/$defs/GenericPureLocalCall"\n      }\n    ]\n  },\n  "GenericTransactionStep": {\n    "oneOf": [\n      {\n        "type": "object",\n        "additionalProperties": false,\n        "properties": {\n          "kind": {\n            "const": "create"\n          },\n          "binding": {\n            "$ref": "#/$defs/PropertyName"\n          },\n          "entity": {\n            "$ref": "#/$defs/SourceName"\n          },\n          "ordered_fields": {\n            "type": "array",\n            "items": {\n              "type": "object",\n              "additionalProperties": false,\n              "properties": {\n                "name": {\n                  "$ref": "#/$defs/PropertyName"\n                },\n                "value": {\n                  "$ref": "#/$defs/GenericKeyedRoleExpression"\n                }\n              },\n              "required": [\n                "name",\n                "value"\n              ]\n            },\n            "minItems": 1,\n            "maxItems": 64\n          },\n          "source_site": {\n            "$ref": "#/$defs/GenericTransactionSourceSite"\n          }\n        },\n        "required": [\n          "kind",\n          "binding",\n          "entity",\n          "ordered_fields",\n          "source_site"\n        ]\n      },\n      {\n        "type": "object",\n        "additionalProperties": false,\n        "properties": {\n          "kind": {\n            "const": "update-observed"\n          },\n          "binding": {\n            "$ref": "#/$defs/PropertyName"\n          },\n          "entity": {\n            "$ref": "#/$defs/SourceName"\n          },\n          "origin_read_binding": {\n            "$ref": "#/$defs/PropertyName"\n          },\n          "ordered_fields": {\n            "type": "array",\n            "items": {\n              "type": "object",\n              "additionalProperties": false,\n              "properties": {\n                "name": {\n                  "$ref": "#/$defs/PropertyName"\n                },\n                "value": {\n                  "$ref": "#/$defs/GenericKeyedRoleExpression"\n                }\n              },\n              "required": [\n                "name",\n                "value"\n              ]\n            },\n            "minItems": 1,\n            "maxItems": 64\n          },\n          "source_site": {\n            "$ref": "#/$defs/GenericTransactionSourceSite"\n          }\n        },\n        "required": [\n          "kind",\n          "binding",\n          "entity",\n          "origin_read_binding",\n          "ordered_fields",\n          "source_site"\n        ]\n      },\n      {\n        "type": "object",\n        "additionalProperties": false,\n        "properties": {\n          "kind": {\n            "const": "guard"\n          },\n          "condition": {\n            "$ref": "#/$defs/GenericKeyedRoleExpression"\n          },\n          "on_false": {\n            "$ref": "#/$defs/GenericTransactionSourceFailure"\n          },\n          "source_site": {\n            "$ref": "#/$defs/GenericTransactionSourceSite"\n          }\n        },\n        "required": [\n          "kind",\n          "condition",\n          "on_false",\n          "source_site"\n        ]\n      },\n      {\n        "type": "object",\n        "additionalProperties": false,\n        "properties": {\n          "kind": {\n            "const": "let"\n          },\n          "binding": {\n            "$ref": "#/$defs/PropertyName"\n          },\n          "type": {\n            "$ref": "#/$defs/ValueType"\n          },\n          "value": {\n            "$ref": "#/$defs/GenericKeyedRoleExpression"\n          },\n          "source_site": {\n            "$ref": "#/$defs/GenericTransactionSourceSite"\n          }\n        },\n        "required": [\n          "kind",\n          "binding",\n          "type",\n          "value",\n          "source_site"\n        ]\n      },\n      {\n        "type": "object",\n        "additionalProperties": false,\n        "properties": {\n          "kind": {\n            "const": "conditional"\n          },\n          "condition": {\n            "$ref": "#/$defs/GenericKeyedRoleExpression"\n          },\n          "then": {\n            "type": "array",\n            "items": {\n              "$ref": "#/$defs/GenericTransactionStep"\n            },\n            "minItems": 0,\n            "maxItems": 128\n          },\n          "otherwise": {\n            "type": "array",\n            "items": {\n              "$ref": "#/$defs/GenericTransactionStep"\n            },\n            "minItems": 0,\n            "maxItems": 128\n          },\n          "source_site": {\n            "$ref": "#/$defs/GenericTransactionSourceSite"\n          }\n        },\n        "required": [\n          "kind",\n          "condition",\n          "then",\n          "otherwise",\n          "source_site"\n        ]\n      },\n      {\n        "type": "object",\n        "additionalProperties": false,\n        "properties": {\n          "kind": {\n            "const": "for"\n          },\n          "item": {\n            "$ref": "#/$defs/PropertyName"\n          },\n          "source": {\n            "$ref": "#/$defs/GenericKeyedRoleExpression"\n          },\n          "body": {\n            "type": "array",\n            "items": {\n              "$ref": "#/$defs/GenericTransactionStep"\n            },\n            "minItems": 0,\n            "maxItems": 128\n          },\n          "source_site": {\n            "$ref": "#/$defs/GenericTransactionSourceSite"\n          }\n        },\n        "required": [\n          "kind",\n          "item",\n          "source",\n          "body",\n          "source_site"\n        ]\n      }\n    ]\n  },\n  "GenericTransactionPlan": {\n    "type": "object",\n    "additionalProperties": false,\n    "properties": {\n      "name": {\n        "$ref": "#/$defs/PropertyName"\n      },\n      "participants": {\n        "type": "array",\n        "items": {\n          "$ref": "#/$defs/SourceName"\n        },\n        "minItems": 1,\n        "maxItems": 16\n      },\n      "body": {\n        "type": "array",\n        "items": {\n          "$ref": "#/$defs/GenericTransactionStep"\n        },\n        "minItems": 1,\n        "maxItems": 128\n      },\n      "result_expression": {\n        "$ref": "#/$defs/GenericKeyedRoleExpression"\n      },\n      "handlers": {\n        "type": "object",\n        "additionalProperties": false,\n        "properties": {\n          "on-version-conflict": {\n            "$ref": "#/$defs/GenericTransactionSourceFailure"\n          },\n          "on-unique-conflict": {\n            "$ref": "#/$defs/GenericTransactionSourceFailure"\n          },\n          "on-proven-rollback": {\n            "$ref": "#/$defs/GenericTransactionSourceFailure"\n          },\n          "on-unknown-commit": {\n            "$ref": "#/$defs/GenericTransactionSourceFailure"\n          }\n        },\n        "required": [\n          "on-version-conflict",\n          "on-unique-conflict",\n          "on-proven-rollback",\n          "on-unknown-commit"\n        ]\n      },\n      "limits": {\n        "$ref": "#/$defs/ComputationLimits"\n      },\n      "transaction_bounds": {\n        "$ref": "#/$defs/GenericTransactionBounds"\n      },\n      "defaults": {\n        "type": "array",\n        "items": false,\n        "minItems": 0,\n        "maxItems": 0\n      }\n    },\n    "required": [\n      "name",\n      "participants",\n      "body",\n      "result_expression",\n      "handlers",\n      "limits",\n      "transaction_bounds",\n      "defaults"\n    ]\n  },\n  "GenericStatefulControl": {\n    "type": "object",\n    "additionalProperties": false,\n    "properties": {\n      "schema_version": {\n        "const": "craft.generic-stateful-control/v1-candidate"\n      },\n      "semantics_revision": {\n        "const": "atomic-state-entry/v1-candidate"\n      },\n      "operation": {\n        "$ref": "#/$defs/SourceName"\n      },\n      "service": {\n        "$ref": "#/$defs/SourceName"\n      },\n      "parameters": {\n        "type": "array",\n        "items": {\n          "$ref": "#/$defs/Binder"\n        },\n        "minItems": 0,\n        "maxItems": 64\n      },\n      "contexts": {\n        "type": "array",\n        "items": {\n          "$ref": "#/$defs/GenericContextRequirement"\n        },\n        "minItems": 0,\n        "maxItems": 16\n      },\n      "context_slots": {\n        "type": "array",\n        "items": {\n          "$ref": "#/$defs/GenericContextSlot"\n        },\n        "minItems": 0,\n        "maxItems": 256\n      },\n      "result": {\n        "$ref": "#/$defs/ValueType"\n      },\n      "preflight": {\n        "type": "array",\n        "items": {\n          "$ref": "#/$defs/GenericStatefulPreflightStep"\n        },\n        "minItems": 0,\n        "maxItems": 128\n      },\n      "transaction": {\n        "$ref": "#/$defs/GenericTransactionPlan"\n      },\n      "protocol": {\n        "const": null\n      }\n    },\n    "required": [\n      "schema_version",\n      "semantics_revision",\n      "operation",\n      "service",\n      "parameters",\n      "contexts",\n      "context_slots",\n      "result",\n      "preflight",\n      "transaction",\n      "protocol"\n    ]\n  },\n  "GenericTransactionEntry": {\n    "type": "object",\n    "additionalProperties": false,\n    "properties": {\n      "schema_version": {\n        "const": "craft.generic-transaction-entry/v1-candidate"\n      },\n      "entry": {\n        "$ref": "#/$defs/SourceName"\n      },\n      "target": {\n        "$ref": "#/$defs/SourceName"\n      },\n      "target_role": {\n        "const": "Operation"\n      },\n      "service": {\n        "$ref": "#/$defs/SourceName"\n      },\n      "interaction": {\n        "const": "request-response"\n      },\n      "parameters": {\n        "type": "array",\n        "items": {\n          "$ref": "#/$defs/Binder"\n        },\n        "minItems": 0,\n        "maxItems": 128\n      },\n      "result": {\n        "$ref": "#/$defs/ValueType"\n      },\n      "access": {\n        "type": "object",\n        "additionalProperties": false,\n        "properties": {\n          "principal_kind": {\n            "const": "customer"\n          },\n          "caller": {\n            "const": "self"\n          },\n          "permission": {\n            "type": "string",\n            "minLength": 1,\n            "maxLength": 256\n          },\n          "resource": {\n            "type": "string",\n            "minLength": 1,\n            "maxLength": 256\n          },\n          "action": {\n            "type": "string",\n            "minLength": 1,\n            "maxLength": 256\n          },\n          "scope": {\n            "type": "string",\n            "minLength": 1,\n            "maxLength": 256\n          },\n          "route": {\n            "type": "string",\n            "minLength": 1,\n            "maxLength": 256\n          },\n          "context_type": {\n            "const": "Craft.Generated.Auth.CustomerContext"\n          },\n          "context_abi": {\n            "const": "craft.generic-auth-customer-context/v1-candidate"\n          },\n          "native_abi": {\n            "const": "craft.commerce-auth-ready-bridge/v1-candidate"\n          },\n          "native_asset": {\n            "const": "auth-foundation-ready"\n          },\n          "current_action": {\n            "const": "final-ready-before-command-replay-and-commit"\n          }\n        },\n        "required": [\n          "principal_kind",\n          "caller",\n          "permission",\n          "resource",\n          "action",\n          "scope",\n          "route",\n          "context_type",\n          "context_abi",\n          "native_abi",\n          "native_asset",\n          "current_action"\n        ]\n      }\n    },\n    "required": [\n      "schema_version",\n      "entry",\n      "target",\n      "target_role",\n      "service",\n      "interaction",\n      "parameters",\n      "result",\n      "access"\n    ]\n  },\n  "GenericTransactionApplicationContract": {\n    "type": "object",\n    "additionalProperties": false,\n    "properties": {\n      "schema_version": {\n        "const": "craft.generic-transaction-application/v1-candidate"\n      },\n      "semantics_revision": {\n        "const": "atomic-state-entry/v1-candidate"\n      },\n      "admission_mode": {\n        "const": "atomic-state-entry"\n      },\n      "source_node": {\n        "$ref": "#/$defs/SourceName"\n      },\n      "values": {\n        "$ref": "#/$defs/GenericValueSchema"\n      },\n      "functions": {\n        "type": "array",\n        "items": {\n          "$ref": "#/$defs/GenericPureDeclaration"\n        },\n        "minItems": 0,\n        "maxItems": 256\n      },\n      "pure_operations": {\n        "type": "array",\n        "items": {\n          "$ref": "#/$defs/GenericEffectPlan"\n        },\n        "minItems": 0,\n        "maxItems": 256\n      },\n      "queries": {\n        "type": "array",\n        "items": {\n          "$ref": "#/$defs/GenericKeyedQuery"\n        },\n        "minItems": 0,\n        "maxItems": 256\n      },\n      "readonly_operations": {\n        "type": "array",\n        "items": {\n          "$ref": "#/$defs/GenericReadonlyControl"\n        },\n        "minItems": 0,\n        "maxItems": 256\n      },\n      "entries": {\n        "type": "array",\n        "items": {\n          "oneOf": [\n            {\n              "$ref": "#/$defs/GenericLogicalEntry"\n            },\n            {\n              "$ref": "#/$defs/GenericTransactionEntry"\n            }\n          ]\n        },\n        "minItems": 0,\n        "maxItems": 256\n      },\n      "services": {\n        "type": "array",\n        "items": {\n          "$ref": "#/$defs/GenericKeyedService"\n        },\n        "minItems": 1,\n        "maxItems": 16\n      },\n      "limits": {\n        "$ref": "#/$defs/ComputationLimits"\n      },\n      "pure_semantics_revision": {\n        "const": "ordered-metered-generic-v1-candidate"\n      },\n      "invariant_policy": {\n        "const": "reject-inexact/v1"\n      },\n      "record_layout": {\n        "const": "canonical-fields/v1"\n      },\n      "equality_policy": {\n        "const": "typed-structural-metered/v1"\n      },\n      "append_policy": {\n        "const": "list-item-checkpoint-capacity/v1"\n      },\n      "application_namespace": {\n        "$ref": "#/$defs/SourceName"\n      },\n      "transaction_bounds": {\n        "$ref": "#/$defs/GenericTransactionBounds"\n      },\n      "stateful_operations": {\n        "type": "array",\n        "items": {\n          "$ref": "#/$defs/GenericStatefulControl"\n        },\n        "minItems": 1,\n        "maxItems": 256\n      }\n    },\n    "required": [\n      "schema_version",\n      "semantics_revision",\n      "admission_mode",\n      "source_node",\n      "values",\n      "functions",\n      "pure_operations",\n      "queries",\n      "readonly_operations",\n      "entries",\n      "services",\n      "limits",\n      "pure_semantics_revision",\n      "invariant_policy",\n      "record_layout",\n      "equality_policy",\n      "append_policy",\n      "application_namespace",\n      "transaction_bounds",\n      "stateful_operations"\n    ]\n  },\n  "GenericTransactionProfile": {\n    "type": "object",\n    "additionalProperties": false,\n    "properties": {\n      "schema_version": {\n        "const": "craft.generic-transaction-profile/v1-candidate"\n      },\n      "id": {\n        "type": "string",\n        "pattern": "^[a-z][a-z0-9-]{0,63}$"\n      },\n      "target": {\n        "const": "node-esm"\n      },\n      "capabilities": {\n        "const": [\n          "Rule",\n          "record-bool",\n          "Operation",\n          "Mapping",\n          "record-uint64",\n          "Calculation",\n          "Policy",\n          "bounded-values",\n          "bounded-collections",\n          "StateMachine",\n          "Entity",\n          "Query",\n          "Entry",\n          "keyed-sqlite-read",\n          "auth-foundation-ready",\n          "stateful-operation",\n          "atomic-sqlite-transaction",\n          "hidden-revision",\n          "command-replay"\n        ]\n      },\n      "limits": {\n        "$ref": "#/$defs/ComputationLimits"\n      },\n      "services": {\n        "type": "array",\n        "items": {\n          "$ref": "#/$defs/GenericKeyedService"\n        },\n        "minItems": 1,\n        "maxItems": 16\n      },\n      "entry_context": {\n        "const": "customer-ready-scalars/v1-candidate"\n      },\n      "auth_abi": {\n        "const": "craft.commerce-auth-ready-bridge/v1-candidate"\n      },\n      "auth_route_template": {\n        "const": "commerce:{logical_entry_id}"\n      },\n      "storage": {\n        "const": "sqlite-atomic-command-values/v1-candidate"\n      },\n      "application_namespace": {\n        "$ref": "#/$defs/SourceName"\n      },\n      "transaction_bounds": {\n        "$ref": "#/$defs/GenericTransactionBounds"\n      }\n    },\n    "required": [\n      "schema_version",\n      "id",\n      "target",\n      "capabilities",\n      "limits",\n      "services",\n      "entry_context",\n      "auth_abi",\n      "auth_route_template",\n      "storage",\n      "application_namespace",\n      "transaction_bounds"\n    ]\n  },\n  "GenericCommandPermissionTraceItem": {\n    "type": "object",\n    "additionalProperties": false,\n    "properties": {\n      "entry": {\n        "$ref": "#/$defs/SourceName"\n      },\n      "source_callsite": {\n        "$ref": "#/$defs/GenericTransactionSourceSite"\n      },\n      "ordinal": {\n        "type": "integer",\n        "minimum": 0,\n        "maximum": 127\n      },\n      "policy_sha256": {\n        "$ref": "#/$defs/Sha256"\n      }\n    },\n    "required": [\n      "entry",\n      "source_callsite",\n      "ordinal",\n      "policy_sha256"\n    ]\n  },\n  "GenericCommandRecord": {\n    "type": "object",\n    "additionalProperties": false,\n    "properties": {\n      "schema_version": {\n        "const": "craft.generic-command-record/v1-candidate"\n      },\n      "tuple": {\n        "$ref": "#/$defs/GenericRootCommandTuple"\n      },\n      "tuple_canonical_hex": {\n        "type": "string",\n        "pattern": "^(?:[0-9a-f]{2})+$",\n        "minLength": 2,\n        "maxLength": 8192\n      },\n      "tuple_sha256": {\n        "$ref": "#/$defs/Sha256"\n      },\n      "payload_canonical_json": {\n        "type": "string",\n        "minLength": 1,\n        "maxLength": 65536\n      },\n      "payload_sha256": {\n        "$ref": "#/$defs/Sha256"\n      },\n      "result_canonical_json": {\n        "type": "string",\n        "minLength": 1,\n        "maxLength": 65536\n      },\n      "result_sha256": {\n        "$ref": "#/$defs/Sha256"\n      },\n      "permission_trace": {\n        "type": "array",\n        "items": {\n          "$ref": "#/$defs/GenericCommandPermissionTraceItem"\n        },\n        "minItems": 0,\n        "maxItems": 128\n      },\n      "execution_fuel_used": {\n        "type": "integer",\n        "minimum": 0,\n        "maximum": 9007199254740991\n      },\n      "storage_compatibility_sha256": {\n        "$ref": "#/$defs/Sha256"\n      },\n      "state": {\n        "const": "committed"\n      }\n    },\n    "required": [\n      "schema_version",\n      "tuple",\n      "tuple_canonical_hex",\n      "tuple_sha256",\n      "payload_canonical_json",\n      "payload_sha256",\n      "result_canonical_json",\n      "result_sha256",\n      "permission_trace",\n      "execution_fuel_used",\n      "storage_compatibility_sha256",\n      "state"\n    ]\n  },\n  "GenericTransactionFault": {\n    "type": "object",\n    "additionalProperties": false,\n    "properties": {\n      "kind": {\n        "const": "transaction"\n      },\n      "code": {\n        "enum": [\n          "CommandPayloadConflict",\n          "CommandIdentityCollision",\n          "CommandCapacity",\n          "ReadConflict",\n          "RevisionExhausted",\n          "StorageUnavailable",\n          "CommitIndeterminate",\n          "StoredCommandInvalid"\n        ]\n      },\n      "site": {\n        "type": "string",\n        "minLength": 1,\n        "maxLength": 2048\n      },\n      "source_action": {\n        "oneOf": [\n          {\n            "$ref": "#/$defs/GenericTransactionSourceFailure"\n          },\n          {\n            "const": null\n          }\n        ]\n      }\n    },\n    "required": [\n      "kind",\n      "code",\n      "site",\n      "source_action"\n    ]\n  },\n  "GenericCommandCommittedObservation": {\n    "type": "object",\n    "additionalProperties": false,\n    "properties": {\n      "kind": {\n        "enum": [\n          "committed",\n          "replayed",\n          "business-rejected",\n          "business-failed"\n        ]\n      },\n      "command_tuple_sha256": {\n        "$ref": "#/$defs/Sha256"\n      },\n      "result_sha256": {\n        "$ref": "#/$defs/Sha256"\n      }\n    },\n    "required": [\n      "kind",\n      "command_tuple_sha256",\n      "result_sha256"\n    ]\n  },\n  "GenericCommandUncommittedObservation": {\n    "type": "object",\n    "additionalProperties": false,\n    "properties": {\n      "kind": {\n        "enum": [\n          "rolled-back",\n          "unavailable-before-start",\n          "indeterminate",\n          "failed-before-write"\n        ]\n      },\n      "command_tuple_sha256": {\n        "$ref": "#/$defs/Sha256"\n      }\n    },\n    "required": [\n      "kind",\n      "command_tuple_sha256"\n    ]\n  },\n  "GenericCommandResult": {\n    "oneOf": [\n      {\n        "type": "object",\n        "additionalProperties": false,\n        "properties": {\n          "schema_version": {\n            "const": "craft.generic-command-result/v1-candidate"\n          },\n          "ok": {\n            "const": true\n          },\n          "outcome": {\n            "type": "object",\n            "additionalProperties": false,\n            "properties": {\n              "kind": {\n                "const": "Returned"\n              },\n              "value": {\n                "$ref": "#/$defs/GenericWireValue"\n              }\n            },\n            "required": [\n              "kind",\n              "value"\n            ]\n          },\n          "fuel_used": {\n            "type": "integer",\n            "minimum": 0,\n            "maximum": 9007199254740991\n          },\n          "observation": {\n            "type": "object",\n            "additionalProperties": false,\n            "properties": {\n              "kind": {\n                "const": "committed"\n              },\n              "command_tuple_sha256": {\n                "$ref": "#/$defs/Sha256"\n              },\n              "result_sha256": {\n                "$ref": "#/$defs/Sha256"\n              }\n            },\n            "required": [\n              "kind",\n              "command_tuple_sha256",\n              "result_sha256"\n            ]\n          }\n        },\n        "required": [\n          "schema_version",\n          "ok",\n          "outcome",\n          "fuel_used",\n          "observation"\n        ]\n      },\n      {\n        "type": "object",\n        "additionalProperties": false,\n        "properties": {\n          "schema_version": {\n            "const": "craft.generic-command-result/v1-candidate"\n          },\n          "ok": {\n            "const": true\n          },\n          "outcome": {\n            "type": "object",\n            "additionalProperties": false,\n            "properties": {\n              "kind": {\n                "const": "Rejected"\n              },\n              "code": {\n                "$ref": "#/$defs/FailureCode"\n              }\n            },\n            "required": [\n              "kind",\n              "code"\n            ]\n          },\n          "fuel_used": {\n            "type": "integer",\n            "minimum": 0,\n            "maximum": 9007199254740991\n          },\n          "observation": {\n            "type": "object",\n            "additionalProperties": false,\n            "properties": {\n              "kind": {\n                "const": "business-rejected"\n              },\n              "command_tuple_sha256": {\n                "$ref": "#/$defs/Sha256"\n              },\n              "result_sha256": {\n                "$ref": "#/$defs/Sha256"\n              }\n            },\n            "required": [\n              "kind",\n              "command_tuple_sha256",\n              "result_sha256"\n            ]\n          }\n        },\n        "required": [\n          "schema_version",\n          "ok",\n          "outcome",\n          "fuel_used",\n          "observation"\n        ]\n      },\n      {\n        "type": "object",\n        "additionalProperties": false,\n        "properties": {\n          "schema_version": {\n            "const": "craft.generic-command-result/v1-candidate"\n          },\n          "ok": {\n            "const": true\n          },\n          "outcome": {\n            "type": "object",\n            "additionalProperties": false,\n            "properties": {\n              "kind": {\n                "const": "Failed"\n              },\n              "code": {\n                "$ref": "#/$defs/FailureCode"\n              }\n            },\n            "required": [\n              "kind",\n              "code"\n            ]\n          },\n          "fuel_used": {\n            "type": "integer",\n            "minimum": 0,\n            "maximum": 9007199254740991\n          },\n          "observation": {\n            "type": "object",\n            "additionalProperties": false,\n            "properties": {\n              "kind": {\n                "const": "business-failed"\n              },\n              "command_tuple_sha256": {\n                "$ref": "#/$defs/Sha256"\n              },\n              "result_sha256": {\n                "$ref": "#/$defs/Sha256"\n              }\n            },\n            "required": [\n              "kind",\n              "command_tuple_sha256",\n              "result_sha256"\n            ]\n          }\n        },\n        "required": [\n          "schema_version",\n          "ok",\n          "outcome",\n          "fuel_used",\n          "observation"\n        ]\n      },\n      {\n        "type": "object",\n        "additionalProperties": false,\n        "properties": {\n          "schema_version": {\n            "const": "craft.generic-command-result/v1-candidate"\n          },\n          "ok": {\n            "const": true\n          },\n          "outcome": {\n            "$ref": "#/$defs/GenericEntryOutcome"\n          },\n          "fuel_used": {\n            "type": "integer",\n            "minimum": 0,\n            "maximum": 9007199254740991\n          },\n          "observation": {\n            "type": "object",\n            "additionalProperties": false,\n            "properties": {\n              "kind": {\n                "const": "replayed"\n              },\n              "command_tuple_sha256": {\n                "$ref": "#/$defs/Sha256"\n              },\n              "result_sha256": {\n                "$ref": "#/$defs/Sha256"\n              }\n            },\n            "required": [\n              "kind",\n              "command_tuple_sha256",\n              "result_sha256"\n            ]\n          }\n        },\n        "required": [\n          "schema_version",\n          "ok",\n          "outcome",\n          "fuel_used",\n          "observation"\n        ]\n      },\n      {\n        "type": "object",\n        "additionalProperties": false,\n        "properties": {\n          "schema_version": {\n            "const": "craft.generic-command-result/v1-candidate"\n          },\n          "ok": {\n            "const": true\n          },\n          "outcome": {\n            "type": "object",\n            "additionalProperties": false,\n            "properties": {\n              "kind": {\n                "enum": [\n                  "Rejected",\n                  "Failed"\n                ]\n              },\n              "code": {\n                "$ref": "#/$defs/FailureCode"\n              }\n            },\n            "required": [\n              "kind",\n              "code"\n            ]\n          },\n          "fuel_used": {\n            "type": "integer",\n            "minimum": 0,\n            "maximum": 9007199254740991\n          },\n          "observation": {\n            "type": "object",\n            "additionalProperties": false,\n            "properties": {\n              "kind": {\n                "const": "rolled-back"\n              },\n              "command_tuple_sha256": {\n                "$ref": "#/$defs/Sha256"\n              }\n            },\n            "required": [\n              "kind",\n              "command_tuple_sha256"\n            ]\n          }\n        },\n        "required": [\n          "schema_version",\n          "ok",\n          "outcome",\n          "fuel_used",\n          "observation"\n        ]\n      },\n      {\n        "type": "object",\n        "additionalProperties": false,\n        "properties": {\n          "schema_version": {\n            "const": "craft.generic-command-result/v1-candidate"\n          },\n          "ok": {\n            "const": false\n          },\n          "error": {\n            "oneOf": [\n              {\n                "$ref": "#/$defs/ExpressionFailure"\n              },\n              {\n                "$ref": "#/$defs/GenericAuthFault"\n              },\n              {\n                "$ref": "#/$defs/GenericStorageFault"\n              },\n              {\n                "type": "object",\n                "additionalProperties": false,\n                "properties": {\n                  "kind": {\n                    "const": "transaction"\n                  },\n                  "code": {\n                    "enum": [\n                      "CommandPayloadConflict",\n                      "CommandIdentityCollision",\n                      "CommandCapacity",\n                      "ReadConflict",\n                      "RevisionExhausted",\n                      "StorageUnavailable",\n                      "StoredCommandInvalid"\n                    ]\n                  },\n                  "site": {\n                    "type": "string",\n                    "minLength": 1,\n                    "maxLength": 2048\n                  },\n                  "source_action": {\n                    "oneOf": [\n                      {\n                        "$ref": "#/$defs/GenericTransactionSourceFailure"\n                      },\n                      {\n                        "const": null\n                      }\n                    ]\n                  }\n                },\n                "required": [\n                  "kind",\n                  "code",\n                  "site",\n                  "source_action"\n                ]\n              }\n            ]\n          },\n          "fuel_used": {\n            "type": "integer",\n            "minimum": 0,\n            "maximum": 9007199254740991\n          },\n          "observation": {\n            "type": "object",\n            "additionalProperties": false,\n            "properties": {\n              "kind": {\n                "enum": [\n                  "rolled-back",\n                  "unavailable-before-start",\n                  "failed-before-write"\n                ]\n              },\n              "command_tuple_sha256": {\n                "$ref": "#/$defs/Sha256"\n              }\n            },\n            "required": [\n              "kind",\n              "command_tuple_sha256"\n            ]\n          }\n        },\n        "required": [\n          "schema_version",\n          "ok",\n          "error",\n          "fuel_used",\n          "observation"\n        ]\n      },\n      {\n        "type": "object",\n        "additionalProperties": false,\n        "properties": {\n          "schema_version": {\n            "const": "craft.generic-command-result/v1-candidate"\n          },\n          "ok": {\n            "const": false\n          },\n          "error": {\n            "type": "object",\n            "additionalProperties": false,\n            "properties": {\n              "kind": {\n                "const": "transaction"\n              },\n              "code": {\n                "const": "CommitIndeterminate"\n              },\n              "site": {\n                "type": "string",\n                "minLength": 1,\n                "maxLength": 2048\n              },\n              "source_action": {\n                "oneOf": [\n                  {\n                    "$ref": "#/$defs/GenericTransactionSourceFailure"\n                  },\n                  {\n                    "const": null\n                  }\n                ]\n              }\n            },\n            "required": [\n              "kind",\n              "code",\n              "site",\n              "source_action"\n            ]\n          },\n          "fuel_used": {\n            "type": "integer",\n            "minimum": 0,\n            "maximum": 9007199254740991\n          },\n          "observation": {\n            "type": "object",\n            "additionalProperties": false,\n            "properties": {\n              "kind": {\n                "const": "indeterminate"\n              },\n              "command_tuple_sha256": {\n                "$ref": "#/$defs/Sha256"\n              }\n            },\n            "required": [\n              "kind",\n              "command_tuple_sha256"\n            ]\n          }\n        },\n        "required": [\n          "schema_version",\n          "ok",\n          "error",\n          "fuel_used",\n          "observation"\n        ]\n      },\n      {\n        "type": "object",\n        "additionalProperties": false,\n        "properties": {\n          "schema_version": {\n            "const": "craft.generic-command-result/v1-candidate"\n          },\n          "ok": {\n            "const": false\n          },\n          "error": {\n            "$ref": "#/$defs/GenericCommandWithheldCommitFault"\n          },\n          "fuel_used": {\n            "type": "integer",\n            "minimum": 0,\n            "maximum": 9007199254740991\n          },\n          "observation": {\n            "$ref": "#/$defs/GenericCommandWithheldCommitObservation"\n          }\n        },\n        "required": [\n          "schema_version",\n          "ok",\n          "error",\n          "fuel_used",\n          "observation"\n        ]\n      }\n    ]\n  },\n  "GenericCommandInspection": {\n    "oneOf": [\n      {\n        "type": "object",\n        "additionalProperties": false,\n        "properties": {\n          "schema_version": {\n            "const": "craft.generic-command-inspection/v1-candidate"\n          },\n          "kind": {\n            "const": "committed"\n          },\n          "outcome": {\n            "$ref": "#/$defs/GenericEntryOutcome"\n          },\n          "fuel_used": {\n            "type": "integer",\n            "minimum": 0,\n            "maximum": 9007199254740991\n          },\n          "command_tuple_sha256": {\n            "$ref": "#/$defs/Sha256"\n          },\n          "result_sha256": {\n            "$ref": "#/$defs/Sha256"\n          }\n        },\n        "required": [\n          "schema_version",\n          "kind",\n          "outcome",\n          "fuel_used",\n          "command_tuple_sha256",\n          "result_sha256"\n        ]\n      },\n      {\n        "type": "object",\n        "additionalProperties": false,\n        "properties": {\n          "schema_version": {\n            "const": "craft.generic-command-inspection/v1-candidate"\n          },\n          "kind": {\n            "const": "not-committed"\n          },\n          "fuel_used": {\n            "type": "integer",\n            "minimum": 0,\n            "maximum": 9007199254740991\n          },\n          "command_tuple_sha256": {\n            "$ref": "#/$defs/Sha256"\n          }\n        },\n        "required": [\n          "schema_version",\n          "kind",\n          "fuel_used",\n          "command_tuple_sha256"\n        ]\n      },\n      {\n        "type": "object",\n        "additionalProperties": false,\n        "properties": {\n          "schema_version": {\n            "const": "craft.generic-command-inspection/v1-candidate"\n          },\n          "kind": {\n            "const": "unavailable"\n          },\n          "fuel_used": {\n            "type": "integer",\n            "minimum": 0,\n            "maximum": 9007199254740991\n          },\n          "command_tuple_sha256": {\n            "$ref": "#/$defs/Sha256"\n          }\n        },\n        "required": [\n          "schema_version",\n          "kind",\n          "fuel_used",\n          "command_tuple_sha256"\n        ]\n      },\n      {\n        "type": "object",\n        "additionalProperties": false,\n        "properties": {\n          "schema_version": {\n            "const": "craft.generic-command-inspection/v1-candidate"\n          },\n          "kind": {\n            "const": "fault"\n          },\n          "error": {\n            "oneOf": [\n              {\n                "$ref": "#/$defs/ExpressionFailure"\n              },\n              {\n                "$ref": "#/$defs/GenericAuthFault"\n              },\n              {\n                "$ref": "#/$defs/GenericStorageFault"\n              },\n              {\n                "type": "object",\n                "additionalProperties": false,\n                "properties": {\n                  "kind": {\n                    "const": "transaction"\n                  },\n                  "code": {\n                    "enum": [\n                      "CommandPayloadConflict",\n                      "CommandIdentityCollision",\n                      "CommandCapacity",\n                      "ReadConflict",\n                      "RevisionExhausted",\n                      "StorageUnavailable",\n                      "StoredCommandInvalid"\n                    ]\n                  },\n                  "site": {\n                    "type": "string",\n                    "minLength": 1,\n                    "maxLength": 2048\n                  },\n                  "source_action": {\n                    "oneOf": [\n                      {\n                        "$ref": "#/$defs/GenericTransactionSourceFailure"\n                      },\n                      {\n                        "const": null\n                      }\n                    ]\n                  }\n                },\n                "required": [\n                  "kind",\n                  "code",\n                  "site",\n                  "source_action"\n                ]\n              }\n            ]\n          },\n          "fuel_used": {\n            "type": "integer",\n            "minimum": 0,\n            "maximum": 9007199254740991\n          },\n          "command_tuple_sha256": {\n            "$ref": "#/$defs/Sha256"\n          }\n        },\n        "required": [\n          "schema_version",\n          "kind",\n          "error",\n          "fuel_used",\n          "command_tuple_sha256"\n        ]\n      }\n    ]\n  },\n  "GenericCommandWithheldCommitObservation": {\n    "type": "object",\n    "additionalProperties": false,\n    "properties": {\n      "kind": {\n        "const": "commit-observed-result-withheld"\n      },\n      "command_tuple_sha256": {\n        "$ref": "#/$defs/Sha256"\n      },\n      "result_sha256": {\n        "$ref": "#/$defs/Sha256"\n      }\n    },\n    "required": [\n      "kind",\n      "command_tuple_sha256",\n      "result_sha256"\n    ]\n  },\n  "GenericCommandWithheldCommitFault": {\n    "type": "object",\n    "additionalProperties": false,\n    "properties": {\n      "kind": {\n        "const": "custody"\n      },\n      "code": {\n        "const": "CommittedResultWithheld"\n      },\n      "cause_code": {\n        "enum": [\n          "ForeignOwner",\n          "StaleOwner",\n          "DisposedOwner",\n          "InvalidContract",\n          "HostCurrentnessFailure"\n        ]\n      }\n    },\n    "required": [\n      "kind",\n      "code",\n      "cause_code"\n    ]\n  },\n  "GenericOpaqueClaimAttachment": {\n    "type": "object",\n    "additionalProperties": false,\n    "properties": {\n      "id": {\n        "$ref": "#/$defs/SourceName"\n      },\n      "language": {\n        "enum": [\n          "lean4",\n          "smtlib2",\n          "alloy",\n          "tla-plus",\n          "souffle"\n        ]\n      },\n      "source": {\n        "type": "object",\n        "additionalProperties": false,\n        "properties": {\n          "path": {\n            "type": "string",\n            "minLength": 1,\n            "maxLength": 2048\n          },\n          "sha256": {\n            "$ref": "#/$defs/Sha256"\n          },\n          "bytes": {\n            "type": "integer",\n            "minimum": 0,\n            "maximum": 262144\n          }\n        },\n        "required": [\n          "path",\n          "sha256",\n          "bytes"\n        ]\n      },\n      "targets": {\n        "type": "array",\n        "items": {\n          "$ref": "#/$defs/SourceName"\n        },\n        "minItems": 1,\n        "maxItems": 16\n      },\n      "qualification": {\n        "const": "opaque-not-evaluated"\n      }\n    },\n    "required": [\n      "id",\n      "language",\n      "source",\n      "targets",\n      "qualification"\n    ]\n  },\n  "GenericOpaqueAssuranceInspection": {\n    "type": "object",\n    "additionalProperties": false,\n    "properties": {\n      "schema_version": {\n        "const": "craft.generic-opaque-assurance/v1-candidate"\n      },\n      "claims": {\n        "type": "array",\n        "items": {\n          "$ref": "#/$defs/GenericOpaqueClaimAttachment"\n        },\n        "minItems": 0,\n        "maxItems": 16\n      },\n      "assurance_sha256": {\n        "$ref": "#/$defs/Sha256"\n      },\n      "authority_effect": {\n        "const": "none"\n      }\n    },\n    "required": [\n      "schema_version",\n      "claims",\n      "assurance_sha256",\n      "authority_effect"\n    ]\n  },\n  "GenericTransactionSourceSite": {\n    "type": "string",\n    "minLength": 14,\n    "maxLength": 2048,\n    "pattern": "^c08-site/v1:"\n  },\n  "GenericTransactionSqlResultColumn": {\n    "oneOf": [\n      {\n        "$ref": "#/$defs/GenericSqlResultColumn"\n      },\n      {\n        "type": "object",\n        "additionalProperties": false,\n        "properties": {\n          "name": {\n            "const": "_craft_revision"\n          },\n          "sql_name": {\n            "const": "_craft_revision"\n          },\n          "representation": {\n            "const": "blob"\n          },\n          "nullable": {\n            "const": false\n          },\n          "role": {\n            "const": "hidden-revision"\n          },\n          "type_alias": {\n            "type": "string",\n            "minLength": 1,\n            "maxLength": 2048\n          },\n          "length_alias": {\n            "type": "string",\n            "minLength": 1,\n            "maxLength": 2048\n          },\n          "payload_alias": {\n            "type": "string",\n            "minLength": 1,\n            "maxLength": 2048\n          },\n          "max_bytes": {\n            "const": 8\n          }\n        },\n        "required": [\n          "name",\n          "sql_name",\n          "representation",\n          "nullable",\n          "role",\n          "type_alias",\n          "length_alias",\n          "payload_alias",\n          "max_bytes"\n        ]\n      }\n    ]\n  },\n  "GenericTransactionSqlMaterialization": {\n    "type": "object",\n    "additionalProperties": false,\n    "properties": {\n      "schema_version": {\n        "const": "craft.generic-transaction-sql-materialization/v1-candidate"\n      },\n      "query": {\n        "$ref": "#/$defs/SourceName"\n      },\n      "entity": {\n        "$ref": "#/$defs/SourceName"\n      },\n      "service": {\n        "$ref": "#/$defs/SourceName"\n      },\n      "selected_key_index": {\n        "type": "integer",\n        "minimum": 0,\n        "maximum": 15\n      },\n      "sql": {\n        "type": "string",\n        "minLength": 1,\n        "maxLength": 1048576\n      },\n      "sql_sha256": {\n        "$ref": "#/$defs/Sha256"\n      },\n      "columns": {\n        "type": "array",\n        "items": {\n          "$ref": "#/$defs/GenericTransactionSqlResultColumn"\n        },\n        "minItems": 2,\n        "maxItems": 82\n      },\n      "database_encoding": {\n        "const": "UTF-8"\n      },\n      "rows_max": {\n        "const": 2\n      },\n      "value_bytes_max": {\n        "type": "integer",\n        "minimum": 1,\n        "maximum": 524288\n      },\n      "data_bytes_max": {\n        "type": "integer",\n        "minimum": 1,\n        "maximum": 524288\n      },\n      "aggregate_bytes_max": {\n        "type": "integer",\n        "minimum": 9,\n        "maximum": 9437192\n      },\n      "shape_alias": {\n        "const": "m_shape"\n      },\n      "bound_alias": {\n        "const": "m_bound"\n      },\n      "guard": {\n        "const": "whole-row-case-before-js-materialization/v1"\n      },\n      "length_measure": {\n        "const": "octet_length-utf8/v1"\n      },\n      "revision_column": {\n        "const": "_craft_revision"\n      },\n      "revision_encoding": {\n        "const": "uint64-big-endian-nonzero/v1"\n      },\n      "revision_guard": {\n        "const": "blob-exactly-eight-nonzero-before-js/v1"\n      }\n    },\n    "required": [\n      "schema_version",\n      "query",\n      "entity",\n      "service",\n      "selected_key_index",\n      "sql",\n      "sql_sha256",\n      "columns",\n      "database_encoding",\n      "rows_max",\n      "value_bytes_max",\n      "data_bytes_max",\n      "aggregate_bytes_max",\n      "shape_alias",\n      "bound_alias",\n      "guard",\n      "length_measure",\n      "revision_column",\n      "revision_encoding",\n      "revision_guard"\n    ]\n  },\n  "GenericTransactionStorageColumn": {\n    "type": "object",\n    "additionalProperties": false,\n    "properties": {\n      "name": {\n        "$ref": "#/$defs/PropertyName"\n      },\n      "sql_name": {\n        "type": "string",\n        "minLength": 1,\n        "maxLength": 2048\n      },\n      "type": {\n        "$ref": "#/$defs/ValueType"\n      },\n      "nullable": {\n        "type": "boolean"\n      }\n    },\n    "required": [\n      "name",\n      "sql_name",\n      "type",\n      "nullable"\n    ]\n  },\n  "GenericTransactionStorageTable": {\n    "type": "object",\n    "additionalProperties": false,\n    "properties": {\n      "entity": {\n        "$ref": "#/$defs/SourceName"\n      },\n      "service": {\n        "$ref": "#/$defs/SourceName"\n      },\n      "physical_name": {\n        "type": "string",\n        "minLength": 1,\n        "maxLength": 2048\n      },\n      "columns": {\n        "type": "array",\n        "items": {\n          "$ref": "#/$defs/GenericTransactionStorageColumn"\n        },\n        "minItems": 1,\n        "maxItems": 64\n      },\n      "keys": {\n        "type": "array",\n        "items": {\n          "type": "array",\n          "items": {\n            "$ref": "#/$defs/PropertyName"\n          },\n          "minItems": 1,\n          "maxItems": 16\n        },\n        "minItems": 1,\n        "maxItems": 16\n      },\n      "record": {\n        "$ref": "#/$defs/GenericRecordDefinition"\n      },\n      "row_column": {\n        "const": "_craft_row"\n      },\n      "key_columns": {\n        "type": "array",\n        "items": {\n          "type": "string",\n          "minLength": 1,\n          "maxLength": 128\n        },\n        "minItems": 1,\n        "maxItems": 16\n      },\n      "revision_column": {\n        "const": "_craft_revision"\n      },\n      "revision_encoding": {\n        "const": "uint64-big-endian-nonzero/v1"\n      },\n      "create_sql": {\n        "type": "string",\n        "minLength": 1,\n        "maxLength": 1048576\n      },\n      "indexes": {\n        "type": "array",\n        "items": {\n          "type": "string",\n          "minLength": 1,\n          "maxLength": 1048576\n        },\n        "minItems": 0,\n        "maxItems": 15\n      },\n      "insert_sql": {\n        "type": "string",\n        "minLength": 1,\n        "maxLength": 1048576\n      },\n      "update_sql": {\n        "type": "string",\n        "minLength": 1,\n        "maxLength": 1048576\n      }\n    },\n    "required": [\n      "entity",\n      "service",\n      "physical_name",\n      "columns",\n      "keys",\n      "record",\n      "row_column",\n      "key_columns",\n      "revision_column",\n      "revision_encoding",\n      "create_sql",\n      "indexes",\n      "insert_sql",\n      "update_sql"\n    ]\n  },\n  "GenericCommandSqlColumn": {\n    "type": "object",\n    "additionalProperties": false,\n    "properties": {\n      "name": {\n        "enum": [\n          "tuple_sha256",\n          "tuple",\n          "payload_sha256",\n          "payload",\n          "result_sha256",\n          "result",\n          "permission_trace",\n          "execution_fuel",\n          "record_bytes"\n        ]\n      },\n      "representation": {\n        "enum": [\n          "text",\n          "blob",\n          "integer"\n        ]\n      },\n      "type_alias": {\n        "type": "string",\n        "minLength": 1,\n        "maxLength": 128\n      },\n      "length_alias": {\n        "type": "string",\n        "minLength": 1,\n        "maxLength": 128\n      },\n      "payload_alias": {\n        "type": "string",\n        "minLength": 1,\n        "maxLength": 128\n      },\n      "max_bytes": {\n        "type": "integer",\n        "minimum": 1,\n        "maximum": 65536\n      }\n    },\n    "required": [\n      "name",\n      "representation",\n      "type_alias",\n      "length_alias",\n      "payload_alias",\n      "max_bytes"\n    ]\n  },\n  "GenericCommandJournalMaterialization": {\n    "type": "object",\n    "additionalProperties": false,\n    "properties": {\n      "schema_version": {\n        "const": "craft.generic-command-journal-materialization/v1-candidate"\n      },\n      "table": {\n        "const": "_craft_generic_commands_v1"\n      },\n      "sql": {\n        "type": "string",\n        "minLength": 1,\n        "maxLength": 1048576\n      },\n      "sql_sha256": {\n        "$ref": "#/$defs/Sha256"\n      },\n      "columns": {\n        "type": "array",\n        "items": {\n          "$ref": "#/$defs/GenericCommandSqlColumn"\n        },\n        "minItems": 9,\n        "maxItems": 9\n      },\n      "rows_max": {\n        "const": 2\n      },\n      "shape_alias": {\n        "const": "j_shape"\n      },\n      "bound_alias": {\n        "const": "j_bound"\n      },\n      "guard": {\n        "const": "whole-command-case-before-js-materialization/v1"\n      },\n      "length_measure": {\n        "const": "octet_length-utf8/v1"\n      },\n      "tuple_bytes_max": {\n        "type": "integer",\n        "minimum": 1,\n        "maximum": 4096\n      },\n      "payload_bytes_max": {\n        "type": "integer",\n        "minimum": 1,\n        "maximum": 65536\n      },\n      "result_bytes_max": {\n        "type": "integer",\n        "minimum": 1,\n        "maximum": 65536\n      },\n      "permission_trace_bytes_max": {\n        "type": "integer",\n        "minimum": 1,\n        "maximum": 32768\n      },\n      "record_accounting": {\n        "const": "three-ascii-sha256-plus-four-blobs-plus-two-u64/v1"\n      }\n    },\n    "required": [\n      "schema_version",\n      "table",\n      "sql",\n      "sql_sha256",\n      "columns",\n      "rows_max",\n      "shape_alias",\n      "bound_alias",\n      "guard",\n      "length_measure",\n      "tuple_bytes_max",\n      "payload_bytes_max",\n      "result_bytes_max",\n      "permission_trace_bytes_max",\n      "record_accounting"\n    ]\n  },\n  "GenericCommandJournalDescriptor": {\n    "type": "object",\n    "additionalProperties": false,\n    "properties": {\n      "table": {\n        "const": "_craft_generic_commands_v1"\n      },\n      "create_sql": {\n        "const": "CREATE TABLE \\"_craft_generic_commands_v1\\" (tuple_sha256 TEXT PRIMARY KEY, tuple BLOB NOT NULL, payload_sha256 TEXT NOT NULL, payload BLOB NOT NULL, result_sha256 TEXT NOT NULL, result BLOB NOT NULL, permission_trace BLOB NOT NULL, execution_fuel INTEGER NOT NULL, record_bytes INTEGER NOT NULL) STRICT;"\n      },\n      "insert_sql": {\n        "const": "INSERT INTO \\"_craft_generic_commands_v1\\" (tuple_sha256,tuple,payload_sha256,payload,result_sha256,result,permission_trace,execution_fuel,record_bytes) VALUES (?,?,?,?,?,?,?,?,?)"\n      },\n      "materialization": {\n        "$ref": "#/$defs/GenericCommandJournalMaterialization"\n      },\n      "mutation_policy": {\n        "const": "original-owner-insert-and-read-only/v1"\n      },\n      "update_sql": {\n        "const": null\n      },\n      "delete_sql": {\n        "const": null\n      },\n      "pruning": {\n        "const": false\n      }\n    },\n    "required": [\n      "table",\n      "create_sql",\n      "insert_sql",\n      "materialization",\n      "mutation_policy",\n      "update_sql",\n      "delete_sql",\n      "pruning"\n    ]\n  },\n  "GenericTransactionStorageDescriptor": {\n    "type": "object",\n    "additionalProperties": false,\n    "properties": {\n      "schema_version": {\n        "const": "craft.generic-sqlite-atomic-storage/v1-candidate"\n      },\n      "service": {\n        "$ref": "#/$defs/SourceName"\n      },\n      "value_bytes_max": {\n        "type": "integer",\n        "minimum": 1,\n        "maximum": 524288\n      },\n      "tables": {\n        "type": "array",\n        "items": {\n          "$ref": "#/$defs/GenericTransactionStorageTable"\n        },\n        "minItems": 1,\n        "maxItems": 256\n      },\n      "materializations": {\n        "type": "array",\n        "items": {\n          "$ref": "#/$defs/GenericTransactionSqlMaterialization"\n        },\n        "minItems": 0,\n        "maxItems": 256\n      },\n      "journal": {\n        "$ref": "#/$defs/GenericCommandJournalDescriptor"\n      },\n      "metadata": {\n        "type": "object",\n        "additionalProperties": false,\n        "properties": {\n          "table": {\n            "const": "_craft_generic_metadata"\n          },\n          "create_sql": {\n            "const": "CREATE TABLE \\"_craft_generic_metadata\\" (id INTEGER PRIMARY KEY CHECK(id=1), store_id TEXT NOT NULL, compatibility TEXT NOT NULL, revision_counter BLOB NOT NULL CHECK(typeof(revision_counter)=\'blob\' AND length(revision_counter)=8), command_count INTEGER NOT NULL CHECK(command_count>=0), command_bytes INTEGER NOT NULL CHECK(command_bytes>=0)) STRICT;"\n          },\n          "revision_encoding": {\n            "const": "uint64-big-endian-counter-zero-initial/v1"\n          },\n          "revision_max_hex": {\n            "const": "ffffffffffffffff"\n          },\n          "materialization": {\n            "$ref": "#/$defs/GenericTransactionMetadataMaterialization"\n          }\n        },\n        "required": [\n          "table",\n          "create_sql",\n          "revision_encoding",\n          "revision_max_hex",\n          "materialization"\n        ]\n      },\n      "storage_projection_sha256": {\n        "$ref": "#/$defs/Sha256"\n      },\n      "authority_effect": {\n        "const": "none"\n      }\n    },\n    "required": [\n      "schema_version",\n      "service",\n      "value_bytes_max",\n      "tables",\n      "materializations",\n      "journal",\n      "metadata",\n      "storage_projection_sha256",\n      "authority_effect"\n    ]\n  },\n  "GenericTransactionMetadataMaterialization": {\n    "type": "object",\n    "additionalProperties": false,\n    "properties": {\n      "schema_version": {\n        "const": "craft.generic-transaction-metadata-materialization/v1-candidate"\n      },\n      "table": {\n        "const": "_craft_generic_metadata"\n      },\n      "open_sql": {\n        "type": "string",\n        "minLength": 1,\n        "maxLength": 1048576\n      },\n      "open_sql_sha256": {\n        "$ref": "#/$defs/Sha256"\n      },\n      "held_sql": {\n        "type": "string",\n        "minLength": 1,\n        "maxLength": 1048576\n      },\n      "held_sql_sha256": {\n        "$ref": "#/$defs/Sha256"\n      },\n      "occupancy_sql": {\n        "type": "string",\n        "minLength": 1,\n        "maxLength": 1048576\n      },\n      "occupancy_sql_sha256": {\n        "$ref": "#/$defs/Sha256"\n      },\n      "rows_max": {\n        "const": 2\n      },\n      "store_id_bytes": {\n        "const": 36\n      },\n      "compatibility_bytes_max": {\n        "const": 1048576\n      },\n      "revision_bytes": {\n        "const": 8\n      },\n      "command_records_max": {\n        "type": "integer",\n        "minimum": 1,\n        "maximum": 1024\n      },\n      "command_bytes_max": {\n        "type": "integer",\n        "minimum": 1,\n        "maximum": 16777216\n      },\n      "occupancy_rows_max": {\n        "const": 1025\n      },\n      "guard": {\n        "const": "metadata-identity-equality-and-whole-row-case-before-js/v1"\n      },\n      "snapshot": {\n        "const": "same-original-sqlite-snapshot-as-occupancy/v1"\n      },\n      "compatibility_payload": {\n        "const": "never-returned-to-js"\n      },\n      "held_store_id_payload": {\n        "const": "never-returned-to-js"\n      }\n    },\n    "required": [\n      "schema_version",\n      "table",\n      "open_sql",\n      "open_sql_sha256",\n      "held_sql",\n      "held_sql_sha256",\n      "occupancy_sql",\n      "occupancy_sql_sha256",\n      "rows_max",\n      "store_id_bytes",\n      "compatibility_bytes_max",\n      "revision_bytes",\n      "command_records_max",\n      "command_bytes_max",\n      "occupancy_rows_max",\n      "guard",\n      "snapshot",\n      "compatibility_payload",\n      "held_store_id_payload"\n    ]\n  },\n  "GenericTransactionAuthoredFile": {\n    "type": "object",\n    "additionalProperties": false,\n    "properties": {\n      "path": {\n        "type": "string",\n        "minLength": 1,\n        "maxLength": 2048\n      },\n      "sha256": {\n        "$ref": "#/$defs/Sha256"\n      },\n      "bytes": {\n        "type": "integer",\n        "minimum": 0,\n        "maximum": 1048576\n      }\n    },\n    "required": [\n      "path",\n      "sha256",\n      "bytes"\n    ]\n  },\n  "GenericTransactionAuthoredInput": {\n    "type": "object",\n    "additionalProperties": false,\n    "properties": {\n      "schema_version": {\n        "const": "craft.generic-transaction-authored-input/v1-candidate"\n      },\n      "primary_source": {\n        "$ref": "#/$defs/GenericTransactionAuthoredFile"\n      },\n      "additional_sources": {\n        "type": "array",\n        "items": {\n          "$ref": "#/$defs/GenericTransactionAuthoredFile"\n        },\n        "minItems": 0,\n        "maxItems": 31\n      },\n      "computation_bounds": {\n        "$ref": "#/$defs/GenericTransactionAuthoredFile"\n      },\n      "transaction_bounds": {\n        "$ref": "#/$defs/GenericTransactionAuthoredFile"\n      },\n      "claim_assets": {\n        "type": "array",\n        "items": {\n          "$ref": "#/$defs/GenericTransactionAuthoredFile"\n        },\n        "minItems": 0,\n        "maxItems": 16\n      },\n      "profile": {\n        "$ref": "#/$defs/GenericTransactionAuthoredFile"\n      },\n      "source_origin_sha256": {\n        "$ref": "#/$defs/Sha256"\n      }\n    },\n    "required": [\n      "schema_version",\n      "primary_source",\n      "additional_sources",\n      "computation_bounds",\n      "transaction_bounds",\n      "claim_assets",\n      "profile",\n      "source_origin_sha256"\n    ]\n  }\n}')
# A missing version-conflict business mapping preserves the intrinsic ReadConflict
# fault. It does not invent a business rejection or change rollback semantics.
TRANSACTION_DEFINITIONS['GenericTransactionPlan']['properties']['handlers']['properties']['on-version-conflict'] = {
    'anyOf': [{'$ref': '#/$defs/GenericTransactionSourceFailure'}, {'type': 'null'}]
}
# Finite preflight consumer of the existing typed Policy value. SourceSpan is retained
# separately from the original generic control-site identity.
TRANSACTION_DEFINITIONS['GenericPolicyEnforcementPreflight'] = obj({
    'kind': {'const':'enforce-policy'},
    'semantics_revision': {'const':'typed-policy-enforcement/v1'},
    'policy':ref('SourceName'), 'value':ref('GenericKeyedRoleExpression'),
    'result_enum':ref('SourceName'), 'reason_enum':ref('SourceName'),
    'rejections': {'type':'array','items':obj({'variant':ref('PropertyName'),'wire':ref('FailureCode'),'code':ref('FailureCode')}),'minItems':1,'maxItems':64},
    'source_site':ref('GenericTransactionSourceSite'), 'source_span':ref('SourceSpan'),
})
TRANSACTION_DEFINITIONS['GenericStatefulPreflightStep']['oneOf'].append(ref('GenericPolicyEnforcementPreflight'))
_legacy_transaction_caps = TRANSACTION_DEFINITIONS['GenericTransactionProfile']['properties']['capabilities']['const']
TRANSACTION_DEFINITIONS['GenericTransactionProfile']['properties']['capabilities'] = {'anyOf':[
    {'const': _legacy_transaction_caps}, {'const':_legacy_transaction_caps+['operation-policy-enforcement']}
]}
TRANSACTION_OWNED = tuple(TRANSACTION_DEFINITIONS)
# Preserve the cumulative C11 indeterminate external-write fault when
# regenerating C12 computation data. It is a first-class command fault.
def preserve_external_outcome_unknown(value):
    if isinstance(value, dict):
        for item in value.values():
            preserve_external_outcome_unknown(item)
    elif isinstance(value, list):
        if 'StoredCommandInvalid' in value and 'CommandPayloadConflict' in value and 'ExternalOutcomeUnknown' not in value:
            value.insert(value.index('StoredCommandInvalid'), 'ExternalOutcomeUnknown')
        for item in value:
            preserve_external_outcome_unknown(item)
preserve_external_outcome_unknown(TRANSACTION_DEFINITIONS)
assert not set(TRANSACTION_OWNED).intersection(D)
D.update(TRANSACTION_DEFINITIONS)


def transaction_materializations():
    schema = {
        '$schema': 'https://json-schema.org/draft/2020-12/schema',
        '$id': 'craft.generic-transaction/v1-candidate',
        '$ref': '#/$defs/GenericTransactionApplicationContract',
        '$defs': closure(TRANSACTION_OWNED),
        '$comment': 'Closed transaction data only. Source reconstruction, semantic checking and original runtime custody remain required. Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions.',
    }
    dependencies = sorted(set().union(*(references(D[n]) for n in TRANSACTION_OWNED)) - set(TRANSACTION_OWNED))
    generic_dependencies = [n for n in dependencies if n in OWNED]
    keyed_dependencies = [n for n in dependencies if n in KEYED_OWNED]
    legacy_dependencies = [n for n in dependencies if n not in OWNED and n not in KEYED_OWNED]
    header = '// GENERATED from Core tools/generic-contracts/schema-source.py; data only.\n// Closed transaction data does not confer source, Auth, storage or invocation custody.\n// Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions.\n'
    body = '\n'.join('export type ' + name + 'V1 = ' + ts(D[name], inline_records=True) + ';' for name in TRANSACTION_OWNED) + '\n'
    def imports(generic_path, keyed_path, legacy_path):
        parts = []
        for names, source in [(generic_dependencies, generic_path), (keyed_dependencies, keyed_path), (legacy_dependencies, legacy_path)]:
            if names:
                parts.append('import type {' + ','.join(n + 'V1' for n in names) + "} from '" + source + "';\n")
        return ''.join(parts)
    return {
        ROOT / 'contracts/generic-transaction-v1.schema.json': json.dumps(schema, indent=2, ensure_ascii=False) + '\n',
        ROOT / 'src/generic/transaction-data-v1.ts': header + imports('./computation-data-v1.js', './query-data-v1.js', '../commerce/commerce-data-v1.js') + body,
        REPO / 'language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/generic-transaction-data-v1.ts': header + imports('./generic-computation-data-v1.js', './generic-query-data-v1.js', './commerce-data-v1.js') + body,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    capability = runpy.run_path(str(Path(__file__).with_name('capability-source.py')))
    outputs = {**materializations(), **keyed_materializations(), **transaction_materializations(),
               **capability['materializations'](ROOT, REPO, D, closure, ts)}
    errors = []
    for path, content in outputs.items():
        if args.write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        elif not path.is_file() or path.read_text() != content:
            errors.append(str(path))
    if errors:
        raise SystemExit('Generated generic contract drift: ' + ', '.join(errors))
    print(json.dumps({'status': 'materialized' if args.write else 'pass-exact', 'files': len(outputs), 'scope': 'versioned generic data only; no semantic/runtime custody', 'open_questions_ref': '../../docs/GENERIC-APPLICATIONS.md#open-questions'}))
