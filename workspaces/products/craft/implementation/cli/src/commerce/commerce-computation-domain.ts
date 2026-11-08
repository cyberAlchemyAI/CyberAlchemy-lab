/** Genuine original v2 domain environment custody; no runtime owner is minted.
 * Open Questions: docs/COMMERCE-COMPUTATION-V2.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {dataDigest,captureJson} from '../profile-engine/contracts.js';
import {assertCoreCommerceSourceOwner} from './commerce-core-source-owner.js';
import {assertCoreCommerceSemanticOwner} from './commerce-core-semantic-owner.js';
import {createCoreValueTypes} from './commerce-core-types.js';
import {createCoreContextCatalog} from './commerce-core-context.js';
import {checkCoreCommerceComputationProposal} from './commerce-core-pure-contract.js';
import {coreFreeze,coreSourceFail as fail} from './commerce-core-syntax.js';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {assertCoreCommerceStageSourceOwner,createCoreCommerceSemanticStageComponent,type CoreCommerceStageSourceOwner} from './commerce-core-stage-owner.js';
import {deriveCommerceComputationEnvironment,type CommerceComputationEnvironment} from './commerce-computation-environment.js';
import type {CommerceSourceHandle} from './commerce-stages-v1.js';
import type {ComputationContractV1,SourceIdentityV1,RoleSelectorV1,SourceSpanV1} from './commerce-data-v1.js';
const ext=path.extname(fileURLToPath(import.meta.url)),pin=pinCoreImplementation(import.meta.url,['commerce-computation-environment'+ext,'commerce-core-stage-owner'+ext,'commerce-core-physical'+ext,'../profile-engine/contracts'+ext]);
const purePin=pinCoreImplementation(import.meta.url,['commerce-core-source-owner'+ext,'commerce-core-semantic-owner'+ext,'commerce-core-types'+ext,'commerce-core-context'+ext,'commerce-core-pure-contract'+ext,'commerce-computation-environment'+ext]);
const where={path:'application.alch',start:0,end:0};
export interface CommerceComputationDomainHandle {readonly kind:'original-commerce-computation-domain/v2-candidate'}
export interface CommerceComputationDomainInspection {
 readonly kind:'commerce-computation-domain-inspection/v2-candidate';readonly source:SourceIdentityV1;readonly source_capture_sha256:string;readonly code_epoch_sha256:string;
 readonly contract:ComputationContractV1;readonly contract_sha256:string;readonly environment:CommerceComputationEnvironment;
 readonly symbols:readonly {readonly selector:RoleSelectorV1;readonly source:SourceIdentityV1;readonly span:SourceSpanV1}[];
 readonly qualification:'original-source-checked-computation-domain-only;emitter-evaluator-native-and-call-runtime-not-established';readonly authority_effect:'none';
}
export interface CommerceComputationDomainOwner {check(contract:ComputationContractV1):CommerceComputationDomainHandle;inspect(handle:CommerceComputationDomainHandle):CommerceComputationDomainInspection;assertCurrent(handle:CommerceComputationDomainHandle):void;dispose(handle:CommerceComputationDomainHandle):void}
const registered=new WeakSet<object>();
export function assertCommerceComputationDomainOwner(owner:CommerceComputationDomainOwner):void {if(!owner||typeof owner!=='object'||!registered.has(owner))fail('ForeignOwner',where,'original commerce computation-domain owner required');}
export function createCommerceComputationDomainOwner(stage:CoreCommerceStageSourceOwner,source:CommerceSourceHandle):CommerceComputationDomainOwner {
 assertCoreCommerceStageSourceOwner(stage);stage.assertCurrent(source);pin.assertCurrent();const component=createCoreCommerceSemanticStageComponent(stage,source),owned=new WeakMap<object,{inspection:CommerceComputationDomainInspection;disposed:boolean}>();
 const current=(handle:CommerceComputationDomainHandle)=>{const row=handle&&typeof handle==='object'?owned.get(handle):undefined;if(!row)fail('ForeignOwner',where,'original computation-domain handle from this exact factory required');if(row.disposed)fail('DisposedOwner',where,'computation domain disposed');pin.assertCurrent();stage.assertCurrent(source);return row;};
 const owner:CommerceComputationDomainOwner=Object.freeze({check(proposed:ComputationContractV1){
  pin.assertCurrent();stage.assertCurrent(source);const result=component.checkComputation(proposed);if(!result.ok){const d=result.diagnostics[0]!;fail(d.code,d,d.message);}const contract=result.value,environment=deriveCommerceComputationEnvironment(contract),inspection=stage.inspect(source);
  const modules=stage.moduleContracts(source),module=modules.find(m=>m.declarations.some(d=>d.selector.module+'.'+d.selector.name===contract.source_node));if(!module)fail('UnknownReference',where,'computation must belong to its original captured module');
  const names=new Set([...contract.functions,...contract.values.records,...contract.values.enums,...contract.values.refinements].map(d=>d.name)),symbols=modules.flatMap(m=>m.declarations.filter(d=>names.has(d.selector.module+'.'+d.selector.name)).map(d=>({selector:d.selector,source:m.source,span:d.span})));
  if(symbols.length!==names.size)fail('MissingMapping',where,'every computation function/value declaration needs its actual source identity and span');
  const value:CommerceComputationDomainInspection=coreFreeze({kind:'commerce-computation-domain-inspection/v2-candidate',source:module.source,source_capture_sha256:inspection.source_sha256,code_epoch_sha256:pin.sha256,contract,contract_sha256:dataDigest(contract),environment,symbols,qualification:'original-source-checked-computation-domain-only;emitter-evaluator-native-and-call-runtime-not-established',authority_effect:'none'});
  const handle=Object.freeze({kind:'original-commerce-computation-domain/v2-candidate' as const});owned.set(handle,{inspection:value,disposed:false});current(handle);return handle;
 },inspect(handle:CommerceComputationDomainHandle){return current(handle).inspection;},assertCurrent(handle:CommerceComputationDomainHandle){current(handle);},dispose(handle:CommerceComputationDomainHandle){current(handle).disposed=true;}});registered.add(owner);return owner;
}

/** Pure-only source adapter. Unlike the full stage adapter this requires no
 * invented service, entry, Auth or application-runtime ownership. Limits are
 * reconstructed from the original captured source reference, never the caller.
 * Existing v2 computation data and native emitter semantics are unchanged. */
