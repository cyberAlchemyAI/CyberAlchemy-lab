/**
 * Structural ports consumed by AlchLang integration adapters.
 *
 * DomainSpec owns the runtime implementations. Keeping the consumed shapes here
 * prevents emitted declarations from importing a repository checkout while
 * preserving ordinary TypeScript structural compatibility with the installed
 * `@domainspec-v2/cli` runtime objects.
 */
export type InvocationJson = null | boolean | number | string | readonly InvocationJson[] | { readonly [key: string]: InvocationJson };
export interface InvocationControl { readonly deadline: number; readonly signal: AbortSignal }
export interface BindingIdentity { readonly id: string; readonly version: string; readonly model: string }
export interface HttpExchange { readonly status: number; readonly mediaType: string; readonly body: AsyncIterable<Uint8Array> }
export interface HttpAttempt {
  readonly response: Promise<HttpExchange>;
  readonly settled: Promise<void>;
  cancel(reason: "cancelled" | "deadline" | "invalid-response"): Promise<void>;
}
export interface HttpInvocation { sendOnce(binding: BindingIdentity, body: InvocationJson, control: InvocationControl): HttpAttempt }

declare const executionToken: unique symbol;
export type ExecutionToken = string & { readonly [executionToken]: true };
export interface AttemptIdentity { readonly id: string; readonly version: string; readonly model: string; readonly policyVersion: string }
export interface ReservationRequest { readonly scope: string; readonly key: string | null; readonly requestId: string; readonly fingerprintVersion: string; readonly fingerprint: string; readonly stream: boolean }
export type LocalOutcome =
  | { kind: "json-completed"; result: InvocationJson; usage: InvocationJson }
  | { kind: "stream-completed"; usage: InvocationJson }
  | { kind: "failed" | "cancelled"; code: string };
export type Reservation =
  | { kind: "execute"; requestId: string; token: ExecutionToken }
  | { kind: "replay"; requestId: string; result: InvocationJson }
  | { kind: "reject"; requestId?: string; code: string };
export interface RequestInspection { requestId: string; attempt: AttemptIdentity | null; outcome: LocalOutcome["kind"] | null; transportSettled: boolean; remoteCompletion: "unknown" | "reported-complete"; usage: InvocationJson | null }
export interface RequestCustody {
  reserve(request: ReservationRequest, control: InvocationControl): Promise<Reservation>;
  beginAttempt(token: ExecutionToken, binding: AttemptIdentity): Promise<void>;
  recordOutcome(token: ExecutionToken, outcome: LocalOutcome): Promise<void>;
  markTransportSettled(token: ExecutionToken): Promise<void>;
  inspect(requestId: string): Promise<RequestInspection | null>;
}

export interface StreamFrameSink {
  write(event: string, value: unknown, signal?: AbortSignal, accepted?: () => void): Promise<void>;
  close(): void;
  error(reason: unknown): void;
}
