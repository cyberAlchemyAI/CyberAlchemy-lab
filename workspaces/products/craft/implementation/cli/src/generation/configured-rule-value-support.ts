// Static typed Rule combinators; no expression/type-schema interpreter.
// Support is emitted by observed capability so generated modules do not carry
// helpers that their specialized value program cannot call.
export type StructuredRuleCapability = "String" | "Bool" | "UInt64" | "optional" | "sequence" | "to-set" | "sum";

const BASE = `type RuleProtocol<T> = Readonly<{normalize:(input:unknown)=>T;key:(value:T)=>string}>;
const rulePart = (value:string):string=>value.length+':'+value;
const ruleData = (input:unknown,allowed:readonly string[]):Record<string,PropertyDescriptor>=>{
  if(input===null||typeof input!=='object'||Array.isArray(input)||![Object.prototype,null].includes(Object.getPrototypeOf(input))) throw new TypeError('RULE_INPUT');
  const descriptors=Object.getOwnPropertyDescriptors(input);
  if(Reflect.ownKeys(descriptors).some(key=>typeof key!=='string'||!allowed.includes(key))||Object.values(descriptors).some(d=>!Object.hasOwn(d,'value')||!d.enumerable)) throw new TypeError('RULE_INPUT');
  return descriptors;
};
`;
const STRING = `const ruleString:RuleProtocol<string> = Object.freeze({normalize:(input:unknown):string=>{if(typeof input!=='string')throw new TypeError('RULE_INPUT');return input;},key:(value:string):string=>rulePart('String')+rulePart(value)});
`;
const BOOL = `const ruleBool:RuleProtocol<boolean> = Object.freeze({normalize:(input:unknown):boolean=>{if(typeof input!=='boolean')throw new TypeError('RULE_INPUT');return input;},key:(value:boolean):string=>rulePart('Bool')+rulePart(value?'1':'0')});
`;
const UINT64 = `const ruleUInt64:RuleProtocol<bigint> = Object.freeze({
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
`;
const OPTIONAL = `const ruleOptional = <T>(element:RuleProtocol<T>):RuleProtocol<T|null>=>Object.freeze({normalize:(input:unknown):T|null=>input===null?null:element.normalize(input),key:(value:T|null):string=>value===null?rulePart('absent'):rulePart('present')+rulePart(element.key(value))});
`;
const SEQUENCE = `const ruleSequence = <T>(element:RuleProtocol<T>,unique:boolean):RuleProtocol<readonly T[]>=>Object.freeze({
  normalize:(input:unknown):readonly T[]=>{
    if(!Array.isArray(input)||Object.getPrototypeOf(input)!==Array.prototype)throw new TypeError('RULE_INPUT');
    const descriptors:Record<string,PropertyDescriptor>=Object.getOwnPropertyDescriptors(input),length=descriptors.length!.value as number;
    if(Reflect.ownKeys(descriptors).length!==length+1)throw new TypeError('RULE_INPUT');
    const rows:{value:T;key:string}[]=[];
    for(let i=0;i<length;i++){const d=descriptors[String(i)];if(!d||!Object.hasOwn(d,'value')||!d.enumerable)throw new TypeError('RULE_INPUT');const value=element.normalize(d.value);rows.push({value,key:element.key(value)});}
    if(unique){if(new Set(rows.map(row=>row.key)).size!==rows.length)throw new TypeError('RULE_INPUT');rows.sort((a,b)=>a.key<b.key?-1:a.key>b.key?1:0);}
    return Object.freeze(rows.map(row=>row.value));
  },key:(values:readonly T[]):string=>rulePart(unique?'set':'list')+rulePart(String(values.length))+values.map(value=>rulePart(element.key(value))).join(''),
});
`;
const TO_SET = `const ruleToSet = <T>(input:readonly T[],element:RuleProtocol<T>):readonly T[]=>{
  const rows=new Map<string,T>();for(const value of input){const key=element.key(value);if(!rows.has(key))rows.set(key,value);}
  return Object.freeze([...rows].sort(([a],[b])=>a<b?-1:a>b?1:0).map(([,value])=>value));
};
`;
const SUM = `type RuleAnyProtocol = Readonly<{normalize:(input:unknown)=>unknown;key:(value:never)=>string}>;
type RuleSumCase<P> = {[K in keyof P]:P[K] extends null?Readonly<{variant:K}>:P[K] extends RuleProtocol<infer T>?Readonly<{variant:K;payload:T}>:never}[keyof P];
const ruleSum = <const P extends Readonly<Record<string,RuleAnyProtocol|null>>>(variants:P):RuleProtocol<RuleSumCase<P>>=>Object.freeze({
  normalize:(input:unknown):RuleSumCase<P>=>{
    const d=ruleData(input,['variant','payload']),variant=d.variant?.value;
    if(typeof variant!=='string'||!Object.hasOwn(variants,variant))throw new TypeError('RULE_INPUT');
    const protocol=variants[variant]!;
    if(Object.keys(d).length!==(protocol===null?1:2)||(protocol!==null&&!Object.hasOwn(d,'payload')))throw new TypeError('RULE_INPUT');
    return Object.freeze(protocol===null?{variant}:{variant,payload:protocol.normalize(d.payload!.value)}) as RuleSumCase<P>;
  },key:(value:RuleSumCase<P>):string=>{
    const protocol=variants[value.variant]!;
    if(protocol!==null&&!('payload' in value))throw new TypeError('RULE_INPUT');
    return rulePart('sum')+rulePart(String(value.variant))+(protocol===null?rulePart('no-payload'):rulePart(protocol.key(('payload' in value?value.payload:undefined) as never)));
  },
});
`;

export function renderStructuredRuleSupport(capabilities: ReadonlySet<StructuredRuleCapability>): string {
  const part = (name: string, source: string): string => `// structured-rule-capability:${name}\n${source}`;
  return part("base", BASE)
    + (capabilities.has("String") ? part("String", STRING) : "")
    + (capabilities.has("Bool") ? part("Bool", BOOL) : "")
    + (capabilities.has("UInt64") ? part("UInt64", UINT64) : "")
    + (capabilities.has("optional") ? part("optional", OPTIONAL) : "")
    + (capabilities.has("sequence") ? part("sequence", SEQUENCE) : "")
    + (capabilities.has("to-set") ? part("to-set", TO_SET) : "")
    + (capabilities.has("sum") ? part("sum", SUM) : "")
    + "// end structured Rule support\n";
}
