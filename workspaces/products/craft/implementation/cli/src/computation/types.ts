/** Additive pure computation candidate. Frozen scalar catalog profiles remain unchanged. */
export type ValueType = {kind:'scalar';name:'Bool'|'UInt64'} | {kind:'string';max_bytes:number} | {kind:'record';name:string} | {kind:'list';element:ValueType;max_items:number} | {kind:'outcome';state:ValueType;intent:ValueType;max_intents:number};
export interface Binder {name:string;type:ValueType}
export interface SortKey {value:Expr;direction:'asc'|'desc';mode:'numeric'|'lexical'|'natural'}
export interface PolicyAction {calculation:string;arguments:Expr[]}
export type Expr =
 | {op:'literal';type:ValueType;value:string|boolean}
 | {op:'var';name:string}
 | {op:'field';value:Expr;field:string}
 | {op:'record';type_name:string;fields:Record<string,Expr>}
 | {op:'let';binding:Binder;value:Expr;body:Expr}
 | {op:'if';condition:Expr;then:Expr;else:Expr}
 | {op:'binary';operator:'eq'|'lt'|'lte'|'gt'|'gte'|'add'|'subtract'|'multiply'|'divide'|'and'|'or';left:Expr;right:Expr}
 | {op:'unary';operator:'not';value:Expr}
 | {op:'call';declaration:string;arguments:Expr[]}
 | {op:'map';source:Expr;item:Binder;body:Expr}
 | {op:'filter';source:Expr;item:Binder;predicate:Expr}
 | {op:'fold';source:Expr;initial:Expr;state:Binder;item:Binder;body:Expr}
 | {op:'indexed_fold';source:Expr;initial:Expr;state:Binder;item:Binder;index:Binder;body:Expr}
 | {op:'repeat';count:Expr;max_iterations:number;initial:Expr;state:Binder;index:Binder;body:Expr}
 | {op:'while_bounded'|'until_bounded';max_iterations:number;initial:Expr;state:Binder;guard:Expr;body:Expr}
 | {op:'range';start:Expr;end:Expr;step:Expr;max_iterations:number}
 | {op:'sort';source:Expr;item:Binder;keys:SortKey[]}
 | {op:'policy';declaration:string;cases:{condition:Expr;calculation:string;arguments:Expr[]}[];otherwise:PolicyAction}
 | {op:'match';value:Expr;binding:Binder;cases:{when:Expr;then:Expr}[];otherwise:Expr}
 | {op:'state_machine';declaration:string;state:Expr;event:Expr;state_binding:Binder;event_binding:Binder;transitions:{guard:Expr;next:Expr;intents:Expr[]}[];otherwise:'stay'|'reject';intent_type:ValueType;max_intents:number};
export interface PureDeclaration {name:string;kind?:'Rule'|'Mapping'|'Calculation'|'Policy'|'StateMachine';pure?:true;parameters:Binder[];result:ValueType;body:Expr}
export interface ComputationLimits {max_input_bytes:number;max_output_bytes:number;max_value_bytes:number;max_items:number;max_iterations:number;max_ast_nodes:number;max_ast_depth:number;max_call_depth:number;fuel:number}
export interface ComputationContract {schema_version:'domainspec.iteration-expression/v1-candidate';semantics_revision:'ordered-metered-v1-candidate';stage:'collection'|'finite-loop'|'condition-loop'|'full-computation';source_node:string;records:{name:string;fields:Record<string,ValueType>}[];inputs:Binder[];functions:PureDeclaration[];result:ValueType;rounding:'floor'|'ceil'|'reject';limits:ComputationLimits;expression:Expr}
export interface CheckedComputation {readonly contract:ComputationContract;readonly expressionTypes:ReadonlyMap<string,ValueType>}
export type SemanticValue = boolean|string|bigint|SemanticValue[]|{[key:string]:SemanticValue};
export interface SemanticError {code:string;expression_path:string;index_path:number[];call_path:string[]}
export type ComputationResult = {ok:true;value:unknown;fuel_used:number}|{ok:false;error:SemanticError;fuel_used:number};
export class ComputationContractError extends Error {constructor(public readonly code:string, public readonly path:string, message:string){super(`${code} at ${path}: ${message}`);this.name='ComputationContractError';}}
export const BOOL:ValueType=Object.freeze({kind:'scalar',name:'Bool'});
export const UINT64:ValueType=Object.freeze({kind:'scalar',name:'UInt64'});
export const MAX_UINT64=18446744073709551615n;
export const DEFAULT_COMPUTATION_LIMITS:ComputationLimits=Object.freeze({max_input_bytes:262144,max_output_bytes:65536,max_value_bytes:65536,max_items:100,max_iterations:100,max_ast_nodes:4096,max_ast_depth:32,max_call_depth:32,fuel:100000});

/** Bounded engine-owned decision data; never a callback or effect channel. */
export interface PolicyDecisionObservation {policy:string;branch:string;calculation:string;expression_path:string;index_path:number[];call_path:string[];invocation_entered:boolean}
export interface ComputationObservedResult {result:ComputationResult;policy_decisions:PolicyDecisionObservation[];observation_status:'complete'|'truncated'}
export const POLICY_OBSERVATION_LIMITS=Object.freeze({max_records:100,max_bytes:65536} as const);
