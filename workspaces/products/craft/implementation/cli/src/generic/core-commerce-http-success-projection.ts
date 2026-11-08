/** Checked HTTP success value shape for a selected source Query binding.
 * The Query output codec validates values; this adapter removes only the
 * optional wrapper when the HTTP contract declares a concrete value_ref.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import type {ReadPlanV1} from '../commerce/commerce-data-v1.js';

export type CoreCommerceHttpGetSuccessProjection=Readonly<{
 query:string;
 value_ref:string;
 kind:'direct'|'unwrap-some';
}>;

export function selectCoreCommerceHttpGetSuccessProjection(read:ReadPlanV1,valueRef:string):CoreCommerceHttpGetSuccessProjection {
 const match=/^([A-Za-z][A-Za-z0-9]*(?:\.[A-Za-z][A-Za-z0-9]*)+)@1$/.exec(valueRef);
 if(!match||read.kind!=='local'||read.query.role!=='Query')throw new Error('checked local GET Query and versioned value reference required');
 const expected=match[1]!,output=read.output,query=read.query.module+'.'+read.query.name;
 if(output.kind==='record'&&output.name===expected)
  return Object.freeze({query,value_ref:valueRef,kind:'direct' as const});
 if(output.kind==='optional'&&output.element.kind==='record'&&output.element.name===expected&&
   read.on_missing.kind==='reject')
  return Object.freeze({query,value_ref:valueRef,kind:'unwrap-some' as const});
 throw new Error('GET HTTP value reference differs from checked Query output or missing policy');
}

export function projectCoreCommerceHttpGetSuccessValue(projection:CoreCommerceHttpGetSuccessProjection,value:unknown):unknown {
 if(projection.kind==='direct')return value;
 if(!value||typeof value!=='object'||Array.isArray(value)||
   (value as {kind?:unknown}).kind!=='some'||!Object.hasOwn(value,'value'))
  throw new Error('checked GET Query returned no concrete HTTP success value');
 return (value as {value:unknown}).value;
}
