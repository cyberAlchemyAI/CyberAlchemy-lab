import {assertCompiledCompositionBoundary, type CompiledCompositionBoundary} from '../input/composition-boundary.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {decodeTypedCalculationContract, type NumericExpression, type TypedCalculationContract} from '../typed-backend/contracts.js';
import {PROFILED_SOURCE_DIGESTS} from './profiled-project.js';
import {EXACT_UINT64_PROFILE} from './exact-uint64.js';
import type {PlannedArtifact} from './contracts.js';

// Candidate construction; not a source-profile amendment or public default.
export const CONFIGURED_CALCULATION_VERSION='domainspec.configured-calculations-selection/v1-candidate';
export const CALCULATION_CONTRACT_SHA256='6475ec98ba166abca42c25d99f519639d23e6f92fda22de0839139b99118699b';
const CONFIGURATION_SHA256='9ac018e42080483f373219049b466d8a515cb3e7748181ea8e635b1162af8317';
export interface ConfiguredCalculationSelection {
  readonly schema_version:typeof CONFIGURED_CALCULATION_VERSION;
  readonly language:'typescript';
  readonly value_profile:typeof EXACT_UINT64_PROFILE;
  readonly boundary_sha256:string;
  readonly module_root:string;
  readonly roots:readonly string[];
}
export interface CalculationConfigurationSources {
  readonly configuration:string;
  readonly base:string;
  readonly typescript:string;
  readonly calculation_contract:string;
}
const fail=(message:string):never=>{throw new Error('DS_CONFIGURED_CALCULATION:'+message);};
const reserved=new Set(('as async await break case catch class const continue crate debugger def default del do else enum except export extends false finally fn for from function global if impl import in interface is lambda let loop match mod move mut new nonlocal null package pass private protected pub public raise ref return self static struct super switch this throw trait true try type typeof unsafe use var void while with yield con prn aux nul '+Array.from({length:9},(_,i)=>`com${i+1} lpt${i+1}`).join(' ')).split(' '));
const portable=(s:string)=>/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.test(s)&&!reserved.has(s);
function keys(value:unknown,expected:readonly string[]):void{
  if(!value||typeof value!=='object'||Array.isArray(value)||![Object.prototype,null].includes(Object.getPrototypeOf(value)))fail('plain data object required');
  const d=Object.getOwnPropertyDescriptors(value);
  if(Reflect.ownKeys(d).length!==expected.length||Reflect.ownKeys(d).some(k=>typeof k!=='string'||!expected.includes(k))||Object.values(d).some(v=>!Object.hasOwn(v,'value')||!v.enumerable))fail('closed data object required');
}
const freeze=<T>(value:T):T=>{if(value&&typeof value==='object'&&!Object.isFrozen(value)){Object.values(value).forEach(freeze);Object.freeze(value);}return value;};
function frozenLiteral(value:unknown):string{
  if(Array.isArray(value))return `Object.freeze([${value.map(frozenLiteral).join(',')}])`;
  if(value&&typeof value==='object')return `Object.freeze({${Object.entries(value).map(([k,v])=>`[${JSON.stringify(k)}]:${frozenLiteral(v)}`).join(',')}})`;
  return JSON.stringify(value);
}

