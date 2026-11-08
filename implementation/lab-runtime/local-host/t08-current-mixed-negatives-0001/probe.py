"""Actual full-selector T08 proof/control refusals, with private mutations only."""

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import time
import types

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
PRIOR = ROOT / 'implementation/lab-runtime/local-host/t08-current-mixed-boundary-0001'
PRIOR_CODE_SHA = 'd9f2bb14c7f5eb5f2a2decbc1ca71afce9c20f0f4ea358d9936d2927e4dd6311'
PRIOR_RESULT_SHA = '669533df4a0e739d8a4c7a4c9ab680b6bef2dc24d9e29d549f856707a167a571'


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def prior_module():
    raw = (PRIOR / 'run_boundary.py').read_bytes()
    need(sha(raw) == PRIOR_CODE_SHA, 'selected prior runner changed')
    need(sha((PRIOR / 'working/RESULT-0002.json').read_bytes()) == PRIOR_RESULT_SHA,
         'selected positive receipt changed')
    module = types.ModuleType('_cal_t08_selected_positive_constructor')
    module.__file__ = str(PRIOR / 'run_boundary.py')
    exec(compile(raw, module.__file__, 'exec'), module.__dict__)
    return module


def exact_replace(path, raw):
    with path.open('r+b') as stream:
        stream.seek(0)
        stream.write(raw)
        stream.truncate()
        stream.flush()
        os.fsync(stream.fileno())


@contextmanager
def changed_proof(path):
    original = path.read_bytes()
    need(len(original) > 100 and original[:1] == b'{', 'selected proof shape differs')
    try:
        exact_replace(path, b'[' + original[1:])
        yield
    finally:
        exact_replace(path, original)


@contextmanager
def missing_proof(path):
    away = path.with_name('scope-full.json.missing-probe')
    need(not away.exists(), 'private missing-probe collision')
    path.rename(away)
    try:
        yield
    finally:
        away.rename(path)


@contextmanager
def linked_root(path):
    away = path.with_name('private-linked-probe-held')
    need(not away.exists(), 'private root probe collision')
    path.rename(away)
    try:
        path.symlink_to(away, target_is_directory=True)
        yield
    finally:
        if path.is_symlink():
            path.unlink()
        away.rename(path)


@contextmanager
def changed_root(path):
    away = path.with_name('private-changed-probe-held')
    need(not away.exists(), 'private root probe collision')
    path.rename(away)
    try:
        path.mkdir(mode=0o700)
        yield
    finally:
        if path.is_dir() and not path.is_symlink():
            path.rmdir()
        away.rename(path)


