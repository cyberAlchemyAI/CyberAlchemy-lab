"""Independent retained-public-fixture review. No native or runtime effects."""
import ast, base64, copy, datetime, hashlib, json, os, stat, sys, types
from pathlib import Path

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE = Path(__file__).absolute().parent
INSTALL = ROOT / 'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
MF = '5dc7baec6ff2575c3bb5691cbab19c37d25c2e0716a25e5e6f3f67eb6abb5349'
sha = lambda raw: hashlib.sha256(raw).hexdigest()
assert Path(sys.executable) == INSTALL / 'bin/python'
fd_before = len(os.listdir('/proc/self/fd'))
manifest_raw = (HERE / 'source-manifest.json').read_bytes()
assert sha(manifest_raw) == MF
rows = json.loads(manifest_raw)['files']
# The author capture routine is selected explicitly as a source artifact; execute
# only that pure nofollow reader under its true filename, never its writing main.
capture_file = HERE / 'qualify.py'
capture_raw = capture_file.read_bytes()
capture_row = next(r for r in rows if r['path'] == str(capture_file.relative_to(ROOT)))
assert sha(capture_raw) == capture_row['sha256'] == 'bbb2d72da0ead088a074110d88148727aa303b8a59136b6e17b5ff40dee2902b'
tree = ast.parse(capture_raw, filename=str(capture_file))
node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'capture')
exec(compile(ast.Module(body=[node], type_ignores=[]), str(capture_file), 'exec'), globals())
entry = []; bodies = {}
for r in rows:
    raw, record = capture(ROOT / r['path'], r['sha256'], r['size_bytes'])
    bodies[r['path']] = raw; entry.append(record)
assert len(rows) == len(bodies) == 240
dep_path = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json'
dep_raw, _ = capture(dep_path, '2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835')
dep = json.loads(dep_raw); installed = []
for r in dep['inputs']:
    mode = 0o755 if r['kind'] in {'interpreter', 'native-executable'} or r['destination'] == 'lib/abi/ld-linux-x86-64.so.2' else 0o644
    installed.append(dict(path=str((INSTALL / r['destination']).relative_to(ROOT)), sha256=r['sha256'], size_bytes=r['size_bytes'], mode=mode))
installed += [dict(path=str((INSTALL / name).relative_to(ROOT)), **r) for name, r in dep['wheel_members'].items()]
assert len(installed) == len({r['path'] for r in installed}) == 1010
installed_entry = [capture(ROOT / r['path'], r['sha256'], r['size_bytes'], r['mode'])[1] for r in installed]
own = str(HERE.relative_to(ROOT)) + '/'
W = types.ModuleType('_independent_T13_fixture_review')
W.__file__ = str(HERE / 'witness.py')
exec(compile(bodies[own + 'witness.py'], W.__file__, 'exec', dont_inherit=True), W.__dict__)
packet = json.loads(bodies[own + 'FIXTURE-PUBLIC-INPUTS.json'])
decode = lambda x: base64.b64decode(x, validate=True)
assert packet['fixture_only'] and not packet['private_keys_exported'] and packet['native_effects'] == 0
cr = decode(packet['context_raw_base64']); c = W.parse(cr)
pr = decode(packet['plan_raw_base64']); p = W.parse(pr)
rr = decode(packet['response_raw_base64']); response = W.parse(rr)
dr = decode(packet['Decision_raw_base64']); wr = decode(packet['witness_raw_base64'])
at = W.instant(response['payload']['issued_at'])
artifacts = {name: decode(raw) for name, raw in packet['public_artifacts'].items()}
for binding, source in [('materializer_binding','materializer'), ('schema_binding','native'), ('decision_schema_binding','Decision_schema')]:
    ref = packet['public_code_source_refs'][source]
    raw = bodies[ref['path']]
    assert sha(raw) == ref['sha256'] == c[binding]['sha256']
    artifacts[c[binding]['path']] = raw
sr = bodies[own + 'protocol.schema.json']; sp = sha(sr)
heads = [t['expected_head'] for t in p['targets']]
prep = W.prepare(cr, sha(cr), pr, sha(pr), artifacts, sr, sp, heads, at)
ds = artifacts[c['decision_schema_binding']['path']]; dsp = sha(ds)
initial_events = tuple(prep['events'])
out = W.verify_witness(wr, sha(wr), prep, rr, dr, ds, dsp, heads, at)
assert out == dict(technical_fixture_witness_verified=True, fixture_only=True, authority_effect='none', actual_adoption_authorized=False, native_seal_qualified=False, native_effects=0)
assert len(prep['events']) == len(prep['cores']) == 88
negatives = []
def refuse(name, fn, reason=None):
    try: fn()
    except W.Refused as error:
        if reason is not None: assert str(error) == reason, (name, str(error))
        negatives.append(dict(name=name, refusal=str(error))); return
    raise AssertionError('unexpected acceptance: ' + name)
