/** Native transport dependencies for generated D45 response streams. Open Questions: ../../STREAM-LIFECYCLE.md. */
export interface StreamFrame {readonly event:string;readonly data:string}
export interface StreamFrameSink {
 /** Resolves after bounded downstream capacity accepts the frame. */
 write(event:string,value:unknown,signal?:AbortSignal,accepted?:()=>void):Promise<void>;
 close():void;
 error(reason:unknown):void;
}
export interface StreamTerminalObservation {readonly type:'stream_terminal';readonly outcome:'completed'|'error'|'cancelled';readonly value?:unknown}
export interface ResponseStreamSession {readonly response:Response;readonly finished:Promise<void>}
