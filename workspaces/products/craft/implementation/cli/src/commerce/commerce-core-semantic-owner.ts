/** Genuine original source-semantic custody across the wider commerce roles.
 * This is not a profile/native selection or application acceptance owner.
 * Open Questions: docs/COMMERCE-OWNERS.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze,coreSourceFail as fail,coreSourceChildren,coreSourceDescendants,coreSourceTokens,coreSourceText} from './commerce-core-syntax.js';
import {assertCoreCommerceSourceOwner,parseCoreCommerceJson,type CoreCommerceSourceOwner,type CoreCommerceSourceCapture} from './commerce-core-source-owner.js';
import {checkCoreCommercePureSources,type CorePureSemantics} from './commerce-core-pure.js';
import {createCoreCommerceReadContracts,createCoreCommerceEffectContracts,createCoreCommerceWorkflowContracts,createCoreCommerceEntryContracts} from './commerce-core-role-contracts.js';
import type {ReadPlanV1,EffectPlanV1,WorkflowContractV1,EntryContractV1} from './commerce-data-v1.js';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {checkCoreCommerceInterfaceSources,type CoreInterfaceSemantics} from './commerce-core-interface-semantics.js';
const extension=path.extname(fileURLToPath(import.meta.url));
const code=['source-owner','syntax','reconstruction','grammar','types','expression','pure','context','flow-expression','flow-evaluation','flow-query','flow-operation','flow-workflow','flow-entry','pure-contract','role-contracts','physical','interface-semantics'].map(n=>'commerce-core-'+n+extension);
const schemas=['commerce-values-v1','iteration-expression-v2','commerce-entry-v1','commerce-read-v1','commerce-effects-v1','commerce-workflow-v1','profile-package-v5','commerce-module-v1','commerce-application-v1'].map(n=>'../../contracts/'+n+'.schema.json');
const pin=pinCoreImplementation(import.meta.url,[...code,'commerce-policy-enforcement'+extension,'commerce-data-v1'+extension,'commerce-registry-v1'+extension,'../profile-engine/contracts'+extension,...schemas]);
export interface CoreCommerceSemanticCapture {readonly kind:'original-core-commerce-semantic-capture/v1-candidate'}
export interface CoreCommerceSemanticInspection {
 readonly kind:'core-commerce-semantic-inspection/v1-candidate';readonly application:string;readonly source_capture_sha256:string;readonly semantic_code_epoch_sha256:string;
 readonly canonicalization:'craft.commerce-source-executable-keysort/v1-candidate';readonly executable_sha256:string;readonly assurance_sha256:string;
 readonly pure:CorePureSemantics;readonly reads:readonly ReadPlanV1[];readonly effects:readonly EffectPlanV1[];readonly workflows:readonly WorkflowContractV1[];readonly entries:readonly EntryContractV1[];
 readonly interfaces:readonly CoreInterfaceSemantics[];
 readonly ownership:readonly {readonly declaration:string;readonly service:string|null;readonly category:string}[];
 readonly counts:Readonly<{modules:number;files:number;pure:number;values:number;queries:number;operations:number;workflows:number;entries:number;claims:number}>;
 readonly qualification:'original-source-semantics-only;profile-native-application-acceptance-not-established';readonly authority_effect:'none';
}
export interface CoreCommerceSemanticOwner {check(source:CoreCommerceSourceCapture):CoreCommerceSemanticCapture;inspect(handle:CoreCommerceSemanticCapture):CoreCommerceSemanticInspection;assertCurrent(handle:CoreCommerceSemanticCapture):void;assertSource(handle:CoreCommerceSemanticCapture,source:CoreCommerceSourceCapture):void;dispose(handle:CoreCommerceSemanticCapture):void}
const registry=new WeakSet<object>();
export function assertCoreCommerceSemanticOwner(owner:CoreCommerceSemanticOwner):void {if(!owner||typeof owner!=='object'||!registry.has(owner))fail('ForeignOwner',{path:'application.alch',start:0,end:0},'original Core semantic owner factory required');}
export function createCoreCommerceSemanticOwner(sourceOwner:CoreCommerceSourceOwner):CoreCommerceSemanticOwner {
 assertCoreCommerceSourceOwner(sourceOwner);pin.assertCurrent();const owned=new WeakMap<object,{source:CoreCommerceSourceCapture;inspection:CoreCommerceSemanticInspection;disposed:boolean}>();
 const state=(handle:CoreCommerceSemanticCapture)=>{const row=handle&&typeof handle==='object'?owned.get(handle):undefined;if(!row)fail('ForeignOwner',{path:'application.alch',start:0,end:0},'original semantic handle from this exact owner required');if(row.disposed)fail('DisposedOwner',{path:'application.alch',start:0,end:0},'semantic handle disposed');assertCoreCommerceSourceOwner(sourceOwner);pin.assertCurrent();sourceOwner.assertCurrent(row.source);return row;};
 const owner:CoreCommerceSemanticOwner=Object.freeze({check(source:CoreCommerceSourceCapture){
  pin.assertCurrent();const capture=sourceOwner.inspect(source),model=capture.reconstruction,paths=new Set(model.modules.map(m=>m.path)),sources=capture.files.filter(f=>paths.has(f.path)),assets=capture.files.filter(f=>f.path.endsWith('.json'));
  const pure=checkCoreCommercePureSources(sources),interfaceSemantics=checkCoreCommerceInterfaceSources(sources,assets),reads=createCoreCommerceReadContracts(sources,assets),effects=createCoreCommerceEffectContracts(sources,assets),workflows=createCoreCommerceWorkflowContracts(sources,assets),entries=createCoreCommerceEntryContracts(sources,assets);
  const root=model.modules.flatMap(m=>m.declarations).find(d=>d.interface_kind==='application-composition')!,claims=model.modules.flatMap(m=>m.declarations).filter(d=>d.surface==='FormalClaim');
  const reference=(modulePath:string,raw:string)=>{const file=raw.split('#')[0]!;return file.includes('/')?file:path.posix.join(path.posix.dirname(modulePath),file);};
  const claimFiles=new Set(claims.flatMap(d=>coreSourceDescendants(d.syntax,'reference').map(n=>reference(d.syntax.path,coreSourceText(n)))).filter(p=>capture.files.some(f=>f.path===p)));
  const identityFiles=new Set(coreSourceDescendants(root.syntax,'application-clause').filter(n=>coreSourceTokens(n).find(t=>!t.layout)?.token==='source-identities').map(n=>reference(root.syntax.path,coreSourceText(coreSourceChildren(n,'reference')[0]!))));
  const nonClaimReferences=new Set(model.modules.flatMap(m=>m.declarations.filter(d=>d.surface!=='FormalClaim').flatMap(d=>coreSourceDescendants(d.syntax,'reference').map(n=>reference(m.path,coreSourceText(n))))));
  const config=assets.filter(f=>!identityFiles.has(f.path)&&(!claimFiles.has(f.path)||nonClaimReferences.has(f.path))).map(f=>({path:f.path,value:parseCoreCommerceJson(f.text,f.path)}));
  const interfaces=model.modules.flatMap(m=>m.declarations.filter(d=>d.surface==='Interface').map(d=>{const captureClauses=d===root?coreSourceDescendants(d.syntax,'application-clause').filter(n=>['source','source-identities'].includes(coreSourceTokens(n).find(t=>!t.layout)?.token??'')):[];return {name:d.id,tokens:coreSourceTokens(d.syntax).filter(t=>!t.layout&&!captureClauses.some(n=>t.start>=n.start&&t.end<=n.end)).map(t=>t.token)};})).sort((a,b)=>a.name<b.name?-1:a.name>b.name?1:0);
  const roleSubjects={reads:reads.map(r=>({selector:r.query,sha256:dataDigest(r)})),effects:effects.map(r=>({selector:r.operation,sha256:dataDigest(r)})),workflows:workflows.map(r=>({selector:r.workflow,sha256:dataDigest(r)})),entries:entries.map(r=>({id:r.id,sha256:dataDigest(r)}))};
  const executable_sha256=dataDigest({application:root.id,pure:pure.pure_subject_sha256,roles:roleSubjects,interfaces,services:model.services,ownership:model.ownership.filter(o=>!claims.some(c=>c.id===o.declaration)),configuration:config});
  const assurance_sha256=dataDigest({source:model.optional_assurance_source_sha256,files:capture.files.filter(f=>claimFiles.has(f.path)).map(({path,sha256,bytes})=>({path,sha256,bytes}))});
  const inspection:CoreCommerceSemanticInspection=coreFreeze({kind:'core-commerce-semantic-inspection/v1-candidate',application:root.id,source_capture_sha256:capture.capture_sha256,semantic_code_epoch_sha256:pin.sha256,canonicalization:'craft.commerce-source-executable-keysort/v1-candidate',executable_sha256,assurance_sha256,pure,reads,effects,workflows,entries,interfaces:interfaceSemantics,ownership:model.ownership,counts:{modules:model.modules.length,files:capture.files.length,pure:pure.declarations.length,values:pure.value_declarations.length,queries:reads.length,operations:effects.length,workflows:workflows.length,entries:entries.length,claims:claims.length},qualification:'original-source-semantics-only;profile-native-application-acceptance-not-established',authority_effect:'none'});
  sourceOwner.assertCurrent(source);pin.assertCurrent();const handle=Object.freeze({kind:'original-core-commerce-semantic-capture/v1-candidate' as const});owned.set(handle,{source,inspection,disposed:false});state(handle);return handle;
 },inspect(handle:CoreCommerceSemanticCapture){return state(handle).inspection;},assertCurrent(handle:CoreCommerceSemanticCapture){state(handle);},assertSource(handle:CoreCommerceSemanticCapture,source:CoreCommerceSourceCapture){if(state(handle).source!==source)fail('ForeignOwner',{path:'application.alch',start:0,end:0},'exact original source capture required');},dispose(handle:CoreCommerceSemanticCapture){state(handle).disposed=true;}});
 registry.add(owner);return owner;
}
