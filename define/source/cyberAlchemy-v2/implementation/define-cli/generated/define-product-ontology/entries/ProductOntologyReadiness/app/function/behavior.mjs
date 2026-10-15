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
const n_DefinitionPackBlocked = memo(() => observed("DefinitionPackBlocked", "Mapping", () => (Object.freeze({"status": "block","repair_focus": "definition-pack","authority_effect": "none"})), observe));
const n_ProductQuestionsBlocked = memo(() => observed("ProductQuestionsBlocked", "Mapping", () => (Object.freeze({"status": "block","repair_focus": "product-questions","authority_effect": "none"})), observe));
const n_ProductGroundingBlocked = memo(() => observed("ProductGroundingBlocked", "Mapping", () => (Object.freeze({"status": "block","repair_focus": "semantic-grounding","authority_effect": "none"})), observe));
const n_ProductNonCollapseBlocked = memo(() => observed("ProductNonCollapseBlocked", "Mapping", () => (Object.freeze({"status": "block","repair_focus": "non-collapse","authority_effect": "none"})), observe));
const n_ProductOrthogonalityBlocked = memo(() => observed("ProductOrthogonalityBlocked", "Mapping", () => (Object.freeze({"status": "block","repair_focus": "orthogonality","authority_effect": "none"})), observe));
const n_ProductOntologyReady = memo(() => observed("ProductOntologyReady", "Mapping", () => (Object.freeze({"status": "ready","repair_focus": "none","authority_effect": "none"})), observe));
const n_DefinitionPackMissing = memo(() => observed("DefinitionPackMissing", "Rule", () => ((v_input["definition_pack_current"] === false)), observe));
const n_ProductQuestionsIncomplete = memo(() => observed("ProductQuestionsIncomplete", "Rule", () => ((v_input["definition_pack_current"] && (v_input["product_questions_complete"] === false))), observe));
const n_ProductGroundingFailed = memo(() => observed("ProductGroundingFailed", "Rule", () => (((v_input["definition_pack_current"] && v_input["product_questions_complete"]) && (v_input["semantic_grounding_pass"] === false))), observe));
const n_ProductNonCollapseFailed = memo(() => observed("ProductNonCollapseFailed", "Rule", () => ((((v_input["definition_pack_current"] && v_input["product_questions_complete"]) && v_input["semantic_grounding_pass"]) && (v_input["non_collapse_pass"] === false))), observe));
const n_ProductOrthogonalityFailed = memo(() => observed("ProductOrthogonalityFailed", "Rule", () => (((((v_input["definition_pack_current"] && v_input["product_questions_complete"]) && v_input["semantic_grounding_pass"]) && v_input["non_collapse_pass"]) && (v_input["orthogonality_pass"] === false))), observe));
const n_ProductCanMaterialize = memo(() => observed("ProductCanMaterialize", "Rule", () => (((((v_input["definition_pack_current"] && v_input["product_questions_complete"]) && v_input["semantic_grounding_pass"]) && v_input["non_collapse_pass"]) && v_input["orthogonality_pass"])), observe));


const matches = [() => (n_DefinitionPackMissing()),() => (n_ProductQuestionsIncomplete()),() => (n_ProductGroundingFailed()),() => (n_ProductNonCollapseFailed()),() => (n_ProductOrthogonalityFailed()),() => (n_ProductCanMaterialize())].map((test,index) => {const passed=test();emit(observe,{kind:'result-case',index,passed});return passed;});
if (matches.filter(Boolean).length !== 1) throw fault('DS_RESULT_CARDINALITY');
if (matches[0]) {emit(observe,{kind:'selected-case',index:0});return n_DefinitionPackBlocked();}
if (matches[1]) {emit(observe,{kind:'selected-case',index:1});return n_ProductQuestionsBlocked();}
if (matches[2]) {emit(observe,{kind:'selected-case',index:2});return n_ProductGroundingBlocked();}
if (matches[3]) {emit(observe,{kind:'selected-case',index:3});return n_ProductNonCollapseBlocked();}
if (matches[4]) {emit(observe,{kind:'selected-case',index:4});return n_ProductOrthogonalityBlocked();}
if (matches[5]) {emit(observe,{kind:'selected-case',index:5});return n_ProductOntologyReady();}
}
