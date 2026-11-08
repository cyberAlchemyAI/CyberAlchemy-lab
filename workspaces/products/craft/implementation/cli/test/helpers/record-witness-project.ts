import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {publicSelection} from './composition-project.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
export const scalar=(name:string)=>({kind:'scalar',name}),named=(id:string)=>({kind:'named',selector:'alpha:'+id}),wrap=(kind:string,element:unknown)=>({kind,element});
export const p=(root:string,properties:string[]=[])=>({op:'path',root,properties}),lit=(type:string,value:unknown)=>({op:'literal',type,value}),eq=(left:unknown,right:unknown)=>({op:'eq',left,right});
export function recordWitnessFixture(t:any,impossible=false,moduleRoot='domain',representative=false){
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'ds-record-witness-')),source=path.join(root,'source'),nodes:string[]=[];
 t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
 const write=(p:string,v:unknown)=>{const file=path.join(source,p);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,JSON.stringify(v)+'\n');};
 const node=(id:string,kind:string,body:unknown)=>{nodes.push(id);write('specs/alpha/nodes/'+id+'.json',{schema_version:'domainspec.node/v1',feature_id:'alpha',node_id:id,kind,body});};
 const rule=(id:string,parameters:unknown[],expression:unknown)=>node(id,'Rule',{description:id,predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'TEST-'+id.toUpperCase(),parameters,expression}});
 rule('allowed',[{name:'value',type:scalar('String')}],eq(p('value'),lit('String','approved')));
 rule('nonempty',[{name:'value',type:scalar('String')}],{op:'not',term:eq(p('value'),lit('String',''))});
 rule('budget',[{name:'amount',type:scalar('UInt64')},{name:'approved',type:scalar('Bool')}],impossible?eq(lit('Bool',true),lit('Bool',false)):{op:'all',terms:[{op:'lt',left:lit('UInt64','0'),right:p('amount')},eq(p('approved'),lit('Bool',true))]});
 const pred=eq(p('item'),lit('String','approved')),self=eq(p('item'),p('item'));
 rule('customer-valid',[{name:'tags',type:wrap('list',scalar('String'))},{name:'credit',type:named('money')},{name:'label',type:scalar('String')}],{op:'all',terms:[
  {op:'rule_ref',selector:'alpha:allowed',arguments:[{parameter:'value',value:p('label')}]},
  {op:'lt',left:lit('UInt64','0'),right:p('credit',['TEST-MONEY#amount'])},
  {op:'contains',left:p('tags'),right:lit('String','approved')},
  {op:'unique',binding:'item',collection:p('tags'),where:self},
  {op:'exactly_one',binding:'item',collection:p('tags'),where:pred},
  {op:'exists',binding:'item',collection:p('tags'),where:pred},
  {op:'any',terms:[eq(p('label'),lit('String','other')),eq(p('label'),lit('String','approved'))]},
  {op:'set_equal',left:{op:'to_set',value:p('tags')},right:{op:'to_set',value:p('tags')}}
 ]});
 const record=(id:string,kind:string,fields:[string,any][],invariants:string[]=[])=>node(id,kind,{description:id,fields:fields.map(([name])=>name),...(invariants.length?{invariant_refs:invariants}:{}),typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'TEST-'+id.toUpperCase(),properties:fields.map(([name,type])=>({name,type,ontology_property:'TEST-'+id.toUpperCase()+'#'+name,identity:kind==='Entity'&&name==='id',cardinality:type.kind==='optional'?'optional':type.kind==='list'?'many':type.kind==='set'?'many-unique':'one',meaning:name}))}});
 record('money','Value Object',[['amount',scalar('UInt64')],['approved',scalar('Bool')]],['alpha:budget']);
 record('customer','Entity',[['id',scalar('String')],['label',scalar('String')],['credit',named('money')],['tags',wrap('list',scalar('String'))],['note',wrap('optional',scalar('String'))]]);
 node('choice','Enum',{description:'Owned business payloads',values:['None','Customer','Money','Customers','CustomerSet','Optional'],typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'TEST-CHOICE',variants:[['None',null],['Customer',named('customer')],['Money',named('money')],['Customers',wrap('list',named('customer'))],['CustomerSet',wrap('set',named('customer'))],['Optional',wrap('optional',named('customer'))]].map(([name,payload])=>({name,payload,ontology_variant:'TEST-CHOICE#'+name}))}});
 if(representative)rule('first-customer',[{name:'customers',type:wrap('list',named('customer'))}],{op:'exists',binding:'item',collection:{op:'to_set',value:p('customers')},where:eq(p('item',['TEST-CUSTOMER#label']),lit('String','approved'))});
 write('project.json',{schema_version:'domainspec.project/v1',project_id:'record-witness',features:['alpha'],cross_feature_edges:[]});
 write('specs/alpha/feature.json',{schema_version:'domainspec.feature/v1',feature_id:'alpha',nodes,edges:[]});
 const selection={...publicSelection(),module_root:moduleRoot,factories:[
  {selector:'alpha:money',base_validators:[{rule:'alpha:budget',arguments:[{parameter:'amount',field:'amount'},{parameter:'approved',field:'approved'}]}],extensions:[]},
  {selector:'alpha:customer',base_validators:[{rule:'alpha:nonempty',arguments:[{parameter:'value',field:'id'}]},{rule:'alpha:budget',arguments:[{parameter:'amount',path:['credit','amount']},{parameter:'approved',path:['credit','approved']}]},{rule:'alpha:customer-valid',arguments:[{parameter:'tags',field:'tags'},{parameter:'credit',field:'credit'},{parameter:'label',field:'label'}]}],extensions:[]}
 ],operations:[]},graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection);
 return {root,temp:root,source,selection,graph,plan};
}

