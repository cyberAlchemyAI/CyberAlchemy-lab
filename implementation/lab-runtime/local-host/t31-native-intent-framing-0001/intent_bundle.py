"""Private intent-framing originals from one exact current signed Source cut.

Preparation reads the actual installed current Source once. Cold consumption
rebuilds the private IntentResolution from retained original Source bytes; it
does not replay a producer or turn candidate Work into Source admission.
"""
import argparse
import copy
import hashlib
import importlib
import importlib.util
import json
import os
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
ROUTES = ('transition:intent-framing:resolved',
          'transition:intent-framing:prepared')
KINDS = ('intent', 'work', 'goal', 'coordination', 'project', 'goal_project')
CARRIERS = {'intent': 'cal.artifact-type.intent/v1',
            'work': 'cal.artifact-type.work/v1',
            'goal': 'cal.artifact-type.goal/v1',
            'coordination': 'cal.artifact-type.coordination-context/v2',
            'project': 'cal.artifact-type.project-identity/v1',
            'goal_project': 'cal.artifact-type.typed-relation/v3'}


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode()


def write_new(path, raw):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as out:
        out.write(raw); out.flush(); os.fsync(out.fileno())


def frame():
    path = ROOT / 'implementation/lab-runtime/local-host/t31-retained-api-0001/frame.py'
    need(path.is_file() and not path.is_symlink(), 'installed current-Source frame unavailable')
    name = '_t31_intent_frame_' + sha(str(ROOT).encode())[:12]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    need(Path(module.__file__) == path, 'selected frame origin differs')
    return module


def derive(inputs, source_cut, principal, run_ref):
    """Pure exact-byte two-output closure; no runtime or owner authority."""
    need(type(inputs) is dict and set(inputs) == set(KINDS),
         'six exact current Source inputs required')
    need(type(run_ref) is str and run_ref.startswith('workflow-run:')
         and len(run_ref) <= 200 and type(principal) is str and principal,
         'bounded private framing actor/Run required')
    F = frame()
    for kind, pair in inputs.items():
        need(type(pair) is tuple and len(pair) == 2 and type(pair[1]) is bytes
             and pair[0]['carrier_ref'] == CARRIERS[kind]
             and pair[0]['byte_sha256'] == sha(pair[1]),
             'current Source ' + kind + ' original/header differs')
    capsule, raws = F.construct(root=ROOT, inputs=inputs, source_cut=source_cut,
                                principal=principal, run_ref=run_ref)
    ir = capsule['private_artifacts']['intent-resolution']
    ir_raw = raws[ir['version_ref']]
    work, work_raw = inputs['work']
    body = json.loads(ir_raw)
    need(body['payload']['intent_ref'] == inputs['intent'][0]['version_ref']
         and work['version_ref'] in body['payload']['selected_subject_refs']
         and work['version_ref'] not in body['payload']['excluded_subject_refs']
         and capsule['original_Work_Goal_or_Source_bytes_rewritten'] is False
         and ir['byte_sha256'] == sha(ir_raw) and work['byte_sha256'] == sha(work_raw),
         'private IntentResolution does not select exact unchanged Source Work')
    routes = {ROUTES[0]: [copy.deepcopy(ir)], ROUTES[1]: [copy.deepcopy(work)]}
    records = {pair[0]['version_ref']: (copy.deepcopy(pair[0]), pair[1])
               for pair in inputs.values()}
    need(ir['version_ref'] not in records, 'private IntentResolution shadows current Source')
    records[ir['version_ref']] = (copy.deepcopy(ir), ir_raw)
    return {'records': records, 'transitions': routes, 'capsule': capsule,
            'intent_resolution': ir, 'current_source_work': work,
            'frame_sha256': sha((ROOT / 'implementation/lab-runtime/local-host/t31-retained-api-0001/frame.py').read_bytes())}