export function createOriginalPureComputationDomainOwner(
 sources: import('./commerce-core-source-owner.js').CoreCommerceSourceOwner,
 source: import('./commerce-core-source-owner.js').CoreCommerceSourceCapture,
 semantics: import('./commerce-core-semantic-owner.js').CoreCommerceSemanticOwner,
 semantic: import('./commerce-core-semantic-owner.js').CoreCommerceSemanticCapture,
):CommerceComputationDomainOwner {
 assertCoreCommerceSourceOwner(sources);assertCoreCommerceSemanticOwner(semantics);semantics.assertSource(semantic,source);purePin.assertCurrent();
 const currentSource=()=>{purePin.assertCurrent();sources.assertCurrent(source);semantics.assertSource(semantic,source);};
 const owned=new WeakMap<object,{inspection:CommerceComputationDomainInspection;disposed:boolean}>();
 const current=(h:CommerceComputationDomainHandle)=>{const row=h&&typeof h==='object'?owned.get(h):undefined;if(!row)fail('ForeignOwner',where,'original pure computation handle from this factory required');if(row.disposed)fail('DisposedOwner',where,'pure computation disposed');currentSource();return row;};
 const owner:CommerceComputationDomainOwner=Object.freeze({check(proposal:ComputationContractV1){
  currentSource();const captured=sources.inspect(source),types=createCoreValueTypes(captured.reconstruction),app=[...types.declarations.values()].find(d=>d.interface_kind==='application-composition')!;
  const bounds=createCoreContextCatalog(types,captured.files.filter(f=>f.path.endsWith('.json'))).asset(app,['computation-bounds']);
  const raw=bounds?.value as any;
  if(!raw||raw.schema_version!=='craft.commerce-compute-bounds/v1-candidate'||raw.computation?.required_schema_version!=='domainspec.iteration-expression/v2-candidate'||raw.computation?.required_semantics_revision!=='ordered-metered-commerce-v2-candidate')fail('MissingMapping',where,'exact original source computation bounds required');
  const p=captureJson(proposal) as unknown as ComputationContractV1;
  if(typeof p?.source_node!=='string')fail('InvalidContract',where,'exact source selector required');
  const paths=new Set(captured.reconstruction.modules.map(m=>m.path)),texts=captured.files.filter(f=>paths.has(f.path));
  const contract=checkCoreCommerceComputationProposal(texts,p.source_node,raw.computation.limits,p),environment=deriveCommerceComputationEnvironment(contract);
  const m=captured.reconstruction.modules.find(m=>m.declarations.some(d=>d.id===contract.source_node));if(!m)fail('UnknownReference',where,'source declaration absent');
  const identity=(m:typeof captured.reconstruction.modules[number]):SourceIdentityV1=>({module:m.module,version:1,artifact:{path:m.path,sha256:m.sha256,bytes:m.bytes}});
  const names=new Set([...contract.functions,...contract.values.records,...contract.values.enums,...contract.values.refinements].map(d=>d.name));
  const symbols=captured.reconstruction.modules.flatMap(m=>m.declarations.filter(d=>names.has(d.id)).map(d=>({selector:{module:m.module,role:d.meta_type!,name:d.name},source:identity(m),span:{path:m.path,start:d.syntax.start,end:d.syntax.end}})));
  if(symbols.length!==names.size)fail('MissingMapping',where,'every pure declaration needs an original source span');
  const inspection:CommerceComputationDomainInspection=coreFreeze({kind:'commerce-computation-domain-inspection/v2-candidate',source:identity(m),source_capture_sha256:captured.capture_sha256,code_epoch_sha256:purePin.sha256,contract,contract_sha256:dataDigest(contract),environment,symbols,qualification:'original-source-checked-computation-domain-only;emitter-evaluator-native-and-call-runtime-not-established',authority_effect:'none'});
  const h=Object.freeze({kind:'original-commerce-computation-domain/v2-candidate' as const});owned.set(h,{inspection,disposed:false});current(h);return h;
 },inspect(h:CommerceComputationDomainHandle){return current(h).inspection;},assertCurrent(h:CommerceComputationDomainHandle){current(h);},dispose(h:CommerceComputationDomainHandle){current(h).disposed=true;}});
 registered.add(owner);return owner;
}

