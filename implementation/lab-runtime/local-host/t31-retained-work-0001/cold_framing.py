"""Independent original-byte use of the two committed private framing stages."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(Path.home()/'.local/share/cyberalchemy-lab/native-install/t22-0001/deps'),str(HERE),str(HERE.parent/'t31-durable-output-0001')]
import profiles as P
import output_store as S

def main():
    P.need(sys.flags.isolated and sys.dont_write_bytecode,'isolated later framing consumer required')
    raw=Path(sys.argv[1]).read_bytes();P.need(P.sha(raw)==sys.argv[2],'actual framing receipt bytes differ');result=json.loads(raw)
    P.need(result['actual_owned_commits']==2 and len(result['families'])==1,'actual framing commit count differs')
    family=result['families'][0];parent=Path(family['journal_archive']).parent;receipt_raw=S.read_owned(parent/'producer.json')
    P.need(P.sha(receipt_raw)==family['producer_receipt_sha256'],'actual framing producer original differs');receipt=json.loads(receipt_raw)
    profile=P.load('engineering');P.guard(profile)
    P.need(receipt['actual_original_resolver_prepared'] and receipt['original_work']==profile['original_work']==family['original_work']
           and receipt['original_producer_source_cut']==profile['original_producer_source_cut']
           and receipt['current_coordinating_source_cut']==result['source_cut'] and not receipt['original_Work_promoted_to_Source_current']
           and receipt['human_Intent_resolution_or_actual_owner_outcome'] is None,'private versus original framing meaning differs')
    with tempfile.TemporaryDirectory(prefix='cal-T31-framing-cold-') as folder:
        root=Path(folder)/'workflow';shutil.copytree(family['journal_archive'],root)
        store=S.OutputJournal(root,family['journal_config_sha256']);head,run_raw=store.replay();run=json.loads(run_raw)
        P.need(head['sequence']==2 and run['state']=='prepared' and run['work']==profile['original_work']
               and run['actor']==result['coordinating_actor'] and run['source_cut']==result['source_cut'],'actual framing terminal Run differs')
        rows1=store.consume(1);rows2=store.consume(2)
        P.need([h for h,b in rows1]==receipt['transitions']['transition:intent-framing:resolved']
               and [h for h,b in rows2]==receipt['transitions']['transition:intent-framing:prepared'],'exact framing output closure differs')
        ir=json.loads(rows1[0][1]);work_header,work_raw=rows2[0]
        P.need(work_header==profile['original_work'] and work_raw==profile['raws'][work_header['version_ref']]
               and work_header['version_ref'] in ir['payload']['selected_subject_refs']
               and work_header['version_ref'] not in ir['payload']['excluded_subject_refs']
               and ir['payload']['intent_ref']==run['intent']['version_ref'],'later consumer actual private resolution does not select original Work')
        changed=root/'outputs'/rows1[0][0]['byte_sha256'];changed.write_bytes(changed.read_bytes()+b' ')
        try:S.OutputJournal(root,family['journal_config_sha256'])
        except (ValueError,OSError):pass
        else:raise ValueError('isolated changed private resolution accepted')
        print(json.dumps({'result':'PASS-independent-two-framing-original-byte-consumption','selected_result_sha256':P.sha(raw),
          'head':head,'actual_outputs':[h for h,b in rows1+rows2],'later_private_resolution_original_Work_join_verified':True,
          'isolated_changed_resolution_refused':True,'original_Work_bytes_unchanged':True,'original_Work_Source_current_claimed':False,
          'actual_owner_outcome':None,'canonical_admissions':0,'authority_effect':'none'},sort_keys=True))
if __name__=='__main__':main()