def selected_runtime():
    selected = sys.modules.get('cal_installed_runtime_selection_v1')
    need(selected is not None, 'installed selected-python launcher required')
    selected.require_runtime_ready(); selected.guard()
    need(selected.root() == ROOT, 'selected installed repository differs')
    api = ROOT / selected.current().package['entrypoint']['api_directory']
    source = selected.binding('api.source')
    profile = selected.binding('api.profile')
    need(source['path'] == str((api / 'source-manifest.json').relative_to(ROOT))
         and profile['path'] == str((api / 'contract-profile.json').relative_to(ROOT)),
         'selected installed API source/profile paths differ')
    return selected, api, source, profile


def current_inputs(view, model, delivery):
    """Mirror the selected workflow fixture's six signed Source roles."""
    rows = {}
    scope = view.custody_signed_sources.sources.scope_ref
    with model.model_read_batch(view):
        for kind, identity in (('intent', delivery.records.INTENT),
                               ('work', delivery.records.WORK),
                               ('goal', delivery.records.GOAL),
                               ('coordination', delivery.records.COORDINATION)):
            found = [s for s in view.subjects.values()
                     if s['identity'] == identity
                     and s['effective_state'] in ('admitted-current', 'local-admitted-current')]
            need(len(found) == 1, 'one exact current Source ' + kind + ' required')
            header = model.artifact_ref(view, found[0]); raw = model.record_bytes(view, found[0])[0]
            rows[kind] = (header, raw)
        project = [s for s in view.subjects.values()
                   if s['identity'] == scope
                   and s['carrier_ref'] == 'cal.artifact-type.project-identity/v1'
                   and s['effective_state'] in ('admitted-current', 'local-admitted-current')]
        need(len(project) == 1, 'one current Project original required')
        rows['project'] = (model.artifact_ref(view, project[0]),
                           model.record_bytes(view, project[0])[0])
        goal = rows['goal'][0]
        edges = []
        for subject in view.subjects.values():
            if (subject.get('carrier_ref') != 'cal.artifact-type.typed-relation/v3'
                    or subject['effective_state'] not in ('admitted-current', 'local-admitted-current')):
                continue
            header = model.artifact_ref(view, subject)
            raw = model.record_bytes(view, subject)[0]
            body = json.loads(raw)
            if (body['payload']['relation_kind_ref'] == 'relation.member-of'
                    and body['payload']['source']['version_ref'] == goal['version_ref']
                    and body['payload']['target']['version_ref'] == rows['project'][0]['version_ref']):
                edges.append((header, raw))
        need(len(edges) == 1, 'one exact current Goal/Project relation required')
        rows['goal_project'] = edges[0]
    need(all(h['scope_ref'] == scope and sha(raw) == h['byte_sha256']
             for h, raw in rows.values()), 'current signed Source scope/bytes differ')
    return rows


