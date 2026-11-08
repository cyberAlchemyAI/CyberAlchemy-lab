"""Fresh-process byte and computational read of six committed original stages."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path[:0]=[str(Path.home()/'.local/share/cyberalchemy-lab/native-install/t22-0001/deps'),str(HERE),str(HERE.parent/'t31-durable-output-0001')]
from jsonschema import Draft202012Validator
import profiles as P
import output_store as S
import observed_replay as R

def main():
    P.need(sys.flags.isolated and sys.dont_write_bytecode,'isolated no-bytecode later consumer required')
    selected=Path(sys.argv[1]);raw=selected.read_bytes();P.need(P.sha(raw)==sys.argv[2],'actual six-phase result bytes differ')
    result=json.loads(raw);P.need(result['actual_owned_commits']==6 and result['canonical_admissions']==0 and result['actual_owner_outcome'] is None,'actual result claim ceiling differs')
    outputs=[];families=[]
    with tempfile.TemporaryDirectory(prefix='cal-T31-original-Work-cold-') as folder:
        for family in result['families']:
            kind=family['kind'];profile=P.load(kind);P.guard(profile)
            parent=Path(family['journal_archive']).parent
            producer_raw=S.read_owned(parent/'producer.json');P.need(P.sha(producer_raw)==family['producer_receipt_sha256'],'actual producer receipt original differs')
            producer=json.loads(producer_raw)
            P.need(producer['original_work']==family['original_work']==profile['original_work']
                   and producer['original_producer_source_cut']==family['original_producer_source_cut']==profile['original_producer_source_cut']
                   and family['current_coordinating_source_cut']==result['source_cut']
                   and producer['original_design_run_schema']=='lab-workflow-design-run/v1-candidate'
                   and producer['original_output_bytes_unchanged'] and not producer['retained_implementation_or_experiment_rerun'],
                   'original Work meaning, producer/current cut distinction or retained origin differs')
            P.need(S.read_owned(parent/'original-producer-result.json')==profile['original_result_raw']
                   and S.read_owned(parent/'original-design-run.json')==profile['original_run_raw'],'actual retained producer lineage differs')
            root=Path(folder)/kind;shutil.copytree(family['journal_archive'],root)
            store=S.OutputJournal(root,family['journal_config_sha256']);head,run_raw=store.replay();run=json.loads(run_raw)
            P.need(head['sequence']==3 and run['state']==('assessed' if kind=='engineering' else 'evaluated')
                   and run['work']==profile['original_work'] and run['source_cut']==result['source_cut']
                   and run['actor']==result['coordinating_actor'],'actual terminal Run/head/Actor/Work differs')
            committed={};bodies={}
            for tx in family['transactions']:
                rows=store.consume(tx['sequence']);P.need([h for h,b in rows]==tx['outputs']==producer['transitions'][tx['transition_ref']],'committed original output closure differs')
                committed[tx['transition_ref']]=rows
                for h,body in rows:
                    P.need(S.sha(body)==h['byte_sha256'],'committed original byte digest differs')
                    bodies[h['version_ref']]=body;outputs.append({'kind':kind,'sequence':tx['sequence'],'artifact':h,'byte_size':len(body)})
            designed='transition:'+kind+':designed';origin=producer['origins'][designed]
            receipt=copy.deepcopy(origin['receipt']);output=receipt.pop('output')
            P.need(origin['origin']=='fresh-actual-original-design-method' and output==committed[designed][0][0]
                   and receipt['actual_original_method_invoked'] and receipt['actual_original_stage_event']['from']=='prepared'
                   and receipt['actual_original_stage_event']['to']=='designed'
                   and receipt['original_code_binding']['sha256']==P.SPECS[kind]['code_sha256'],'actual first design emission provenance differs')
            if kind=='engineering':
                body=json.loads(bodies[output['version_ref']]);digest=P.sha(P.enc(receipt))
                P.need(body['payload']['output_digest']=='sha256:'+digest
                       and body['payload']['reproducibility_receipt_ref']=='original-design-stage:'+digest,'engineering actual design manifest digest differs')
                generator=receipt['generator_artifact'];genraw=P.enc(receipt['generator_original'])
                Draft202012Validator(profile['module'].carrier('implementation')[1]).validate(receipt['generator_original'])
                P.need(P.sha(genraw)==generator['byte_sha256'] and receipt['generator_original']['node_id']==generator['identity_ref']
                       and body['payload']['generator_ref']==generator['version_ref'],'actual design generator original differs')
            else:
                P.need(bodies[output['version_ref']]==profile['raws'][profile['manifest']['design_ref']],'research original ready design body rewritten')
            middle='transition:'+kind+(':implemented' if kind=='engineering' else ':executed')
            computation=R.consume_observed(kind,committed[middle],P.RETAINED)
            P.need(computation==producer['origins'][middle]['later_computation'],'fresh later computation differs from original producer observation')
            victim=root/'outputs'/output['byte_sha256'];victim.write_bytes(victim.read_bytes()+b' ')
            try:S.OutputJournal(root,family['journal_config_sha256'])
            except (ValueError,OSError):pass
            else:raise ValueError('isolated changed original design output accepted')
            families.append({'kind':kind,'head':head,'later_computation':computation,'actual_design_manifest_or_ready_design_verified':True,'isolated_changed_original_refused':True})
    P.need(len(outputs)==9 and len(families)==2,'six phase/nine output-instance actual closure differs')
    print(json.dumps({'result':'PASS-independent-six-phase-nine-original-and-computational-consumption','selected_result_sha256':P.sha(raw),
      'families':families,'outputs':outputs,'original_producer_schema_preserved':True,'retained_implementation_or_experiment_rerun':False,
      'Source_current_original_Work_claimed':False,'Work_satisfaction_asserted':False,'actual_owner_outcome':None,'canonical_admissions':0,'authority_effect':'none'},sort_keys=True))

if __name__=='__main__':main()