const baseSupport=`type CalculationUInt64Input = bigint|number|string;
const normalize = (input:unknown):bigint=>{
  let result:bigint;
  if(typeof input==='bigint') result=input;
  else if(typeof input==='number'&&Number.isSafeInteger(input)) result=BigInt(input);
  else if(typeof input==='string'&&input.length<=20&&/^(0|[1-9][0-9]*)$/.exec(input)?.[0]===input) result=BigInt(input);
  else throw new TypeError('CALCULATION_INPUT');
  if(result<0n||result>18446744073709551615n) throw new TypeError('CALCULATION_INPUT');
  return result;
};
const properties = (input:unknown,names:readonly string[]):Record<string,PropertyDescriptor>=>{
  if(!input||typeof input!=='object'||![Object.prototype,null].includes(Object.getPrototypeOf(input))) throw new TypeError('CALCULATION_INPUT');
  const descriptors=Object.getOwnPropertyDescriptors(input);
  if(Reflect.ownKeys(descriptors).length!==names.length||Reflect.ownKeys(descriptors).some(k=>typeof k!=='string'||!names.includes(k))||Object.values(descriptors).some(d=>!Object.hasOwn(d,'value')||!d.enumerable)) throw new TypeError('CALCULATION_INPUT');
  return descriptors;
};
const checked = (value:bigint):bigint=>{
  if(value<0n) throw new RangeError('CALCULATION_UNDERFLOW');
  if(value>18446744073709551615n) throw new RangeError('CALCULATION_OVERFLOW');
  return value;
};
`;
const divideSupport=`const divide = (left:bigint,right:bigint,rounding:'floor'|'ceil'|'reject'):bigint=>{
  if(right===0n) throw new RangeError('CALCULATION_DIVIDE_BY_ZERO');
  const remainder=left%right;
  if(remainder!==0n&&rounding==='reject') throw new RangeError('CALCULATION_INEXACT');
  return checked(left/right+(rounding==='ceil'&&remainder!==0n?1n:0n));
};
`;
const programMarker='// Checked arithmetic program follows.\n';

function provider(contract:TypedCalculationContract):string{
  const names=contract.inputs.map(p=>p.name),lines:string[]=[];
  let usesDivide=false;
  const expression=(e:NumericExpression):string=>{
    if(e.op==='input'){const i=names.indexOf(e.name);if(i<0)fail('unknown input');return `p${i}`;}
    if(e.op==='literal')return `${e.value}n`;
    const left=expression(e.left),right=expression(e.right),name=`v${lines.length}`;
    if(e.op==='divide')usesDivide=true;
    const source=e.op==='divide'?`divide(${left},${right},${JSON.stringify(contract.division_rounding)})`:
      `checked(${left}${e.op==='add'?'+':e.op==='subtract'?'-':'*'}${right})`;
    lines.push(`  const ${name}=${source};`);return name;
  };
  const result=expression(contract.expression);
  return baseSupport+(usesDivide?divideSupport:'')+programMarker+`export const calculate = (input:Readonly<{${names.map(n=>`readonly ${JSON.stringify(n)}:CalculationUInt64Input`).join(';')}}>):bigint=>{\n`+
    `  const d=properties(input,${JSON.stringify(names)});\n`+
    names.map((n,i)=>`  const p${i}=normalize(d[${JSON.stringify(n)}]!.value);\n`).join('')+
    lines.map(s=>s+'\n').join('')+`  return ${result};\n};\n`;
}

/** In-memory planner over an explicitly selected registered boundary. The
 * provider and descriptor are separate artifacts to avoid self-hash cycles.
 */
