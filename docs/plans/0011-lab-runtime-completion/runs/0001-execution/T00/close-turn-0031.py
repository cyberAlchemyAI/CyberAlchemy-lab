"""Root authoritative progress closure after interrupted runtime observation."""
import datetime,hashlib,json
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
sha=lambda b:hashlib.sha256(b).hexdigest()
def write(p,v):
    with p.open('x')as f:json.dump(v,f,sort_keys=True,indent=2);f.write('\n')
def binding(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes())}
statepath=RUN/'execution-state.json';before=statepath.read_bytes()
assert sha(before)=='890cdd4232e110efdc6e1c1b10c44c03a57457141a3ebbee5a4dcd26a52618a3'
state=json.loads(before)
root4=RUN/'T32/native-node-recovery-root-0004'
selection=json.loads((root4/'qualification-selection.json').read_bytes())
output=Path(selection['output_root']['path'])
assert not(output/'result.json').exists()
cases=[json.loads((output/name).read_bytes())for name in ['case-01.json','case-02.json']]
assert all(row['result']=='PASS'for row in cases)
interrupted={'schema_version':'lab-T32-interrupted-owned-native-observation/v1-candidate','authority_effect':'none',
 'recorded_at':now,'session_id':49472,'initial_chunk':'8eeee8','poll_failure':'Unknown process id 49472',
 'process_search':{'chunk':'41f849','exit_code':1,'matching_qualifier_processes':0},
 'result':'INTERRUPTED-terminal-code-and-final-exits-unobserved','exit_code':None,
 'qualification_selection_binding':binding(root4/'qualification-selection.json'),
 'owned_output_root':selection['output_root'],'owned_store_parent':selection['store_parent'],
 'observed_case_receipts':cases,'actual_final_result_present':False,
 'full_Source_profile_executor_boundary_exit_checks_observed':False,'strict_operational_final_FD_map_observed':False,
 'interruption_cause_or_exact_termination_time_proved':False,'all_owned_native_and_output_residue_preserved':True,
 'old_packet_deadline_extended_or_old_unknown_effect_redispatched':False,
 'bounded_fourcase_or_whole_runtime_qualified':False}
write(root4/'terminal.json',interrupted)
evidence={
 'T07':['T07/ontology-native-execution-independent-review-0002/independent-review-0001.json','T07/ontology-installation-independent-review-0002/independent-review-0001.json','T07/ontology-installation-root-0002/terminal.json'],
 'T31':['T31/output-integration-preparation-0005/HANDOFF.json','T31/output-integration-independent-review-0005/independent-review-0001.json','T31/output-integration-root-controls-0005/result.json','T31/output-integration-root-controls-0005-successor-0001/result.json','T31/output-integration-root-controls-0005-successor-0002/result.json','T31/output-integration-independent-review-0005/Root-replay-sidecar-review-0001.json','T31/output-integration-Root-acceptance-0005.json'],
 'T32':['T32/native-store-guard-composition-Root-review-0001/review.json','T32/native-node-recovery-root-0003/terminal.json','T32/native-node-recovery-qualification-independent-review-0003/CAP03-erratum-0001.json','T32/native-node-recovery-qualification-preparation-0004/HANDOFF.json','T32/native-node-recovery-qualification-independent-review-0004/review.json','T32/native-node-recovery-root-0004/Root-review.json','T32/native-node-recovery-root-0004/terminal.json']}
for task,rows in evidence.items():
    for row in rows:
        assert(RUN/row).is_file(),row
        if row not in state['task_states'][task]['accepted_evidence']:state['task_states'][task]['accepted_evidence'].append(row)
