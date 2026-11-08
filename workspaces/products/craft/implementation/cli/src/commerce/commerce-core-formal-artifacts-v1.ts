/** Optional, source-selected files for the checked Core Commerce Alloy view.
 * The files carry a structural projection and its exact provenance, not a
 * temporal model, executable semantics, or solver result. Claims are optional.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import path from 'node:path';
import {createHash} from 'node:crypto';
import {publishAtomicDirectory} from '../generation/atomic-publication.js';
import {coreFreeze} from './commerce-core-syntax.js';
import {type CoreCommerceSourceOwner,type CoreCommerceSourceCapture} from './commerce-core-source-owner.js';
import {type CoreCommerceSemanticOwner,type CoreCommerceSemanticCapture} from './commerce-core-semantic-owner.js';
import {type CommerceWorkflowCoordinationBindingV1} from './commerce-workflow-coordination-binding-v1.js';
import {type CommerceApplicationAssemblyV1} from './commerce-application-assembly-v1.js';
import {exportCoreCommerceFormalStructureV1,type CoreCommerceFormalStructureV1} from './commerce-core-formal-structure-v1.js';

const sha=(value:string)=>createHash('sha256').update(value).digest('hex');
export class CoreCommerceFormalArtifactErrorV1 extends Error {
 constructor(readonly code:'UnsupportedLanguage'|'InvalidFormalTarget') {super(code);this.name='CoreCommerceFormalArtifactErrorV1';}
}
export type CoreCommerceFormalLanguageV1='alloy'|'tla+';
export interface CoreCommerceFormalArtifactsV1 {
 readonly schema_version:'craft.core-commerce-formal-artifacts/v1-candidate';
 readonly model:CoreCommerceFormalStructureV1;
 readonly files:readonly Readonly<{relative_path:'core-commerce-structure.als'|'core-commerce-structure.json';content:string;sha256:string}>[];
 readonly authority_effect:'none';
 readonly claim_ceiling:CoreCommerceFormalStructureV1['claim_ceiling'];
}

/** Generate independently of ordinary application code and without claims. */
export function createCoreCommerceFormalArtifactsV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 binding:CommerceWorkflowCoordinationBindingV1,assembly:CommerceApplicationAssemblyV1,
 language:CoreCommerceFormalLanguageV1='alloy',
):CoreCommerceFormalArtifactsV1 {
 if(language!=='alloy')throw new CoreCommerceFormalArtifactErrorV1('UnsupportedLanguage');
 const model=exportCoreCommerceFormalStructureV1(sources,capture,semantics,semantic,binding,assembly);
 const content=JSON.stringify(model,null,2)+'\n';
 const files=coreFreeze([
  {relative_path:'core-commerce-structure.als' as const,content:model.alloy,sha256:model.alloy_sha256},
  {relative_path:'core-commerce-structure.json' as const,content,sha256:sha(content)},
 ]);
 return coreFreeze({schema_version:'craft.core-commerce-formal-artifacts/v1-candidate' as const,
  model,files,authority_effect:'none' as const,claim_ceiling:model.claim_ceiling});
}

/** Publish only to a fresh sibling directory with a no-replace commit. The
 * same branded owners are rechecked immediately before the commit. */
export function publishCoreCommerceFormalArtifactsV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 binding:CommerceWorkflowCoordinationBindingV1,assembly:CommerceApplicationAssemblyV1,
 targetRoot:string,language:CoreCommerceFormalLanguageV1='alloy',
):CoreCommerceFormalArtifactsV1 {
 if(typeof targetRoot!=='string'||!path.isAbsolute(targetRoot)||path.normalize(targetRoot)!==targetRoot)
  throw new CoreCommerceFormalArtifactErrorV1('InvalidFormalTarget');
 const artifacts=createCoreCommerceFormalArtifactsV1(sources,capture,semantics,semantic,binding,assembly,language);
 publishAtomicDirectory(targetRoot,artifacts.files,'.domainspec-formal-',()=>{
  // Rebuild the exact model, not only the source hash: this rechecks source,
  // executable, profile, workflow, and exporter identities at commit time.
  const current=exportCoreCommerceFormalStructureV1(sources,capture,semantics,semantic,binding,assembly);
  if(current.alloy_sha256!==artifacts.model.alloy_sha256||current.structure_sha256!==artifacts.model.structure_sha256)
   throw Object.assign(new Error('formal model changed before publication'),{code:'StaleFormalModel'});
 });
 return artifacts;
}
