"""Bind historical embedded source posture, current admission and the open Definition mapping."""
import json
import build_candidate as b


def verify(write=False):
    snap = b.snapshot()
    b.r.verify(snap, b.ROOT)
    source = b.source_ref(snap, 'cal.definition.governed-model')
    definition = b.source_ref(snap, 'cal.definition.definition')
    document = b.co.source_document(snap, source)
    definition_document = b.co.source_document(snap, definition)
    registry_path = b.ROOT / 'authority/definitions/registry.json'
    decision = next(row for row in snap['admission_decision_bindings']
                    if row['decision_ref'] == 'CAL-DECISION-0065-INTEGRATED-LAB-DEFINITION-MODEL-ADMISSION')
    paths = [b.ROOT / source['path'], b.ROOT / definition['path'], registry_path,
        b.ROOT / decision['path'], b.BASE / 'definitions/cal.definition.definition/correspondence.json',
        b.UNIT / 'correspondence.json', b.UNIT / 'verify_source_posture.py']
    bindings = [b.ref(path) for path in paths]
    registry = b.r.parse(b.r.read_bytes(b.ROOT, bindings[2]['path']), 'registry')
    admitted = b.r.parse(b.r.read_bytes(b.ROOT, bindings[3]['path']), 'decision')
    if bindings[3]['sha256'] != decision['sha256']:
        raise ValueError('Changed bound admission decision')
    entries = [row for row in registry['entries'] if row['definition_id'] == source['definition_id']
               and row['version'] == source['version_ref'].split('@', 1)[1]]
    admission_rows = [row for row in admitted['admitted_definitions'] if row['definition_ref'] == source['version_ref']]
    if len(entries) != 1 or len(admission_rows) != 1:
        raise ValueError('Wrong exact source/admission denominator')
    if any(entries[0][key] != source[key] for key in ['path', 'sha256']):
        raise ValueError('Registry source mismatch')
    if any(admission_rows[0][key] != source[key] for key in ['path', 'sha256']):
        raise ValueError('Decision source mismatch')
    if registry['current_lookup'][source['definition_id']] != source['version_ref']:
        raise ValueError('Not the current source')
    if entries[0]['lifecycle_state'] != 'admitted' or entries[0]['admission_decision_ref'] != admitted['decision_id'] or admitted['status'] != 'owner-admitted':
        raise ValueError('Wrong actual admission facts')
    embedded = document['source_refs'][0]
    if embedded['admission_posture'] != 'candidate-unadmitted' or embedded['source_admission_ref'] is not None:
        raise ValueError('Changed embedded source posture')
    if 'admitted source posture' not in definition_document['voices']['scientific_formal']['normative_statement']:
        raise ValueError('Changed comparison clause')
    packet = json.loads((b.UNIT / 'correspondence.json').read_bytes())
    if 'GM-SOURCE-005' not in {row['finding_id'] for row in packet['source_precedence']['conflicts']}:
        raise ValueError('Open source-posture finding omitted')
    report = {'schema_version': 'definition-assurance-governed-model-source-posture/v1-candidate',
        'status': 'PASS-for-exact-provenance-facts;semantic-mapping-unresolved',
        'authority_effect': 'none', 'input_refs': bindings, 'source': source,
        'Definition_counterpart_source': definition,
        'current_registry_lifecycle': entries[0]['lifecycle_state'],
        'current_exact_admission': {'decision_ref': admitted['decision_id'],
            'decision_status': admitted['status'], 'matched_source_count': 1,
            'excluded_effects': admitted['excluded_effects']},
        'embedded_source_reference': embedded,
        'historical_source_claim_ceiling': document['claim_ceiling'],
        'Definition_comparison': {'normative_selector': '/voices/scientific_formal/normative_statement',
            'normative_excerpt': definition_document['voices']['scientific_formal']['normative_statement'],
            'formal_selector': '/voices/scientific_formal/formal_expression',
            'formal_excerpt': definition_document['voices']['scientific_formal']['formal_expression']},
        'finding_id': 'GM-SOURCE-005', 'source_files_current': 201,
        'semantic_mapping': 'unresolved: no selected mapping connects AdmittedSources(d) to these embedded source-reference facts or makes current Definition admission promote its cited source',
        'logical_contradiction': 'not-established', 'source_fidelity': 'pending',
        'semantic_ready': False, 'mechanized_proof': False,
        'claim_ceiling': 'Exact read-only provenance facts and a source-bound review question. Existing Definition admission, cited-source admission, model-instance admission and new interpretation fidelity are distinct. No source repair, new promotion, universal source-posture rule or logical contradiction is claimed.'}
    for reference in bindings:
        if b.ref(b.ROOT / reference['path']) != reference:
            raise ValueError('Closing comparison-input drift')
    b.r.verify(snap, b.ROOT)
    if write:
        b.put('source-posture-review.json', report)
    elif not b.r.same_json(report, json.loads((b.UNIT / 'source-posture-review.json').read_bytes())):
        raise ValueError('Fresh source-posture review differs')
    return report


def main():
    result = verify('--write' in b.sys.argv)
    print(json.dumps({'result': result['status'], 'finding_id': result['finding_id'],
        'current_registry_lifecycle': result['current_registry_lifecycle'],
        'current_exact_admission_ref': result['current_exact_admission']['decision_ref'],
        'embedded_source_posture': result['embedded_source_reference']['admission_posture'],
        'logical_contradiction': 'not-established', 'semantic_ready': False,
        'source_files_current': 201}, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
