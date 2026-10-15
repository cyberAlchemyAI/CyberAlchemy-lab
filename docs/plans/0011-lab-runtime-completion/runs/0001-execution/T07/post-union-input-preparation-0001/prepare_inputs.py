"""Passive preparation, or Root-only freezing after the independently accepted union.

This module imports no application code and cannot apply the union or capture Source.
The default command verifies frozen public inputs and writes only this package's
preflight observation. --freeze requires a separate exact Root selection and an
absent owned output directory; it never writes shared code/generated metadata.
"""
import argparse
import hashlib
import json
import os
import re
import stat
from pathlib import Path

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
RUN = 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/'
HERE = Path(__file__).parent
OUTPUT = ROOT / (RUN + 'T07/post-union-frozen-inputs-0001')
API = 'product/lab/release-candidates/v1/interface/api-integration-v17/'
GENERATED = {API + n for n in ('source-manifest.json', 'contract-profile.json',
                              'SCHEMA-EXECUTION-DEPENDENCIES.json', 'INPUT-ACCOUNTING.json')}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False,
                       allow_nan=False) + '\n').encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(name):
    need(type(name) is str and name and '\\' not in name and '\0' not in name,
         'invalid origin')
    p = Path(name)
    need(p.as_posix() == name and '..' not in p.parts and name != '.', 'aliased origin')
    if p.is_absolute():
        need(not p.is_relative_to(ROOT), 'absolute repository alias')
    return p if p.is_absolute() else ROOT / p


def raw(row):
    need(type(row) is dict and set(row) == {'path', 'sha256'}, 'open binding')
    need(type(row['sha256']) is str and re.fullmatch('[a-f0-9]{64}', row['sha256']),
         'invalid digest')
    p = canonical(row['path'])
    need(p.is_file() and not p.is_symlink() and not any(x.is_symlink() for x in p.parents),
         'absent or aliased input: ' + row['path'])
    body = p.read_bytes()
    need(digest(body) == row['sha256'], 'input bytes differ: ' + row['path'])
    return body


def parse(body):
    def pairs(items):
        result = {}
        for k, v in items:
            need(k not in result, 'duplicate JSON key')
            result[k] = v
        return result
    return json.loads(body, object_pairs_hook=pairs,
                      parse_constant=lambda x: need(False, 'nonfinite JSON'))


def load(row):
    return parse(raw(row))


def byte_binding(row):
    # Some frozen v5 held preimages independently declare their original mode.
    # Preserve those declarations in the raw map, check the extra obligation,
    # and project only the closed byte pair accepted by the original writer.
    need(type(row) is dict and set(row) in ({'path', 'sha256'}, {'path', 'sha256', 'mode'}),
         'open held-byte binding')
    if 'mode' in row:
        need(type(row['mode']) is int and
             stat.S_IMODE(canonical(row['path']).stat().st_mode) == row['mode'],
             'held-byte mode differs')
    return {k: row[k] for k in ('path', 'sha256')}


def actual_binding(p):
    p = Path(p)
    return {'path': p.relative_to(ROOT).as_posix(), 'sha256': digest(p.read_bytes())}


def deduplicate(rows):
    result = {}
    for row in rows:
        need(set(row) == {'path', 'sha256'}, 'open inventory binding')
        need(result.get(row['path'], row) == row, 'conflicting origin: ' + row['path'])
        result[row['path']] = row
    return [result[x] for x in sorted(result)]


