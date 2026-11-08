#!/usr/bin/env python3
"""Check source-bound workspace navigation; optionally render its explanation.

No runtime, native registry, frozen Define Pack or original source is changed.
"""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
ROOT = PACKAGE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def pointer(body, selector):
    for token in selector.split('/')[1:]:
        key = token.replace('~1', '/').replace('~0', '~')
        body = body[int(key)] if isinstance(body, list) else body[key]
    return body


def link(source, title=None):
    if source['location'] == 'external':
        return '`' + source['path'] + '`'
    relative = os.path.relpath(ROOT / source['path'], PACKAGE)
    return '[' + (title or source['path']) + '](' + relative + ')'


def code(value):
    return chr(96) + str(value) + chr(96)


def render(data):
    counts = Counter(row['workspace_kind'] for row in data['entries'])
    lines = ['<!-- GENERATED from inventory/workspace-catalog.json by inventory/check_workspaces.py --render. -->', '',
        '# Product Workspaces and Project Workspaces', '',
        'Status: candidate hosting/catalog revision, ' + data['observed_client_date'] + '. Authority effect: none.', '',
        'Product Workspaces use ' + code('workspaces/products/') + '; Project Workspaces use ' + code('workspaces/projects/') + '. Both use shared operations by default. Catalog registration does not provision a runtime or change native authority.', '',
        'The active Lab map has **' + str(counts['product']) + ' Product Workspace candidates and ' + str(counts['project']) + ' Project Workspace candidates**. Three external workspaces are listed separately. Definition NFT and Lab migration are removed from the active plan. Ontology Lifecycle is an embedded Project of one Ontology Product Workspace.', '']
    for kind in ('product', 'project'):
        lines += ['## Active ' + kind.title() + ' Workspaces', '', '| Workspace | Existing source | Current material | Proposed home |', '| --- | --- | --- | --- |']
        for row in data['entries']:
            if row['workspace_kind'] != kind: continue
            ref = (row['identity_source'] or {'source_ref': row['source_refs'][0]})['source_ref']
            basis = code(row['subject_ref']) if row['subject_ref'] else row['basis'] + '; native identity unselected'
            homes = '<br>'.join(code(h) for h in row['current_homes'] if not h.startswith('/'))
            target = code(row['catalog_location'])
            if row['placement'] == 'repository-root-registration': target += '<br>physical home remains ' + code('.')
            lines.append('| **' + row['display_name'] + '** | ' + basis + '<br>' + link(data['sources'][ref], 'Source') + ' | ' + homes + ' | ' + target + ' |')
        lines.append('')
    lines += ['Craft development remains co-located with its Product; an independent physical Project home is optional. Relational theorem checker still needs an explicit identity/boundary choice.', '',
        '## External workspaces', '', '| Workspace | Existing checkout | Disposition |', '| --- | --- | --- |']
    for row in data['external_workspaces']:
        lines.append('| **' + row['display_name'] + '** | ' + code(row['external_root']) + ' | Editable source belongs externally. Lab cuts remain historical source/review evidence. |')
    lines += ['', 'These subjects have no proposed Lab-hosted Product or Project workspace. The [content comparison](inventory/external-comparison-20261107.json) checked 5,139 selected Lab files against explicit external source paths. No missing current source requiring migration was identified; no external file was overwritten.', '',
        'ARN has all 156 counterparts, with 13 publication-specific adaptations. Engineer Assessment has 4,983 retained Lab files spanning exact current matches, earlier versions, frozen review material and Lab contracts. Its originating brief is present with only a repaired relative link. Body War owns its local app model/docs; Craft canary examples and shared dependencies remain referenced.', '',
        '## One Ontology workspace', '',
        'Use ' + code('workspaces/products/ontology/') + ' for the Product interface, package implementation and embedded Ontology Lifecycle Project/engine. Keep Product identity ' + code('CA2-PRODUCT-ONTOLOGY') + ' and Project identity ' + code('CA2-PROJECT-CYBERALCHEMY-LAB-ONTOLOGY-LIFECYCLE') + ' distinct.', '',
        'The Product package turns source meaning into typed packages and retrieval interfaces. Lifecycle records changes and rebuilds state from event histories. Separate implementation packages can share one development workspace. An existing event-runtime Product candidate already composes them. See [the source-backed consolidation](ONTOLOGY-WORKSPACE.md).', '',
        '## Removed active entries', '', '| Entry | Disposition |', '| --- | --- |']
    for row in data['retired_entries']:
        lines.append('| ' + code(row['catalog_key']) + ' | ' + row['catalog_retirement']['reason'] + ' Historical source/admission bytes remain retained. |')
    lines += ['', 'Removing Lab migration from active planning is not a new native completion Decision. Its D71 Project/state/history references remain exact. Definition NFT has no active workspace or pending workspace work in this map; its unaccepted historical proposal remains in the migration ledger.', '',
        '## Remaining boundaries', '', '| Active entry | Open items |', '| --- | --- |']
    for row in data['entries']:
        lines.append('| ' + code(row['catalog_key']) + ' | ' + '<br>'.join(row['open_items']) + ' |')
    lines += ['', '## Existing plans and proposals', '', 'Associations are navigation proposals. External scope labels direct future editing outside Lab. Retained Lab cuts remain addressable; a plan does not automatically create another Project.', '',
        '| Existing scope | Navigation scope | Source |', '| --- | --- | --- |']
    for row in data['workstreams']:
        lines.append('| ' + code(row['current_home']) + ' | ' + code(row['proposed_scope']) + ' | ' + link(data['sources'][row['source_ref']], 'Read') + ' |')
    lines += ['', '## Imported and historical contexts', '', 'These references are not additional active workspaces. Withdrawn proposals are historical only.', '',
        '| Source scope | Subject | Association / disposition |', '| --- | --- | --- |']
    for row in data['imported_reference_scopes']:
        disposition = ', '.join(code(k) for k in row['related_entries']) or row['boundary_status']
        lines.append('| ' + link(data['sources'][row['source_ref']], Path(row['source_scope']).name) + ' | ' + row['title'] + ' | ' + disposition + ' |')
    lines += ['', '## Evidence and compatibility', '',
        '- [Machine catalog and source pins](inventory/workspace-catalog.json)',
        '- [Cleanup and content-audit result](CLEANUP-20261107.md)',
        '- [Ontology consolidation](ONTOLOGY-WORKSPACE.md)',
        '- [Boundary rules](WORKSPACE-BOUNDARIES.md)',
        '- [Required successor of the earlier Project-only model](MODEL-REVISION.md)', '',
        'The earlier profile and frozen Define Packs have not been converted to Product/Project kinds. This catalog performs no physical moves, native identity changes or runtime deployments. The [previous catalog](inventory/workspace-catalog-20261106.snapshot.json) remains historical.', '',
        'Check with ' + code('python3 architecture/workspace-model-mapping/inventory/check_workspaces.py') + '. Render with ' + code('--render') + '; write the local receipt with ' + code('--write-report') + '.']
    return '\n'.join(lines) + '\n'


