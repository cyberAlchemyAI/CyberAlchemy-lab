/** Private-brand dispatch for the three source-owned ways to produce one
 * observation: a returned remote result, a local step, or recovery of a
 * quiescent dispatched predecessor. Each owner rechecks its own custody.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {assertCommerceWorkflowObservationAdmissionV1,
 CommerceWorkflowObservationAdmissionErrorV1,
 type CommerceWorkflowObservationAdmissionV1}
 from './commerce-workflow-observation-admission-v1.js';
import {assertCommerceWorkflowLocalObservationAdmissionV1,
 CommerceWorkflowLocalObservationAdmissionErrorV1,
 type CommerceWorkflowLocalObservationAdmissionV1}
 from './commerce-workflow-local-observation-admission-v1.js';
import {assertCommerceWorkflowRecoveryObservationAdmissionV1,
 CommerceWorkflowRecoveryObservationAdmissionErrorV1,
 type CommerceWorkflowRecoveryObservationAdmissionV1}
 from './commerce-workflow-recovery-observation-admission-v1.js';

export type CommerceWorkflowAnyObservationAdmissionV1=
 CommerceWorkflowObservationAdmissionV1|
 CommerceWorkflowLocalObservationAdmissionV1|
 CommerceWorkflowRecoveryObservationAdmissionV1;

export type CommerceWorkflowCheckedObservationAdmissionV1=
 Readonly<{kind:'remote-result';owner:CommerceWorkflowObservationAdmissionV1;
  inspection:ReturnType<CommerceWorkflowObservationAdmissionV1['inspect']>}>|
 Readonly<{kind:'local';owner:CommerceWorkflowLocalObservationAdmissionV1;
  inspection:ReturnType<CommerceWorkflowLocalObservationAdmissionV1['inspect']>}>|
 Readonly<{kind:'quiescent-recovery';owner:CommerceWorkflowRecoveryObservationAdmissionV1;
  inspection:ReturnType<CommerceWorkflowRecoveryObservationAdmissionV1['inspect']>}>;

/** Fall through only on a proven foreign private brand. A stale recognized
 * owner fails immediately, even if another admission class exists. */
export function assertCommerceWorkflowAnyObservationAdmissionV1(
 owner:CommerceWorkflowAnyObservationAdmissionV1,
):void {
 try{assertCommerceWorkflowObservationAdmissionV1(owner as CommerceWorkflowObservationAdmissionV1);return;}
 catch(error){
  if(!(error instanceof CommerceWorkflowObservationAdmissionErrorV1)||error.code!=='ForeignOwner')throw error;
 }
 try{assertCommerceWorkflowLocalObservationAdmissionV1(owner as CommerceWorkflowLocalObservationAdmissionV1);return;}
 catch(error){
  if(!(error instanceof CommerceWorkflowLocalObservationAdmissionErrorV1)||error.code!=='ForeignOwner')throw error;
 }
 assertCommerceWorkflowRecoveryObservationAdmissionV1(owner as CommerceWorkflowRecoveryObservationAdmissionV1);
}

/** Only private factories can produce a checked result. Callers receive the
 * inspected source category, never authority derived from a copied object. */
export function inspectCommerceWorkflowAnyObservationAdmissionV1(
 owner:CommerceWorkflowAnyObservationAdmissionV1,
):CommerceWorkflowCheckedObservationAdmissionV1 {
 try{
  const original=owner as CommerceWorkflowObservationAdmissionV1;
  const inspection=assertCommerceWorkflowObservationAdmissionV1(original);
  return Object.freeze({kind:'remote-result' as const,owner:original,inspection});
 }catch(error){
  if(!(error instanceof CommerceWorkflowObservationAdmissionErrorV1)||error.code!=='ForeignOwner')throw error;
 }
 try{
  const local=owner as CommerceWorkflowLocalObservationAdmissionV1;
  const inspection=assertCommerceWorkflowLocalObservationAdmissionV1(local);
  return Object.freeze({kind:'local' as const,owner:local,inspection});
 }catch(error){
  if(!(error instanceof CommerceWorkflowLocalObservationAdmissionErrorV1)||error.code!=='ForeignOwner')throw error;
 }
 const recovery=owner as CommerceWorkflowRecoveryObservationAdmissionV1;
 const inspection=assertCommerceWorkflowRecoveryObservationAdmissionV1(recovery);
 return Object.freeze({kind:'quiescent-recovery' as const,owner:recovery,inspection});
}
