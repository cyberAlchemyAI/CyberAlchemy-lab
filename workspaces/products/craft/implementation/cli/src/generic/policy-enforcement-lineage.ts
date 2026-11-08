/** Static projection of original checked control; not runtime branch evidence.
 * The original source/plan owner retains custody. No expression literals or
 * invocation data are emitted. Open Questions: docs/POLICY-ENFORCEMENT.md. */
import {dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze,coreSourceFail as fail} from '../commerce/commerce-core-syntax.js';
import type {SourceSpanV1} from '../commerce/commerce-data-v1.js';
import type {GenericOperationControlStepV1,GenericOperationPolicyEnforcementV1,GenericPureDeclarationV1} from './computation-data-v1.js';
import type {GenericStatefulPreflightStepV1,GenericPolicyEnforcementPreflightV1} from './transaction-data-v1.js';
import type {GenericExternalStatefulControlV1} from './external-read-data-v1.js';
import type {GenericExternalWriteStatefulControlV1} from './external-write-data-v1.js';
import type {GenericEventStatefulControlV1} from './event-data-v1.js';

type Control=GenericOperationControlStepV1|GenericStatefulPreflightStepV1|GenericExternalStatefulControlV1['preflight'][number]|GenericExternalWriteStatefulControlV1['preflight'][number]|GenericEventStatefulControlV1['preflight'][number];
type Enforcement=GenericOperationPolicyEnforcementV1|GenericPolicyEnforcementPreflightV1;
export interface PolicyEnforcementLineageInput {
 readonly artifactNode:string;
 readonly functions:readonly GenericPureDeclarationV1[];
 readonly operations:readonly {readonly operation:string;readonly body:readonly Control[]}[];
}
export interface PolicyEnforcementLineageNode {
 readonly id:string;
 readonly kind:'checked-operation'|'policy-enforcement-site'|'checked-pure-declaration'|'policy-case'|'checked-enforcement-type';
 readonly declaration?:string;
 readonly meta_type?:string;
 readonly source_span?:SourceSpanV1;
 readonly source_site?:string;
 readonly case_index?:number;
 readonly branch?:string;
 readonly static_only:true;
}
export interface PolicyEnforcementLineageEdge {readonly from:string;readonly to:string;readonly kind:string;readonly static_only:true}
export interface PolicyEnforcementLineageLink {readonly business:string;readonly system:string;readonly kind:'static-policy-enforcement'|'static-policy-declaration'|'static-policy-case';readonly source_span?:SourceSpanV1;readonly source_site?:string;readonly static_only:true}
export interface PolicyEnforcementLineage {
 readonly nodes:readonly PolicyEnforcementLineageNode[];
 readonly edges:readonly PolicyEnforcementLineageEdge[];
 readonly links:readonly PolicyEnforcementLineageLink[];
}

/** Pure metadata projection. Only pass data from the original checked owners;
 * this function neither establishes custody nor evaluates the Policy. */
