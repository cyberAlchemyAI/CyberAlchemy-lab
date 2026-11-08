import {createInvoker} from {{callable}};
import {validateSchema,FunctionFault} from {{boundary}};
import model from {{model}} with {type:'json'};
import {createPublicEntry} from {{transport}};
export const config={{config}};
export const handler=createPublicEntry(config,model,validateSchema,createInvoker,FunctionFault);
