/** Optional, bounded TLA+ projection of the original checked C13 Workflow.
 * This models one journal instance and its control transitions. Auth, provider
 * effects, Event delivery, SQLite atomicity, and real time are abstract inputs.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions.
 */
import {createHash} from 'node:crypto';
import {dataDigest} from '../profile-engine/contracts.js';
import {type GenericCompositionHandle,requireGenericWorkflowRuntime} from './public-sdk.js';
import {workflowCompatibilitySha256} from './workflow-worker.js';

export interface GenericWorkflowTlaModelV1 {
 readonly schema_version:'craft.generic-workflow-tla/v1-candidate';
 readonly language:'tla+';
 readonly scope:'one-checked-workflow-journal-instance';
 readonly qualification:'bounded-control-abstraction-only';
 readonly workflow:string;
 readonly service:string;
 readonly steps:readonly Readonly<{name:string;kind:'local-command'|'provider-command'|'event-await'}>[];
 readonly source_capture_sha256:string;
 readonly profile_sha256:string;
 readonly base_application_sha256:string;
 readonly workflow_contract_sha256:string;
 readonly executable_semantics_sha256:string;
 readonly compatibility_sha256:string;
 readonly max_fence:3;
 readonly max_revision:24;
 readonly tla:string;
 readonly tla_sha256:string;
 readonly authority_effect:'none';
 readonly claim_ceiling:'one-instance-journal-control-with-abstract-provider-no-effect-evidence-no-auth-provider-event-sqlite-time-or-model-checker-proof';
}

export class GenericWorkflowTlaUnsupportedError extends Error {
 constructor(readonly code:'InvalidWorkflow'|'InvalidModel') {super(code);this.name='GenericWorkflowTlaUnsupportedError';}
}
const hex=/^[0-9a-f]{64}$/;
const name=/^[A-Za-z_][A-Za-z0-9_]*$/;
const sha=(value:string)=>createHash('sha256').update(value).digest('hex');
const reject=(code:GenericWorkflowTlaUnsupportedError['code']):never=>{throw new GenericWorkflowTlaUnsupportedError(code);};

/** The generated module has fixed TLA+ identifiers. Source names occur only in
 * JSON metadata returned alongside it, avoiding source-controlled syntax. */
