import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {assertReconciledProjectPlan, type ReconciledProjectPlan} from '../generation/reconciled-project.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {getReconciledSource} from '../generation/reconciled-sources.js';
import {freezeWorkflow} from '../typed-backend/workflow-occurrences.js';
import {createWorkflowBinding, SEMANTIC_WORKFLOW_BINDING_DEFINITION_SHA256} from './reconciled-workflow-binding.js';
import {OPERATION_EFFECT_AUDIT_RUNNER} from './reconciled-operation-effect-audit.js';

export const WORKFLOW_EFFECT_AUDIT_DEFINITION_SHA256 = 'e3f6ee3ee1f975ba48f4a9f9602a1e96b7e018f3b7d11a414224e0b01162588b';
export function createWorkflowEffectAudit(graph: CompiledProjectGraph, plan: ReconciledProjectPlan, bindingDefinition: string, definition: string) {
  assertCompiledProjectSnapshot(graph); assertReconciledProjectPlan(plan);
  if (typeof definition !== 'string' || sha256(definition) !== WORKFLOW_EFFECT_AUDIT_DEFINITION_SHA256) throw new TypeError('WORKFLOW_EFFECT_AUDIT:definition drift');
  if (typeof bindingDefinition !== 'string' || sha256(bindingDefinition) !== SEMANTIC_WORKFLOW_BINDING_DEFINITION_SHA256) throw new TypeError('WORKFLOW_EFFECT_AUDIT:binding definition drift');
  if (canonicalJson(createCompiledProjectCertificate(graph)) !== canonicalJson(plan.resolved.certificate)) throw new TypeError('WORKFLOW_EFFECT_AUDIT:cross-graph plan');
  const nodes = graph.nodes.filter(n => n.kind === 'Workflow'), bindings = nodes.map(n => createWorkflowBinding(n, graph, plan, bindingDefinition));
  const module_paths = [...new Set(bindings.flatMap(b => b.module_paths))].sort(), runtime = plan.selection.module_root + '/runtime/enum.ts';
  return freezeWorkflow({definition_sha256: WORKFLOW_EFFECT_AUDIT_DEFINITION_SHA256, roots: nodes.map(n => n.selector).sort(), module_paths,
    workflow_modules: bindings.map(b => ({relative_path: b.provider_path, source_sha256: b.descriptor.provider_sha256})).sort((a, b) => a.relative_path < b.relative_path ? -1 : a.relative_path > b.relative_path ? 1 : 0),
    support_modules: module_paths.filter(p => p === runtime).map(relative_path => ({relative_path, source_sha256: sha256(getReconciledSource('enum_provider'))}))});
}

// Reuse inherited restrictions byte-for-byte. Fail if a construction hook drifts,
// rather than silently producing a partial observer from a failed replacement.
const replace = (source: string, from: string, to: string): string => {
  if (source.split(from).length !== 2) throw new TypeError('WORKFLOW_EFFECT_AUDIT:observer hook drift');
  return source.replace(from, to);
};
let runner = OPERATION_EFFECT_AUDIT_RUNNER.replaceAll('OPERATION_EFFECT_AUDIT', 'WORKFLOW_EFFECT_AUDIT').replaceAll('domainspec.operation-effect-observation/v1-candidate', 'domainspec.workflow-effect-observation/v1-candidate');
runner = replace(runner, 'try{\n const snapshot=', String.raw`try{
 if(hash(selected.definition)!=='${WORKFLOW_EFFECT_AUDIT_DEFINITION_SHA256}')throw Error('WORKFLOW_EFFECT_AUDIT:definition drift');
 if(!['source','native'].includes(selected.phase)||typeof selected.module_root!=='string'||!path.isAbsolute(selected.module_root))throw Error('WORKFLOW_EFFECT_AUDIT:phase/root');
 const safe=p=>typeof p==='string'&&p.length>0&&!p.includes('\0')&&!p.includes('\\')&&!path.posix.isAbsolute(p)&&!p.split('/').some(x=>!x||x==='.'||x==='..');
 const phasePath=p=>p.replace(/\.ts$/,selected.phase==='native'?'.js':'.ts');
 if(!Array.isArray(selected.module_paths)||selected.module_paths.some(p=>!safe(p)||!p.endsWith(selected.phase==='native'?'.js':'.ts')||p.endsWith('.d.ts'))||new Set(selected.module_paths).size!==selected.module_paths.length)throw Error('WORKFLOW_EFFECT_AUDIT:module paths');
 const paths=new Set(selected.module_paths),metadata=new Set();
 const metadataRows=rows=>{
  if(!Array.isArray(rows))throw Error('WORKFLOW_EFFECT_AUDIT:exception metadata');
  return new Map(rows.map(m=>{
   if(!m||typeof m!=='object'||Object.keys(m).sort().join(',')!=='relative_path,source_sha256'||!safe(m.relative_path)||!m.relative_path.endsWith('.ts')||typeof m.source_sha256!=='string'||m.source_sha256.length!==64||!/^[a-f0-9]{64}$/.test(m.source_sha256)||!paths.has(phasePath(m.relative_path))||metadata.has(m.relative_path))throw Error('WORKFLOW_EFFECT_AUDIT:unbound exception metadata');
   metadata.add(m.relative_path);return [phasePath(m.relative_path),m];
  }));
 };
 const workflowModules=metadataRows(selected.workflow_modules);metadataRows(selected.support_modules);
 const snapshot=`);