notes={
'T07':' Turn31: fresh explicitly versioned827 role independently PASS and actual newowned ontology0002-tu00qs02 provision81428/155ccdexit0:1011payloads+receipt; full Source/profile/720+77ELF/1010/new1011/all176 entryexitPASS andFD0. Actualselector3b679/receiptabbd, Rootterminalc07a. Old574/480equivalence unproved. Source6v5union0002/data peerPASS and callbackclosure report frozen; actualmerge/aggregate/software3/snapshots/finalpacket/capture pending.',
'T31':' Turn31: coherentv5 independentlyPASS947static+23inert; bothW06result-verifier integration and finalinput UID700 defects fixed, all10/28/33/293/26targets/Service103 preserved. Original authoredsuite failed missing isolatedfixtureimport; firstRootrelocatedcopy retained absolute inertHERE andfailed; bothpreserved. Secondimmutable testonlysidecar fixes exactly2fixturefiles, all26productionpostimages unchanged: actual53617/d4b2deexit0,110checks/full58+60entryexit/exactFDmap0; independent36893PASS. Root scopedcodeacceptance frozen; all28genuine producers/authority/output/journal qualification andactualSource6 stillpending.',
'T32':' Turn31: guardcomposition Rootaccepted. Runner3 actual63972/246d89exit1 beforeSource/native due32MiB reader againstselectedCargo40680304bytes, preserveerratum. Immutable runner4 exactCargo reviewedcontrol capture fix retains originalcapture/13helpers/4case/finally; independent382rows/47+15+9controlsPASSFD0. Actual49472/8eeee8 underfresh899deadline03:32:58UTC reached2PASS case receipts; turninterruption leaveshandlemissing/noPID/noresult, finalguards/FDmap/exitcodeunobserved. Allresidue retained; nofourcase/runtime qualification. Freshintegritypostcheck/separatenewownedtest required. Original27/26lifecycle/29withdrawal/48migration/3paths/N01-N11/T14 scope retained.'}
for task,note in notes.items():state['task_states'][task]['claim_ceiling']+=note
state['updated_at']=now;state['goal_complete']=False
completed=sorted(k for k,v in state['task_states'].items()if v['status']=='complete')
assert completed==['T00','T01','T04']
progress={'schema_version':'lab-goal-turn-progress/v1-candidate','authority_effect':'none','recorded_at':now,
 'goal_turn':31,'classification':'progress','previous_turn_classification':'progress','state_preimage_sha256':sha(before),
 'accepted_tasks':completed,'goal_complete':False,'evidence':evidence,
 'actual_progress':['Explicit827role/provision completewithincomponent scope','T31v5peerandfull110inert suite pass after2testfixture corrections; Rootcodeaccepted','Runner4 exactlargepublicinputcorrected/reviewed; actual4case attemptinterrupted2PASS/nofinalqualification'],
 'remaining':['Nativeactualcomplete4cases/fulloriginal3paths/27interruptions/T14coupling','Source6actualmerge/provenance/software/snapshots/packet/capture andwholeoriginalregression','GenuineWork/authority/owner/humanpilot/admission/release original36taskscope']}
write(RUN/'T00/goal-turn-0031-progress.json',progress)
with statepath.open('w')as f:json.dump(state,f,sort_keys=True,indent=2);f.write('\n')
with (RUN/'STATUS.md').open('a')as f:f.write('\nTurn0031 recovered '+now+': explicit827role/provisionactualPASS1011+receipt/FD0; T31v5peer+Root110inertPASS with2testfixture-only corrections, productionbytes unchanged. Rootcodeacceptance scoped. Runner3 preeffectCargo32MiB mismatch preserved; runner4 exactCargo route peerPASS, actual49472 interrupted after2PASS/noresult/finalexits, handlemissing andprocessabsent. Allresidue retained, no4case qualification. Freshpostguard/separatenewtest andSource6actualcomposition stillrequired. Original36tasks/73edges/3accepted completions unchanged.\n')
write(RUN/'T00/goal-turn-0032-start-audit.json',{'recorded_at':now,'authority_effect':'none','previous_turn_classification':'progress','current_state_sha256':sha(statepath.read_bytes()),'live_handle49472':False,'process_search_exit_code':1,'native4_result_absent':True,'new_native_run_started':False,'goal_complete':False})
print(json.dumps({'progress31':binding(RUN/'T00/goal-turn-0031-progress.json'),'state':binding(statepath),'interrupted':binding(root4/'terminal.json'),'accepted':completed},sort_keys=True))

