// Test-only outcome accounting; no verification receipt or provider qualification.
// Open Questions: goals/plans/domainspec-alchlang-review-repair/C4-NATIVE-FAILURE-ACCOUNTING.v1.md#open-questions
const stream=(value:unknown):string=>typeof value==='string'?value:Buffer.isBuffer(value)?value.toString('utf8'):'';

export class NativeProcessFailure extends Error {
  readonly status:number|null;
  readonly signal:string|null;
  readonly code:string|null;
  readonly stdout:string;
  readonly stderr:string;
  readonly diagnostic:string;
  readonly failure_kind:'exit'|'signal'|'spawn-or-transport'|'unknown';

  constructor(context:string,cause:unknown,protocolDiagnostic?:string){
    const e=cause!==null&&typeof cause==='object'?cause as Record<string,unknown>:{};
    const status=typeof e.status==='number'&&Number.isSafeInteger(e.status)&&e.status>=0?e.status:null;
    const signal=e.signal==null?null:String(e.signal),code=e.code==null?null:String(e.code);
    const stdout=stream(e.stdout),stderr=stream(e.stderr),diagnostic=[stdout,stderr].filter(Boolean).join('\n');
    const transport=code!==null||e.error!=null||(e.timed!==undefined&&e.timed!==false);
    const kind=transport?'spawn-or-transport':signal!==null?'signal':status!==null&&status>0?'exit':'unknown';
    const message=typeof e.message==='string'?e.message:String(cause);
    super([`${context}: ${kind}; status=${status??'none'}; signal=${signal??'none'}; code=${code??'none'}`,protocolDiagnostic,message,diagnostic].filter(Boolean).join('\n').slice(0,6000),{cause});
    this.name='NativeProcessFailure';this.status=status;this.signal=signal;this.code=code;
    this.stdout=stdout;this.stderr=stderr;this.diagnostic=diagnostic;this.failure_kind=kind;
  }
}

export function nativeProcessFailure(context:string,cause:unknown):NativeProcessFailure{
  return new NativeProcessFailure(context,cause);
}

export function isLeanDecideFailure(error:unknown,requireFalseEval=false):boolean{
  return error instanceof NativeProcessFailure&&error.failure_kind==='exit'
    &&/\berror:/i.test(error.diagnostic)
    &&(requireFalseEval?/\bdecide\b/:/currentStructuralReferencesHold|\bdecide\b/).test(error.diagnostic)
    &&(!requireFalseEval||/^false\r?$/m.test(error.diagnostic));
}

export type NativeObserverResult={result:'pass';interfaces:number;fields:number}|{result:'fail';error:string};

export function readNativeObserver(execute:()=>string|Buffer):NativeObserverResult{
  let stdout:string,status=0,cause:unknown;
  try{stdout=stream(execute());}
  catch(error){
    const failure=nativeProcessFailure('native observer',error);
    if(failure.failure_kind!=='exit'||failure.status!==1)throw failure;
    stdout=failure.stdout;status=1;cause=error;
  }
  try{
    const value:unknown=JSON.parse(stdout);
    if(stdout!==JSON.stringify(value)+'\n')throw Error('expected one exact tool-style JSON object and LF');
    if(value===null||typeof value!=='object'||Array.isArray(value))throw Error('expected observer object');
    const row=value as Record<string,unknown>,keys=Object.keys(row).sort().join(',');
    if(status===0&&row.result==='pass'&&keys==='fields,interfaces,result'
      &&Number.isSafeInteger(row.interfaces)&&Number(row.interfaces)>=0
      &&Number.isSafeInteger(row.fields)&&Number(row.fields)>=0)return row as NativeObserverResult;
    if(status===1&&row.result==='fail'&&keys==='error,result'&&typeof row.error==='string'&&row.error.trim().length>0)return row as NativeObserverResult;
    throw Error('observer schema and exit status do not match');
  }catch(error){
    // Keep the original process cause on exit1, including full captured streams.
    throw new NativeProcessFailure('native observer protocol',cause??{status,signal:null,stdout,stderr:''},error instanceof Error?error.message:String(error));
  }
}
