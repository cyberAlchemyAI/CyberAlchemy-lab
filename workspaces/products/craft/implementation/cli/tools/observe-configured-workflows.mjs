import fs from 'node:fs';
import path from 'node:path';
import {API} from '/opt/node-toolchain/node_modules/typescript/dist/api/sync/api.js';
import {SyntaxKind as K} from '/opt/node-toolchain/node_modules/typescript/dist/ast/index.js';
// Authored occurrence/binding evidence, not generator execution or descriptor-only approval.
const [root,expectedPath]=process.argv.slice(2),expected=JSON.parse(fs.readFileSync(expectedPath,'utf8'));
const api=new API({cwd:root}),need=(c,m)=>{if(!c)throw Error(m)},txt=n=>n?.getText(),compact=n=>txt(n)?.replace(/\s+/g,'');
function frozen(n){
 if(n?.kind===K.StringLiteral)return n.text;
 if(n?.kind===K.NumericLiteral)return Number(n.text);
 if(n?.kind===K.TrueKeyword)return true;if(n?.kind===K.FalseKeyword)return false;if(n?.kind===K.NullKeyword)return null;
 need(n?.kind===K.CallExpression&&txt(n.expression)==='Object.freeze'&&n.arguments.length===1,'frozen literal');
 const v=n.arguments[0];if(v.kind===K.ArrayLiteralExpression)return v.elements.map(frozen);
 need(v.kind===K.ObjectLiteralExpression,'literal object');const o=Object.create(null);
 for(const p of v.properties){need(p.kind===K.PropertyAssignment&&p.name.kind===K.ComputedPropertyName&&p.name.expression.kind===K.StringLiteral,'literal property');o[p.name.expression.text]=frozen(p.initializer);}return o;
}
const canonical=v=>JSON.stringify(v,(_,x)=>x&&typeof x==='object'&&!Array.isArray(x)?Object.fromEntries(Object.entries(x).sort(([a],[b])=>a<b?-1:a>b?1:0)):x);
try{
 const snapshot=api.updateSnapshot({openProjects:[path.join(root,'tsconfig.json')]}),project=snapshot.getProject(path.join(root,'tsconfig.json'));
 const source=project.program.getSourceFile(path.join(root,expected.provider_path));
 need(source,'generated source');const declarations=new Map(),calls=[],awaits=[],imports=new Map();
 const visit=n=>{
  if(n.kind===K.VariableDeclaration)declarations.set(txt(n.name),n.initializer);
  if(n.kind===K.CallExpression)calls.push(n);
  if(n.kind===K.AwaitExpression)awaits.push(n);
  need(n.kind!==K.ClassDeclaration,'class Workflow');
  if(n.kind===K.Identifier)need(!['fetch','Date','process','eval','Function','setTimeout','setInterval','store','begin','commit','rollback','publish','dispatch','clock'].includes(txt(n)),'undeclared effect');
  n.forEachChild(visit);
 };source.forEachChild(visit);
 for(const s of source.statements)if(s.kind===K.ImportDeclaration&&s.importClause?.namedBindings?.elements)for(const i of s.importClause.namedBindings.elements)imports.set(txt(i.name),{symbol:txt(i.propertyName??i.name),path:s.moduleSpecifier.text});
 const forward=[...new Set(expected.occurrences.steps.map(s=>s.operation_ref))].sort();
 need([...imports].filter(([,i])=>i.symbol.startsWith('operation')).every(([name])=>/^forward[0-9]+$/.test(name)),'no recovery Operation import');
 for(const [i,selector]of forward.entries()){
  const [feature,id]=selector.split(':'),relative=path.posix.relative(path.posix.dirname(expected.provider_path),expected.module_root+'/features/'+feature+'/src/application/operations/'+id+'.js');
  const selected=imports.get('forward'+i);
  need(selected?.path===(relative.startsWith('.')?relative:'./'+relative)&&selected.symbol==='operation'+id.split('-').map(p=>p[0].toUpperCase()+p.slice(1)).join(''),'exact Operation import');
  need(txt(declarations.get('call'+i))==='forward'+i,'captured callable');
 }
 need([...imports.keys()].filter(k=>k.startsWith('forward')).length===forward.length,'no compensation import');
 const execute=declarations.get('execute');need(execute?.kind===K.ArrowFunction&&execute.modifiers?.some(m=>m.kind===K.AsyncKeyword),'async callable');
 const body=compact(execute.body),blocks=execute.body.statements.filter(n=>n.kind===K.Block);
 need(blocks.length===expected.occurrences.steps.length,'exact occurrence blocks');
 const forwardCalls=calls.filter(c=>/^call[0-9]+$/.test(txt(c.expression)));
 need(forwardCalls.length===blocks.length,'exact forward call count');
 need(awaits.length===blocks.length&&awaits.every(n=>n.expression.kind===K.CallExpression&&/^call[0-9]+$/.test(txt(n.expression.expression))),'one await per occurrence');
 need(body.indexOf('material.capture(parameters)')<body.indexOf('awaitcall'),'capture before suspension');
 const pinCalls=calls.filter(c=>txt(c.expression)==='imported');
 need(pinCalls.length===forward.length,'exact dependency pins');
 for(const [i,selector]of forward.entries()){
  const p=pinCalls[i];need(txt(p.arguments[0])==='call'+i&&p.arguments[1].text===selector&&p.arguments[2].text===expected.actions[selector].action_sha256&&p.arguments[3].text===expected.actions[selector].descriptor_sha256,'action and descriptor pins');
 }
 blocks.forEach((block,index)=>{
  const step=expected.occurrences.steps[index],b=compact(block),i=forward.indexOf(step.operation_ref),call=forwardCalls[index];
  need(b.includes('args=material.steps['+JSON.stringify(step.step_id)+'].arguments(input,results)'),'step argument binding');
  need(b.includes('raw=awaitcall'+i+'(args,dep'+i+')')&&txt(call.expression)==='call'+i,'source call order and dependency');
  need(b.includes('observations.push(observe('+index+',settlement))'),'occurrence observation');
  need(b.includes('if(settlement.commit_status!=="committed")returnstopped(input,results,observations,ids);'),'terminal settlement stop');
  need(b.indexOf('if(settlement.commit_status!=="committed")')<b.indexOf('results.push(material.captureResult'),'validate only after commit');
  need(b.includes('results.push(material.captureResult(input,'+JSON.stringify(step.step_id)+',Object.getOwnPropertyDescriptor(raw,"value")!.value))'),'exact result capture');
  need(b.includes('observe('+index+',unknown("threw"))')&&b.includes('observe('+index+',notStarted())'),'unknown and not-started distinction');
 });
 need(body.includes('value=material.result(input,results)')&&body.indexOf('value=material.result(input,results)')>body.lastIndexOf('raw=awaitcall'),'final materialization after calls');
 need(body.includes('returnstopped(input,results,observations,ids,"committed-result-invalid")')&&body.includes('returnstopped(input,results,observations,ids,"result-materialization-failed")'),'local error boundaries');
 const wf=frozen(declarations.get('wf'));need(canonical(wf)===canonical(expected.wf),'Workflow identity and ordered steps');
 need(frozen(declarations.get('policyHash'))===expected.policy_sha256,'selected recovery identity');
 need(canonical(frozen(declarations.get('prefixTemplates')))===canonical(expected.prefix_templates),'exact selected failure-prefix plans');
 need(compact(declarations.get('evaluate').body).includes("observations.filter(r=>r.settlement.commit_status==='committed').map(r=>r.step_id)"),'only committed prefix');
 const recover=compact(declarations.get('recover').body);
 need(recover.includes("if(failed.settlement.commit_status==='indeterminate')return")&&recover.indexOf("if(failed.settlement.commit_status==='indeterminate')")<recover.indexOf('constintent_id='),'uncertainty before intent');
 const prepare=compact(declarations.get('prepareBindings').body);
 for(const c of expected.occurrences.compensations)need(prepare.includes('material.compensations['+JSON.stringify(c.compensation_id)+'].arguments(input,results)'),'typed compensation preparation');
 need(!calls.some(c=>/\.(execute|make|commit|begin|rollback|publish|dispatch)$/.test(txt(c.expression))),'no hidden effect call');
 console.log(JSON.stringify({result:'pass',steps:blocks.length}));
}catch(e){console.log(JSON.stringify({result:'fail',error:e.message}));process.exitCode=1;}finally{api.close();}
