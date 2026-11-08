// domainspec.declarative-function/v1; generated from typed contracts, not executable source text.

const fault = code => Object.assign(new Error(code), {code});
const errorCode = error => /^[A-Z][A-Z0-9_]*$/.test(error?.code ?? '') ? error.code : String(error?.message ?? '').match(/\bCALCULATION_(?:OVERFLOW|UNDERFLOW|DIVIDE_BY_ZERO|INEXACT)\b/)?.[0] ?? 'EVALUATION_FAILED';
function emit(observe,event) {if(observe) {try {observe(structuredClone(event));} catch { /* Observers cannot alter evaluation. */ }}}
function observed(declaration,node_kind,compute,observe) {
 emit(observe,{kind:'node-start',declaration,node_kind});
 try {const value=compute();emit(observe,{kind:'node-result',declaration,node_kind,...(node_kind==='Query'?{count:value.length}:{value})});return value;}
 catch(error){emit(observe,{kind:'node-error',declaration,node_kind,code:errorCode(error)});throw error;}
}
function traceQuery(declaration,rows,predicate,project,observe) {
 emit(observe,{kind:'query-start',declaration,total:rows.length});
 // Preserve filter-before-projection order and evaluate each predicate exactly once.
 return rows.filter((row,index)=>{const accepted=predicate(row);emit(observe,{kind:'query-row',declaration,index,accepted,row});return accepted;}).map(project);
}
function assertObserved(index,phase,code,test,observe) {
 const passed=test();emit(observe,{kind:'assertion',index,phase,code,passed});if(!passed)throw fault(code);
}

const memo = f => { let ready=false, value; return () => {if (!ready) {value=f(); ready=true;} return value;}; };
function fullMatch(pattern,value) {const match=pattern.exec(value);return !!match&&match[0].length===value.length;}
function uint64(value) {
 if (typeof value==='number'&&!Number.isSafeInteger(value)||typeof value==='string'&&!fullMatch(/^(0|[1-9][0-9]*)$/,value)||!['bigint','number','string'].includes(typeof value)) throw fault('FUNCTION_UINT64');
 const n=BigInt(value); if(n<0n||n>18446744073709551615n)throw fault('FUNCTION_UINT64');return n;
}
function optionalUint64(value) {return value == null ? null : uint64(value);}
function decimal(value,scale) {
 if(!fullMatch(new RegExp('^(0|[1-9][0-9]*)(\\.[0-9]{1,'+Math.max(1,scale)+'})?$'),value)||(scale===0&&value.includes('.')))throw fault('FUNCTION_DECIMAL');
 const [whole,fraction='']=value.split('.');return uint64(BigInt(whole)*10n**BigInt(scale)+BigInt(fraction.padEnd(scale,'0')||'0'));
}
function format(value,scale) { const n=uint64(value),base=10n**BigInt(scale);return scale ? (n/base)+'.'+(n%base).toString().padStart(scale,'0') : n.toString(); }
function first(rows) { if(rows.length===0)throw fault('DS_QUERY_EMPTY');return rows[0]; }
function one(rows) { if(rows.length!==1)throw fault('DS_QUERY_CARDINALITY');return rows[0]; }

