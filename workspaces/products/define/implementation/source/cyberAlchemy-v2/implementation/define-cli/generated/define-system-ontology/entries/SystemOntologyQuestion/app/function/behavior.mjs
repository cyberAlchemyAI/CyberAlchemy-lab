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
const n_AskRuntimeBoundary = memo(() => observed("AskRuntimeBoundary", "Mapping", () => (Object.freeze({"status": "ask","next_focus": "runtime-boundary","authority_effect": "none"})), observe));
const n_AskComponents = memo(() => observed("AskComponents", "Mapping", () => (Object.freeze({"status": "ask","next_focus": "components","authority_effect": "none"})), observe));
const n_AskInterfaces = memo(() => observed("AskInterfaces", "Mapping", () => (Object.freeze({"status": "ask","next_focus": "interfaces","authority_effect": "none"})), observe));
const n_AskStateModel = memo(() => observed("AskStateModel", "Mapping", () => (Object.freeze({"status": "ask","next_focus": "state-model","authority_effect": "none"})), observe));
const n_AskPersistenceRecovery = memo(() => observed("AskPersistenceRecovery", "Mapping", () => (Object.freeze({"status": "ask","next_focus": "persistence-recovery","authority_effect": "none"})), observe));
const n_AskOperatingConstraints = memo(() => observed("AskOperatingConstraints", "Mapping", () => (Object.freeze({"status": "ask","next_focus": "operating-constraints","authority_effect": "none"})), observe));
const n_SystemQuestionsComplete = memo(() => observed("SystemQuestionsComplete", "Mapping", () => (Object.freeze({"status": "complete","next_focus": "none","authority_effect": "none"})), observe));
const n_RuntimeBoundaryMissing = memo(() => observed("RuntimeBoundaryMissing", "Rule", () => ((v_input["runtime_boundary_present"] === false)), observe));
const n_ComponentsMissing = memo(() => observed("ComponentsMissing", "Rule", () => ((v_input["runtime_boundary_present"] && (v_input["components_present"] === false))), observe));
const n_InterfacesMissing = memo(() => observed("InterfacesMissing", "Rule", () => (((v_input["runtime_boundary_present"] && v_input["components_present"]) && (v_input["interfaces_present"] === false))), observe));
const n_StateModelMissing = memo(() => observed("StateModelMissing", "Rule", () => ((((v_input["runtime_boundary_present"] && v_input["components_present"]) && v_input["interfaces_present"]) && (v_input["state_model_present"] === false))), observe));
const n_PersistenceRecoveryMissing = memo(() => observed("PersistenceRecoveryMissing", "Rule", () => (((((v_input["runtime_boundary_present"] && v_input["components_present"]) && v_input["interfaces_present"]) && v_input["state_model_present"]) && (v_input["persistence_recovery_present"] === false))), observe));
const n_OperatingConstraintsMissing = memo(() => observed("OperatingConstraintsMissing", "Rule", () => ((((((v_input["runtime_boundary_present"] && v_input["components_present"]) && v_input["interfaces_present"]) && v_input["state_model_present"]) && v_input["persistence_recovery_present"]) && (v_input["operating_constraints_present"] === false))), observe));
const n_QuestionsComplete = memo(() => observed("QuestionsComplete", "Rule", () => ((((((v_input["runtime_boundary_present"] && v_input["components_present"]) && v_input["interfaces_present"]) && v_input["state_model_present"]) && v_input["persistence_recovery_present"]) && v_input["operating_constraints_present"])), observe));


const matches = [() => (n_RuntimeBoundaryMissing()),() => (n_ComponentsMissing()),() => (n_InterfacesMissing()),() => (n_StateModelMissing()),() => (n_PersistenceRecoveryMissing()),() => (n_OperatingConstraintsMissing()),() => (n_QuestionsComplete())].map((test,index) => {const passed=test();emit(observe,{kind:'result-case',index,passed});return passed;});
if (matches.filter(Boolean).length !== 1) throw fault('DS_RESULT_CARDINALITY');
if (matches[0]) {emit(observe,{kind:'selected-case',index:0});return n_AskRuntimeBoundary();}
if (matches[1]) {emit(observe,{kind:'selected-case',index:1});return n_AskComponents();}
if (matches[2]) {emit(observe,{kind:'selected-case',index:2});return n_AskInterfaces();}
if (matches[3]) {emit(observe,{kind:'selected-case',index:3});return n_AskStateModel();}
if (matches[4]) {emit(observe,{kind:'selected-case',index:4});return n_AskPersistenceRecovery();}
if (matches[5]) {emit(observe,{kind:'selected-case',index:5});return n_AskOperatingConstraints();}
if (matches[6]) {emit(observe,{kind:'selected-case',index:6});return n_SystemQuestionsComplete();}
}