def persist(output, inputs, derived, source_binding, profile_binding,
            cut, principal, run_ref):
    output = Path(output)
    need(output.is_absolute() and not output.exists() and output.parent.is_dir()
         and not output.is_relative_to(ROOT)
         and not any(p.is_symlink() for p in output.parents),
         'fresh external private intent-framing bundle required')
    checked = derive(inputs, cut, principal, run_ref)
    need(derived['transitions'] == checked['transitions']
         and derived['records'] == checked['records'],
         'source-framing output changed before private custody')
    output.mkdir(mode=0o700)
    input_rows = {}
    for kind, (header, raw) in inputs.items():
        name = 'input-' + kind + '.json'
        write_new(output / name, raw)
        input_rows[kind] = {'artifact': header, 'path': name, 'sha256': sha(raw)}
    ir = derived['intent_resolution']; ir_raw = derived['records'][ir['version_ref']][1]
    write_new(output / 'intent-resolution.json', ir_raw)
    receipt = {'schema_version': 'lab-private-current-intent-framing-originals/v1',
               'source_cut': cut, 'source_binding': source_binding,
               'profile_binding': profile_binding,
               'run_ref': run_ref, 'principal_ref': principal,
               'source_inputs': input_rows,
               'intent_resolution': ir, 'current_source_work': derived['current_source_work'],
               'transitions': derived['transitions'],
               'original_Work_body_unchanged': True,
               'private_IntentResolution_selects_current_Work': True,
               'human_Intent_resolution_or_actual_owner_outcome': None,
               'canonical_admissions': 0, 'authority_effect': 'none'}
    receipt_raw = encoded(receipt)
    write_new(output / 'ORIGINAL-RECEIPT.json', receipt_raw)
    manifest = {'schema_version': 'lab-current-intent-framing-bundle/v1',
                'receipt_sha256': sha(receipt_raw),
                'producer_code_sha256': sha(Path(__file__).read_bytes()),
                'frame_code_sha256': derived['frame_sha256'],
                'source_binding': source_binding, 'profile_binding': profile_binding,
                'source_cut': cut, 'run_ref': run_ref, 'principal_ref': principal,
                'input_files': input_rows,
                'output_files': {'intent-resolution': {'path': 'intent-resolution.json',
                    'artifact': ir, 'sha256': sha(ir_raw)},
                    'work': input_rows['work']},
                'transitions': derived['transitions'],
                'authority_effect': 'none', 'actual_owner_outcome': None}
    raw = encoded(manifest); write_new(output / 'MANIFEST.json', raw)
    return {'kind': 'intent-framing', 'manifest_path': str(output / 'MANIFEST.json'),
            'manifest_sha256': sha(raw), 'source_binding': source_binding,
            'profile_binding': profile_binding, 'source_cut': cut,
            'transition_count': 2, 'authority_effect': 'none'}


def prepare(output, run_ref):
    selected, api, source_binding, profile_binding = selected_runtime()
    output = Path(output)
    need(output.is_absolute() and not output.exists() and output.parent.is_dir()
         and not output.is_relative_to(ROOT)
         and not any(p.is_symlink() for p in output.parents),
         'fresh external private intent-framing bundle required')
    sys.path.insert(0, str(api.parent))
    P = importlib.import_module(api.name + '.protocol')
    G = importlib.import_module(api.name + '.guard')
    M = importlib.import_module(api.name + '.artifact_model')
    H = importlib.import_module(api.name + '.handlers')
    G.verify(source_binding['sha256'])
    with P.source.replay_source(P.source.CURRENT_LEGACY_NAME) as view:
        selected_source = view.custody_signed_sources
        selected_source.guard()
        inputs = current_inputs(view, M, P.source.current_legacy_delivery())
        cut = H.cut(view)
        need(cut == selected_source.source_cut,
             'current signed Source cut differs from workflow replay')
        principal = P.source.current_legacy_delivery().records.PRINCIPAL
        derived = derive(inputs, cut, principal, run_ref)
        selected_source.guard()
    selected.guard(); G.verify(source_binding['sha256'])
    return persist(output, inputs, derived, source_binding, profile_binding,
                   cut, principal, run_ref)


