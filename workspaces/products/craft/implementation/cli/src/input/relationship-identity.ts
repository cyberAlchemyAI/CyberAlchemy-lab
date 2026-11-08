import type {DecodedRelationship} from './project-model.js';

/** Retain legacy evidence bytes unless a local name needs its existing owner. */
export function relationshipEvidenceId(edge:DecodedRelationship,relationships:readonly DecodedRelationship[]):string {
 const collides=relationships.filter(other=>other.edge_id===edge.edge_id).length>1;
 return collides?(edge.scope==='project'?'project:'+edge.edge_id:'feature:'+edge.source.feature_id+':'+edge.edge_id):edge.edge_id;
}