/** Original zero-effect Operation domain. Lazy adapter loading preserves the
 * independent legacy pure-domain package closure. No caller-supplied AST or
 * claimed semantic graph can acquire registered executable custody. */
export async function createOriginalPureOperationDomainOwner(
 sources: import('./commerce-core-source-owner.js').CoreCommerceSourceOwner,
 source: import('./commerce-core-source-owner.js').CoreCommerceSourceCapture,
 semantics: import('./commerce-core-semantic-owner.js').CoreCommerceSemanticOwner,
 semantic: import('./commerce-core-semantic-owner.js').CoreCommerceSemanticCapture,
 mapping=false,
 calculations=false,
):Promise<CommerceComputationDomainOwner>{
 assertCoreCommerceSourceOwner(sources);assertCoreCommerceSemanticOwner(semantics);semantics.assertSource(semantic,source);
 const adapter=await import('../generic/pure-operation.js');
 const currentSource=()=>{purePin.assertCurrent();adapter.pureOperationPin.assertCurrent();sources.assertCurrent(source);semantics.assertSource(semantic,source);};currentSource();
 const owned=new WeakMap<object,{inspection:CommerceComputationDomainInspection;disposed:boolean}>();
 const current=(h:CommerceComputationDomainHandle)=>{const r=h&&typeof h==='object'?owned.get(h):undefined;if(!r)fail('ForeignOwner',where,'original pure Operation domain handle required');if(r.disposed)fail('DisposedOwner',where,'pure Operation domain disposed');currentSource();return r;};
 const owner:CommerceComputationDomainOwner=Object.freeze({check(proposal:ComputationContractV1){
  currentSource();const captured=sources.inspect(source),types=createCoreValueTypes(captured.reconstruction),app=[...types.declarations.values()].find(d=>d.interface_kind==='application-composition')!;
  const bounds=createCoreContextCatalog(types,captured.files.filter(f=>f.path.endsWith('.json'))).asset(app,['computation-bounds']),raw=bounds?.value as any;
  if(!raw||raw.schema_version!=='craft.commerce-compute-bounds/v1-candidate'||raw.computation?.required_schema_version!=='domainspec.iteration-expression/v2-candidate'||raw.computation?.required_semantics_revision!=='ordered-metered-commerce-v2-candidate')fail('MissingMapping',where,'exact original source computation bounds required');
  const p=captureJson(proposal) as unknown as ComputationContractV1;if(typeof p?.source_node!=='string')fail('InvalidContract',where,'exact Operation selector required');
  const paths=new Set(captured.reconstruction.modules.map(m=>m.path)),texts=captured.files.filter(f=>paths.has(f.path)),assets=captured.files.filter(f=>f.path.endsWith('.json'));
  const {contract,derivation}=adapter.createPureOperationComputation(texts,assets,p.source_node,raw.computation.limits,mapping,calculations);
  if(dataDigest(p)!==dataDigest(contract))fail('InvalidContract',where,'Operation computation differs from fresh original EffectPlan lowering');
  const environment=deriveCommerceComputationEnvironment(contract),m=captured.reconstruction.modules.find(m=>m.declarations.some(d=>d.id===contract.source_node&&d.surface==='Operation'));
  if(!m)fail('UnknownReference',where,'actual Operation source declaration required');
  const identity=(m:typeof captured.reconstruction.modules[number]):SourceIdentityV1=>({module:m.module,version:1,artifact:{path:m.path,sha256:m.sha256,bytes:m.bytes}});
  const technical=new Set(derivation.internal_types.map(t=>t.name)),names=new Set([...contract.functions,...contract.values.records,...contract.values.enums,...contract.values.refinements].map(d=>d.name).filter(name=>!technical.has(name)));names.add(contract.source_node);
  const symbols=captured.reconstruction.modules.flatMap(m=>m.declarations.filter(d=>names.has(d.id)).map(d=>({selector:{module:m.module,role:d.meta_type!,name:d.name},source:identity(m),span:{path:m.path,start:d.syntax.start,end:d.syntax.end}})));
  if(symbols.length!==names.size)fail('MissingMapping',where,'every original pure/Operation declaration requires exact source provenance');
  const operation=symbols.find(s=>s.selector.module+'.'+s.selector.name===contract.source_node)!;
  const inspection=coreFreeze({kind:'commerce-computation-domain-inspection/v2-candidate' as const,source:identity(m),source_capture_sha256:captured.capture_sha256,code_epoch_sha256:dataDigest({domain:purePin.sha256,adapter:adapter.pureOperationPin.sha256}),contract,contract_sha256:dataDigest(contract),environment,symbols,derivation:{...derivation,operation_source:operation},qualification:'original-source-checked-computation-domain-only;emitter-evaluator-native-and-call-runtime-not-established' as const,authority_effect:'none' as const});
  const h=Object.freeze({kind:'original-commerce-computation-domain/v2-candidate' as const});owned.set(h,{inspection,disposed:false});current(h);return h;
 },inspect(h:CommerceComputationDomainHandle){return current(h).inspection;},assertCurrent(h:CommerceComputationDomainHandle){current(h);},dispose(h:CommerceComputationDomainHandle){current(h).disposed=true;}});
 registered.add(owner);return owner;
}

