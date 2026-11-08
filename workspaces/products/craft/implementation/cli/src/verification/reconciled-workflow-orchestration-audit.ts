import path from 'node:path';
import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {assertReconciledProjectPlan, type ReconciledProjectPlan} from '../generation/reconciled-project.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {freezeWorkflow} from '../typed-backend/workflow-occurrences.js';
import {createWorkflowBinding, SEMANTIC_WORKFLOW_BINDING_DEFINITION_SHA256} from './reconciled-workflow-binding.js';
import {createWorkflowOutcomeReference, WORKFLOW_CONTROLS_DEFINITION_SHA256} from './reconciled-workflow-outcome-reference.js';

export const WORKFLOW_ORCHESTRATION_DEFINITION_SHA256 = '1f29fa09c82f5a42f37fa666ad96e59e56021e625a40312fdecac4d0b0bfded1';
export function createWorkflowOrchestrationAudit(graph: CompiledProjectGraph, plan: ReconciledProjectPlan, definitions: {binding: string; outcomes: string; orchestration: string}) {
  assertCompiledProjectSnapshot(graph); assertReconciledProjectPlan(plan);
  for (const [key, pin] of Object.entries({binding: SEMANTIC_WORKFLOW_BINDING_DEFINITION_SHA256, outcomes: WORKFLOW_CONTROLS_DEFINITION_SHA256, orchestration: WORKFLOW_ORCHESTRATION_DEFINITION_SHA256})) {
    const value = definitions[key as keyof typeof definitions];
    if (typeof value !== 'string' || sha256(value) !== pin) throw new TypeError('WORKFLOW_ORCHESTRATION:definition drift:' + key);
  }
  if (canonicalJson(createCompiledProjectCertificate(graph)) !== canonicalJson(plan.resolved.certificate)) throw new TypeError('WORKFLOW_ORCHESTRATION:cross-graph plan');
  const rows = graph.nodes.filter(n => n.kind === 'Workflow').map(node => {
    const binding = createWorkflowBinding(node, graph, plan, definitions.binding), {workflow, policy} = binding;
    const reference = createWorkflowOutcomeReference(policy, definitions.outcomes);
    const steps = workflow.steps.map(s => ({step_id: s.step_id, operation_ref: s.operation_ref, action_sha256: s.action_sha256}));
    const prefix_templates = workflow.steps.map((failed, i) => {
      const evaluation = reference.evaluate({workflow_execution_id: 'audit-execution', failure_occurrence_id: 'audit-failure', local_error: null,
        events: [...steps.slice(0, i).map(s => ({step_id: s.step_id, kind: 'returned', outcome: {status: 'committed', value: null}})), {step_id: failed.step_id, kind: 'not-started'}]});
      const intent = evaluation.recovery?.recovery_intent;
      return {steps: steps.slice(0, i), plan: intent?.plan.map(({invocation_identity: _identity, ...row}) => row) ?? [], plan_digest: intent?.plan_digest ?? null};
    });
    const relative = path.posix.relative(path.posix.dirname(binding.provider_path), binding.material_path).replace(/\.ts$/, '.js');
    return {relative_path: binding.provider_path, source_sha256: binding.descriptor.provider_sha256, expected: {
      selector: node.selector, wf: {hash: workflow.workflow_sha256, selector: node.selector, steps}, policy_sha256: policy.policy_sha256,
      outcome_contract_sha256: '0a7cb5a92bbec1bc5003dd5a6ba70ebc184a8316ad617f2a362b5d9de82ba607',
      material_path: relative.startsWith('.') ? relative : './' + relative,
      imports: binding.descriptor.operation_imports, steps: workflow.steps.map(s => ({...steps.find(x => x.step_id === s.step_id)!, failure_continuation: s.failure_continuation})),
      compensations: workflow.compensations.map(c => ({compensation_id: c.compensation_id, operation_ref: c.operation_ref, action_sha256: c.action_sha256})), prefix_templates
    }};
  }).sort((a, b) => a.relative_path < b.relative_path ? -1 : a.relative_path > b.relative_path ? 1 : 0);
  return freezeWorkflow({definition_sha256: WORKFLOW_ORCHESTRATION_DEFINITION_SHA256, roots: rows.map(r => r.expected.selector).sort(), module_paths: rows.map(r => r.relative_path), workflow_modules: rows});
}

