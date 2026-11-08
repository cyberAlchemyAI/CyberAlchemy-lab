"""Selected signed local endpoint interpretation; raw subjects never change.

This module belongs to a separate pinned candidate engine. Its mapping is not
an admitted alias and introduces no Relation Kind, ordered pair or qualifier.
"""
from pathlib import Path
import copy
from .common import byte_digest, load, pointer, require
from .sources import resolve, validate_schema

ENGINE_ID = 'lab-operator-reference-correction/v1-candidate'
MAPPING_PATH = 'product/lab/release-candidates/v1/interface/coupling/engine/endpoint-mapping.json'
MAPPING_SHA = '4594cab2172646b1c2157e0a4be37f560088c580de875fd7d269925993fe1f0b'
PROPOSAL_PATH = 'implementation/lab-runtime/candidates/repeatable-operation/design/contract-impact.json'
PROPOSAL_SHA = 'c0f69674bd37802c669a29fff208232549a3bcfdd28673fc1999c074ad82396a'
CURRENT = {'admitted-current', 'local-admitted-current'}


def mapping_document():
    path = Path(__file__).resolve().parents[1] / 'endpoint-mapping.json'
    require(not path.is_symlink() and byte_digest(path.read_bytes()) == MAPPING_SHA,
        'selected candidate endpoint mapping bytes changed')
    value = load(path)
    require(value['authority_effect'] == 'none' and value['actual_owner_outcome'] is None,
        'candidate mapping cannot confer source or repository admission')
    return value


def binding():
    mapping_document()
    return {'path': MAPPING_PATH, 'sha256': MAPPING_SHA}


def mapping_for(carrier, projection):
    mapping = mapping_document()
    require(projection['documents'].get(MAPPING_PATH) == mapping,
        'candidate mapping is outside the signed source snapshot')
    rows = [r for r in mapping['mappings'] if r['carrier_ref'] == carrier]
    require(len(rows) <= 1, 'ambiguous candidate carrier mapping')
    return rows[0] if rows else None


def selected_contract(carrier, projection, row):
    require(carrier in projection['contracts'], 'mapped source carrier unresolved')
    c = projection['contracts'][carrier]
    require(c['lifecycle_state'] in CURRENT, 'mapped source carrier is not current')
    b = row['schema_binding']
    require(c['semantic_kind'] == row['carrier_kind'] and c['schema_path'] == b['path']
        and c['schema_sha256'] == b['sha256'] and c.get('schema_selector') is None,
        'mapped carrier kind or exact schema binding differs')
    require(c.get('instance_discriminator') == row['instance_discriminator'],
        'mapped carrier discriminator differs')
    require(c['artifact']['semantic_definition_refs'] == row['semantic_definition_refs'],
        'mapped carrier Definition revisions differ')
    for ref in row['semantic_definition_refs']:
        d = resolve(projection['subjects'], ref)
        require(d['version_ref'] == ref and d['kind'] == 'definition'
            and d['effective_state'] in CURRENT, 'mapped semantic Definition is not eligible')
    return c


def subject_kind(subject, projection, *, allow_historical=False):
    """Exact source eligibility, carrier and identity; never caller normalization."""
    row = mapping_for(subject.get('carrier_ref'), projection)
    if row is None:
        return subject['kind']
    states = CURRENT | ({'admitted-historical', 'local-admitted-historical'} if allow_historical else set())
    require(subject['effective_state'] in states, 'mapped endpoint instance is not eligible for this use')
    c = selected_contract(subject['carrier_ref'], projection, row)
    record = subject['record']
    # The immutable foundation overlay already declared its subject kind as
    # project/product. New runtime records retain the raw carrier semantic kind.
    # Both still require this exact mapping, schema and identity; no entry changes.
    require(subject['kind'] in (row['carrier_kind'], row['endpoint_kind'])
        and ('kind' not in record or record['kind'] == row['carrier_kind']),
        'raw mapped carrier kind differs')
    require(pointer(record, row['instance_discriminator']['path']) == row['instance_discriminator']['value'],
        'mapped source discriminator differs')
    validate_schema(record, c['schema_path'], c.get('schema_selector'), projection['documents'])
    ident = pointer(record, row['identity_selector'])
    require(type(ident) is str and ident == subject['identity']
        and subject['version_ref'].startswith(ident + '@'), 'mapped source identity/revision differs')
    return row['endpoint_kind']


def carrier_kind(carrier, projection):
    row = mapping_for(carrier, projection)
    if row is None:
        return projection['contracts'][carrier]['semantic_kind']
    selected_contract(carrier, projection, row)
    return row['endpoint_kind']


def explain(subject, projection, *, allow_historical=False):
    represented = subject_kind(subject, projection, allow_historical=allow_historical)
    row = mapping_for(subject.get('carrier_ref'), projection)
    return {'version_ref': subject['version_ref'], 'identity_ref': subject['identity'],
        'carrier_kind': projection['contracts'][subject['carrier_ref']]['semantic_kind'] if subject.get('carrier_ref') in projection['contracts'] else subject['kind'],
        'source_projection_kind': subject['kind'], 'represented_endpoint_kind': represented,
        'carrier_ref': subject.get('carrier_ref'), 'effective_state': subject['effective_state'],
        'candidate_mapping_ref': row['candidate_mapping_ref'] if row else None,
        'mapping_binding': binding() if row else None, 'raw_subject_rewritten': False,
        'historical_endpoint_use':allow_historical,
        'authority_effect': 'none', 'actual_owner_outcome': None}
