import {readFileSync,statSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import type {BusinessRecipeSelectionSurface,PreparedBusinessRecipeSelection} from './business-authoring-profile-selection.js';
import {assertPreparedBusinessRecipeSelectionCurrent} from './business-authoring-profile-selection.js';
import {businessCanonical,businessHash,businessReject,businessSymbol,freezeBusinessData} from './business-authoring-model.js';
import {parseDomainSource} from './parser.js';
import type {ApplicationFormalSource} from './formal-claim.js';
import type {ApplicationMappingDeclaration} from './application-source.js';

// B07.1 syntax insertion only. Open questions: B04 acceptance, B06.2 checked carriers,
// and B07.2 request graph/callable generation belong to subsequent plan tasks.
export interface BusinessRequestMappingSurface {
 readonly mapping_id:string;readonly source_fragment:string;
}
export interface BusinessRequestPreparationSurface<Selection extends BusinessRecipeSelectionSurface=BusinessRecipeSelectionSurface> {
 readonly kind:'business-authoring-request-preparation';readonly selection:Selection;
 readonly models:readonly {readonly model_id:string;readonly mappings:readonly BusinessRequestMappingSurface[]}[];
 readonly derivation_sha256:string;
}
/** Trusted Core SDK owner, never a profile-supplied callback. */
export interface BusinessRequestPreparationEngine<Preparation> {
 assertBusinessAuthoringRequestsCurrent(preparation:Preparation):void;
}
export interface InsertedBusinessRequestMappings<Selection extends BusinessRecipeSelectionSurface=BusinessRecipeSelectionSurface,Preparation extends BusinessRequestPreparationSurface<Selection>=BusinessRequestPreparationSurface<Selection>> {
 readonly kind:'inserted-business-request-mappings';
 readonly prepared:PreparedBusinessRecipeSelection<Selection>;readonly preparation:Preparation;readonly model_id:string;
 readonly base_source:string;readonly base_sha256:string;readonly source:string;readonly source_sha256:string;
 readonly parsed:ApplicationFormalSource;readonly mapping_ids:readonly string[];readonly authority_effect:'none';
}
type Owner={prepared:PreparedBusinessRecipeSelection<BusinessRecipeSelectionSurface>;preparation:BusinessRequestPreparationSurface;assertPreparation:(value:BusinessRequestPreparationSurface)=>void;fingerprint:string};
const owners=new WeakMap<object,Owner>();
const ownPath=fileURLToPath(import.meta.url);
function ownIdentity():string {const s=statSync(ownPath);return businessHash(readFileSync(ownPath))+':'+[s.dev,s.ino,s.size,s.mtimeMs,s.ctimeMs].join(':');}
const originalIdentity=ownIdentity();
function reject(message:string):never {return businessReject('BUSINESS_REQUEST_INSERTION','business.alch',1,1,message);}
const same=(a:unknown,b:unknown)=>businessCanonical(a)===businessCanonical(b);
const sorted=<T extends {id:string}>(items:readonly T[])=>[...items].sort((a,b)=>a.id<b.id?-1:a.id>b.id?1:0);
function parse(source:string):ApplicationFormalSource {
 if(typeof source!=='string'||Buffer.byteLength(source)>2*1024*1024)reject('prospective application source exceeds the bounded syntax envelope');
 const parsed=parseDomainSource(source);
 if(parsed.source_profile!=='application-v1')reject('explicit application-v1 prospective source required');
 return parsed.carrier as unknown as ApplicationFormalSource;
}

/** Insert real, typed Mapping declarations before later accepted domain compilation.
 * This function neither records acceptance nor creates a registered graph/carrier. */
export function insertBusinessRequestMappings<Selection extends BusinessRecipeSelectionSurface,Preparation extends BusinessRequestPreparationSurface<Selection>>(
 prepared:PreparedBusinessRecipeSelection<Selection>,preparation:Preparation,modelId:string,source:string,engine:BusinessRequestPreparationEngine<Preparation>,
):InsertedBusinessRequestMappings<Selection,Preparation> {
 assertPreparedBusinessRecipeSelectionCurrent(prepared);
 const assertPreparation=engine.assertBusinessAuthoringRequestsCurrent.bind(engine);assertPreparation(preparation);
 if(ownIdentity()!==originalIdentity)reject('Mapping insertion implementation changed');
 if(preparation.selection!==prepared.selection)reject('request preparation must retain the same original Core selection as the genuine Alch producers');
 const input=prepared.selection.models.find(model=>model.model_id===modelId),request=preparation.models.find(model=>model.model_id===modelId);
 if(!input||!request)reject('model must select one captured business/request projection');
 const spec=input!.spec,base=parse(source);
 if(base.domain_id!==spec.identity.namespace||base.title!==spec.identity.title||base.owner!==spec.identity.owner)reject('prospective source must match the selected business identity');
 if(base.invariants.length||base.integrations.length||base.runtime_profiles?.length||base.realizations?.length||base.verification_profiles?.length)reject('unsupported additional application behavior');
 if(base.declarations.length!==spec.entities.length+spec.operations.length)reject('prospective source must contain exactly the selected Entities and Operations before Mapping insertion');
 const feature=businessSymbol(spec.identity.namespace);
 // Prospective sources may carry the eventual generated metadata inline, but may
 // not replace authored meaning or the fixed namespace-derived ontology identity.
 for(const actual of [...base.declarations,...base.rules]){
  const authored=[...spec.entities,...spec.rules,...spec.operations].find(value=>value.id===actual.id);
  const ontology=`BUSINESS-${feature.toUpperCase()}-${businessSymbol(actual.id).toUpperCase()}`;
  if(!authored||(actual.meaning!==null&&actual.meaning!==authored.meaning)||(actual.ontology!==null&&actual.ontology!==ontology))reject('inline declaration metadata differs from authored meaning or the derived ontology identity');
 }
 for(const entity of spec.entities){
  const actual=base.declarations.find(value=>value.id===entity.id);
  if(!actual||actual.kind!=='entity'||actual.identity!==entity.identity||!same([...actual.fields].sort((a,b)=>a.name<b.name?-1:a.name>b.name?1:0).map(f=>({name:f.name,type:f.type})),[...entity.fields].sort((a,b)=>a.name<b.name?-1:a.name>b.name?1:0).map(f=>({name:f.name,type:{kind:'scalar',name:f.type}}))))reject('Entity input structure differs from the selected typed business source');
 }
 for(const operation of spec.operations){
  const actual=base.declarations.find(value=>value.id===operation.id);
  if(!actual||actual.kind!=='operation'||!same(actual.input,{kind:'declaration',ref:operation.input.type_ref})||!same(actual.output,{kind:'declaration',ref:operation.output_ref})||!same(actual.requires,operation.guards.map(g=>g.rule_ref))||actual.reads.length||actual.writes.length||actual.produces.length)reject('Operation input, output, guard or effects differ from the selected business source');
 }
 if(!same(sorted(base.rules).map(r=>({id:r.id,claim_ref:r.claim_ref,enforces:r.enforces})),sorted(spec.rules).map(r=>({id:r.id,claim_ref:r.claim_ref,enforces:[]}))))reject('Rule conditions differ from selected business source');
 const claimShape=(c:ApplicationFormalSource['formal_claims'][number])=>({id:c.id,profile:c.profile,sorts:c.signature.sorts.map(s=>s.name).sort(),predicates:[...c.signature.predicates].sort((a,b)=>a.name<b.name?-1:a.name>b.name?1:0),constants:[...c.signature.constants].sort((a,b)=>a.name<b.name?-1:a.name>b.name?1:0),functions:c.signature.functions,proposition:c.proposition_source,ceiling:c.ceiling});
 if(!same(sorted(base.formal_claims).map(claimShape),sorted(spec.claims).map(c=>({id:c.id,profile:c.logic_profile,sorts:c.sorts.map(s=>s.name).sort(),predicates:[...c.predicates].sort((a,b)=>a.name<b.name?-1:a.name>b.name?1:0).map(p=>({name:p.name,parameter_sorts:p.sort_refs})),constants:[...c.constants].sort((a,b)=>a.name<b.name?-1:a.name>b.name?1:0).map(c=>({name:c.name,sort:c.sort_ref})),functions:[],proposition:c.proposition,ceiling:c.ceiling}))))reject('FormalClaim signature, proposition or ceiling differs from selected source');
 const existing=[...base.declarations,...base.rules,...base.formal_claims].map(d=>businessSymbol(d.id)),ids=request!.mappings.map(m=>m.mapping_id);
 if(new Set([...existing,...ids.map(businessSymbol)]).size!==existing.length+ids.length)reject('generated Mapping collides with an existing normalized declaration');
 const finalSource=source.trimEnd()+'\n\n'+request!.mappings.map(m=>m.source_fragment.trimEnd()).join('\n\n')+'\n',parsed=parse(finalSource);
 const mappings=parsed.declarations.filter((d):d is ApplicationMappingDeclaration=>d.kind==='mapping');
 if(mappings.length!==ids.length||!same(mappings.map(m=>m.id),ids))reject('generated fragments must insert exactly their declared Mapping identities');
 for(const mapping of mappings){
  const entity=spec.entities.find(e=>e.id===mapping.target);
  if(!entity||!mapping.total||!same(mapping.inputs.map(f=>({name:f.name,type:f.type})),[{name:'body',type:{kind:'declaration',ref:entity.id}}])||!same(mapping.fields.map(f=>({target:f.target,path:f.path})),[...entity.fields].sort((a,b)=>a.name<b.name?-1:a.name>b.name?1:0).map(f=>({target:f.name,path:['body',f.name]}))))reject('generated Mapping must preserve exactly every declared field from the whole body');
 }
 const value=freezeBusinessData({kind:'inserted-business-request-mappings' as const,prepared,preparation,model_id:modelId,base_source:source,base_sha256:businessHash(source),source:finalSource,source_sha256:businessHash(finalSource),parsed,mapping_ids:ids,authority_effect:'none' as const},'business.alch');
 owners.set(value,{prepared,preparation,assertPreparation:assertPreparation as Owner['assertPreparation'],fingerprint:businessHash(businessCanonical(value))});
 assertInsertedBusinessRequestMappingsCurrent(value);return value;
}
export function assertInsertedBusinessRequestMappingsCurrent<Selection extends BusinessRecipeSelectionSurface,Preparation extends BusinessRequestPreparationSurface<Selection>>(value:InsertedBusinessRequestMappings<Selection,Preparation>):void {
 const state=value&&typeof value==='object'?owners.get(value):undefined;
 if(!state)reject('registered original Mapping insertion required');
 assertPreparedBusinessRecipeSelectionCurrent(state.prepared);state.assertPreparation(state.preparation);
 if(ownIdentity()!==originalIdentity||value.prepared!==state.prepared||value.preparation!==state.preparation||businessHash(businessCanonical(value))!==state.fingerprint)reject('Mapping insertion custody or source changed');
}