def inspect(inputs):
    # All top-level public evidence is independently pinned in external-inputs.json.
    for row in inputs['bindings'].values():
        raw(row)
    union = load(inputs['bindings']['union'])
    mapping = load(inputs['bindings']['declarations'])
    proposal = load(inputs['bindings']['input_plan'])
    transition = load(inputs['bindings']['old_transition'])
    predecessor = load(inputs['bindings']['capture5_selection'])
    targets = {x['target']: x for x in union['rows']}
    need(len(targets) == len(union['rows']) == 38, 'full exact38 union required')
    need(sum(x['preimage_binding'] is not None for x in targets.values()) == 6,
         'all six existing target preimages required')
    for name, row in targets.items():
        need(row['postimage_binding']['path'] == name and
             row['postimage_source_binding']['sha256'] == row['postimage_binding']['sha256'],
             'postimage correspondence differs')
        raw(row['postimage_source_binding'])
        if row['held_preimage_binding'] is not None:
            need(row['held_preimage_binding']['sha256'] == row['preimage_binding']['sha256'],
                 'held preimage differs')
            raw(byte_binding(row['held_preimage_binding']))
    declared = mapping['declarations']
    need(len(declared) == 524 and mapping['declaration_count'] == 524,
         'all524 declarations required')
    origins = []
    indices = set()
    raw_manifests = {}
    changed = 0
    unavailable = []
    for item in declared:
        mf = item['component_manifest']
        raw_manifests[mf['path']] = mf
        data = load(mf)
        key = (mf['path'], item['declaration_index'])
        need(key not in indices, 'duplicate declaration index')
        indices.add(key)
        need(data['files'][item['declaration_index']] == item['original_declaration'],
             'original declaration or index changed')
        physical = item['selected_physical_binding']
        original = item['original_declaration']
        need(physical['sha256'] == original['sha256'], 'old byte identity changed')
        if item['disposition'] == 'unchanged-declaration':
            need(physical == {k: original[k] for k in ('path', 'sha256')},
                 'unchanged declaration origin changed')
        else:
            changed += 1
            need(item['disposition'] == 'historical-original-to-exact-held-preimage' and
                 original['path'] in targets and targets[original['path']]['preimage_binding'] is not None and
                 physical == targets[original['path']]['held_preimage_binding'],
                 'historical mapping is not exact union held preimage')
        byte_pair = byte_binding(physical)
        if canonical(byte_pair['path']).exists():
            body = raw(byte_pair)
            need(len(body) == original['size_bytes'], 'original declaration size differs')
        else:
            # Preserve the literal absent declaration. No substitution, row
            # suppression or reconstruction is authorized; actual freeze refuses.
            unavailable.append({'component_manifest': mf,
                                'declaration_index': item['declaration_index'],
                                'binding': byte_pair, 'size_bytes': original['size_bytes']})
        origins.append(byte_binding(physical))
    physical = deduplicate(origins)
    need(len(physical) == 511 and changed == 10 and len(raw_manifests) == 3,
         '524/511/10/three-raw conservation differs')
    need(len(transition['unchanged_original_components']) == 18, 'all18 retained components required')
    components = transition['unchanged_original_components'] + inputs['additional_components']
    component_audit = []
    remapped_components = {}
    for c in components:
        need(set(c) == {'base', 'path', 'sha256'} and c['base'] == '.', 'closed root component required')
        mf = {k: c[k] for k in ('path', 'sha256')}
        data = load(mf)
        hits = []
        mapped_files = []
        remaps = inputs['component_historical_mappings'].get(c['path'], [])
        used_remaps = []
        for i, row in enumerate(data['files']):
            selected = {k: row[k] for k in ('path', 'sha256')}
            replacement = [x for x in remaps if x['declaration_index'] == i]
            need(len(replacement) <= 1, 'duplicate historical component mapping')
            if replacement:
                item = replacement[0]
                need(set(item) == {'declaration_index', 'original_binding', 'held_binding'} and
                     item['original_binding'] == selected and
                     item['held_binding']['sha256'] == selected['sha256'],
                     'historical component preimage differs')
                selected = item['held_binding']
                used_remaps.append(item)
            raw(selected)
            mapped_files.append(selected)
            if selected['path'] in targets or selected['path'] in GENERATED:
                hits.append({'index': i, 'binding': selected})
        # The explicitly selected editions currently have no affected live rows.
        # Future changes must receive their own provenance treatment, never rewrite a digest.
        need(not hits, 'component consumes replaced/generated bytes: ' + c['path'])
        need(len(used_remaps) == len(remaps), 'unconsumed component mapping')
        if remaps:
            remapped_components[c['path']] = {'original_manifest': mf,
                'files': deduplicate(mapped_files + [mf]), 'declarations': len(data['files']),
                'historical_mappings': used_remaps}
        component_audit.append({'binding': mf, 'declarations': len(data['files']),
                                'exact_target_or_generated_hits': hits, 'byte_drift': [],
                                'historical_origin_mappings': used_remaps})
    software = proposal['software3']['exact_same_16_selected_origins']
    need(len(software) == 16 and len({x['path'] for x in software}) == 16,
         'exact16 software origins required')
    for row in software:
        if row['path'] in targets:
            need(row == targets[row['path']]['postimage_binding'], 'software postimage differs')
            raw(targets[row['path']]['postimage_source_binding'])
        else:
            raw(row)
    # Preserve predecessor helper roots and exact closed members. They are not
    # recursively expanded application imports and cannot silently acquire new files.
    helpers = predecessor['inputs']['helper_expected_files']
    for row in helpers:
        raw(row)
    expected_helpers = {x['path'] for x in helpers}
    actual_helpers = {p.relative_to(ROOT).as_posix()
                      for folder in predecessor['inputs']['helper_roots']
                      for p in (ROOT / folder).rglob('*')
                      if p.is_file() and '__pycache__' not in p.parts}
    need(actual_helpers == expected_helpers, 'helper membership differs')
    # One old direct Service input is historical after the new union. Retain
    # its literal bytes at its already held old origin, alongside the new API pin.
    directs = []
    direct_mapping = []
    for row in predecessor['inputs']['direct_inputs']:
        if row['path'] in targets:
            old = targets[row['path']]['preimage_binding']
            need(row == old, 'unexpected direct old target binding')
            held = byte_binding(targets[row['path']]['held_preimage_binding'])
            raw(held)
            directs.append(held)
            direct_mapping.append({'original': row, 'held': held})
        else:
            raw(row)
            directs.append(row)
    need(len(direct_mapping) == 1 and direct_mapping[0]['original']['path'] == API + 'service.py',
         'unexpected old direct-input mapping')
    for row in proposal['required_public_direct_inputs']:
        raw(row)
        directs.append(row)
    directs += list(inputs['bindings'].values())
    aggregate = deduplicate(physical + list(raw_manifests.values()) +
                            [inputs['bindings']['declarations']])
    return {'union': union, 'targets': targets, 'mapping': mapping,
            'proposal': proposal, 'predecessor': predecessor,
            'components': components, 'component_audit': component_audit,
            'remapped_components': remapped_components,
            'aggregate': aggregate, 'software': software,
            'directs': deduplicate(directs), 'direct_mapping': direct_mapping,
            'unavailable_declared_inputs': unavailable}


