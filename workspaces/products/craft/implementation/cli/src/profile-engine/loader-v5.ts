/** Additive v5 descriptor/derivation checking. This is not a native basis loader.
 * Open Questions: docs/COMMERCE-PROFILE-FAMILY-V5.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {dataDigest} from './contracts.js';
import {validateProfilePackageV5} from './contracts-v5.js';
import {assertFamilyOwnerV5,type CommerceFamilyOwnerV5} from './family-v5.js';
import {coreFreeze,coreSourceFail as fail} from '../commerce/commerce-core-syntax.js';
import {pinCoreImplementation,readCorePhysicalFile} from '../commerce/commerce-core-physical.js';
import {parseCoreCommerceJson} from '../commerce/commerce-core-source-owner.js';
import type {CommerceDerivedFamilyHandle} from '../commerce/commerce-stages-v1.js';
const ext=path.extname(fileURLToPath(import.meta.url)),pin=pinCoreImplementation(import.meta.url,['contracts-v5'+ext,'family-v5'+ext,'../commerce/commerce-core-source-owner'+ext]),where={path:'profile-loader-v5',start:0,end:0};
export interface CheckedDerivedDescriptorDataV5 {readonly kind:'checked-derived-profile-descriptor-data/v5-candidate'}
export function createDerivedProfileCheckerV5(families:CommerceFamilyOwnerV5){
 assertFamilyOwnerV5(families);const owned=new WeakMap<object,{family:CommerceDerivedFamilyHandle;value:ReturnType<typeof validateProfilePackageV5>;file:ReturnType<typeof readCorePhysicalFile>|null;disposed:boolean}>();
 const current=(h:CheckedDerivedDescriptorDataV5)=>{const s=h&&typeof h==='object'?owned.get(h):undefined;if(!s)fail('ForeignOwner',where,'original derived descriptor checker token required');if(s.disposed)fail('DisposedOwner',where,'derived descriptor data disposed');pin.assertCurrent();families.assertCurrent(s.family);if(s.file&&readCorePhysicalFile(s.file.file.path).fingerprint!==s.file.fingerprint)fail('StaleOwner',where,'captured descriptor data changed');return s;};
 const check=(family:CommerceDerivedFamilyHandle,proposal:unknown,file:ReturnType<typeof readCorePhysicalFile>|null)=>{pin.assertCurrent();const original=families.inspect(family),value=validateProfilePackageV5(proposal),{resolved_dependencies,...header}=value;if(dataDigest(header)!==dataDigest(original.descriptor))fail('InvalidContract',where,'descriptor must match the exact original checked graph/family/mapping/scope/options');const h=Object.freeze({kind:'checked-derived-profile-descriptor-data/v5-candidate' as const});owned.set(h,{family,value,file,disposed:false});current(h);return h;};
 return Object.freeze({checkDescriptorData(family:CommerceDerivedFamilyHandle,proposal:unknown){return check(family,proposal,null);},readDescriptorData(family:CommerceDerivedFamilyHandle,file:string){const captured=readCorePhysicalFile(file);return check(family,parseCoreCommerceJson(captured.text,captured.file.path),captured);},inspect(h:CheckedDerivedDescriptorDataV5){const s=current(h);return coreFreeze({descriptor:s.value,source:families.inspect(s.family).source_capture_sha256,qualification:'validated-descriptor-data-only;not-resolved-native-owner-or-loaded-profile',native_resolution_verified:false,authority_effect:'none'});},assertCurrent(h:CheckedDerivedDescriptorDataV5){current(h);},dispose(h:CheckedDerivedDescriptorDataV5){current(h).disposed=true;}});
}
