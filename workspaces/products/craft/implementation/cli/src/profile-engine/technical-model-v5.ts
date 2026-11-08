/** Genuine Core typed technical graph and compiled source Mapping custody.
 * Open Questions: docs/COMMERCE-PROFILE-FAMILY-V5.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {stripTypeScriptTypes} from 'node:module';
import {captureJson,dataDigest} from './contracts.js';
import {familyLoweringPolicyV5,parametersV5,type FamilyLoweringPolicyV5} from './contracts-v5.js';
import {coreFreeze,coreRelativePath,coreSourceFail as fail,coreSourceTokens,coreSourceChildren} from '../commerce/commerce-core-syntax.js';
import {pinCoreImplementation,readCorePhysicalFile,type CorePhysicalFile} from '../commerce/commerce-core-physical.js';
import {createCoreCommerceSourceOwner,parseCoreCommerceJson,type CoreCommerceSourceCapture} from '../commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from '../commerce/commerce-core-semantic-owner.js';
import {createCoreCommerceStageSourceOwner} from '../commerce/commerce-core-stage-owner.js';
import {checkCoreCommerceInterfaceSources} from '../commerce/commerce-core-interface-semantics.js';
import {createCoreValueTypes} from '../commerce/commerce-core-types.js';
import {createCoreContextCatalog} from '../commerce/commerce-core-context.js';
import {createCoreCommerceComputationContract} from '../commerce/commerce-core-pure-contract.js';
import {createCommerceComputationDomainOwner,type CommerceComputationDomainHandle} from '../commerce/commerce-computation-domain.js';
import {compileCommerceComputationTypeScript} from '../commerce/commerce-computation-native.js';
import {metaTypeIdForLabel} from '../meta-types/catalog.js';
import type {CommerceTechnicalModelHandle,CommerceSourceHandle} from '../commerce/commerce-stages-v1.js';
import type {ProfilePackageV1,SourceIdentityV1} from '../commerce/commerce-data-v1.js';
const ext=path.extname(fileURLToPath(import.meta.url)),pin=pinCoreImplementation(import.meta.url,['contracts-v5'+ext,'../commerce/commerce-core-source-owner'+ext,'../commerce/commerce-core-stage-owner'+ext,'../commerce/commerce-core-interface-semantics'+ext,'../commerce/commerce-core-types'+ext,'../commerce/commerce-core-context'+ext,'../commerce/commerce-core-pure-contract'+ext,'../commerce/commerce-computation-domain'+ext,'../commerce/commerce-computation-native'+ext,'../commerce/commerce-computation-kernel'+ext,'../commerce/commerce-computation-environment'+ext,'../meta-types/catalog'+ext,'../meta-types/frozen-catalog.generated'+ext]),where={path:'technical-model',start:0,end:0};
export interface TechnicalModelInspectionV5 {
 readonly kind:'core-checked-technical-model/v5-candidate';readonly source:SourceIdentityV1;readonly source_capture_sha256:string;
 readonly mapping:string;readonly graph:Readonly<{schema_version:'craft.core-typed-technical-graph/v1-candidate';nodes:readonly any[];edges:readonly {from:string;to:string;kind:string}[];technical_nodes:readonly string[];imports:readonly string[];authority_effect:'none'}>;
 readonly graph_sha256:string;readonly policy:FamilyLoweringPolicyV5;readonly policy_sha256:string;
 readonly family_contract:Readonly<Record<string,any>>;readonly native_contract:Readonly<Record<string,any>>;
 readonly values:ReturnType<ReturnType<typeof createCommerceComputationDomainOwner>['inspect']>['contract']['values'];
 readonly module_contracts:ReturnType<ReturnType<typeof createCoreCommerceStageSourceOwner>['moduleContracts']>;
 readonly compiled_mapping:ReturnType<typeof compileCommerceComputationTypeScript>;
 readonly qualification:'original-Core-source-and-typed-technical-graph;not-selected-profile-native-or-application';readonly authority_effect:'none';
}
export interface CommerceTechnicalModelOwnerV5 {
 checkTechnicalSource(root:string,relativePath:string):Promise<CommerceTechnicalModelHandle>;
 inspect(model:CommerceTechnicalModelHandle):TechnicalModelInspectionV5;
 evaluateSelection(model:CommerceTechnicalModelHandle,parameters:ProfilePackageV1['parameters']):Readonly<Record<string,unknown>>;
 assertCurrent(model:CommerceTechnicalModelHandle):void;dispose(model:CommerceTechnicalModelHandle):void;
}
const owners=new WeakSet<object>();
export function assertTechnicalModelOwnerV5(owner:CommerceTechnicalModelOwnerV5){if(!owner||typeof owner!=='object'||!owners.has(owner))fail('ForeignOwner',where,'original Core technical model factory required');}
export function createCommerceTechnicalModelOwnerV5(policyFile=fileURLToPath(new URL('../../profiles/commerce-local-v1-candidate/technical-contract.json',import.meta.url))):CommerceTechnicalModelOwnerV5 {
 pin.assertCurrent();const policyCapture=readCorePhysicalFile(policyFile),policy=familyLoweringPolicyV5(parseCoreCommerceJson(policyCapture.text,policyCapture.file.path)),sources=createCoreCommerceSourceOwner(),semantics=createCoreCommerceSemanticOwner(sources),stage=createCoreCommerceStageSourceOwner(sources,semantics);
 type State={capture:CoreCommerceSourceCapture;source:CommerceSourceHandle;domain:ReturnType<typeof createCommerceComputationDomainOwner>;handle:CommerceComputationDomainHandle;inspection:TechnicalModelInspectionV5;native:any;parameter:string;disposed:boolean};const owned=new WeakMap<object,State>();
 const current=(model:CommerceTechnicalModelHandle)=>{const s=model&&typeof model==='object'?owned.get(model):undefined;if(!s)fail('ForeignOwner',where,'original technical model from this exact factory required');if(s.disposed)fail('DisposedOwner',where,'technical model disposed');pin.assertCurrent();if(readCorePhysicalFile(policyFile).fingerprint!==policyCapture.fingerprint)fail('StaleOwner',where,'original technical lowering policy changed');sources.assertCurrent(s.capture);s.domain.assertCurrent(s.handle);return s;};
 const owner:CommerceTechnicalModelOwnerV5=Object.freeze({async checkTechnicalSource(root:string,relativePath:string){
  pin.assertCurrent();if(!coreRelativePath(relativePath))fail('InvalidContract',where,'exact relative technical source path required');const capture=sources.prepare(root),captured=sources.inspect(capture),source=await stage.prepare(root,'application.alch'),original=stage.inspect(source),application=original.application;
  if(captured.capture_sha256!==original.source_sha256||application.profile_source.artifact.path!==relativePath)fail('ForeignOwner',where,'technical source must be the actual captured application selection module');
  const modules=stage.moduleContracts(source),module=modules.find(m=>m.source.artifact.path===relativePath)!,syntax=captured.reconstruction.modules.find(m=>m.path===relativePath)!;const boundaries=syntax.declarations.filter(d=>d.interface_kind==='technical-profile-family');if(boundaries.length!==1)fail('InvalidContract',where,'one technical family Interface required');
  const boundary=boundaries[0]!;for(const [head,value]of [['callbacks','forbidden'],['unknown-primitive','reject'],['missing-producer','reject']]){const clauses=coreSourceChildren(boundary.syntax,'interface-clause').filter(n=>coreSourceTokens(n).filter(t=>!t.layout)[0]?.token===head);if(clauses.length!==1||coreSourceTokens(clauses[0]!).filter(t=>!t.layout).map(t=>t.token).join(' ')!==head+' '+value)fail('UnsupportedCapability',where,'technical family preserves explicit no-hook and missing-primitive rejection');}
  const types=createCoreValueTypes(captured.reconstruction),catalog=createCoreContextCatalog(types,captured.files.filter(f=>f.path.endsWith('.json'))),family=catalog.asset(boundary,['family-contract']),nativeContract=catalog.asset(boundary,['obligations']);if(!family||!nativeContract)fail('MissingMapping',where,'original captured family and native requirement contracts required');
  const sourcePaths=new Set(captured.reconstruction.modules.map(m=>m.path)),texts=captured.files.filter(f=>sourcePaths.has(f.path)),assets=captured.files.filter(f=>f.path.endsWith('.json')),contractAssets=catalog.asset(types.declarations.get(application.id)!,['computation-bounds']);const bounds=contractAssets?.value as any,limits=bounds?.computation?.limits;if(!limits)fail('MissingMapping',where,'original explicit native computation budgets required');
  const domain=createCommerceComputationDomainOwner(stage,source),handle=domain.check(createCoreCommerceComputationContract(texts,application.profile_mapping,limits)),checked=domain.inspect(handle),c=checked.contract,f=c.functions.find(f=>f.name===application.profile_mapping)!;if(f.kind!=='Mapping'||f.parameters.length!==1||f.result.kind!=='record')fail('UnsupportedCapability',where,'technical selection must be a checked pure one-input record Mapping');
  const interfaces=checkCoreCommerceInterfaceSources(texts,assets),symbols=new Map(modules.flatMap(m=>m.declarations.map(d=>[d.selector.module+'.'+d.selector.name,{...d,source:m.source}] as const))),definitions=new Map<string,any>();for(const d of [...c.values.records,...c.values.enums,...c.values.refinements,...c.functions])definitions.set(d.name,d);for(const d of interfaces)definitions.set(d.name,d);
  const nodes:any[]=[],edges:{from:string;to:string;kind:string}[]=[],seen=new Set<string>(),technical=module.declarations.map(d=>d.selector.module+'.'+d.selector.name);
  const add=(name:string)=>{if(seen.has(name))return;seen.add(name);const symbol=symbols.get(name),definition=definitions.get(name);if(!symbol||!definition)fail('UnknownReference',where,'every technical/imported graph node needs original checked semantics');const label=symbol.selector.role==='ValueObject'?'Value Object':symbol.selector.role==='StateMachine'?'State Machine':symbol.selector.role;nodes.push({id:name,selector:symbol.selector,meta_type_id:metaTypeIdForLabel(label),source:symbol.source,span:symbol.span,technical:technical.includes(name),definition});
   const refs=new Set<string>();const visit=(v:any)=>{if(!v||typeof v!=='object')return;if(['record','enum','refinement'].includes(v.kind)&&typeof v.name==='string')refs.add(v.name);if(v.kind==='variant')refs.add(v.enum_name);if(v.op==='call')refs.add(v.declaration);if(['record','enum_value'].includes(v.op))refs.add(v.type_name);for(const child of Object.values(v))if(child&&typeof child==='object')visit(child);};visit(definition);for(const to of refs){edges.push({from:name,to,kind:'typed-source-dependency'});add(to);}
  };technical.forEach(add);for(const imported of module.imports)for(const name of imported.names){const target=imported.module+'.'+name;add(target);edges.push({from:module.source.module,to:target,kind:'source-import'});}
  const graph=coreFreeze({schema_version:'craft.core-typed-technical-graph/v1-candidate' as const,nodes,edges,technical_nodes:technical,imports:module.imports.flatMap(m=>m.names.map(n=>m.module+'.'+n)),authority_effect:'none' as const}),compiled=compileCommerceComputationTypeScript(domain,handle),native=await import('data:text/javascript;base64,'+Buffer.from(stripTypeScriptTypes(compiled.source)).toString('base64'));
  const inspection:TechnicalModelInspectionV5=coreFreeze({kind:'core-checked-technical-model/v5-candidate',source:module.source,source_capture_sha256:original.source_sha256,mapping:application.profile_mapping,graph,graph_sha256:dataDigest(graph),policy,policy_sha256:policyCapture.file.sha256,family_contract:captureJson(family.value) as any,native_contract:captureJson(nativeContract.value) as any,values:c.values,module_contracts:modules,compiled_mapping:compiled,qualification:'original-Core-source-and-typed-technical-graph;not-selected-profile-native-or-application',authority_effect:'none'});
  // This cast types a newly minted token. Custody is the actual private entry,
  // original Core parents and compiled source; no JSON/legacy graph brand used.
  const model=Object.freeze({kind:'technical-model'}) as unknown as CommerceTechnicalModelHandle;owned.set(model,{capture,source,domain,handle,inspection,native,parameter:f.parameters[0]!.name,disposed:false});current(model);return model;
 },inspect(model:CommerceTechnicalModelHandle){return current(model).inspection;},evaluateSelection(model:CommerceTechnicalModelHandle,parameters:ProfilePackageV1['parameters']){const s=current(model),p=parametersV5(parameters),wire=new TextEncoder().encode(JSON.stringify({[s.parameter]:{...p,requestBytes:String(p.requestBytes),responseBytes:String(p.responseBytes),bodyTimeoutMs:String(p.bodyTimeoutMs)}})),result=s.native.evaluate(wire);if(!result.ok)fail(result.error.code,where,'actual technical Mapping evaluation failed');const output=JSON.parse(new TextDecoder().decode(result.wire));current(model);return coreFreeze(output);},assertCurrent(model:CommerceTechnicalModelHandle){current(model);},dispose(model:CommerceTechnicalModelHandle){const s=current(model);s.disposed=true;s.domain.dispose(s.handle);stage.dispose(s.source);sources.dispose(s.capture);}});owners.add(owner);return owner;
}
