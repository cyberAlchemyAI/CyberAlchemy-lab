// ISB-02 candidate dependency signatures, not runtime implementations.
// Canonical basis: domainspec-v2-D45. Semantics and Open Questions: README.md.
export type Json = null | boolean | number | string | readonly Json[] | {readonly [key: string]: Json};
export interface InvocationControl {
  /** Absolute monotonic deadline, in the same host clock domain; not wall time. */
  readonly deadline: number;
  readonly signal: AbortSignal;
}
export interface BindingIdentity {
  readonly id: string;
  readonly version: string;
}
export interface AttemptIdentity extends BindingIdentity {
  readonly model: string;
  readonly policyVersion: string;
}
export interface HttpExchange {
  readonly status: number;
  readonly mediaType: string;
  readonly body: AsyncIterable<Uint8Array>;
}
export interface HttpAttempt {
  /** May reject on deadline while settled remains pending. */
  readonly response: Promise<HttpExchange>;
  /** Resolves only when actual transport resource custody ends. */
  readonly settled: Promise<void>;
  cancel(reason: 'cancelled' | 'deadline' | 'invalid-response'): Promise<void>;
}
export interface HttpInvocation {
  /** Operator configuration resolves URL and secrets; one call, no redirects/retry. */
  sendOnce(binding: BindingIdentity, body: Json, control: InvocationControl): HttpAttempt;
}
export interface StreamIdentity {readonly requestId: string; readonly model: string}
export interface CountObservation {
  readonly value: number | null;
  readonly provenance: 'provider-reported' | 'locally-estimated' | 'unavailable';
  readonly estimatorVersion?: string;
}
export interface Usage {readonly inputTokens: CountObservation; readonly outputTokens: CountObservation}
export interface Completion {readonly finishReason: string; readonly usage: Usage}
export interface PublicFailure {readonly code: string; readonly requestId?: string}
export interface ResponseStream {
  /** Each call awaits downstream capacity; runtime enforces stream-state.json. */
  start(identity: StreamIdentity): Promise<void>;
  delta(text: string): Promise<void>;
  complete(completion: Completion): Promise<void>;
  fail(error: PublicFailure): Promise<void>;
  cancel(): Promise<void>;
}
// ISB-07: import executable candidate custody signatures instead of duplicating them.
export type {ExecutionToken,ReservationRequest,Reservation,LocalOutcome,RequestInspection,RequestCustody} from '../../../../../../../../craft/projects/domainspec-v2/impl/cli/src/runtime/request-custody.js';
