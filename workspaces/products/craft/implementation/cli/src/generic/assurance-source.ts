/** Original captured opaque attachment validation; no parser or proof authority.
 * Open Questions: C08 runtime and installed qualification remain pending. */
import path from 'node:path';
import {dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze,coreRelativePath,coreSourceFail as fail,coreSourceTokens as tokens,coreSourceChild as child,coreSourceChildren as children,coreSourceText as text} from '../commerce/commerce-core-syntax.js';
import {createCoreValueTypes} from '../commerce/commerce-core-types.js';
import type {CoreCommerceDeclaration} from '../commerce/commerce-core-reconstruction.js';
import type {CoreCommerceSourceInspection} from '../commerce/commerce-core-source-owner.js';
import type {GenericOpaqueClaimAttachmentV1,GenericOpaqueAssuranceInspectionV1} from './transaction-data-v1.js';
const extensions={lean4:'.lean',smtlib2:'.smt2',alloy:'.als','tla-plus':'.tla',souffle:'.dl'} as const;
export function genericClaimReference(d:CoreCommerceDeclaration,modulePath:string){
 if(d.surface!=='FormalClaim')fail('InvalidContract',d.syntax,'actual FormalClaim declaration required');
 const words=tokens(d.syntax).filter(t=>!t.layout).map(t=>t.token),language=words[words.indexOf('language')+1] as keyof typeof extensions;
 if(!Object.hasOwn(extensions,language))fail('Syntax',d.syntax,'unknown opaque claim language');
 const reference=text(child(d.syntax,'reference')),relative=reference.includes('/')?reference:path.posix.join(path.posix.dirname(modulePath),reference);
 if(!coreRelativePath(relative)||reference.includes('#')||reference.includes(':')||!reference.endsWith(extensions[language]))fail('InvalidContract',d.syntax,'exact normalized language/file pairing required');
 return {path:relative,language};
}
export function inspectGenericOpaqueAssurance(capture:CoreCommerceSourceInspection,_executableSubject?:string):GenericOpaqueAssuranceInspectionV1{
 if(capture.capture_mode!=='atomic-state-entry'&&capture.capture_mode!=='external-read-entry'&&capture.capture_mode!=='external-write-entry'&&capture.capture_mode!=='event-handoff-entry')fail('InvalidContract',{path:capture.application_path,start:0,end:0},'opaque generic attachments require actual atomic capture');
 const types=createCoreValueTypes(capture.reconstruction),claims:GenericOpaqueClaimAttachmentV1[]=[],assets=new Map<string,number>();
 for(const m of capture.reconstruction.modules)for(const d of m.declarations)if(d.surface==='FormalClaim'){
  if(claims.length>=16)fail('ResourceLimit',d.syntax,'opaque claim count bound');
  const reference=genericClaimReference(d,m.path),asset=capture.files.find(f=>f.path===reference.path);if(!asset)fail('UnknownReference',d.syntax,'claim asset must be physically captured');
  if(asset.bytes>262144)fail('ResourceLimit',d.syntax,'opaque claim asset byte bound');assets.set(asset.path,asset.bytes);
  if([...assets.values()].reduce((a,b)=>a+b,0)>262144)fail('ResourceLimit',d.syntax,'opaque claim aggregate byte bound');
  const targets=children(child(d.syntax,'name-list'),'qualified-name').map(n=>{const t=types.resolve(d.module,text(n),n),ownership=capture.reconstruction.ownership.find(o=>o.declaration===t.id);if(t.surface==='FormalClaim'||t.module==='Craft.Generated.Auth'||t.module.startsWith('Craft.Generated.Auth.')||ownership?.category==='technical'||ownership?.category==='coordination')fail('InvalidContract',n,'claim target must be actual authored declaration');return t.id;});
  if(!targets.length||targets.length>16)fail('ResourceLimit',d.syntax,'opaque claim target count bound');if(new Set(targets).size!==targets.length)fail('DuplicateSymbol',d.syntax,'distinct resolved claim targets required');
  claims.push({id:d.id,language:reference.language,source:{path:asset.path,sha256:asset.sha256,bytes:asset.bytes},targets,qualification:'opaque-not-evaluated'});
 }
 claims.sort((a,b)=>a.id<b.id?-1:a.id>b.id?1:0);
 return coreFreeze({schema_version:'craft.generic-opaque-assurance/v1-candidate',claims,assurance_sha256:dataDigest(claims),authority_effect:'none'});
}
