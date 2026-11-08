/** Keep fresh-source Auth as the default integration oracle. The selected
 * package asset is an additional run of the same business path. */
import {produceCommerceAuthNativeOwnerV1,
 createCommerceAuthNativeOwnerFromSelectedAsset} from '../../src/commerce/commerce-auth-ready-bridge-v1.js';
import {loadOriginalGenericAuthAsset} from '../../src/generic/auth-asset.js';

export async function createCommerceTestAuthNativeV1(directory:string){
 const variant=process.env.CRAFT_COMMERCE_AUTH_COMPONENT??'source';
 if(variant==='source')return produceCommerceAuthNativeOwnerV1(directory);
 if(variant==='selected')return createCommerceAuthNativeOwnerFromSelectedAsset(
  loadOriginalGenericAuthAsset(directory));
 throw new Error('Unknown CRAFT_COMMERCE_AUTH_COMPONENT');
}
