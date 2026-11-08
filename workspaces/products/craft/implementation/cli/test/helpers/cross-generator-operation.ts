import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
import {OPERATION_ACTION_BINDINGS_VERSION} from '../../src/typed-operation/action-bindings.ts';
import {publicSelection} from './composition-project.ts';
const scalar=(name='String'):any=>({kind:'scalar',name}),named=(id:string):any=>({kind:'named',selector:'commerce:'+id});
const at=(root:string,...properties:string[]):any=>({op:'path',root,properties}),lit=(type:string,value:any):any=>({op:'literal',type,value});
const arg=(parameter:string,value:any)=>({parameter,value});
/** Compound fixture copied from the existing Operation qualification, not reduced to scalar-only calls. */
export function operationFixture(t:any,moduleRoot='domain'){
  const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ds-operations-'));t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
  const source=path.join(temp,'source'),nodes:string[]=[],edges:string[]=[];
  const write=(p:string,v:any)=>{const f=path.join(source,p);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,JSON.stringify(v,null,2));};
  const node=(id:string,kind:string,body:any)=>{if(!nodes.includes(id))nodes.push(id);write('specs/commerce/nodes/'+id+'.json',{schema_version:'domainspec.node/v1',feature_id:'commerce',node_id:id,kind,body:{description:id,...body}});};
  const edge=(id:string,relationship:string,from:string,to:string)=>{edges.push(id);write('specs/commerce/edges/'+id+'.json',{schema_version:'domainspec.edge/v1',edge_id:id,feature_id:'commerce',relationship,source_node_id:from,target_node_id:to,scope:'feature'});};
  const rule=(id:string,parameters:any[],expression:any)=>node(id,'Rule',{predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'FIXTURE-'+id.toUpperCase(),parameters,expression}});
  const property=(id:string,name:string,type:any,identity=false)=>({ontology_property:'FIXTURE-'+id.toUpperCase()+'#'+name,name,type,identity,meaning:name,cardinality:type.kind==='optional'?'optional':type.kind==='list'?'many':type.kind==='set'?'many-unique':'one'});
  rule('positive',[{name:'amount',type:scalar('UInt64')}],{op:'lt',left:lit('UInt64','0'),right:at('amount')});
  rule('can-post',[{name:'current',type:named('account')},{name:'amount',type:scalar('UInt64')}],{op:'lt',left:at('amount'),right:at('current','FIXTURE-ACCOUNT#balance')});
  rule('receipt-matches',[{name:'expected',type:scalar('UInt64')},{name:'actual',type:scalar('UInt64')}],{op:'eq',left:at('expected'),right:at('actual')});
  node('detail','Value Object',{fields:['amount'],invariant_refs:['commerce:positive'],typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'FIXTURE-DETAIL',properties:[property('detail','amount',scalar('UInt64'))]}});
  node('status','Enum',{values:['Ready','Draft'],typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'FIXTURE-STATUS',variants:['Ready','Draft'].map(name=>({name,ontology_variant:'FIXTURE-STATUS#'+name,payload:null}))}});
  const choice={kind:'sum',variants:[{name:'None',ontology_variant:'FIXTURE-CHOICE#None',payload:null},{name:'Some',ontology_variant:'FIXTURE-CHOICE#Some',payload:named('detail')}]};
  const props=[property('account','id',scalar(),true),property('account','balance',scalar('UInt64')),property('account','detail',named('detail')),property('account','labels',{kind:'set',element:scalar()}),property('account','status',named('status')),property('account','choice',choice)];
  node('account','Entity',{fields:props.map(p=>p.name),typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'FIXTURE-ACCOUNT',properties:props}});
  node('receipt','Entity',{fields:['id','amount'],typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'FIXTURE-RECEIPT',properties:[property('receipt','id',scalar(),true),property('receipt','amount',scalar('UInt64'))]}});
  node('posted','Event',{event_type:'posted',version:'1',occurrence_id:{field_id:'occurrence-id',type_ref:{kind:'primitive',name:'uuid'},required:true},occurred_at_policy:'generated',payload:[{field_id:'account-id',type_ref:{kind:'reference',selector:'commerce:account'},required:true},{field_id:'amount',type_ref:{kind:'primitive',name:'integer'},required:true}]});
  node('post','Operation',{reads:['current-account'],writes:['account-state','receipt-state'],effects:['posted-fact','audit-fact'],guard:'can-post',failure_continuation:'return-post-error'});
  edge('post-reads-account','reads','post','account');edge('post-creates-receipt','creates','post','receipt');edge('post-produces-posted','produces','post','posted');edge('can-post-enforces-post','enforces','can-post','post');edge('receipt-matches-enforces-post','enforces','receipt-matches','post');
  const save=()=>{write('project.json',{schema_version:'domainspec.project/v1',project_id:'native-operations',features:['commerce'],cross_feature_edges:[]});write('specs/commerce/feature.json',{schema_version:'domainspec.feature/v1',feature_id:'commerce',nodes,edges});};save();
  const bindings:any={schema_version:OPERATION_ACTION_BINDINGS_VERSION,selector:'commerce:post',inputs:[{name:'account_id',type:scalar()},{name:'amount',type:scalar('UInt64')},{name:'replacement',type:named('account')},{name:'receipt',type:named('receipt')},{name:'response',type:scalar()}],
    reads:[{slot:'current-account',target:'commerce:account',parameter:'current',key:at('account_id')}],
    guards:[{selector:'commerce:can-post',arguments:[arg('current',at('current')),arg('amount',at('amount'))]},{selector:'commerce:receipt-matches',arguments:[arg('expected',at('amount')),arg('actual',at('receipt','FIXTURE-RECEIPT#amount'))]}],
    writes:[{slot:'account-state',target:'commerce:account',mode:'replace',value:at('replacement')},{slot:'receipt-state',target:'commerce:receipt',mode:'create',value:at('receipt')}],
    events:[{slot:'posted-fact',target:'commerce:posted',parameter:'posted_input'},{slot:'audit-fact',target:'commerce:posted',parameter:'audit_input'}],result:{type:scalar(),value:at('response')},atomicity:'state-and-outbox',continuation:'awaited-settlement'};
  const factories=['account','receipt','detail'].map(id=>({selector:'commerce:'+id,base_validators:[{rule:'commerce:positive',arguments:[{parameter:'amount',field:id==='account'?'balance':'amount'}]}],extensions:[]}));
  const selection={...publicSelection(moduleRoot),factories,operations:[bindings]};
  const compile=()=>{const graph=loadCompiledProjectGraph(source);return {graph,plan:planCompiledReconciledProject(graph,selection)};};
  return {temp,root:temp,source,write,node,edge,save,bindings,factories,selection,compile};
}

