import {createPublicEntry as createEntry} from {{runtime}};
/** @type { {fetch:typeof fetch} } */
export const httpPort={fetch:(request,options)=>globalThis.fetch(request,options)};
export function createPublicEntry(config,model,validate,createInvoker,IntegrationFault){const handler=createEntry(config,model,validate,createInvoker,IntegrationFault);return (request,env={},io={})=>handler(request,env,{...io,fetch:io.fetch??httpPort.fetch});}