/** Generic Mapping semantics are independently reconstructed inside original
 * registry custody. This additive owner never changes legacy record ordering. */
export async function createOriginalGenericMappingDomainOwner(
 sources: import('./commerce-core-source-owner.js').CoreCommerceSourceOwner,
 source: import('./commerce-core-source-owner.js').CoreCommerceSourceCapture,
 semantics: import('./commerce-core-semantic-owner.js').CoreCommerceSemanticOwner,
 semantic: import('./commerce-core-semantic-owner.js').CoreCommerceSemanticCapture,
 calculations=false,
):Promise<CommerceComputationDomainOwner>{
 assertCoreCommerceSourceOwner(sources);assertCoreCommerceSemanticOwner(semantics);semantics.assertSource(semantic,source);
 const adapter=await import('../generic/pure-mapping.js'),operations=await import('../generic/pure-operation.js');
 const currentSource=()=>{purePin.assertCurrent();adapter.pureMappingPin.assertCurrent();operations.pureOperationPin.assertCurrent();sources.assertCurrent(source);semantics.assertSource(semantic,source);};currentSource();
 const owned=new WeakMap<object,{inspection:CommerceComputationDomainInspection;disposed:boolean}>();
 const current=(h:CommerceComputationDomainHandle)=>{const r=h&&typeof h==='object'?owned.get(h):undefined;if(!r)fail('ForeignOwner',where,'original generic Mapping handle required');if(r.disposed)fail('DisposedOwner',where,'generic Mapping disposed');currentSource();return r;};
 const owner:CommerceComputationDomainOwner=Object.freeze({check(proposal:ComputationContractV1){
  currentSource();const captured=sources.inspect(source),types=createCoreValueTypes(captured.reconstruction),app=[...types.declarations.values()].find(d=>d.interface_kind==='application-composition')!;
  const bounds=createCoreContextCatalog(types,captured.files.filter(f=>f.path.endsWith('.json'))).asset(app,['computation-bounds']),raw=bounds?.value as any;
  if(!raw||raw.schema_version!=='craft.commerce-compute-bounds/v1-candidate'||raw.computation?.required_schema_version!=='domainspec.iteration-expression/v2-candidate'||raw.computation?.required_semantics_revision!=='ordered-metered-commerce-v2-candidate')fail('MissingMapping',where,'exact original source computation bounds required');
  const p=captureJson(proposal) as unknown as ComputationContractV1;if(typeof p?.source_node!=='string')fail('InvalidContract',where,'exact pure selector required');
  const paths=new Set(captured.reconstruction.modules.map(m=>m.path)),texts=captured.files.filter(f=>paths.has(f.path));
  const {contract,derivation}=adapter.createOrderedMappingComputation(texts,p.source_node,raw.computation.limits,calculations);
  const checked=semantics.inspect(semantic);for(const plan of checked.effects)operations.assertPureOperationPlan(plan,new Set(checked.pure.declarations.map(d=>d.name)),true,calculations);
  if(dataDigest(p)!==dataDigest(contract))fail('InvalidContract',where,'generic Mapping computation differs from fresh ordered source lowering');
  const environment=deriveCommerceComputationEnvironment(contract),m=captured.reconstruction.modules.find(m=>m.declarations.some(d=>d.id===contract.source_node));if(!m)fail('UnknownReference',where,'actual pure source declaration required');
  const identity=(m:typeof captured.reconstruction.modules[number]):SourceIdentityV1=>({module:m.module,version:1,artifact:{path:m.path,sha256:m.sha256,bytes:m.bytes}});
  const names=new Set([...contract.functions,...contract.values.records,...contract.values.enums,...contract.values.refinements].map(d=>d.name));
  const symbols=captured.reconstruction.modules.flatMap(m=>m.declarations.filter(d=>names.has(d.id)).map(d=>({selector:{module:m.module,role:d.meta_type!,name:d.name},source:identity(m),span:{path:m.path,start:d.syntax.start,end:d.syntax.end}})));
  if(symbols.length!==names.size)fail('MissingMapping',where,'every original Mapping/pure declaration requires source provenance');
  const inspection=coreFreeze({kind:'commerce-computation-domain-inspection/v2-candidate' as const,source:identity(m),source_capture_sha256:captured.capture_sha256,code_epoch_sha256:dataDigest({domain:purePin.sha256,adapter:adapter.pureMappingPin.sha256,operations:operations.pureOperationPin.sha256}),contract,contract_sha256:dataDigest(contract),environment,symbols,derivation,qualification:'original-source-checked-computation-domain-only;emitter-evaluator-native-and-call-runtime-not-established' as const,authority_effect:'none' as const});
  const h=Object.freeze({kind:'original-commerce-computation-domain/v2-candidate' as const});owned.set(h,{inspection,disposed:false});current(h);return h;
 },inspect(h:CommerceComputationDomainHandle){return current(h).inspection;},assertCurrent(h:CommerceComputationDomainHandle){current(h);},dispose(h:CommerceComputationDomainHandle){current(h).disposed=true;}});
 registered.add(owner);return owner;
}