/** An actual record-free Operation, not a filtered compound closure. */
export function valueOperationFixture(t:any,moduleRoot='domain'){
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'ds-operation-value-')),source=path.join(root,'source');
 t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
 const write=(p:string,v:unknown)=>{const file=path.join(source,p);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,JSON.stringify(v)+'\n');};
 const nodes:string[]=[];
 const node=(id:string,kind:string,body:unknown)=>{nodes.push(id);write('specs/alpha/nodes/'+id+'.json',{schema_version:'domainspec.node/v1',feature_id:'alpha',node_id:id,kind,body});};
 const scalar={kind:'scalar',name:'UInt64'},named=(selector:string)=>({kind:'named',selector:'alpha:'+selector});
 const variants=(id:string,rows:[string,unknown][])=>rows.map(([name,payload])=>({name,payload,ontology_variant:'TEST-'+id+'#'+name}));
 node('state','Enum',{description:'State',values:['Open','Closed'],typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'TEST-STATE',variants:variants('STATE',[['Open',null],['Closed',null]])}});
 node('choice','Enum',{description:'Choice',values:['Number','State','None'],typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'TEST-CHOICE',variants:variants('CHOICE',[['Number',scalar],['State',named('state')],['None',null]])}});
 node('allowed','Rule',{description:'Allowed',predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'TEST-ALLOWED',parameters:[{name:'value',type:scalar}],expression:{op:'eq',left:{op:'path',root:'value',properties:[]},right:{op:'path',root:'value',properties:[]}}}});
 node('perform','Operation',{description:'Perform',reads:[],writes:[],effects:[],guard:'allowed',failure_continuation:'return-error'});
 write('specs/alpha/edges/allowed-enforces-perform.json',{schema_version:'domainspec.edge/v1',edge_id:'allowed-enforces-perform',feature_id:'alpha',relationship:'enforces',source_node_id:'allowed',target_node_id:'perform',scope:'feature'});
 write('specs/alpha/feature.json',{schema_version:'domainspec.feature/v1',feature_id:'alpha',nodes,edges:['allowed-enforces-perform']});
 write('project.json',{schema_version:'domainspec.project/v1',project_id:'value-operation',features:['alpha'],cross_feature_edges:[]});
 const type={kind:'set',element:named('choice')},selection=publicSelection(moduleRoot);
 selection.factories=[];selection.operations=[{...selection.operations[0],inputs:[{name:'amount',type:scalar},{name:'value',type}],result:{type,value:{op:'path',root:'value',properties:[]}}}];
 const compile=()=>{const graph=loadCompiledProjectGraph(source);return {graph,plan:planCompiledReconciledProject(graph,selection)};};
 return {root,source,selection,compile};
}

