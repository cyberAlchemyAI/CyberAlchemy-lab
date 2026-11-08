/** Source-only pre-effect placement regressions; not execution evidence.
 * Open Questions: docs/POLICY-ENFORCEMENT.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {checkCoreGenericOperationSources} from '../../src/commerce/commerce-core-flow-operation.js';

const declarations=`module Placement version 1
entity Counter:
  id UInt64
  value Bool
  version UInt64
  identity id
enum Cause:
  value Denied wire "denied"
enum Admission:
  variant Allow
  variant Reject reason Cause
calculation Allowed:
  pure
  result Admission
  expression Admission.Allow()
policy Eligibility:
  result Admission
  ordered-cases:
    allowed when true -> Allowed()
    otherwise -> Allowed()
interface Application:
  kind application-composition
  service PlacementService module Placement
  formal-claims optional
`;
const create=`  transaction CreateCounter:
    atomic-participants Counter
    create changed Counter:
      id <- id
      value <- true
      version <- 1
    on-version-conflict reject changed
    on-unique-conflict reject duplicate
    on-proven-rollback fail rolled-back
    on-unknown-commit fail unknown
`;
const write=`operation Write:
  input id UInt64
  output Bool
${create}  return true
`;
const check=(extra:string)=>checkCoreGenericOperationSources([{path:'placement.alch',text:declarations+write+extra}],[],'atomic-state-entry');
const preEffectReject=(extra:string)=>assert.throws(()=>check(extra),(error:any)=>error?.diagnostics?.[0]?.code==='UnsupportedCapability'&&error.diagnostics[0].message.includes('pre-effect'));

test('EN02 placement accepts a genuine pre-effect enforcement before a checked local write',()=>{
 assert.doesNotThrow(()=>check(`operation BeforeWrite:
  input id UInt64
  output Bool
  enforce Eligibility()
  call result Write(id=id)
  return result
`));
});
test('EN02 placement refuses an enforcement after a direct local write',()=>{
 preEffectReject(`operation AfterWrite:
  input id UInt64
  output Bool
  call result Write(id=id)
  enforce Eligibility()
  return result
`);
});
test('EN02 placement follows invoke-return wrappers when determining previous local effects',()=>{
 preEffectReject(`operation Wrapper:
  input id UInt64
  output Bool
  return Write(id=id)
operation AfterWrapper:
  input id UInt64
  output Bool
  call result Wrapper(id=id)
  enforce Eligibility()
  return result
`);
});
test('EN02 placement follows a conditional invoke-return wrapper transitively',()=>{
 preEffectReject(`operation ConditionalWrapper:
  input id UInt64
  output Bool
  when id > 0:
    return Write(id=id)
  otherwise:
    return false
operation OuterWrapper:
  input id UInt64
  output Bool
  return ConditionalWrapper(id=id)
operation AfterWrapper:
  input id UInt64
  output Bool
  call result OuterWrapper(id=id)
  enforce Eligibility()
  return result
`);
});
test('EN02 placement follows invoke-return actions in inline conditions',()=>{
 preEffectReject(`operation ConditionalActionWrapper:
  input id UInt64
  output Bool
  on id > 0 return Write(id=id)
  return false
operation AfterWrapper:
  input id UInt64
  output Bool
  call result ConditionalActionWrapper(id=id)
  enforce Eligibility()
  return result
`);
});
test('EN02 placement retains effects of on-present transactions on a continuing path',()=>{
 preEffectReject(`operation AfterPresentTransaction:
  input id UInt64
  input candidate optional<Bool>
  output Bool
  on-present candidate ${create.trimStart()}  enforce Eligibility()
  return true
`);
});
test('EN02 placement does not inherit a transaction from an already terminal branch',()=>{
 assert.doesNotThrow(()=>check(`operation ConditionalTerminal:
  input id UInt64
  output Bool
  when id > 0:
    return Write(id=id)
  enforce Eligibility()
  return false
`));
});
test('EN02 placement keeps pure enum-constructor returns distinct from invoke-return effects',()=>{
 assert.doesNotThrow(()=>check(`operation PureResult:
  output Admission
  return Admission.Allow()
operation AfterPureResult:
  output Bool
  call result PureResult()
  enforce Eligibility()
  return true
`));
});
