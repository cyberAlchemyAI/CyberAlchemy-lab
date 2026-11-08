// Explicit exact-uint64 field realization. Scope: EXACT-FACTORY-GENERATION.md.
// Keep the existing JSON-safe helper unchanged.
export function renderExactUInt64Support(): string {
  return `const uint64Value:ValueProtocol<bigint> = Object.freeze({
  normalize:(input:unknown):bigint=>{
    let value:bigint;
    if(typeof input === 'bigint') value=input;
    else if(typeof input === 'number' && Number.isSafeInteger(input)) value=BigInt(input);
    else if(typeof input === 'string' && input.length <= 20 && /^(0|[1-9][0-9]*)$/.exec(input)?.[0] === input) value=BigInt(input);
    else throw new TypeError('INVALID_UINT64');
    if(value < 0n || value > 18446744073709551615n) throw new TypeError('INVALID_UINT64');
    return value;
  },
  key:(value:bigint):string=>part('UInt64') + part(String(value)),
});
`;
}