def freeze(inputs, result, selection_row):
    need(not result['unavailable_declared_inputs'], 'recorded physical inputs unavailable; owned freeze refused')
    selection = load(selection_row)
    need(set(selection) == {'schema_version', 'status', 'authority_effect',
                            'preparation_manifest_binding', 'union_binding',
                            'actual_merge_binding', 'accepted_review_bindings',
                            'callback_disposition_binding', 'provider_disposition_binding'},
         'closed separately selected Root freeze packet required')
    need(selection['schema_version'] == 'lab-T00-post-union-input-freeze/v1-candidate' and
         selection['status'] == 'Root-selected-actual-union-ready-for-owned-freeze' and
         selection['authority_effect'] == 'none', 'inactive or invalid Root selection')
    need(selection_row['path'].startswith(RUN + 'T00/'), 'Root selection must have true T00 origin')
    need(selection['union_binding'] == inputs['bindings']['union'], 'Root union differs')
    own_manifest = actual_binding(HERE / 'source-manifest.json')
    need(selection['preparation_manifest_binding'] == own_manifest, 'Root preparation differs')
    raw(own_manifest)
    proof_rows = [selection['actual_merge_binding'], selection['callback_disposition_binding'],
                  selection['provider_disposition_binding']] + selection['accepted_review_bindings']
    need(type(selection['accepted_review_bindings']) is list and selection['accepted_review_bindings'],
         'independent preparation/union/callback reviews required')
    for row in proof_rows:
        raw(row)
    for row in result['targets'].values():
        raw(row['postimage_binding'])
    # Refuse until Root has preserved all four exact fixed-origin metadata preimages.
    for value in result['proposal']['predecessor_metadata'].values():
        raw(value['original_binding'])
        raw(value['snapshot_binding'])
    expected_api = result['union']['proposed_API_expected_files']
    actual_api = {p.relative_to(ROOT).as_posix() for p in (ROOT / API).rglob('*')
                  if p.is_file() and '__pycache__' not in p.parts and 'receipts' not in p.parts and
                  p.relative_to(ROOT).as_posix() not in GENERATED}
    need(actual_api == {x['path'] for x in expected_api} and len(actual_api) == 197,
         'actual complete post-union API197 inventory differs')
    for row in expected_api:
        raw(row)
    # Reverify the complete independently frozen preparation, without importing it.
    for row in load(own_manifest)['files']:
        raw({k: row[k] for k in ('path', 'sha256')})
    need(not OUTPUT.exists() and not OUTPUT.is_symlink(), 'owned output already exists')
    OUTPUT.mkdir(mode=0o700)
    def write(name, value):
        p = OUTPUT / name
        fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC, 0o600)
        with os.fdopen(fd, 'wb') as f:
            f.write(encoded(value)); f.flush(); os.fsync(f.fileno())
        return actual_binding(p)
    provenance = write('active-component-provenance.json', {
        'schema_version': 'lab-T07-held-component-provenance/v1-candidate',
        'authority_effect': 'none', 'files': result['aggregate'],
        'declaration_map_binding': inputs['bindings']['declarations'],
        'conservation': {'declarations': 524, 'physical_originals': 511,
                         'held_old_declarations': 10, 'raw_manifests': 3},
        'Root_selection_binding': selection_row, 'runtime_qualified': False})
    software = write('software-0003.json', {'schema_version': 'lab-T03-observed-margin-software/v1-candidate',
                    'authority_effect': 'none', 'files': result['software']})
    components = []
    for c in result['components']:
        remap = result['remapped_components'].get(c['path'])
        if remap:
            successor = write('provider-provenance-%04d.json' % (len(components) + 1), {
                'schema_version': 'lab-T07-provider-held-input-provenance/v1-candidate',
                'authority_effect': 'none', **remap, 'runtime_qualified': False})
            components.append(dict(successor, base='.'))
        else:
            components.append(c)
    predecessor = result['predecessor']['inputs']
    directs = deduplicate(result['directs'] + proof_rows + [selection_row, own_manifest])
    seed = {'api_expected_files': expected_api,
            'helper_roots': predecessor['helper_roots'],
            'helper_expected_files': predecessor['helper_expected_files'],
            'component_manifests': components + [dict(provenance, base='.')],
            'direct_inputs': directs,
            'replacement_bindings': [{'preimage_binding': x['preimage_binding'],
                                      'postimage_binding': x['postimage_binding']}
                                     for x in result['targets'].values() if x['preimage_binding']],
            'active_family': predecessor['active_family'],
            'public_software_manifest_binding': software,
            'guard_binding': predecessor['guard_binding'], 'profile_updates': []}
    write('inputs-INACTIVE.json', {'schema_version': 'lab-T07-post-union-input-seed/v1-candidate',
          'active': False, 'authority_effect': 'none', 'inputs': seed,
          'actual_capture_run': False, 'final_Root_packet_binding': None,
          'final_packet_peer_binding': None,
          'required_before_capture': 'Independent exact frozen aggregate/software/inputs review; Root final T00 packet and its independent peer. Original fresh guards and periods remain mandatory.'})
    # Output publication is an owned freeze only. Interrupted/partial output is
    # retained and makes repetition refuse; no deleting or automatic re-entry.
    for row in result['aggregate'] + result['software'] + proof_rows:
        raw(row)
    for row in result['targets'].values():
        raw(row['postimage_binding'])
    write('freeze-result.json', {'schema_version': 'lab-T07-owned-input-freeze-result/v1-candidate',
          'authority_effect': 'none', 'result': 'owned-inputs-frozen-await-independent-peer',
          'provenance_binding': provenance, 'software_binding': software,
          'Root_selection_binding': selection_row, 'shared_write_performed': False,
          'actual_capture_run': False, 'runtime_qualified': False})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--freeze-selection')
    parser.add_argument('--freeze-selection-sha256')
    args = parser.parse_args()
    inputs = parse((HERE / 'external-inputs.json').read_bytes())
    result = inspect(inputs)
    if args.freeze_selection:
        need(args.freeze_selection_sha256 is not None, 'independent Root selection digest required')
        freeze(inputs, result, {'path': args.freeze_selection, 'sha256': args.freeze_selection_sha256})
    else:
        need(args.freeze_selection_sha256 is None, 'orphan Root digest')
        report = {'schema_version': 'lab-T07-post-union-passive-preflight/v1-candidate',
                  'authority_effect': 'none',
                  'result': ('PARTIAL-inactive-preflight-recorded-inputs-unavailable'
                             if result['unavailable_declared_inputs'] else 'PASS-inactive-public-byte-preflight'),
                  'active': False, 'actual_capture_or_union_or_guard_run': False,
                  'component_audit': result['component_audit'],
                  'conservation': {'declarations': 524, 'physical_originals': 511,
                                   'held_old_declarations': 10, 'raw_manifests': 3,
                                   'prospective_aggregate_unique_rows': len(result['aggregate'])},
                  'unavailable_declared_inputs': result['unavailable_declared_inputs'],
                  'retained_direct_input_mapping': result['direct_mapping'],
                  'software_files': 16, 'union_targets': 38, 'post_union_API_members': 197,
                  'current_provider_activation': 'Unselected; candidate inventories do not select runtime providers or prove old480/new827 compatibility.',
                  'remaining': ['Root actual union and four preserved metadata preimages',
                                'Real legacy Source expiry requires an independently reviewed coherent42-target successor before actual Source6; this exact38 preparation cannot activate it',
                                'Independent callback and preparation peer',
                                'Root explicit provider/callback disposition and actual freeze selection',
                                'Independent frozen aggregate/software/inputs peer and final T00 packet peer',
                                'Actual Source6 capture, full fresh guards and runtime qualification']}
        target = HERE / 'preflight-result.json'
        with target.open('xb') as f:
            f.write(encoded(report))
        print(json.dumps({'result': report['result'], 'component_manifests': len(report['component_audit']),
                          'prospective_aggregate_rows': len(result['aggregate']),
                          'actual_freeze_or_capture': False}), flush=True)


if __name__ == '__main__':
    main()
