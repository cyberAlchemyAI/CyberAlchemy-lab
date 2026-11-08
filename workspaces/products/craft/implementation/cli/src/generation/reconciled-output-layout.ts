import type {SelectedReconciledProject} from './selected-reconciled-project.js';
import {selectSelectedReconciledArtifacts} from './selected-reconciled-project.js';
import {APPLICATION_LAYOUT,PROJECT_LAYOUT,type OutputLayout} from './output-layout.js';
import {RECONCILED_APPLICATION_LAYOUT_DEFINITION_SHA256,selectReconciledApplicationArtifacts} from './reconciled-application-layout.js';
import {RECONCILED_PROJECT_LAYOUT_DEFINITION_SHA256,selectReconciledProjectArtifacts} from './reconciled-project-layout.js';

export function assertReconciledOutputLayout(layout:unknown,roots:readonly string[]|null=null):asserts layout is OutputLayout|undefined {
  if(layout!==undefined&&((layout!==APPLICATION_LAYOUT.id&&layout!==PROJECT_LAYOUT.id)||roots!==null)){
    throw Object.assign(new Error('DS_RECONCILED_BUILD_LAYOUT: unsupported layout or node-scoped structured output; no legacy fallback'),{code:'DS_RECONCILED_BUILD_LAYOUT',pointer:'/output-layout',exitCode:22});
  }
}

export function reconciledLayoutDefinitionSha256(layout:OutputLayout):string {
  return layout===APPLICATION_LAYOUT.id?RECONCILED_APPLICATION_LAYOUT_DEFINITION_SHA256:RECONCILED_PROJECT_LAYOUT_DEFINITION_SHA256;
}

export function reconciledOutputView(plan:SelectedReconciledProject,roots:readonly string[]|null,layout:OutputLayout|undefined){
  assertReconciledOutputLayout(layout,roots);
  return layout===undefined
    ? selectSelectedReconciledArtifacts(plan,roots)
    : layout===APPLICATION_LAYOUT.id
      ? selectReconciledApplicationArtifacts(plan)
      : selectReconciledProjectArtifacts(plan);
}
