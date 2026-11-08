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
const n_PackInvalid = memo(() => observed("PackInvalid", "Mapping", () => (Object.freeze({"status": "invalid","valid": false,"handoff_ready": false,"session_state": "validation-blocked","authority_effect": "none"})), observe));
const n_PackValidOpen = memo(() => observed("PackValidOpen", "Mapping", () => (Object.freeze({"status": "valid_open","valid": true,"handoff_ready": false,"session_state": "blocked-open-meaning","authority_effect": "none"})), observe));
const n_PackHandoffReady = memo(() => observed("PackHandoffReady", "Mapping", () => (Object.freeze({"status": "handoff_ready","valid": true,"handoff_ready": true,"session_state": "definition-pack-complete","authority_effect": "none"})), observe));
const n_PackHasDefect = memo(() => observed("PackHasDefect", "Rule", () => ((!((((((((v_input["version_supported"] && v_input["identity_complete"]) && v_input["scope_complete"]) && v_input["concepts_present"]) && v_input["dispositions_exact"]) && v_input["dispositions_declared"]) && v_input["authority_none"]) && v_input["language_quality_pass"]) && v_input["language_evidence_complete"]))), observe));
const n_PackIsValidWithOpenMeaning = memo(() => observed("PackIsValidWithOpenMeaning", "Rule", () => ((((((((((v_input["version_supported"] && v_input["identity_complete"]) && v_input["scope_complete"]) && v_input["concepts_present"]) && v_input["dispositions_exact"]) && v_input["dispositions_declared"]) && v_input["authority_none"]) && v_input["language_quality_pass"]) && v_input["language_evidence_complete"]) && (v_input["open_questions_empty"] === false))), observe));
const n_PackIsHandoffReady = memo(() => observed("PackIsHandoffReady", "Rule", () => ((((((((((v_input["version_supported"] && v_input["identity_complete"]) && v_input["scope_complete"]) && v_input["concepts_present"]) && v_input["dispositions_exact"]) && v_input["dispositions_declared"]) && v_input["authority_none"]) && v_input["language_quality_pass"]) && v_input["language_evidence_complete"]) && v_input["open_questions_empty"])), observe));


const matches = [() => (n_PackHasDefect()),() => (n_PackIsValidWithOpenMeaning()),() => (n_PackIsHandoffReady())].map((test,index) => {const passed=test();emit(observe,{kind:'result-case',index,passed});return passed;});
if (matches.filter(Boolean).length !== 1) throw fault('DS_RESULT_CARDINALITY');
if (matches[0]) {emit(observe,{kind:'selected-case',index:0});return n_PackInvalid();}
if (matches[1]) {emit(observe,{kind:'selected-case',index:1});return n_PackValidOpen();}
if (matches[2]) {emit(observe,{kind:'selected-case',index:2});return n_PackHandoffReady();}
}
