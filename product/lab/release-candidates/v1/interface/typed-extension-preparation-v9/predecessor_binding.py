"""Bind declared public catalog headers to immutable original predecessors.

Private host inputs only. This adapter authenticates no Actor or policy and
supplies no scope grant. Physical source metadata and public representation are
retained separately; the unchanged runtime consumes the original version ref.
"""
import copy
import importlib
from . import adapter as A


def bind_public_predecessors(proposal, *, projection, baseline, config,
                             representation_profile_bytes, expected_profile_sha256,
                             read_source_material):
    K = A.kernel()
    C = importlib.import_module(K.__package__ + '.common')
    A.require(type(representation_profile_bytes) is bytes
              and A.sha(representation_profile_bytes) == expected_profile_sha256,
              'independent representation profile pin differs')
    profile = A.parse(representation_profile_bytes)
    A.require(profile['authority_effect'] == 'none' and profile['actual_owner_outcome'] is None,
              'representation profile cannot grant authority')
    rows = profile['rows']
    refs = [r['represented_contract_ref'] for r in rows]
    current = {'admitted-current', 'local-admitted-current'}
    selected = {ref for ref, c in projection['contracts'].items() if c['lifecycle_state'] in current}
    historic = {'admitted-historical', 'local-admitted-historical'}
    selected_history = {ref for ref, c in projection['contracts'].items() if c['lifecycle_state'] in historic}
    current_rows = {r['represented_contract_ref'] for r in rows if r['lifecycle_state'] in current}
    historical_rows = {r['represented_contract_ref'] for r in rows if r['lifecycle_state'] in historic}
    A.require(len(refs) == len(set(refs)) and current_rows == selected
              and historical_rows == selected_history and set(refs) == selected | selected_history,
              'complete unique representation inventory differs')
    by_ref = dict(zip(refs, rows))
    bound = {}
    for target in proposal['targets']:
        predecessor = target['predecessor']
        if predecessor is None:
            continue
        public = A.public_header(predecessor)
        ref = public['version_ref']
        A.require(ref not in bound, 'duplicate predecessor in complete transaction')
        prior = projection['subjects'].get(ref)
        A.require(prior is not None and prior['effective_state'] in current,
                  'selected original predecessor is not current')
        source = prior['source']
        binding = {'ref': source['path'], 'sha256': source['sha256']}
        A.require(baseline['materials'].get(binding['ref']) == binding['sha256'],
                  'original predecessor outside signed material closure')
        raw = read_source_material(binding)
        A.require(type(raw) is bytes and A.sha(raw) == binding['sha256'],
                  'original predecessor file bytes differ')
        document = A.parse(raw)
        A.require(document == baseline['documents'][binding['ref']],
                  'original predecessor parsed document differs')
        selected_body = K.pointer(document, source['selector']) if source.get('selector') else document
        A.require(selected_body == prior['record'], 'original predecessor selected body differs')
        category = prior['category']
        if category == 'artifact-type':
            row = by_ref[ref]
            contract = projection['contracts'][ref]
            A.require(row['source_binding'] == {'path': contract['artifact_path'], 'sha256': contract['artifact_sha256']}
                      == {'path': binding['ref'], 'sha256': binding['sha256']},
                      'declared representation source binding differs')
            A.require(row['instance_schema_binding'] == {'ref': contract['schema_path'], 'sha256': contract['schema_sha256']}
                      and row['instance_schema_selector'] == contract['schema_selector'],
                      'declared representation instance schema differs')
            body = K.pointer(document, row['selector'])
            encoded = C.encoded(body) if row['selector'] else raw
            A.require(A.sha(encoded) == row['byte_sha256'] and len(encoded) == row['size_bytes']
                      and K.digest(body) == row['body_structural_sha256'],
                      'exact declared representation body bytes differ')
            carrier = row['meta_carrier_ref']
            A.require(carrier in selected and projection['contracts'][carrier]['semantic_kind'] == 'artifact-type',
                      'selected representation meta carrier differs')
            A.require(row['identity_ref'] == ref.rsplit('/', 1)[0], 'represented family identity differs')
            expected = {'scope_ref': config['scope_ref'], 'identity_ref': row['identity_ref'],
                        'version_ref': ref, 'carrier_ref': carrier, 'byte_sha256': row['byte_sha256']}
            kind = row['representation_kind']
        elif category == 'relation-kind':
            A.require(not source.get('encoding'), 'undeclared Relation Kind source encoding')
            carrier = prior['carrier_ref'] or prior['record'].get('classification', {}).get('artifact_type_ref')
            if carrier is None:
                matches = [r for r in selected if projection['contracts'][r]['semantic_kind'] == 'relation-kind'
                           and projection['contracts'][r]['instance_discriminator']['value'] == prior['record']['schema_version']]
                A.require(len(matches) == 1, 'Relation Kind discriminator is missing or ambiguous')
                carrier = matches[0]
            A.require(carrier in selected and projection['contracts'][carrier]['semantic_kind'] == 'relation-kind',
                      'selected Relation Kind carrier differs')
            encoded = C.encoded(selected_body) if source.get('selector') else raw
            expected = {'scope_ref': config['scope_ref'], 'identity_ref': prior['identity'],
                        'version_ref': ref, 'carrier_ref': carrier, 'byte_sha256': A.sha(encoded)}
            kind = 'explicit-relation-kind-classification-or-discriminator'
        else:
            raise A.WireFault('undeclared catalog predecessor category')
        A.require(public == expected and public['scope_ref'] == proposal['scope_ref'],
                  'exact public predecessor representation differs')
        bound[ref] = {'public_header': copy.deepcopy(public),
                     'original_predecessor_metadata': copy.deepcopy(prior),
                     'source_binding': binding, 'representation_kind': kind,
                     'runtime_predecessor_ref': ref,
                     'physical_carrier_ref': prior['carrier_ref'],
                     'semantic_record_scope_ref': prior['record'].get('scope_ref')}
    return {'schema_version': 'lab-public-catalog-predecessor-binding/v1-candidate',
            'result': 'PASS', 'representation_profile_sha256': expected_profile_sha256,
            'predecessors': bound, 'scope_grant_supplied': False,
            'actual_transport_authenticated': False, 'actual_public_calls': 0,
            'actual_transactions_written': 0, 'authority_effect': 'none', 'actual_owner_outcome': None}
