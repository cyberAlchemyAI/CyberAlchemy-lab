import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {publicSelection} from './composition-project.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
const scalar=(name:string)=>({kind:'scalar',name}),at=(root:string)=>({op:'path',root,properties:[]});
export function stateMachineFixture(t:any,moduleRoot='domain'){
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ds-state-controls-')),source=path.join(temp,'source'),nodes:string[]=[],edges:string[]=[];
 t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
 const write=(p:string,value:unknown)=>{const file=path.join(source,p);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,JSON.stringify(value)+'\n');};
 const node=(id:string,kind:string,body:any)=>{if(!nodes.includes(id))nodes.push(id);write('specs/alpha/nodes/'+id+'.json',{schema_version:'domainspec.node/v1',feature_id:'alpha',node_id:id,kind,body:{description:id,...body}});};
 const edge=(event:string,machine:string)=>{const id=event+'-advances-'+machine;edges.push(id);write('specs/alpha/edges/'+id+'.json',{schema_version:'domainspec.edge/v1',feature_id:'alpha',edge_id:id,relationship:'transitions',source_node_id:event,target_node_id:machine,scope:'feature'});};
 const parameters=[{name:'amount',type:scalar('UInt64')}];
 node('allowed','Rule',{predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'TEST-ALLOWED',parameters,expression:{op:'lt',left:{op:'literal',type:'UInt64',value:'100'},right:at('amount')}}});
 node('forward','Rule',{predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'TEST-FORWARD',parameters,expression:{op:'rule_ref',selector:'alpha:allowed',arguments:[{parameter:'amount',value:at('amount')}]}}});
 for(const id of ['requested','completed','unrelated'])node(id,'Event',{event_type:id,version:'1',occurrence_id:{field_id:'id',type_ref:{kind:'primitive',name:'uuid'},required:true},occurred_at_policy:'required',payload:[]});
 const c:any={schema_version:'domainspec.typed-state-machine/v1',ontology_state_machine:'TEST-LIFECYCLE',inputs:[...parameters,{name:'unused',type:scalar('Bool')}],states:['draft','submitted','closed'],initial:'draft',transitions:[
  {transition_id:'submit',source_state:'draft',target_state:'submitted',trigger_event_ref:'alpha:requested',guard:{selector:'alpha:forward',arguments:[{parameter:'amount',value:at('amount')}]},output_intents:[{slot:'primary',event_ref:'alpha:completed'},{slot:'audit',event_ref:'alpha:completed'}]},
  {transition_id:'close',source_state:'submitted',target_state:'closed',trigger_event_ref:'alpha:completed',guard:null,output_intents:[]},
  {transition_id:'repeat',source_state:'closed',target_state:'closed',trigger_event_ref:'alpha:requested',guard:null,output_intents:[]}
 ]};
 node('lifecycle','State Machine',{typed_contract:c});
 node('guardless','State Machine',{typed_contract:{...c,ontology_state_machine:'TEST-GUARDLESS',inputs:[],states:['idle'],initial:'idle',transitions:[{...c.transitions[2],source_state:'idle',target_state:'idle'}]}});
 edge('requested','lifecycle');edge('completed','lifecycle');edge('requested','guardless');
 const save=()=>{write('project.json',{schema_version:'domainspec.project/v1',project_id:'state-controls',features:['alpha'],cross_feature_edges:[]});write('specs/alpha/feature.json',{schema_version:'domainspec.feature/v1',feature_id:'alpha',nodes,edges});};save();
 const selection={...publicSelection(moduleRoot),factories:[],operations:[]},graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection);
 return {temp,root:temp,source,selection,graph,plan,c,node,edge,save};
}
