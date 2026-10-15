from .selected_factory import verify_factory
#!/usr/bin/env python3
"""Actual selected Lab/ontology mapping, independent challenge and lifecycle."""
from native_store import *


def emit(path,value):
    path.write_text(json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n')


def run(executable, executable_sha256, output, *, store_factory):
    verify_factory(store_factory)
    output = Path(output).resolve()
    allowed = PACKAGE/'receipts/O02/lifecycle-episodes'
    require(output.parent==allowed and output.name.isdigit() and not output.exists(),'new owned lifecycle evidence path required')
    output.mkdir(parents=True)
    initial_archive_sha = sha(ARCHIVE.read_bytes())
    with signed_catalog() as (catalog,operations):
        adapter = CandidateRepresentationAdapter(catalog,operations)
        translator = RichTranslation(adapter,bind(PROFILE))
        case_path = ROOT/'implementation/lab-workflows/candidates/v1/receipts/integration/W07/0001/scenarios/failure/case.json'
        case = parse(case_path.read_bytes())
        cut = {'cut_id':case['case_id'],'authority_effect':'none','actual_owner_outcome':None,
            'records':[{k:r[k] for k in ['path','sha256','kind','version_ref']} for r in case['records']]}
        view = adapter.candidate_cut(cut);adapter.validate_candidate_relations(view)
        old = next(v for v in view['views'].values() if v['represented_subject']['identity']=='implementation:lab-W05:historical-builder')
        capability = next(v for v in view['views'].values() if v['carrier']['kind']=='product-capability')
        relation = next(v for v in view['views'].values() if v['carrier']['kind']=='typed-relation'
            and v['record']['payload']['source']['version_ref']==old['represented_subject']['version_ref']
            and v['record']['payload']['target']['version_ref']==capability['represented_subject']['version_ref'])
        work_path = ROOT/'implementation/lab-work/candidates/v1/packages/0002/work.json'
        work = adapter.represent({**bind(work_path),'kind':'work','version_ref':'work:lab-development:c12-source-audit-0002@candidate.1'})
        signed = translator.signed_source_effect(work);emit(output/'signed-source-effect.json',signed)
        store = store_factory.create(translator,executable,executable_sha256)
        try:
            work_node,work_witness = store.map_node(work)
            impl_node,impl_witness = store.map_node(old)
            cap_node,cap_witness = store.map_node(capability)
            edge,edge_witness = store.map_relation(relation,view,{
                old['represented_subject']['version_ref']:impl_node,
                capability['represented_subject']['version_ref']:cap_node})
            initial = store.read();emit(output/'initial-native-view.json',initial)
            require(len(initial['cut']['subjects'])==4,'selected native node/relation coverage differs')
            before_semantic = {k:v for k,v in store.files().items() if k.startswith('semantic/')}
            contract = next(r for r in case['records'] if r['kind']=='challenge-contract')
            events = sorted([r for r in case['records'] if r['kind']=='challenge-event'],key=lambda r:r['version_ref'])
            decision = next(r for r in case['records'] if r['kind']=='decision')
            challenge_witnesses = [store.map_challenge(impl_node,r,contract,decision) for r in events]
            challenged = store.read();emit(output/'challenged-native-view.json',challenged)
            require(initial['cut']==challenged['cut'] and before_semantic=={k:v for k,v in store.files().items() if k.startswith('semantic/')},
                'challenge changed semantic cut or original bytes')
            require(len(challenge_witnesses)==4,'all exact W05 source contest revisions required')
            # Every intermediate cut respects native active endpoint rules.
            store.change_lifecycle(edge,'retired')
            store.change_lifecycle(impl_node,'retired')
            retired = store.read();emit(output/'retired-native-view.json',retired)
            require(len(retired['cut']['subjects'])==2,'retired relation/node still present in active cut')
            store.change_lifecycle(impl_node,'active')
            store.change_lifecycle(edge,'active')
            resumed = store.read();emit(output/'reactivated-native-view.json',resumed)
            require(len(resumed['cut']['subjects'])==4,'reversible retirement did not restore active representation')
            store.change_lifecycle(edge,'removed')
            store.change_lifecycle(impl_node,'removed')
            removed = store.read();emit(output/'removed-native-view.json',removed)
            require(len(removed['cut']['subjects'])==2,'removed representation still active')
            require(adapter.represent({**bind(work_path),'kind':'work','version_ref':work['represented_subject']['version_ref']})==work,
                'representation lifecycle changed signed Work source')
            archive = store.export();emit(output/'native.snapshot',archive)
            witnesses = {'work':work_witness,'implementation':impl_witness,'capability':cap_witness,'relation':edge_witness,
                'challenges':challenge_witnesses,'signed_source_effect':signed,'source_case_binding':bind(case_path),
                'profile_binding':bind(PROFILE),'native_event_source_scope':'owned candidate canonical-format events only; no ontology adoption'}
            emit(output/'mapping-witnesses.json',witnesses)
            result = {'result':'PASS','task_complete':False,'authority_effect':'none','actual_owner_outcome':None,
                'native_recovery_commit_receipts':copy.deepcopy(store.commit_receipts),'native_owned_root_retained':True,
                'native_semantic_cursor':len(store.semantic_events),'native_governance_cursor':len(store.governance_events),
                'project_histories':signed['project_histories'],'ontology_history_domain':'separate original native events',
                'rich_nodes':3,'typed_relations':1,'challenge_revisions':4,'challenge_semantic_bytes_unchanged':True,
                'retire_reactivate_remove_observed':True,'source_withdrawal_observed':False,
                'signed_source_effect_verified':True,'original_source_archive_unchanged':sha(ARCHIVE.read_bytes())==initial_archive_sha,
                'source_effects_applied':0,'canonical_ontology_admissions_applied':0,'native_checkpoint_parity':removed['checkpoint_parity'],
                'remaining_obligations':['Actual source-withdrawal mapping and independent eligibility/governance evidence.',
                    'Fresh cold archive reconstruction and full negative/source-currentness guards.',
                    'Exact final native/profile/translation review members and O05/R03 signed transaction coupling.'],
                'claim_ceiling':'Actual rich native representation, signed source-effect selector proof, exact candidate challenge revisions and independent owned lifecycle only. No source withdrawal, ontology adoption, owner outcome, global confirmed edge or full O02 completion.'}
            emit(output/'result.json',result)
            return result
        finally:
            store.close();require(store.closed and store.root.is_dir(),'original recovery generations must be retained')


if __name__ == '__main__':
    raise SystemExit('Use the independently selected private native bootstrap with an actual StoreFactory.')
