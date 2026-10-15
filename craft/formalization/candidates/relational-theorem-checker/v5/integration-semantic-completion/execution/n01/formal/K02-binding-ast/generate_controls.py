from pathlib import Path
import json,hashlib
root=Path('/home/vlad_/projects/CyberAlchemy-lab')
n=root/'craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01'
p=n/'formal/K02-binding-ast';s=n/'formal/K02-pipeline/schemas'
r=json.loads((s/'resolution-binding.fixture.json').read_text());k=json.loads((s/'role-binding.fixture.json').read_text())
def quoted(t):return json.dumps(t,ensure_ascii=False)
def ast(v):
 if isinstance(v,str):return f'(.string {quoted(v)})'
 if isinstance(v,list):return '(.array ['+', '.join(map(ast,v))+'])'
 if isinstance(v,dict):return '(.object ['+', '.join('('+quoted(k)+', '+ast(x)+')' for k,x in v.items())+'])'
 raise ValueError(v)
def rev(v):return '⟨⟨'+','.join(quoted(v['key'][x]) for x in ['owner','artifact','revision'])+'⟩,'+quoted(v['digest'])+'⟩'
def revlist(v):return '['+','.join(map(rev,v))+']'
target=r['body']['target']; role=k['body']['target'];reference=target['ref'];key=r['binding_revision_key']
subject_case={'agent-assignment':'agentAssignment','goal':'goal','product':'product','product-capability':'productCapability','project':'project','research-inquiry':'researchInquiry','other':'other'}[role['subjectKind']]
rows=['import BindingTargets','set_option autoImplicit false','namespace RelationalSuccessor.CandidateBindingAst.Controls','open RelationalSuccessor','open RelationalSuccessor.CandidateBindingAst','open RelationalSuccessor.CandidateIntentAddressing (Resolution Role)','',f'def referenceAst : J := {ast(reference)}',f'def expectedReference : RevisionRef := {rev(reference)}',f'def keyAst : J := {ast(key)}',f'def expectedKey : RevisionKey := ⟨'+','.join(quoted(key[x]) for x in ['owner','artifact','revision'])+'⟩',f'def roleAst : J := {ast(role)}',f'def expectedRole : Role := ⟨{rev(role["ref"])},{quoted(role["code"])},.{subject_case}⟩',f'def resolutionAst : J := {ast(target)}',f'def expectedResolution : Resolution := ⟨'+','.join([rev(target[x]) for x in ['ref','scope','intent','ownerDecision']]+[revlist(target[x]) for x in ['selectedSubjects','excludedSubjects','satisfactionTests']])+'⟩','']
# Check role enum in source; do not silently assume unrelated subject kind.
assert subject_case in {'agentAssignment','goal','product','productCapability','project','researchInquiry','other'}
names=[]
def theorem(name,expr,proof='by decide'):
 names.append(name); rows.extend([f'theorem {name} : {expr} := {proof}',''])
theorem('original_key_accepts','key.decode keyAst = some expectedKey')
theorem('original_reference_accepts','reference.decode referenceAst = some expectedReference')
theorem('original_role_target_accepts','role.decode roleAst = some expectedRole')
theorem('original_resolution_target_accepts','resolution.decode resolutionAst = some expectedResolution')
theorem('key_order_permutation_accepts',f'key.decode {ast(dict(reversed(list(key.items()))))} = some expectedKey')
bad=dict(key);bad['owner']='';theorem('empty_key_owner_refuses',f'key.decode {ast(bad)} = none')
bad=dict(reference);bad['digest']='';theorem('empty_reference_digest_refuses',f'reference.decode {ast(bad)} = none')
bad=dict(reference);bad['approval']=True
# bool explicit node not supported ast helper
badexpr='(.object [("key", '+ast(reference['key'])+'), ("digest", .string '+quoted(reference['digest'])+'), ("approval", .boolean true)])'
theorem('extra_approval_field_refuses',f'reference.decode {badexpr} = none')
badexpr='(.object [("key", '+ast(reference['key'])+'), ("digest", .string '+quoted(reference['digest'])+'), ("digest", .string '+quoted(reference['digest'])+')])'
theorem('identical_duplicate_digest_refuses',f'reference.decode {badexpr} = none')
bad=dict(reference);del bad['digest'];theorem('missing_digest_refuses',f'reference.decode {ast(bad)} = none')
bad=dict(role);bad['code']='';theorem('empty_role_code_refuses',f'role.decode {ast(bad)} = none')
bad=dict(role);bad['subjectKind']='principal';theorem('unlisted_role_subject_kind_refuses',f'role.decode {ast(bad)} = none')
bad=dict(role);bad['subjectKind']='other';theorem('other_role_is_syntax_valid',f'role.decode {ast(bad)} = some {{expectedRole with subjectKind := .other}}')
bad=dict(target);bad['selectedSubjects']=[];theorem('empty_selection_is_syntax_valid',f'resolution.decode {ast(bad)} = some {{expectedResolution with selectedSubjects := []}}')
bad=dict(target);bad['selectedSubjects']=[reference,reference];theorem('selection_repetitions_preserved',f'resolution.decode {ast(bad)} = some {{expectedResolution with selectedSubjects := [expectedReference,expectedReference]}}')
bad=dict(target);bad['selectedSubjects']=[reference,target['intent']];theorem('selection_order_preserved',f'resolution.decode {ast(bad)} = some {{expectedResolution with selectedSubjects := [expectedReference,{rev(target["intent"])}]}}')
bad=dict(target);bad['selectedSubjects']=[{'key':reference['key'],'digest':''}];theorem('bad_array_element_refuses',f'resolution.decode {ast(bad)} = none')
bad=dict(target);del bad['ownerDecision'];theorem('missing_owner_decision_refuses',f'resolution.decode {ast(bad)} = none')
theorem('original_role_has_independent_meaning','RoleMeaning roleAst expectedRole','(role_exact roleAst expectedRole).mp original_role_target_accepts')
theorem('original_resolution_has_independent_meaning','ResolutionMeaning resolutionAst expectedResolution','(resolution_exact resolutionAst expectedResolution).mp original_resolution_target_accepts')
rows += [f'#print axioms {name}' for name in names];rows += ['end RelationalSuccessor.CandidateBindingAst.Controls','']
(p/'BindingAstControls.lean').write_text('\n'.join(rows))
def binding(path):return {'path':str(path.relative_to(root)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
capture={'task':'N01','unit':'K02-binding-ast','method':'Python JSON to Lean retained-entry AST/typed literals for source target examples only; this translation is not proved.','resolution_fixture':binding(s/'resolution-binding.fixture.json'),'role_fixture':binding(s/'role-binding.fixture.json'),'resolution_schema':binding(s/'resolution-binding.schema.json'),'role_schema':binding(s/'role-binding.schema.json'),'generated_controls':binding(p/'BindingAstControls.lean'),'generator':binding(Path(__file__)),'captured_context_is_synthetic':True,'byte_parser_proved':False,'schema_AST_correspondence_proved':False,'complete_binding_record_AST_proved':False,'inherited_discharges':0}
(p/'source-capture.json').write_text(json.dumps(capture,indent=2)+'\n')
print('controls',len(names))