def changed(value, key, replacement):
    v = copy.deepcopy(value); v[key] = replacement; return W.external_json(v)
actual = changed(c, 'mode', 'actual')
refuse('actual mode before all body access', lambda: W.prepare(actual, sha(actual), b'', '0'*64, {}, b'', '0'*64, [], at), 'actual adoption rule/T10/T11/current heads/eligible authority unselected')
identity = changed(c, 'principal_ref', 'real-owner')
refuse('nonfixture principal', lambda: W.prepare(identity, sha(identity), pr, sha(pr), artifacts, sr, sp, heads, at))
for name, key in [('native source byte drift','schema_binding'), ('materializer byte drift','materializer_binding'), ('owner evidence byte drift','role_evidence_binding')]:
    a = dict(artifacts); a[c[key]['path']] += b' '
    refuse(name, lambda a=a: W.prepare(cr, sha(cr), pr, sha(pr), a, sr, sp, heads, at))
a = dict(artifacts); a[p['targets'][0]['event_binding']['path']] += b' '
refuse('event byte drift', lambda: W.prepare(cr, sha(cr), pr, sha(pr), a, sr, sp, heads, at))
h = copy.deepcopy(heads); h[0]['cursor_position'] = 2
refuse('changed head before preparation', lambda: W.prepare(cr, sha(cr), pr, sha(pr), artifacts, sr, sp, h, at))
refuse('changed head after response', lambda: W.materialize_witness(prep, rr, dr, ds, dsp, h, at))
for label, targets in [('omitted target', p['targets'][:-1]), ('reordered targets', list(reversed(p['targets'])))]:
    raw = changed(p, 'targets', targets)
    refuse(label, lambda raw=raw: W.prepare(cr, sha(cr), raw, sha(raw), artifacts, sr, sp, heads, at))
held = copy.deepcopy(prep); held['cores'][0]['requested_axis'] = 'other'
held['core_commitment'] = W.domain_hash('ordered-fixed-cores', list(held['cores']))
refuse('recommitted altered held core', lambda: W.verify_response(held, rr, at))
r = copy.deepcopy(response); r['payload']['nonce'] += '0'; raw = W.external_json(r)
refuse('changed signed response', lambda: W.verify_response(prep, raw, at))
refuse('Decision whitespace byte drift', lambda: W.materialize_witness(prep, rr, dr + b' ', ds, dsp, heads, at))
d = W.parse(dr); d['authority_effect'] = 'adopted'; rawd = W.external_json(d) + b'\n'
refuse('Decision authority promotion', lambda: W.materialize_witness(prep, rr, rawd, ds, dsp, heads, at))
for key in ['actual_adoption_authorized', 'native_seal_qualified']:
    promoted = changed(W.parse(wr), key, True)
    refuse(key + ' promotion', lambda promoted=promoted: W.verify_witness(promoted, sha(promoted), prep, rr, dr, ds, dsp, heads, at))
refuse('expired context boundary at fixture time', lambda: W.verify_response(prep, rr, W.instant(c['valid_until'])))
refuse('wrong external witness independent pin', lambda: W.verify_witness(wr, '0'*64, prep, rr, dr, ds, dsp, heads, at))
assert initial_events == prep['events']
account_path = 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T13/native-event-closure-preparation-0001/ACCOUNTING-88.json'
inherited = W.inherited_originals(bodies[account_path], 'c783761f5180365cbec59ef8ab654cb3d9bb3376e408eee37f06216ccaf46f1d')
assert inherited['original_intents'] == len(inherited['unchanged_blockers']) == 88
assert inherited['original_event_or_core_or_Decision_materializations'] == 0 and not inherited['actual_adoption_ready'] and not inherited['task_complete']
assert entry == [capture(ROOT / r['path'], r['sha256'], r['size_bytes'])[1] for r in rows]
assert installed_entry == [capture(ROOT / r['path'], r['sha256'], r['size_bytes'], r['mode'])[1] for r in installed]
assert sha((HERE / 'source-manifest.json').read_bytes()) == MF
assert len(os.listdir('/proc/self/fd')) == fd_before
report = dict(result='PASS-scoped-independent-retained-fixture-review', source_manifest_sha256=MF, source_rows=240, installed_rows=1010, source_and_installed_entry_exit_identity_equal=True, FD_delta=0, positive_fixture_targets=88, negative_controls=negatives, fixture_time_evaluated=response['payload']['issued_at'], real_current_authority_evaluated=False, original_intents_blocked=88, original_materializations=0, original_semantic_bytes_changed=False, native_or_runtime_or_lease_calls=False, private_original_archives_or_keys_read=False, authority_effect='none', native_seal_qualified=False, task_complete=False)
with (HERE / 'independent-review-controls-0001.json').open('x') as stream:
    stream.write(json.dumps(report, sort_keys=True, indent=2) + '\n')
print(json.dumps(report, sort_keys=True))
