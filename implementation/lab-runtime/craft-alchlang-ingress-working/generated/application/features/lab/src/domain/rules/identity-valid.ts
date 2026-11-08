// structured-rule-capability:base
type RuleProtocol<T> = Readonly<{normalize:(input:unknown)=>T;key:(value:T)=>string}>;
const rulePart = (value:string):string=>value.length+':'+value;
const ruleData = (input:unknown,allowed:readonly string[]):Record<string,PropertyDescriptor>=>{
  if(input===null||typeof input!=='object'||Array.isArray(input)||![Object.prototype,null].includes(Object.getPrototypeOf(input))) throw new TypeError('RULE_INPUT');
  const descriptors=Object.getOwnPropertyDescriptors(input);
  if(Reflect.ownKeys(descriptors).some(key=>typeof key!=='string'||!allowed.includes(key))||Object.values(descriptors).some(d=>!Object.hasOwn(d,'value')||!d.enumerable)) throw new TypeError('RULE_INPUT');
  return descriptors;
};
// structured-rule-capability:UInt64
const ruleUInt64:RuleProtocol<bigint> = Object.freeze({
  normalize:(input:unknown):bigint=>{
    let value:bigint;
    if(typeof input==='bigint')value=input;
    else if(typeof input==='number'&&Number.isSafeInteger(input))value=BigInt(input);
    else if(typeof input==='string'&&input.length<=20&&/^(0|[1-9][0-9]*)$/.exec(input)?.[0]===input)value=BigInt(input);
    else throw new TypeError('RULE_INPUT');
    if(value<0n||value>18446744073709551615n)throw new TypeError('RULE_INPUT');
    return value;
  },key:(value:bigint):string=>rulePart('UInt64')+rulePart(String(value)),
});
// end structured Rule support
// domainspec-rule: "lab:identity-valid"; closure: 9f1bb34aa63f7f1d795ac00371cd83077a8d4149557d232cc9f00e5a4750d6bc
export const ruleIdentityValid = (parameters:Readonly<{readonly "identity":bigint|number|string}>):boolean => {
  const d=ruleData(parameters,["identity"]);
  if(Object.keys(d).length!==1)throw new TypeError('RULE_INPUT');
  const p0 = ruleUInt64.normalize(d["identity"]!.value);
  return (ruleUInt64.key(p0) === ruleUInt64.key(p0));
};
