// Compile-only witnesses. No implementation or I/O. Open Questions: README.md.
import type {HttpInvocation, HttpExchange, HttpAttempt, RequestCustody, ExecutionToken} from './dependencies.js';
declare const response: Promise<HttpExchange>;
declare const settled: Promise<void>;
declare const cancel: HttpAttempt['cancel'];
const valid: HttpInvocation = {sendOnce: () => ({response, settled, cancel})};
// A response promise alone loses settlement visibility after an ambiguous deadline.
// @ts-expect-error HttpAttempt must expose a settlement handle immediately.
const invalid: HttpInvocation = {sendOnce: () => response};
declare const custody: RequestCustody;
// @ts-expect-error public strings cannot impersonate an execution token.
custody.markTransportSettled('caller-controlled');
declare const token: ExecutionToken;
custody.markTransportSettled(token);
void valid; void invalid;
