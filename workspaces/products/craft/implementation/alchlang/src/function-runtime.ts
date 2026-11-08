// General runtime for the opt-in function profile. No application-specific identifiers.
export type Expr = {kind:string; value?:any; name?:string; args?:Expr[]; fields?:[string,Expr][]; body?:Expr};
export type FunctionModel = {portability?:string; modules?:Record<string,any>; schemas:Record<string,Record<string,any>>; integrations:Record<string,any>; flows:Record<string,any[]>; endpoint:any};
const MAX=18446744073709551615n;
export class FunctionFault extends Error { constructor(public code:string){super(code);} }
const fail=(code:string):never=>{throw new FunctionFault(code);};
const own=(v:any,k:string)=>Object.prototype.hasOwnProperty.call(v,k);
function plain(v:any){if(!v||typeof v!=="object"||Array.isArray(v)||![Object.prototype,null].includes(Object.getPrototypeOf(v)))fail("FUNCTION_RECORD");for(const k of Reflect.ownKeys(v))if(typeof k!=="string"||!("value" in Object.getOwnPropertyDescriptor(v,k)!))fail("FUNCTION_RECORD");return v;}
function access(v:any,parts:string[]){for(const k of parts){if(v==null)return undefined;plain(v);v=own(v,k)?v[k]:undefined;}return v;}
function uint(v:any):bigint{if(typeof v==="number"&&(!Number.isSafeInteger(v)||v<0)||typeof v==="string"&&!/^(0|[1-9][0-9]*)$/.test(v)||!["number","bigint","string"].includes(typeof v))return fail("FUNCTION_UINT64");const n=BigInt(v);if(n<0n||n>MAX)fail("FUNCTION_UINT64");return n;}
function scale(v:any){if(!Number.isInteger(v)||v<0||v>18)fail("FUNCTION_SCALE");return v as number;}
function decimal(v:any,s:any){const n=scale(s);if(typeof v!=="string"||!new RegExp(`^(0|[1-9][0-9]*)(\\.[0-9]{1,${Math.max(n,1)}})?$`).test(v)||(n===0&&v.includes('.')))fail("FUNCTION_DECIMAL");const [a,b='']=v.split('.');return uint(BigInt(a)*10n**BigInt(n)+BigInt(b.padEnd(n,'0')||'0'));}
function list(v:any){if(!Array.isArray(v))fail("FUNCTION_LIST");return v as any[];}
const truth=(v:any)=>{if(typeof v!=="boolean")fail("FUNCTION_BOOLEAN");return v;};
export function validateSchema(model:FunctionModel,name:string,value:any,depth=0):any{
 if(depth>32)fail("FUNCTION_DEPTH");const fields=model.schemas[name];if(!fields)fail("FUNCTION_SCHEMA");plain(value);
 for(const k of Object.keys(value))if(!own(fields,k))fail("FUNCTION_UNKNOWN_FIELD");
 const result:Record<string,any>=Object.create(null);
 for(const [key,s] of Object.entries(fields)){
  let v=own(value,key)?value[key]:undefined;
  if(v===undefined){if(s.optional)continue;fail("FUNCTION_REQUIRED");}
  if(v===null){if(!s.nullable)fail("FUNCTION_TYPE");if(own(s,'const')&&s.const!==null)fail('FUNCTION_CONST');result[key]=null;continue;}
  if(s.type==='string'||s.type==='identifier'||s.type==='timestamp'){
   if(typeof v!=='string')fail('FUNCTION_TYPE');if(s.type==='identifier'&&!v.trim())fail('FUNCTION_ID');if(s.type==='timestamp'&&Number.isNaN(Date.parse(v)))fail('FUNCTION_TIMESTAMP');
   if(s.max!==undefined&&v.length>s.max)fail('FUNCTION_LIMIT');if(s.pattern&&!new RegExp(s.pattern).test(v))fail('FUNCTION_PATTERN');
  }else if(s.type==='integer'){if(!Number.isSafeInteger(v))fail('FUNCTION_TYPE');if(s.min!==undefined&&v<s.min||s.max!==undefined&&v>s.max)fail('FUNCTION_RANGE');}
  else if(s.type==='boolean'){truth(v);}
  else if(s.type==='list'){list(v);if(s.max!==undefined&&v.length>s.max)fail('FUNCTION_LIMIT');v=v.map((x:any)=>{if(['string','identifier'].includes(s.items)){if(typeof x!=='string'||s.items==='identifier'&&!x.trim())fail('FUNCTION_TYPE');return x;}return validateSchema(model,s.items,x,depth+1);});}
  else v=validateSchema(model,s.type,v,depth+1);
  if(own(s,'const')&&v!==s.const)fail('FUNCTION_CONST');result[key]=v;
 }
 return result;
}
export function evaluate(expr:Expr,scope:Record<string,any>,api:any):any{
 if(expr.kind==='literal')return expr.value;
 if(expr.kind==='ref'){const [head,...tail]=expr.name!.split('.');if(!own(scope,head!))fail('FUNCTION_REFERENCE');return access(scope[head!],tail);}
 if(expr.kind==='object'){const obj:Record<string,any>=Object.create(null);for(const [k,v] of expr.fields!)obj[k]=evaluate(v,scope,api);return obj;}
 if(expr.kind==='array')return expr.args!.map(x=>evaluate(x,scope,api));
 if(expr.kind==='lambda')return (v:any)=>evaluate(expr.body!,{...scope,[expr.name!]:v},api);
 const args=expr.args!,name=expr.name!;
 if(name==='if')return evaluate(truth(evaluate(args[0],scope,api))?args[1]:args[2],scope,api);
 if(name==='and')return args.every(x=>truth(evaluate(x,scope,api)));
 if(name==='or')return args.some(x=>truth(evaluate(x,scope,api)));
 const v=args.map(x=>evaluate(x,scope,api));
 switch(name){
  case 'eq':return v[0]===v[1];case 'ne':return v[0]!==v[1];
  case 'lte':case 'gte':case 'gt':{if(!v.every(x=>typeof x==='bigint'||typeof x==='number'&&Number.isSafeInteger(x)))fail('FUNCTION_TYPE');return name==='lte'?v[0]<=v[1]:name==='gte'?v[0]>=v[1]:v[0]>v[1];}
  case 'not':return !truth(v[0]);case 'present':return v[0]!==null&&v[0]!==undefined;
  case 'lower':if(typeof v[0]!=='string')fail('FUNCTION_TYPE');return v[0].toLowerCase();
  case 'uint64':return uint(v[0]);case 'decimalToUInt64':return decimal(v[0],v[1]);
  case 'formatDecimal':{const n=uint(v[0]),s=scale(v[1]),m=10n**BigInt(s);return s?`${n/m}.${(n%m).toString().padStart(s,'0')}`:n.toString();}
  case 'string':if(typeof v[0]!=='bigint'&&typeof v[0]!=='string')fail('FUNCTION_TYPE');return String(v[0]);
  case 'count':return list(v[0]).length;case 'first':return list(v[0])[0];
  case 'map':return list(v[0]).map(v[1]);case 'filter':return list(v[0]).filter(x=>truth(v[1](x)));case 'every':return list(v[0]).every(x=>truth(v[1](x)));
  case 'distinct':return [...new Set(list(v[0]))];
  case 'sort':{const a=list(v[0]);if(!a.every(x=>typeof x==='string'))fail('FUNCTION_TYPE');return [...a].sort();}
  case 'merge':return Object.assign(Object.create(null),...v.map(plain));
  case 'query':return api.evaluateQuery(v[0],v[1],v[2]);
  case 'calculate':return api.evaluateCalculation(v[0],v[1]);
  default:return fail('FUNCTION_OPERATOR');
 }
}
async function boundedText(response:Response|Request,limit:number,timeout=30000):Promise<string>{
 if(!response.body)return '';const reader=response.body.getReader();const chunks:Uint8Array[]=[];let size=0;let timedOut=false;const timer=setTimeout(()=>{timedOut=true;void reader.cancel().catch(()=>{});},timeout);
 try{while(true){const {value,done}=await reader.read();if(done){if(timedOut)fail('FUNCTION_TIMEOUT');break;}size+=value.byteLength;if(size>limit){await reader.cancel();fail('FUNCTION_BODY_LIMIT');}chunks.push(value);}}
 finally{clearTimeout(timer);reader.releaseLock();}
 const bytes=new Uint8Array(size);let offset=0;for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.length;}return new TextDecoder('utf-8',{fatal:true}).decode(bytes);
}
export function createFunction(model:FunctionModel,api:any){
 const output=(result:any)=>{try{validateSchema(model,model.endpoint.output,result);}catch{fail('FUNCTION_OUTPUT_SCHEMA');}return result;};
 async function invoke(input:any,env:Record<string,string|undefined>={},io:{fetch?:typeof fetch}={}){
  const endpoint=model.endpoint;const scope:Record<string,any>={input:validateSchema(model,endpoint.input,input)};
  for(const step of model.flows[endpoint.flow]){
   if(step.kind==='bind'){
    const b=model.integrations[step.integration];let remote=false;let data=b.provided?access(scope,b.provided.split('.')):undefined;
    if(data===undefined){remote=true;
     if(b.transport==='provided')fail('FUNCTION_INTEGRATION_REQUIRED');const url=env[b.urlEnv];if(!url)fail('FUNCTION_ENV_REQUIRED');
     let target:URL;try{target=new URL(url!);}catch{return fail('FUNCTION_URL');}if(target.protocol!=='https:'||target.username||target.password)fail('FUNCTION_URL');
     for(const [key,selector] of Object.entries(b.query??{})){const value=access(scope,(selector as string).split('.'));if(typeof value!=='string'&&typeof value!=='number')fail('FUNCTION_INTEGRATION_QUERY');target.searchParams.set(key,String(value));}
     const headers:Record<string,string>={accept:'application/json'};
     if(b.secretEnv){const secret=env[b.secretEnv];if(!secret)fail('FUNCTION_ENV_REQUIRED');headers.authorization=`Bearer ${secret}`;}
     const controller=new AbortController();const timer=setTimeout(()=>controller.abort(),b.timeout);
     try{
      const response=await (io.fetch??fetch)(target,{method:'GET',headers,redirect:'error',signal:controller.signal});
      if(!response.ok){await response.body?.cancel();fail('FUNCTION_INTEGRATION_STATUS');}
      const text=await boundedText(response,b.maxBytes);data=JSON.parse(text);
     }catch(error){if(controller.signal.aborted)fail('FUNCTION_INTEGRATION_TIMEOUT');if(error instanceof FunctionFault){if(error.code==='FUNCTION_BODY_LIMIT')fail('FUNCTION_INTEGRATION_LIMIT');throw error;}fail('FUNCTION_INTEGRATION_FAILED');}finally{clearTimeout(timer);}
    }
    try{scope[step.name]=validateSchema(model,b.output,data);}catch(e){if(remote)fail('FUNCTION_INTEGRATION_SCHEMA');throw e;}
   }else if(step.kind==='let')scope[step.name]=evaluate(step.expr,scope,api);
   else if(step.kind==='require'){if(!truth(evaluate(step.expr,scope,api)))fail(step.code);}
   else if(step.kind==='when'){if(truth(evaluate(step.expr,scope,api))){const result=evaluate(step.result,scope,api);return output(result);}}
   else if(step.kind==='return'){const result=evaluate(step.expr,scope,api);if(model.endpoint.output)return output(result);}
  }
  return fail('FUNCTION_RETURN');
 }
 async function handler(request:Request,env:Record<string,string|undefined>={},io:{fetch?:typeof fetch}={}):Promise<Response>{
  const ep=model.endpoint;const response=(body:any,status:number)=>new Response(JSON.stringify(body),{status,headers:{'content-type':'application/json','cache-control':'no-store'}});
  if(new URL(request.url).pathname!==ep.path)return response({error:'NOT_FOUND'},404);
  if(request.method!==ep.method)return response({error:'METHOD_NOT_ALLOWED'},405);
  const secret=env[ep.authEnv];if(!secret)return response({error:'FUNCTION_ENV_REQUIRED'},503);
  if(request.headers.get('authorization')!==`Bearer ${secret}`)return response({error:'UNAUTHORIZED'},401);
  if(request.headers.get('content-type')?.split(';')[0].trim()!=='application/json')return response({error:'CONTENT_TYPE'},415);
  try{
   let body;try{body=JSON.parse(await boundedText(request,ep.maxBytes,ep.timeout));}catch(e){if(e instanceof FunctionFault)throw e;return response({error:'INVALID_JSON'},400);}
   const result=await invoke(body,env,io);const status=ep.statuses[result.status];if(!status)fail('FUNCTION_RESPONSE_STATUS');return response(result,status);
  }catch(e){
   const code=e instanceof FunctionFault?e.code: typeof (e as any)?.message==='string'&&(e as any).message.includes('CALCULATION_OVERFLOW')?'CALCULATION_OVERFLOW':'FUNCTION_INTERNAL';
   return response({error:code},ep.errors[code]??(code==='FUNCTION_INTERNAL'?500:ep.errorStatus));
  }
 }
 return {invoke,handler};
}
