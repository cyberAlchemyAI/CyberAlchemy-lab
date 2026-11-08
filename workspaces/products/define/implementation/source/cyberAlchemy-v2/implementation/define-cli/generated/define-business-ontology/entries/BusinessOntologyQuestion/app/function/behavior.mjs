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
const n_AskMeaningOwner = memo(() => observed("AskMeaningOwner", "Mapping", () => (Object.freeze({"status": "ask","next_focus": "meaning-owner","authority_effect": "none"})), observe));
const n_AskBoundedModel = memo(() => observed("AskBoundedModel", "Mapping", () => (Object.freeze({"status": "ask","next_focus": "bounded-model","authority_effect": "none"})), observe));
const n_AskConceptsAndRelationships = memo(() => observed("AskConceptsAndRelationships", "Mapping", () => (Object.freeze({"status": "ask","next_focus": "concepts-and-relationships","authority_effect": "none"})), observe));
const n_AskDomainRule = memo(() => observed("AskDomainRule", "Mapping", () => (Object.freeze({"status": "ask","next_focus": "domain-rule","authority_effect": "none"})), observe));
const n_AskLifecycle = memo(() => observed("AskLifecycle", "Mapping", () => (Object.freeze({"status": "ask","next_focus": "lifecycle","authority_effect": "none"})), observe));
const n_AskAuthorityBoundary = memo(() => observed("AskAuthorityBoundary", "Mapping", () => (Object.freeze({"status": "ask","next_focus": "authority-boundary","authority_effect": "none"})), observe));
const n_BusinessQuestionsComplete = memo(() => observed("BusinessQuestionsComplete", "Mapping", () => (Object.freeze({"status": "complete","next_focus": "none","authority_effect": "none"})), observe));
const n_MeaningOwnerMissing = memo(() => observed("MeaningOwnerMissing", "Rule", () => ((v_input["meaning_owner_present"] === false)), observe));
const n_BoundedModelMissing = memo(() => observed("BoundedModelMissing", "Rule", () => ((v_input["meaning_owner_present"] && (v_input["bounded_model_present"] === false))), observe));
const n_ConceptsAndRelationshipsMissing = memo(() => observed("ConceptsAndRelationshipsMissing", "Rule", () => (((v_input["meaning_owner_present"] && v_input["bounded_model_present"]) && (v_input["concepts_and_relationships_present"] === false))), observe));
const n_DomainRuleMissing = memo(() => observed("DomainRuleMissing", "Rule", () => ((((v_input["meaning_owner_present"] && v_input["bounded_model_present"]) && v_input["concepts_and_relationships_present"]) && (v_input["domain_rule_present"] === false))), observe));
const n_LifecycleMissing = memo(() => observed("LifecycleMissing", "Rule", () => (((((v_input["meaning_owner_present"] && v_input["bounded_model_present"]) && v_input["concepts_and_relationships_present"]) && v_input["domain_rule_present"]) && (v_input["lifecycle_present"] === false))), observe));
const n_AuthorityBoundaryMissing = memo(() => observed("AuthorityBoundaryMissing", "Rule", () => ((((((v_input["meaning_owner_present"] && v_input["bounded_model_present"]) && v_input["concepts_and_relationships_present"]) && v_input["domain_rule_present"]) && v_input["lifecycle_present"]) && (v_input["authority_boundary_present"] === false))), observe));
const n_QuestionsComplete = memo(() => observed("QuestionsComplete", "Rule", () => ((((((v_input["meaning_owner_present"] && v_input["bounded_model_present"]) && v_input["concepts_and_relationships_present"]) && v_input["domain_rule_present"]) && v_input["lifecycle_present"]) && v_input["authority_boundary_present"])), observe));


const matches = [() => (n_MeaningOwnerMissing()),() => (n_BoundedModelMissing()),() => (n_ConceptsAndRelationshipsMissing()),() => (n_DomainRuleMissing()),() => (n_LifecycleMissing()),() => (n_AuthorityBoundaryMissing()),() => (n_QuestionsComplete())].map((test,index) => {const passed=test();emit(observe,{kind:'result-case',index,passed});return passed;});
if (matches.filter(Boolean).length !== 1) throw fault('DS_RESULT_CARDINALITY');
if (matches[0]) {emit(observe,{kind:'selected-case',index:0});return n_AskMeaningOwner();}
if (matches[1]) {emit(observe,{kind:'selected-case',index:1});return n_AskBoundedModel();}
if (matches[2]) {emit(observe,{kind:'selected-case',index:2});return n_AskConceptsAndRelationships();}
if (matches[3]) {emit(observe,{kind:'selected-case',index:3});return n_AskDomainRule();}
if (matches[4]) {emit(observe,{kind:'selected-case',index:4});return n_AskLifecycle();}
if (matches[5]) {emit(observe,{kind:'selected-case',index:5});return n_AskAuthorityBoundary();}
if (matches[6]) {emit(observe,{kind:'selected-case',index:6});return n_BusinessQuestionsComplete();}
}
