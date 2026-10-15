"""Generate a draft operation reference from explicitly selected public inputs.

Imports no Lab code and starts no service. Exact input selection is required;
this is neither a runtime qualification nor a documentation publication.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re

HERE = Path(__file__).absolute().parent
ROOT = HERE.parents[6]

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def parse(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate selected JSON key')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs)

def exact(binding):
    path = Path(binding['path'])
    if path.is_absolute() or '..' in path.parts or path.as_posix() != binding['path']:
        raise ValueError('noncanonical documentation input')
    raw = (ROOT / path).read_bytes()
    if sha(raw) != binding['sha256'] or ('size_bytes' in binding and len(raw) != binding['size_bytes']):
        raise ValueError('selected documentation bytes changed: ' + path.as_posix())
    return raw

def link(label, path, output):
    target = os.path.relpath(path, output.parent).replace(os.sep, '/')
    return '[' + label + '](' + target + ')'

def bullets(items):
    return '\n'.join('- ' + str(item) for item in items) or 'None declared.'

def filename(operation):
    if re.fullmatch(r'[a-z]+(?:\.[a-z]+)+', operation) is None:
        raise ValueError('unsupported operation name')
    return operation.replace('.', '-') + '.md'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--selection-sha256', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    selection_path = HERE / 'input-selection.json'
    raw = selection_path.read_bytes()
    if sha(raw) != args.selection_sha256:
        raise ValueError('independent documentation selection differs')
    s = parse(raw)
    if s['authority_effect'] != 'none' or s['operation_count'] != 34 or s['outputs_publishable'] is not False:
        raise ValueError('draft selection standing differs')
    exact(s['selected_source']); profile = parse(exact(s['selected_profile']))
    public = {row['path']: row for row in s['public_inputs']}
    for binding in public.values():
        exact(binding)
    catalog = parse(exact(s['catalog'])); resources = parse(exact(s['resources']))
    operations = catalog['operations']; names = [row['operation'] for row in operations]
    if len(set(names)) != 34 or set(names) != set(profile['implemented_operations']):
        raise ValueError('complete selected operation accounting differs')
    implementations = {row['operation']: row for row in s['implementation_rows']}
    if set(implementations) != set(names):
        raise ValueError('implementation map omits an operation')
    remapped = {row['original_uri']: row for row in resources['resources']}
    local_by_uri = {}
    for row in s['local_runtime_schemas']:
        schema = parse(exact(row['binding']))
        if schema['$id'] != row['resource_uri'] or row['binding']['path'] not in public:
            raise ValueError('local runtime schema selection differs')
        if row['resource_uri'] in local_by_uri:
            raise ValueError('duplicate local runtime schema ID')
        local_by_uri[row['resource_uri']] = row
    if {k: row['selected_uri'] for k, row in remapped.items()} != resources['uri_mapping']:
        raise ValueError('protocol resource map differs')
    out = HERE / args.output
    if out.parent != HERE or out.exists():
        raise ValueError('exclusive owned output required')
    out.mkdir(); (out / 'operations').mkdir()
    emitted = []; index_rows = []
    def emit(path, text):
        with path.open('x') as stream:
            stream.write(text)
        emitted.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes())})
    for operation in operations:
        name = operation['operation']; path = out / 'operations' / filename(name)
        mapped = implementations[name]; exact(mapped['candidate_implementation'])
        text = '# ' + name + '\n\n' + operation['description'] + '\n\n'
        text += 'Draft reference for the selected API17 capture. Final current operation qualification is pending. '
        text += link('Reference scope and recovery', out / 'README.md', path) + '.\n\n'
        text += '## Effects and permission\n\n'
        text += '- Declared effect: `' + operation['effect_kind'] + '`.\n'
        text += '- Dispatcher branch: `' + mapped['branch'] + '`.\n'
        text += '- Caller requirement: `' + operation['authority']['caller_requirement'] + '`.\n'
        text += '- Trusted channel required: `' + str(operation['authority']['trusted_channel_required']).lower() + '`.\n'
        text += '- Public message claims grant authority: `' + str(operation['authority']['message_claims_grant_authority']).lower() + '`.\n'
        text += '- Repository admission possible in this contract: `' + str(operation['repository_admission_possible']).lower() + '`.\n'
        text += '\nRequired obligations: ' + ', '.join('`' + x + '`' for x in operation['authority']['required_obligation_refs']) + '.\n\n'
        text += 'Declared external effects: ' + (', '.join('`' + x + '`' for x in operation['external_effect_refs']) or 'none') + '.\n\n'
        text += '## Request, result and error schemas\n\n'
        for field, label in [('request_schema', 'Request'), ('result_schema', 'Result'), ('error_schema', 'Error')]:
            value = operation[field]; exact(public[value['ref']])
            text += '- ' + label + ': ' + link('original schema', ROOT / value['ref'], path) + '; resource `' + value['resource_uri'] + '`.\n'
            original, separator, fragment = value['resource_uri'].partition('#')
            selected = remapped.get(original)
            if selected:
                selected = {**selected, 'selected_binding': local_by_uri[selected['selected_uri']]['binding']} if selected['selected_uri'] in local_by_uri else selected
                exact(public[selected['selected_binding']['path']])
                text += '  Selected runtime resource: ' + link('versioned schema', ROOT / selected['selected_binding']['path'], path)
                text += '; `' + selected['selected_uri'] + (separator + fragment if separator else '') + '`.\n'
        text += '\nAllowed domain errors: ' + ', '.join('`' + x + '`' for x in operation['allowed_error_codes']) + '.\n\n'
        text += 'Transport refusals are checked separately from domain errors. A response envelope alone does not prove the domain outcome.\n\n'
        text += '## Before calling\n\n' + bullets(operation['preconditions']) + '\n\n'
        text += 'Source-cut selectors: ' + ', '.join('`' + x + '`' for x in operation['source_cut_selectors']) + '.\n\n'
        text += operation['deadline_rule'] + '\n\n'
        text += '## Idempotency and recovery\n\n'
        text += 'Idempotency key required: `' + str(operation['idempotency_required']).lower() + '`.\n\n'
        text += operation['idempotency_rule'] + '\n\n'
        text += 'Namespace: ' + ', '.join('`' + x + '`' for x in operation['idempotency_namespace']) + '.\n\n'
        if operation['inner_idempotency_selector'] is not None:
            text += 'Inner command-key selector: `' + str(operation['inner_idempotency_selector']) + '`.\n\n'
        text += 'After a possible effect, preserve the exact original request and inspect its operation journal under current authorization. Pending or uncertain keys must not automatically redispatch.\n\n'
        text += '## Assessing the result\n\n' + bullets(operation['postconditions']) + '\n\n' + operation['completion_rule'] + '\n\n'
        text += '## Implementation and evidence\n\n'
        text += link('General candidate implementation route', ROOT / mapped['candidate_implementation']['path'], path) + '. '
        text += 'This is a source locator, not proof that the complete operation passed.\n\n'
        if 'current_implementation' in mapped:
            exact(mapped['current_implementation']); exact(mapped['current_host'])
            text += mapped['current_condition'] + '\n\n'
            text += link('Current Source8 route', ROOT / mapped['current_implementation']['path'], path) + ' selects ' + link('the current host implementation', ROOT / mapped['current_host']['path'], path) + '. The general route remains selected for other supported source families. These are conditional code selections, not complete current operation qualification.\n\n'
        text += 'The catalog retains its original `' + operation['implementation_status'] + '` authoring label. '
        text += 'API17 implementation and execution evidence have separate standing. Final same-candidate all34 operation and security coverage remains pending.\n'
        emit(path, text)
        index_rows.append('| ' + link('`' + name + '`', path, out / 'README.md') + ' | ' + operation['effect_kind'] + ' | ' + mapped['branch'] + ' | Pending final qualification |')
    readme = '# Lab API operation reference\n\n'
    readme += 'Documentation draft for the API17 input capture selected on 14 October 2026. The composite declares 34 operations across base, Action and Governance branches. '
    readme += 'These pages explain exact declared contracts and selected resource remapping; they do not establish final runtime qualification, current operator installation, owner acceptance or release.\n\n'
    readme += 'The historical catalog authoring labels describe the catalog package. Candidate implementation files are selected separately and linked on each page. '
    readme += 'A result envelope must be assessed against its domain posture and evidence. Paperclip reader integration does not establish autonomous engineering or research task execution.\n\n'
    readme += '| Operation | Declared effect | Branch | Current execution standing |\n| --- | --- | --- | --- |\n' + '\n'.join(index_rows) + '\n\n'
    readme += '## Authentication, calls and replies\n\n'
    for field, label in [('call_schema_binding', 'Call envelope'), ('reply_schema_binding', 'Reply envelope'), ('transport_error_schema_binding', 'Transport refusal'), ('trusted_context_schema_binding', 'Trusted caller context')]:
        readme += '- ' + link(label, ROOT / catalog[field]['ref'], out / 'README.md') + '.\n'
    readme += '\nThe envelope links above retain the original catalog declaration. API17 selects its local v2 call and reply schemas and separately selects its authentication schema. These local registrations also override matching resource IDs after the versioned resource map; referenced resources follow that registry selection.\n\n'
    readme += '### Selected local runtime schemas\n\n'
    for row in s['local_runtime_schemas']:
        readme += '- ' + link(row['name'], ROOT / row['binding']['path'], out / 'README.md') + '; resource `' + row['resource_uri'] + '`.\n'
    readme += '\nThe maintained composition authenticates independent branches. An opaque public context locator or message Actor is not a grant. Each selected branch repeats its current source, principal, scope, policy, nonce and expiry checks.\n\n'
    readme += '## Currentness and recovery\n\n' + bullets(catalog['global_rules']) + '\n\n'
    readme += '## Exact inputs and publication standing\n\n'
    readme += 'The generator checks directly displayed contract/schema/code inputs. This is not a self-contained $ref registry or a full schema-validity proof. The runtime separately selects the remaining domain, dependency and storage schema registrations.\n\n'
    readme += link('Additional selected typed-relation schema', ROOT / s['additional_typed_relation_schema']['path'], out / 'README.md') + ' is also directly bound.\n\n'
    readme += link('Documentation input selection', selection_path, out / 'README.md') + ' binds the public contract and schema files used here. '
    readme += 'The source manifest is a captured input inventory; unavailable historical physical inputs remain a separate unresolved proof obligation. '
    readme += 'The selected API is an unfrozen successor candidate. Fresh execution freeze, full operation/security qualification, installation walkthrough, website integration and Markdown import remain required for T21 completion.\n'
    emit(out / 'README.md', readme)
    for binding in public.values():
        exact(binding)
    exact(s['selected_source']); exact(s['selected_profile'])
    (out / 'generated-manifest.json').write_text(json.dumps({'schema_version': 'lab-T21-generated-reference/v1-candidate', 'authority_effect': 'none', 'input_selection_sha256': args.selection_sha256, 'operation_count': 34, 'files': emitted, 'runtime_imported_or_executed': False, 'website_integrated': False, 'operator_recipe_verified': False, 'task_complete': False}, sort_keys=True, indent=2) + '\n')
    print(json.dumps({'result': 'GENERATED-draft-reference', 'operation_pages': len(operations), 'public_inputs_checked': len(public), 'runtime_executed': False}))

if __name__ == '__main__':
    main()