runner = replace(runner, 'const violations=[];let visits=0;', String.raw`
  const violations=[];let visits=0;
  const problem=(code,name,n)=>{if(violations.length<64)violations.push({code,name,offset:n?.pos??0});};
  const workflow=workflowModules.get(relative_path);
  if(workflow&&selected.phase==='source'&&hash(fs.readFileSync(file))!==workflow.source_sha256)throw Error('WORKFLOW_EFFECT_AUDIT:Workflow source drift');
  const cryptoUses=new Set(),cryptoImports=[];
  const id=(n,name)=>n?.kind===K.Identifier&&identifier(n)===name;
  const string=(n,value)=>n?.kind===K.StringLiteral&&n.text===value;
  const call=(n,count)=>n?.kind===K.CallExpression&&!n.questionDotToken&&!n.typeArguments?.length&&n.arguments?.length===count&&!n.arguments.some(a=>a.kind===K.SpreadElement);
  const member=(n,name)=>n?.kind===K.PropertyAccessExpression&&!n.questionDotToken&&id(n.name,name);
  for(const s of source.statements){
   if(s.kind===K.ImportEqualsDeclaration)problem('external-import','import-equals',s);
   if(![K.ImportDeclaration,K.ExportDeclaration].includes(s.kind)||!s.moduleSpecifier)continue;
   const spec=s.moduleSpecifier;
   if(spec.kind!==K.StringLiteral){problem('external-import','nonliteral',s);continue;}
   if(spec.text==='node:crypto'){
    const clause=s.importClause,elements=clause?.namedBindings?.elements;
    const permitted=workflow&&s.kind===K.ImportDeclaration&&!clause?.isTypeOnly&&!clause?.name&&!s.attributes&&!s.assertClause&&elements?.length===1&&!elements[0].isTypeOnly&&!elements[0].propertyName&&id(elements[0].name,'createHash');
    if(!permitted)problem('crypto-binding','named createHash import required',s);
    else{cryptoImports.push(s);cryptoUses.add(elements[0].name);}
   }else{
    const target=path.posix.normalize(path.posix.join(path.posix.dirname(relative_path),spec.text));
    const mapped=selected.phase==='source'?target.replace(/\.js$/,'.ts'):target;
    if(!spec.text.startsWith('.')||!paths.has(mapped))problem('external-import',spec.text,s);
   }
  }
  if(workflow){
   if(cryptoImports.length!==1)problem('crypto-binding','one metadata import required',source);
   const declarations=source.statements.filter(s=>s.kind===K.VariableStatement).flatMap(statement=>statement.declarationList.declarations.map(declaration=>({statement,declaration}))).filter(r=>id(r.declaration.name,'digest'));
   let valid=false;
   if(declarations.length===1){
    const {statement,declaration}=declarations[0],fn=declaration.initializer,p=fn?.parameters?.[0],body=fn?.body;
    const update=body?.expression?.expression,hashCall=update?.expression?.expression,canonical=update?.arguments?.[0];
    valid=!statement.modifiers?.length&&/^const\b/.test(statement.declarationList.getText())&&statement.declarationList.declarations.length===1&&
     fn?.kind===K.ArrowFunction&&!fn.modifiers?.length&&!fn.typeParameters?.length&&fn.parameters.length===1&&id(p?.name,'v')&&!p.initializer&&!p.questionToken&&!p.dotDotDotToken&&!p.modifiers?.length&&
     call(body,1)&&member(body.expression,'digest')&&string(body.arguments[0],'hex')&&
     call(update,1)&&member(update.expression,'update')&&call(hashCall,1)&&id(hashCall.expression,'createHash')&&string(hashCall.arguments[0],'sha256')&&
     call(canonical,1)&&id(canonical.expression,'canonical')&&id(canonical.arguments[0],'v');
    if(valid)cryptoUses.add(hashCall.expression);
   }
   if(!valid)problem('crypto-helper','exact metadata digest helper required',source);
  }
`);
runner = replace(runner, 'const form=forms.get(n.kind);', String.raw`
   if(n.kind===K.Identifier&&identifier(n)==='createHash'&&!cryptoUses.has(n))problem('crypto-escape','createHash',n);
   const form=forms.get(n.kind);`);
export const WORKFLOW_EFFECT_AUDIT_RUNNER = runner;
