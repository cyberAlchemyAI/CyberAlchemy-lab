// Explicit json-safe-uint64/v1-candidate support; not full-width UInt64.
// Contract and verification: NUMERIC-RULES.md in the PCR reconciliation package.
export const NUMERIC_RULE_VALUE_PROFILE = 'json-safe-uint64/v1-candidate';
export const numericRuleSupport = `type RuleScalar = string|boolean|number;
const normalizeRuleUInt64 = (input:unknown):number=>{
  if(typeof input!=='number'||!Number.isSafeInteger(input)||input<0) throw new TypeError('RULE_INPUT');
  return input===0?0:input;
};
const normalizeRuleCollection = <T extends RuleScalar>(input:unknown,element:'string'|'boolean'|'number',unique:boolean):readonly T[]=>{
  if(!Array.isArray(input)||Object.getPrototypeOf(input)!==Array.prototype) throw new TypeError('RULE_INPUT');
  const descriptors:Record<string,PropertyDescriptor>=Object.getOwnPropertyDescriptors(input),length=descriptors.length?.value;
  if(!Number.isSafeInteger(length)||length<0||Reflect.ownKeys(descriptors).length!==length+1) throw new TypeError('RULE_INPUT');
  const values:T[]=[];
  for(let i=0;i<length;i++){const d=descriptors[String(i)];if(!d||!Object.hasOwn(d,'value')||!d.enumerable||typeof d.value!==element) throw new TypeError('RULE_INPUT');values.push((element==='number'?normalizeRuleUInt64(d.value):d.value) as T);}
  if(unique){if(new Set(values).size!==values.length) throw new TypeError('RULE_INPUT');values.sort((a,b)=>{if(typeof a==='number'&&typeof b==='number')return a-b;const ka=typeof a==='string'?'S'+a:a?'B1':'B0',kb=typeof b==='string'?'S'+b:b?'B1':'B0';return ka<kb?-1:ka>kb?1:0;});}
  return Object.freeze(values);
};
`;
