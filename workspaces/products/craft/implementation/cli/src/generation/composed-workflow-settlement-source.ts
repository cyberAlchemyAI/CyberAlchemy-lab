import {WORKFLOW_SETTLEMENT_SUPPORT} from './workflow-settlement-source.js';

/** Add the checked call's finite precommit vocabulary without changing legacy bytes. */
export function composedWorkflowSettlementSupport():string{
 const replacements=[
  ['export function inspectOperationSettlement(value:unknown,expectedContinuation:string):OperationSettlement{','export function inspectOperationSettlement(value:unknown,expectedContinuation:string,precommit:readonly Readonly<{stage:string;codes:readonly string[]}>[]):OperationSettlement{'],
  ["  if(!valid)return unknown('invalid-return');","  if(!valid)valid=status==='failed'&&precommit.some(row=>row.stage===stage&&row.codes.includes(code));\n  if(!valid)return unknown('invalid-return');"],
 ];
 let source=WORKFLOW_SETTLEMENT_SUPPORT;
 for(const [from,to]of replacements){if(source.split(from!).length!==2)throw new TypeError('COMPOSED_WORKFLOW_SETTLEMENT:legacy specialization drift');source=source.replace(from!,to!);}
 return source;
}
