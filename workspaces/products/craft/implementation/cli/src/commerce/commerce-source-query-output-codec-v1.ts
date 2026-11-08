/** Generated native output codec bound to one checked Query result type.
 * Open Questions: docs/COMMERCE-SQLITE-FAMILY-V1.md. */
import {stripTypeScriptTypes} from 'node:module';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {generateCommerceValueCodecBundle} from './commerce-value-codec-generation.js';
import {assertCoreCommerceStageSourceOwner,type CoreCommerceStageSourceOwner} from './commerce-core-stage-owner.js';
import {assertCommerceComputationDomainOwner,type CommerceComputationDomainOwner,type CommerceComputationDomainHandle} from './commerce-computation-domain.js';
import {assertCommerceLocalPlanOwnerV1,type CommerceLocalPlanOwnerV1,type CommerceLocalReadHandleV1} from './commerce-local-plan-owner-v1.js';
import type {CommerceSourceHandle} from './commerce-stages-v1.js';
import type {CommerceNativeValue} from './commerce-native-v1.js';

const ext=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,['commerce-value-codec-generation'+ext,'commerce-core-stage-owner'+ext,'commerce-computation-domain'+ext,'commerce-local-plan-owner-v1'+ext]);
export class CommerceSourceQueryCodecErrorV1 extends Error {constructor(readonly code:string){super(code);this.name='CommerceSourceQueryCodecErrorV1';}}
const bad=(code:string):never=>{throw new CommerceSourceQueryCodecErrorV1(code);};
export interface CommerceSourceQueryOutputCodecV1 {
 readonly query:string;
 readonly source_capture_sha256:string;
 readonly plan_sha256:string;
 copy(value:CommerceNativeValue):CommerceNativeValue;
 assertCurrent():void;
 dispose():void;
}
const owners=new WeakSet<object>();
export function assertCommerceSourceQueryOutputCodecV1(owner:CommerceSourceQueryOutputCodecV1):void {if(!owner||typeof owner!=='object'||!owners.has(owner))bad('ForeignOwner');owner.assertCurrent();}
export async function createCommerceSourceQueryOutputCodecV1(stage:CoreCommerceStageSourceOwner,source:CommerceSourceHandle,domain:CommerceComputationDomainOwner,baseline:CommerceComputationDomainHandle,plans:CommerceLocalPlanOwnerV1,read:CommerceLocalReadHandleV1):Promise<CommerceSourceQueryOutputCodecV1> {
 assertCoreCommerceStageSourceOwner(stage);assertCommerceComputationDomainOwner(domain);assertCommerceLocalPlanOwnerV1(plans);pin.assertCurrent();
 const view=plans.inspectRead(read),checked=domain.inspect(baseline),captured=stage.inspect(source);
 if(view.plan.kind!=='local'||view.source_capture_sha256!==captured.source_sha256||checked.source_capture_sha256!==captured.source_sha256)bad('ForeignOwner');
 const bundle=generateCommerceValueCodecBundle(stage,source,domain,baseline,[view.plan.output]);
 const values=bundle.files.find(f=>f.path==='commerce-domain-values.ts')?.text,codec=bundle.files.find(f=>f.path==='values-and-codecs.ts')?.text;
 if(!values||!codec)return bad('InvalidContract');
 const url=(text:string)=>'data:text/javascript;base64,'+Buffer.from(stripTypeScriptTypes(text)).toString('base64');
 const needle="'./commerce-domain-values.js'";
 if(!codec.includes(needle))bad('InvalidContract');
 const runtime=await import(url(codec.replace(needle,JSON.stringify(url(values)))));
 const generated=runtime.createCommerceValueCodecs();
 const schema=generated.checkCommerceSchema({...checked.contract.values,root:view.plan.output});
 if(!schema.ok)bad('UnsupportedOutputType');
 let disposed=false;
 const current=()=>{if(disposed)bad('DisposedOwner');pin.assertCurrent();stage.assertCurrent(source);domain.assertCurrent(baseline);plans.assertReadCurrent(read);const actual=plans.inspectRead(read);if(actual.query!==view.query||actual.plan_sha256!==view.plan_sha256||actual.source_capture_sha256!==view.source_capture_sha256)bad('StaleOwner');};
 const owner:CommerceSourceQueryOutputCodecV1=Object.freeze({query:view.query,source_capture_sha256:view.source_capture_sha256,plan_sha256:view.plan_sha256,copy(value:CommerceNativeValue){current();const copied=generated.copyCommerceValue(schema.value,value);if(!copied.ok)bad('InvalidQueryOutput');return copied.value as CommerceNativeValue;},assertCurrent:current,dispose(){disposed=true;}});
 owners.add(owner);current();return owner;
}
