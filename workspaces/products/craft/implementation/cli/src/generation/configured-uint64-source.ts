// Opt-in json-safe-uint64/v1-candidate realization, not full-width UInt64.
// Scope/open questions: UINT64-FIELD-FACTORY-GENERATION.md.
export function renderUInt64Support():string {
  return `const uint64Value:ValueProtocol<number> = Object.freeze({
  normalize:(input:unknown):number=>{
    if(typeof input !== 'number' || !Number.isSafeInteger(input) || input < 0) throw new TypeError('INVALID_UINT64');
    return input === 0 ? 0 : input;
  },
  key:(value:number):string=>part('UInt64') + part(String(value)),
});
`;
}
