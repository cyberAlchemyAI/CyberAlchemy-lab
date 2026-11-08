import type {CompiledProjectGraph} from '../input/project-model.js';
import type {ScalarName,TypedRecordContract} from '../typed-operation/contracts.js';

export interface EventReferenceIdentity {
  readonly selector:string;
  readonly projection:readonly [string];
  readonly ontology_property:string;
  readonly scalar:Extract<ScalarName,'String'|'UInt64'>;
}

/** Typed Entity references carry their declared identity. Existing references to
 * other Event-referenceable concepts remain opaque nonempty strings. */
export function eventReferenceIdentity(graph:CompiledProjectGraph,selector:string,fail:(reason:string)=>never):EventReferenceIdentity {
  const node=graph.nodes.find(candidate=>candidate.selector===selector);
  if(!node)return fail('Event reference target is missing:'+selector);
  if(node.kind!=='Entity')return Object.freeze({selector,projection:Object.freeze(['id']) as readonly [string],ontology_property:'',scalar:'String'});
  const contract=node?.body.typed_contract as TypedRecordContract|undefined;
  if(contract?.schema_version!=='domainspec.typed-record/v1')return Object.freeze({selector,projection:Object.freeze(['id']) as readonly [string],ontology_property:'',scalar:'String'});
  const identities=contract.properties.filter(field=>field.identity);
  if(identities.length!==1)return fail('Event reference target requires one identity:'+selector);
  const identity=identities[0]!;
  if(identity.type.kind!=='scalar'||(identity.type.name!=='String'&&identity.type.name!=='UInt64'))return fail('Event reference identity must be String or UInt64:'+selector+'#'+identity.name);
  return Object.freeze({selector,projection:Object.freeze([identity.name]) as readonly [string],ontology_property:identity.ontology_property,scalar:identity.type.name});
}
