/** Internal C11 DemoPay-v1 wire adapter. The generated original owner must bind
 * current source/Auth and an owned raw HTTP port; this module grants neither.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import { createHash } from 'node:crypto';
import { parseCoreCommerceJson } from '../commerce/commerce-core-source-owner.js';
import type { DispatchCustody, EffectInput, EffectRow } from './durable-write-intent-store.js';

const decoder = new TextDecoder('utf-8', { fatal: true, ignoreBOM: true });
const hex = /^[0-9a-f]{64}$/;
const uint64 = /^(0|[1-9][0-9]{0,19})$/;
const identifier = (value: unknown): value is string => typeof value === 'string' &&
  value.length > 0 && value.length <= 128 && Buffer.byteLength(value, 'utf8') <= 128 &&
  !/[\uD800-\uDBFF](?![\uDC00-\uDFFF])|(?<![\uD800-\uDBFF])[\uDC00-\uDFFF]/u.test(value);
const closed = (value: unknown, keys: readonly string[]): value is Record<string, unknown> =>
  !!value && typeof value === 'object' && !Array.isArray(value) &&
  Object.keys(value).length === keys.length && keys.every(key => Object.hasOwn(value, key));
const parse = (bytes: Uint8Array, maximum: number): unknown => {
  if (!(bytes instanceof Uint8Array) || bytes.byteLength > maximum) throw new Error('C11_WIRE_BOUND');
  return parseCoreCommerceJson(decoder.decode(bytes), 'C11 DemoPay wire');
};

export type DemoPayCaptureRequest = Readonly<{
  attemptKey: string; orderId: string; amountMinor: string; currency: 'USD';
}>;
export type DemoPayCaptureResult = DemoPayCaptureRequest & Readonly<{
  status: 'Captured' | 'DefinitivelyDeclined' | 'Pending' | 'Unknown' | 'UnknownKey';
  providerReference: string | null;
}>;
export type DemoPayWireRequest = Readonly<{
  origin: 'https://demopay.invalid'; method: 'POST'; path: '/v1/capture' | '/v1/capture/inspect';
  headers: Readonly<Record<'content-type' | 'demopay-protocol', string>>;
  body: Uint8Array; signal: AbortSignal;
}>;
export type DemoPayWireResponse = Readonly<{
  status: number; headers: Readonly<Record<string, string>>; body: Uint8Array;
}>;
/** Raw bytes only. An owning runtime supplies this port; no global fetch fallback. */
export interface DemoPayRawHttpPort {
  exchange(request: DemoPayWireRequest): Promise<DemoPayWireResponse>;
}
/** The generated owner supplies this narrow, READY-bound view of its store. */
export interface DemoPayIntentStorePort {
  assertDispatchCurrent(custody: DispatchCustody, input: EffectInput): void;
  inspect(input: EffectInput): EffectRow | null;
}
export type DemoPayNativeOutcome = Readonly<
  | { kind: 'observed'; result: DemoPayCaptureResult; matches_request: boolean;
      checked: CheckedDemoPayObservation | null }
  | { kind: 'unknown'; reason: 'timeout' | 'transport' | 'unavailable' | 'malformed' | 'pending' | 'unknown-key' | 'provider-unknown' | 'invalid-request' }
  | { kind: 'conflict'; reason: 'attempt-key-conflict' }
>;
/** Opaque, instance-local evidence of exact native wire identity. Source rule
 * admission and current Auth remain separate original-owner obligations. */
export interface CheckedDemoPayObservation {
  readonly kind: 'private-c11-demopay-observation/v1-candidate';
}
const checkedObservations = new WeakMap<object, Readonly<{
  effect_sha256: string; payload_sha256: string; binding_sha256: string; request_sha256: string;
  kind: 'Captured' | 'DefinitivelyDeclined'; providerReference: string;
}>>();
const invokedCustodies = new WeakSet<object>();
const digest = (bytes: Uint8Array): string => createHash('sha256').update(bytes).digest('hex');
export function readCheckedDemoPayObservation(handle: CheckedDemoPayObservation,
  input: EffectInput): Readonly<{ effect_sha256: string; request_sha256: string;
  kind: 'Captured' | 'DefinitivelyDeclined'; providerReference: string }> {
  const found = handle && typeof handle === 'object' ? checkedObservations.get(handle) : undefined;
  if (!found || found.effect_sha256 !== input.effect_sha256 ||
    found.payload_sha256 !== input.payload_sha256 || found.binding_sha256 !== input.binding_sha256 ||
    found.request_sha256 !== digest(input.request_bytes)) throw new Error('C11_FOREIGN_NATIVE_OBSERVATION');
  return Object.freeze({ effect_sha256: found.effect_sha256, request_sha256: found.request_sha256,
    kind: found.kind, providerReference: found.providerReference });
}

