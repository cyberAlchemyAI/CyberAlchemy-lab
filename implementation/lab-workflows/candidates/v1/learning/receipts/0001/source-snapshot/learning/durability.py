"""Owned signed lesson persistence and byte-pinned current-cut host guards.

The guard checks original files after a full replay/context boundary. It supplies
no cached projection or new action authority. New context consumes full replay.
"""
from dataclasses import asdict, replace
import base64
from pathlib import Path
import time
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lessons import *


def committed_paths(store, sequence):
    return [store/n for n in ['config.json','baseline.json','HEAD.json']] + [store/'transactions'/f'{n:010d}.json' for n in range(sequence+1)]


class CurrentCutGuard:
    def __init__(self, agent, store, native_root, *, clock):
        self.agent, self.store, self.clock = agent, Path(store), clock
        pack = agent.context()  # Independent full replay and native verification.
        self.head = pack['head']
        sequence = parse((self.store/'HEAD.json').read_bytes())['sequence']
        self.originals = {p:byte_sha(p.read_bytes()) for p in committed_paths(self.store,sequence)}
        self.originals.update({p:byte_sha(p.read_bytes()) for p in Path(native_root).rglob('*') if p.is_file()})
        self.originals[Path(agent.native_store.executable)] = byte_sha(Path(agent.native_store.executable).read_bytes())
        manifest = parse(agent.manifest_path.read_bytes())
        for row in manifest['files'] + [manifest['implementation_record'],manifest['realization_record']]:
            self.originals[ROOT/row['path']] = row['sha256']
        self.originals[agent.manifest_path] = agent.generator_pins.manifest_sha256
        self.pack = pack

    def __call__(self):
        self.clock[0] = time.time()
        try:
            require(not self.agent.closed and self.agent.core.clock() < self.agent.core.deadline,'actual Project context expired or closed')
            require(all(p.is_file() and not p.is_symlink() and byte_sha(p.read_bytes()) == sha for p,sha in self.originals.items()),'actual committed/native/context source bytes changed')
            require(parse((self.store/'HEAD.json').read_bytes())['transaction_digest'] == self.head,'actual current Project cut changed')
            return {'head':self.head}
        except BaseException:
            self.agent.close()
            raise


def persist_exact_lesson(branch, sources, lesson_ref, *, before_effect):
    """Closed caller boundary: one exact selected lesson, no arbitrary targets."""
    from lab_runtime.replay import full_replay
    sources.check(); before_effect()
    lesson = sources.get(lesson_ref,'operational-lesson')
    require(sources.scope == branch.scope.scope_ref and lesson['scope_ref'] == branch.scope.scope_ref,'selected isolated lesson scope differs')
    original_sha = sources.records[lesson_ref][1]
    data = branch.store.replay(require_current=True); config = data['config']
    proposal_id = branch.scope.store_id+'-lesson'
    proposal = {'schema_version':'lab-runtime-proposal/v1','proposal_id':proposal_id,
        'expected_head':data['head']['transaction_digest'],'source_snapshot_digest':config['source_snapshot_digest'],
        'scope_ref':config['scope_ref'],'policy_ref':config['policy_ref'],'challenge_route':config['challenge_route'],'schemas':{},
        'targets':[{'category':'artifact-instance','operation':'admit','version_ref':lesson_ref,
            'carrier_ref':carrier('operational-lesson')[0]['artifact_type_ref'],'record':lesson,'predecessor_ref':None,
            'decision_ref':'decision:candidate-local:'+proposal_id,'contract':None}]}
    require(len(proposal['targets']) == 1 and proposal['targets'][0]['carrier_ref'] == 'cal.artifact-type.operational-lesson/v1'
        and byte_sha(encoded(proposal['targets'][0]['record'])) == original_sha,'exact reviewed Lesson target changed')
    reviewed = branch.store.review(proposal)
    # A separate current host check precedes signature/effect; review is not permission.
    sources.check(); before_effect()
    require(byte_sha(encoded(sources.get(lesson_ref,'operational-lesson'))) == original_sha,'lesson changed after review')
    approval = branch.store.authorize(proposal,branch.key_path)
    outcome = branch.store.apply(proposal,approval)
    pins = replace(branch.pins,expected_head=outcome['transaction_digest'])
    replayed = full_replay(branch.store_path,ROOT,ROOT,pins,require_current=True)
    subject = replayed['projection']['subjects'][lesson_ref]
    require(subject['effective_state'] == 'local-admitted-current' and subject['record'] == lesson,'actual committed lesson differs')
    detail = {'lesson_ref':lesson_ref,'lesson_sha256':original_sha,'source_head':outcome['transaction_digest'],
        'scope_ref':branch.scope.scope_ref,'disposition':'reviewed-for-controlled-use','fixture_only':True,
        'proposal':proposal,'review':reviewed,'approval':approval,'outcome':outcome,
        'actual_owner_outcome':None,'canonical_admission':False}
    return pins,replayed,detail


def public_archive(branch, pins, replayed, destination):
    archive = {'schema_version':'lab-public-original-branch-archive/v1-candidate','authority_effect':'none',
        'project_pins':asdict(pins),'files':{p.relative_to(branch.store_path).as_posix():{'sha256':byte_sha(p.read_bytes()),
            'base64_original_bytes':base64.b64encode(p.read_bytes()).decode()} for p in committed_paths(branch.store_path,replayed['head']['sequence'])},
        'private_key_included':False,'Session_memory_included':False,'actual_owner_outcome':None}
    raw = encoded(archive)
    require(len(raw) <= 20971520 and b'PRIVATE KEY' not in raw and b'W06 private session thought' not in raw,'public original export violates bounded custody')
    with Path(destination).open('xb') as stream: stream.write(raw)
    return byte_sha(raw)
