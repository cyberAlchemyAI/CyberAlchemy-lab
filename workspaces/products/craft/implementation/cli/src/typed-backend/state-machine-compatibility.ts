import {decodeBody,type StateTransitionSpec} from '../input/project-model.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';
import {assertStateMachineData,decodeTypedStateMachineContract,freezeStateMachine,stateMachineObject,stateMachineFail,TYPED_STATE_MACHINE_VERSION} from './state-machine.js';

/** Non-writing migration. An old output edge never supplies a missing trigger. */
export function migrateLegacyStateMachine(source:unknown,bindings:unknown){
  assertStateMachineData(source);assertStateMachineData(bindings);
  const raw=stateMachineObject(source,['description','states','initial','transitions']);
  const legacy=decodeBody('State Machine',raw),old=legacy.transitions as readonly StateTransitionSpec[];
  const b=stateMachineObject(bindings,['ontology_state_machine','inputs','transitions']);
  if(!Array.isArray(b.transitions)||b.transitions.length!==old.length)stateMachineFail('migration requires every transition binding');
  const rows=(b.transitions as unknown[]).map(v=>stateMachineObject(v,['transition_id','trigger_event_ref','guard_arguments','output_slot']));
  if(new Set(rows.map(r=>r.transition_id)).size!==rows.length||rows.some(r=>!old.some(t=>t.transition_id===r.transition_id)))stateMachineFail('migration transition coverage');
  const contract=decodeTypedStateMachineContract({schema_version:TYPED_STATE_MACHINE_VERSION,ontology_state_machine:b.ontology_state_machine,inputs:b.inputs,states:legacy.states,initial:legacy.initial,transitions:old.map(t=>{
    const row=rows.find(r=>r.transition_id===t.transition_id)!;
    if(t.guard_ref===null&&row.guard_arguments!==null)stateMachineFail('migration cannot add a guard');
    if(t.effect_event_ref===null&&row.output_slot!==null)stateMachineFail('migration cannot add an output');
    return {transition_id:t.transition_id,source_state:t.source_state,target_state:t.target_state,trigger_event_ref:row.trigger_event_ref,
      guard:t.guard_ref===null?null:{selector:t.guard_ref,arguments:row.guard_arguments},
      output_intents:t.effect_event_ref===null?[]:[{slot:row.output_slot,event_ref:t.effect_event_ref}]};
  })});
  return freezeStateMachine({schema_version:'domainspec.state-machine-migration/v1-candidate',legacy_sha256:sha256(canonicalJson(legacy)),body:{description:legacy.description,typed_contract:contract},
    relationship_review:{legacy_output_events:[...new Set(old.flatMap(t=>t.effect_event_ref===null?[]:[t.effect_event_ref]))].sort(),required_trigger_events:[...new Set(contract.transitions.map(t=>t.trigger_event_ref))].sort(),action:'explicitly reconcile incoming transitions edges; do not retain an output edge unless independently declared as a trigger'},
    graph_effect:'none',authority_effect:'none'});
}
