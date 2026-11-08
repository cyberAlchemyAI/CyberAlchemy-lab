/** Original application/profile requirements custody before native resolution.
 * Open Questions: docs/COMMERCE-PROFILE-FAMILY-V5.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {coreFreeze,coreSourceFail as fail} from './commerce-core-syntax.js';
import {assertCoreCommerceSourceOwner,type CoreCommerceSourceOwner,type CoreCommerceSourceCapture} from './commerce-core-source-owner.js';
import {assertCoreCommerceSemanticOwner,type CoreCommerceSemanticOwner,type CoreCommerceSemanticCapture} from './commerce-core-semantic-owner.js';
import {assertTechnicalModelOwnerV5,type CommerceTechnicalModelOwnerV5} from '../profile-engine/technical-model-v5.js';
import {assertFamilyOwnerV5,type CommerceFamilyOwnerV5} from '../profile-engine/family-v5.js';
import {selectCoreApplicationFamilyV1,type CoreApplicationFamilySelectionV1} from '../generic/core-application-family.js';
import type {CommerceBindingAssemblyHandle,CommerceDerivedFamilyHandle,CommerceTechnicalModelHandle} from './commerce-stages-v1.js';

const ext=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,['commerce-core-source-owner'+ext,'commerce-core-semantic-owner'+ext,'../profile-engine/technical-model-v5'+ext,'../profile-engine/family-v5'+ext,'../generic/core-application-family'+ext]);
const where={path:'application.alch',start:0,end:0};

export interface CommerceBindingAssemblyInspectionV1 {
 readonly kind:'original-commerce-binding-assembly/v1-candidate';
 readonly selection:CoreApplicationFamilySelectionV1;
 readonly selected_family_sha256:string;
 readonly native_basis_qualified:false;
 readonly imported_output_qualified:false;
 readonly bound_application_qualified:false;
 readonly qualification:'original-source-profile-and-topology-requirements-only;native-and-runtime-binding-pending';
 readonly authority_effect:'none';
}
export interface CommerceBindingAssemblyOwnerV1 {
 assembly():CommerceBindingAssemblyHandle;
 family(assembly:CommerceBindingAssemblyHandle):CommerceDerivedFamilyHandle;
 inspect(assembly:CommerceBindingAssemblyHandle):CommerceBindingAssemblyInspectionV1;
 assertCurrent(assembly:CommerceBindingAssemblyHandle):void;
 dispose():void;
}
const owners=new WeakSet<object>();
export function assertCommerceBindingAssemblyOwnerV1(owner:CommerceBindingAssemblyOwnerV1):void {
 if(!owner||typeof owner!=='object'||!owners.has(owner))fail('ForeignOwner',where,'original binding assembly owner required');
 owner.assertCurrent(owner.assembly());
}

/** The issuer derives the selected family itself. No caller DTO, dependency
 * descriptor, imported module or runtime callback can mint this handle. */
export function createCommerceBindingAssemblyOwnerV1(
 sources:CoreCommerceSourceOwner,source:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 models:CommerceTechnicalModelOwnerV5,model:CommerceTechnicalModelHandle,
 families:CommerceFamilyOwnerV5,
):CommerceBindingAssemblyOwnerV1 {
 assertCoreCommerceSourceOwner(sources);assertCoreCommerceSemanticOwner(semantics);
 assertTechnicalModelOwnerV5(models);assertFamilyOwnerV5(families);pin.assertCurrent();
 const selected=selectCoreApplicationFamilyV1(sources,source,semantics,semantic,models,model,families);
 const inspection:CommerceBindingAssemblyInspectionV1=coreFreeze({
  kind:'original-commerce-binding-assembly/v1-candidate',selection:selected.selection,
  selected_family_sha256:selected.selection.family_sha256,native_basis_qualified:false,
  imported_output_qualified:false,bound_application_qualified:false,
  qualification:'original-source-profile-and-topology-requirements-only;native-and-runtime-binding-pending',authority_effect:'none',
 });
 const token=Object.freeze({kind:'original-commerce-binding-assembly/v1-candidate'}) as unknown as CommerceBindingAssemblyHandle;
 let disposed=false;
 const current=(h:CommerceBindingAssemblyHandle)=>{
  if(h!==token)fail('ForeignOwner',where,'exact original binding assembly handle required');
  if(disposed)fail('DisposedOwner',where,'binding assembly disposed');
  pin.assertCurrent();semantics.assertCurrent(semantic);
  const family=families.inspect(selected.family);
  if(family.family_sha256!==inspection.selected_family_sha256||family.source_capture_sha256!==inspection.selection.source_capture_sha256||family.graph_sha256!==inspection.selection.technical_graph_sha256)
   fail('StaleOwner',where,'selected original family changed');
 };
 const owner:CommerceBindingAssemblyOwnerV1=Object.freeze({
  assembly(){current(token);return token;},
  family(h:CommerceBindingAssemblyHandle){current(h);return selected.family;},
  inspect(h:CommerceBindingAssemblyHandle){current(h);return inspection;},
  assertCurrent:current,
  dispose(){if(disposed)return;current(token);disposed=true;families.dispose(selected.family);},
 });
 owners.add(owner);current(token);return owner;
}
