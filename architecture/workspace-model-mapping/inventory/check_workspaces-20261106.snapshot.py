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


def render(data):
    lines = ['<!-- GENERATED from inventory/workspace-catalog.json by inventory/check_workspaces.py --render. -->', '',
        '# Product Workspaces and Project Workspaces', '',
        'Status: candidate naming and source-backed scope catalog, 6 November 2026. Authority effect: none.', '',
        '**Product Workspace** is the display label for a durable Product scope; **Project Workspace** is the label for a coordinated initiative. The catalog namespaces are `workspaces/products/` and `workspaces/projects/`. These are local planning labels, not newly admitted Definitions.', '',
        'Both kinds use the eight responsibilities and shared operations. A Product can be advanced by several Projects. A Project references its Product or another declared purpose. A distinct catalog entry does not require a separate physical directory, database, runtime or copied business record.', '',
        'This catalog has 12 Product-scope entries and 7 Project-scope entries. These are not 19 established operating workspaces: the list includes identities, documented Products, unaccepted proposals, one boundary proposal, a plan-only Project candidate and one external checkout. Only Craft has the previously authored candidate Lab Workspace profile in this selection.', '',
        '## Product Workspaces', '',
        '| Catalog name | Existing source / identity basis | Current material | Proposed location or registration |',
        '| --- | --- | --- | --- |']
    for row in data['entries']:
        if row['workspace_kind'] != 'product':
            continue
        src = data['sources'][(row['identity_source'] or {'source_ref': row['source_refs'][0]})['source_ref']]
        basis = '`' + row['subject_ref'] + '`' if row['subject_ref'] else row['basis'] + '; native identity unselected'
        current = '<br>'.join('`' + h + '`' for h in row['current_homes'])
        target = '`' + row['catalog_location'] + '`'
        if row['placement'] == 'repository-root-registration':
            target += '<br>physical home remains `.`'
        if row['placement'] == 'external-registration':
            target += '<br>external home retained'
        lines.append('| **' + row['display_name'] + '**<br>`' + row['catalog_key'] + '` | ' + basis + '<br>' + link(src, 'Exact source') + ' | ' + current + ' | ' + target + ' |')
    lines += ['', '## Project Workspaces', '',
        '| Catalog name | Existing source / identity basis | Product / related scope | Proposed location |',
        '| --- | --- | --- | --- |']
    for row in data['entries']:
        if row['workspace_kind'] != 'project':
            continue
        src = data['sources'][(row['identity_source'] or {'source_ref': row['source_refs'][0]})['source_ref']]
        # Keep external source content in the pinned JSON; link the retained local plan for navigation.
        if src['location'] == 'external':
            src = next(data['sources'][ref] for ref in row['source_refs'] if data['sources'][ref]['location'] == 'repository' and data['sources'][ref]['path'].endswith('PLAN.md'))
        basis = '`' + row['subject_ref'] + '`' if row['subject_ref'] else 'Plan/work-pack only; native Project identity unselected'
        related = '<br>'.join('`' + key + '`' for key in row['related_entries'])
        lines.append('| **' + row['display_name'] + '**<br>`' + row['catalog_key'] + '` | ' + basis + '<br>' + link(src, 'Source / retained plan') + ' | ' + related + ' | `' + row['catalog_location'] + '` |')
    lines += ['', 'Craft development is currently co-located with the Craft Product. Its separate Project catalog entry exposes the existing coordination identity; `projects/craft-development/` is only a possible independent home, requiring a boundary and primary-source transition before use. TROQAR is likewise one external checkout with local Product/Project labels, not two copied workspaces.', '',
        'Ontology Lifecycle maps to its existing Project ownership. The Ontology Product keeps its own Product identity. Their application/library/Product dependency boundary is unresolved; this catalog does not invent a separate Ontology Lifecycle Product or merge the existing subjects.', '',
        '## Subject standing and open boundaries', '',
        '| Catalog key | What exists / standing | Remaining work |', '| --- | --- | --- |']
    for row in data['entries']:
        lines.append('| `' + row['catalog_key'] + '` | ' + row['subject_standing'] + ' | ' + '<br>'.join(row['open_items']) + ' |')
    lines += ['', '## Proposed physical convention', '', '```text',
        'CyberAlchemy-lab/                  # Lab Product workspace stays at repository root',
        '  product/ project/ work/ authority/ ontology/ architecture/ implementation/ docs/',
        '  workspaces/', '    products/',
        '      craft/ define/ ontology/ people-and-teams/',
        '      engineer-assessment/ agentic-research-network/ lab-website/',
        '      trusted-dataset-materialization/ definition-nft/',
        '      # agent-reasoning-engine: upstream reference until explicitly imported',
        '      # cyberalchemy-lab: root registration; troqar: external registration',
        '    projects/',
        '      lab-migration/ ontology-lifecycle/ definition-formal-assurance/',
        '      engineer-assessment-research/ agentic-research-network-modeling/',
        '      # craft-development: currently co-located; independent home optional',
        '      # relational-theorem-checker: identity / boundary still pending', '```', '',
        'The tree is a candidate destination convention. No container, folder move, native workspace identity or runtime installation is created by this catalog. Exact frozen admission and import material stays retained; only selected authored records could later receive new current homes.', '',
        '## Existing plans and proposals', '',
        'Every first-level `docs/plans/` and `docs/proposals/` scope is listed. Associations below are navigation proposals, not newly asserted Project ownership, Goal membership or Typed Relations. A plan, design, migration phase or research package does not automatically become another Project Workspace.', '',
        '| Existing scope | Proposed navigation scope | Source |', '| --- | --- | --- |']
    for row in data['workstreams']:
        lines.append('| `' + row['current_home'] + '` | `' + row['proposed_scope'] + '` | ' + link(data['sources'][row['source_ref']], 'Read scope') + ' |')
    lines += ['', '## Imported and referenced contexts', '',
        'The following source packages remain visible. Imported meaning, capability registration and a prepared context do not establish a new Product/Project workspace. Unlinked contexts retain an unresolved boundary; they are not silently assigned to a Product.', '',
        '| Source scope | Existing subject | Catalog association / disposition |', '| --- | --- | --- |']
    for row in data['imported_reference_scopes']:
        lines.append('| ' + link(data['sources'][row['source_ref']], Path(row['source_scope']).name) + ' | ' + row['title'] + ' | ' + (', '.join('`' + key + '`' for key in row['related_entries']) or row['boundary_status']) + ' |')
    lines += ['', '## Coverage, authority and model compatibility', '',
        'The machine catalog also records every current root entry except `.git`, without reading private stores or ignored runtime content. Shared capability code, context packages, fixtures, generated compiler projects, replay stores, frozen snapshots, Goals and individual Person/Team records are not additional workspaces merely because they have directories or IDs.', '',
        'The Lab Product and migration Project use the exact D71 instance-admission overlay; immutable embedded candidate labels remain provenance. Other candidates keep their source standing. Product Identity/v2 being an admitted carrier does not admit every Product instance.', '',
        'This catalog does not convert the earlier Project-only Workspace Definition/profile. That earlier candidate and its three frozen Define Packs remain exact. The [required model revision](MODEL-REVISION.md) names the concrete discriminator, cardinality, binding and fixture changes needed before either kind can be represented operationally.', '',
        '- [Machine catalog, all source hashes and root dispositions](inventory/workspace-catalog.json)',
        '- [Boundary rules](WORKSPACE-BOUNDARIES.md)',
        '- [Model revision and drift obligations](MODEL-REVISION.md)',
        '- [Earlier candidate model](../../docs/proposals/0012-lab-workspace-model/README.md)', '',
        'Validation: `python3 architecture/workspace-model-mapping/inventory/check_workspaces.py`. Render after an intentional catalog edit with `--render`; write only this catalog check receipt with `--write-report`. The older path/source inventory remains its dated snapshot and is not silently refreshed.']
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
    keys = [row['catalog_key'] for row in entries]
    require(len(keys) == len(set(keys)), 'duplicate catalog entry')
    identities = [(row['workspace_kind'], row['subject_ref']) for row in entries if row['subject_ref']]
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
    return {'status': 'pass', 'authority_effect': 'none', 'catalog_entries': len(entries),
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
    for path in (doc, PACKAGE / 'WORKSPACE-BOUNDARIES.md', PACKAGE / 'MODEL-REVISION.md', PACKAGE / 'README.md'):
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