export function projectPolicyEnforcementLineage(input:PolicyEnforcementLineageInput):PolicyEnforcementLineage {
 const at={path:'policy-enforcement-lineage',start:0,end:0};
 const nodes=new Map<string,PolicyEnforcementLineageNode>(),edges=new Map<string,PolicyEnforcementLineageEdge>(),links=new Map<string,PolicyEnforcementLineageLink>();
 const declarations=new Map(input.functions.map(f=>[f.name,f]));
 if(!input.artifactNode||declarations.size!==input.functions.length)fail('InvalidContract',at,'actual artifact identity and unique checked function names required');
 let visited=0;
 const account=()=>{if(++visited>262144)fail('ResourceLimit',at,'bounded static enforcement lineage traversal');};
 const id=(kind:string,identity:unknown)=>kind+':'+dataDigest({artifact:input.artifactNode,identity});
 const node=(value:PolicyEnforcementLineageNode)=>{if(nodes.size>=65536&&!nodes.has(value.id))fail('ResourceLimit',at,'bounded static enforcement lineage nodes');nodes.set(value.id,value);return value.id;};
 const edge=(from:string,to:string,kind:string)=>{const value={from,to,kind,static_only:true as const};edges.set(dataDigest(value),value);};
 const link=(value:PolicyEnforcementLineageLink)=>links.set(dataDigest(value),value);
 const pendingFunctions:string[]=[],processedFunctions=new Set<string>();
 const functionNode=(name:string):string=>{
  const declaration=declarations.get(name);if(!declaration)return fail('UnknownReference',at,'enforcement lineage requires original checked declaration '+name);
  const key=id('policy-declaration',name);node({id:key,kind:'checked-pure-declaration',declaration:name,meta_type:declaration.kind,static_only:true});
  link({business:name,system:key,kind:'static-policy-declaration',static_only:true});
  if(!processedFunctions.has(name)){processedFunctions.add(name);pendingFunctions.push(name);}return key;
 };
 const typeNode=(name:string)=>node({id:id('policy-type',name),kind:'checked-enforcement-type',declaration:name,meta_type:'Enum',static_only:true});
 const scan=(root:unknown,call:(name:string)=>void,policy?:(body:Record<string,unknown>)=>void)=>{
  const work:{value:unknown;depth:number}[]=[{value:root,depth:0}];
  while(work.length){account();const {value,depth}=work.pop()!;if(!value||typeof value!=='object')continue;if(depth>128)fail('ResourceLimit',at,'bounded static expression lineage depth');
   if(Array.isArray(value)){for(const child of value)work.push({value:child,depth:depth+1});continue;}
   const row=value as Record<string,unknown>;
   if(row.op==='call'&&typeof row.declaration==='string')call(row.declaration);
   if(row.op==='policy')policy?.(row);
   for(const child of Object.values(row))if(child&&typeof child==='object')work.push({value:child,depth:depth+1});
  }
 };
 const enforcement=(operation:string,step:Enforcement)=>{
  if(step.semantics_revision!=='typed-policy-enforcement/v1'||declarations.get(step.policy)?.kind!=='Policy')fail('InvalidContract',at,'actual checked Policy enforcement descriptor required');
  const physical='source_span'in step?step.source_span:step.source_site;
  if(!physical||typeof physical.path!=='string'||!Number.isSafeInteger(physical.start)||!Number.isSafeInteger(physical.end)||physical.end<=physical.start)fail('InvalidContract',at,'original physical enforcement source span required');
  const source_span={path:physical.path,start:physical.start,end:physical.end},source_site=typeof step.source_site==='string'?step.source_site:undefined;
  const operationId=node({id:id('policy-operation',operation),kind:'checked-operation',declaration:operation,meta_type:'Operation',static_only:true});
  const site=node({id:id('policy-enforcement',{operation,source_span,source_site:source_site??null,policy:step.policy}),kind:'policy-enforcement-site',declaration:operation,source_span,...(source_site?{source_site}:{}),static_only:true});
  edge(input.artifactNode,operationId,'implements-operation');edge(operationId,site,'enforces-policy-at');edge(site,functionNode(step.policy),'evaluates-policy');
  edge(functionNode(step.policy),typeNode(step.result_enum),'returns-admission-type');edge(typeNode(step.result_enum),typeNode(step.reason_enum),'reject-reason-type');
  link({business:operation,system:site,kind:'static-policy-enforcement',source_span,...(source_site?{source_site}:{}),static_only:true});
  scan(step.value.expression,name=>edge(site,functionNode(name),'argument-or-policy-call'));
 };
 const work=input.operations.flatMap(operation=>operation.body.map(step=>({operation:operation.operation,step,depth:0})));
 while(work.length){account();const {operation,step,depth}=work.pop()!;if(depth>64)fail('ResourceLimit',at,'bounded static control lineage depth');
  if(step.kind==='enforce-policy')enforcement(operation,step);
  if(step.kind==='conditional')for(const child of [...step.then,...step.otherwise])work.push({operation,step:child,depth:depth+1});
 }
 while(pendingFunctions.length){account();const name=pendingFunctions.pop()!,declaration=declarations.get(name)!,from=functionNode(name);
  scan(declaration.body,target=>edge(from,functionNode(target),'calls-pure-declaration'),body=>{
   if(body.declaration!==name||!Array.isArray(body.cases))return;
   const cases=[...body.cases.map((value,index)=>({value,index,branch:'case:'+index})),{value:{condition:null,action:body.otherwise},index:body.cases.length,branch:'otherwise'}];
   for(const cs of cases){account();const row=cs.value as {condition?:unknown;action?:{calculation?:unknown;expression?:unknown}};
    if(typeof row.action?.calculation!=='string')fail('InvalidContract',at,'checked Policy branch Calculation lineage required');
    const branch=node({id:id('policy-case',{policy:name,branch:cs.branch}),kind:'policy-case',declaration:name,meta_type:'Policy',case_index:cs.index,branch:cs.branch,static_only:true});
    edge(from,branch,'has-ordered-case');edge(branch,functionNode(row.action.calculation),'selects-calculation');
    link({business:name,system:branch,kind:'static-policy-case',static_only:true});
    if(row.condition)scan(row.condition,target=>edge(branch,functionNode(target),'predicate-calls'));
   }
  });
 }
 const compare=(a:{id:string},b:{id:string})=>a.id.localeCompare(b.id);
 return coreFreeze({nodes:[...nodes.values()].sort(compare),edges:[...edges.values()].sort((a,b)=>dataDigest(a).localeCompare(dataDigest(b))),links:[...links.values()].sort((a,b)=>dataDigest(a).localeCompare(dataDigest(b)))});
}
