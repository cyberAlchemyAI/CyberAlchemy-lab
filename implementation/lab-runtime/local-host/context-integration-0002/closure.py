"""Exact current metadata inventory and unresolved Context input classes."""
from __future__ import annotations

import collections
import datetime as dt
import json
from pathlib import Path

import admission as A

AUDIT = A.REPO / 'implementation/lab-runtime/local-host/context-construction-0003/historical-closure-candidates.json'
AUDIT_SHA = 'e02c3061ee705d826f02d74887340ce85047ef989491dfddfdf1e3590aec350a'


def plan(now: dt.datetime):
    observed = A.verify(now)
    selected = A.selection()
    audit = json.loads(A.read_exact(AUDIT, AUDIT_SHA))
    states = dict(sorted(collections.Counter(row['state'] for row in audit['rows']).items()))
    A.require(len(audit['rows']) == 1804 and states == {
        'historical_family_requires_projection': 318,
        'protected_archive_excluded': 6,
        'unselected_candidate': 1480,
    }, 'historical closure audit changed')
    source, reader = selected['source'], selected['reader']
    existing = [
        {'role': 'source_source', 'path': source['source_manifest_path'],
         'sha256': source['source_manifest_sha256']},
        {'role': 'source_package', 'path': source['package_manifest_path'],
         'sha256': source['package_manifest_sha256']},
        {'role': 'source_period', 'path': source['period_path'],
         'sha256': source['period_sha256']},
        {'role': 'reader_source', 'path': reader['source_manifest_path'],
         'sha256': reader['source_manifest_sha256']},
        {'role': 'reader_code', 'path': reader['reader_code_path'],
         'sha256': reader['reader_code_sha256']},
        {'role': 'reader_receipt', 'path': reader['receipt_path'],
         'sha256': reader['receipt_sha256']},
    ]
    A.require(len({row['path'] for row in existing}) == 6 and
              all(not row['path'].endswith('branch.snapshot') for row in existing),
              'selected metadata inventory differs')
    return {
        'schema_version': 'lab-context-inert-closure-map/v1',
        'status': 'PARTIAL_SOURCE_READER_ONLY',
        'observed_at': observed['observed_at'],
        'period_expires_at': observed['period_expires_at'],
        'selected_existing_metadata': existing,
        'dependency_order': ['source_source', 'source_package', 'reader_source',
                             'mapper_source', 'mapper_package', 'context_source', 'context_package'],
        'reader_package': 'DOES_NOT_EXIST_BY_DESIGN',
        'historical_context_rows': 1804,
        'historical_row_states': states,
        'reader_implementation_binding': 'CANDIDATE_CODE_ONLY_REQUIRES_SAME_FAMILY',
        'development_authorization': 'UNSELECTED_CONSTRUCTION_INPUT',
        'protected_issuer_grant': 'NOT_SUPPLIED_BY_DEVELOPMENT_AUTHORIZATION',
        'control_AUTH_path_and_sha_projection': 'UNSELECTED',
        'api_v25_fact_scope_schema_runtime': 'UNSELECTED_COMPLETE_CLOSURE',
        'mapper_source': 'UNSELECTED', 'mapper_package': 'UNSELECTED',
        'mapper_native_byte_parity': 'UNSELECTED',
        'context_source_manifest': 'REFUSED', 'context_launch': 'REFUSED',
        'authority_effect': 'none', 'actual_owner_outcome': None,
        'archive_body_read': False,
    }
