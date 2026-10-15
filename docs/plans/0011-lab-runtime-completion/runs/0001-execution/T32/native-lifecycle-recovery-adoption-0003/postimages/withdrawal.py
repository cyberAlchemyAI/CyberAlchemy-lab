from ..selected_store import StoreFactory
"""Perform the two explicitly scoped signed source effects and native joins."""
from mapping import *


def emit(path, value):
    with path.open('xb') as stream:stream.write((json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode())


def run(executable, executable_sha, output, *, store_factory):
    require(type(store_factory) is StoreFactory, 'selected native store factory required');store_factory.guard()
    output=Path(output).resolve()
    require(output.parent==PACKAGE/'receipts/O02/withdrawal-episodes' and output.name.isdigit()
        and not output.exists(), 'fresh owned source-withdrawal episode path required')
    output.mkdir(parents=True)
    source=native=None;result=None
    try:
        with signed_catalog() as (catalog,operations):
            adapter=CandidateRepresentationAdapter(catalog,operations)
            view=adapter.represent({**bind(WORK),'kind':'work','version_ref':REF})
            require(view['source_admission']=='candidate-unadmitted' and view['signed_catalog_subject_binding'] is None,
                'selected catalog cannot claim the new fixture is admitted')
            translator=RichTranslation(adapter,bind(PROFILE))
            source=SourceFixture(WithdrawalScope())
            admitted,admission=source.commit('admit')
            native=store_factory.create(translator,executable,executable_sha)
            node,rich=native.map_node(view)
            mapper=SourceEligibilityMapping(native)
            admit_witness=mapper.apply(node,admitted)
            require(mapper.current_source(node,admitted)==parse(WORK.read_bytes()), 'signed current source unavailable')
            initial=native.read();semantic_bytes={k:v for k,v in native.files().items() if k.startswith('semantic/')}
            emit(output/'admitted-native-view.json',initial)
            withdrawn,withdrawal=source.commit('withdraw')
            withdraw_witness=mapper.apply(node,withdrawn)
            final=native.read()
            require(initial['cut']==final['cut'] and semantic_bytes=={k:v for k,v in native.files().items() if k.startswith('semantic/')},
                'source withdrawal changed semantic cut or original native bytes')
            history=mapper.historical_representation(node)
            require(history['state']['lifecycle']=='active' and len(final['cut']['subjects'])==1, 'withdrawal retired or removed representation')
            rejected=[]
            for cut in (withdrawn,admitted):
                try:mapper.current_source(node,cut)
                except RepresentationFault as error:rejected.append(str(error))
            require(len(rejected)==2, 'withdrawn or stale source was usable as current')
            before=native.files();duplicate=mapper.apply(node,withdrawn)
            require(duplicate['idempotent'] is True and native.files()==before, 'duplicate source mapping appended another event')
            retry=source.retry(withdrawal)
            source_archive=source.export();native_archive=native.export()
            for name,value in [('source.snapshot',source_archive),('native.snapshot',native_archive),
                               ('withdrawn-native-view.json',final),('historical-representation.json',history)]:emit(output/name,value)
            witnesses={'profile_binding':bind(PROFILE),'work_binding':bind(WORK),'rich_node':rich,
                'source_effects':[admit_witness,withdraw_witness],
                'source_pins':{k:v['pins'] for k,v in source.snapshots.items()},
                'source_projection_digests':{k:v['projection_sha256'] for k,v in source.snapshots.items()},
                'semantic_original_byte_digests':semantic_bytes,
                'source_archive_binding':bind(output/'source.snapshot'),
                'native_archive_binding':bind(output/'native.snapshot'),
                'complete_native_view_digest':object_sha(final),
                'original_C12_source_archive_binding':bind(ARCHIVE),
                'selected_catalog_posture':view['source_admission'],
                'scope':asdict(source.scope),'authority_effect':'none','actual_owner_outcome':None}
            emit(output/'witnesses.json',witnesses)
            result={'result':'PASS','authority_effect':'none','actual_owner_outcome':None,
                'actual_local_fixture_admissions':1,'actual_local_fixture_withdrawals':1,
                'actual_source_withdrawal_observed':True,'native_semantic_cursor':len(native.semantic_events),
                'native_governance_cursor':len(native.governance_events),'representation_lifecycle':'active',
                'native_semantic_bytes_unchanged':True,'current_source_ineligible':True,
                'historical_representation_inspectable':True,'stale_source_cut_rejected':True,
                'source_retry_idempotent':retry['idempotent'],'native_mapping_retry_idempotent':duplicate['idempotent'],
                'source_project_histories':{k:v['effect']['project_histories'] for k,v in source.snapshots.items()},
                'independent_Decision_identities':admission['proposal']['targets'][0]['decision_ref']!=withdrawal['proposal']['targets'][0]['decision_ref'],
                'native_checkpoint_parity':final['checkpoint_parity'],'original_C12_source_archive_unchanged':sha(ARCHIVE.read_bytes())==ARCHIVE_SHA,
                'private_key_included':False,'Session_memory_included':False,
                'canonical_ontology_admissions_applied':0,'repository_admissions_applied':0,
                'source_projection_digests':witnesses['source_projection_digests'],
                'complete_native_view_digest':object_sha(final),
                'claim_ceiling':'Actual controlled signed local source admission/withdrawal, exact native governance joins, current-source rejection and active historical representation only. No repository/ontology admission or actual R08 owner outcome.'}
    finally:
        if native:
            native.close();require(native.closed and native.root.is_dir(), 'original recovery generations must be retained')
        if source:
            source.close();require(not source.root.exists() and not source.key.exists(), 'owned source root/private key retained')
    require(result is not None, 'source withdrawal episode incomplete')
    result['owned_source_root_removed']=True;result['owned_native_root_removed']=False;result['owned_native_root_retained']=True;result['native_recovery_commit_receipts']=copy.deepcopy(native.commit_receipts);result['fixture_private_key_removed']=True
    emit(output/'result.json',result)
    return result


if __name__ == '__main__':
    raise SystemExit('Use the independently selected private native bootstrap with an actual StoreFactory.')