def consume(selection):
    import retained as R
    need(type(selection) is dict and set(selection) == {'kind', 'manifest_path', 'manifest_sha256'}
         and selection['kind'] == 'intent-framing',
         'closed current intent-framing bundle selection required')
    path = Path(selection['manifest_path'])
    need(path.is_absolute() and path.name == 'MANIFEST.json'
         and not path.is_symlink() and not any(p.is_symlink() for p in path.parents),
         'private current intent-framing manifest locator required')
    folder = path.parent; st = folder.stat()
    need(folder.is_dir() and st.st_uid == os.getuid()
         and stat.S_IMODE(st.st_mode) == 0o700,
         'owned private intent-framing bundle required')
    raw = R.read(path)
    need(sha(raw) == selection['manifest_sha256'], 'selected intent-framing manifest changed')
    manifest = json.loads(raw)
    need(manifest['schema_version'] == 'lab-current-intent-framing-bundle/v1'
         and manifest['authority_effect'] == 'none'
         and manifest['actual_owner_outcome'] is None
         and manifest['producer_code_sha256'] == sha(Path(__file__).read_bytes())
         and manifest['frame_code_sha256'] == sha((ROOT / 'implementation/lab-runtime/local-host/t31-retained-api-0001/frame.py').read_bytes()),
         'intent-framing producer/frame selection changed')
    selected, api, source_binding, profile_binding = selected_runtime()
    need(manifest['source_binding'] == source_binding
         and manifest['profile_binding'] == profile_binding,
         'intent-framing selected installed API differs')
    inputs = {}
    names = {'MANIFEST.json', 'ORIGINAL-RECEIPT.json', 'intent-resolution.json'}
    for kind in KINDS:
        row = manifest['input_files'][kind]
        need(row['path'] == 'input-' + kind + '.json', 'Source original locator differs')
        body = R.read(folder / row['path'])
        need(sha(body) == row['sha256'] == row['artifact']['byte_sha256'],
             'retained signed Source original/header differs')
        inputs[kind] = (row['artifact'], body); names.add(row['path'])
    need({p.name for p in folder.iterdir()} == names
         and not any(p.is_symlink() for p in folder.iterdir()),
         'private intent-framing bundle file closure differs')
    derived = derive(inputs, manifest['source_cut'], manifest['principal_ref'],
                     manifest['run_ref'])
    ir = derived['intent_resolution']; ir_raw = R.read(folder / 'intent-resolution.json')
    need(ir == manifest['output_files']['intent-resolution']['artifact']
         and ir_raw == derived['records'][ir['version_ref']][1]
         and sha(ir_raw) == manifest['output_files']['intent-resolution']['sha256']
         and manifest['output_files']['work'] == manifest['input_files']['work']
         and derived['transitions'] == manifest['transitions'],
         'private resolution/current Work output original differs')
    receipt_raw = R.read(folder / 'ORIGINAL-RECEIPT.json')
    receipt = json.loads(receipt_raw)
    need(sha(receipt_raw) == manifest['receipt_sha256']
         and receipt['source_inputs'] == manifest['input_files']
         and receipt['transitions'] == manifest['transitions']
         and receipt['source_cut'] == manifest['source_cut']
         and receipt['source_binding'] == source_binding
         and receipt['profile_binding'] == profile_binding
         and receipt['run_ref'] == manifest['run_ref']
         and receipt['principal_ref'] == manifest['principal_ref']
         and receipt['intent_resolution'] == ir
         and receipt['current_source_work'] == derived['current_source_work']
         and receipt['private_IntentResolution_selects_current_Work'] is True
         and receipt['original_Work_body_unchanged'] is True
         and receipt['human_Intent_resolution_or_actual_owner_outcome'] is None
         and receipt['canonical_admissions'] == 0
         and receipt['authority_effect'] == 'none',
         'intent-framing original receipt differs')
    selected.guard()
    return {'records': derived['records'], 'transitions': derived['transitions'],
            'source_inputs': inputs,
            'receipt_raw': receipt_raw, 'manifest_raw': raw,
            'manifest_binding': {'ref': str(path), 'sha256': sha(raw)},
            'source_binding': source_binding, 'profile_binding': profile_binding,
            'source_cut': manifest['source_cut'], 'run_ref': manifest['run_ref'],
            'principal_ref': manifest['principal_ref'],
            'input_refs': {inputs[kind][0]['carrier_ref']: inputs[kind][0]['version_ref']
                           for kind in ('intent', 'goal', 'coordination')},
            'intent_resolution': ir, 'current_source_work': derived['current_source_work']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--run-ref', required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.output, args.run_ref), sort_keys=True), flush=True)
