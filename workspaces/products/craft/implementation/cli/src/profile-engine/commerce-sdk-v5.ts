/** Built public bootstrap. Source execution cannot create an SDK/basis.
 * Open Questions: docs/COMMERCE-SDK-V5.md#open-questions. */
import {captureCommercePublicSdkV5,inspectCommercePublicSdkV5,assertCommercePublicSdkCurrentV5,disposeCommercePublicSdkV5} from './commerce-sdk-physical-v5.js';
import {createCommerceTechnicalModelOwnerV5} from './technical-model-v5.js';
import {createCommerceFamilyOwnerV5} from './family-v5.js';
import {createCommerceNativeOwnerV5} from './commerce-native-v5.js';
import {createCommercePrefixStagesV5} from './commerce-prefix-stages-v5.js';
export async function createCommercePublicSdkV5(frontendRoot:string){
 const closure=await captureCommercePublicSdkV5(frontendRoot);
 try{
  const models=createCommerceTechnicalModelOwnerV5(),families=createCommerceFamilyOwnerV5(models),native=createCommerceNativeOwnerV5(closure,families);
  const stages=createCommercePrefixStagesV5(native);
  return Object.freeze({models,families,native,stages,inspect(){return inspectCommercePublicSdkV5(closure);},assertCurrent(){assertCommercePublicSdkCurrentV5(closure);},dispose(){disposeCommercePublicSdkV5(closure);}});
 }catch(error){disposeCommercePublicSdkV5(closure);throw error;}
}
