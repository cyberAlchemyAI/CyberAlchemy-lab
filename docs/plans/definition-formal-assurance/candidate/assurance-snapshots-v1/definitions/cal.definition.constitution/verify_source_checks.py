"""Actual Constitution artifact, source section and admission checks; live-source currentness stays partial."""
import ast
import copy
import json
import re
import types
from pathlib import Path
import build_candidate as b


def verify(write=False):
    context = json.loads((b.UNIT / 'context.json').read_bytes())
    for reference in context['sources']:
        if b.ref(b.ROOT / reference['path']) != reference: raise ValueError('Changed selected task input')
    b.external_current(context); snap = b.snapshot(); b.r.verify(snap, b.ROOT)
    source = b.source_ref(snap, 'cal.definition.constitution')
    document = b.co.source_document(snap, source)
    decision_binding = next(x for x in snap['admission_decision_bindings'] if x['decision_ref'] == 'CAL-DECISION-0053-FULL-DEFINITION-QUEUE-ADMISSION')
    helper_path = b.ROOT / 'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/author.py'
    paths = {'source': b.ROOT / source['path'],
        'schema': b.ROOT / 'authority/artifact-types/definition/v1/schema.json',
        'generator': b.ROOT / 'authority/artifact-types/definition/v1/generator.py', 'source_extractor': helper_path,
        'registry': b.ROOT / 'authority/definitions/registry.json', 'decision': b.ROOT / decision_binding['path'],
        'source_admissions': b.ROOT / 'authority/decisions/source-admission/full-definition-queue/v1/admissions.json',
        'source_projection': (b.ROOT / source['path']).with_name('DEFINITION.md'),
        'candidate_registry': (b.ROOT / source['path']).parents[3] / 'registry.json',
        'checker': b.UNIT / 'verify_source_checks.py','comparison': b.UNIT/'comparison-selection.json'}
    bindings = {name: b.ref(path) for name, path in paths.items()}
    raws = {name: b.r.read_bytes(b.ROOT, ref['path']) for name, ref in bindings.items()}
    if any(b.r.digest(raws[name]) != ref['sha256'] for name, ref in bindings.items()): raise ValueError('Capture drift')
    schema = b.r.parse(raws['schema'], 'schema'); b.c.Draft202012Validator.check_schema(schema)
    schema_errors = list(b.c.Draft202012Validator(schema).iter_errors(document))
    module = types.ModuleType('_bound_schema_renderer'); module.__file__ = str(paths['generator'])
    exec(compile(raws['generator'], str(paths['generator']), 'exec'), module.__dict__)
    before = copy.deepcopy(document); first = module.render(document).encode(); second = module.render(document).encode()
    if document != before: raise ValueError('Renderer mutated selected input')
    # Execute only the existing bounded extractor function, not the reconstruction writer.
    tree = ast.parse(raws['source_extractor'], filename=str(helper_path))
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'markdown_h2_section']
    if len(functions) != 1: raise ValueError('Ambiguous source extraction function')
    namespace = {'Path': Path, 're': re}
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(helper_path), 'exec'), namespace)
    external = context['external_sources'][0]; selected_path = Path(external['absolute_path'])
    section = namespace['markdown_h2_section'](selected_path, document['source_refs'][0]['selector'])
    section_sha = b.r.digest(section)
    registry = b.r.parse(raws['registry'], 'registry'); decision = b.r.parse(raws['decision'], 'decision')
    admissions = b.r.parse(raws['source_admissions'], 'source-admissions'); candidate = b.r.parse(raws['candidate_registry'], 'candidate-registry')
    entries = [x for x in registry['entries'] if x['definition_id'] == source['definition_id'] and x['version'] == source['version_ref'].split('@', 1)[1]]
    local_entries = [x for x in candidate['entries'] if x['definition_ref'] == source['version_ref']]
    admission_rows = [x for x in admissions['admissions'] if x['source_ref'] == document['source_refs'][0]['source_ref'] and x['selector'] == document['source_refs'][0]['selector']]
    if len(entries) != 1 or len(admission_rows) != 1: raise ValueError('Ambiguous exact current/source-admission selection')
    selected_admission = admission_rows[0]
    checks = [
        {'check_id': 'stable-authority-identity', 'result': document['definition_id'] == 'cal.definition.constitution'},
        {'check_id': 'source-schema-digest-current', 'result': document['schema_digest'] == bindings['schema']['sha256']},
        {'check_id': 'source-generator-digest-current', 'result': document['source_direction']['generator_sha256'] == bindings['generator']['sha256']},
        {'check_id': 'source-Definition-v1-schema-valid', 'result': not schema_errors},
        {'check_id': 'two-renders-byte-identical', 'result': first == second},
        {'check_id': 'existing-projection-exact', 'result': first == raws['source_projection']},
        {'check_id': 'selected-D58-section-digest-current', 'result': section_sha == document['source_refs'][0]['content_sha256'] == selected_admission['selected_sha256']},
        {'check_id': 'selected-local-file-exact-admission-bytes', 'result': external['sha256'] == selected_admission['source_file_sha256_at_admission']},
        {'check_id': 'decision-exactly-binds-source-admission-record', 'result': bindings['decision']['sha256'] == decision_binding['sha256'] and bindings['source_admissions']['path'] == decision['admitted_source_selection']['path'] and bindings['source_admissions']['sha256'] == decision['admitted_source_selection']['sha256']},
        {'check_id':'D58-admitted-for-single-Constitution-target','result':selected_admission['status']=='admitted-for-definition-use' and selected_admission['target_definition_refs']==[source['version_ref']] and selected_admission['decision_ref']==admissions['admission_decision_ref']==decision['decision_id']},
        {'check_id': 'current-schema-registry-binding-and-admission', 'result': registry['current_lookup'][source['definition_id']] == source['version_ref'] and all(entries[0][key] == source[key] for key in ['path', 'sha256']) and entries[0]['lifecycle_state'] == 'admitted' and entries[0]['admission_decision_ref'] == decision['decision_id']},
        {'check_id': 'historical-candidate-registry-exactly-one-source', 'result': len(local_entries) == 1 and local_entries[0]['path'] == source['path'] and local_entries[0]['sha256'] == source['sha256'] and local_entries[0]['target_id'] == 'semantic.constitution'}]
    comparison=json.loads(raws['comparison']);b.unchanged(comparison['selected_refs']);marker='Bound source-semantic basis:\n\n'
    core=json.loads((b.UNIT/'t.json').read_bytes())['payload'];enc=[x for x in core['clauses'] if x['disposition']=='encoded']
    checks.append({'check_id':'no-comparison-import-no-sufficient-approval-assumption','result':comparison['comparison_assembled_into_primary_T'] is False and comparison['source_precedence_reviewed'] is False and len(enc)==9 and sum(x['source_selector']=='/voices/scientific_formal/formal_expression' for x in enc)==4 and not core['assumptions']})
    contextual=context['external_sources'][1];contextual_bytes=Path(contextual['absolute_path']).read_bytes()
    checks.append({'check_id':'referenced-full-legacy-model-exact-contextual-copy-not-admitted-theory','result':comparison['external_context_refs']==context['external_sources'][1:] and b.r.digest(contextual_bytes)==contextual['sha256'] and len(contextual_bytes)==9018 and '../AUTHORITY-MODEL.md' in document['voices']['domain_context']['explanation']})
    schema_context=context['external_sources'][2];schema_bytes=Path(schema_context['absolute_path']).read_bytes();schema_rows=[x for x in schema_bytes.decode().splitlines() if x.startswith('| `CAV2-D58-SCHEMA` |')]
    if len(schema_rows)!=1:raise ValueError('Ambiguous documentary D58 row')
    schema_row=(schema_rows[0]+'\n').encode();instance_context=context['external_sources'][3];instance_bytes=Path(instance_context['absolute_path']).read_bytes()
    checks.append({'check_id':'referenced-documentary-D58-schema-not-activated','result':b.r.digest(schema_bytes)==schema_context['sha256'] and b'tracked (documentary)' in schema_row and b'no constitution or validator activation' in schema_row})
    checks.append({'check_id':'referenced-repository-Constitution-remains-an-unimported-candidate','result':b.r.digest(instance_bytes)==instance_context['sha256'] and b'Status: candidate' in instance_bytes and b'Canonical concept: [CAV2-D58 Constitution]' in instance_bytes})
    if not all(x['result'] is True for x in checks): raise ValueError(json.dumps(checks))
    producer_path = b.ROOT.parent / 'domainspec-core/cyberAlchemy-v2/authority/definitions/DEFINITIONS.md'
    report = {'schema_version': 'definition-assurance-Constitution-source-checks/v1-candidate',
        'status': 'PASS-for-exact-artifact-source-section-and-admission-checks', 'authority_effect': 'none',
        'source': source, 'selected_inputs': bindings, 'external_source_ref': external,'external_model_context_ref':contextual,'external_schema_context_ref':schema_context,'external_candidate_instance_context_ref':instance_context,'documentary_schema_row_sha256':b.r.digest(schema_row),'contextual_document_admitted_into_primary_theory':False,
        'checks': checks, 'first_render_sha256': b.r.digest(first), 'second_render_sha256': b.r.digest(second),
        'projection_bytes': len(first), 'selected_source_section_sha256': section_sha, 'selected_source_section_bytes': len(section),
        'source_section_extraction_policy': 'Exact bound author.markdown_h2_section function: unique CAV2 heading to next CAV2 heading, outer trailing whitespace replaced with one newline.',
        'selected_source_admission': selected_admission, 'current_registry_entry_lifecycle': entries[0]['lifecycle_state'],
        'current_registry_admission_ref': entries[0]['admission_decision_ref'], 'historical_embedded_source_posture': document['source_refs'][0]['admission_posture'],
        'source_location': {'producer_declared_file': str(producer_path), 'producer_declared_file_exists': producer_path.is_file(),
            'selected_local_copy': str(selected_path), 'selected_file_matches_admission_file_sha256': True,
            'producer_configuration_changed': False, 'repository_identity_authenticated': False},
        'source_testable_conditions': [
            {'selector': '/voices/scientific_formal/testable_conditions/0', 'result': 'PASS-for-exact-selected-identity'},
            {'selector': '/voices/scientific_formal/testable_conditions/1', 'result': 'PARTIAL: selected-local-copy-digest-matches; declared-live-producer-file-absent and repository/root currentness not authenticated'},
            {'selector': '/voices/scientific_formal/testable_conditions/2', 'result': 'PASS-for-selected-Definition-v1-record'},
            {'selector': '/voices/scientific_formal/testable_conditions/3', 'result': 'PASS-for-exact-selected-generated-projection'}],
        'canonical_legacy_source_currentness': 'not-established; only selected local bytes checked',
        'source_inner_claim_ceiling': document['claim_ceiling'], 'source_precedence': 'CON-PRECEDENCE-001 and other candidate denotation/scope findings remain unresolved',
        'source_fidelity': 'pending', 'semantic_ready': False, 'mechanized_proof': False,
        'claim_ceiling': 'Sixteen actual read-only checks of one Definition artifact, exact D58 section and single-target recorded admission plus referenced legacy Model context bytes. Source-use facts do not admit the full referenced document or accept interpretation fidelity. No live producer currentness, actual instance adoption or application, sufficient approval or whole meaning proof established.'}
    for name, path in paths.items():
        if b.ref(path) != bindings[name]: raise ValueError('Closing selected-input drift')
    b.external_current(context); b.r.verify(snap, b.ROOT)
    if write:
        for name, raw in [('source-render-1.md', first), ('source-render-2.md', second), ('legacy-source-section.md', section),('legacy-model-context.md',contextual_bytes),('legacy-schema-row-context.md',schema_row),('legacy-candidate-constitution-context.md',instance_bytes)]:
            with (b.UNIT / name).open('xb') as stream: stream.write(raw)
        b.put('source-checks.json', report)
    elif not b.r.same_json(report, json.loads((b.UNIT / 'source-checks.json').read_bytes())) or first != (b.UNIT / 'source-render-1.md').read_bytes() or second != (b.UNIT / 'source-render-2.md').read_bytes() or section != (b.UNIT / 'legacy-source-section.md').read_bytes() or contextual_bytes!=(b.UNIT/'legacy-model-context.md').read_bytes() or schema_row!=(b.UNIT/'legacy-schema-row-context.md').read_bytes() or instance_bytes!=(b.UNIT/'legacy-candidate-constitution-context.md').read_bytes():
        raise ValueError('Fresh source evidence differs')
    return report


def main():
    report = verify('--write' in b.sys.argv)
    print(json.dumps({'result': report['status'], 'checks': len(report['checks']), 'render_bytes': report['projection_bytes'],
        'render_sha256': report['first_render_sha256'], 'source_section_bytes': report['selected_source_section_bytes'],
        'source_section_sha256': report['selected_source_section_sha256'], 'current_registry_entry_lifecycle': report['current_registry_entry_lifecycle'],
        'producer_declared_file_exists': report['source_location']['producer_declared_file_exists'],
        'source_fidelity': 'pending', 'semantic_ready': False}, indent=2, sort_keys=True))


if __name__ == '__main__': main()
