/** Core reconstructs source roles from its own grammar recognizer. This is the
 * structural input to semantic checking, not an accepted/generated application.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze,coreSha256,coreSourceFail as fail,coreSourceChildren as children,coreSourceChild as child,
 coreSourceDescendants as descendants,coreSourceTokens as tokens,coreSourceText as text,parseCoreCommerceSyntax,
 type CoreSourceNode,type CoreSourceRange} from './commerce-core-syntax.js';
export type CoreCommerceMetaType='Entity'|'ValueObject'|'Enum'|'Rule'|'Calculation'|'Mapping'|'Policy'|'StateMachine'|'Operation'|'Query'|'Workflow'|'Interface'|'Event';
export type CoreCommerceType=
 {readonly kind:'UInt64'|'Bool'|'String'}|{readonly kind:'named';readonly name:string}|
 {readonly kind:'optional';readonly value:CoreCommerceType}|{readonly kind:'List';readonly value:CoreCommerceType;readonly maximum:number}|
 {readonly kind:'literal';readonly value:string}|{readonly kind:'outcome';readonly state:CoreCommerceType;readonly intent:CoreCommerceType;readonly maximum:number};
export interface CoreCommerceField {readonly name:string;readonly type:CoreCommerceType;readonly span:CoreSourceRange}
export interface CoreCommerceDeclaration {
 readonly id:string;readonly module:string;readonly name:string;readonly meta_type:CoreCommerceMetaType|null;
 readonly surface:CoreCommerceMetaType|'Entry'|'FormalClaim';readonly syntax:CoreSourceNode;
 readonly fields:readonly CoreCommerceField[];readonly parameters:readonly CoreCommerceField[];readonly contexts:readonly CoreCommerceField[];
 readonly result:CoreCommerceType|null;readonly identity:readonly string[];readonly unique:readonly (readonly string[])[];
 readonly immutable:readonly string[]|'all';readonly variants:readonly {readonly name:string;readonly fields:readonly CoreCommerceField[];readonly wire:string}[];
 readonly interface_kind:string|null;readonly exposes:readonly string[];readonly invokes:string|null;
 readonly access:readonly CoreSourceNode[];readonly refinement:boolean;
 readonly event_handoff?:Readonly<{version:1;payload:CoreCommerceType;from:string;delivered_to:string}>;
}
export interface CoreCommerceModule {
 readonly module:string;readonly version:1;readonly path:string;readonly sha256:string;readonly bytes:number;
 readonly syntax:CoreSourceNode;readonly imports:readonly {readonly alias:string;readonly target:string;readonly span:CoreSourceRange}[];
 readonly declarations:readonly CoreCommerceDeclaration[];
}
export interface CoreCommerceSourceObligation {readonly id:string;readonly declaration:string;readonly kind:string;readonly span:CoreSourceRange;readonly status:'requires-semantic-check'}
export interface CoreCommerceReconstruction {
 readonly schema_version:'craft.commerce-core-source-reconstruction/v1-candidate';
 readonly capture_mode?:'event-handoff-entry';
 readonly qualification:'independent-source-structure-only';readonly modules:readonly CoreCommerceModule[];
 readonly services:readonly {readonly service:string;readonly module:string}[];
 readonly ownership:readonly {readonly declaration:string;readonly service:string|null;readonly category:'service'|'shared'|'technical'|'coordination'}[];
 readonly obligations:readonly CoreCommerceSourceObligation[];
 readonly executable_source_sha256:string;readonly optional_assurance_source_sha256:string;
 readonly authority_effect:'none';
}
const role:Readonly<Record<string,CoreCommerceMetaType|'Entry'|'FormalClaim'>>={
 'enum-declaration':'Enum','rule-declaration':'Rule','calculation-declaration':'Calculation','mapping-declaration':'Mapping',
 'policy-declaration':'Policy','machine-declaration':'StateMachine','operation-declaration':'Operation','query-declaration':'Query',
 'workflow-declaration':'Workflow','generic-workflow-declaration':'Workflow','interface-declaration':'Interface','entry-declaration':'Entry','claim-declaration':'FormalClaim',
};
const span=(n:CoreSourceRange):CoreSourceRange=>({path:n.path,start:n.start,end:n.end});
const words=(n:CoreSourceNode)=>tokens(n).filter(t=>t.layout===null).map(t=>t.token);
const unique=(names:readonly string[],n:CoreSourceRange)=>{if(new Set(names).size!==names.length)fail('DuplicateSymbol',n,'duplicate source identity');};
function typeOf(n:CoreSourceNode):CoreCommerceType {
 const ts=words(n);let at=0;
 const next=()=>ts[at++]??fail('Syntax',n,'missing type');
 const expect=(t:string)=>{if(next()!==t)fail('Syntax',n,'expected type delimiter '+t);};
 const bounded=(minimum:number)=>{const t=next();if(!/^(0|[1-9][0-9]*)$/.test(t)||BigInt(t)<BigInt(minimum)||BigInt(t)>100n)fail('ResourceLimit',n,'collection bound outside finite contract');return Number(t);};
 const parse=(depth:number):CoreCommerceType=>{
  if(depth>32)fail('ResourceLimit',n,'value type depth');const t=next();if(t==='UInt64'||t==='Bool'||t==='String')return {kind:t};
  if(t==='optional'){expect('<');const value=parse(depth+1);expect('>');return {kind:'optional',value};}
  if(t==='List'){expect('<');const value=parse(depth+1);expect(',');const maximum=bounded(1);expect('>');return {kind:'List',value,maximum};}
  if(t==='outcome'){expect('<');const state=parse(depth+1);expect(',');const intent=parse(depth+1);expect(',');const maximum=bounded(0);expect('>');return {kind:'outcome',state,intent,maximum};}
  if(t==='literal')return {kind:'literal',value:JSON.parse(next()) as string};
  let name=t;while(ts[at]==='.'){at++;name+='.'+next();}return {kind:'named',name};
 };
 const value=parse(0);if(at!==ts.length)fail('Syntax',n,'trailing type tokens');return value;
}
function fieldOf(n:CoreSourceNode):CoreCommerceField {const ts=words(n),type=children(n,'type')[0]??child(n,'qualified-name');return {name:ts[0]==='input'||ts[0]==='context'?ts[1]!:ts[0]!,type:typeOf(type),span:span(n)};}
export function reconstructCoreCommerceModule(source:string,path:string):CoreCommerceModule {
 const syntax=parseCoreCommerceSyntax(source,path),header=child(syntax,'module-header'),module=text(child(header,'qualified-name'));
 if(module.length>256)fail('ResourceLimit',header,'module identity exceeds 256');
 const imports:CoreCommerceModule['imports'][number][]=[];
 for(const use of children(syntax,'import-line')){let previous:string|undefined;for(const name of children(use,'qualified-name')){let target=text(name);if(target.includes('.'))previous=target.slice(0,target.lastIndexOf('.'));else if(previous)target=previous+'.'+target;else fail('UnknownReference',name,'first grouped import must be qualified');imports.push({alias:target.slice(target.lastIndexOf('.')+1),target,span:span(name)});}}
 unique(imports.map(r=>r.alias),syntax);
 const declarations:CoreCommerceDeclaration[]=[];
 for(const wrapper of children(syntax,'declaration')){
  const syntax=wrapper.children.find((x):x is CoreSourceNode=>'rule'in x)??fail('Syntax',wrapper,'missing declaration');
  const ts=words(syntax),surface=syntax.rule==='record-declaration'?({entity:'Entity','value-object':'ValueObject',event:'Event'}as const)[ts[0] as 'entity']!:role[syntax.rule];
  if(!surface)fail('UnsupportedCapability',syntax,'unknown source role');
  const name=surface==='Entry'?text(child(syntax,'qualified-name')):ts[1]!,id=surface==='Entry'?name:module+'.'+name;
  if(id.length>256)fail('ResourceLimit',syntax,'declaration identity exceeds 256');
  const fields:CoreCommerceField[]=[],identity:string[]=[],uniques:string[][]=[],immutable:string[]=[],variants:CoreCommerceDeclaration['variants'][number][]=[],exposes:string[]=[];
  const parameters=children(syntax,'parameter').map(fieldOf),contexts=children(syntax,'context').map(fieldOf);let result:CoreCommerceType|null=null,refinement=false,all=false,interfaceKind:string|null=null,invokes:string|null=null,eventHandoff:CoreCommerceDeclaration['event_handoff'];
  if(surface==='Entity'||surface==='ValueObject'||surface==='Event'){
   const clauses=children(syntax,'record-clause'),singleton=new Set<string>();
   for(const c of clauses){const ws=words(c),head=ws[0]!;
    if(head==='unique')uniques.push(children(child(c,'name-list'),'qualified-name').map(text));
    else if(children(c,'type').length)fields.push(fieldOf(c));
    else if(head==='identity'||head==='immutable'){
     if(singleton.has(head))fail('DuplicateSymbol',c,'duplicate record metadata');singleton.add(head);
     if(head==='immutable'&&ws[1]==='all')all=true;else (head==='identity'?identity:immutable).push(...children(child(c,'name-list'),'qualified-name').map(text));
    }else if(head!=='invariant'){
     if(singleton.has(head))fail('DuplicateSymbol',c,'duplicate refinement/event metadata');singleton.add(head);if(head==='carrier')refinement=true;
    }
   }
   unique(fields.map(f=>f.name),syntax);unique(identity,syntax);unique(immutable,syntax);unique(uniques.map(k=>JSON.stringify(k)),syntax);
   const names=new Set(fields.map(f=>f.name));for(const key of [identity,immutable,...uniques]){unique(key,syntax);for(const name of key)if(!names.has(name))fail('UnknownReference',syntax,'identity/unique/immutable field absent: '+name);}
   if(surface==='Entity'&&!identity.length)fail('InvalidContract',syntax,'Entity requires a complete declared identity');
   if(refinement&&(surface!=='ValueObject'||fields.length))fail('InvalidContract',syntax,'transparent scalar must be a field-free ValueObject');
   if(surface!=='Event'&&clauses.some(c=>words(c)[0]==='version'&&!children(c,'type').length))fail('InvalidContract',syntax,'numeric schema version metadata belongs to Event');
   if(surface==='Event'){
    const handoff=children(syntax,'event-clause');
    if(handoff.length){
     if(ts[2]!=='version'||ts[3]!=='1'||clauses.length||handoff.length!==3)fail('InvalidContract',syntax,'event handoff requires exact version 1 and three distinct clauses');
     const value=(key:string)=>{const matches=handoff.filter(c=>words(c)[0]===key);if(matches.length!==1)fail('MissingMapping',syntax,'event handoff requires one '+key);return matches[0]!;};
     const payloadClause=value('payload'),payload=typeOf(child(payloadClause,'type'));
     fields.push({name:'payload',type:payload,span:span(payloadClause)});
     eventHandoff={version:1,payload,from:text(child(value('from'),'qualified-name')),delivered_to:text(child(value('delivered-to'),'qualified-name'))};
    }else if(clauses.filter(c=>words(c)[0]==='version'&&!children(c,'type').length&&words(c)[1]==='1').length!==1)fail('InvalidContract',syntax,'Event requires declared schema version 1');
   }
   if(fields.length>64)fail('ResourceLimit',syntax,'record field limit');
  }else if(surface==='Enum'){
   const forms=new Set<string>();for(const item of children(syntax,'enum-item')){const ws=words(item),fields:CoreCommerceField[]=[];forms.add(ws[0]!);
    for(const type of children(item,'type')){const before=tokens(item).findIndex(t=>t.start===type.start),name=tokens(item)[before-1]!.token;fields.push({name,type:typeOf(type),span:span(type)});}
    unique(fields.map(f=>f.name),item);const wire=ws.indexOf('wire');variants.push({name:ws[1]!,fields,wire:wire<0?ws[1]!:JSON.parse(ws[wire+1]!) as string});}
   unique(variants.map(v=>v.name),syntax);unique(variants.map(v=>v.wire),syntax);if(forms.size>1)fail('InvalidContract',syntax,'mixed enum wire representations');if(variants.length>64)fail('ResourceLimit',syntax,'enum variant limit');
  }else if(surface==='Interface'){
   interfaceKind=text(child(syntax,'interface-kind'));for(const clause of children(syntax,'interface-clause'))if(words(clause)[0]==='exposes')exposes.push(...children(child(clause,'name-list'),'qualified-name').map(text));unique(exposes,syntax);if(interfaceKind==='external'){const results=children(syntax,'interface-clause').filter(c=>words(c)[0]==='result');if(results.length>1)fail('DuplicateSymbol',syntax,'duplicate external result signature');if(results.length)result=typeOf(child(results[0]!,'type'));}
  }else if(surface==='Entry'){invokes=text(children(syntax,'qualified-name')[1]!);}
  else if(surface==='Rule')result={kind:'Bool'};
  else if(surface==='StateMachine'){const types=children(syntax,'type');parameters.push({name:'state',type:typeOf(types[0]!),span:span(types[0]!)},{name:'event',type:typeOf(types[1]!),span:span(types[1]!)});result={kind:'outcome',state:parameters[0]!.type,intent:{kind:'Bool'},maximum:0};}
  else if(surface!=='FormalClaim'){
   const type=children(syntax,'type')[0]??['local-query','delegated-query','native-inspect-body'].flatMap(k=>children(syntax,k).flatMap(n=>children(n,'type')))[0];if(type)result=typeOf(type);
  }
  unique([...parameters,...contexts].map(f=>f.name),syntax);if(parameters.length>128||contexts.length>16)fail('ResourceLimit',syntax,'signature limits');
  declarations.push({id,module,name,meta_type:surface==='Entry'||surface==='FormalClaim'?null:surface,surface,syntax,fields,parameters,contexts,result,identity,unique:uniques,immutable:all?'all':immutable,variants,interface_kind:interfaceKind,exposes,invokes,access:children(syntax,'access-clause'),refinement,...(eventHandoff?{event_handoff:eventHandoff}:{})});
 }
 unique(declarations.map(d=>d.name),syntax);for(const d of declarations)if(d.surface!=='Entry'&&imports.some(i=>i.alias===d.name))fail('DuplicateSymbol',d.syntax,'declaration/import alias collision');
 if(declarations.filter(d=>d.surface!=='Entry').length>256||declarations.filter(d=>d.surface==='Entry').length>64)fail('ResourceLimit',syntax,'module declaration limit');
 return coreFreeze({module,version:1,path,sha256:coreSha256(source),bytes:Buffer.byteLength(source),syntax,imports,declarations});
}
function resolvedName(module:CoreCommerceModule,name:string,all:ReadonlyMap<string,CoreCommerceDeclaration>,where:CoreSourceRange):CoreCommerceDeclaration {
 const id=all.has(module.module+'.'+name)?module.module+'.'+name:module.imports.find(i=>i.alias===name)?.target??name;
 const d=all.get(id);if(!d)fail('UnknownReference',where,'unresolved exact source declaration '+name);return d;
}
export function reconstructCoreCommerceSources(sources:readonly {readonly path:string;readonly text:string}[],captureMode:'legacy'|'keyed-query-entry'|'atomic-state-entry'|'external-read-entry'|'external-write-entry'|'event-handoff-entry'='legacy'):CoreCommerceReconstruction {
 if(captureMode!=='legacy'&&captureMode!=='keyed-query-entry'&&(captureMode!=='atomic-state-entry'&&captureMode!=='external-read-entry'&&captureMode!=='external-write-entry'&&captureMode!=='event-handoff-entry'))fail('InvalidContract',{path:'source-mode',start:0,end:0},'exact source reconstruction mode required');
 if(!sources.length||sources.length>((captureMode==='atomic-state-entry'||captureMode==='external-read-entry'||captureMode==='external-write-entry'||captureMode==='event-handoff-entry')?34:32)||sources.reduce((n,s)=>n+Buffer.byteLength(s.text),0)>4194304)fail('ResourceLimit',{path:'application.alch',start:0,end:0},'finite complete module closure required');
 const modules=sources.map(s=>reconstructCoreCommerceModule(s.text,s.path));unique(modules.map(m=>m.module),modules[0]!.syntax);unique(modules.map(m=>m.path),modules[0]!.syntax);
 const all=new Map(modules.flatMap(m=>m.declarations.map(d=>[d.id,d]as const)));if(all.size!==modules.reduce((n,m)=>n+m.declarations.length,0))fail('DuplicateSymbol',modules[0]!.syntax,'global declaration collision');
 for(const m of modules)for(const i of m.imports)if(!all.has(i.target))fail('UnknownReference',i.span,'import not in captured source closure '+i.target);
 const application=modules.flatMap(m=>m.declarations).filter(d=>d.interface_kind==='application-composition');if(application.length!==1)fail('InvalidContract',modules[0]!.syntax,'one declared application composition required');
 if((captureMode==='atomic-state-entry'||captureMode==='external-read-entry'||captureMode==='external-write-entry'||captureMode==='event-handoff-entry')&&modules.filter(m=>m.module!==application[0]!.module&&m.module!=='Craft.Generated.Auth').length>32)fail('ResourceLimit',application[0]!.syntax,'at most 32 authored modules');
 const app=application[0]!,services:CoreCommerceReconstruction['services'][number][]=[],technicalModules=new Set<string>();
 const coordinationParticipants=new Set<string>();
 for(const clause of children(app.syntax,'interface-clause'))for(const item of children(clause,'application-clause'))if(words(item)[0]==='coordination-records'){
  const list=children(item,'name-list')[0];if(!list)fail('MissingMapping',item,'coordination records require exact names');
  for(const name of children(list,'qualified-name')){const record=resolvedName(modules.find(m=>m.module===app.module)!,text(name),all,name);if(record.surface==='Entity')coordinationParticipants.add(record.id);}
 }
 for(const m of modules)for(const d of m.declarations)if(d.interface_kind==='technical-profile-family')technicalModules.add(m.module);
 for(const clause of children(app.syntax,'interface-clause'))for(const c of children(clause,'application-clause')){const ts=words(c);if(ts[0]==='service'){const owner=text(child(c,'qualified-name'));if(!modules.some(m=>m.module===owner))fail('UnknownReference',c,'service module absent');services.push({service:ts[1]!,module:owner});}}
 unique(services.map(s=>s.service),app.syntax);unique(services.map(s=>s.module),app.syntax);
 const serviceFor=(module:string)=>{const owners=services.filter(s=>module===s.module||module.startsWith(s.module+'.'));if(owners.length>1)fail('InvalidContract',app.syntax,'ambiguous service module prefix');return owners[0]?.service??null;};
 const ownership=modules.flatMap(m=>m.declarations.map(d=>({declaration:d.id,service:serviceFor(d.module),category:technicalModules.has(d.module)?'technical' as const:d.module===app.module?'coordination' as const:serviceFor(d.module)?'service' as const:'shared' as const})));
 const graph=new Map<string,Set<string>>();
 for(const m of modules)for(const d of m.declarations){
  if(technicalModules.has(m.module)&&['Operation','Query','Workflow','Entry','Event'].includes(d.surface))fail('InvalidContract',d.syntax,'technical source cannot introduce business effects, exposure or entry permission');
  const visit=(t:CoreCommerceType,where:CoreSourceRange,context=false)=>{
   if(t.kind==='named'){const target=resolvedName(m,t.name,all,where);if(!['Entity','ValueObject','Enum','Event','Interface'].includes(target.surface))fail('TypeMismatch',where,'callable is not a type');
    if(target.surface==='Interface'&&!context)fail('TypeMismatch',where,'private context/interface is not a serializable data field/result');
    if(context&&target.surface==='Interface'&&!['trusted-context','native-producer','native-auth-owner'].includes(target.interface_kind??''))fail('TypeMismatch',where,'context interface requires its declared private owner kind');
    if(target.surface==='Entity'&&target.module!==m.module&&serviceFor(target.module)!==serviceFor(m.module))fail('InvalidContract',where,'private service Entity cannot cross service signatures');
    if(['Entity','ValueObject','Enum','Event'].includes(d.surface)&&target.surface!=='Interface'){const edges=graph.get(d.id)??new Set<string>();edges.add(target.id);graph.set(d.id,edges);}
   }else if(t.kind==='optional'||t.kind==='List')visit(t.value,where);else if(t.kind==='outcome'){visit(t.state,where);visit(t.intent,where);}
  };
  for(const f of [...d.fields,...d.parameters,...d.variants.flatMap(v=>v.fields)])visit(f.type,f.span);for(const f of d.contexts)visit(f.type,f.span,true);if(d.result)visit(d.result,d.syntax);
  if(d.surface==='Interface'&&d.interface_kind==='internal')for(const name of d.exposes){const target=resolvedName(m,name,all,d.syntax);if(target.module!==m.module||!['Operation','Query'].includes(target.surface))fail('TypeMismatch',d.syntax,'internal Interface exposes only local Operation/Query');}
  if(d.surface==='Entry'){
   const target=resolvedName(m,d.invokes!,all,d.syntax);if(!['Operation','Query','Workflow'].includes(target.surface))fail('TypeMismatch',d.syntax,'entry must invoke Operation, Query or Workflow');
   if(captureMode==='legacy'&&target.surface!=='Workflow'&&!modules.find(m=>m.module===target.module)!.declarations.some(i=>i.interface_kind==='internal'&&i.exposes.includes(target.name)))fail('InvalidContract',d.syntax,'entry cannot expose an unexported private callable');
   for(const key of ['authenticated','permission','auth-resource','auth-action','auth-scope',...(captureMode==='legacy'?['auth-route','context','native-requires','current-action']:[])])if(d.access.filter(c=>words(c)[0]===key).length!==1)fail('MissingMapping',d.syntax,'entry requires one inline '+key+' contract');
   for(const key of ['authenticated','permission','auth-resource','auth-action','auth-scope','auth-route','context','native-requires','producer','caller'])if(d.access.filter(c=>words(c)[0]===key).length>1)fail('DuplicateSymbol',d.syntax,'duplicate inline entry clause '+key);
   unique(d.access.filter(c=>words(c)[0]==='resource-binding').map(c=>words(c)[1]!),d.syntax);
  }
  // Every direct table access/mutation resolves to an Entity owned by this module.
  for(const kind of ['read-statement','mutation','transaction-guard','local-query'])for(const n of descendants(d.syntax,kind)){
   const ts=words(n),names=children(n,'qualified-name');let tables:CoreSourceNode[]=[];
   if(kind==='read-statement'&&ts[2]!=='from')tables=names;
   if(kind==='mutation')tables=names;
   if(kind==='transaction-guard'&&ts[0]==='require-absent')tables=names;
   if(kind==='local-query')tables=names;
   for(const name of tables){const target=resolvedName(m,text(name),all,name),event=kind==='mutation'&&ts[0]==='record-event';
    if(target.surface!==(event?'Event':'Entity'))fail('TypeMismatch',name,'local storage target has wrong role');
    if(!event&&target.module!==m.module)fail('InvalidContract',name,'cross-module private table access');
   }
  }
  for(const n of descendants(d.syntax,'transaction'))for(const name of children(child(n,'name-list'),'qualified-name')){const target=resolvedName(m,text(name),all,name);if((target.surface!=='Entity'&&!(captureMode==='event-handoff-entry'&&target.surface==='Event'))||!(target.module===m.module||(target.surface==='Entity'&&coordinationParticipants.has(target.id))))fail('InvalidContract',name,'transaction participants must be local entities, C12 Event, or application coordination Entity');}
 }
 const done=new Set<string>(),active=new Set<string>();const dfs=(id:string,depth:number)=>{if(active.has(id))fail('InvalidContract',all.get(id)!.syntax,'recursive source value dependency');if(done.has(id))return;if(depth>32)fail('ResourceLimit',all.get(id)!.syntax,'value dependency depth');active.add(id);for(const to of graph.get(id)??[])dfs(to,depth+1);active.delete(id);done.add(id);};for(const id of graph.keys())dfs(id,0);
 const obligationKinds=new Set(['expression','guard','transaction','mutation','read-statement','call-statement','access-clause','machine-transition','workflow-step','workflow-terminal','query-clause','interface-clause']);
 const obligations:CoreCommerceSourceObligation[]=[];
 for(const m of modules)for(const d of m.declarations){if(d.surface==='FormalClaim')continue;const queue=[d.syntax];while(queue.length){const n=queue.pop()!;if(n===d.syntax||obligationKinds.has(n.rule))obligations.push({id:d.id+'#'+n.rule+':'+n.start+':'+n.end,declaration:d.id,kind:n.rule,span:span(n),status:'requires-semantic-check'});for(let i=n.children.length-1;i>=0;i--){const c=n.children[i]!;if('rule'in c)queue.push(c);}}}
 const projection=(claim:boolean)=>modules.map(m=>({module:m.module,version:m.version,imports:claim?[]:m.imports.map(i=>({alias:i.alias,target:i.target})),declarations:m.declarations.filter(d=>(d.surface==='FormalClaim')===claim).map(d=>({id:d.id,surface:d.surface,tokens:tokens(d.syntax).map(t=>t.layout??t.token)}))})).sort((a,b)=>a.module<b.module?-1:a.module>b.module?1:0);
 return coreFreeze({schema_version:'craft.commerce-core-source-reconstruction/v1-candidate',...(captureMode==='event-handoff-entry'?{capture_mode:captureMode}:{}),qualification:'independent-source-structure-only',modules,services,ownership,obligations,executable_source_sha256:dataDigest(projection(false)),optional_assurance_source_sha256:dataDigest(projection(true)),authority_effect:'none'});
}
