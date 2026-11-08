/** Finite consumer of existing typed Policy results; not another evaluator.
 * Open Questions: docs/POLICY-ENFORCEMENT.md#open-questions. */
import {coreFreeze,coreSourceFail as fail,coreSourceChildren as children,coreSourceTokens as tokens,type CoreSourceRange} from './commerce-core-syntax.js';
import type {CoreValueType,CoreValueTypes} from './commerce-core-types.js';
import type {CoreCommerceDeclaration} from './commerce-core-reconstruction.js';

export const POLICY_ENFORCEMENT_REVISION='typed-policy-enforcement/v1' as const;
export const POLICY_ENFORCEMENT_CAPABILITY='operation-policy-enforcement' as const;
// Existing contracts/* $defs.FailureCode. Tests bind this finite validator to it.
export const isPolicyRejectionCode=(code:string):boolean=>code.length>=1&&code.length<=128&&/^[A-Za-z_][A-Za-z0-9_-]*$/.test(code);
/** Source syntax is not profile support. Call only with a resolved profile. */
export function assertPolicyEnforcementProfile(declarations:readonly Pick<CoreCommerceDeclaration,'syntax'>[],capabilities:readonly string[]):void {
 const pending=declarations.map(d=>d.syntax);
 while(pending.length){const node=pending.pop()!;
  if(node.rule==='enforce-statement'&&!capabilities.includes(POLICY_ENFORCEMENT_CAPABILITY))fail('UnsupportedCapability',node,'selected profile must explicitly include operation-policy-enforcement');
  for(const child of node.children)if('rule'in child)pending.push(child);
 }
}
export interface CorePolicyEnforcementResult {
 readonly semantics_revision:typeof POLICY_ENFORCEMENT_REVISION;
 readonly result_enum:string;
 readonly reason_enum:string;
 readonly rejections:readonly {readonly variant:string;readonly wire:string;readonly code:string}[];
}
export function checkCorePolicyEnforcementResult(types:CoreValueTypes,result:CoreValueType,where:CoreSourceRange):CorePolicyEnforcementResult {
 if(result.kind!=='enum')return fail('TypeMismatch',where,'enforce Policy must return an ordinary Allow/Reject enum');
 const declaration=types.declarations.get(result.name),allow=declaration?.variants.find(v=>v.name==='Allow'),reject=declaration?.variants.find(v=>v.name==='Reject');
 if(!declaration||declaration.surface!=='Enum'||declaration.variants.length!==2||!allow||allow.fields.length||!reject||reject.fields.length!==1||reject.fields[0]!.name!=='reason')return fail('TypeMismatch',where,'enforce result requires exactly Allow() and Reject(reason finite-enum)');
 const reasonType=types.type(declaration.module,reject.fields[0]!.type,where);
 if(reasonType.kind!=='enum'||reasonType.name===result.name)return fail('TypeMismatch',where,'enforce rejection reason must name a distinct finite nullary enum');
 const reason=types.declarations.get(reasonType.name)!;
 if(!reason.variants.length||reason.variants.some(v=>v.fields.length))return fail('TypeMismatch',where,'enforce rejection reason must be a nonempty nullary enum');
 const authored=children(reason.syntax,'enum-item');
 const rejections=reason.variants.map(v=>{
  const item=authored.find(n=>tokens(n).filter(t=>!t.layout)[1]?.token===v.name);
  if(!item||!tokens(item).some(t=>t.token==='wire'))return fail('InvalidContract',where,'enforce rejection reason requires an explicit wire code: '+v.name);
  if(!isPolicyRejectionCode(v.wire))return fail('InvalidContract',where,'enforce reason wire must satisfy existing FailureCode (1..128 ASCII identifier characters)');
  return {variant:v.name,wire:v.wire,code:v.wire};
 });
 if(new Set(rejections.map(x=>x.code)).size!==rejections.length)return fail('DuplicateSymbol',where,'enforce reason wire codes must be unique');
 return coreFreeze({semantics_revision:POLICY_ENFORCEMENT_REVISION,result_enum:result.name,reason_enum:reasonType.name,rejections});
}