export function demoPayAttemptKey(effectSha256: string): string {
  if (!hex.test(effectSha256)) throw new Error('C11_EFFECT_IDENTITY');
  return `c11-${effectSha256}`;
}
export function buildDemoPayCaptureRequest(effectSha256: string, orderId: string,
  amountMinor: string, currency: 'USD'): Uint8Array {
  if (!identifier(orderId) || !uint64.test(amountMinor) || BigInt(amountMinor) > 18446744073709551615n ||
    currency !== 'USD') throw new Error('C11_CAPTURE_REQUEST_INVALID');
  const body = Buffer.from(JSON.stringify({ attemptKey: demoPayAttemptKey(effectSha256), orderId,
    amountMinor, currency }), 'utf8');
  if (body.byteLength > 4096) throw new Error('C11_CAPTURE_REQUEST_BOUND');
  return body;
}
function originalRequest(input: EffectInput): DemoPayCaptureRequest {
  const value = parse(input.request_bytes, 4096);
  if (!closed(value, ['attemptKey', 'orderId', 'amountMinor', 'currency']) ||
    value.attemptKey !== demoPayAttemptKey(input.effect_sha256) || !identifier(value.orderId) ||
    typeof value.amountMinor !== 'string' || !uint64.test(value.amountMinor) ||
    BigInt(value.amountMinor) > 18446744073709551615n || value.currency !== 'USD' ||
    !Buffer.from(input.request_bytes).equals(buildDemoPayCaptureRequest(input.effect_sha256,
      value.orderId, value.amountMinor, 'USD'))) throw new Error('C11_CAPTURE_REQUEST_IDENTITY');
  return value as DemoPayCaptureRequest;
}
function resultOf(value: unknown): DemoPayCaptureResult {
  if (!closed(value, ['attemptKey', 'orderId', 'amountMinor', 'currency', 'status', 'providerReference']) ||
    !identifier(value.attemptKey) || !identifier(value.orderId) ||
    typeof value.amountMinor !== 'string' || !uint64.test(value.amountMinor) ||
    BigInt(value.amountMinor) > 18446744073709551615n || value.currency !== 'USD' ||
    !['Captured', 'DefinitivelyDeclined', 'Pending', 'Unknown', 'UnknownKey'].includes(value.status as string) ||
    (['Captured', 'DefinitivelyDeclined'].includes(value.status as string)
      ? !identifier(value.providerReference) : value.providerReference !== null))
    throw new Error('C11_CAPTURE_RESULT_INVALID');
  return value as DemoPayCaptureResult;
}
const exactHeaders = (headers: Readonly<Record<string, string>>): boolean =>
  headers['content-type'] === 'application/json; charset=utf-8' && headers['demopay-protocol'] === '1';
const errorBody = (value: unknown, code: string): boolean => closed(value, ['kind', 'code']) &&
  value.kind === 'error' && value.code === code;

/** A definite provider status remains wire-observed data until the source
 * MatchesCaptureRequest rule and original owner admit the business transition. */
