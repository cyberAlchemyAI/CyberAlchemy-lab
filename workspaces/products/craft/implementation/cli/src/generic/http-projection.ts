/** Inert route topology from an already checked HTTP source contract.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {coreFreeze} from '../commerce/commerce-core-syntax.js';
import type {GenericHttpApplicationV1} from './http-data-v1.js';

export function projectGenericHttpTransport(contract:GenericHttpApplicationV1){
 const entries=[...new Map(contract.entries.map(entry=>[entry.route.entry,entry])).values()];
 return coreFreeze({
  nodes:[
   ...entries.map(entry=>({id:'entry:'+entry.route.entry,kind:'protected-entry',entry:entry.route.entry,service:entry.route.service,source:entry.entry_source,entry_contract_sha256:entry.entry_contract_sha256})),
   ...contract.entries.map(entry=>({id:'http:'+entry.route.id,kind:'injected-http-handler',artifact:'entry-http.mjs',route:entry.route,entry_source:entry.entry_source,mapping_source:entry.mapping_source,profile_source:entry.profile_source,transport_semantics_sha256:contract.transport_semantics_sha256})),
  ],
  edges:contract.entries.map(entry=>({from:'http:'+entry.route.id,to:'entry:'+entry.route.entry,kind:'invokes-protected-entry'})),
  bridge_links:contract.entries.map(entry=>({business:entry.route.entry,system:'http:'+entry.route.id,mapping:entry.route.response_mapping,entry_source:entry.entry_source,mapping_source:entry.mapping_source,profile_source:entry.profile_source,entry_contract_sha256:entry.entry_contract_sha256,response_mapping_sha256:entry.response_mapping_sha256,transport_semantics_sha256:contract.transport_semantics_sha256})),
  authority_effect:'none' as const,
 });
}
