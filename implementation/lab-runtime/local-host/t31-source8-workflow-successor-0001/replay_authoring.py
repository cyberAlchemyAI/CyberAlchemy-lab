"""Reconstruct the selected T31 source code from exact retained predecessor bytes.

This post-construction replay is read-only. It does not sign a Source, rerun an
effect, or claim to be a contemporaneous construction log.
"""
import ast
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'implementation/lab-runtime/local-host/source8-current-fixture/instances'
INSTANCE = 'legacy-local-ce4d53a6479188a5'
DEST = BASE / INSTANCE / 'source'
RECORDS_PRE = BASE / 'legacy-local-3bda8c54e9af17c2/source/records.py'
BUILD_PRE = BASE / 'legacy-local-710362c855a8a11c/source/build.py'
PINS = {
    RECORDS_PRE: '2d3709c7a9df3180ab53b0b14b2e44b4ea50151969cd90695bbb866665cff3c7',
    BUILD_PRE: 'eaaa85f2dc76aeafe47453408460abe074d634005a357b44fb35b5c56931ec7b',
}
RESULTS = {
    'records.py': '6c9d75a3f0f24f68cdcbaff10ee8a7db13b7c33178915e7288c66a5f54974157',
    'build.py': '3a1286df0dbd15afed38e6325389118c158270b951832db546159b4329899338',
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_exact(path, digest):
    if not path.is_file() or path.is_symlink():
        raise ValueError('selected authoring input missing or linked: ' + str(path))
    raw = path.read_bytes()
    if sha(raw) != digest:
        raise ValueError('selected authoring input changed: ' + str(path))
    return raw.decode('utf-8')


def once(value, before, after):
    if value.count(before) != 1:
        raise ValueError('authoring anchor missing or ambiguous: ' + before[:50])
    return value.replace(before, after)


def records():
    value = read_exact(RECORDS_PRE, PINS[RECORDS_PRE])
    value = value.replace('3bda8c54e9af17c2', INSTANCE.removeprefix('legacy-local-'))
    value = once(value, "INTENT = 'intent:' + PREFIX\n",
        "INTENT = 'intent:' + PREFIX\n"
        "RESOLUTION = 'intent-resolution:' + PREFIX + ':workflow'\n"
        "DECISION = 'decision:' + PREFIX + ':workflow'\n"
        "EFFECT = 'effect:' + PREFIX + ':workflow'\n")
    marker = "    return {'principal': principal, 'principal-reference': principal_reference, 'intent': intent, 'goal': goal, 'work': work, 'agent-profile': profile,\n"
    added = """    resolution = common('intent-resolution', RESOLUTION, scope)
    resolution['name'] = 'Select the fresh API30 inspection Work for one bounded workflow'
    resolution['payload'].update(intent_ref=INTENT, owner_decision_ref=DECISION,
        selected_subject_refs=[WORK + '@' + VERSION], excluded_subject_refs=[],
        satisfaction_test_refs=['protocol:R03-source-pinned-report-and-Session-consumption'])
    resolution['relation_refs'] = [{'relation_kind_ref': 'relation.declares-effect-on',
        'direction': 'target', 'counterpart_kind': 'decision',
        'counterpart_ref': DECISION + '@' + VERSION}]
    decision = common('decision', DECISION, scope)
    decision['schema_version'] = 'cyberalchemy-lab-decision/v2'
    decision['name'] = 'Controlled local workflow selection decision'
    decision['payload'].update(decision_maker_ref=PRINCIPAL,
        declared_effect_refs=[EFFECT], evidence_basis_refs=[EVIDENCE],
        selected_outcome='select the exact Work for a local candidate workflow',
        subject_refs=[RESOLUTION + '@' + VERSION])
    decision['relation_refs'] = [relation_ref('relation.declares-effect-on',
        'intent-resolution', RESOLUTION + '@' + VERSION)]
    effect = common('effect', EFFECT, scope)
    effect['name'] = 'Candidate workflow selection declaration only'
    effect['payload'].update(effect_kind='candidate-coordination-selection',
        effective_when='only after the exact signed source and private workflow grant validate',
        intended_state='candidate-current', subject_ref=RESOLUTION + '@' + VERSION,
        verification_refs=[EVIDENCE])
    effect['relation_refs'] = [{'relation_kind_ref': 'relation.declares-effect-on',
        'direction': 'target', 'counterpart_kind': 'decision',
        'counterpart_ref': DECISION + '@' + VERSION}]
"""
    value = once(value, marker, added + marker.replace(" 'agent-profile': profile,", "\n        'intent-resolution': resolution, 'decision': decision, 'effect': effect, 'agent-profile': profile,"))
    value = once(value,
        "('/v2' if kind == 'coordination-context' else '/v1')",
        "('/v2' if kind in ('coordination-context', 'decision') else '/v1')")
    value = once(value,
        "        ('context-goal', 'relation.frames', CONTEXT, GOAL, {'framing_role': 'Relevance for the one selected Goal'}),\n",
        "        ('context-goal', 'relation.frames', CONTEXT, GOAL, {'framing_role': 'Relevance for the one selected Goal'}),\n"
        "        ('workflow-decision-resolution', 'relation.declares-effect-on', DECISION, RESOLUTION,\n"
        "            {'effect_kind': 'candidate-coordination-selection',\n"
        "             'exact_target_version_ref': RESOLUTION + '@' + VERSION}),\n")
    return value


def build():
    value = read_exact(BUILD_PRE, PINS[BUILD_PRE])
    value = value.replace('710362c855a8a11c', INSTANCE.removeprefix('legacy-local-'))
    before = next(line for line in value.splitlines(keepends=True) if line.startswith('PRIVATE_ARCHIVE=Path('))
    value = once(value, before,
        "PRIVATE_ARCHIVE=Path('/tmp/cal-t31-workflow-source-" + INSTANCE + '/' + INSTANCE + "/branch.snapshot')\n")
    for original, successor in (
        ("len(items)==21,'all eleven sources and ten Typed Relations required'", "len(items)==25,'all fourteen sources and eleven Typed Relations required'"),
        ("len(cores)==21 and post!=before['projection'],'twenty-one independent prospective cores required'", "len(cores)==25 and post!=before['projection'],'twenty-five independent prospective cores required'"),
        ("'authored_current_artifacts':11,'authored_current_typed_relations':10", "'authored_current_artifacts':14,'authored_current_typed_relations':11"),
        ("'independent_participation_decision_cores':21", "'independent_participation_decision_cores':25"),
        ("'actual_original_targets':23,'records':21", "'actual_original_targets':27,'records':25"),
    ):
        value = once(value, original, successor)
    return value


def main():
    for name, value in (('records.py', records()), ('build.py', build())):
        raw = value.encode('utf-8')
        ast.parse(value)
        if sha(raw) != RESULTS[name] or read_exact(DEST / name, RESULTS[name]).encode('utf-8') != raw:
            raise ValueError('reconstructed selected source differs: ' + name)
        print(name, RESULTS[name])


if __name__ == '__main__':
    main()
