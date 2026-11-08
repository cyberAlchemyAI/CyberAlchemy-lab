/** Finite application inputs over original source and application owners.
 * No resource, actor or runtime authority is represented by these values.
 * Open Questions: docs/TECHNICAL-PROFILE-SOURCE.md#open-questions. */
import path from 'node:path';
import {captureJson,dataDigest,reject} from './contracts.js';
import {coreFreeze,coreRelativePath,coreSourceDescendants,coreSourceTokens} from '../commerce/commerce-core-syntax.js';
import {readCorePhysicalFile} from '../commerce/commerce-core-physical.js';
import {reconstructCoreCommerceModule,type CoreCommerceType} from '../commerce/commerce-core-reconstruction.js';
import {assertTechnicalProfileSourceOwner,type CheckedTechnicalProfileSource,type createTechnicalProfileSourceOwner} from './technical-profile-source.js';
import {serviceInputFamilies,validateServiceApplicationInputs} from './technical-profile-service-inputs.js';
export const APPLICATION_INPUTS_CONSUMER='craft.application-inputs/v1';
function fail(message:string):never{return reject('TECHNICAL_PROFILE_APPLICATION_INPUTS','application-inputs',message);}
function closed(v:any,keys:readonly string[],required=keys){if(!v||typeof v!=='object'||Array.isArray(v)||Object.keys(v).some(k=>!keys.includes(k))||required.some(k=>!Object.hasOwn(v,k)))fail('closed application input record required: '+keys.join(','));return v;}
const symbol=(v:any)=>typeof v==='string'&&/^[A-Za-z_][A-Za-z0-9_]*$/.test(v);
const label=(v:any)=>typeof v==='string'&&/^[A-Za-z][A-Za-z0-9_.\/-]{0,255}$/.test(v);
const knowledgeFamilies=new Set(['knowledge-ingestion/domain-v1','permissioned-rag/domain-v1']);
function validateKnowledgeInputs(raw:any,contract:any){
 const v=closed(raw,['family','decisionRole','layout','types','sources','projections','representation']);
 if(contract?.schema!=='craft.application-input-contract/v1'||contract.family!==v.family||!knowledgeFamilies.has(v.family)||!symbol(v.decisionRole)||!['EntryModules','ServiceAssembly'].includes(v.layout))fail('supported knowledge family and original layout required');
 closed(v.types,['request','modelInput','proposal','decision']);if(!Object.values(v.types).every(symbol))fail('nominal knowledge type symbols required');
 closed(contract.roles,['decision']);closed(contract.roles.decision,['targetRole','effect','input','output','permission']);
 if(contract.roles.decision.targetRole!=='Operation'||contract.roles.decision.effect!=='pure'||contract.roles.decision.permission!=='preserve-original-entry'||v.types.request!==contract.roles.decision.input||v.types.decision!==contract.roles.decision.output||contract.callbacks!=='forbidden'||contract.unknownPrimitive!=='reject')fail('exact original knowledge decision role required');
 const rag=v.family==='permissioned-rag/domain-v1';
 closed(contract.assets,rag?['baseProfile','inferenceKernel']:['baseProfile']);for(const ref of Object.values(contract.assets))if(typeof ref!=='string'||!coreRelativePath(ref))fail('relative knowledge profile asset required');
 closed(contract.architectureProfiles,['EntryModules','ServiceAssembly']);for(const ref of Object.values(contract.architectureProfiles))if(typeof ref!=='string'||!coreRelativePath(ref))fail('relative knowledge architecture asset required');
 closed(v.representation,['model','dimensions','preprocessing','space']);if(!label(v.representation.model)||!label(v.representation.space)||v.representation.preprocessing!=='utf8-exact-v1'||!['1536',1536].includes(v.representation.dimensions))fail('existing 1536-dimensional knowledge representation required');
 const aliases:Record<string,string>={Facts:'facts',Approval:'approval',DocumentA:'documentA',DocumentB:'documentB'},expected=new Set(Object.keys(aliases)),prefixes=new Set<string>();
 closed(contract.sourceContracts,Object.values(aliases));
 if(!Array.isArray(v.sources)||v.sources.length!==4)fail('four knowledge source roles required');
 for(const source of v.sources){
  closed(source,['role','kind','contract','disclose','minimumOrdinal','prefix']);const name=aliases[source.role],sourceContract=name&&contract.sourceContracts[name];
  if(!expected.delete(source.role)||source.kind!=='Document'||!sourceContract||source.contract!==sourceContract.schema||sourceContract.adapter!=='original-document-authority'||sourceContract.format!==(source.role==='DocumentA'||source.role==='DocumentB'?'binary':'json')||source.disclose!==(source.role!=='Approval')||!['1',1].includes(source.minimumOrdinal)||typeof source.prefix!=='string'||!/^[a-z][a-z0-9-]{0,63}-$/.test(source.prefix)||prefixes.has(source.prefix))fail('finite original knowledge source roles required');
  prefixes.add(source.prefix);
 }
 closed(v.projections,['modelInput','review']);for(const p of Object.values(v.projections))projection(p);
 const originalPaths=(actual:any,paths:Record<string,string>,group:string)=>{closed(actual,Object.keys(paths));for(const [field,from]of Object.entries(paths)){closed(actual[field],['from']);if(actual[field].from!==from)fail('original knowledge producer required for '+group+'.'+field);}};
 originalPaths(v.projections.modelInput,{subjectId:'id',sourceVersion:'sources.facts.revision',prompt:'technical.prompt'},'modelInput');
 originalPaths(v.projections.review,rag?{evidenceContext:'technical.evidenceContext',answerSupported:'technical.answerSupported',injectionDetected:'technical.injectionDetected',retrievalAvailable:'technical.retrievalAvailable'}:{state:'technical.state',format:'technical.format',chunks:'technical.chunks',generation:'technical.generation',deletionRequested:'facts.deletionRequested',parsed:'technical.parsed'},'review');
 return coreFreeze(v);
}
function projection(v:any,depth=0):void{if(depth>12)fail('projection depth');closed(v,Object.keys(v),[]);if(Object.keys(v).length>64)fail('projection field count');for(const [name,p]of Object.entries(v) as [string,any][]){if(!symbol(name))fail('projection field name');if(!p||typeof p!=='object'||Array.isArray(p))fail('inert projection required');const keys=Object.keys(p).sort().join(',');if(keys==='from'){if(typeof p.from!=='string'||!/^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*$/.test(p.from))fail('bounded original projection path');}else if(keys==='literal'){if(p.literal!==null&&!['string','boolean','number'].includes(typeof p.literal))fail('scalar literal required');}else if(keys==='each,fields'){if(typeof p.each!=='string'||!/^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*$/.test(p.each))fail('collection projection path');projection(p.fields,depth+1);}else if(keys==='fields')projection(p.fields,depth+1);else fail('unsupported projection primitive');}}
export function validateTechnicalApplicationInputs(raw:unknown,contract:any){
 const candidate=captureJson(raw) as any;if(serviceInputFamilies.has(candidate?.family))return validateServiceApplicationInputs(candidate,contract);if(knowledgeFamilies.has(candidate?.family))return validateKnowledgeInputs(candidate,contract);
 const v=closed(captureJson(raw),['family','decisionRole','preferenceRole','admission','sources','layout','providerProfile','types','projections']);
 if(contract?.schema!=='craft.application-input-contract/v1'||contract.family!==v.family||!label(v.family)||!symbol(v.decisionRole)||!symbol(v.preferenceRole)||v.decisionRole===v.preferenceRole||v.admission!=='PreparedBeforeDispatch'||!['EntryModules','ServiceAssembly'].includes(v.layout)||!label(v.providerProfile))fail('supported family and original layout required');
 closed(v.types,['request','modelInput','proposal','decision']);if(!Object.values(v.types).every(symbol))fail('nominal type symbols required');
 const domain=v.family==='crm-contact-enrichment/domain-v1';
 closed(v.projections,domain?['modelInput','review','businessProposal','businessApproval','reviewEnvelope']:['modelInput','review']);
 for(const p of Object.values(v.projections))projection(p);
 if(domain){
  // This finite family's business approval is a view of the genuine selected
  // record, never a profile constant that manufactures a business decision.
  if(JSON.stringify(v.projections.businessApproval)!==JSON.stringify({approved:{from:'sources.approval.json.approved'}}))fail('domain approval must project the original selected approval decision');
  const proposal=v.projections.businessProposal;
  if(Object.keys(proposal).sort().join(',')!=='evidenceIds,industry'||proposal.industry?.from!=='proposal.industry'||proposal.evidenceIds?.from!=='proposal.evidenceIds')fail('domain proposal must project the original candidate fields');
 }
 const ownerOnly=['sourceCurrent','releaseAllowed','manifestDigest','inputDigest','outputDigest','subjectId','sourceVersion','policyVersion','recipientId','principal','now','attempt','approval','proposal'];for(const field of domain?['subjectId','approval','proposal']:ownerOnly)if(Object.hasOwn(v.projections.review,field))fail('original owner supplies '+field);
 const expected=new Set(['Facts','Evidence','Preference','Approval']);if(!Array.isArray(v.sources)||v.sources.length!==4)fail('four source roles required');const prefixes=new Set<string>();for(const s of v.sources){closed(s,['role','kind','contract','disclose','minimumOrdinal','prefix']);if(!expected.delete(s.role)||!['Document','ProtectedQuery'].includes(s.kind)||!label(s.contract)||typeof s.disclose!=='boolean'||typeof s.prefix!=='string'||!/^[a-z][a-z0-9-]{0,63}-$/.test(s.prefix)||prefixes.has(s.prefix)||!['1','2',1,2].includes(s.minimumOrdinal))fail('finite distinct source roles required');prefixes.add(s.prefix);if(s.kind!==(s.role==='Preference'?'ProtectedQuery':'Document'))fail('unsupported source owner');if(['Approval','Preference'].includes(s.role)&&s.disclose!==false||['Facts','Evidence','Approval'].includes(s.role)&&Number(s.minimumOrdinal)!==1)fail('existing gateway control/source stages');}
 const disclosed=new Set(v.sources.filter((s:any)=>s.disclose).map((s:any)=>({Facts:'facts',Evidence:'evidence',Preference:'preferences',Approval:'approval'} as any)[s.role]));
 const modelPaths=(value:any)=>{for(const p of Object.values(value) as any[]){for(const key of ['from','each'])if(p[key]!==undefined){const ref=p[key] as string;if(ref==='id'||ref.startsWith('item.'))continue;if(ref.startsWith('facts.')&&disclosed.has('facts'))continue;const source=/^sources\.([A-Za-z_][A-Za-z0-9_]*)\./.exec(ref);if(!source||!disclosed.has(source[1]))fail('model input cannot disclose private/owner source '+ref);}if(p.fields)modelPaths(p.fields);}};modelPaths(v.projections.modelInput);
 closed(contract.assets,['baseProfile','inferenceKernel','providerProfile','providerBinding','compositionProfile']);for(const k of ['baseProfile','inferenceKernel','providerProfile','compositionProfile'])if(!coreRelativePath(contract.assets[k]))fail('relative profile asset required');if(!symbol(contract.assets.providerBinding))fail('provider binding required');
 if(v.types.request!==contract.roles?.decision?.input||v.types.decision!==contract.roles?.decision?.output)fail('nominal profile type family mismatch');
 if(contract.roles?.decision?.targetRole!=='Operation'||contract.roles?.decision?.effect!=='pure'||contract.roles?.preference?.targetRole!=='Query'||contract.roles?.preference?.effect!=='read'||contract.callbacks!=='forbidden'||contract.unknownPrimitive!=='reject')fail('exact original business roles required');
 return coreFreeze(v);
}
export function resolveTechnicalApplicationInputRoles(options:{sourceOwner:ReturnType<typeof createTechnicalProfileSourceOwner>;sourceHandle:CheckedTechnicalProfileSource;businessSourcePath:string;components:{sameModule:readonly string[];entryAccess:readonly string[];presentation:readonly string[]};roles:Readonly<Record<string,string>>}){
 assertTechnicalProfileSourceOwner(options.sourceOwner);const inspected=options.sourceOwner.inspect(options.sourceHandle);if(inspected.target_consumer!==APPLICATION_INPUTS_CONSUMER)fail('genuine application-input source selection required');const input=inspected.topology as any;
 const components=closed(options.components,['sameModule','entryAccess','presentation']);for(const files of Object.values(components) as any[])if(!Array.isArray(files)||files.length>8||files.some((f:any)=>typeof f!=='string'||!path.isAbsolute(f)))fail('bounded absolute source components required');
 const files=[options.businessSourcePath,...components.sameModule,...components.entryAccess,...components.presentation];if(new Set(files).size!==files.length)fail('duplicate source classification');const captured=files.map(f=>readCorePhysicalFile(f)),modules=captured.map((f,i)=>reconstructCoreCommerceModule(f.text,'role-source/'+i+'/'+path.basename(f.file.path))),business=modules[0]!;if(components.sameModule.some((_:any,i:number)=>modules[i+1]!.module!==business.module))fail('same-module domain additions required');
 const declarations=modules.flatMap(m=>m.declarations);const seen=new Set<string>();for(const d of declarations){if(seen.has(d.id))fail('duplicate declaration');seen.add(d.id);}
 const choose=(role:string,surface:'Operation'|'Query')=>{const selector=options.roles[role];if(typeof selector!=='string')fail('exact business selector required for '+role);const entry=declarations.find(d=>d.id===selector&&d.surface==='Entry');if(!entry?.invokes)fail('selected business Entry required');const target=declarations.find(d=>d.id===entry.invokes&&d.surface===surface);if(!target)fail('selected Entry must invoke original '+surface);return {entry,target};};
 const service=serviceInputFamilies.has(input.family),knowledge=knowledgeFamilies.has(input.family)||service;
 if(Object.keys(options.roles).sort().join(',')!==(knowledge?[input.decisionRole]:[input.decisionRole,input.preferenceRole]).sort().join(','))fail('exact role assignment set required');const decision=choose(input.decisionRole,'Operation'),preference=knowledge?null:choose(input.preferenceRole,'Query');if(decision.target.module!==business.module||preference&&preference.target.module!==business.module)fail('business target modules must resolve to original business closure');
 const nominal=(t:CoreCommerceType|null,module:string,name:string)=>t?.kind==='named'&&(t.name.includes('.')?t.name:module+'.'+t.name)===business.module+'.'+name;
 if(decision.target.parameters.length!==1||!nominal(decision.target.parameters[0]!.type,decision.target.module,input.types.request)||!nominal(decision.target.result,decision.target.module,input.types.decision))fail('nominal decision input/output family mismatch');
 if(preference){const pr=preference.target.result;if(preference.target.parameters.length!==1||preference.target.parameters[0]!.name!=='contactId'||preference.target.parameters[0]!.type.kind!=='UInt64'||pr?.kind!=='optional'||!nominal(pr.value,preference.target.module,'ContactPreferenceSnapshot'))fail('nominal preference Query family mismatch');}
 for(const name of Object.values(input.types) as string[])if(!declarations.some(d=>d.module===business.module&&d.name===name&&d.surface==='ValueObject'))fail('original nominal business DTO required '+name);
 if(preference){const preferenceType=declarations.find(d=>d.id===business.module+'.ContactPreferenceSnapshot');for(const [field,kind]of [['contactId','UInt64'],['version','UInt64'],['allowed','Bool']])if(!preferenceType?.fields.some(f=>f.name===field&&f.type.kind===kind))fail('original typed preference field required '+field);}
 let continuationRule:string|undefined;
 if(knowledge){
  if(decision.target.contexts.length)fail('knowledge decision must have no hidden context inputs');
  for(const kind of ['transaction','mutation','read-statement','call-statement'])if(coreSourceDescendants(decision.target.syntax,kind).length)fail('knowledge decision must retain its original pure operation role');
  if(service){
   for(const name of [input.configuration.effectOperation,input.configuration.draftOperation,input.configuration.observationOperation].filter(Boolean)){const op=declarations.find(d=>d.id===business.module+'.'+name&&d.surface==='Operation');if(!op||op.contexts.length||op.parameters.length!==1)fail('original service pure operation required '+name);for(const kind of ['transaction','mutation','read-statement','call-statement'])if(coreSourceDescendants(op.syntax,kind).length)fail('original service operation must remain pure '+name);if(name===input.configuration.observationOperation&&(!nominal(op.parameters[0]!.type,op.module,'MetricsObservationRequest')||!nominal(op.result,op.module,'CampaignMetrics')))fail('original service observation nominal role');if(name!==input.configuration.observationOperation&&(!nominal(op.parameters[0]!.type,op.module,input.types.request)||!nominal(op.result,op.module,input.types.decision)))fail('nominal service operation role '+name);}
   if(input.configuration.continuationRule){const rule=declarations.find(d=>d.id===business.module+'.'+input.configuration.continuationRule&&d.surface==='Rule');if(!rule||rule.parameters.length!==1||!nominal(rule.parameters[0]!.type,rule.module,input.types.decision)||rule.result?.kind!=='Bool')fail('original service continuation Rule required');continuationRule=rule.id;}
  }
  if(input.family==='knowledge-ingestion/domain-v1'){
   const rule=declarations.find(d=>d.id===business.module+'.CanActivate'&&d.surface==='Rule');if(!rule||rule.parameters.length!==1||!nominal(rule.parameters[0]!.type,rule.module,input.types.decision)||rule.result?.kind!=='Bool'||rule.contexts.length)fail('original CanActivate Decision-to-Bool Rule required');continuationRule=rule.id;
  }
 }
 // Export source-derived Query field evidence without tightening the legacy
 // standalone three-field preference contract. Composed consumers must check
 // their own additional fields against this actual original declaration.
 const preferenceContract=preference?(()=>{const snapshot=declarations.find(d=>d.id===business.module+'.ContactPreferenceSnapshot')!;
  const wireKind=(type:CoreCommerceType,module:string):string=>{if(type.kind!=='named')return type.kind;const id=type.name.includes('.')?type.name:module+'.'+type.name,decl=declarations.find(d=>d.id===id);if(!decl?.refinement)return 'named';const tokens=coreSourceTokens(decl.syntax).filter(t=>!t.layout).map(t=>t.token),at=tokens.indexOf('carrier');return at>=0&&['String','UInt64','Bool'].includes(tokens[at+1]??'')?tokens[at+1]!:'named';};
  return coreFreeze({schema:'craft.application-preference-contract/v1',entry:preference.entry.id,query:preference.target.id,result:snapshot.id,fields:snapshot.fields.map(field=>({name:field.name,type:field.type,wire_kind:wireKind(field.type,snapshot.module)}))});})():undefined;
 const snapshots=captured.map(f=>({path:f.file.path,sha256:f.file.sha256}));const current=()=>{options.sourceOwner.assertCurrent(options.sourceHandle);for(const f of captured)if(readCorePhysicalFile(f.file.path).fingerprint!==f.fingerprint)fail('business source changed');};current();
 const entryIndex=modules.findIndex(m=>m.declarations.some(d=>d.id===decision.entry.id));const entryFile=captured[entryIndex]!.file.path;
 return Object.freeze({module:business.module,operation:decision.target.name,entry:decision.entry.id,entrySourcePath:entryFile,types:input.types,...(preference?{preferenceEntry:preference.entry.id,preferenceContract}:{}),...(knowledge?{family:input.family}:{}),...(continuationRule?{continuationRule}:{}),sourcePins:coreFreeze(snapshots),role_fingerprint:dataDigest(service?{decision:{id:decision.target.id,parameters:decision.target.parameters,result:decision.target.result},continuationRule:continuationRule??null,files:snapshots}:knowledge?{decision:decision.target,continuationRule:continuationRule??null,files:snapshots}:{decision:decision.target,preference:preference!.target,files:snapshots}),assertCurrent:current,qualification:'source-role-precheck; original application semantic checking required before generation/runtime'});
}