export function createDemoPayNativeWriteAdapter(selection: Readonly<{ protocol_id: string }>,
  port: DemoPayRawHttpPort, deadlineMs = 5000): Readonly<{
    capture(store: DemoPayIntentStorePort, custody: DispatchCustody, input: EffectInput): Promise<DemoPayNativeOutcome>;
    inspect(store: DemoPayIntentStorePort, input: EffectInput): Promise<DemoPayNativeOutcome>;
  }> {
  if (selection.protocol_id !== 'DemoPay-v1' || !port || typeof port.exchange !== 'function' ||
    !Number.isSafeInteger(deadlineMs) || deadlineMs < 1 || deadlineMs > 30000)
    throw new Error('C11_NATIVE_PROFILE_UNSUPPORTED');
  async function invoke(path: DemoPayWireRequest['path'], input: EffectInput): Promise<DemoPayNativeOutcome> {
    const original = originalRequest(input);
    const controller = new AbortController();
    let timer: ReturnType<typeof setTimeout> | undefined;
    const request: DemoPayWireRequest = Object.freeze({ origin: 'https://demopay.invalid', method: 'POST', path,
      headers: Object.freeze({ 'content-type': 'application/json; charset=utf-8', 'demopay-protocol': '1' }),
      body: Buffer.from(input.request_bytes), signal: controller.signal });
    let response: DemoPayWireResponse;
    try {
      response = await Promise.race([
        port.exchange(request),
        new Promise<never>((_, reject) => { timer = setTimeout(() => {
          controller.abort(); reject(new Error('C11_NATIVE_TIMEOUT'));
        }, deadlineMs); }),
      ]);
    } catch (error) {
      return { kind: 'unknown', reason: error instanceof Error && error.message === 'C11_NATIVE_TIMEOUT'
        ? 'timeout' : 'transport' };
    } finally { if (timer) clearTimeout(timer); }
    if (!response || !Number.isInteger(response.status) || !response.headers ||
      !(response.body instanceof Uint8Array) || response.body.byteLength > 8192 ||
      !exactHeaders(response.headers)) return { kind: 'unknown', reason: 'malformed' };
    if (response.status === 503) return { kind: 'unknown', reason: 'unavailable' };
    let body: unknown;
    try { body = parse(response.body, 8192); }
    catch { return { kind: 'unknown', reason: 'malformed' }; }
    if (response.status === 409 && errorBody(body, 'attempt-key-conflict'))
      return { kind: 'conflict', reason: 'attempt-key-conflict' };
    if (response.status === 400 && errorBody(body, 'invalid-request'))
      return { kind: 'unknown', reason: 'invalid-request' };
    if (response.status !== 200 && !(path === '/v1/capture/inspect' && response.status === 404))
      return { kind: 'unknown', reason: 'malformed' };
    let result: DemoPayCaptureResult;
    try { result = resultOf(body); } catch { return { kind: 'unknown', reason: 'malformed' }; }
    if (response.status === 404 && result.status !== 'UnknownKey' ||
      response.status === 200 && result.status === 'UnknownKey')
      return { kind: 'unknown', reason: 'malformed' };
    const matches = result.attemptKey === original.attemptKey && result.orderId === original.orderId &&
      result.amountMinor === original.amountMinor && result.currency === original.currency;
    if (result.status === 'UnknownKey') return { kind: 'unknown', reason: matches ? 'unknown-key' : 'malformed' };
    if (result.status === 'Pending') return { kind: 'unknown', reason: 'pending' };
    if (result.status === 'Unknown') return { kind: 'unknown', reason: 'provider-unknown' };
    let checked: CheckedDemoPayObservation | null = null;
    if (matches && (result.status === 'Captured' || result.status === 'DefinitivelyDeclined')) {
      checked = Object.freeze({ kind: 'private-c11-demopay-observation/v1-candidate' as const });
      checkedObservations.set(checked, Object.freeze({ effect_sha256: input.effect_sha256,
        payload_sha256: input.payload_sha256, binding_sha256: input.binding_sha256,
        request_sha256: digest(input.request_bytes), kind: result.status,
        providerReference: result.providerReference! }));
    }
    return { kind: 'observed', result, matches_request: matches, checked };
  }
  return Object.freeze({
    capture(store: DemoPayIntentStorePort, custody: DispatchCustody, input: EffectInput) {
      store.assertDispatchCurrent(custody, input);
      if (invokedCustodies.has(custody)) throw new Error('C11_CAPTURE_ALREADY_SENT_INSPECT_REQUIRED');
      invokedCustodies.add(custody);
      return invoke('/v1/capture', input);
    },
    inspect(store: DemoPayIntentStorePort, input: EffectInput) {
      if (!store.inspect(input)) throw new Error('C11_INTENT_MISSING');
      return invoke('/v1/capture/inspect', input);
    },
  });
}
