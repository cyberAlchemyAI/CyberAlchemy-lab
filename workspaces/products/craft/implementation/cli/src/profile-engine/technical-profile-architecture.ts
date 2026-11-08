/** Inert lowering into the original v1 architecture package vocabulary.
 * Checked source custody is owned by technical-profile-source, not this adapter.
 * Open questions: goals/plans/craft-technical-profiles-2026-10-31/UNIFIED-DESIGN.md.
 */
import path from 'node:path';
import {captureJson,dataDigest,validateProfilePackage,reject,PROFILE_ROLE_CONTRACTS,type Json,type ProfilePackage,type DerivationRule,type Role} from './contracts.js';
import {readCorePhysicalFile} from '../commerce/commerce-core-physical.js';
import {validateTechnicalTopologyRoot} from './technical-profile-topology.js';

type Port=Readonly<{direction:'requires'|'provides';contract:string}>;
type Binding=Readonly<{kind:string;descriptor_ref?:string;recipe_ref?:string;contract?:string;ports:Readonly<Record<string,Port>>}>;
export interface TechnicalProfileArchitectureEnvelope {
 readonly id:string;readonly version:string;readonly kind:string;
 readonly selection:Readonly<{mapping:string}>;
 readonly target:Readonly<{consumer:string;package_schema:string|null;selected_package?:Readonly<{id:string;version:string;manifest:string}>}>;
 readonly bindings:Readonly<Record<string,Binding>>;
 readonly resource_requirements:readonly unknown[];readonly runtime_bindings:readonly unknown[];
}
export interface TechnicalProfileArchitectureTopology {
 readonly requestBytes:string;
 readonly nodes:readonly Readonly<{id:string;binding:string}>[];
 readonly edges:readonly Readonly<{source:string;sourcePort:string;target:string;targetPort:string;contract:string;kind:string}>[];
}
export interface TechnicalProfileArchitectureResult {
 readonly package:ProfilePackage;
 readonly files:Readonly<Record<string,string>>;
 readonly manifest:Readonly<{
  schema_version:'craft.technical-profile-architecture-derivation/v1';source_id:string;source_version:string;mapping:string;
  generated_package_id:string;generated_package_version:string;generated_package_sha256:string;
  topology_sha256:string;provenance:Json;basis_files:readonly Readonly<{path:string;sha256:string;bytes:number}>[];
  roles:readonly Role[];request_bytes:number;authority_effect:'none';
 }>;
}

function fail(detail:string):never{return reject('PROFILE_TECHNICAL_ARCHITECTURE','/',detail);}
const ownPath=(root:string,value:string):string=>{
 if(typeof value!=='string'||!value||path.isAbsolute(value)||value.includes('\\')||value.split('/').some(x=>!x||x==='.'||x==='..'))fail('owned repository-relative path required');
 const result=path.resolve(root,value);if(path.relative(root,result).startsWith('..'))fail('path outside original owner');return result;
};
const roles:readonly Role[]=['domain-function','http-entry','http-dispatch','shared-http-port'];
function bindingRole(binding:Binding):Role {
 if(binding.kind==='business-root'&&binding.contract==='entry')return 'domain-function';
 if(binding.kind!=='owner')return fail('architecture admits original owner and checked business-root bindings only');
 const role=roles.find(role=>PROFILE_ROLE_CONTRACTS[role].descriptor_ref===binding.descriptor_ref&&PROFILE_ROLE_CONTRACTS[role].recipe_ref===binding.recipe_ref);
 if(!role||role==='domain-function')return fail('unregistered architecture descriptor/recipe');return role;
}

/** Only call after original source checking/evaluation, with physical currentness
 * asserted by that source owner before and after this synchronous derivation.
 * Returned data is not a native handle or authority grant.
 */
