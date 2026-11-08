// structured-rule-capability:base
type RuleProtocol<T> = Readonly<{normalize:(input:unknown)=>T;key:(value:T)=>string}>;
const rulePart = (value:string):string=>value.length+':'+value;
const ruleData = (input:unknown,allowed:readonly string[]):Record<string,PropertyDescriptor>=>{
  if(input===null||typeof input!=='object'||Array.isArray(input)||![Object.prototype,null].includes(Object.getPrototypeOf(input))) throw new TypeError('QUERY_INPUT');
  const descriptors=Object.getOwnPropertyDescriptors(input);
  if(Reflect.ownKeys(descriptors).some(key=>typeof key!=='string'||!allowed.includes(key))||Object.values(descriptors).some(d=>!Object.hasOwn(d,'value')||!d.enumerable)) throw new TypeError('QUERY_INPUT');
  return descriptors;
};
// structured-rule-capability:Bool
const ruleBool:RuleProtocol<boolean> = Object.freeze({normalize:(input:unknown):boolean=>{if(typeof input!=='boolean')throw new TypeError('QUERY_INPUT');return input;},key:(value:boolean):string=>rulePart('Bool')+rulePart(value?'1':'0')});
// structured-rule-capability:UInt64
const ruleUInt64:RuleProtocol<bigint> = Object.freeze({
  normalize:(input:unknown):bigint=>{
    let value:bigint;
    if(typeof input==='bigint')value=input;
    else if(typeof input==='number'&&Number.isSafeInteger(input))value=BigInt(input);
    else if(typeof input==='string'&&input.length<=20&&/^(0|[1-9][0-9]*)$/.exec(input)?.[0]===input)value=BigInt(input);
    else throw new TypeError('QUERY_INPUT');
    if(value<0n||value>18446744073709551615n)throw new TypeError('QUERY_INPUT');
    return value;
  },key:(value:bigint):string=>rulePart('UInt64')+rulePart(String(value)),
});
// structured-rule-capability:sequence
const ruleSequence = <T>(element:RuleProtocol<T>,unique:boolean):RuleProtocol<readonly T[]>=>Object.freeze({
  normalize:(input:unknown):readonly T[]=>{
    if(!Array.isArray(input)||Object.getPrototypeOf(input)!==Array.prototype)throw new TypeError('QUERY_INPUT');
    const descriptors:Record<string,PropertyDescriptor>=Object.getOwnPropertyDescriptors(input),length=descriptors.length!.value as number;
    if(Reflect.ownKeys(descriptors).length!==length+1)throw new TypeError('QUERY_INPUT');
    const rows:{value:T;key:string}[]=[];
    for(let i=0;i<length;i++){const d=descriptors[String(i)];if(!d||!Object.hasOwn(d,'value')||!d.enumerable)throw new TypeError('QUERY_INPUT');const value=element.normalize(d.value);rows.push({value,key:element.key(value)});}
    if(unique){if(new Set(rows.map(row=>row.key)).size!==rows.length)throw new TypeError('QUERY_INPUT');rows.sort((a,b)=>a.key<b.key?-1:a.key>b.key?1:0);}
    return Object.freeze(rows.map(row=>row.value));
  },key:(values:readonly T[]):string=>rulePart(unique?'set':'list')+rulePart(String(values.length))+values.map(value=>rulePart(element.key(value))).join(''),
});
// end structured Rule support
type R2 = Readonly<{readonly "accepted":boolean;readonly "id":bigint}>;
type R2Input = Readonly<{readonly "accepted":boolean;readonly "id":bigint|number|string}>;
const R2Value:RuleProtocol<R2> = Object.freeze({
  normalize:(input:unknown):R2=>{
    const d=ruleData(input,["accepted","id"]);
    return Object.freeze({["accepted"]:ruleBool.normalize(Object.hasOwn(d,"accepted")?d["accepted"]!.value:undefined),["id"]:ruleUInt64.normalize(Object.hasOwn(d,"id")?d["id"]!.value:undefined)});
  },key:(value:R2):string=>rulePart("Entity")+rulePart("lab:submission")+rulePart("id")+rulePart(ruleUInt64.key(value["id"])),
});
type R3 = ReadonlyArray<R2>;
type R3Input = ReadonlyArray<R2Input>;
const R3Value:RuleProtocol<R3> = ruleSequence(R2Value,false);
// Checked Query program follows.
export const query = (rows:R3Input,parameters:Readonly<{}>):Readonly<{readonly "id":bigint;readonly "accepted":boolean}> | null => {
  const d=ruleData(parameters,[]);
  if(Object.keys(d).length!==0)throw new TypeError('QUERY_INPUT');
  const snapshots=R3Value.normalize(rows);
  let selected=snapshots.filter(row=>(ruleBool.key(row["accepted"]) === ruleBool.key(true)));
  if(selected.length>1)throw new TypeError('QUERY_CARDINALITY');
  if(selected.length===0)return null;
  const row=selected[0]!;
  return Object.freeze({["id"]:row["id"],["accepted"]:row["accepted"]});
};
