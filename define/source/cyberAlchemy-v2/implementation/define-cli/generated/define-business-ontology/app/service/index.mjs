import * as entry_BusinessOntologyQuestion from '../../entries/BusinessOntologyQuestion/app/function/index.mjs';
import * as entry_BusinessOntologyReadiness from '../../entries/BusinessOntologyReadiness/app/function/index.mjs';
const entrypoints={"BusinessOntologyQuestion":entry_BusinessOntologyQuestion,"BusinessOntologyReadiness":entry_BusinessOntologyReadiness};
export const routes=[
  {
    "id": "BusinessOntologyQuestion",
    "method": "POST",
    "path": "/define/business-ontology/question"
  },
  {
    "id": "BusinessOntologyReadiness",
    "method": "POST",
    "path": "/define/business-ontology/readiness"
  }
];
export async function invoke(entry,input,env={},io={}){const selected=entrypoints[entry];if(!selected){const error=new Error('SERVICE_ENTRY_NOT_FOUND');error.code='SERVICE_ENTRY_NOT_FOUND';throw error;}return selected.invoke(input,env,io);}
export function createInvoker(entry,observe){const selected=entrypoints[entry];if(!selected){const error=new Error('SERVICE_ENTRY_NOT_FOUND');error.code='SERVICE_ENTRY_NOT_FOUND';throw error;}return selected.createInvoker(observe);}
export async function handler(request,env={},io={}){const url=new URL(request.url),samePath=routes.filter(route=>route.path===url.pathname);if(!samePath.length)return Response.json({error:'NOT_FOUND'},{status:404});const route=samePath.find(route=>route.method===request.method);if(!route)return Response.json({error:'METHOD_NOT_ALLOWED'},{status:405});return entrypoints[route.id].handler(request,env,{...io,signal:io.signal??request.signal});}
export default {fetch:handler};
