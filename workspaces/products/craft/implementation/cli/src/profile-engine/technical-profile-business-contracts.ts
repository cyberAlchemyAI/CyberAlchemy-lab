/** Finite source-produced business-role contract; inert shape, no authority.
 * Open Questions: docs/TECHNICAL-PROFILE-SOURCE.md#open-questions. */
import {captureJson,reject} from './contracts.js';
import {coreFreeze} from '../commerce/commerce-core-syntax.js';
export const TECHNICAL_BUSINESS_CONSUMER='craft.generic-business-bindings/v1-candidate';
const effects=['pure','read','atomic-state','external-read','external-write','event-handoff'] as const;
export type TechnicalBusinessEffect=typeof effects[number];
export interface TechnicalBusinessRole {readonly id:string;readonly targetRole:'Operation'|'Query';readonly effect:typeof effects[number];readonly inputCodec:string;readonly outputCodec:string;readonly cardinality:'one'}
export type TechnicalBusinessAssignment = Readonly<{role:string;entries:readonly string[]}> | Readonly<{role:string;selection:'discover-matching'}>;
export interface CheckedTechnicalBusinessBindings {readonly kind:'original-technical-business-bindings/v1'}
function fail(message:string):never{return reject('TECHNICAL_PROFILE_BUSINESS_BINDING','business-binding',message);}
function object(value:unknown,keys:readonly string[]):Record<string,any>{if(!value||typeof value!=='object'||Array.isArray(value)||Object.keys(value).sort().join(',')!==[...keys].sort().join(','))fail('closed business binding record required');return value as Record<string,any>;}
const symbol=(v:unknown)=>typeof v==='string'&&/^[A-Za-z_][A-Za-z0-9_.-]{0,255}$/.test(v);
/** Shape checks are reused by the source consumer, but return no authority. */
export function validateTechnicalBusinessTopology(value:unknown):Readonly<{roles:readonly TechnicalBusinessRole[];assignments:readonly TechnicalBusinessAssignment[]}>{
 const v=object(captureJson(value),['roles','assignments']);if(!Array.isArray(v.roles)||v.roles.length<1||v.roles.length>64||!Array.isArray(v.assignments)||v.assignments.length>64)fail('bounded roles and assignments required');const ids=new Set<string>();
 for(const raw of v.roles){const r=object(raw,['id','targetRole','effect','inputCodec','outputCodec','cardinality']);if(!symbol(r.id)||ids.has(r.id)||!['Operation','Query'].includes(r.targetRole)||!effects.includes(r.effect)||r.cardinality!=='one'||![r.inputCodec,r.outputCodec].every(c=>c==='preserve-entry'||typeof c==='string'&&/^[a-f0-9]{64}$/.test(c)))fail('unique role and exact supported contract required');ids.add(r.id);}
 const assigned=new Set<string>();for(const raw of v.assignments){const discover=!!raw&&typeof raw==='object'&&Object.hasOwn(raw,'selection'),a=object(raw,discover?['role','selection']:['role','entries']);if(!ids.has(a.role)||assigned.has(a.role)||discover&&a.selection!=='discover-matching'||!discover&&(!Array.isArray(a.entries)||a.entries.length!==1||!symbol(a.entries[0])))fail('exactly one explicit selector or declared discover-matching selection per role; missing or ambiguous assignment');assigned.add(a.role);}
 if(assigned.size!==ids.size)fail('every required role must resolve exactly once');return coreFreeze(v) as unknown as Readonly<{roles:readonly TechnicalBusinessRole[];assignments:readonly TechnicalBusinessAssignment[]}>;
}
