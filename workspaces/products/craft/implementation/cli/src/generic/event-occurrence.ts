/** Deterministic identity for a source-declared Event emitted by a committed command.
 * This is inert calculation; the transaction owner must supply the checked journal
 * tuple hash and keep the resulting intent inside its original SQLite transaction.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {createHash} from 'node:crypto';

export interface GenericEventOccurrenceInput {
 readonly producer_namespace:string;
 readonly causal_command_tuple_sha256:string;
 readonly event_selector:string;
 readonly event_version:number;
 readonly emission_ordinal:number;
}

const DOMAIN='craft.event-occurrence/v1-candidate';
const NAME=/^[A-Za-z_][A-Za-z0-9_]*$/;
const HEX=/^[0-9a-f]{64}$/;

/** The identity is a lowercase SHA-256 digest over five length-prefixed UTF-8 members. */
export function deriveGenericEventOccurrence(input:GenericEventOccurrenceInput):string {
 if(!input||typeof input!=='object'||Array.isArray(input))throw Error('EVENT_OCCURRENCE_INPUT');
 const {producer_namespace:producer,causal_command_tuple_sha256:causal,event_selector:selector,event_version:version,emission_ordinal:ordinal}=input;
 const names=typeof selector==='string'?selector.split('.'):[];
 if(typeof producer!=='string'||!NAME.test(producer)||names.length!==2||!NAME.test(names[0]!)||!NAME.test(names[1]!)||typeof causal!=='string'||!HEX.test(causal)||version!==1||!Number.isSafeInteger(ordinal)||ordinal<0||ordinal>0xffffffff)throw Error('EVENT_OCCURRENCE_IDENTITY');
 const members=[producer,causal,selector,String(version),String(ordinal)].map(value=>Buffer.from(value,'utf8'));
 if(members.some(bytes=>bytes.length>4096)||DOMAIN.length+1+20+members.reduce((n,b)=>n+b.length,0)>20544)throw Error('EVENT_OCCURRENCE_BOUND');
 const hash=createHash('sha256');hash.update(DOMAIN,'ascii');hash.update(Buffer.from([0]));
 for(const bytes of members){const length=Buffer.allocUnsafe(4);length.writeUInt32BE(bytes.length);hash.update(length);hash.update(bytes);}
 return hash.digest('hex');
}
