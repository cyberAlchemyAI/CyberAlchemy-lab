// Exact input realization; source literals keep their checked typed-contract bounds.
// Contract and verification: EXACT-NUMERIC-RULES.md in the PCR package.
export const exactRuleSupport = `type RuleScalar = string|boolean|bigint;
type RuleUInt64Input = bigint|number|string;
const normalizeRuleUInt64 = (input:unknown):bigint=>{
  let result:bigint;
  if(typeof input==='bigint') result=input;
  else if(typeof input==='number'&&Number.isSafeInteger(input)) result=BigInt(input);
  else if(typeof input==='string'&&input.length<=20&&/^(0|[1-9][0-9]*)$/.exec(input)?.[0]===input) result=BigInt(input);
  else throw new TypeError('RULE_INPUT');
  if(result<0n||result>18446744073709551615n) throw new TypeError('RULE_INPUT');
  return result;
};
const normalizeRuleCollection = <T extends RuleScalar>(input:unknown,element:'string'|'boolean'|'bigint',unique:boolean):readonly T[]=>{
  if(!Array.isArray(input)||Object.getPrototypeOf(input)!==Array.prototype) throw new TypeError('RULE_INPUT');
  const descriptors:Record<string,PropertyDescriptor>=Object.getOwnPropertyDescriptors(input),length=descriptors.length?.value;
  if(!Number.isSafeInteger(length)||length<0||Reflect.ownKeys(descriptors).length!==length+1) throw new TypeError('RULE_INPUT');
  const values:T[]=[];
  for(let i=0;i<length;i++){const d=descriptors[String(i)];if(!d||!Object.hasOwn(d,'value')||!d.enumerable||(element!=='bigint'&&typeof d.value!==element)) throw new TypeError('RULE_INPUT');values.push((element==='bigint'?normalizeRuleUInt64(d.value):d.value) as T);}
  if(unique){if(new Set(values).size!==values.length) throw new TypeError('RULE_INPUT');values.sort((a,b)=>{if(typeof a==='bigint'&&typeof b==='bigint')return a<b?-1:a>b?1:0;const ka=typeof a==='string'?'S'+a:a?'B1':'B0',kb=typeof b==='string'?'S'+b:b?'B1':'B0';return ka<kb?-1:ka>kb?1:0;});}
  return Object.freeze(values);
};
`;
