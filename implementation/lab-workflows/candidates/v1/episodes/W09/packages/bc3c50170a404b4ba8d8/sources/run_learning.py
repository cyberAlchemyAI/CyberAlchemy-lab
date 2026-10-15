#!/usr/bin/env python3
"""Real signed lesson -> new Agent context -> later controlled application."""
from dataclasses import asdict
from pathlib import Path
import shutil
import sys
import tempfile
import time

PACKAGE = Path('/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-workflows/candidates/v1')
sys.path.insert(0,str(PACKAGE/'learning'))
from application import *
from durability import *
sys.path.insert(0,str(ROOT/'implementation/lab-continuity/candidates/v1'))
import continuity
import provision
from lab_runtime.replay import ReplayPins
from lab_runtime.store import VerifiedLegacyReadStore
from native_reader import NativePins, NativeReadStore


def emit(path, value):
    with Path(path).open('xb') as stream: stream.write(encoded(value))


def descriptors(e):
    refs = {}; capability = e.W05_refs['capability']
    for name, filename in [('source-adapter','adapter.py'),('selection-adapter','lessons.py'),
        ('application-adapter','application.py'),('probe-adapter','probe_child.py'),('durability-adapter','durability.py')]:
        source = Path(__file__).resolve().parent/filename if filename in {'adapter.py','application.py'} else PACKAGE/'learning'/filename
        refs[name] = e.put(e.make('implementation',name,{
            'conforms_to_schema_refs':[carrier('implementation')[1]['properties']['schema_version']['const']],
            'realizes_capability_refs':[capability],'implementation_kind':'candidate-bounded-learning-adapter',
            'execution_entrypoint_ref':source.relative_to(ROOT).as_posix()+'#sha256='+byte_sha(source.read_bytes()),
            'environment_contract_ref':'protocol:W06-python-and-current-host-development-permission'},
            ('realizes','source','product-capability',capability)))
        e.edge(name+'-capability','realizes',refs[name],capability,{
            'realization_role':'bounded-operational-learning','exact_target_version_ref':capability})
    return refs


def case_context(e, pack):
    return CaseContext(pack['session_id'],SCOPE,'protocol:W06-real-later-preparation',FAMILY,e.sources[OLD],
        frozenset({'allow-controlled-source-repair'}),frozenset({'controlled-owned-preparation'}),pack['head'],
        pack['context_view']['node_id']+'@candidate.1',pack['ontology_view']['node_id']+'@candidate.1')