export function lowerTechnicalProfileArchitecture(input:Readonly<{
 envelope:TechnicalProfileArchitectureEnvelope;topology:TechnicalProfileArchitectureTopology;provenance:unknown;repositoryRoot:string;
}>):TechnicalProfileArchitectureResult {
 const envelope=captureJson(input.envelope) as unknown as TechnicalProfileArchitectureEnvelope;
 const topology=captureJson(input.topology) as unknown as TechnicalProfileArchitectureTopology;
 const provenance=captureJson(input.provenance);
 if(!path.isAbsolute(input.repositoryRoot)||path.normalize(input.repositoryRoot)!==input.repositoryRoot)fail('normalized repository root required');
 if(envelope.kind!=='architecture'||envelope.target.consumer!=='craft.profile-engine/v1'||envelope.target.package_schema!=='craft.profile-package/v1')fail('exact supported architecture consumer required; stateful families cannot be coerced');
 validateTechnicalTopologyRoot(envelope.target.consumer,topology);
 if(envelope.resource_requirements.length||envelope.runtime_bindings.length)fail('external resource/runtime bindings require their original effect consumer');
 if(typeof topology.requestBytes!=='string'||!/^\d+$/.test(topology.requestBytes)||BigInt(topology.requestBytes)<1n||BigInt(topology.requestBytes)>65536n)fail('checked requestBytes must be UInt64 within 1..65536');
 const requestBytes=Number(topology.requestBytes);
 if(!Array.isArray(topology.nodes)||topology.nodes.length<3||topology.nodes.length>32||!Array.isArray(topology.edges)||topology.edges.length>64)fail('bounded architecture topology required');
 const nodes=new Map<string,{binding:Binding;role:Role}>(),bindings=new Set<string>();
 for(const node of topology.nodes){
  if(typeof node.id!=='string'||!node.id||nodes.has(node.id)||bindings.has(node.binding))fail('unique topology node and binding identities required');
  const binding=envelope.bindings[node.binding];if(!binding||!binding.ports)fail('node has no declared binding/ports');
  const role=bindingRole(binding);nodes.set(node.id,{binding,role});bindings.add(node.binding);
 }
 if(bindings.size!==Object.keys(envelope.bindings).length)fail('architecture bindings must all participate in selected topology');
 const byRole=(role:Role)=>[...nodes].filter(([,node])=>node.role===role).map(([id])=>id);
 const business=byRole('domain-function'),entries=byRole('http-entry'),dispatchers=byRole('http-dispatch'),ports=byRole('shared-http-port');
 if(!business.length||business.length!==entries.length||dispatchers.length!==1||ports.length>1)fail('one dispatcher and paired business/entry archetypes required, with at most one shared transport');
 const links=new Map<string,string>(),incomingBusiness=new Set<string>(),incomingEntries=new Set<string>();
 for(const edge of topology.edges){
  const from=nodes.get(edge.source),to=nodes.get(edge.target),sourcePort=from?.binding.ports[edge.sourcePort],targetPort=to?.binding.ports[edge.targetPort];
  if(!from||!to||!sourcePort||!targetPort||sourcePort.direction!=='requires'||targetPort.direction!=='provides'||edge.contract!==sourcePort.contract||edge.contract!==targetPort.contract||edge.kind!=='Dependency')fail('exact declared directional dependency ports required');
  const key=edge.source+':'+edge.sourcePort;if(links.has(key))fail('required port must resolve exactly once');links.set(key,edge.target);
  if(from.role==='http-entry'&&to.role==='domain-function'&&edge.contract==='entry'){
   if(incomingBusiness.has(edge.target))fail('each business archetype has exactly one entry');incomingBusiness.add(edge.target);
  }else if(from.role==='http-dispatch'&&to.role==='http-entry'&&edge.contract==='entry'){
   if(incomingEntries.has(edge.target))fail('dispatcher entry dependency repeated');incomingEntries.add(edge.target);
  }else if(from.role==='http-entry'&&to.role==='shared-http-port'&&edge.contract==='httpTransport'){
   if(edge.target!==ports[0])fail('entries must use one original shared transport');
  }else fail('unsupported architecture edge; source graph cannot invent native wiring');
 }
 for(const [id,node] of nodes)for(const [port,value] of Object.entries(node.binding.ports))if(value.direction==='requires'&&!links.has(id+':'+port))fail('unbound required architecture port');
 if(incomingBusiness.size!==business.length||incomingEntries.size!==entries.length)fail('every business/entry archetype must participate in the dispatcher');
 for(const id of entries){const outgoing=topology.edges.filter(edge=>edge.source===id);if(outgoing.filter(edge=>nodes.get(edge.target)?.role==='domain-function').length!==1||outgoing.filter(edge=>nodes.get(edge.target)?.role==='shared-http-port').length!==ports.length)fail('each entry must invoke exactly one business role and the selected transport');}
 const basis=envelope.target.selected_package;if(!basis)fail('exact original package realization required');
 const manifestPath=ownPath(input.repositoryRoot,basis.manifest),manifestFile=readCorePhysicalFile(manifestPath),basisPackage=validateProfilePackage(JSON.parse(manifestFile.text));
 if(basisPackage.id!==basis.id||basisPackage.version!==basis.version||basisPackage.dependencies.length)fail('exact original dependency-free package basis required');
 const needed=new Set<Role>([...nodes.values()].map(node=>node.role));
 for(const role of needed)if(!basisPackage.capabilities.some(capability=>capability.role===role))fail('original selected package lacks required role');
 // Existing http-entry producer chooses transport ownership from its one shared
 // port contribution; preserve that original behavior instead of new callbacks.
 if(basisPackage.capabilities.some(capability=>capability.role==='shared-http-port')!==!!ports.length)fail('source topology and original transport recipe disagree');
 const basisFiles=[manifestFile],packageRoot=path.dirname(manifestPath),files:Record<string,string>=Object.create(null);
 const rules=JSON.parse(JSON.stringify(basisPackage.rules)) as any[];
 const emittedRules=rules.filter(rule=>rule.op!=='emit'||needed.has(rule.role));
 const usedTables=new Set(emittedRules.filter(rule=>rule.op==='emit').map(rule=>rule.from));
 const selectedRules=emittedRules.filter(rule=>rule.op!=='defaults'||usedTables.has(rule.as));
 const assetIds=new Set<string>();
 for(const rule of selectedRules){
  if(rule.op==='emit'&&rule.role==='http-entry'){
   if(!rule.fields.technical?.literal||typeof rule.fields.technical.literal!=='object')fail('original entry producer has no admitted technical configuration');
   rule.fields.technical.literal.request_bytes=requestBytes;
  }
  const template=rule.op==='emit'?rule.fields.template_ref?.literal:rule.op==='defaults'?rule.values.template_ref:undefined;
  if(typeof template==='string')assetIds.add(template);
 }
 const selectAsset=(id:string)=>{const asset=basisPackage.assets.find(asset=>asset.id===id);if(!asset)fail('original asset reference is unresolved');for(const included of asset.includes)if(!assetIds.has(included)){assetIds.add(included);selectAsset(included);}};
 for(const id of assetIds)selectAsset(id);
 const selectedAssets=basisPackage.assets.filter(asset=>assetIds.has(asset.id));
 for(const asset of selectedAssets){const physical=readCorePhysicalFile(ownPath(packageRoot,asset.path));if(physical.file.sha256!==asset.sha256)fail('original recipe asset changed');basisFiles.push(physical);files[asset.path]=physical.text;}
 const topologyDigest=dataDigest(topology),sourceIdentity={source_id:envelope.id,source_version:envelope.version,mapping:envelope.selection.mapping,topology_sha256:topologyDigest,provenance,basis_files:basisFiles.map(file=>({...file.file,path:path.relative(input.repositoryRoot,file.file.path).split(path.sep).join('/')}))};
 const portable=envelope.id.replace(/[^A-Za-z0-9_-]/g,'_').slice(0,85),id='Technical_'+portable+'_'+dataDigest(sourceIdentity).slice(0,16);
 if(selectedRules.some(rule=>rule.id==='technicalSourceProvenance'||rule.as==='technicalSourceProvenance'))fail('reserved source provenance rule collides');
 selectedRules.push({id:'technicalSourceProvenance',op:'defaults',as:'technicalSourceProvenance',values:sourceIdentity});
 const generated=validateProfilePackage({...basisPackage,id,capabilities:basisPackage.capabilities.filter(capability=>needed.has(capability.role)),assets:selectedAssets,rules:selectedRules as DerivationRule[]});
 files['profile.json']=JSON.stringify(generated,null,2)+'\n';
 for(const file of basisFiles)if(readCorePhysicalFile(file.file.path).fingerprint!==file.fingerprint)fail('original recipe basis changed during lowering');
 const manifest={schema_version:'craft.technical-profile-architecture-derivation/v1' as const,...sourceIdentity,generated_package_id:generated.id,generated_package_version:generated.version,generated_package_sha256:dataDigest(generated),roles:[...needed].sort() as Role[],request_bytes:requestBytes,authority_effect:'none' as const};
 return Object.freeze({package:generated,files:Object.freeze(files),manifest:Object.freeze(manifest)});
}