function moduleText(identity:Readonly<{source:string;profile:string;application:string;contract:string;executable:string;compatibility:string}>):string {
 return `---- MODULE GenericWorkflowJournal ----
EXTENDS Naturals, Integers
\\* Original checked source identities; comments have hex-only values.
\\* source_capture_sha256=${identity.source}
\\* profile_sha256=${identity.profile}
\\* base_application_sha256=${identity.application}
\\* workflow_contract_sha256=${identity.contract}
\\* executable_semantics_sha256=${identity.executable}
\\* compatibility_sha256=${identity.compatibility}
\\* One instance; C13 checked shape: local command, provider command, event await.
\\* Auth, command/provider outcomes, event receipt, wall clock, and SQLite CAS
\\* are external choices. Outcome and receipt observations are explicit
\\* abstract inputs; they do not prove the underlying external effects.
\\* Provider no-effect evidence is an abstract input;
\\* compensation after provider failure requires that evidence first.
\\* No fairness or eventual-completion claim is made.
MaxFence == 3
MaxRevision == 24
LastStep == 2
EventStep == 2
CompensableStep == 0
Active == {"scheduled", "claimed", "step-prepared", "step-committed",
           "suspended-unknown", "waiting-event", "compensating"}
Terminal == {"completed", "compensated", "needs-review"}
States == Active \\cup Terminal
VARIABLES phase, step, fence, revision, held, compensationPrepared, providerNoEffect,
          commandSuccessObserved, eventReceiptObserved
vars == <<phase, step, fence, revision, held, compensationPrepared, providerNoEffect,
          commandSuccessObserved, eventReceiptObserved>>
Init == /\\ phase = "scheduled"
        /\\ step = -1
        /\\ fence = 0
        /\\ revision = 0
        /\\ held = FALSE
        /\\ compensationPrepared = FALSE
        /\\ providerNoEffect = FALSE
        /\\ commandSuccessObserved = FALSE
        /\\ eventReceiptObserved = FALSE
Claim == /\\ phase \\in Active /\\ ~held /\\ fence < MaxFence /\\ revision < MaxRevision
         /\\ phase' = IF phase = "scheduled" THEN "claimed" ELSE phase
         /\\ fence' = fence + 1 /\\ revision' = revision + 1 /\\ held' = TRUE
         /\\ providerNoEffect' = FALSE
         /\\ UNCHANGED <<step, compensationPrepared, commandSuccessObserved,
                        eventReceiptObserved>>
Expire == /\\ held /\\ phase \\in Active /\\ held' = FALSE
          /\\ providerNoEffect' = FALSE
          /\\ UNCHANGED <<phase, step, fence, revision, compensationPrepared,
                         commandSuccessObserved, eventReceiptObserved>>
Renew == /\\ held /\\ phase \\in Active /\\ revision < MaxRevision
         /\\ revision' = revision + 1
         /\\ UNCHANGED <<phase, step, fence, held, compensationPrepared,
                        providerNoEffect, commandSuccessObserved, eventReceiptObserved>>
PrepareStep == /\\ held /\\ phase \\in {"claimed", "step-committed"}
               /\\ step < EventStep - 1 /\\ revision < MaxRevision
               /\\ phase' = "step-prepared" /\\ step' = step + 1
               /\\ revision' = revision + 1 /\\ providerNoEffect' = FALSE
               /\\ commandSuccessObserved' = FALSE
               /\\ UNCHANGED <<fence, held, compensationPrepared, eventReceiptObserved>>
ObserveCommandSuccess == /\\ held
                         /\\ phase \\in {"step-prepared", "suspended-unknown"}
                         /\\ ~commandSuccessObserved /\\ revision < MaxRevision
                         /\\ commandSuccessObserved' = TRUE
                         /\\ revision' = revision + 1
                         /\\ UNCHANGED <<phase, step, fence, held,
                                        compensationPrepared, providerNoEffect,
                                        eventReceiptObserved>>
CommitStep == /\\ held /\\ phase \\in {"step-prepared", "suspended-unknown"}
              /\\ commandSuccessObserved /\\ revision < MaxRevision
              /\\ phase' = "step-committed"
              /\\ revision' = revision + 1 /\\ providerNoEffect' = FALSE
              /\\ UNCHANGED <<step, fence, held, compensationPrepared,
                             commandSuccessObserved, eventReceiptObserved>>
SuspendUnknown == /\\ held /\\ phase = "step-prepared" /\\ revision < MaxRevision
                  /\\ phase' = "suspended-unknown" /\\ revision' = revision + 1
                  /\\ UNCHANGED <<step, fence, held, compensationPrepared,
                                 providerNoEffect, commandSuccessObserved,
                                 eventReceiptObserved>>
ProveNoProviderEffect == /\\ held /\\ step = 1
                         /\\ phase \\in {"step-prepared", "suspended-unknown"}
                         /\\ ~providerNoEffect /\\ revision < MaxRevision
                         /\\ providerNoEffect' = TRUE /\\ revision' = revision + 1
                         /\\ UNCHANGED <<phase, step, fence, held,
                                        compensationPrepared, commandSuccessObserved,
                                        eventReceiptObserved>>
DefiniteFailure == /\\ held /\\ phase \\in {"step-prepared", "suspended-unknown"}
                   /\\ (step = 0 \\/ (step = 1 /\\ providerNoEffect))
                   /\\ revision < MaxRevision /\\ phase' = "compensating"
                   /\\ step' = IF step > CompensableStep THEN CompensableStep ELSE -1
                   /\\ revision' = revision + 1 /\\ providerNoEffect' = FALSE
                   /\\ UNCHANGED <<fence, held, compensationPrepared,
                                  commandSuccessObserved, eventReceiptObserved>>
ProviderFailureUnproven == /\\ held /\\ step = 1 /\\ ~providerNoEffect
                           /\\ phase \\in {"step-prepared", "suspended-unknown"}
                           /\\ revision < MaxRevision /\\ phase' = "needs-review"
                           /\\ held' = FALSE /\\ revision' = revision + 1
                           /\\ UNCHANGED <<step, fence, compensationPrepared,
                                          providerNoEffect, commandSuccessObserved,
                                          eventReceiptObserved>>
WaitEvent == /\\ held /\\ phase = "step-committed" /\\ step = EventStep - 1
             /\\ revision < MaxRevision /\\ phase' = "waiting-event"
             /\\ step' = EventStep /\\ revision' = revision + 1
             /\\ eventReceiptObserved' = FALSE
             /\\ UNCHANGED <<fence, held, compensationPrepared,
                            providerNoEffect, commandSuccessObserved>>
ObserveEventReceipt == /\\ held /\\ phase = "waiting-event"
                       /\\ ~eventReceiptObserved /\\ revision < MaxRevision
                       /\\ eventReceiptObserved' = TRUE
                       /\\ revision' = revision + 1
                       /\\ UNCHANGED <<phase, step, fence, held,
                                      compensationPrepared, providerNoEffect,
                                      commandSuccessObserved>>
CommitEvent == /\\ held /\\ phase = "waiting-event"
               /\\ eventReceiptObserved /\\ revision < MaxRevision
               /\\ phase' = "step-committed" /\\ revision' = revision + 1
               /\\ UNCHANGED <<step, fence, held, compensationPrepared,
                              providerNoEffect, commandSuccessObserved,
                              eventReceiptObserved>>
Complete == /\\ held /\\ phase = "step-committed" /\\ step = LastStep
            /\\ revision < MaxRevision /\\ phase' = "completed"
            /\\ held' = FALSE /\\ revision' = revision + 1
            /\\ UNCHANGED <<step, fence, compensationPrepared, providerNoEffect,
                           commandSuccessObserved, eventReceiptObserved>>
BeginCompensation == /\\ held /\\ phase = "step-committed" /\\ step = 0
                     /\\ revision < MaxRevision /\\ phase' = "compensating"
                     /\\ step' = CompensableStep
                     /\\ revision' = revision + 1
                     /\\ UNCHANGED <<fence, held, compensationPrepared,
                                    providerNoEffect, commandSuccessObserved,
                                    eventReceiptObserved>>
PrepareCompensation == /\\ held /\\ phase = "compensating"
                       /\\ step = CompensableStep /\\ ~compensationPrepared
                       /\\ revision < MaxRevision /\\ compensationPrepared' = TRUE
                       /\\ revision' = revision + 1
                       /\\ UNCHANGED <<phase, step, fence, held, providerNoEffect,
                                      commandSuccessObserved, eventReceiptObserved>>
CommitCompensation == /\\ held /\\ phase = "compensating"
                      /\\ step = CompensableStep /\\ compensationPrepared
                      /\\ revision < MaxRevision /\\ step' = -1
                      /\\ compensationPrepared' = FALSE /\\ revision' = revision + 1
                      /\\ UNCHANGED <<phase, fence, held, providerNoEffect,
                                     commandSuccessObserved, eventReceiptObserved>>
FinishCompensation == /\\ held /\\ phase = "compensating" /\\ step = -1
                      /\\ revision < MaxRevision /\\ phase' = "compensated"
                      /\\ held' = FALSE /\\ revision' = revision + 1
                      /\\ UNCHANGED <<step, fence, compensationPrepared,
                                     providerNoEffect, commandSuccessObserved,
                                     eventReceiptObserved>>
NeedsReview == /\\ held /\\ phase \\in Active /\\ phase # "scheduled"
               /\\ revision < MaxRevision /\\ phase' = "needs-review"
               /\\ held' = FALSE /\\ revision' = revision + 1
               /\\ UNCHANGED <<step, fence, compensationPrepared,
                              providerNoEffect, commandSuccessObserved,
                              eventReceiptObserved>>
Next == Claim \\/ Expire \\/ Renew \\/ PrepareStep \\/ ObserveCommandSuccess
        \\/ CommitStep
        \\/ SuspendUnknown \\/ ProveNoProviderEffect \\/ DefiniteFailure
        \\/ ProviderFailureUnproven \\/ WaitEvent \\/ ObserveEventReceipt
        \\/ CommitEvent
        \\/ Complete \\/ BeginCompensation \\/ PrepareCompensation
        \\/ CommitCompensation \\/ FinishCompensation \\/ NeedsReview
Spec == Init /\\ [][Next]_vars
TypeOK == /\\ phase \\in States /\\ step \\in -1..LastStep
          /\\ fence \\in 0..MaxFence /\\ revision \\in 0..MaxRevision
          /\\ held \\in BOOLEAN /\\ compensationPrepared \\in BOOLEAN
          /\\ providerNoEffect \\in BOOLEAN
          /\\ commandSuccessObserved \\in BOOLEAN
          /\\ eventReceiptObserved \\in BOOLEAN
CommittedHasObservation == (phase = "step-committed") =>
  (IF step = EventStep THEN eventReceiptObserved ELSE commandSuccessObserved)
TerminalStable == [][(phase \\in Terminal) => (phase' = phase)]_vars
FenceMonotonic == [][fence' >= fence]_vars
====
`;
}