def perform(destination, executable):
    destination = Path(destination)
    require(not destination.exists(),'new owned episode output required');destination.mkdir(mode=0o700)
    require(byte_sha(Path(executable).read_bytes()) == parse(continuity.MANIFEST.read_bytes())['native_executable_sha256'],'independent native pin differs')
    row, _, snapshot = continuity.selected_source()
    store_id = 'w06-learning-'+destination.parent.name+'-'+byte_sha(str(destination.resolve()).encode())[:8]
    scope = provision.CandidateScope(store_id,'role:candidate-w06-operator','scope:lab-runtime-local:'+store_id)
    first = later = None; first_host = later_host = None
    branch = provision.CandidateBranch(scope)
    try:
        native_root = branch.root/'native';native_root.mkdir()
        native = continuity.diagnostic_native_fixture(native_root,Path(executable),snapshot)
        initial_store = VerifiedLegacyReadStore(branch.store_path,ROOT,ROOT,branch.pins)
        first = continuity.session_for(initial_store,snapshot,native,'product:cyberalchemy-lab')
        clock = [time.time()]
        guard = CurrentCutGuard(first,branch.store_path,native_root,clock=clock)
        first_pack = guard.pack
        first.note('W06 private session thought');first_host = host_fixture(head=first_pack['head'],context_guard=guard,
            handles=(first.instance_id,first.session_id),now=clock,store_scope=scope.scope_ref)
        first_host.session.note('W06 private session thought')
        draft = CandidateSources(destination/'draft',first_host,record_scope=scope.scope_ref)
        drafting = LessonService(draft,review_reader=lambda _:None)
        reflection_ref, lesson_ref = drafting.draft()
        rule = drafting.rules[lesson_ref]
        rule_bytes = encoded({**asdict(rule),'exclusion_tags':sorted(rule.exclusion_tags),'lesson_ref':lesson_ref,
            'lesson_sha256':draft.records[lesson_ref][1],'authority_effect':'none','fixture_only':True})
        draft.blob('applicability-rule.json',rule_bytes)
        pins, replayed, detail = persist_exact_lesson(branch,draft,lesson_ref,before_effect=guard)
        try: first.context()
        except Exception: pass
        require(first.closed and not first.core._memory,'HEAD change failed to erase initial Agent memory')
        try: first_host.session.check()
        except Exception: pass
        require(first_host.session.closed and not first_host.session._memory,'initial host lease survived changed cut')
        archive_sha = public_archive(branch,pins,replayed,destination/'branch.snapshot')
        # New handles and an independently replayed current-cut generator.
        later_store = VerifiedLegacyReadStore(branch.store_path,ROOT,ROOT,pins)
        later = continuity.session_for(later_store,snapshot,native,lesson_ref)
        next_clock = [time.time()]
        later_guard = CurrentCutGuard(later,branch.store_path,native_root,clock=next_clock)
        pack = later_guard.pack
        require(first_pack['session_id'] != pack['session_id'] and first_pack['instance_id'] != pack['instance_id'],'new Agent must have new handles')
        require(not later.core._memory and pack['short_memory_persisted'] is False,'later Agent inherited short memory')
        selected = next(r for r in pack['resolved_references'] if r['version_ref'] == lesson_ref)
        require(selected['effective_state'] == 'local-admitted-current' and selected['source_binding']['path'] == 'transactions/0000000001.json','later Context did not reconstruct actual committed lesson')
        later_host = host_fixture(head=pack['head'],context_guard=later_guard,handles=(later.instance_id,later.session_id),
            now=next_clock,store_scope=scope.scope_ref)
        e = CandidateSources(destination/'later',later_host,record_scope=scope.scope_ref)
        # Public durable inputs only; no old Session object or memory is consulted.
        for ref, (path, sha) in draft.records.items():
            if draft.roles[ref] == 'output': e.import_record(path,ref,sha)
        replayed_lesson = replayed['projection']['subjects'][lesson_ref]['record']
        require(e.get(lesson_ref,'operational-lesson') == replayed_lesson and byte_sha(encoded(replayed_lesson)) == detail['lesson_sha256'],'Project State and retained exact lesson bytes differ')
        review_ref = e.blob('durable-lesson-review.json',encoded(detail))
        rule_ref = e.blob('durable-applicability-rule.json',rule_bytes)
        persisted_rule = parse(e.original(rule_ref))
        require(persisted_rule['lesson_ref'] == lesson_ref and persisted_rule['lesson_sha256'] == detail['lesson_sha256'],'durable applicability binding differs')
        actual_rule = Applicability(**{k:(frozenset(v) if k == 'exclusion_tags' else v) for k,v in persisted_rule.items() if k in Applicability.__dataclass_fields__})
        def reviewed(ref):
            later_guard()
            if ref != lesson_ref: return None
            e.original(review_ref)
            return ReviewedLesson(ref,detail['lesson_sha256'],'reviewed-for-controlled-use',pack['head'],scope.scope_ref,
                review_ref,'local-admitted-current',True)
        lessons = LessonService(e,review_reader=reviewed);lessons.register_rule(lesson_ref,actual_rule)
        impls = descriptors(e)
        context = case_context(e,pack)
        selection = lessons.select([lesson_ref],context)
        require(selection.selected_refs == (lesson_ref,) and not any(e.get(r)['kind'] == 'lesson-application' for r in e.records),'selection was counted as application')
        application = LessonApplicationService(lessons)
        application_ref = application.apply(selection,lesson_ref,current_context_reader=later.context)
        outcome_ref = application.assess()
        signal_ref,target_ref,effect_ref = application.propose_improvement()
        # Retain native original events for a fresh process, not an ontology cache.
        shutil.copytree(native_root,destination/'native-originals')
        emit(destination/'context-before.json',first_pack);emit(destination/'context-later.json',pack)
        emit(destination/'native-pins.json',{'pins':asdict(native.pins),'claim_ceiling':'Real diagnostic native history only; no Artifact domain mapping.'})
        outcome = e.get(outcome_ref,'lesson-outcome-assessment')
        index = {'schema_version':'lab-W06-real-learning-episode/v1-candidate','authority_effect':'none','actual_owner_outcome':None,
            'signed_lesson_persisted':True,'candidate_scope':asdict(scope),'archive_sha256':archive_sha,'replay_pins':asdict(pins),
            'first_Agent_invalidated':first.closed,'first_memory_erased':not first.core._memory and not first_host.session._memory,
            'new_Agent_handles':{'instance_ref':pack['instance_id'],'session_ref':pack['session_id']},'first_Agent_handles':{'instance_ref':first_pack['instance_id'],'session_ref':first_pack['session_id']},
            'lesson_from_committed_Project_State':selected,'selection_count':1,'applications_after_selection':0,'actual_later_application':True,
            'lesson_ref':lesson_ref,'reflection_ref':reflection_ref,'selection_ref':selection.original_ref,
            'application_ref':application_ref,'outcome_ref':outcome_ref,'improvement_signal_ref':signal_ref,
            'improvement_target_ref':target_ref,'unapplied_effect_ref':effect_ref,'implementation_refs':impls,
            'outcome_disposition':outcome['payload']['disposition'],'causal_claim_ceiling':CAUSAL_CEILING,
            'records':[{'version_ref':r,'path':'later/'+p.name,'sha256':sha,'kind':e.get(r)['kind'],'role':e.roles[r]} for r,(p,sha) in e.records.items()],
            'blobs':[{'reference':r,'path':'later/'+p.name,'sha256':sha} for r,(p,sha) in e.blobs.items()],
            'original_sources':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha} for p,sha in e.sources.items()],
            'canonical_effects_applied':0,'lesson_promoted':False,'general_benefit_established':False,'native_domain_mapping':False}
        later.close();later_host.session.close()
        require(not later.core._memory and not later_host.session._memory,'later Session memory retained')
        index.update(later_Agent_closed=True,later_memory_erased=True)
        emit(destination/'episode-index.json',index)
    finally:
        for agent in [first,later]:
            if agent: agent.close()
        for host in [first_host,later_host]:
            if host: host.session.close()
        branch.close()
    require(branch.closed and not branch.root.exists(),'owned candidate branch/private key remains')
    return index


