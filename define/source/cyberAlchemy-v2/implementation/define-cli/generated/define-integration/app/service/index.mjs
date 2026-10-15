import * as entry_StageDependency from '../../entries/StageDependency/app/function/index.mjs';
import * as entry_StageResponse from '../../entries/StageResponse/app/function/index.mjs';
import * as entry_StageReadiness from '../../entries/StageReadiness/app/function/index.mjs';
import * as entry_StageHandoff from '../../entries/StageHandoff/app/function/index.mjs';
const entrypoints={"StageDependency":entry_StageDependency,"StageResponse":entry_StageResponse,"StageReadiness":entry_StageReadiness,"StageHandoff":entry_StageHandoff};
export const routes=[
  {
    "id": "StageDependency",
    "method": "POST",
    "path": "/define/integration/stage-dependency"
  },
  {
    "id": "StageResponse",
    "method": "POST",
    "path": "/define/integration/stage-response"
  },
  {
    "id": "StageReadiness",
    "method": "POST",
    "path": "/define/integration/stage-readiness"
  },
  {
    "id": "StageHandoff",
    "method": "POST",
    "path": "/define/integration/stage-handoff"
  }
];
export async function invoke(entry,input,env={},io={}){const selected=entrypoints[entry];if(!selected){const error=new Error('SERVICE_ENTRY_NOT_FOUND');error.code='SERVICE_ENTRY_NOT_FOUND';throw error;}return selected.invoke(input,env,io);}
export function createInvoker(entry,observe){const selected=entrypoints[entry];if(!selected){const error=new Error('SERVICE_ENTRY_NOT_FOUND');error.code='SERVICE_ENTRY_NOT_FOUND';throw error;}return selected.createInvoker(observe);}
export async function handler(request,env={},io={}){const url=new URL(request.url),samePath=routes.filter(route=>route.path===url.pathname);if(!samePath.length)return Response.json({error:'NOT_FOUND'},{status:404});const route=samePath.find(route=>route.method===request.method);if(!route)return Response.json({error:'METHOD_NOT_ALLOWED'},{status:405});return entrypoints[route.id].handler(request,env,{...io,signal:io.signal??request.signal});}
export default {fetch:handler};
