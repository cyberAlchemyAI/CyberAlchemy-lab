import { createHash } from 'node:crypto';
import { checkComputationContract } from './check.js';
import { inertSnapshot, validUnicode } from './data.js';
import { ComputationContractError } from './types.js';
import type { CheckedComputation, ComputationContract, PureDeclaration } from './types.js';

export const COMPUTATION_SOURCE_VERSION='domainspec.computation-source/v1-candidate' as const;
export const COMPUTATION_SOURCE_PROFILE='application-v1' as const;
export const COMPUTATION_SOURCE_CAPABILITY='domainspec.computation/v1-candidate' as const;
export interface ComputationDeclarationBinding {
  name:string;
  /** `record` describes a declared type shape, never a new catalog meta-type. */
  kind:'record'|NonNullable<PureDeclaration['kind']>;
  meaning:string;
  body_sha256:string;
}
export interface ComputationSourceBinding {
  schema_version:typeof COMPUTATION_SOURCE_VERSION;
  profile:typeof COMPUTATION_SOURCE_PROFILE;
  capability:typeof COMPUTATION_SOURCE_CAPABILITY;
  owner:{name:string;kind:'Calculation';source_node:string;owner_ref:string;meaning:string;body_sha256:string};
  declarations:Record<string,ComputationDeclarationBinding>;
}
export interface ComputationSource extends ComputationSourceBinding {contract:ComputationContract}
export interface BindComputationSourceOptions {
  owner_ref:string;
  meaning:string;
  /** Exact normalized selectors `$.records[i]` and `$.functions[i]`. */
  declaration_meanings:Readonly<Record<string,string>>;
}
const reject=(path:string,message:string):never=>{throw new ComputationContractError('SourceBinding',path,message);};
function exact(value:unknown,path:string,keys:string[]):Record<string,unknown>{if(!value||typeof value!=='object'||Array.isArray(value)||Object.keys(value).sort().join(',')!==keys.sort().join(','))reject(path,'exact source members required');return value as Record<string,unknown>;}
function nonempty(value:unknown,path:string,max=65536):asserts value is string {if(typeof value!=='string'||!value.trim()||!validUnicode(value)||Buffer.byteLength(value,'utf8')>max)reject(path,'bounded nonempty Unicode text required');}
function stable(value:unknown):unknown {if(Array.isArray(value))return value.map(stable);if(value&&typeof value==='object')return Object.fromEntries(Object.keys(value).sort().map(k=>[k,stable((value as Record<string,unknown>)[k])]));return value;}
/** Current normalized body/signature fingerprint, not approval of domain meaning. */
export function computationBodySha256(body:unknown):string {return createHash('sha256').update(JSON.stringify(stable(inertSnapshot(body)))).digest('hex');}
function descriptors(c:ComputationContract):{path:string;name:string;kind:ComputationDeclarationBinding['kind'];body:unknown}[]{return [...c.records.map((r,i)=>({path:`$.records[${i}]`,name:r.name,kind:'record' as const,body:r})),...c.functions.map((f,i)=>({path:`$.functions[${i}]`,name:f.name,kind:f.kind!,body:f}))];}
function rootName(c:ComputationContract):string {const name=c.source_node.split(':')[1]!.replaceAll('-','_');if(!/^[a-z][a-z0-9_]{0,127}$/.test(name))reject('$.owner.name','source node cannot name bounded Calculation');return name;}
const rootBody=(c:ComputationContract)=>({name:rootName(c),kind:'Calculation',parameters:c.inputs,result:c.result,body:c.expression});
function freeze<T>(value:T):T {if(value&&typeof value==='object'){Object.values(value).forEach(freeze);Object.freeze(value);}return value;}
/** Explicit authoring helper. The caller supplies every meaning; this does not review or approve it. */
export function bindComputationSource(raw:unknown,options:BindComputationSourceOptions):ComputationSource {const checked=checkComputationContract(raw),c=checked.contract;if(c.stage!=='full-computation')reject('$.contract.stage','source successor requires full-computation');const safe=inertSnapshot(options) as unknown as BindComputationSourceOptions;exact(safe,'$options',['owner_ref','meaning','declaration_meanings']);const defs=descriptors(c);exact(safe.declaration_meanings,'$options.declaration_meanings',defs.map(d=>d.path));const source:ComputationSource={schema_version:COMPUTATION_SOURCE_VERSION,profile:COMPUTATION_SOURCE_PROFILE,capability:COMPUTATION_SOURCE_CAPABILITY,owner:{name:rootName(c),kind:'Calculation',source_node:c.source_node,owner_ref:safe.owner_ref,meaning:safe.meaning,body_sha256:computationBodySha256(rootBody(c))},declarations:Object.fromEntries(defs.map(d=>[d.path,{name:d.name,kind:d.kind,meaning:safe.declaration_meanings[d.path]!,body_sha256:computationBodySha256(d.body)}])),contract:c};unwrapComputationSource(source);return freeze(source);}
/** Validate ownership, declared meaning closure and current body identities before exposing checked IR. */
export function unwrapComputationSource(raw:unknown):{checked:CheckedComputation;source_binding:ComputationSourceBinding} {const source=inertSnapshot(raw) as Record<string,unknown>;exact(source,'$',['schema_version','profile','capability','owner','declarations','contract']);if(source.schema_version!==COMPUTATION_SOURCE_VERSION||source.profile!==COMPUTATION_SOURCE_PROFILE||source.capability!==COMPUTATION_SOURCE_CAPABILITY)reject('$','unsupported source successor');const checked=checkComputationContract(source.contract),c=checked.contract;if(c.stage!=='full-computation')reject('$.contract.stage','source successor requires full-computation');const owner=exact(source.owner,'$.owner',['name','kind','source_node','owner_ref','meaning','body_sha256']);if(owner.kind!=='Calculation'||owner.name!==rootName(c)||owner.source_node!==c.source_node)reject('$.owner','declared Calculation owner must match exact normalized root');nonempty(owner.owner_ref,'$.owner.owner_ref',256);if(!/^[\x21-\x7e]+$/.test(owner.owner_ref))reject('$.owner.owner_ref','nonempty printable ASCII owner identity required');nonempty(owner.meaning,'$.owner.meaning');if(owner.body_sha256!==computationBodySha256(rootBody(c)))reject('$.owner.body_sha256','stale Calculation body/signature');const defs=descriptors(c);if(new Set([owner.name,...defs.map(d=>d.name)]).size!==defs.length+1)reject('$.declarations','source declarations require unique names including root');const declared=exact(source.declarations,'$.declarations',defs.map(d=>d.path));for(const d of defs){const row=exact(declared[d.path],`$.declarations[${JSON.stringify(d.path)}]`,['name','kind','meaning','body_sha256']);if(row.name!==d.name||row.kind!==d.kind)reject(`$.declarations[${JSON.stringify(d.path)}]`,'declaration kind/name must match actual contract position');nonempty(row.meaning,`$.declarations[${JSON.stringify(d.path)}].meaning`);if(row.body_sha256!==computationBodySha256(d.body))reject(`$.declarations[${JSON.stringify(d.path)}].body_sha256`,'stale declaration body/signature');}const binding:ComputationSourceBinding={schema_version:COMPUTATION_SOURCE_VERSION,profile:COMPUTATION_SOURCE_PROFILE,capability:COMPUTATION_SOURCE_CAPABILITY,owner:owner as unknown as ComputationSourceBinding['owner'],declarations:declared as unknown as Record<string,ComputationDeclarationBinding>};return {checked,source_binding:freeze(binding)};}
