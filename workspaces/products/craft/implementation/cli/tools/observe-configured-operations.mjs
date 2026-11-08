import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';

// Independent source observer: authored graph nodes and action bindings are the
// semantic inputs. Neither generator nor generated module is executed here.
const compilerRoot='/opt/node-toolchain/node_modules/typescript';
if(JSON.parse(fs.readFileSync(path.join(compilerRoot,'package.json'),'utf8')).version!=='7.0.2')throw Error('unselected compiler');
const {API}=await import(pathToFileURL(path.join(compilerRoot,'dist/api/sync/api.js')).href);
const {SyntaxKind:K}=await import(pathToFileURL(path.join(compilerRoot,'dist/ast/index.js')).href);
const [configPath,expectedPath]=process.argv.slice(2),expected=JSON.parse(fs.readFileSync(expectedPath,'utf8'));
const hash=s=>createHash('sha256').update(s).digest('hex'),q=JSON.stringify;
const canonical=v=>JSON.stringify(v,(_,x)=>x&&typeof x==='object'&&!Array.isArray(x)?Object.fromEntries(Object.entries(x).sort(([a],[b])=>a<b?-1:a>b?1:0)):x);
const compact=s=>s.replace(/\s+/g,''),text=n=>n?.getText(),pascal=s=>s.split('-').map(w=>w[0].toUpperCase()+w.slice(1)).join('');
const need=(condition,message)=>{if(!condition)throw Error(message);};
function frozen(n){
  if(n?.kind===K.StringLiteral)return n.text;
  if(n?.kind===K.NumericLiteral)return Number(n.text);
  if(n?.kind===K.TrueKeyword)return true;if(n?.kind===K.FalseKeyword)return false;if(n?.kind===K.NullKeyword)return null;
  need(n?.kind===K.CallExpression&&text(n.expression)==='Object.freeze'&&n.arguments.length===1,'frozen descriptor');const v=n.arguments[0];
  if(v.kind===K.ArrayLiteralExpression)return v.elements.map(frozen);
  need(v.kind===K.ObjectLiteralExpression,'literal descriptor');const result=Object.create(null);
  for(const p of v.properties){need(p.kind===K.PropertyAssignment&&p.name.kind===K.ComputedPropertyName&&p.name.expression.kind===K.StringLiteral&&!Object.hasOwn(result,p.name.expression.text),'literal member');result[p.name.expression.text]=frozen(p.initializer);}return result;
}
const api=new API({cwd:path.dirname(configPath)}),errors=[],observations=[];
try{
  const snapshot=api.updateSnapshot({openProjects:[configPath]}),project=snapshot.getProject(configPath);need(project,'missing project');
  for(const e of expected){try{
    const nodeBytes=fs.readFileSync(e.source_path,'utf8'),source=JSON.parse(nodeBytes),bindings=JSON.parse(fs.readFileSync(e.bindings_path,'utf8'));
    const nodes=new Map(e.node_paths.map(p=>{const n=JSON.parse(fs.readFileSync(p,'utf8'));return [n.feature_id+':'+n.node_id,n];}));
    const root=path.dirname(configPath),providerPath=path.resolve(root,e.provider_path),wrapperPath=path.resolve(root,e.relative_path),bytes=fs.readFileSync(providerPath,'utf8');
    const provider=project.program.getSourceFile(providerPath),wrapper=project.program.getSourceFile(wrapperPath);need(provider&&wrapper,'missing native source');
    need(!project.program.getSyntacticDiagnostics(providerPath).length&&!project.program.getSyntacticDiagnostics(wrapperPath).length,'native syntax');
    const declarations=new Map(),calls=[],awaited=[],ifs=[],imports=new Map();
    const visit=n=>{if(n.kind===K.VariableDeclaration)declarations.set(text(n.name),n.initializer);if(n.kind===K.CallExpression)calls.push(n);if(n.kind===K.AwaitExpression)awaited.push(n);if(n.kind===K.IfStatement)ifs.push(n);if(n.kind===K.ClassDeclaration)throw Error('class action');if(n.kind===K.Identifier&&['eval','Function','fetch','process','console','Date','setTimeout','setInterval'].includes(text(n)))throw Error('ambient effect');n.forEachChild(visit);};provider.forEachChild(visit);
    for(const s of provider.statements)if(s.kind===K.ImportDeclaration&&s.importClause?.namedBindings?.elements)for(const i of s.importClause.namedBindings.elements)imports.set(text(i.name),{symbol:text(i.propertyName??i.name),path:s.moduleSpecifier.text});
    const fn=declarations.get('execute');need(fn?.kind===K.ArrowFunction&&fn.modifiers?.some(m=>m.kind===K.AsyncKeyword)&&fn.parameters.length===2,'async action signature');
    const body=compact(text(fn.body));
    const count=expression=>calls.filter(c=>text(c.expression)===expression).length;
    const awaitCount=expression=>awaited.filter(a=>a.expression.kind===K.CallExpression&&text(a.expression.expression)===expression).length;
    need(count('dependencies.store.begin')===1&&awaitCount('dependencies.store.begin')===1,'awaited begin');
    need(count('transaction.commit')===1&&awaitCount('transaction.commit')===1,'one awaited commit');
    need(count('transaction.rollback')===1&&awaitCount('transaction.rollback')===1,'one rollback site');
    need(count('transaction.read')===bindings.reads.length&&awaitCount('transaction.read')===bindings.reads.length,'transactional reads');
    need(body.indexOf('captureData(parameters)')>=0&&body.indexOf('captureData(parameters)')<body.indexOf('awaitdependencies.store.begin()'),'capture before suspension');
    need(body.includes('commitAttempted=true;constreceipt=awaittransaction.commit(batch);'),'commit uncertainty checkpoint');
    need(body.includes('returncommitAttempted?failure("indeterminate","COMMIT_UNCERTAIN"):abort("failed","OPERATION_FAILED");'),'no rollback after uncertain commit');
    const stages=['read','guard','write-validation','event','result','commit'].map(s=>body.indexOf('stage='+q(s)+';'));need(stages.every((n,i)=>n>=0&&(!i||n>stages[i-1])),'action checkpoint order');
    const scope=new Map(bindings.inputs.map((p,i)=>[p.name,{type:p.type,code:'p'+i}]));
    const expression=v=>{
      if(v.op==='literal')return v.type==='UInt64'?String(v.value)+'n':q(v.value);
      need(v.op==='path','observer requires independently supported value form');let row=scope.get(v.root);need(row,'unknown input');let {type,code}=row;
      for(const p of v.properties){need(type.kind==='named','observer path profile');const declaration=nodes.get(type.selector)?.body.typed_contract,field=declaration?.properties?.find(f=>f.ontology_property===p);need(field,'missing authored property');code+='['+q(field.name)+']';type=field.type;}return code;
    };
    for(const [i,r]of bindings.reads.entries()){
      const key=declarations.get('key'+i);need(key?.kind===K.CallExpression&&compact(text(key.arguments[0]))===compact(expression(r.key)),'read key binding');
      const raw=compact(text(declarations.get('raw'+i)));need(raw==='awaittransaction.read(Object.freeze({slot:'+q(r.slot)+',target:'+q(r.target)+',key:key'+i+'}))','read target binding');
      const identity=nodes.get(r.target)?.body.typed_contract?.properties.find(p=>p.identity);need(identity,'Entity identity');
      need(ifs.some(n=>compact(text(n.expression)).includes('.key(read'+i+'['+q(identity.name)+'])!==')&&compact(text(n.thenStatement))==='returnabort("failed","READ_IDENTITY_MISMATCH");'),'read identity guard');
      scope.set(r.parameter,{type:{kind:'named',selector:r.target},code:'read'+i});
    }
    for(const [i,g]of bindings.guards.entries()){
      const dependency=imports.get('guard'+i),id=g.selector.split(':')[1];need(dependency?.symbol==='rule'+pascal(id)&&dependency.path.endsWith('/rules/'+id+'.js'),'declared Rule import');
      const call='guard'+i+'({'+g.arguments.map(a=>'['+q(a.parameter)+']:'+expression(a.value)).join(',')+'})';
      need(count('guard'+i)===1&&ifs.some(n=>compact(text(n.expression))==='!'+compact(call)&&compact(text(n.thenStatement))==='returnabort("rejected",'+q('RULE_REJECTED:'+g.selector)+');'),'guard arguments and outcome');
    }
    for(const [i,w]of bindings.writes.entries()){
      const v=declarations.get('write'+i);need(v?.kind===K.CallExpression&&compact(text(v.arguments[0]))===compact(expression(w.value)),'write value binding');
      const validation=calls.filter(c=>/^own\d+$/.test(text(c.expression))&&c.arguments.length===1&&text(c.arguments[0])==='write'+i);need(validation.length===1,'owned write validation');
      const validator=declarations.get(text(validation[0].expression));need(validator?.kind===K.ArrowFunction&&compact(text(validator.body)).includes('if(!result.ok)thrownewTypeError(')&&compact(text(validator.body)).includes('returnresult.value;'),'factory failure propagation');
      need(body.includes('Object.freeze({slot:'+q(w.slot)+',target:'+q(w.target)+',mode:'+q(w.mode)+',value:write'+i+'})'),'write batch binding');
    }
    const eventTargets=[...new Set(bindings.events.map(e=>e.target))].sort();
    for(const [i,event]of bindings.events.entries()){
      const index=eventTargets.indexOf(event.target),dependency=imports.get('makeEvent'+index),id=event.target.split(':')[1],eventNode=nodes.get(event.target);
      need(dependency?.symbol==='event'+pascal(id)&&dependency.path.endsWith('/events/'+id+'.js'),'declared Event import');
      const call='makeEvent'+index+'(captured['+q(event.parameter)+']asEvent'+index+'Input'+(eventNode.body.occurred_at_policy==='generated'?',clocks['+q(event.slot)+']':'')+')';
      need(compact(text(declarations.get('event'+i)))===call,'Event occurrence input and clock');
      need(body.includes('Object.freeze({slot:'+q(event.slot)+',target:'+q(event.target)+',value:event'+i+'})'),'Event batch binding');
    }
    const result=declarations.get('result');need(result?.kind===K.CallExpression&&compact(text(result.arguments[0]))===compact(expression(bindings.result.value))&&body.includes('stage="result";constresult='),'result binding before commit');
    need(calls.filter(c=>/^own\d+$/.test(text(c.expression))&&c.arguments.length===1&&text(c.arguments[0])==='result').length===1,'owned result validation');
    need(body.includes('if(d.status!.value==="committed")returnObject.freeze({status:"committed",value:result});'),'success only after commit receipt');
    need(body.includes('returnfailure("indeterminate",d.status!.value==="indeterminate"?"COMMIT_INDETERMINATE":"INVALID_COMMIT_RECEIPT");'),'indeterminate receipt is not rejection');
    const wrapperDecl=wrapper.statements.filter(s=>s.kind===K.VariableStatement).flatMap(s=>s.declarationList.declarations);need(wrapperDecl.length===1,'one bound action');
    const outer=wrapperDecl[0].initializer;need(text(outer.expression)==='Object.freeze','bound freeze');const assign=outer.arguments[0];need(text(assign.expression)==='Object.assign'&&text(assign.arguments[0])==='execute','bound executable');
    const descriptor=frozen(assign.arguments[1].properties[0].initializer),{descriptor_sha256,...descriptorBody}=descriptor;
    need(descriptor.provider.sha256===hash(bytes)&&descriptor_sha256===hash(canonical(descriptorBody)),'provider/descriptor digest');
    need(descriptor.source.source.sha256===hash(nodeBytes)&&canonical(descriptor.bindings)===canonical(bindings),'authored source binding');
    need(descriptor.publication===false&&descriptor.provider_durability_claim===false&&descriptor.effect_contract==='state-and-outbox','claim boundary');
    need(canonical([...source.body.reads].sort())===canonical(bindings.reads.map(r=>r.slot).sort())&&canonical([...source.body.writes].sort())===canonical(bindings.writes.map(w=>w.slot).sort())&&canonical([...source.body.effects].sort())===canonical(bindings.events.map(e=>e.slot).sort()),'authored slots');
    observations.push({selector:bindings.selector,result:'pass',provider_sha256:hash(bytes)});
  }catch(error){errors.push({provider:e.provider_path,reason:error.message});}}
  snapshot.dispose();
}finally{api.close();}
console.log(JSON.stringify({result:errors.length?'fail':'pass',observations,errors}));if(errors.length)process.exitCode=1;