def cold(index_path, expected_sha, executable):
    index_path = Path(index_path);root = index_path.parent
    require(byte_sha(index_path.read_bytes()) == expected_sha,'independent episode index differs')
    index = parse(index_path.read_bytes())
    for row in index['original_sources']:
        require(byte_sha((ROOT/row['path']).read_bytes()) == row['sha256'],'cold selected source changed')
    records = {}
    for row in index['records']:
        p = root/row['path'];require(p.is_file() and not p.is_symlink() and byte_sha(p.read_bytes()) == row['sha256'],'cold original record drift')
        value = parse(p.read_bytes());validate(value,row['kind']);records[row['version_ref']] = value
    connections = 0
    for value in records.values():
        if value['kind'] != 'typed-relation': continue
        payload = value['payload']
        checked = contracts.typed('cold-existing-pair',payload['relation_kind_ref'],payload['source']['version_ref'],
            payload['target']['version_ref'],records,payload['qualifiers'])['payload']
        require(checked['source'] == payload['source'] and checked['target'] == payload['target'],'cold typed endpoint differs')
        connections += 1
    originals = {}
    for row in index['blobs']:
        p = root/row['path'];require(p.is_file() and not p.is_symlink() and byte_sha(p.read_bytes()) == row['sha256'],'cold original evidence drift')
        originals[row['reference']] = parse(p.read_bytes()) if p.suffix == '.json' else p.read_bytes()
    application = records[index['application_ref']]['payload'];outcome = records[index['outcome_ref']]['payload']
    require(application['lesson_revision_ref'] == index['lesson_ref'] and application['application_posture'] == 'applied-in-controlled-later-case','cold exact lesson application differs')
    require(outcome['lesson_application_ref'] == index['application_ref'] and outcome['causal_claim_ceiling'] == CAUSAL_CEILING,'cold bounded outcome differs')
    selected = originals[index['selection_ref']]
    require(selected['applications_created'] == 0 and selected['selected_refs'] == [index['lesson_ref']],'cold selection/application collapse')
    manifest = parse((root/'later/application-manifest.json').read_bytes())
    require(manifest['lesson_ref'] == index['lesson_ref'] and manifest['result']['validated_records'] == 13 and manifest['inline_only_change'],'cold later original observation differs')
    require(outcome['disposition'] == index['outcome_disposition'] == 'supported-for-this-controlled-case','cold observation/outcome mismatch')
    require((root/'later/repaired_builder.py').read_bytes() == repaired_source(OLD.read_bytes()),'cold exact inline-only transform differs')
    require(index['lesson_promoted'] is False and index['canonical_effects_applied'] == 0 and not index['general_benefit_established'],'cold invented promotion/benefit')
    with tempfile.TemporaryDirectory(prefix='cal-W06-cold-') as temp:
        dest = Path(temp)/'project'
        data = continuity.restore_archive(root/'branch.snapshot',index['archive_sha256'],dest)
        require(data['projection']['subjects'][index['lesson_ref']]['record'] == records[index['lesson_ref']],'cold committed lesson body differs')
        _,_,snapshot = continuity.selected_source()
        native_root = root/'native-originals'
        native = NativeReadStore(native_root/'semantic',native_root/'governance',parse((native_root/'request.json').read_bytes()),
            Path(executable),NativePins(**parse((root/'native-pins.json').read_bytes())['pins']))
        adapter = VerifiedLegacyReadStore(dest,ROOT,ROOT,ReplayPins(**index['replay_pins']))
        agent = continuity.session_for(adapter,snapshot,native,index['lesson_ref'])
        try:
            pack = agent.context()
            resolved = next(r for r in pack['resolved_references'] if r['version_ref'] == index['lesson_ref'])
            require(resolved['effective_state'] == 'local-admitted-current' and not agent.core._memory,'cold new context failed to reconstruct exact lesson')
            require(pack['session_id'] != index['new_Agent_handles']['session_ref'],'cold reused old Session')
        finally: agent.close()
    return {'result':'PASS','signed_original_branch_replayed':True,'new_Agent_lesson_context':True,'original_record_count':len(records),
        'existing_typed_connections_checked':connections,
        'applications_reexecuted':0,'private_key_restored':False,'general_benefit_established':False,'actual_owner_outcome':None}


if __name__ == '__main__':
    if sys.argv[1] == '--cold': result = cold(Path(sys.argv[2]),sys.argv[3],Path(sys.argv[4]))
    else: result = perform(Path(sys.argv[1]),Path(sys.argv[2]))
    sys.stdout.buffer.write(encoded(result))
