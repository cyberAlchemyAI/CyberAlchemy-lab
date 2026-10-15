"""Link authored challenge closure and actual bounded results, retaining failures."""
import argparse
import hashlib
import json
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
def load(p):return json.loads(p.read_bytes())
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def emit(p,v):
    with p.open('x') as stream:json.dump(v,stream,indent=2,sort_keys=True);stream.write('\n')
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--api',type=int,required=True)
    parser.add_argument('--terminal-path',required=True);parser.add_argument('--active-check-path');args=parser.parse_args()
    API=BASE/f'api-v{args.api}';source=load(API/'source-manifest.json');profile=load(API/'contract-profile.json')
    assert profile['implemented_operations'][12]=='challenge.submit' and len(profile['implemented_operations'])==21
    parent_path=BASE/'api-v66/receipts/R03-0105.json';parent=load(parent_path)
    terminal_path=RUN/args.terminal_path;terminals=load(terminal_path)
    rows={r['path']:r for r in parent['files']}
    for row in source['files']:rows[row['path']]=row
    outcomes=[]
    for version in range(61,args.api+1):
        folder=BASE/f'api-v{version}'
        for scope in ('focused','full'):
            path=folder/f'receipts/challenge-{scope}-checks-0001.json'
            if not path.exists():continue
            proof=load(path);assert proof['source_sha256']==bind(folder/'source-manifest.json')['sha256']
            assert proof['profile_sha256']==bind(folder/'contract-profile.json')['sha256']
            assert proof['whole_API_qualified'] is False and proof['canonical_admissions_applied']==0
            terminal=[r for r in terminals['terminals'] if r['report_binding']==bind(path)]
            assert len(terminal)==1 and terminal[0]['actual_exit_code']==(0 if proof['result']=='PASS' else 1)
            for row in proof['files']+[bind(path)]:rows[row['path']]=row
            outcomes.append({'version':version,'scope':scope,'result':proof['result'],'actual_cases':proof['actual_cases'],
                'actual_public_calls':proof['actual_public_calls'],'failures':proof['failures'],'errors':proof['errors'],
                'report_binding':bind(path),'terminal':terminal[0]})
    active=None
    if args.active_check_path:
        active_path=RUN/args.active_check_path;active=load(active_path)
        assert active['source_binding']==bind(API/'source-manifest.json') and active['status']=='running-at-observation'
        row=bind(active_path);rows[row['path']]=row
    assert active is not None or any(o['version']==args.api for o in outcomes),'current actual check outcome or observed active job required'
    for p in (API/'source-manifest.json',API/'contract-profile.json',parent_path,terminal_path,Path(__file__).resolve(),
        RUN/'API62-challenge-preflight-diagnosis-0001.json',RUN/'diagnose-API62-challenge-preflight-0001.py',
        RUN/'API64-challenge-preflight-diagnosis-0001.json',RUN/'diagnose-API64-challenge-preflight-0001.py',
        RUN/'API66-challenge-preflight-diagnosis-0001.json',RUN/'diagnose-API66-challenge-preflight-0001.py',
        RUN/'API50-remaining-driver-failed-terminal-0002.json',RUN/'API50-machine14-terminal-0002.json'):
        row=bind(p);rows[row['path']]=row
    for row in rows.values():assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],row['path']
    current=[o for o in outcomes if o['version']==args.api]
    focused_pass=any(o['scope']=='focused' and o['result']=='PASS' for o in current)
    full_pass=any(o['scope']=='full' and o['result']=='PASS' and o['actual_cases']==7 for o in current)
    wire=load(BASE/'api-v67/receipts/challenge-focused-wire-0001.json')['observations'][0]['reply']
    assert wire['kind']=='result' and len(wire['message']['targets'])==4 and len(wire['message']['connection_proposals'])==2
    missing=[o for o in parent['unimplemented_public_operations'] if o!='challenge.submit'];assert len(missing)==13
    machine=load(RUN/'API50-machine14-terminal-0002.json')
    for row in [machine['report_binding'],machine['log_binding']]:rows[row['path']]=row
    for row in rows.values():assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],row['path']
    reset=['lesson_selection_empty_inventory_transport_qualified','package_closed_Work_prospective_target_qualified',
        'package_export_full14_qualified','package_export_runtime_qualified','readonly_lookup_runtime_qualified']
    historical=parent.get('historical_parent_scope_qualifications',{k:parent[k] for k in reset})
    value={**parent,**{k:False for k in reset},'historical_parent_scope_qualifications':historical,'files':[rows[k] for k in sorted(rows)],'parent_progress_binding':bind(parent_path),
        'source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json'),
        'authored_handlers':21,'implemented_public_handlers':21,'implemented_operations':profile['implemented_operations'],
        'unimplemented_public_operation_count':13,'unimplemented_public_operations':missing,
        'challenge_actual_outcomes':outcomes,'challenge_actual_terminal_binding':bind(terminal_path),
        'challenge_current_active_job_observation':active,
        'challenge_submit_authored':True,
        'API67_successful_four_target_reply_observed':True,
        'API67_complete_output_assertions_passed':False,
        'API50_closed_selected_cases':446,'API50_closed_selected_cases_passed':441,
        'API50_closed_selected_assertion_failures':3,'API50_closed_selected_errors':2,
        'API50_unexecuted_termination_cases':6,'API50_original_driver_stopped_after_unexpected_error':True,'challenge_operator_focused_runtime_qualified':focused_pass,
        'challenge_operator_selected_full7_runtime_qualified':full_pass,'challenge_machine_runtime_qualified':False,
        'challenge_factual_ground_adjudication_qualified':False,'challenge_actual_owner_resolution_qualified':False,
        'challenge_complete_evidence_and_typed_connection_closure_authored':True,
        'current_API_version':args.api,
        'change':'Authored original challenge.submit contract; added independently selected finite challenger routing, exact revision/evidence validation, eligibility calculation, candidate journal and retry/recovery routing. API61 failed before public calls because fixture demanded absent admitted Evidence Set. API62 uses explicit unadmitted/bound-original evidence adapters but actual call failed; private original-source diagnosis identified nonempty relation_refs requirements. API63 proposes Evidence Set, Challenge Event and explicit member-of/challenges Typed Relations; its fixture failed before public calls because it selected raw Project kind. API64 uses the existing exact endpoint mapping and actual signed Typed Relation source template. API64 public call failed because its bound-original Decision carrier was historical; actual diagnosis is retained. API65 attempted retained-carrier validation but that native adapter is restricted to Typed Relations. API66 instead verifies the captured original descriptor, discriminator and frozen schema for bound-original document evidence without current endpoint or authority eligibility. API66 refused the v2 Decision under the assumed v1 discriminator; actual diagnosis retained. API67 selects one captured carrier by the exact original discriminator and returned an actual four-target/two-connection result. Its test errored because it read output objects as selected inputs. API68 corrects that output custody accessor and retains all assertions. Original API50 Machine14 completed13PASS/1ERROR with TypeError in Service.reply; the original scheduler stopped and six termination cases remain unrun. Frozen predecessors and failed receipts retained; no original schema or admitted source was changed.',
        'remaining_obligations':[
            'Bridge generated challenge output objects and metadata into independently selected generic candidate validation/review, then qualify the complete workflow. Current proposal shape and local native core preparation do not qualify the generic consumer integration.',
            'Diagnose and repair the current Machine public read/error path; preserve original API50 terminal and complete its unexecuted six termination cases with owned original-clock fixtures. No temporal cause is asserted by the captured TypeError frames.',
            'Qualify complete actual operator challenge candidate closure and all seven selected cases; add complete Machine challenger authority and historical exact endpoint cases. Preserve refusal, retry, recovery and independent routing boundaries.',
            *parent['remaining_obligations']],
        'claim_ceiling':'Actual authored candidate challenge closure and the exact listed runtime outcomes only. Historical owner/export proofs retain their historical scope. No complete current API, Machine challenge authority, factual adjudication, actual owner resolution, R08 outcome, canonical admission or complete plan.',
        'whole_API_qualified':False,'task_complete':False,'goal_complete':False}
    path=API/'receipts/R03-0106.json';emit(path,value)
    print(json.dumps({'result':'PASS','progress_binding':bind(path),'bound_files':len(rows),
        'authored_handlers':21,'missing_operations':13,'challenge_focused_pass':focused_pass,
        'challenge_selected_full7_pass':full_pass,'goal_complete':False}),flush=True)
if __name__=='__main__':main()