export function validateInput(roots, observe) {const v_input=roots.input;  }
export function execute(roots, api, observe, binding, phase='guard') {
const v_input = roots["input"];
const n_BusinessReceiptBlocked = memo(() => observed("BusinessReceiptBlocked", "Mapping", () => (Object.freeze({"status": "block","repair_focus": "business-receipt","authority_effect": "none"})), observe));
const n_SourceCandidateBlocked = memo(() => observed("SourceCandidateBlocked", "Mapping", () => (Object.freeze({"status": "block","repair_focus": "source-candidate","authority_effect": "none"})), observe));
const n_SystemQuestionsBlocked = memo(() => observed("SystemQuestionsBlocked", "Mapping", () => (Object.freeze({"status": "block","repair_focus": "system-questions","authority_effect": "none"})), observe));
const n_SystemGroundingBlocked = memo(() => observed("SystemGroundingBlocked", "Mapping", () => (Object.freeze({"status": "block","repair_focus": "semantic-grounding","authority_effect": "none"})), observe));
const n_SystemNonCollapseBlocked = memo(() => observed("SystemNonCollapseBlocked", "Mapping", () => (Object.freeze({"status": "block","repair_focus": "non-collapse","authority_effect": "none"})), observe));
const n_SystemOrthogonalityBlocked = memo(() => observed("SystemOrthogonalityBlocked", "Mapping", () => (Object.freeze({"status": "block","repair_focus": "orthogonality","authority_effect": "none"})), observe));
const n_SystemOntologyReady = memo(() => observed("SystemOntologyReady", "Mapping", () => (Object.freeze({"status": "ready","repair_focus": "none","authority_effect": "none"})), observe));
const n_BusinessReceiptMissing = memo(() => observed("BusinessReceiptMissing", "Rule", () => ((v_input["business_receipt_current"] === false)), observe));
const n_SourceCandidateMissing = memo(() => observed("SourceCandidateMissing", "Rule", () => ((v_input["business_receipt_current"] && (v_input["source_candidate_current"] === false))), observe));
const n_SystemQuestionsIncomplete = memo(() => observed("SystemQuestionsIncomplete", "Rule", () => (((v_input["business_receipt_current"] && v_input["source_candidate_current"]) && (v_input["system_questions_complete"] === false))), observe));
const n_SystemGroundingFailed = memo(() => observed("SystemGroundingFailed", "Rule", () => ((((v_input["business_receipt_current"] && v_input["source_candidate_current"]) && v_input["system_questions_complete"]) && (v_input["semantic_grounding_pass"] === false))), observe));
const n_SystemNonCollapseFailed = memo(() => observed("SystemNonCollapseFailed", "Rule", () => (((((v_input["business_receipt_current"] && v_input["source_candidate_current"]) && v_input["system_questions_complete"]) && v_input["semantic_grounding_pass"]) && (v_input["non_collapse_pass"] === false))), observe));
const n_SystemOrthogonalityFailed = memo(() => observed("SystemOrthogonalityFailed", "Rule", () => ((((((v_input["business_receipt_current"] && v_input["source_candidate_current"]) && v_input["system_questions_complete"]) && v_input["semantic_grounding_pass"]) && v_input["non_collapse_pass"]) && (v_input["orthogonality_pass"] === false))), observe));
const n_SystemCanMaterialize = memo(() => observed("SystemCanMaterialize", "Rule", () => ((((((v_input["business_receipt_current"] && v_input["source_candidate_current"]) && v_input["system_questions_complete"]) && v_input["semantic_grounding_pass"]) && v_input["non_collapse_pass"]) && v_input["orthogonality_pass"])), observe));


const matches = [() => (n_BusinessReceiptMissing()),() => (n_SourceCandidateMissing()),() => (n_SystemQuestionsIncomplete()),() => (n_SystemGroundingFailed()),() => (n_SystemNonCollapseFailed()),() => (n_SystemOrthogonalityFailed()),() => (n_SystemCanMaterialize())].map((test,index) => {const passed=test();emit(observe,{kind:'result-case',index,passed});return passed;});
if (matches.filter(Boolean).length !== 1) throw fault('DS_RESULT_CARDINALITY');
if (matches[0]) {emit(observe,{kind:'selected-case',index:0});return n_BusinessReceiptBlocked();}
if (matches[1]) {emit(observe,{kind:'selected-case',index:1});return n_SourceCandidateBlocked();}
if (matches[2]) {emit(observe,{kind:'selected-case',index:2});return n_SystemQuestionsBlocked();}
if (matches[3]) {emit(observe,{kind:'selected-case',index:3});return n_SystemGroundingBlocked();}
if (matches[4]) {emit(observe,{kind:'selected-case',index:4});return n_SystemNonCollapseBlocked();}
if (matches[5]) {emit(observe,{kind:'selected-case',index:5});return n_SystemOrthogonalityBlocked();}
if (matches[6]) {emit(observe,{kind:'selected-case',index:6});return n_SystemOntologyReady();}
}
