import {canonicalJson,sha256} from '../input/source-manifest.js';
import {selectSelectedReconciledArtifacts as selectReconciledArtifacts,type SelectedReconciledProject as ReconciledProjectPlan} from './selected-reconciled-project.js';
import {APPLICATION_LAYOUT} from './output-layout.js';
import {selectedReconciledExtension} from './selected-reconciled-project.js';

export const RECONCILED_APPLICATION_LAYOUT_DEFINITION_SHA256='b226e6236b37674bcba3cf7e5481e361f7899ccb7eb95ba31baa1e12f21d138d';
function freeze<T>(value:T):T{if(value&&typeof value==='object'&&!Object.isFrozen(value)){Object.values(value).forEach(freeze);Object.freeze(value);}return value;}

/** A path envelope only: do not regenerate modules or rewrite import specifiers. */
export function selectReconciledApplicationArtifacts(plan:ReconciledProjectPlan){
 const original=selectReconciledArtifacts(plan),{view_sha256,...source}=original;
 const prefix=APPLICATION_LAYOUT.domain+'/'+plan.selection.language+'/src/';
 const body={...source,output_layout:APPLICATION_LAYOUT.id,layout_definition_sha256:RECONCILED_APPLICATION_LAYOUT_DEFINITION_SHA256,source_view_sha256:view_sha256,
  ...selectedReconciledExtension(plan.selection),
  artifacts:source.artifacts.map(a=>({...a,relative_path:prefix+a.relative_path})),
  modules:source.modules.map(m=>({...m,relative_path:prefix+m.relative_path,...('imports' in m&&Array.isArray(m.imports)?{imports:m.imports.map(i=>({...i,target_path:i.target_path===null?null:prefix+i.target_path}))}:{})}))};
 return freeze({...body,view_sha256:sha256(canonicalJson(body))});
}
