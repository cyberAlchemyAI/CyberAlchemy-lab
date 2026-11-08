"""Cold original-byte consumer for bounded negative Product assessment."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(Path.home()/'.local/share/cyberalchemy-lab/native-install/t22-0001/deps'),str(HERE),str(HERE.parent/'t31-durable-output-0001')]
import profiles as P
import output_store as S
import product_negative as N

def main():
    P.need(sys.flags.isolated and sys.dont_write_bytecode,'isolated negative Product later consumer required')
    raw=Path(sys.argv[1]).read_bytes();P.need(P.sha(raw)==sys.argv[2],'actual Product result bytes differ');result=json.loads(raw)
    P.need(result['actual_owned_commits']==2 and len(result['families'])==1,'actual Product phase count differs')
    family=result['families'][0];parent=Path(family['journal_archive']).parent
    receipt_raw=S.read_owned(parent/'producer.json');P.need(P.sha(receipt_raw)==family['producer_receipt_sha256'],'actual negative Product producer differs');receipt=json.loads(receipt_raw)
    profile=P.load('engineering');P.guard(profile)
    product_raw=S.read_owned(parent/'actual-source-product.json');capability_raw=S.read_owned(parent/'actual-source-capability.json')
    implementation_raw=S.read_owned(parent/'actual-retained-implementation.json')
    ph,ch,ih=(receipt[k] for k in ('selected_product','selected_capability','selected_observed_implementation'))
    P.need([P.sha(v) for v in (product_raw,capability_raw,implementation_raw)]==[h['byte_sha256'] for h in (ph,ch,ih)],'actual selected Product/Capability/implementation bytes differ')
    product,capability,implementation=map(json.loads,(product_raw,capability_raw,implementation_raw))
    P.need(product['product_id']==ph['identity_ref']==capability['product_ref']
           and capability['node_id']==ch['identity_ref'] and ch['version_ref'] in implementation['payload']['realizes_capability_refs']
           and implementation['node_id']==ih['identity_ref'],'exact observed Product/Capability/implementation semantic join differs')
    P.need(P.sha(implementation_raw)==N.IMPLEMENTATION_SHA and implementation['payload']['execution_entrypoint_ref'].endswith(profile['manifest']['output_source_sha256']),
           'actual corrected implementation lineage differs')
    P.need(receipt['original_work']==family['original_work']==profile['original_work']
           and receipt['original_producer_source_cut']==profile['original_producer_source_cut']
           and not receipt['human_pilot_performed'] and not receipt['actual_pilot_result_available'] and not receipt['original_ready_only_adapter_invoked']
           and receipt['actual_original_assessment_disposition']=='unsupported' and receipt['actual_owner_outcome'] is None,
           'negative Product profile invents pilot, readiness, owner or original Work outcome')
    exclusion=receipt['excluded_original_transition']
    P.need(exclusion['transition_ref']=='transition:product-adoption-release:release-reviewed' and exclusion['required_role']=='role:accountable-owner'
           and exclusion['required_obligation']=='obligation:exact-owner-outcome','original excluded owner contract differs')
    with tempfile.TemporaryDirectory(prefix='cal-T31-negative-product-cold-') as folder:
        root=Path(folder)/'workflow';shutil.copytree(family['journal_archive'],root)
        store=S.OutputJournal(root,family['journal_config_sha256']);head,run_raw=store.replay();run=json.loads(run_raw)
        P.need(head['sequence']==2 and run['state']=='pilot-assessed' and run['work']==profile['original_work'] and run['actor']==result['coordinating_actor'],
               'actual negative Product Run/Actor/head differs')
        rows=[]
        for tx in family['transactions']:
            consumed=store.consume(tx['sequence']);P.need([h for h,b in consumed]==receipt['transitions'][tx['transition_ref']]==tx['outputs'],'exact negative Product output closure differs');rows+=consumed
        binding,assessment=map(json.loads,(rows[0][1],rows[1][1]))
        P.need(binding['capability_version_ref']==ch['version_ref'] and binding['realization_refs'][0]['realization_ref']==ih['version_ref']
               and binding['adoption_decision_ref'] is None and binding['status']=='candidate-unadmitted' and binding['binding_state']=='candidate' and binding['conformance_refs']==[],
               'unqualified candidate binding became adoption/conformance')
        P.need(assessment['payload']['subject_ref']==profile['original_work']['version_ref'] and assessment['payload']['disposition']=='unsupported'
               and 'gap:actual-human-pilot-not-performed' in assessment['payload']['gap_refs'], 'original unsupported outcome or missing pilot was lost')
        P.need(not any(tx['transition_ref']==exclusion['transition_ref'] for tx in family['transactions']),'excluded owner transition was claimed')
        changed=root/'outputs'/rows[0][0]['byte_sha256'];changed.write_bytes(changed.read_bytes()+b' ')
        try:S.OutputJournal(root,family['journal_config_sha256'])
        except (ValueError,OSError):pass
        else:raise ValueError('isolated changed candidate binding accepted')
        print(json.dumps({'result':'PASS-independent-two-negative-Product-original-consumption','selected_result_sha256':P.sha(raw),'head':head,
          'actual_outputs':[h for h,b in rows],'actual_original_Product_Capability_implementation_join':True,'original_Work_unsupported_preserved':True,
          'human_pilot_performed':False,'actual_owner_outcome':None,'excluded_original_owner_transition':exclusion,'isolated_changed_candidate_refused':True,
          'Source_admission_or_Product_release_claimed':False,'canonical_admissions':0,'authority_effect':'none'},sort_keys=True))
if __name__=='__main__':main()
