import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';
import {validStructuredRuleSupport} from '/structured-rule-support-observer.mjs';
// Independent native AST observer. Reads authored expectations, never generators.
const compilerRoot='/opt/node-toolchain/node_modules/typescript';
if(JSON.parse(fs.readFileSync(path.join(compilerRoot,'package.json'),'utf8')).version!=='7.0.2')throw Error('unselected compiler');
const {API}=await import(pathToFileURL(path.join(compilerRoot,'dist/api/sync/api.js')).href);
const {SyntaxKind:K}=await import(pathToFileURL(path.join(compilerRoot,'dist/ast/index.js')).href);
const [configPath,expectedPath]=process.argv.slice(2),e=JSON.parse(fs.readFileSync(expectedPath,'utf8')),root=path.dirname(configPath),errors=[];
const text=n=>n?.getText(),compact=s=>s?.replace(/\s+/g,''),q=JSON.stringify,hash=s=>createHash('sha256').update(s).digest('hex');
const canonical=v=>JSON.stringify(v,(_,x)=>x&&typeof x==='object'&&!Array.isArray(x)?Object.fromEntries(Object.entries(x).sort(([a],[b])=>a<b?-1:a>b?1:0)):x);
function literal(n){
 if(n?.kind===K.StringLiteral)return n.text;if(n?.kind===K.NumericLiteral)return Number(n.text);if(n?.kind===K.TrueKeyword)return true;if(n?.kind===K.FalseKeyword)return false;if(n?.kind===K.NullKeyword)return null;
 if(n?.kind!==K.CallExpression||text(n.expression)!=='Object.freeze'||n.arguments.length!==1)throw Error('descriptor-literal');
 const v=n.arguments[0];if(v.kind===K.ArrayLiteralExpression)return v.elements.map(literal);if(v.kind!==K.ObjectLiteralExpression)throw Error('descriptor-object');
 const result=Object.create(null);for(const p of v.properties){if(p.kind!==K.PropertyAssignment||p.name.kind!==K.ComputedPropertyName||p.name.expression.kind!==K.StringLiteral||Object.hasOwn(result,p.name.expression.text))throw Error('descriptor-key');result[p.name.expression.text]=literal(p.initializer);}return result;
}
const api=new API({cwd:root});
try{
 const snapshot=api.updateSnapshot({openProjects:[configPath]}),project=snapshot.getProject(configPath);if(!project)throw Error('missing project');
 const provider=project.program.getSourceFile(path.resolve(root,e.provider_path)),binding=project.program.getSourceFile(path.resolve(root,e.relative_path));if(!provider||!binding)throw Error('missing source');
 const imports=provider.statements.filter(s=>s.kind===K.ImportDeclaration).flatMap(s=>s.importClause?.namedBindings?.elements?.map(b=>({path:s.moduleSpecifier.text,symbol:text(b.propertyName??b.name),local:text(b.name)}))??[]);
 const expectedImports=e.rules.map((r,i)=>({path:r.path,symbol:r.symbol,local:'condition'+i}));if(canonical(imports)!==canonical(expectedImports))errors.push('guard-imports');
 const raw=fs.readFileSync(path.resolve(root,e.provider_path),'utf8');
 if(!validStructuredRuleSupport(raw))errors.push('support-source-drift');
 const variables=new Map(provider.statements.filter(s=>s.kind===K.VariableStatement).flatMap(s=>s.declarationList.declarations).map(d=>[text(d.name),d.initializer]));
 const c=e.contract,states=[...c.states].sort(),triggers=[...new Set(c.transitions.map(t=>t.trigger_event_ref))].sort();
 if(variables.get('initialState')?.text!==c.initial)errors.push('initial-state');
 const arrow=variables.get('reduce');if(arrow?.kind!==K.ArrowFunction||arrow.parameters.length!==3||arrow.modifiers?.length)throw Error('reducer-form');
 if(compact(text(arrow.type))!=='Outcome'||arrow.parameters.map(p=>text(p.name)).join(',')!=='state,trigger,parameters')errors.push('reducer-signature');
 const scope=new Map(c.inputs.map((p,i)=>[p.name,'p'+i]));
 // Closed scalar witness dialect; unsupported expectations fail rather than guess.
 const expression=v=>{if(v.op==='path'&&v.properties.length===0&&scope.has(v.root))return scope.get(v.root);if(v.op==='literal')return v.type==='UInt64'?v.value+'n':q(v.value);throw Error('unsupported observer expression');};
 const empty='Object.freeze([] as const)',rejection=reason=>'return Object.freeze({status:"rejected",state,reason:'+q(reason)+',output_intents:'+empty+'});';
 const expected=[
  'if(typeof state!=="string"||!'+q(states)+'.includes(state)||typeof trigger!=="string"||!'+q(triggers)+'.includes(trigger))throw new TypeError("STATE_MACHINE_INPUT");',
  'checkData(parameters);','const d=ruleData(parameters,'+q(c.inputs.map(p=>p.name))+');',
  'if(Object.keys(d).length!=='+c.inputs.length+')throw new TypeError("STATE_MACHINE_INPUT");',
  ...c.inputs.map((p,i)=>{if(p.type.kind!=='scalar')throw Error('unsupported observer parameter');return 'const p'+i+'=rule'+p.type.name+'.normalize(d['+q(p.name)+']!.value);';}),
  ...c.transitions.map(t=>{
   let guard='';if(t.guard){const index=e.rules.findIndex(r=>r.selector===t.guard.selector);if(index<0)throw Error('missing expected Rule');guard='if(!condition'+index+'({'+[...t.guard.arguments].sort((a,b)=>a.parameter<b.parameter?-1:1).map(a=>'['+q(a.parameter)+']:'+expression(a.value)).join(',')+'}))'+rejection('guard');}
   return 'if(state==='+q(t.source_state)+'&&trigger==='+q(t.trigger_event_ref)+'){'+guard+'return Object.freeze({status:"transitioned",state:'+q(t.target_state)+',transition_id:'+q(t.transition_id)+',output_intents:Object.freeze(['+t.output_intents.map(o=>'Object.freeze({slot:'+q(o.slot)+',event_ref:'+q(o.event_ref)+'})').join(',')+'] as const)});}';
  }),rejection('no-transition')
 ];
 const observed=arrow.body.statements.map(s=>compact(text(s)));if(canonical(observed)!==canonical(expected.map(compact)))errors.push('authored-transition-body');
 const aliases=new Map(provider.statements.filter(s=>s.kind===K.TypeAliasDeclaration).map(s=>[text(s.name),compact(text(s.type))]));
 if(aliases.get('State')!==states.map(q).join('|')||aliases.get('Trigger')!==triggers.map(q).join('|'))errors.push('closed-symbol-unions');
 const successTypes=c.transitions.map(t=>'Readonly<{status:"transitioned";state:'+q(t.target_state)+';transition_id:'+q(t.transition_id)+';output_intents:readonly ['+t.output_intents.map(o=>'Readonly<{slot:'+q(o.slot)+';event_ref:'+q(o.event_ref)+'}>').join(',')+']}>').join('|');
 if(aliases.get('Outcome')!==compact('('+successTypes+')|Readonly<{status:"rejected";state:State;reason:"guard"|"no-transition";output_intents:readonly []}>'))errors.push('outcome-type');
 const providerImport='./'+path.basename(e.provider_path).replace(/\.ts$/,'.js');
 const prefix=['import {reduce,initialState} from '+q(providerImport)+';','export type {State,Trigger,Parameters,Outcome} from '+q(providerImport)+';','export {initialState};'];
 if(binding.statements.length!==4||prefix.some((s,i)=>compact(text(binding.statements[i]))!==compact(s)))errors.push('binding-import-export-perimeter');
 const visit=n=>{if([K.ClassDeclaration,K.ClassExpression,K.AwaitExpression,K.ImportKeyword].includes(n.kind))errors.push('impure-form');if(n.kind===K.Identifier&&['globalThis','process','Date','Math','Promise','fetch','require','eval','Function','setTimeout','setInterval','queueMicrotask','WebSocket'].includes(text(n)))errors.push('ambient-effect');n.forEachChild(visit);};visit(provider);
 const exports=binding.statements.filter(s=>s.kind===K.VariableStatement).flatMap(s=>s.declarationList.declarations);if(exports.length!==1||text(exports[0].name)!==e.callable)throw Error('bound-export');
 const wrap=exports[0].initializer;if(wrap.kind!==K.CallExpression||text(wrap.expression)!=='Object.freeze'||wrap.arguments.length!==1)throw Error('frozen-callable');
 const assign=wrap.arguments[0];if(assign.kind!==K.CallExpression||text(assign.expression)!=='Object.assign'||text(assign.arguments[0])!=='reduce'||assign.arguments.length!==2)throw Error('bound-reducer');
 const props=assign.arguments[1].properties;if(props.length!==1||text(props[0].name)!=='descriptor')throw Error('bound-descriptor');
 const d=literal(props[0].initializer),{descriptor_sha256,...body}=d;
 if(descriptor_sha256!==hash(canonical(body))||d.provider.sha256!==hash(fs.readFileSync(path.resolve(root,e.provider_path),'utf8')))errors.push('binding-hashes');
 if(d.contract_sha256!==hash(canonical(c))||canonical(d.contract)!==canonical(c))errors.push('authored-contract');
 if(d.effect_contract!=='none'||d.output_semantics!=='ordered-unexecuted-intents'||d.trigger_semantics!=='explicit-event-input-symbol')errors.push('bound-meaning');
 if(canonical(d.event_dependencies.map(x=>({selector:x.selector,body_sha256:x.body_sha256,source_sha256:x.source.sha256})))!==canonical(e.events))errors.push('Event-source-evidence');
 for(const r of d.rule_dependencies)if(r.sha256!==hash(fs.readFileSync(path.resolve(root,r.path),'utf8')))errors.push('Rule-source-binding');
}catch(error){errors.push(error.message);}finally{api.close();}
process.stdout.write(JSON.stringify({result:errors.length?'fail':'pass',errors})+'\n');if(errors.length)process.exitCode=1;
