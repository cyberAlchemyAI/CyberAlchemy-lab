import type {InvocationControl} from './http-invocation.js';
import type {ReservationRequest,AttemptIdentity,LocalOutcome,RequestInspection} from './request-custody.js';
// Trusted operator port, separate from tenant inference HTTP. Open Questions: ../../REQUEST-CUSTODY.md.
export type ReconciliationTarget=Omit<ReservationRequest,'key'>&{attempt:AttemptIdentity|null};
export interface ReconciliationAudit {operatorId:string;evidenceRef:string;at:number;outcome:LocalOutcome['kind']}
export interface ReconciliationReview extends RequestInspection {version:string;reconciliation:ReconciliationAudit|null}
export interface ReconciliationBinding {
 operatorId:string;
 authorize(input:{operatorId:string;scope:string;requestId:string;action:'custody.review'|'custody.reconcile'},control:InvocationControl):Promise<boolean>;
 resolveEvidence(evidenceRef:string,target:ReconciliationTarget,control:InvocationControl):Promise<{evidenceRef:string;target:ReconciliationTarget;transportSettled:true;outcome:LocalOutcome}>;
}
export interface CustodyReconciliation {
 review(input:{requestId:string;scope:string},control:InvocationControl):Promise<ReconciliationReview>;
 reconcile(input:{requestId:string;scope:string;version:string;evidenceRef:string},control:InvocationControl):Promise<ReconciliationReview>;
}
export function evidenceJson(value:unknown):string {
 if(value===null||typeof value==='string'||typeof value==='boolean')return JSON.stringify(value);
 if(typeof value==='number'&&Number.isFinite(value))return JSON.stringify(value);
 if(Array.isArray(value))return '['+value.map(evidenceJson).join(',')+']';
 if(value&&typeof value==='object'&&Object.getPrototypeOf(value)===Object.prototype)return '{'+Object.keys(value).sort().map(k=>JSON.stringify(k)+':'+evidenceJson((value as any)[k])).join(',')+'}';
 throw Error('INVALID_RECONCILIATION_EVIDENCE');
}
