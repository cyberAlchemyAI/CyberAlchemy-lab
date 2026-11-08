import type {CompiledProjectGraph} from '../input/project-model.js';
import type {ReconciledProjectPlan} from '../generation/reconciled-project.js';
import {createEffectAuditRunner} from './reconciled-effect-audit.js';
import {CROSS_GENERATOR_WORKFLOW_DEFINITION_SHA256,assertCrossGeneratorWorkflowSurface,type CrossGeneratorWorkflowSurface} from './reconciled-cross-generator-workflow-surface.js';
import {workflowVerificationDefinitions} from './reconciled-workflow-controls.js';
import {createWorkflowEffectAudit,WORKFLOW_EFFECT_AUDIT_RUNNER} from './reconciled-workflow-effect-audit.js';
import {createWorkflowOrchestrationAudit,WORKFLOW_ORCHESTRATION_AUDIT_RUNNER} from './reconciled-workflow-orchestration-audit.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';
const replace=(source:string,from:string,to:string)=>{if(source.split(from).length!==2)throw Error('WORKFLOW_INTEROP_AUDIT:hook drift');return source.replace(from,to);};
function createModuleRunner(){
 let runner=createEffectAuditRunner('WORKFLOW_INTEROP_AUDIT','domainspec.cross-generator-module-observation/v1-candidate');
 runner=replace(runner,'try{\n const snapshot=',String.raw`try{
 if(hash(selected.definition)!=='__HASH__'||!['source','native'].includes(selected.phase))throw Error('WORKFLOW_INTEROP_AUDIT:definition/phase');
 const native=selected.phase==='native',phasePath=p=>p.replace(/\.ts$/,native?'.js':'.ts');
 const canonical=v=>JSON.stringify(v,(_,x)=>x&&typeof x==='object'&&!Array.isArray(x)?Object.fromEntries(Object.entries(x).sort(([a],[b])=>a<b?-1:a>b?1:0)):x);
 const expectedModules=new Map(selected.modules.map(m=>[phasePath(m.relative_path),m]));
 if(expectedModules.size!==selected.modules.length||canonical([...expectedModules.keys()])!==canonical(selected.module_paths))throw Error('WORKFLOW_INTEROP_AUDIT:module set');
 const snapshot=`);
 runner=replace(runner,'const violations=[];let visits=0;',String.raw`
  const expected=expectedModules.get(relative_path),imports=[],exports=[],typeExports=[],valueExports=[],namespaces=new Map();
  const support=(selected.support_modules??[]).find(m=>phasePath(m.relative_path)===relative_path);
  const trustedSupport=!!support&&support.source_sha256===definition.trusted_enum_provider_sha256;
  if(support&&(!trustedSupport||!native&&hash(fs.readFileSync(file))!==support.source_sha256))throw Error('WORKFLOW_INTEROP_AUDIT:support drift');
  const violations=[];let visits=0;
  const problem=(code,name,n)=>{if(violations.length<64)violations.push({code,name,offset:n?.pos??0});};
  const id=(n,name)=>n?.kind===K.Identifier&&identifier(n)===name;
  const literal=n=>n?.kind===K.StringLiteral?n.text:null;
  for(const statement of source.statements){
   if(statement.kind===K.ImportDeclaration){
    const c=statement.importClause,items=c?.namedBindings?.elements,spec=literal(statement.moduleSpecifier),ns=c?.namedBindings;
    if(!spec||c?.name||statement.attributes||statement.assertClause||native&&c?.isTypeOnly)problem('import-form','closed ESM import',statement);
    else if(ns?.kind===K.NamespaceImport&&expected.role==='workflow-provider'&&!c.isTypeOnly){
     imports.push({specifier:spec,names:[],namespace:true});const name=identifier(ns.name);
     if(namespaces.has(name))problem('namespace-binding','duplicate namespace',ns);
     namespaces.set(name,{specifier:spec,names:new Set(),references:new Set([ns.name])});
    }else if(!items?.length||items.some(e=>e.isTypeOnly||e.name?.kind!==K.Identifier))problem('import-form','static named import required',statement);
    else imports.push({specifier:spec,names:items.map(e=>identifier(e.propertyName??e.name)).sort(),...(c.isTypeOnly?{type_only:true}:{})});
   }
   if(statement.kind===K.ExportDeclaration){
    const items=statement.exportClause?.elements,spec=literal(statement.moduleSpecifier);
    if(native||!['workflow-wrapper','workflow-provider','operation-wrapper','event-wrapper'].includes(expected.role)||!statement.isTypeOnly||!items?.length||!spec||statement.attributes||statement.assertClause||items.some(e=>e.propertyName||e.name?.kind!==K.Identifier))problem('export-form','exact type-only reexports only',statement);
    else{const ns=items.map(e=>identifier(e.name)).sort();imports.push({specifier:spec,names:ns,type_only:true,reexport:true});exports.push(...ns);typeExports.push(...ns);}
   }
   if(statement.modifiers?.some(m=>m.kind===K.ExportKeyword)){
    if(statement.modifiers.some(m=>m.kind===K.DefaultKeyword))problem('export-form','default export',statement);
    else if([K.FunctionDeclaration,K.TypeAliasDeclaration,K.InterfaceDeclaration].includes(statement.kind)&&statement.name?.kind===K.Identifier){
     const name=identifier(statement.name);exports.push(name);(statement.kind===K.FunctionDeclaration?valueExports:typeExports).push(name);
    }else if(statement.kind===K.VariableStatement)for(const d of statement.declarationList.declarations){if(d.name.kind===K.Identifier){exports.push(identifier(d.name));valueExports.push(identifier(d.name));}else problem('export-form','destructured export',d);}
    else problem('export-form','unexpected exported declaration',statement);
   }
  }
 `);
 runner=replace(runner,'const visit=(n,depth=0)=>{','const visit=(n,depth=0,inType=false)=>{');
 runner=replace(runner,'const form=forms.get(n.kind);if(form&&violations.length<64)',String.raw`
   if(!inType){
    if(n.kind===K.PropertyAccessExpression&&n.expression?.kind===K.Identifier&&namespaces.has(identifier(n.expression))&&!n.questionDotToken){
     const ns=namespaces.get(identifier(n.expression));ns.references.add(n.expression);ns.names.add(identifier(n.name));
    }
    if(n.kind===K.Identifier&&namespaces.has(identifier(n))&&!namespaces.get(identifier(n)).references.has(n))problem('namespace-binding','nonstatic namespace use',n);
    if(n.kind===K.Identifier&&['require','exports'].includes(identifier(n)))problem('module-format','CommonJS binding in ESM',n);
   }
   const supportError=trustedSupport&&n.kind===K.ClassDeclaration&&n.name&&identifier(n.name)==='EnumContractError'&&n.heritageClauses?.length===1&&n.heritageClauses[0].types?.length===1&&identifier(n.heritageClauses[0].types[0].expression)==='TypeError';
   const form=forms.get(n.kind);if(form&&!supportError&&violations.length<64)`);
 runner=replace(runner,'if(identifiers.has(name)&&violations.length<64)','if(!inType&&identifiers.has(name)&&violations.length<64)');
 runner=replace(runner,'n.forEachChild(child=>visit(child,depth+1));','n.forEachChild(child=>visit(child,depth+1,inType||n.kind===K.TypeReference||n.kind===K.TypeQuery));');
 runner=replace(runner,'modules.push({relative_path,source_sha256:hash(fs.readFileSync(file)),violations});',String.raw`
  for(const ns of namespaces.values()){
   const wanted=expected.imports.find(i=>i.namespace&&i.specifier===ns.specifier);
   if(!wanted||canonical([...ns.names].sort())!==canonical(wanted.native_names))problem('namespace-members','material members differ',source);
  }
  const sort=(a,b)=>a.specifier<b.specifier?-1:a.specifier>b.specifier?1:0;
  imports.sort(sort);exports.sort();
  const wanted=expected.imports.filter(i=>!native||!i.type_only).map(i=>({specifier:i.specifier,names:i.names,...(i.namespace?{namespace:true}:{}),...(!native&&i.type_only?{type_only:true}:{}),...(!native&&i.reexport?{reexport:true}:{})})).sort(sort);
  if(canonical(imports)!==canonical(wanted))problem('import-surface','source-derived imports differ',source);
  if(canonical(typeExports.sort())!==canonical(native?[]:[...expected.type_exports].sort())||canonical(valueExports.sort())!==canonical([...expected.value_exports].sort()))problem('export-kind','source-derived export kinds differ',source);
  if(canonical(exports)!==canonical([...expected.value_exports,...(native?[]:expected.type_exports)].sort()))problem('export-surface','source-derived exports differ',source);
  for(const i of imports){
   if(expected.role==='workflow-provider'&&i.specifier==='node:crypto'&&canonical(i.names)==='["createHash"]'&&!i.namespace&&!i.type_only&&!i.reexport)continue;
   const target=path.posix.normalize(path.posix.join(path.posix.dirname(relative_path),i.specifier));
   if(!i.specifier.startsWith('.')||!expectedModules.has(native?target:target.replace(/\.js$/,'.ts')))problem('external-import',i.specifier,source);
  }
  modules.push({relative_path,source_sha256:hash(fs.readFileSync(file)),imports,exports,violations});`);
 return runner.replace('__HASH__',CROSS_GENERATOR_WORKFLOW_DEFINITION_SHA256);
}
/** ESM module shape only; mandatory effect and orchestration facets remain separate. */
export const CROSS_GENERATOR_WORKFLOW_MODULE_AUDIT_RUNNER=createModuleRunner();
export {WORKFLOW_EFFECT_AUDIT_RUNNER,WORKFLOW_ORCHESTRATION_AUDIT_RUNNER};
function freeze<T>(v:T):T{if(v&&typeof v==='object'&&!Object.isFrozen(v)){Object.values(v).forEach(freeze);Object.freeze(v);}return v;}
const registered=new WeakSet<object>();
export function createCrossGeneratorWorkflowAudit(graph:CompiledProjectGraph,plan:ReconciledProjectPlan,surface:CrossGeneratorWorkflowSurface){
 assertCrossGeneratorWorkflowSurface(surface);
 if(surface.project_plan_sha256!==plan.plan_sha256)throw Error('WORKFLOW_INTEROP_AUDIT:foreign surface');
 const definitions=workflowVerificationDefinitions();
 const effects=createWorkflowEffectAudit(graph,plan,definitions.binding,definitions.effects);
 const orchestration=createWorkflowOrchestrationAudit(graph,plan,{binding:definitions.binding,outcomes:definitions.outcomes,orchestration:definitions.orchestration});
 const paths=[...new Set(surface.rows.flatMap(r=>r.modules.map(m=>m.relative_path)))].sort();
 if(canonicalJson(paths)!==canonicalJson(effects.module_paths)||canonicalJson(surface.rows.map(r=>r.provider_path).sort())!==canonicalJson(orchestration.module_paths))throw Error('WORKFLOW_INTEROP_AUDIT:exact facet closure');
 const body={schema_version:'domainspec.cross-generator-workflow-audit/v1-candidate' as const,surface_sha256:surface.surface_sha256,definition_sha256:surface.definition_sha256,
  project_plan_sha256:plan.plan_sha256,effects,orchestration,definitions:{effects:definitions.effects,orchestration:definitions.orchestration},
  required_facets:['module','effects','orchestration'] as const,native_status:'not_evaluable' as const,authority_effect:'none' as const};
 const result=freeze({...body,audit_sha256:sha256(canonicalJson(body))});registered.add(result);return result;
}
export type CrossGeneratorWorkflowAudit=ReturnType<typeof createCrossGeneratorWorkflowAudit>;
export function assertCrossGeneratorWorkflowAudit(v:unknown):asserts v is CrossGeneratorWorkflowAudit{
 if(!v||typeof v!=='object'||!registered.has(v))throw Error('WORKFLOW_INTEROP_AUDIT:registered audit required');
}
