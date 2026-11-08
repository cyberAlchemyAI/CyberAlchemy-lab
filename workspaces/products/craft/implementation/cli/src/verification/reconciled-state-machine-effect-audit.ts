import {createEffectAuditRunner} from './reconciled-effect-audit.js';
import type {CompiledProjectGraph} from '../input/project-model.js';
import type {ReconciledProjectPlan} from '../generation/reconciled-project.js';
import {getReconciledSource} from '../generation/reconciled-sources.js';
import {sha256} from '../input/source-manifest.js';
export const STATE_MACHINE_EFFECT_DEFINITION_SHA256='76dc0df7b5a296b350809a381cb7528a6ccf81722190afc43a716c16b5c4fdac';
/** Checked closure selection; source auditing does not depend on finite witness availability. */
export function createStateMachineEffectAudit(graph:CompiledProjectGraph,plan:ReconciledProjectPlan){
 if(sha256(getReconciledSource('state_machine_effect_audit'))!==STATE_MACHINE_EFFECT_DEFINITION_SHA256)throw Error('STATE_MACHINE_EFFECT_AUDIT:definition drift');
 const roots=graph.nodes.filter(n=>n.kind==='State Machine').map(n=>n.selector).sort(),paths=new Set<string>();
 const visit=(p:string)=>{
  if(paths.has(p))return;paths.add(p);
  const m=plan.resolved.modules.find(m=>m.relative_path===p);if(!m)throw Error('STATE_MACHINE_EFFECT_AUDIT:missing module');
  if(m.qualified_selectors.some(s=>!['Rule','State Machine'].includes(graph.nodes.find(n=>n.selector===s)!.kind)))throw Error('STATE_MACHINE_EFFECT_AUDIT:unexpected dependency kind');
  for(const i of m.imports){if(!i.target_path)throw Error('STATE_MACHINE_EFFECT_AUDIT:external dependency');visit(i.target_path);}
 };
 for(const selector of roots){
  const callable='transition'+selector.split(':')[1]!.split('-').map(w=>w[0]!.toUpperCase()+w.slice(1)).join('');
  const modules=plan.resolved.modules.filter(m=>m.qualified_selectors.includes(selector)&&m.exports.some(e=>e.name===callable&&e.kind==='value'));
  if(modules.length!==1)throw Error('STATE_MACHINE_EFFECT_AUDIT:unique reducer required');visit(modules[0]!.relative_path);
 }
 return Object.freeze({definition_sha256:STATE_MACHINE_EFFECT_DEFINITION_SHA256,roots:Object.freeze(roots),module_paths:Object.freeze([...paths].sort())});
}
/** Trusted parser only. No generated module is imported by this observer. */
export const STATE_MACHINE_EFFECT_AUDIT_RUNNER=createEffectAuditRunner('STATE_MACHINE_EFFECT_AUDIT','domainspec.state-machine-effect-observation/v1-candidate');
