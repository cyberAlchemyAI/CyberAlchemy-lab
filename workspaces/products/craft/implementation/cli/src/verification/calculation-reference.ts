import type {TypedCalculationContract, NumericExpression} from '../typed-backend/contracts.js';
import type {ExactCalculationContract, ExactNumericExpression} from '../typed-backend/calculation-exact.js';
export type Calculation = TypedCalculationContract | ExactCalculationContract;
export type CalculationOutcome = Readonly<{kind:'value';value:string}> | Readonly<{kind:'error';name:'RangeError'|'TypeError';message:string}>;
const max = 18446744073709551615n;
const fail=(message:string):never=>{throw new TypeError('DS_RECONCILED_SEMANTIC_CONTROLS:'+message);};
const error=(message:string):CalculationOutcome=>({kind:'error',name:message==='CALCULATION_INPUT'?'TypeError':'RangeError',message});

/** Reference arithmetic is deliberately independent of the generated postorder program. */
export function expectedCalculation(contract:Calculation,values:readonly string[]):CalculationOutcome{
 const inputs=new Map(contract.inputs.map((p,i)=>[p.name,BigInt(values[i]!)]));
 const evaluate=(e:NumericExpression|ExactNumericExpression):bigint=>{
  if(e.op==='literal')return BigInt(e.value);
  if(e.op==='input')return inputs.get(e.name)??fail('missing checked input');
  const a=evaluate(e.left),b=evaluate(e.right);
  let result:bigint;
  switch(e.op){
   case 'add':result=a+b;break;
   case 'subtract':result=a-b;break;
   case 'multiply':result=a*b;break;
   case 'divide':
    if(b===0n)throw 'CALCULATION_DIVIDE_BY_ZERO';
    if(a%b!==0n&&contract.division_rounding==='reject')throw 'CALCULATION_INEXACT';
    result=a/b;if(a%b!==0n&&contract.division_rounding==='ceil')result+=1n;break;
  }
  if(result<0n)throw 'CALCULATION_UNDERFLOW';
  if(result>max)throw 'CALCULATION_OVERFLOW';
  return result;
 };
 try{return {kind:'value',value:evaluate(contract.expression).toString()};}
 catch(reason){if(typeof reason==='string'&&reason.startsWith('CALCULATION_'))return error(reason);throw reason;}
}

