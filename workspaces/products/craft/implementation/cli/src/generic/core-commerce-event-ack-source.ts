/** Checked source paths that may satisfy one Event Entry acknowledgement.
 * This is selection data only; native commit receipts and inbox rows remain
 * required at the effect boundary.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {coreFreeze} from '../commerce/commerce-core-syntax.js';
import type {EntryContractV1,EffectPlanV1,TransactionPlanV1} from '../commerce/commerce-data-v1.js';

export interface CoreCommerceEventAckSource {
 readonly entry:string;readonly operation:string;readonly inbox_entity:string;
 readonly acknowledge_path:string;
 readonly candidates:readonly Readonly<{transaction_path:string;inbox_binding:string}>[];
 readonly qualification:'checked-event-inbox-commit-paths-only;native-receipt-required';
 readonly authority_effect:'none';
}
const prefix=(path:string):number=>{
 const match=/^\$\.body\[(\d+)\](?:\.|$)/.exec(path);
 if(!match)throw new Error('original generated Event transaction path required');
 return Number(match[1]);
};

/** The local plan owner supplies exact transaction paths. This function never
 * fabricates an inbox or decides whether a commit happened. */
export function selectCoreCommerceEventAckSource(entry:EntryContractV1,plan:EffectPlanV1,
 transactions:readonly Readonly<{path:string;plan:TransactionPlanV1}>[]):CoreCommerceEventAckSource {
 const operation=plan.operation.module+'.'+plan.operation.name;
 if(entry.interaction!=='event'||entry.invokes.role!=='Operation'||
  entry.invokes.module+'.'+entry.invokes.name!==operation||entry.service!==plan.service||
  entry.event_argument===null||entry.access.principal_kind!=='service'||
  entry.access.event_completion!=='requires-original-consumer-inbox-and-result-commit'||
  plan.protocol!==null)
  throw new Error('original checked Event Entry and receiver Operation required');
 const acknowledgements=plan.body.flatMap((step,index)=>step.kind==='acknowledge'?
  [{step,index,path:'$.body['+index+']'}]:[]);
 if(acknowledgements.length!==1||
  acknowledgements[0]!.step.kind!=='acknowledge'||
  acknowledgements[0]!.step.required_evidence!=='original-consumer-inbox-and-result-commit')
  throw new Error('one original consumer inbox acknowledgement required');
 const acknowledgement=acknowledgements[0]!,inbox=acknowledgement.step.inbox;
 if(transactions.length<1||transactions.length>128)
  throw new Error('bounded source Event transactions required');
 const candidates=transactions.flatMap(row=>{
  if(prefix(row.path)>=acknowledgement.index||!row.plan.participants.includes(inbox))return [];
  const creates=row.plan.body.filter(step=>step.kind==='mutation'&&step.operation==='create'&&
   step.target===inbox&&['consumerEntryId','occurrenceId','receipt','eventFingerprint'].every(name=>
    step.fields.some(field=>field.name===name)));
  if(creates.length!==1||creates[0]!.kind!=='mutation')return [];
  return [{transaction_path:row.path,inbox_binding:creates[0]!.binding}];
 });
 if(candidates.length<1||new Set(candidates.map(row=>row.transaction_path)).size!==candidates.length)
  throw new Error('checked Event acknowledgement lacks unique consumer inbox commits');
 return coreFreeze({entry:entry.id,operation,inbox_entity:inbox,
  acknowledge_path:acknowledgement.path,candidates,
  qualification:'checked-event-inbox-commit-paths-only;native-receipt-required' as const,
  authority_effect:'none' as const});
}
