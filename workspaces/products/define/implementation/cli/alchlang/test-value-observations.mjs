import {createHash} from 'node:crypto';
const normalized=value=>Array.isArray(value)?value.map(normalized):value&&typeof value==='object'?Object.fromEntries(Object.keys(value).sort().map(key=>[key,normalized(value[key])])):value;
export const valueDigest=value=>createHash('sha256').update(JSON.stringify(normalized(value))+'\n').digest('hex');
const chunks=values=>Array.from({length:Math.ceil(values.length/100)},(_,index)=>values.slice(index*100,index*100+100));
export function observedPolicyFacts(name,original){
 const value=structuredClone(original);
 const replace=keys=>{for(const key of keys){value[key+'_digest']=value[key]===null?null:valueDigest(value[key]);delete value[key];}};
 if(name==='VerifyMaterialization'){
  value.owner_route_present=value.owner_route!==null;delete value.owner_route;
  replace(['selected_scope','actual_scope','selected_statement','actual_statement','selected_boundaries','actual_boundaries','selected_notation','actual_notation','parent_identity','parent_revision','actual_identity','actual_revision']);
 }else if(name==='VerifySuccessor')replace(['current_identity','predecessor_identity']);
 else if(name==='VerifyExternalReference')replace(['selected_identity','observed_identity','selected_revision','observed_revision']);
 else if(name==='VerifyEmbeddedReference')replace(['selected_pack','actual_pack','selected_identity','observed_identity']);
 else if(name==='VerifyConceptCoverage'){value.required_ids=chunks(value.required_ids.map(valueDigest));value.handled_ids=chunks(value.handled_ids.map(valueDigest));}
 else if(name==='VerifyAssessment'){value.reason_present=value.unevaluable_reason!==null;value.reason_nonempty=typeof value.unevaluable_reason==='string'&&value.unevaluable_reason.length>0;delete value.unevaluable_reason;}
 else if(name==='VerifyApplicationScope')replace(['selected_consumer','actual_consumer']);
 else if(name==='VerifyParameterBindings'){
  value.parameters=value.parameters.map(row=>({...row,name:valueDigest(row.name),gap:valueDigest(row.gap)}));
  for(const key of ['bound_names','provenance_names','gap_ids'])value[key]=value[key].map(valueDigest);
 }
 return value;
}
