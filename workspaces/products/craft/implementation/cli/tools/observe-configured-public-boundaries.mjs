import fs from 'node:fs';
import path from 'node:path';
import {API} from '/opt/node-toolchain/node_modules/typescript/dist/api/sync/api.js';
import {SyntaxKind as K} from '/opt/node-toolchain/node_modules/typescript/dist/ast/index.js';
// Independent native syntax observation from authored fixture obligations, not renderer output.
const [root,expectedPath]=process.argv.slice(2),expected=JSON.parse(fs.readFileSync(expectedPath,'utf8'));
const api=new API({cwd:root}),need=(condition,reason)=>{if(!condition)throw Error(reason)},text=n=>n?.getText(),compact=n=>text(n)?.replace(/\s+/g,'');
try{
 const config=path.join(root,'tsconfig.json'),snapshot=api.updateSnapshot({openProjects:[config]}),project=snapshot.getProject(config);
 const source=p=>project.program.getSourceFile(path.join(root,p));
 const inspect=p=>{
  const file=source(p);need(file,'missing artifact:'+p);const declarations=new Map(),types=new Map(),imports=[],calls=[];
  const visit=n=>{
   if(n.kind===K.VariableDeclaration)declarations.set(text(n.name),n.initializer);
   if(n.kind===K.TypeAliasDeclaration)types.set(text(n.name),n.type);
   if(n.kind===K.ImportDeclaration)imports.push(n);
   if(n.kind===K.CallExpression)calls.push(n);
   need(n.kind!==K.ClassDeclaration&&n.kind!==K.ClassExpression,'class replacement');
   if(n.kind===K.Identifier)need(!['fetch','Date','process','eval','Function','setTimeout','setInterval','dispatch','publish','begin','commit','rollback'].includes(text(n)),'hidden effect');
   n.forEachChild(visit);
  };file.forEachChild(visit);return {file,declarations,types,imports,calls};
 };
 for(const contract of expected.interfaces){
  const file=inspect(contract.path);need(file.imports.length===0,'standalone Interface');
  need(file.types.has('Interface')&&file.types.has('PublicContracts'),'structural public types');
  const structural=file.types.get('Interface');need(text(structural).startsWith('Readonly<'),'readonly Interface');
  const publicTypes=file.types.get('PublicContracts').typeArguments[0].members;
  const response=text(publicTypes.find(member=>member.name.text==='response')?.type);need(response,'response type');
  for(const member of contract.members)need(compact(structural).includes(JSON.stringify(member)+':(request:string)=>Promise<'+response+'>'),'declared member signature');
  const contracts=file.declarations.get('publicContracts');need(text(contracts.expression)==='Object.freeze','frozen public protocols');
  const keys=contracts.arguments[0].properties.map(p=>p.name.expression.text).sort();need(JSON.stringify(keys)===JSON.stringify([...contract.contracts].sort()),'exact contract exports');
  need(!file.calls.some(c=>/\.(listen|send|execute|make)$/.test(text(c.expression))),'Interface implementation');
 }
 const mapping=inspect(expected.provider_path),map=mapping.declarations.get('map');
 need(map?.kind===K.ArrowFunction&&!map.modifiers?.some(m=>m.kind===K.AsyncKeyword),'one synchronous projection');
 need(compact(mapping.types.get('Result'))==='Public0.PublicContracts["response"]','exact public result type');
 need(mapping.imports.length===expected.imports.length,'exact import count');
 expected.imports.forEach((i,index)=>{const actual=mapping.imports[index];need(actual.moduleSpecifier.text===i.path&&text(actual.importClause.namedBindings.name)===i.alias,'qualified import');});
 const body=map.body.statements,declarations=new Map();for(const s of body)if(s.kind===K.VariableStatement)for(const d of s.declarationList.declarations)declarations.set(text(d.name),d.initializer);
 need(compact(declarations.get('d'))==='ruleData(parameters,'+JSON.stringify(expected.inputs.map(i=>i.name))+')','closed inputs');
 expected.inputs.forEach((input,i)=>need(compact(declarations.get('p'+i))===input.normalizer+'.normalize(d['+JSON.stringify(input.name)+']!.value)','input normalization'));
 expected.fields.forEach((field,i)=>need(compact(declarations.get('v'+i))===field.normalizer+'.normalize('+field.expression+')','exact field projection'));
 const returns=body.filter(s=>s.kind===K.ReturnStatement);need(returns.length===1,'one return');
 need(compact(returns[0].expression)==='Object.freeze({'+expected.fields.map((f,i)=>'['+JSON.stringify(f.name)+']:v'+i).join(',')+'})','owned exact result');
 const pins=mapping.file.statements.filter(s=>s.kind===K.IfStatement);need(pins.length===expected.imports.length,'Interface identity pins');
 expected.imports.forEach((i,index)=>need(compact(pins[index].expression).startsWith(i.alias+'.descriptor.selector!=='+JSON.stringify(i.selector))&&compact(pins[index].expression).split('||').length===4&&compact(pins[index]).includes('MAPPING_INTERFACE_BINDING'),'qualified identity pin'));
 const facade=inspect(expected.facade_path);need(facade.imports.length===1&&facade.imports[0].moduleSpecifier.text===expected.provider_import,'exact facade import');
 need(compact(facade.declarations.get(expected.callable)).startsWith('Object.freeze(Object.assign(map,{descriptor:'),'single bound Mapping facade');
 console.log(JSON.stringify({result:'pass',interfaces:expected.interfaces.length,fields:expected.fields.length}));
}catch(error){console.log(JSON.stringify({result:'fail',error:error.message}));process.exitCode=1;}finally{api.close();}
