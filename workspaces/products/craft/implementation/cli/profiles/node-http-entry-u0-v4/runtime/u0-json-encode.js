import { types } from 'node:util';
import { constants as bufferConstants } from 'node:buffer';
import { copyU0Submission } from './u0-values.js';
/** Fixed canonical ASCII wire schema; no JSON.stringify of caller objects.
 * Open Questions: U07 handler and J01 actual native registration/capture. */
export const U0_ADAPTER_ERROR_CODES = Object.freeze([
    'route-not-found', 'method-not-allowed', 'unsupported-media-type', 'request-aborted',
    'request-too-large', 'body-timeout', 'body-read-failed', 'invalid-request', 'adapter-contract-defect',
]);
export class U0JsonEncodeError extends TypeError {
    code;
    constructor(code) {
        super(code);
        this.code = code;
        this.name = 'U0JsonEncodeError';
    }
}
function fail(code) { throw new U0JsonEncodeError(code); }
function record(input, keys) {
    if (!input || typeof input !== 'object' || types.isProxy(input) || Array.isArray(input))
        fail('U0_ENCODE_SHAPE');
    const prototype = Object.getPrototypeOf(input);
    if (prototype !== null && prototype !== Object.prototype)
        fail('U0_ENCODE_SHAPE');
    const names = Reflect.ownKeys(input);
    if (names.length !== keys.length || names.some(k => typeof k !== 'string' || !keys.includes(k)))
        fail('U0_ENCODE_SHAPE');
    const descriptors = Object.getOwnPropertyDescriptors(input), out = Object.create(null);
    for (const key of keys) {
        const d = descriptors[key];
        if (!d || !d.enumerable || !Object.hasOwn(d, 'value'))
            fail('U0_ENCODE_SHAPE');
        out[key] = d.value;
    }
    return out;
}
function domainLiteral(input) {
    const code = record(input, ['rejection_code']).rejection_code;
    if (typeof code !== 'string' || code.length === 0 || code.length > 8192)
        fail('U0_ENCODE_DOMAIN');
    const out = ['"'];
    let scalars = 0;
    const escape = (unit) => '\\u' + unit.toString(16).padStart(4, '0');
    for (let i = 0; i < code.length; i++) {
        if (++scalars > 4096)
            fail('U0_ENCODE_DOMAIN');
        const unit = code.charCodeAt(i);
        if (unit >= 0xd800 && unit <= 0xdbff) {
            const low = code.charCodeAt(++i);
            if (!(low >= 0xdc00 && low <= 0xdfff))
                fail('U0_ENCODE_DOMAIN');
            out.push(escape(unit), escape(low));
        }
        else if (unit >= 0xdc00 && unit <= 0xdfff)
            fail('U0_ENCODE_DOMAIN');
        else if (unit === 34)
            out.push('\\"');
        else if (unit === 92)
            out.push('\\\\');
        else if (unit === 8)
            out.push('\\b');
        else if (unit === 12)
            out.push('\\f');
        else if (unit === 10)
            out.push('\\n');
        else if (unit === 13)
            out.push('\\r');
        else if (unit === 9)
            out.push('\\t');
        else if (unit < 32 || unit > 126)
            out.push(escape(unit));
        else
            out.push(String.fromCharCode(unit));
    }
    out.push('"');
    return out.join('');
}
const requestPrefix = '{"id":"', requestMiddle = '","verified":', requestSuffix = '}';
const completedPrefix = '{"kind":"completed","value":';
const rejectedPrefix = '{"kind":"rejected","code":';
const errorPrefix = '{"kind":"adapter-error","code":"';
const bytes = (text) => new TextEncoder().encode(text);
function requestText(input) {
    const value = copyU0Submission(input);
    return requestPrefix + String(value.id) + requestMiddle + (value.verified ? 'true' : 'false') + requestSuffix;
}
export function encodeU0Request(value) { return bytes(requestText(value)); }
export function encodeU0Outcome(value, domain) {
    const literal = domainLiteral(domain);
    // Inspect kind without property access on an unchecked object.
    if (!value || typeof value !== 'object' || types.isProxy(value))
        fail('U0_ENCODE_OUTCOME');
    const kind = Object.getOwnPropertyDescriptor(value, 'kind');
    if (!kind || !Object.hasOwn(kind, 'value'))
        fail('U0_ENCODE_OUTCOME');
    if (kind.value === 'completed') {
        const completed = copyU0Submission(record(value, ['kind', 'value']).value);
        // U0's guard is the direct verified projection; false has only rejection.
        if (!completed.verified)
            fail('U0_ENCODE_OUTCOME');
        return bytes(completedPrefix + requestText(completed) + '}');
    }
    if (kind.value === 'rejected') {
        const data = record(value, ['kind', 'code']);
        if (data.code !== record(domain, ['rejection_code']).rejection_code)
            fail('U0_ENCODE_OUTCOME');
        return bytes(rejectedPrefix + literal + '}');
    }
    return fail('U0_ENCODE_OUTCOME');
}
export function encodeU0AdapterError(code) {
    if (typeof code !== 'string' || !U0_ADAPTER_ERROR_CODES.includes(code))
        fail('U0_ENCODE_OUTCOME');
    return bytes(errorPrefix + code + '"}');
}
/** These maxima follow fixed punctuation and scalar/code domains, not samples. */
export function u0WireBounds(domain) {
    const request = requestPrefix.length + 20 + requestMiddle.length + 'false'.length + requestSuffix.length;
    const completed = completedPrefix.length + requestPrefix.length + 20 + requestMiddle.length + 'true'.length + requestSuffix.length + 1;
    const rejected = rejectedPrefix.length + domainLiteral(domain).length + 1;
    const adapter_error = errorPrefix.length + Math.max(...U0_ADAPTER_ERROR_CODES.map(code => code.length)) + 2;
    return Object.freeze({ request, completed, rejected, adapter_error });
}
export function checkU0EncoderConfiguration(input, domain) {
    const keys = ['schema_version', 'method', 'pathname', 'body', 'uint64_codec', 'request_bytes', 'response_bytes', 'body_timeout_ms'];
    const value = record(input, keys);
    if (value.schema_version !== 'craft.operation-json-post/v2-candidate' || value.method !== 'POST' || value.pathname !== '/confirm-delivery' || value.body !== 'closed-submission' || value.uint64_codec !== 'canonical-decimal-string')
        fail('U0_ENCODE_CONFIGURATION');
    const limit = Math.min(bufferConstants.MAX_LENGTH, 2147483647);
    for (const key of ['request_bytes', 'response_bytes', 'body_timeout_ms']) {
        const n = value[key];
        if (typeof n !== 'number' || !Number.isSafeInteger(n) || n < 1 || n > (key === 'body_timeout_ms' ? 2147483647 : limit))
            fail('U0_ENCODE_CONFIGURATION');
    }
    const bounds = u0WireBounds(domain);
    if (value.request_bytes < bounds.request || value.response_bytes < Math.max(bounds.completed, bounds.rejected, bounds.adapter_error))
        fail('U0_ENCODE_COVERAGE');
    return Object.freeze(value);
}
