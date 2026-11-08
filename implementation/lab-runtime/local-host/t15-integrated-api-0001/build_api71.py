"""Merge sealed T03, T16 and T22 runtime deltas on one actual signed family.

The predecessor packages and the signed family remain immutable. No inherited
test method may change; only independently selected fixture helpers are rebound.
"""
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
INTERFACE = ROOT / 'product/lab/release-candidates/v1/interface'
BASE = INTERFACE / 'api-integration-v45-t03-durable-margin-0001'
SESSION = INTERFACE / 'api-integration-v69-t16-call-source-scope-0001'
CONTEST = INTERFACE / 'api-integration-v60-t22-pinned-family-source-0001'
NEW = INTERFACE / 'api-integration-v71-t15-integrated-closure-0001'
LANE = ROOT / 'implementation/lab-runtime/local-host/t15-integrated-fixture-0001'
PINS = LANE / 'INTEGRATED-FAMILY-PINS-0001.json'
EXPECTED = {
    BASE: ('8d6e74a413ca7d801c2c844c98e9431b634d6e6f0ceecf905aa56404c083ec7a', '7211025e2c3baa384b41f930be8bb4a2af32759150de83d247bc46e8efc40502'),
    SESSION: ('28f0bdcc125076f8568c374326fee20eb7822a75e2cf7df49091224a4ad30f9f', '74be9b75498a98bf728a2e4ce3a2ec889ddc98d40e5136cbc8eff110b826c0d5'),
    CONTEST: ('a38d44c85102b527ad681600b9b585914ac548659aba833b28915c59435fa47c', '7c263b912f56c7e5256ff8426d64f0325564038fad84a54f0f6a714ed568a34b'),
}
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
encoded = lambda value: (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()
binding = lambda path: {'path': Path(path).relative_to(ROOT).as_posix(), 'sha256': sha(path)}


def need(value, reason):
    if not value:
        raise ValueError(reason)


def methods(folder):
    result = {}
    for path in sorted([*folder.glob('test_*.py'), *folder.glob('run_*checks.py')]):
        for cls in ast.parse(path.read_text()).body:
            if not isinstance(cls, ast.ClassDef):
                continue
            for method in cls.body:
                if isinstance(method, ast.FunctionDef) and method.name.startswith('test_'):
                    result[path.name + ':' + cls.name + '.' + method.name] = ast.dump(method, include_attributes=False)
    return result


def member(text, cls, name):
    tree = ast.parse(text)
    parent = next(item for item in tree.body if isinstance(item, ast.ClassDef) and item.name == cls)
    node = next(item for item in parent.body if isinstance(item, ast.FunctionDef) and item.name == name)
    start = min([node.lineno, *(item.lineno for item in node.decorator_list)])
    return ''.join(text.splitlines(keepends=True)[start-1:node.end_lineno])


def replace_once(text, before, after):
    need(text.count(before) == 1, 'merge seam differs: ' + before[:100])
    return text.replace(before, after, 1)


def family_for(package):
    manifest = json.loads((package / 'source-manifest.json').read_bytes())
    return (ROOT / manifest['family_source_manifest_binding']['path']).parent.parent


def replacement_map(package, family, pins):
    old_family = family_for(package)
    result = {old_family.relative_to(ROOT).as_posix(): family.relative_to(ROOT).as_posix(),
              old_family.name: family.name, package.name: NEW.name}
    digest_map = {}
    for path in old_family.rglob('*'):
        other = family / path.relative_to(old_family)
        if path.is_file() and other.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
            a, b = sha(path), sha(other)
            if a in digest_map and digest_map[a] != b:
                raise ValueError('ambiguous selected digest retarget: ' + str(path))
            digest_map[a] = b
    result.update(digest_map)
    old_period = json.loads((old_family / 'source/packages/0001/period.json').read_bytes())
    result.update({old_period[key]: pins[key] for key in ('not_before', 'expires_at')})
    # The integrated family selects its own engine profile containing all three
    # diagnosis inputs. Historical engine fixtures remain otherwise untouched.
    old_profile = json.loads((package / 'source-manifest.json').read_bytes())['engine_profile_binding']
    result[old_profile['path']] = pins['engine']['profile']['path']
    result[old_profile['sha256']] = pins['engine']['profile']['sha256']
    return result


def remap(text, replacements):
    # One simultaneous substitution prevents a replacement output becoming a
    # later search key, especially equal original file digests.
    matcher = re.compile('|'.join(re.escape(key) for key in sorted(replacements, key=len, reverse=True)))
    return matcher.sub(lambda found: replacements[found.group(0)], text)


def main():
    os.umask(0o077)
    need(not NEW.exists(), 'integrated package already exists')
    for package, (source_pin, profile_pin) in EXPECTED.items():
        need(sha(package / 'source-manifest.json') == source_pin, 'selected predecessor source differs: ' + package.name)
        need(sha(package / 'contract-profile.json') == profile_pin, 'selected predecessor profile differs: ' + package.name)
    need(sha(PINS) == '5006cfb83997d0954fbbb0d76a88eaaa7bd975dbb62d94cb96399856d7dd4e3c', 'integrated signed family differs')
    pins = json.loads(PINS.read_bytes())
    family = ROOT / pins['family']
    need(pins['counts']['signed_subjects'] == 619 and pins['Context_carriers'] == 35, 'integrated actual closure differs')
    originals = methods(SESSION)
    need(len(originals) == 345, 'inherited Session predecessor inventory differs')
    base_methods = methods(BASE)
    base_method_changes = sorted(key for key in originals if base_methods.get(key) != originals[key])
    maps = {package: replacement_map(package, family, pins) for package in EXPECTED}
    shutil.copytree(BASE, NEW, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    selected_from = {path.name: BASE for path in NEW.iterdir() if path.is_file()}
    for name in ('current_legacy_context_sessions.py', 'session_source_freshness.py'):
        shutil.copyfile(SESSION / name, NEW / name)
        selected_from[name] = SESSION
    for name in ('agent_challenge_grant.py', 'machine_transport.py', 'challenge_submission.py'):
        shutil.copyfile(CONTEST / name, NEW / name)
        selected_from[name] = CONTEST
    for path in [*SESSION.glob('test_*.py'), *SESSION.glob('run_*checks.py')]:
        shutil.copyfile(path, NEW / path.name)
        selected_from[path.name] = SESSION
    for path in NEW.iterdir():
        if path.is_file() and path.name not in ('source-manifest.json', 'contract-profile.json', 'rebind-receipt.json'):
            try:
                text = path.read_text()
            except UnicodeError:
                continue
            path.write_text(remap(text, maps[selected_from[path.name]]))
    # Preserve T03 private Lesson selections and erasure on Session disposal.
    path = NEW / 'current_legacy_context_sessions.py'
    text = path.read_text()
    text = replace_once(text, 'self.delivery=copy.deepcopy(delivery);self.memory=[];self.closed=False',
                        'self.delivery=copy.deepcopy(delivery);self.memory=[];self.lesson_selections={};self.closed=False')
    text = replace_once(text, 'self.memory.clear();self.delivery=None;self.source=None;self.bridge=None',
                        'self.memory.clear();self.lesson_selections.clear();self.delivery=None;self.source=None;self.bridge=None')
    text = replace_once(text, "len(proof['generated_objects'])==30", "len(proof['generated_objects'])==35")
    path.write_text(text)
    path = NEW / 'auth.py'
    text = path.read_text()
    session_auth = (SESSION / 'auth.py').read_text()
    text = replace_once(text, 'import base64\n', 'import base64\nimport threading\nfrom contextlib import contextmanager\n')
    text = replace_once(text, '        self.termination_basis=None', '        self.termination_basis=None\n        self._source_call_local=threading.local()')
    text = replace_once(text, member(text, 'ReaderChannel', 'guard'),
                        member(session_auth, 'ReaderChannel', 'verified_source_call') + '\n' + member(session_auth, 'ReaderChannel', 'guard'))
    path.write_text(text)
    path = NEW / 'service.py'
    text = path.read_text()
    text = replace_once(text, member(text, 'Service', 'call'), member((SESSION / 'service.py').read_text(), 'Service', 'call'))
    text = replace_once(text, "if name=='session.open':session_plan=self.sessions.open_plan(message,call['expected_source_cut'])",
                        "if name=='session.open':session_plan=(self.sessions.prepared_open_plan(message,call['expected_source_cut'],request,inner) if hasattr(self.sessions,'prepared_open_plan') else self.sessions.open_plan(message,call['expected_source_cut']))")
    text = replace_once(text, "for name in ('protocol.py'", "for name in ('agent_challenge_grant.py','session_source_freshness.py','protocol.py'")
    path.write_text(text)
    # T22 dynamic Agent evidence is admitted only by a real selected live grant.
    path = NEW / 'workspace.py'
    text = path.read_text()
    contest_workspace = (CONTEST / 'workspace.py').read_text()
    branch = contest_workspace.split("        if self.channel.policy['schema_version']=='lab-local-challenge-candidate-policy/v1-candidate'", 1)[1].split("        if self.channel.policy['schema_version'] in", 1)[0]
    prefix = "        if self.channel.policy['schema_version']=='lab-local-challenge-candidate-policy/v1-candidate'" + branch
    text = replace_once(text, "        if self.channel.policy['schema_version'] in ('lab-local-package-import-policy/v1-candidate'", prefix + "        if self.channel.policy['schema_version'] in ('lab-local-package-import-policy/v1-candidate'")
    path.write_text(text)
    path = NEW / 'guarded_candidate.py'
    text = path.read_text()
    contest_candidate = (CONTEST / 'guarded_candidate.py').read_text()
    for name in ('selection', 'calculation'):
        # Add only Agent branch; retain T03's effect_guard argument and guarded
        # per-object publication and completion rollback.
        node = next(item for item in ast.parse(text).body if isinstance(item, ast.FunctionDef) and item.name == name)
        target = ast.get_source_segment(text, node)
        origin = next(item for item in ast.parse(contest_candidate).body if isinstance(item, ast.FunctionDef) and item.name == name)
        segment = ast.get_source_segment(contest_candidate, origin)
        branch = '    from .machine_transport import MachinePeer\n' + segment.split('    from .machine_transport import MachinePeer\n', 1)[1].split("    if host.channel.policy['source_name']", 1)[0]
        if name == 'calculation':
            branch = replace_once(branch, '        from .machine_auth_scope import source_facts', "        source.require(effect_guard is None,'Agent challenge cannot borrow Lesson derived effects')\n        from .machine_auth_scope import source_facts")
        target_new = replace_once(target, "    if host.channel.policy['source_name']", branch + "    if host.channel.policy['source_name']")
        text = text.replace(target, target_new, 1)
    path.write_text(text)
    path = NEW / 'native_dispositions.py'
    text = path.read_text().replace('== 616', '== 619')
    need(text.count('== 619') == 3, 'exact disposition predicates differ')
    path.write_text(text)
    # Grant constants select actual exact final Source objects, not old receipts.
    path = NEW / 'agent_challenge_grant.py'
    text = path.read_text()
    index = json.loads((family / 'source/packages/0001/record-index.json').read_bytes())
    kinds = {row['kind']: row for row in index}
    constants = {
        'FAMILY': family.relative_to(ROOT).as_posix(),
        'SOURCE_SHA': sha(family / 'source/source-manifest.json'),
        'PACKAGE_SHA': sha(family / 'source/packages/0001/manifest.json'),
        'INDEX_SHA': sha(family / 'source/packages/0001/record-index.json'),
        'COLD_SHA': pins['receipts']['cold']['sha256'], 'PERIOD_SHA': pins['period_binding']['sha256'],
        'WORK_SHA': kinds['work']['original_binding']['sha256'],
        'CONTRACT_SHA': kinds['challenge-contract']['original_binding']['sha256'],
        'MAPPING_SHA': sha(family / 'mapped/packages/0001/mapping.json'),
        'DELIVERY_SHA': sha(family / 'context/packages/0001/delivery.json'),
        'STORE': pins['source_cut']['store_ref'],
    }
    for node in reversed(ast.parse(text).body):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id in constants:
            name = node.targets[0].id
            lines = text.splitlines(keepends=True)
            text = ''.join(lines[:node.lineno-1]) + name + ' = ' + repr(constants[name]) + '\n' + ''.join(lines[node.end_lineno:])
    text = replace_once(text, "json.loads(selected(FAMILY + '/cold-result.json', COLD_SHA))", "json.loads(selected(" + repr(pins['receipts']['cold']['path']) + ", COLD_SHA))['observation']")
    text = replace_once(text, 'len(index) == 22', 'len(index) == 26')
    path.write_text(text)
    validation = LANE / 'T22-INTEGRATED-SOURCE-VALIDATION-0002.json'
    need(sha(validation) == '9b993689d1737bcd0f98029aea0333321972a4e172e808b2860c35866e681fd6', 'new actual Source validation receipt differs')
    shutil.copyfile(validation, NEW / 't22-validation-receipt.json')
    # Optional portable margin helper is supplied and reviewed independently by
    # the T03 owner before this constructor seals the common API.
    portable = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T03/local-lifecycle-actual-clock-0001/portable-margin-postimages-0001'
    for name in ('observed_margin.py', 'margin_capture.py'):
        need((portable / name).is_file(), 'T03 portable selected-role margin helper pending')
        shutil.copyfile(portable / name, NEW / name)
    path = NEW / 'source_bridge.py'
    text = path.read_text().replace('_cal_api30_current_legacy_local_20261022_0001', '_cal_api71_integrated_legacy_4636').replace('_cal_api30_current_source8_local_20261022_0001', '_cal_api71_integrated_source8_4636')
    path.write_text(text)
    for path in NEW.glob('*.py'):
        ast.parse(path.read_text())
    need(methods(NEW) == originals, 'an inherited test method AST changed')
    source = json.loads((BASE / 'source-manifest.json').read_bytes())
    profile = json.loads((BASE / 'contract-profile.json').read_bytes())
    active_prefixes = (BASE.relative_to(ROOT).as_posix() + '/', family_for(BASE).relative_to(ROOT).as_posix() + '/')
    old_engine = source['engine_profile_binding']['path']
    def recut(row):
        if type(row) is dict and set(row) == {'path', 'sha256'}:
            # Historical external fixtures retain their exact original pins.
            # Only the explicitly selected active package/family/engine moves.
            if not row['path'].startswith(active_prefixes) and row['path'] != old_engine:
                return row
        value = json.loads(remap(json.dumps(row), maps[BASE]))
        if type(value) is dict and set(value) == {'path', 'sha256'}:
            candidate = ROOT / value['path']
            return binding(candidate) if candidate.is_file() and (candidate.is_relative_to(NEW) or candidate.is_relative_to(family) or candidate.is_relative_to(LANE / 'engine-v3')) else value
        return value
    prefix = NEW.relative_to(ROOT).as_posix() + '/'
    profile['files'] = [recut(row) for row in profile['files'] if not row['path'].startswith(BASE.relative_to(ROOT).as_posix() + '/')]
    profile['files'] += [binding(path) for path in NEW.rglob('*') if path.is_file() and '__pycache__' not in path.parts and 'receipts' not in path.parts and path.suffix != '.pyc' and path.name not in ('source-manifest.json', 'contract-profile.json', 'rebind-receipt.json')]
    profile['files'] = sorted(profile['files'], key=lambda row: row['path'])
    for key, value in list(profile.items()):
        if key != 'files' and type(value) is dict and set(value) == {'path', 'sha256'}:
            profile[key] = recut(value)
    profile['claim_ceiling'] = 'One coherent current signed Lesson/Agent-contest local API candidate; integrated behavioral qualification pending.'
    (NEW / 'contract-profile.json').write_bytes(encoded(profile))
    source['files'] = [row for row in source['files'] if not row['path'].startswith(BASE.relative_to(ROOT).as_posix() + '/')]
    source['files'] += [binding(path) for path in NEW.rglob('*') if path.is_file() and '__pycache__' not in path.parts and 'receipts' not in path.parts and path.suffix != '.pyc' and path.name not in ('source-manifest.json', 'rebind-receipt.json')]
    source['files'] = sorted(source['files'], key=lambda row: row['path'])
    for key, value in list(source.items()):
        if key != 'files' and type(value) is dict and set(value) == {'path', 'sha256'}:
            source[key] = recut(value)
    source['profile_binding'] = binding(NEW / 'contract-profile.json')
    source['predecessor_source_manifest_binding'] = binding(BASE / 'source-manifest.json')
    source['claim_ceiling'] = profile['claim_ceiling']
    (NEW / 'source-manifest.json').write_bytes(encoded(source))
    receipt = {'schema_version': 'lab-T15-integrated-api-merge/v1-candidate',
               'successor_package': NEW.relative_to(ROOT).as_posix(),
               'successor_manifest_sha256': sha(NEW / 'source-manifest.json'),
               'source_binding': binding(NEW / 'source-manifest.json'), 'profile_binding': binding(NEW / 'contract-profile.json'),
               'predecessors': [binding(package / 'source-manifest.json') for package in EXPECTED],
               'integrated_family': binding(PINS), 'inherited_methods': 345, 'changed_method_asts': 0,
               'test_inventory_predecessor': binding(SESSION / 'source-manifest.json'),
               'stale_T03_test_methods_replaced_by_preserved_API53_methods': base_method_changes,
               't22_validation_external_origin': binding(validation), 'full345_qualified': False,
               'portable_margin_postimages': [binding(portable / name) for name in ('observed_margin.py','margin_capture.py')],
               'live_integrated_Agent_contest_observed': False, 't15_frozen': False,
               'authority_effect': 'none', 'actual_owner_outcome': None}
    (NEW / 'rebind-receipt.json').write_bytes(encoded(receipt))
    (HERE / 'API71-BUILD-0001.json').write_bytes(encoded(receipt))
    print(json.dumps(receipt, sort_keys=True))


if __name__ == '__main__':
    main()