def run():
    started = time.monotonic()
    R = prior_module()
    p, g, tests, host, content = R.modules()
    source_path = R.API + '/source-manifest.json'
    profile_path = R.API + '/contract-profile.json'
    source_raw = R.selected(source_path, R.SOURCE_SHA)
    profile_raw = R.selected(profile_path, R.PROFILE_SHA)
    source_binding = {'ref': source_path, 'sha256': R.SOURCE_SHA}
    profile_binding = {'ref': profile_path, 'sha256': R.PROFILE_SHA}
    cut = {'branch_ref': 'technical:T08-current-mixed/branch',
           'store_ref': 'technical:T08-current-mixed/store', 'commit_sequence': 0,
           'commit_sha256': sha(b'T08-current-mixed-technical-branch'),
           'source_profile_sha256': R.PROFILE_SHA, 'streams': []}
    with tempfile.TemporaryDirectory(prefix='cal-t08-full-negatives-', dir='/tmp') as location:
        parent = Path(location)
        parent.chmod(0o700)
        template = parent / 'template'
        template.mkdir(mode=0o700)
        private = parent / 'private'
        private.mkdir(mode=0o700)
        policy, eligibility, physical = R.policy_material(
            tests, template, source_binding, profile_binding, cut)
        _, _, selector, roots, policy_raw, eligibility_raw, _ = R.make_reader(
            p, source_raw, profile_raw, source_binding, profile_binding,
            cut, policy, eligibility, physical, private)
        semantic = {'anchor': {
            'policy_binding': {'ref': 'technical:T08-mixed/policy', 'sha256': sha(policy_raw)},
            'eligibility_binding': {'ref': 'technical:T08-mixed/eligibility',
                                    'sha256': sha(eligibility_raw)},
            'source_binding': source_binding, 'profile_binding': profile_binding,
            'source_cut': cut, 'allowed_states': ['candidate-current']},
            'policy_file_id': 'policy', 'declared_edges': [R.EDGE],
            'root_refs': [R.EDGE['source']]}
        reader, anchor, scope_binding, scope, selector = R.full_content_reader(
            p, content, None, selector, roots, semantic,
            source_binding, profile_binding, cut, private)
        need(len(reader.files) == 32231 and len(scope['coverage']) == 24503
             and len(reader.roots) == 128, 'positive full-selector shape differs')
        guard_path = R.API + '/guard.py'
        source = p.parse(source_raw)
        guard_digest = next(row['sha256'] for row in source['files'] if row['path'] == guard_path)
        raw = R.selected(guard_path, guard_digest)
        guard = types.ModuleType('_cal_t08_selected_source_guard_for_negatives')
        guard.__file__ = str(ROOT / guard_path)
        exec(compile(raw, guard.__file__, 'exec'), guard.__dict__)
        guard.verify(R.SOURCE_SHA)
        bindings = {
            'protected_inputs': {'path': R.ORIGINAL + '/protected_inputs.py', 'sha256': R.P_SHA},
            'semantic_graph': {'path': R.ORIGINAL + '/semantic_graph.py', 'sha256': R.G_SHA},
            'private_content': {'path': R.CONTENT, 'sha256': R.CONTENT_SHA}}
        selection = {
            'custody_anchor': {key: getattr(anchor, key) for key in host.ANCHOR_FIELDS},
            'control_roots': list(roots.values()), 'binding_routes': [],
            'semantic_selection': semantic, 'readiness_version': host.REVIEW_VERSION,
            'observation_schema_binding': {
                'path': R.API + '/typed-review-observation.schema.json',
                'sha256': sha((ROOT / R.API / 'typed-review-observation.schema.json').read_bytes())},
            'historical_original_proof': {
                'status': 'REFUSED', 'unavailable_binding': {
                    'path': 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/accounting-0001/unavailable-original-inputs.json',
                    'sha256': '4408c5433d41119a92660f86f856d6847be24171ddb1dab368e22c63ee294e7a'},
                'unavailable_count': 25},
            'historical_content': {'scope_binding': scope_binding,
                                   'scope_file_id': scope['scope_file_id']}}
        bridge = host.ProtectedHostBridge(selection, p, g, bindings, ROOT,
                                          private_content_module=content)
        bridge.builder = types.SimpleNamespace(guard=lambda: guard.verify(R.SOURCE_SHA))
        reached = {'content': 0, 'semantics': 0}
        content_original = bridge.verify_historical_content
        semantics_original = bridge.verify_semantics
        def content_call(actual_reader):
            reached['content'] += 1
            return content_original(actual_reader)
        def semantics_call(actual_reader):
            reached['semantics'] += 1
            return semantics_original(actual_reader)
        bridge.verify_historical_content = content_call
        bridge.verify_semantics = semantics_call
        cases = (
            ('linked-protected-control-root', linked_root(private)),
            ('changed-protected-control-root', changed_root(private)),
            ('changed-selected-proof', changed_proof(private / 'scope-full.json')),
            ('missing-selected-proof', missing_proof(private / 'scope-full.json')),
        )
        refusals = []
        for name, mutation in cases:
            guard.verify(R.SOURCE_SHA)
            before = dict(reached)
            begun = time.monotonic()
            with mutation:
                try:
                    with bridge.verified_boundary(semantics=True):
                        raise ValueError('mutated full selector incorrectly entered')
                except BaseException as error:
                    need(not str(error).startswith('mutated full selector incorrectly entered'),
                         'mutated full selector incorrectly entered')
                    kind = type(error).__name__
                    message = str(error)
                    cause = error.__cause__
                    print(json.dumps({'case': name, 'error_class': kind,
                                      'error_reason': message.replace(str(parent), '<private>'),
                                      'cause_class': type(cause).__name__ if cause else None}),
                          file=sys.stderr, flush=True)
                else:
                    raise ValueError('mutated full selector incorrectly passed')
            guard.verify(R.SOURCE_SHA)
            need(reached == before, 'mutated full selector reached content or graph')
            if name == 'changed-selected-proof':
                need(kind == 'Refusal' and 'fresh file bytes/attachment changed' in message,
                     'changed proof did not cause Reader byte refusal')
            elif name == 'missing-selected-proof':
                need(kind == 'Refusal' and 'root no-follow read refused' in message
                     and isinstance(cause, FileNotFoundError)
                     and Path(cause.filename).name == 'scope-full.json',
                     'missing proof did not cause Reader path refusal')
            elif name == 'linked-protected-control-root':
                need(kind in ('NotADirectoryError', 'OSError') and
                     ('Not a directory' in message or 'Too many levels of symbolic links' in message),
                     'linked control root did not cause no-follow refusal')
            else:
                need(kind == 'ValueError' and 'custody root identity differs' in message,
                     'changed control root did not cause selected-identity refusal')
            refusals.append({'case': name, 'result': 'REFUSED', 'error_class': kind,
                             'content_or_graph_entered': False,
                             'elapsed_seconds': round(time.monotonic() - begun, 3)})
        need(stat.S_ISDIR(private.lstat().st_mode) and
             sha((private / 'scope-full.json').read_bytes()) == scope_binding['sha256'],
             'private selected bytes not restored')
        return {'schema_version': 'lab-T08-current-mixed-full-selector-negatives/v1-candidate',
                'result': 'PASS-four-causal-refusals', 'positive_receipt_sha256': PRIOR_RESULT_SHA,
                'source_sha256': R.SOURCE_SHA, 'profile_sha256': R.PROFILE_SHA,
                'selected_files': len(reader.files), 'historical_coverage_rows': len(scope['coverage']),
                'control_roots': len(reader.roots), 'refusals': refusals,
                'full_reader_positive_repeated': False, 'private_body_exported': False,
                'semantic_graph_entered_in_negatives': False,
                'original_locator_physical_closure': 'REFUSED',
                'original_full_proof_status': 'REFUSED',
                'installation_release_builder_used': False,
                'authority_effect': 'none', 'T08_complete': False,
                'elapsed_seconds': round(time.monotonic() - started, 3)}


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True, indent=2, allow_nan=False))
