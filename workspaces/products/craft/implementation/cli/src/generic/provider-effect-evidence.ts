/** C13/C15 original-provider evidence decision. An attempted dispatch remains
 * possibly effective until the original C11 owner checks a definitive decline.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import type {GenericCommandResultV1} from './transaction-data-v1.js';
import type {GenericWorkflowStepV1} from './workflow-source.js';

export function providerEffectPossibleAfterObservation(
  earlierPossible:boolean,observation:'Captured'|'DefinitivelyDeclined'|null):boolean {
  return earlierPossible||observation!=='DefinitivelyDeclined';
}

export function mayAttestProviderNoEffect(
  freshExecution:boolean,result:GenericCommandResultV1,providerEffectPossible:boolean):boolean {
  return freshExecution&&result.ok&&result.outcome.kind!=='Returned'&&
    providerEffectPossible===false;
}

export function mayCompensateProviderFailure(
  step:GenericWorkflowStepV1,ownerProvesNoEffect:boolean):boolean {
  return step.kind==='provider-command'&&step.on_definite_failure==='compensate'&&
    step.provider_failure_compensation_precondition==='proven-no-provider-effect'&&
    ownerProvesNoEffect;
}