export function exportGenericWorkflowTlaModel(owner:unknown,handle:GenericCompositionHandle):GenericWorkflowTlaModelV1 {
 const binding=requireGenericWorkflowRuntime(owner,handle),source=binding.contract,derivation=binding.derivation;
 binding.assertCurrent();
 if(source.schema_version!=='craft.generic-workflow-source/v1-candidate'||source.authority_effect!=='none'||
   source.recovery!=='needed-compensations-only/reverse-completion-v1'||!name.test(source.workflow.split('.').at(-1)??'')||
   !name.test(source.service)||source.steps.length!==3||source.steps[0]?.kind!=='local-command'||
   source.steps[1]?.kind!=='provider-command'||source.steps[2]?.kind!=='event-await'||
   source.compensation_order.length!==1||source.compensation_order[0]!==source.steps[0].name||
   !source.steps[0].compensation_entry||source.steps[1].on_unknown!=='resume-original-command'||
   source.steps[1].on_definite_failure!=='compensate'||source.steps[1].provider_failure_compensation_precondition!=='proven-no-provider-effect'||
   !source.steps[2].event_binding||!source.steps[2].event_binding_sha256||
   !hex.test(source.source_capture_sha256)||!hex.test(source.profile_sha256)||!hex.test(source.base_application_sha256)||
   derivation.source_capture_sha256!==source.source_capture_sha256||derivation.profile_sha256!==source.profile_sha256||
   derivation.base_application_sha256!==source.base_application_sha256||!hex.test(derivation.executable_semantics_sha256))reject('InvalidWorkflow');
 const workflow_contract_sha256=dataDigest(source),compatibility_sha256=workflowCompatibilitySha256(source);
 const tla=moduleText({source:source.source_capture_sha256,profile:source.profile_sha256,
  application:source.base_application_sha256,contract:workflow_contract_sha256,
  executable:derivation.executable_semantics_sha256,compatibility:compatibility_sha256});
 binding.assertCurrent();
 return Object.freeze({schema_version:'craft.generic-workflow-tla/v1-candidate',language:'tla+',
  scope:'one-checked-workflow-journal-instance',qualification:'bounded-control-abstraction-only',
  workflow:source.workflow,service:source.service,
  steps:source.steps.map(({name,kind})=>Object.freeze({name,kind:kind as 'local-command'|'provider-command'|'event-await'})),
  source_capture_sha256:source.source_capture_sha256,profile_sha256:source.profile_sha256,
  base_application_sha256:source.base_application_sha256,workflow_contract_sha256,
  executable_semantics_sha256:derivation.executable_semantics_sha256,compatibility_sha256,
  max_fence:3,max_revision:24,tla,tla_sha256:sha(tla),authority_effect:'none',
  claim_ceiling:'one-instance-journal-control-with-abstract-provider-no-effect-evidence-no-auth-provider-event-sqlite-time-or-model-checker-proof'});
}

export function assertGenericWorkflowTlaCurrent(owner:unknown,handle:GenericCompositionHandle,model:GenericWorkflowTlaModelV1):void {
 const current=exportGenericWorkflowTlaModel(owner,handle);
 if(!model||dataDigest(model)!==dataDigest(current))reject('InvalidModel');
}