export function planConfiguredCalculations(boundary:CompiledCompositionBoundary,selection:ConfiguredCalculationSelection,sources:CalculationConfigurationSources){
  assertCompiledCompositionBoundary(boundary);
  keys(selection,['schema_version','language','value_profile','boundary_sha256','module_root','roots']);
  keys(sources,['configuration','base','typescript','calculation_contract']);
  if(selection.schema_version!==CONFIGURED_CALCULATION_VERSION||selection.language!=='typescript'||selection.value_profile!==EXACT_UINT64_PROFILE)fail('unsupported selection');
  if(selection.boundary_sha256!==boundary.boundary_sha256)fail('stale boundary');
  if(typeof selection.module_root!=='string'||!selection.module_root.split('/').every(portable))fail('unsafe module root');
  if(!Array.isArray(selection.roots)||Object.getPrototypeOf(selection.roots)!==Array.prototype)fail('roots must be a plain array');
  const rd:Record<string,PropertyDescriptor>=Object.getOwnPropertyDescriptors(selection.roots),length=rd.length!.value;
  if(!Number.isSafeInteger(length)||length<1||Reflect.ownKeys(rd).length!==length+1)fail('roots must be a nonempty dense array');
  const roots:string[]=[];
  for(let i=0;i<length;i++){const d=rd[String(i)];if(!d||!Object.hasOwn(d,'value')||!d.enumerable||typeof d.value!=='string')return fail('inert roots required');roots.push(d.value);}
  if(new Set(roots).size!==roots.length)fail('duplicate roots');roots.sort();
  const expected={configuration:CONFIGURATION_SHA256,...PROFILED_SOURCE_DIGESTS,calculation_contract:CALCULATION_CONTRACT_SHA256};
  for(const key of Object.keys(expected) as (keyof typeof expected)[])if(typeof sources[key]!=='string'||sha256(sources[key])!==expected[key])fail('source drift:'+key);
  const config=JSON.parse(sources.configuration),cell=config.types.find((t:{kind:string})=>t.kind==='Calculation');
  if(cell?.role!=='domain/calculations'||canonicalJson(cell.blocked_by)!=='["DSR-011"]')fail('unexpected Calculation configuration');
  const profile=JSON.parse(sources.typescript),overlay=profile.representation_overlays?.find((o:{contract_id:string})=>o.contract_id==='calculation.profile-representation');
  const protocol=overlay?.candidate_protocols.find((p:{protocol_id:string})=>p.protocol_id==='typescript.bound-calculation/v1');
  if(protocol?.form_id!=='typescript.calculation-arrow-function'||protocol.descriptor_contract.effect_contract!=='none'||protocol.descriptor_contract.dependency_contract!=='explicit-only')fail('missing Calculation protocol');
  const artifacts:PlannedArtifact[]=[];
  const artifact=(relative_path:string,content:string)=>{const a={relative_path,content,size_bytes:Buffer.byteLength(content),sha256:sha256(content)};artifacts.push(a);return a;};
  const modules=roots.map(selector=>{
    const parts=selector.split(':');if(parts.length!==2||!parts.every(portable))fail('unsafe selector');
    const row=boundary.value_bindings.core_contracts.find(c=>c.owner.selector===selector);
    if(!row||row.kind!=='Calculation')return fail('typed Calculation required:'+selector);
    const contract=decodeTypedCalculationContract(row.contract);
    if(contract.inputs.some(p=>p.type.kind!=='scalar'||p.type.name!=='UInt64'))fail('UInt64 inputs required');
    const [feature,node]=parts as [string,string],callable='calculate'+node.split('-').map(s=>s[0]!.toUpperCase()+s.slice(1)).join('');
    const relative_path=`${selection.module_root}/features/${feature}/src/${cell.role}/${node}.ts`;
    const provider_path=relative_path.replace(/\.ts$/,'.provider.ts');
    const implementation=artifact(provider_path,provider(contract));
    const descriptorBody={schema_version:'domainspec.generated-calculation-descriptor/v1-candidate',protocol_id:'typescript.bound-calculation/v1',selector,
      ontology_calculation:contract.ontology_calculation,contract_sha256:sha256(canonicalJson(contract)),source:row.source,
      inputs:contract.inputs,result:contract.result,division_rounding:contract.division_rounding,value_profile:selection.value_profile,
      return_semantics:'value',effect_contract:'none',dependency_contract:'explicit-only',failure_contract:'declared',result_consumption:'complete',primary_callable_count:1,supporting_exports:'explicit-only',
      failures:JSON.parse(sources.calculation_contract).failures,provider:{id:selector+'/typescript-exact/v1',sha256:implementation.sha256},authority_effect:'none'};
    const descriptor={...descriptorBody,descriptor_sha256:sha256(canonicalJson(descriptorBody))};
    const provider_import=`./${node}.provider.js`;
    artifact(relative_path,`import {calculate} from ${JSON.stringify(provider_import)};\nexport const ${callable}=Object.freeze(Object.assign(calculate,{descriptor:${frozenLiteral(descriptor)}}));\n`);
    return {selector,relative_path,provider_path,provider_import,callable,descriptor};
  });
  artifacts.sort((a,b)=>a.relative_path<b.relative_path?-1:1);
  const body={schema_version:'domainspec.configured-calculations-plan/v1-candidate' as const,selection:{...selection,roots},
    source_digests:expected,boundary_sha256:boundary.boundary_sha256,certificate:boundary.certificate,modules,artifacts,
    discharged_configuration_prerequisites:['DSR-011'],authority_effect:'none' as const};
  return freeze({...body,plan_sha256:sha256(canonicalJson(body))});
}
