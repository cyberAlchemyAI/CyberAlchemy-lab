/** Original generic checked-domain registry; inert ASTs cannot mint runtime custody.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {captureJson,dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze,coreSourceFail as fail} from '../commerce/commerce-core-syntax.js';
import {pinCoreImplementation} from '../commerce/commerce-core-physical.js';
import {assertCoreCommerceSourceOwner,type CoreCommerceSourceOwner,type CoreCommerceSourceCapture} from '../commerce/commerce-core-source-owner.js';
import {assertGenericSemanticOwner,genericSourceBounds,type GenericSemanticOwner,type GenericSemanticCapture,type GenericSemanticInspection} from './semantic-reconstruction.js';
import {createGenericSourceComputation,createGenericKeyedPureComputation,genericSourcePin} from './pure-source-stage.js';
import {deriveGenericComputationEnvironment} from '../commerce/commerce-computation-environment.js';
import type {GenericComputationContractV1} from './computation-data-v1.js';
import type {SourceIdentityV1} from '../commerce/commerce-data-v1.js';
const ext=path.extname(fileURLToPath(import.meta.url)),pin=pinCoreImplementation(import.meta.url,['semantic-reconstruction'+ext,'pure-source-stage'+ext,'../commerce/commerce-computation-environment'+ext]);
const at={path:'generic-domain',start:0,end:0};
export interface GenericComputationDomainHandle{readonly kind:'original-generic-computation-domain/v1-candidate'}
export type GenericComputationDomainInspection=ReturnType<typeof inspectDomain>;
export interface GenericComputationDomainOwner{check(proposal:GenericComputationContractV1):GenericComputationDomainHandle;inspect(handle:GenericComputationDomainHandle):GenericComputationDomainInspection;assertCurrent(handle:GenericComputationDomainHandle):void;dispose(handle:GenericComputationDomainHandle):void}
function inspectDomain(capture:ReturnType<CoreCommerceSourceOwner['inspect']>,proposal:GenericComputationContractV1,semantic:GenericSemanticInspection){
 const p=captureJson(proposal) as unknown as GenericComputationContractV1;if(p?.schema_version!=='craft.generic-computation/v1-candidate'||typeof p.source_node!=='string')fail('InvalidContract',at,'exact generic discriminator and source selector required');
 const paths=new Set(capture.reconstruction.modules.map(m=>m.path)),texts=capture.files.filter(f=>paths.has(f.path)),actual=(semantic.admission_mode==='keyed-query-entry'||semantic.admission_mode==='atomic-state-entry')?createGenericKeyedPureComputation(capture,p.source_node):createGenericSourceComputation(texts,p.source_node,genericSourceBounds(capture),semantic.admission_mode);if(actual.derivation.admission_capabilities_sha256!==semantic.admission_capabilities_sha256)fail('InvalidContract',at,'domain admission must match original semantic owner');if(dataDigest(p)!==dataDigest(actual.contract))fail('InvalidContract',at,'generic computation differs from independent original source reconstruction');
 const contract=actual.contract,environment=deriveGenericComputationEnvironment(contract),module=capture.reconstruction.modules.find(m=>m.declarations.some(d=>d.id===contract.source_node));if(!module)fail('UnknownReference',at,'original source selector required');
 const identity=(m:typeof module):SourceIdentityV1=>({module:m!.module,version:1,artifact:{path:m!.path,sha256:m!.sha256,bytes:m!.bytes}});
 const names=new Set([...contract.functions,...contract.values.records,...contract.values.enums,...contract.values.refinements].map(x=>x.name));names.add(contract.source_node);
 const symbols=capture.reconstruction.modules.flatMap(m=>m.declarations.filter(d=>names.has(d.id)).map(d=>({selector:{module:m.module,role:d.meta_type!,name:d.name},source:identity(m),span:{path:m.path,start:d.syntax.start,end:d.syntax.end}})));
 const internal=actual.derivation.operation?.internal_types??[];if(symbols.length+internal.length!==names.size)fail('MissingMapping',at,'all generic symbols need original spans or explicit technical Operation origin');
 return coreFreeze({kind:'generic-computation-domain-inspection/v1-candidate' as const,admission_mode:semantic.admission_mode,admission_capabilities_sha256:semantic.admission_capabilities_sha256,source:identity(module),source_capture_sha256:capture.capture_sha256,code_epoch_sha256:dataDigest({domain:pin.sha256,source:genericSourcePin.sha256}),contract,contract_sha256:dataDigest(contract),environment,symbols,derivation:actual.derivation,qualification:'original-generic-source-domain-only' as const,authority_effect:'none' as const});
}
const registry=new WeakSet<object>();
export function assertGenericComputationDomainOwner(owner:GenericComputationDomainOwner):void{if(!owner||typeof owner!=='object'||!registry.has(owner))fail('ForeignOwner',at,'original generic computation-domain owner required');}
export function createGenericComputationDomainOwner(sources:CoreCommerceSourceOwner,source:CoreCommerceSourceCapture,semantics:GenericSemanticOwner,semantic:GenericSemanticCapture):GenericComputationDomainOwner{
 const currentSource=()=>{pin.assertCurrent();genericSourcePin.assertCurrent();assertCoreCommerceSourceOwner(sources);assertGenericSemanticOwner(semantics);sources.assertCurrent(source);semantics.assertSource(semantic,source);};currentSource();
 const rows=new WeakMap<object,{inspection:GenericComputationDomainInspection;disposed:boolean}>();
 const current=(h:GenericComputationDomainHandle)=>{const r=h&&typeof h==='object'?rows.get(h):undefined;if(!r)fail('ForeignOwner',at,'exact registered generic domain handle required');if(r.disposed)fail('DisposedOwner',at,'generic domain disposed');currentSource();return r;};
 const owner:GenericComputationDomainOwner=Object.freeze({check(proposal:GenericComputationContractV1){currentSource();const inspection=inspectDomain(sources.inspect(source),proposal,semantics.inspect(semantic)),h=Object.freeze({kind:'original-generic-computation-domain/v1-candidate' as const});rows.set(h,{inspection,disposed:false});current(h);return h;},inspect(h:GenericComputationDomainHandle){return current(h).inspection;},assertCurrent(h:GenericComputationDomainHandle){current(h);},dispose(h:GenericComputationDomainHandle){current(h).disposed=true;}});registry.add(owner);return owner;
}
