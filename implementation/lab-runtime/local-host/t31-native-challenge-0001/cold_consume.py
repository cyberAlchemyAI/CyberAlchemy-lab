"""Consume archived three-phase original challenge-handling output bytes."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[4]
sys.path[:0]=[str(Path.home()/'.local/share/cyberalchemy-lab/native-install/t22-0001/deps'),str(ROOT/'implementation/lab-runtime/local-host/t31-durable-output-0001')]
import output_store as S
def need(ok,message):
    if not ok:raise ValueError(message)
def main():
    need(sys.flags.isolated and sys.dont_write_bytecode,'isolated original-byte consumer required')
    raw=Path(sys.argv[1]).read_bytes();need(S.sha(raw)==sys.argv[2],'selected actual result bytes differ');r=json.loads(raw)
    factory_raw=S.read_owned(Path(r['private_persisted_inputs'])/'factory-receipt.json')
    need(S.sha(factory_raw)==r['actual_new_factory_receipt_sha256'],'new actual factory original differs');factory=json.loads(factory_raw)
    need(factory['new_decision_is_distinct_record'] and factory['actual_owner_outcome'] is None and factory['selected_fixture_outcome']=='defer','new candidate factory outcome differs')
    with tempfile.TemporaryDirectory(prefix='cal-T31-challenge-cold-') as folder:
        root=Path(folder)/'workflow';shutil.copytree(r['journal_archive'],root)
        store=S.OutputJournal(root,r['journal_config_sha256']);head,run=store.replay()
        need(head['sequence']==3 and json.loads(run)['state']=='resolved','original three-phase workflow terminal differs')
        consumed=[];bodies={}
        for sequence,labels in [(1,['eligible']),(2,['responded']),(3,['decision','resolved'])]:
            rows=store.consume(sequence);expected={factory['outputs'][k]['version_ref']:factory['outputs'][k] for k in labels}
            need({h['version_ref'] for h,body in rows}==set(expected),'original phase output closure differs')
            for h,body in rows:
                need(h==expected[h['version_ref']] and S.sha(body)==h['byte_sha256'],'actual factory/committed original differs')
                bodies[h['version_ref']]=json.loads(body);consumed.append({'sequence':sequence,'artifact':h,'sha256':S.sha(body),'byte_size':len(body)})
        outputs=factory['outputs'];events=[bodies[outputs[k]['version_ref']] for k in ('eligible','responded','resolved')]
        need([e['payload']['response_state'] for e in events]==['eligible','responded','deferred'],'typed challenge state lineage differs')
        for field in ('challenger_ref','challenge_contract_ref','subject_ref','subject_version_ref','submitted_at'):
            need(len({e['payload'][field] for e in events})==1,'original native challenge identity changed')
        decision=bodies[outputs['decision']['version_ref']]
        need(decision['schema_version']=='cyberalchemy-lab-decision/v2' and decision['payload']['selected_outcome']=='defer local fixture contest; retain unresolved residue'
             and events[-1]['payload']['resolution_decision_ref']==outputs['decision']['version_ref']
             and decision['payload']['subject_refs']==[outputs['resolved']['version_ref']]
             and events[-1]['payload']['residue_refs']==['residue:local-fixture-contest-awaiting-real-owner'], 'new derived Decision/v2/defer event closure differs')
        changed=root/'outputs'/outputs['decision']['byte_sha256'];changed.write_bytes(changed.read_bytes()+b' ')
        try:S.OutputJournal(root,r['journal_config_sha256'])
        except (ValueError,OSError):pass
        else:raise ValueError('isolated changed Decision original accepted')
        print(json.dumps({'result':'PASS-independent-three-phase-native-challenge-byte-consumption','selected_result_sha256':S.sha(raw),'journal_head':head,'consumed':consumed,
          'new_derived_Decision_v2_verified':True,'historical_signature_not_current_permission':True,'selected_fixture_outcome':'defer','actual_owner_outcome':None,
          'isolated_changed_decision_refused':True,'current_Agent_or_owner_capability_reconstructed':False,'Source_admission_claimed':False,'canonical_admissions':0,'authority_effect':'none'},sort_keys=True))
if __name__=='__main__':main()