// Independently authored protocol grammar, not the production renderer.
// Whole statement trees are matched; source-only type wrappers are erased explicitly.
export const WORKFLOW_ORCHESTRATION_AUDIT_RUNNER = String.raw`
import fs from 'node:fs';import path from 'node:path';import {createHash} from 'node:crypto';import {pathToFileURL} from 'node:url';
const [compiler,config,input]=process.argv.slice(2);
const fail=m=>{throw Error('WORKFLOW_ORCHESTRATION:'+m)},need=(v,m)=>{if(!v)fail(m)};
const bytes=fs.readFileSync(input);need(bytes.length<=8388608,'input capacity');
const selected=JSON.parse(bytes),hash=v=>createHash('sha256').update(v).digest('hex');
const pin='1f29fa09c82f5a42f37fa666ad96e59e56021e625a40312fdecac4d0b0bfded1';
need(typeof selected.definition==='string'&&hash(selected.definition)===pin,'definition drift');
need(['source','native'].includes(selected.phase)&&typeof selected.module_root==='string'&&path.isAbsolute(selected.module_root),'phase/root');
let profileVisits=0;const bound=(v,d=0)=>{need(++profileVisits<=1000000&&d<=128,'profile capacity');if(v&&typeof v==='object')Object.values(v).forEach(x=>bound(x,d+1));};bound(selected);
const safe=p=>typeof p==='string'&&p.length>0&&!p.includes('\0')&&!p.includes('\\')&&!path.posix.isAbsolute(p)&&!p.split('/').some(x=>!x||x==='.'||x==='..');
const phasePath=p=>p.replace(/\.ts$/,selected.phase==='native'?'.js':'.ts');
need(Array.isArray(selected.module_paths)&&selected.module_paths.every(p=>safe(p)&&p.endsWith(selected.phase==='native'?'.js':'.ts')&&!p.endsWith('.d.ts'))&&new Set(selected.module_paths).size===selected.module_paths.length,'module paths');
need(Array.isArray(selected.workflow_modules)&&selected.workflow_modules.length===selected.module_paths.length,'profile coverage');
const rows=new Map();for(const r of selected.workflow_modules){
 need(r&&Object.keys(r).sort().join(',')==='expected,relative_path,source_sha256'&&safe(r.relative_path)&&r.relative_path.endsWith('.ts')&&typeof r.source_sha256==='string'&&r.source_sha256.length===64&&/^[a-f0-9]{64}$/.test(r.source_sha256)&&r.expected&&typeof r.expected==='object','profile row');
 const p=phasePath(r.relative_path);need(selected.module_paths.includes(p)&&!rows.has(p),'profile ownership');rows.set(p,r);
}
const {API}=await import(pathToFileURL(path.join(compiler,'dist/api/sync/api.js')).href);
const {SyntaxKind:K}=await import(pathToFileURL(path.join(compiler,'dist/ast/index.js')).href);
const api=new API({cwd:path.dirname(config)}),json=JSON.stringify;
const canonical=v=>json(v,(_,x)=>x&&typeof x==='object'&&!Array.isArray(x)?Object.fromEntries(Object.entries(x).sort(([a],[b])=>a<b?-1:a>b?1:0)):x);
const identifier=n=>n.getText().replace(/\\u(?:\{([0-9a-f]+)\}|([0-9a-f]{4}))/gi,(_,a,b)=>String.fromCodePoint(parseInt(a??b,16)));
const unwrap=n=>{while(n&&[K.AsExpression,K.TypeAssertionExpression,K.NonNullExpression,K.ParenthesizedExpression,K.SatisfiesExpression].includes(n.kind))n=n.expression;return n;};
const I=v=>['id',v],S=v=>['str',v],N=v=>['num',String(v)],G=(v,k)=>['get',v,k],A=(v,k)=>['at',v,k],C=(v,...a)=>['call',typeof v==='string'?I(v):v,...a];
const B=(...s)=>['block',...s],E=v=>['expr',v],R=v=>['return',v],V=(k,n,v=null)=>[k,[[I(n),v]]],X=(op,l,r)=>['binary',op,l,r];
const P=(k,v)=>['prop',k,v],O=(...p)=>['object',...p],L=(...e)=>['array',...e],F=v=>C(G(I('Object'),'freeze'),v);
const arrow=(names,body,async=false)=>['arrow',async,names.map(n=>[I(n),null,false,false,[]]),body];
const TRY=(body,handler)=>['try',body,[null,handler],null],IF=(condition,yes,no=null)=>['if',condition,yes,no];
function shape(node){
 const n=unwrap(node);if(!n)return null;const s=shape,items=x=>Array.from(x??[],s),mods=x=>Array.from(x??[],m=>K[m.kind]);
 switch(n.kind){
 case K.Identifier:return I(identifier(n));
 case K.StringLiteral:return S(n.text);
 case K.NumericLiteral:return N(n.text);
 case K.TrueKeyword:return ['bool',true];case K.FalseKeyword:return ['bool',false];case K.NullKeyword:return ['null'];
 case K.PropertyAccessExpression:return [n.questionDotToken?'optional-get':'get',s(n.expression),identifier(n.name)];
 case K.ElementAccessExpression:return [n.questionDotToken?'optional-at':'at',s(n.expression),s(n.argumentExpression)];
 case K.CallExpression:return [n.questionDotToken?'optional-call':'call',s(n.expression),...items(n.arguments)];
 case K.AwaitExpression:return ['await',s(n.expression)];
 case K.BinaryExpression:return X(n.operatorToken.getText(),s(n.left),s(n.right));
 case K.PrefixUnaryExpression:return ['prefix',K[n.operator],s(n.operand)];
 case K.ConditionalExpression:return ['conditional',s(n.condition),s(n.whenTrue),s(n.whenFalse)];
 case K.ArrowFunction:return ['arrow',!!n.modifiers?.some(m=>m.kind===K.AsyncKeyword),Array.from(n.parameters,p=>[s(p.name),s(p.initializer),!!p.dotDotDotToken,!!p.questionToken,mods(p.modifiers)]),s(n.body)];
 case K.Block:return B(...items(n.statements));
 case K.ExpressionStatement:return E(s(n.expression));
 case K.ReturnStatement:return R(s(n.expression));
 case K.IfStatement:return IF(s(n.expression),s(n.thenStatement),s(n.elseStatement));
 case K.VariableStatement:return s(n.declarationList);
 case K.VariableDeclarationList:return [n.getText().match(/^(const|let|var)\b/)?.[1]??'unknown-binding',Array.from(n.declarations,d=>[s(d.name),s(d.initializer)])];
 case K.TryStatement:return ['try',s(n.tryBlock),n.catchClause?[s(n.catchClause.variableDeclaration?.name),s(n.catchClause.block)]:null,s(n.finallyBlock)];
 case K.ForOfStatement:return ['for-of',!!n.awaitModifier,s(n.initializer),s(n.expression),s(n.statement)];
 case K.ContinueStatement:return ['continue',s(n.label)];
 case K.ArrayLiteralExpression:return L(...items(n.elements));
 case K.ObjectLiteralExpression:return O(...items(n.properties));
 case K.PropertyAssignment:return P(n.name.kind===K.Identifier?identifier(n.name):n.name.kind===K.StringLiteral?n.name.text:s(n.name),s(n.initializer));
 case K.ShorthandPropertyAssignment:need(!n.objectAssignmentInitializer,'shorthand default');return P(identifier(n.name),s(n.name));
 case K.SpreadAssignment:return ['spread-property',s(n.expression)];
 case K.SpreadElement:return ['spread',s(n.expression)];
 default:fail('unsupported protocol syntax:'+K[n.kind]);
 }
}
function expectedExecute(e){
 const id=I,mat=I('material'),results=id('results'),observations=id('observations'),input=id('input'),ids=id('ids');
 const stopped=reason=>C('stopped',input,results,observations,ids,...(reason?[S(reason)]:[]));
 const observe=(i,value)=>E(C(G(observations,'push'),C('observe',N(i),value)));
 const statement=[];
 statement.push(V('const','e',C('own',id('executionIdentity'),L(S('workflow_execution_id'),S('failure_occurrence_id')))));
 statement.push(V('const','ids',F(O(...['workflow_execution_id','failure_occurrence_id'].map(k=>P(k,C('identity',G(G(id('e'),k),'value'))))))));
 statement.push(V('const','input',C(G(mat,'capture'),id('parameters'))));
 statement.push(V('const','d',C('own',id('dependencies'),L(...e.imports.map(i=>S(i.selector))))));
 for(const [n,i]of e.imports.entries()){
  statement.push(V('const','call'+n,id(i.local)));
  statement.push(E(C('imported',id('call'+n),S(i.selector),S(i.action_sha256),S(i.descriptor_sha256))));
  statement.push(V('const','dep'+n,G(A(id('d'),S(i.selector)),'value')));
 }
 statement.push(V('const','results',L()),V('const','observations',L()));
 for(const [n,step]of e.steps.entries()){
  const index=e.imports.findIndex(i=>i.selector===step.operation_ref&&i.action_sha256===step.action_sha256);need(index>=0,'source step import');
  statement.push(B(V('let','args'),
   TRY(B(E(X('=',id('args'),C(G(A(G(mat,'steps'),S(step.step_id)),'arguments'),input,results)))),B(observe(n,C('notStarted')),R(stopped()))),
   V('let','raw'),TRY(B(E(X('=',id('raw'),['await',C('call'+index,id('args'),id('dep'+index))]))),B(observe(n,C('unknown',S('threw'))),R(stopped()))),
   V('const','settlement',C('inspectOperationSettlement',id('raw'),S(step.failure_continuation))),observe(n,id('settlement')),
   IF(X('!==',G(id('settlement'),'commit_status'),S('committed')),R(stopped())),
   TRY(B(E(C(G(results,'push'),C(G(mat,'captureResult'),input,S(step.step_id),G(C(G(id('Object'),'getOwnPropertyDescriptor'),id('raw'),S('value')),'value'))))),B(R(stopped('committed-result-invalid'))))
  ));
 }
 statement.push(V('let','value'),TRY(B(E(X('=',id('value'),C(G(mat,'result'),input,results)))),B(R(stopped('result-materialization-failed')))));
 statement.push(R(C('freeze',O(P('status',S('succeeded')),P('value',id('value')),P('evaluation',C('evaluate',observations,ids,['null'])),P('recovery_bindings',['null'])))));
 return arrow(['parameters','executionIdentity','dependencies'],B(...statement),true);
}
function expectedPrepare(e){
 const row=I('row'),intent=I('intent'),bindings=I('bindings'),body=[];
 for(const c of e.compensations){
  const properties=['compensation_id','operation_ref','action_sha256'];
  const binding=O(...['intent_id','plan_digest'].map(k=>P(k,G(intent,k))),P('invocation_identity',G(row,'invocation_identity')),...properties.map(k=>P(k,S(c[k]))),
   P('arguments',C(G(A(G(I('material'),'compensations'),S(c.compensation_id)),'arguments'),I('input'),I('results'))));
  body.push(IF(X('===',G(row,'compensation_id'),S(c.compensation_id)),B(
   IF(X('||',X('!==',G(row,'operation_ref'),S(c.operation_ref)),X('!==',G(row,'action_sha256'),S(c.action_sha256))),R(C('fail',S('compensation identity')))),
   E(C(G(bindings,'push'),F(binding))),['continue',null])));
 }
 body.push(R(C('fail',S('unknown compensation'))));
 return arrow(['input','results','intent'],B(V('const','bindings',L()),['for-of',false,V('const','row'),G(intent,'plan'),B(...body)],
  R(C('freeze',O(P('schema_version',S('domainspec.workflow-recovery-bindings/v1-candidate')),P('intent_id',G(intent,'intent_id')),P('plan_digest',G(intent,'plan_digest')),P('bindings',bindings),P('compensation_execution',['bool',false]),P('authority_effect',S('none')))))));
}
function frozen(node){
 const n=unwrap(node);if(n?.kind===K.StringLiteral)return n.text;if(n?.kind===K.NumericLiteral)return Number(n.text);
 if(n?.kind===K.NullKeyword)return null;if(n?.kind===K.TrueKeyword)return true;if(n?.kind===K.FalseKeyword)return false;
 need(n?.kind===K.CallExpression&&!n.questionDotToken&&json(shape(n.expression))===json(G(I('Object'),'freeze'))&&n.arguments.length===1,'frozen literal');
 const value=unwrap(n.arguments[0]);if(value.kind===K.ArrayLiteralExpression)return Array.from(value.elements,frozen);
 need(value.kind===K.ObjectLiteralExpression,'literal object');const result=Object.create(null);
 for(const p of value.properties){need(p.kind===K.PropertyAssignment&&p.name.kind===K.ComputedPropertyName&&p.name.expression.kind===K.StringLiteral,'literal property');const key=p.name.expression.text;need(!Object.hasOwn(result,key),'duplicate literal property');result[key]=frozen(p.initializer);}return result;
}
try{
 const snapshot=api.updateSnapshot({openProjects:[config]}),project=snapshot.getProject(config);need(project,'missing project');const modules=[];
 for(const relative_path of selected.module_paths){
  const file=path.resolve(selected.module_root,relative_path),row=rows.get(relative_path),e=row.expected,source=project.program.getSourceFile(file),content=fs.readFileSync(file);
  need(source&&!project.program.getSyntacticDiagnostics(file).length,'missing or invalid syntax');
  if(selected.phase==='source')need(hash(content)===row.source_sha256,'Workflow source drift');
  const violations=[],problem=(code,error,node)=>{if(violations.length<64)violations.push({code,name:String(error),offset:node?.pos??0});};
  const check=(code,fn,node)=>{try{fn();}catch(error){problem(code,error.message,node);}};
  const same=(actual,expected,reason)=>need(canonical(actual)===canonical(expected),reason);
  let visits=0;const calls=[],awaits=[],declarations=new Map(),top=new Map(),runtimeImports=[];
  const visit=(n,d=0)=>{
   need(++visits<=1000000&&d<=512,'AST capacity');
   if([K.TypeAliasDeclaration,K.InterfaceDeclaration,K.TypeReference,K.TypeQuery].includes(n.kind))return;
   if(n.kind===K.CallExpression)calls.push(n);if(n.kind===K.AwaitExpression)awaits.push(n);
   if(n.kind===K.VariableDeclaration&&n.name.kind===K.Identifier){const name=identifier(n.name);declarations.set(name,[...(declarations.get(name)??[]),n]);}
   n.forEachChild(c=>visit(c,d+1));
  };visit(source);
  check('module-protocol',()=>{
   for(const statement of source.statements){
    if([K.TypeAliasDeclaration,K.InterfaceDeclaration].includes(statement.kind))continue;
    if(statement.kind===K.ImportDeclaration){
     const c=statement.importClause;if(c?.isTypeOnly)continue;
     need(c&&!c.name&&!statement.attributes&&!statement.assertClause&&statement.moduleSpecifier.kind===K.StringLiteral,'runtime import form');
     if(c.namedBindings?.kind===K.NamespaceImport)runtimeImports.push({path:statement.moduleSpecifier.text,namespace:identifier(c.namedBindings.name)});
     else{need(c.namedBindings?.kind===K.NamedImports,'named imports');const elements=c.namedBindings.elements.filter(i=>!i.isTypeOnly);if(!elements.length)continue;
      need(elements.length===1,'one imported callable');const i=elements[0];runtimeImports.push({path:statement.moduleSpecifier.text,symbol:identifier(i.propertyName??i.name),local:identifier(i.name)});}
     continue;
    }
    if(statement.kind===K.ExportDeclaration&&statement.isTypeOnly)continue;
    if(statement.kind===K.FunctionDeclaration){need(identifier(statement.name)==='inspectOperationSettlement'&&json(statement.modifiers?.map(m=>K[m.kind]))==='["ExportKeyword"]','support callable export');need(!top.has('inspectOperationSettlement'),'duplicate helper');top.set('inspectOperationSettlement',statement);continue;}
    need(statement.kind===K.VariableStatement&&statement.declarationList.declarations.length===1&&/^const\b/.test(statement.declarationList.getText()),'top-level immutable binding');
    const d=statement.declarationList.declarations[0];need(d.name.kind===K.Identifier,'top-level binding');const name=identifier(d.name);
    need(!top.has(name),'duplicate helper');top.set(name,d.initializer);
    same(statement.modifiers?.map(m=>K[m.kind])??[],name==='execute'?['ExportKeyword']:[],'runtime export identity');
   }
   same([...top.keys()].sort(),['wf','policyHash','outcomeContract','prefixTemplates','fail','own','text','identity','unknown','notStarted','inspectOperationSettlement','freeze','canonical','digest','observe','recover','evaluate','imported','stopped','prepareBindings','execute'].sort(),'exact runtime helpers');
   same(runtimeImports,[{path:'node:crypto',symbol:'createHash',local:'createHash'},{path:e.material_path,namespace:'material'},...e.imports.map(i=>({path:i.path,symbol:i.symbol,local:i.local}))],'exact forward runtime imports');
   for(const name of ['material','createHash',...e.imports.map(i=>i.local)])need(!declarations.has(name),'shadowed import:'+name);
   for(const name of top.keys())need((declarations.get(name)?.length??0)===(name==='inspectOperationSettlement'?0:1),'shadowed helper:'+name);
  },source);
  check('execute-protocol',()=>same(shape(top.get('execute')),expectedExecute(e),'complete async execution protocol'),top.get('execute'));
  check('compensation-protocol',()=>same(shape(top.get('prepareBindings')),expectedPrepare(e),'typed compensation metadata protocol'),top.get('prepareBindings'));
  check('metadata-protocol',()=>{
   same(frozen(top.get('wf')),e.wf,'Workflow identity/steps');same(frozen(top.get('policyHash')),e.policy_sha256,'selected policy');same(frozen(top.get('outcomeContract')),e.outcome_contract_sha256,'outcome contract');
   same(frozen(top.get('prefixTemplates')),e.prefix_templates,'independent recovery prefix templates');
  },top.get('wf'));
  check('call-scope',()=>{
   const execute=top.get('execute'),within=n=>n.pos>=execute.pos&&n.end<=execute.end;
   need(awaits.length===e.steps.length&&awaits.every(within),'exact await ownership');
   const protectedCalls=calls.filter(c=>{const n=unwrap(c.expression);return n?.kind===K.Identifier&&/^(?:call[0-9]+|forward[0-9]+)$/.test(identifier(n));});
   need(protectedCalls.length===e.steps.length&&protectedCalls.every(within),'exact forward call ownership');
  },source);
  check('recovery-boundaries',()=>{
   const evaluate=top.get('evaluate'),recover=top.get('recover');
   need(evaluate?.kind===K.ArrowFunction&&recover?.kind===K.ArrowFunction,'metadata helper form');
   same(Array.from(evaluate.parameters,p=>identifier(p.name)),['observations','ids','local_error'],'evaluation inputs');
   same(Array.from(recover.parameters,p=>identifier(p.name)),['completed','failed','ids'],'recovery inputs');
   const prefix=evaluate.body.statements[1];
   same(shape(prefix),V('const','completed_step_ids',C(G(C(G(I('observations'),'filter'),arrow(['r'],X('===',G(G(I('r'),'settlement'),'commit_status'),S('committed')))),'map'),arrow(['r'],G(I('r'),'step_id')))),'committed-only prefix');
   const statements=recover.body.statements;
   same(shape(statements[0]),V('const','template',A(I('prefixTemplates'),G(I('completed'),'length'))),'failure prefix index');
   same(shape(statements[3]),IF(X('===',G(G(I('failed'),'settlement'),'commit_status'),S('indeterminate')),
    R(C('freeze',O(['spread-property',I('common')],P('status',S('reconciliation-required')),P('workflow_evaluation_result',['null']),P('recovery_intent',['null']),P('unknown_step_id',G(I('failed'),'step_id')))))),'uncertainty before recovery');
   const intents=declarations.get('intent_id');need(intents?.length===1&&intents[0].pos>statements[3].end&&intents[0].end<recover.end,'intent after uncertainty boundary');
  },top.get('recover'));
  modules.push({relative_path,source_sha256:hash(content),violations});
 }
 snapshot.dispose();process.stdout.write(json({schema_version:'domainspec.workflow-orchestration-observation/v1-candidate',phase:selected.phase,definition_sha256:pin,modules}));
}finally{api.close();}
`;