def check(data):
    require(data['authority_effect'] == 'none' and data['status'] == 'candidate-navigation-not-admitted', 'catalog authority/status')
    require(data['terminology']['catalog_containers'] == ['workspaces/products/', 'workspaces/projects/'], 'workspace namespaces')
    require(data['runtime_policy'] == {'default': 'shared', 'per_workspace_installation_required': False,
        'specialization_requires_dedicated_execution': False, 'runtime_copies': 0, 'runtime_deployments': 0}, 'runtime policy')
    for ref, source in data['sources'].items():
        path = Path(source['path'])
        if source['location'] == 'repository':
            require(not path.is_absolute() and '..' not in path.parts, 'unsafe repository source')
            path = ROOT / path
        else:
            require(source['location'] == 'external' and path.is_absolute(), 'external source kind')
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == source['sha256'] and len(raw) == source['byte_length'], 'source drift: ' + source['path'])
    entries = data['entries']
    active_keys = [row['catalog_key'] for row in entries]
    retained = data['embedded_projects'] + data['retired_entries']
    external = data['external_workspaces']
    keys = active_keys + [row['catalog_key'] for row in retained + external]
    require(len(keys) == len(set(keys)), 'duplicate catalog entry')
    subject_rows = entries + retained + [subject for row in external for subject in row['subjects']]
    identities = [(row['workspace_kind'], row['subject_ref']) for row in subject_rows if row['subject_ref']]
    require(len(identities) == len(set(identities)), 'duplicate subject identity')
    for row in entries:
        kind = row['workspace_kind']
        require(kind in ('product', 'project') and row['catalog_key'].startswith(kind + '/'), 'kind mismatch')
        require(row['kind_label'] == ('Product Workspace' if kind == 'product' else 'Project Workspace'), 'label mismatch')
        require(row['catalog_location'] == 'workspaces/' + ('products/' if kind == 'product' else 'projects/') + row['catalog_key'].split('/')[1], 'catalog location')
        require(row['mapping_state'] == 'candidate-navigation-only', 'mapping promoted')
        require(set(row['related_entries']) <= set(keys), 'unresolved navigation association')
        require(row['source_refs'] and set(row['source_refs']) <= data['sources'].keys(), 'missing source binding')
        if row['identity_source']:
            source = data['sources'][row['identity_source']['source_ref']]
            path = Path(source['path']) if source['location'] == 'external' else ROOT / source['path']
            require(pointer(json.loads(path.read_text()), row['identity_source']['selector']) == row['subject_ref'], 'source identity mismatch: ' + row['catalog_key'])
    for row in subject_rows:
        if row.get('identity_source'):
            source = data['sources'][row['identity_source']['source_ref']]
            path = Path(source['path']) if source['location'] == 'external' else ROOT / source['path']
            require(pointer(json.loads(path.read_text()), row['identity_source']['selector']) == row['subject_ref'], 'retained identity mismatch')
    require({row['catalog_key'] for row in external} == {'external/body-war', 'external/engineer-assessment', 'external/agentic-research-network'}, 'external workspace selection')
    require(all(Path(row['external_root']).is_dir() for row in external), 'external checkout missing')
    require(not set(active_keys) & {'product/troqar','product/engineer-assessment','product/agentic-research-network','project/engineer-assessment-research','project/agentic-research-network-modeling','product/definition-nft','project/lab-migration','project/ontology-lifecycle'}, 'removed workspace resurrected')
    require({row['catalog_key'] for row in data['retired_entries']} == {'product/definition-nft','project/lab-migration'}, 'retired scope selection')
    require(len(data['embedded_projects']) == 1 and data['embedded_projects'][0]['host_workspace'] == 'product/ontology', 'Ontology consolidation')
    require(data['embedded_projects'][0]['subject_ref'] == 'CA2-PROJECT-CYBERALCHEMY-LAB-ONTOLOGY-LIFECYCLE', 'Ontology Project identity collapse')
    audit = json.loads((HERE / 'external-comparison-20261107.json').read_text())
    require(audit['review_status'] == 'complete-for-selected-source-paths' and audit['migration_required_files'] == [] and audit['files_copied'] == 0 and audit['external_writes'] == 0, 'migration audit disposition')
    require(sum(len(row['files']) for row in audit['results']) == 5139, 'comparison coverage')
    require(all(row.get('migration_disposition') for result in audit['results'] for row in result['files']), 'unreviewed source migration')
    # Effective standing comes from exact instance admission, not embedded raw candidate labels.
    admission_path = 'authority/admissions/cyberalchemy-lab-operational-foundation/v1/artifact-instance-admission.json'
    overlay = json.loads((ROOT / admission_path).read_text())
    for subject in ('product:cyberalchemy-lab', 'project:cyberalchemy-v2-to-lab-migration'):
        admitted = next(row for row in overlay['entries'] if row['identity_ref'] == subject)
        raw = (ROOT / admitted['admitted_instance_path']).read_bytes()
        require(admitted['lifecycle_state'] == 'admitted-current' and hashlib.sha256(raw).hexdigest() == admitted['admitted_instance_sha256'], 'D71 identity standing')
    expected = {p.relative_to(ROOT).as_posix() for parent in ('docs/plans', 'docs/proposals') for p in (ROOT / parent).iterdir() if p.is_dir() and not p.name.startswith(('.', '__'))}
    require({row['current_home'] for row in data['workstreams']} == expected, 'plan/proposal coverage drift')
    require(all(row['proposed_scope'] in keys for row in data['workstreams']), 'workstream scope')
    require({p.name for p in ROOT.iterdir() if p.name != '.git'} == {row['path'] for row in data['root_regions']}, 'root metadata coverage drift')
    expected_refs = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'evidence/migrations/cyberalchemy-v2-to-lab/executions').iterdir()
        if p.is_dir() and (p / 'README.md').is_file() and any(s in p.name for s in ['context', 'product-import', 'product-proposal', 'package-import', 'people-teams-runtime'])}
    require({row['source_scope'] for row in data['imported_reference_scopes']} == expected_refs, 'reference scope coverage drift')
    for row in data['imported_reference_scopes']:
        require(set(row['related_entries']) <= set(keys), 'reference scope association')
    require(data['model_compatibility']['existing_profile_is_project_only'] is True and
        data['model_compatibility']['product_project_discriminator_implemented'] is False, 'old profile compatibility overclaim')
    return {'status': 'pass', 'authority_effect': 'none', 'catalog_entries': len(entries), 'external_workspaces': len(external),
        'retired_entries': len(data['retired_entries']), 'embedded_projects': len(data['embedded_projects']),
        'by_kind': dict(Counter(row['workspace_kind'] for row in entries)),
        'typed_subject_identities': len(identities), 'source_pins': len(data['sources']),
        'plans_and_proposals': len(data['workstreams']), 'imported_reference_scopes': len(expected_refs),
        'root_entries': len(data['root_regions']), 'physical_moves': 0, 'runtime_operations': 0,
        'native_identities_created': 0, 'product_project_profile_implemented': False,
        'scope': 'source hashes, exact identity selectors, D71 overlay, navigation coverage and Markdown parity only'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--render', action='store_true')
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    data = json.loads((HERE / 'workspace-catalog.json').read_text())
    result = check(data)
    doc = PACKAGE / 'WORKSPACES.md'
    expected = render(data)
    if args.render:
        doc.write_text(expected)
    else:
        require(doc.read_text() == expected, 'catalog Markdown drift')
    for path in (doc, PACKAGE / 'WORKSPACE-BOUNDARIES.md', PACKAGE / 'MODEL-REVISION.md', PACKAGE / 'README.md', PACKAGE / 'CLEANUP-20261107.md', PACKAGE / 'ONTOLOGY-WORKSPACE.md'):
        for raw in re.findall(r'\[[^\]]*\]\(([^)]+)\)', path.read_text()):
            url = urlsplit(raw.strip('<>'))
            if url.scheme or raw.startswith('//'):
                continue
            target = (path.parent / unquote(url.path)).resolve() if url.path else path
            require(target.exists(), 'broken link: ' + str(path) + ': ' + raw)
    if args.write_report:
        (HERE / 'workspace-catalog-check.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
