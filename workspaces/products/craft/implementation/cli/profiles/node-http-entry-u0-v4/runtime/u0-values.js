import { types } from 'node:util';
const part = (value) => value.length + ':' + value;
const uint64Value = Object.freeze({
    normalize: (input) => {
        let value;
        if (typeof input === 'bigint')
            value = input;
        else if (typeof input === 'number' && Number.isSafeInteger(input))
            value = BigInt(input);
        else if (typeof input === 'string' && input.length <= 20 && /^(0|[1-9][0-9]*)$/.exec(input)?.[0] === input)
            value = BigInt(input);
        else
            throw new TypeError('INVALID_UINT64');
        if (value < 0n || value > 18446744073709551615n)
            throw new TypeError('INVALID_UINT64');
        return value;
    },
    key: (value) => part('UInt64') + part(String(value)),
});
export class U0ValueError extends TypeError {
    code;
    constructor(code) {
        super(code);
        this.code = code;
        this.name = 'U0ValueError';
    }
}
function fail(code) { throw new U0ValueError(code); }
function fields(input) {
    if (!input || typeof input !== 'object' || types.isProxy(input) || Array.isArray(input))
        fail('U0_VALUE_SHAPE');
    const prototype = Object.getPrototypeOf(input);
    if (prototype !== null && prototype !== Object.prototype)
        fail('U0_VALUE_SHAPE');
    const keys = Reflect.ownKeys(input);
    if (keys.length !== 2 || !keys.includes('id') || !keys.includes('verified'))
        fail('U0_VALUE_SHAPE');
    const descriptors = Object.getOwnPropertyDescriptors(input);
    const id = descriptors.id, verified = descriptors.verified;
    if (!id || !verified || !Object.hasOwn(id, 'value') || !Object.hasOwn(verified, 'value') || !id.enumerable || !verified.enumerable || typeof verified.value !== 'boolean')
        fail('U0_VALUE_SHAPE');
    return { id: id.value, verified: verified.value };
}
function owned(id, verified) {
    return Object.freeze(Object.assign(Object.create(null), { id, verified }));
}
/** No Number conversion; the finite canonical range is checked before BigInt. */
export function formU0Submission(record) {
    const value = fields(record), decimal = value.id;
    if (typeof decimal !== 'string' || decimal.length === 0 || decimal.length > 20)
        fail('U0_VALUE_DECIMAL');
    if (decimal === '0')
        return owned(uint64Value.normalize(decimal), value.verified);
    if (decimal.charCodeAt(0) < 49 || decimal.charCodeAt(0) > 57)
        fail('U0_VALUE_DECIMAL');
    for (let i = 1; i < decimal.length; i++)
        if (decimal.charCodeAt(i) < 48 || decimal.charCodeAt(i) > 57)
            fail('U0_VALUE_DECIMAL');
    if (decimal.length === 20 && decimal > '18446744073709551615')
        fail('U0_VALUE_RANGE');
    return owned(uint64Value.normalize(decimal), value.verified);
}
/** The pure native ABI is bigint + Boolean, even when the shared helper is wider. */
export function copyU0Submission(input) {
    const value = fields(input);
    if (typeof value.id !== 'bigint')
        fail('U0_VALUE_NATIVE');
    if (value.id < 0n || value.id > 18446744073709551615n)
        fail('U0_VALUE_RANGE');
    return owned(uint64Value.normalize(value.id), value.verified);
}
