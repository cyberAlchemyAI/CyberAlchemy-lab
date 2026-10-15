"""Finish failed witness serialization from retained actual signed originals."""
from episode import *


def recover(directory, pins):
    directory=Path(directory).resolve()
    require(directory.is_relative_to(EXAMPLES) and not (directory/'expected-replay.json').exists()
        and not (directory/'result.json').exists(), 'recovery requires the exact incomplete owned episode')
    archive_path=directory/'branch.snapshot';original_archive_sha=sha(archive_path.read_bytes())
    value=parse(archive_path.read_bytes());proposal=parse((directory/'proposal.json').read_bytes())
    approval=parse((directory/'approval.json').read_bytes());application=parse((directory/'application.json').read_bytes())
    sources=parse((directory/'original-source-witnesses.json').read_bytes())
    before_files={p.name:sha(p.read_bytes()) for p in directory.iterdir() if p.is_file()}
    with tempfile.TemporaryDirectory(prefix='cal-R03-retained-recovery-') as tmp:
        owned=Path(tmp);data=restore_archive(archive_path,original_archive_sha,owned/'store',pins)
        with engine(pins) as handle:
            require(len(data['transactions'])==2 and data['transactions'][1]['proposal']==proposal
                and data['transactions'][1]['approval']==approval,'retained signed transaction differs from proposal/approval')
            require(data['transactions'][1]['digest']==application['transaction_digest'], 'retained application digest differs')
            store=handle.store_module.Store(owned/'store',ROOT)
            retried=store.apply(proposal,approval)
            require(retried['idempotent'] is True and retried['transaction_digest']==application['transaction_digest'],
                'retained original retry failed or created another effect')
            after=store.replay(require_current=True)
            require(after['projection']==data['projection'] and len(after['transactions'])==2,'recovery changed signed postimage/history')
            relation_target=next(t for t in proposal['targets'] if t['category']=='typed-relation')
            relation=after['projection']['subjects'][relation_target['version_ref']]
            rejection=frozen_kind_rejection(handle,after['projection'],relation['record'])
            actual_targets=[{'version_ref':t['version_ref'],'carrier_kind':after['projection']['subjects'][t['version_ref']]['kind'],
                'carrier_ref':t['carrier_ref'],'identity_ref':after['projection']['subjects'][t['version_ref']]['identity'],
                'source_binding':after['projection']['subjects'][t['version_ref']]['source'],
                'effective_state':after['projection']['subjects'][t['version_ref']]['effective_state'],
                'record_structural_sha256':handle.common.digest(t['record'])} for t in proposal['targets']]
            views=[handle.mapping.explain(handle.sources.resolve(after['projection']['subjects'],e['version_ref']),after['projection'])
                for e in (relation['record']['payload']['source'],relation['record']['payload']['target'])]
            expected={'projection_sha256':handle.common.digest(after['projection']),
                'transaction_sha256s':[handle.common.digest(tx) for tx in after['transactions']],
                'config_sha256':value['config_sha256'],'baseline_snapshot_digest':value['baseline_snapshot_digest'],
                'expected_head':value['expected_head'],'relation_ref':relation_target['version_ref'],
                'actual_targets':actual_targets,'endpoint_views':views,'engine_pins':asdict(pins),
                'source_binding':bind(archive_path)}
            result={'result':'PASS','domain':'engineering','authority_effect':'none','actual_owner_outcome':None,
                'scope_ref':data['config']['scope_ref'],'source_case_binding':sources['case_binding'],
                'exact_targets':actual_targets,'endpoint_views':views,'frozen_rejection':rejection,
                'fixture_signature_verified':True,'signed_transactions':1,'idempotent_retry':True,
                'signature_basis':'Independently replayed original controlled fixture approval; no human or canonical owner outcome.',
                'semantic_history_before':len(data['baseline']['histories']['project-semantic-event-history']['payload']['events']),
                'semantic_history_after':len(after['projection']['histories']['project-semantic-event-history']['payload']['events']),
                'governance_history_before':len(data['baseline']['histories']['project-governance-event-history']['payload']['events']),
                'governance_history_after':len(after['projection']['histories']['project-governance-event-history']['payload']['events']),
                'original_domain_cases_reexecuted':0,'source_effects_applied':0,'source_record_bytes_preserved':True,
                'canonical_admission':False,'live_operation':False,'runtime_activation':False,
                'private_key_exported':False,'Session_memory_exported':False,
                'recovery_basis':'Actual retained signed archive; no newly signed transaction or key. Original failed witness writer and failure record preserved.'}
    require(not owned.exists(),'owned recovery directory remains')
    require(all(sha((directory/name).read_bytes())==digest for name,digest in before_files.items()),'original failed episode bytes changed')
    result['owned_store_and_key_removed']=True
    emit(directory/'recovered-retry.json',retried);emit(directory/'expected-replay.json',expected);emit(directory/'result.json',result)
    return result


if __name__=='__main__':
    if len(sys.argv)!=3:raise SystemExit('usage: recover_episode.py retained-episode-path pins-json')
    result=recover(sys.argv[1],EnginePins(**parse(Path(sys.argv[2]).read_bytes())))
    print(json.dumps({'result':result['result'],'new_semantic_transactions':0,'original_keys_restored':False,
        'authority_effect':'none','actual_owner_outcome':None},sort_keys=True))
