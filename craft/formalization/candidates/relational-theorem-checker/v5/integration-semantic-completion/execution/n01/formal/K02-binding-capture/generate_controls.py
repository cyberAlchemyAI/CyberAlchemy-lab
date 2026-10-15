"""Generate synthetic capture controls. No byte parser or authentication is inferred."""
from pathlib import Path
import copy,hashlib,importlib.util,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[9]
SRC=HERE.parent/'K02-binding-records/generate_controls.py'
spec=importlib.util.spec_from_file_location('record_generator',SRC);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def run():
    rows=['import CaptureCatalog','set_option autoImplicit false','namespace RelationalSuccessor.CandidateBindingCapture.Controls','open RelationalSuccessor','open RelationalSuccessor.CandidateBindingCapture','open RelationalSuccessor.CandidateBindingRecords','open RelationalSuccessor.CandidateBindingAst','open RelationalSuccessor.CandidateIntentAddressing (Resolution Role)',''];names=[];cases=[];sources=[]
    def theorem(name,statement,proof='by decide'):
        rows.extend([f'theorem {name} : {statement} := {proof}','']);names.append(name);cases.append({'name':name,'method':'closed kernel proof control'})
    for kind,typ in [('resolution','Resolution'),('role','Role')]:
        p=HERE.parent/f'K02-pipeline/schemas/{kind}-binding.fixture.json';x=json.loads(p.read_text());sources.append(bind(p))
        rows.extend([f'def {kind}Ast : J := {module.ast(x)}',f'def {kind}Record : Record {typ} := {module.record(kind,x)}',f'def {kind}Frame : Frame := {kind}Record.body.frame',f'def {kind}Envelope : Envelope := ⟨[1,2],2,{kind}Record.ownerReview,"synthetic-claimed-digest"⟩',f'def {kind}Prepared : Prepared {typ} := ⟨{kind}Record,{kind}Envelope⟩',f'def {kind}Input : Input := ⟨{kind}Ast,{kind}Envelope⟩',f'def {kind}Stage : CatalogStage {typ} := ⟨{kind}Frame,{kind}Envelope.digestProfile,[{kind}Prepared],[{kind}Prepared]⟩',''])
        function='prepareResolution' if kind=='resolution' else 'prepareRole';cf=function+'Catalog'
        theorem(kind+'_prepare_accepts',f'{function} {kind}Frame {kind}Envelope {kind}Ast = some {kind}Prepared')
        theorem(kind+'_wrong_length_refuses',f'{function} {kind}Frame {{ {kind}Envelope with byteLength := 3 }} {kind}Ast = none')
        theorem(kind+'_empty_digest_refuses',f'{function} {kind}Frame {{ {kind}Envelope with digest := "" }} {kind}Ast = none')
        theorem(kind+'_empty_profile_digest_refuses',f'{function} {kind}Frame {{ {kind}Envelope with digestProfile := {{ {kind}Envelope.digestProfile with digest := "" }} }} {kind}Ast = none')
        theorem(kind+'_stale_epoch_refuses',f'{function} {{ {kind}Frame with epoch := 43 }} {kind}Envelope {kind}Ast = none')
        theorem(kind+'_null_AST_refuses',f'{function} {kind}Frame {kind}Envelope .null = none')
        theorem(kind+'_catalog_stage_accepts',f'{cf} {kind}Frame {kind}Envelope.digestProfile [{kind}Input] [{kind}Input] = some {kind}Stage')
        theorem(kind+'_missing_root_refuses',f'{cf} {kind}Frame {kind}Envelope.digestProfile [{kind}Input] [] = none')
        theorem(kind+'_wrong_requested_profile_refuses',f'{cf} {kind}Frame {{ {kind}Envelope.digestProfile with digest := "different-profile" }} [{kind}Input] [{kind}Input] = none')
        theorem(kind+'_mixed_profiles_refuse',f'{cf} {kind}Frame {kind}Envelope.digestProfile [{kind}Input,{{ {kind}Input with envelope := {{ {kind}Envelope with digestProfile := {{ {kind}Envelope.digestProfile with digest := "different-profile" }} }} }}] [{kind}Input,{{ {kind}Input with envelope := {{ {kind}Envelope with digestProfile := {{ {kind}Envelope.digestProfile with digest := "different-profile" }} }} }}] = none')
        theorem(kind+'_identical_retry_accepts',f'{cf} {kind}Frame {kind}Envelope.digestProfile [{kind}Input,{kind}Input] [{kind}Input] = some {{ {kind}Stage with records := [{kind}Prepared,{kind}Prepared] }}')
        theorem(kind+'_different_bytes_conflict_refuses',f'{cf} {kind}Frame {kind}Envelope.digestProfile [{kind}Input,{{ {kind}Input with envelope := {{ {kind}Envelope with content := [3,4] }} }}] [{kind}Input,{{ {kind}Input with envelope := {{ {kind}Envelope with content := [3,4] }} }}] = none')
        theorem(kind+'_unchanged_length_is_not_byte_authentication',f'{function} {kind}Frame {{ {kind}Envelope with content := [3,4] }} {kind}Ast = some {{ {kind}Prepared with envelope := {{ {kind}Envelope with content := [3,4] }} }}')
        theorem(kind+'_digest_label_is_not_computation',f'{function} {kind}Frame {{ {kind}Envelope with digest := "uncomputed-label" }} {kind}Ast = some {{ {kind}Prepared with envelope := {{ {kind}Envelope with digest := "uncomputed-label" }} }}')
        rows.extend([f'def {kind}UnparsedPolicy : Policies {typ} := ⟨(fun _ _ => False),(fun _ _ _ => False),(fun _ _ => False),(fun _ _ _ _ => False),(fun _ _ => False)⟩',''])
        theorem(kind+'_prepared_syntax_is_not_authentic_capture',f'¬ CaptureMeaning {kind}UnparsedPolicy {kind}Version {kind}Kind {kind} {kind}Frame {kind}Envelope {kind}Ast {kind}Prepared',f'by\n  apply unparsed_bytes_prevent_capture\n  exact fun impossible => impossible')
        theorem(kind+'_stage_retains_profile_and_version',f'{kind}Stage.records = [{kind}Prepared] ∧ {kind}Prepared.envelope.digestProfile = {kind}Envelope.digestProfile ∧ {kind}Prepared.record.schemaVersion = {kind}Version')
    rows.extend(f'#print axioms {name}' for name in names);rows.extend(['end RelationalSuccessor.CandidateBindingCapture.Controls',''])
    (HERE/'CaptureControls.lean').write_text('\n'.join(rows))
    report={'task':'N01','unit':'K02-binding-capture','generator':bind(Path(__file__)),'record_literal_generator':bind(SRC),'fixtures':sources,'controls':bind(HERE/'CaptureControls.lean'),'worked_control_declarations':len(names),'cases':cases,'bytes_are_synthetic_and_not_parsed':True,'digest_is_uncomputed_synthetic_label':True,'review_roots_are_synthetic':True,'method':'Python fixture-to-literal generation; translation not proved. Kernel controls concern explicit retained ASTs and synthetic envelopes.','byte_parser_proved':False,'digest_algorithm_realized':False,'authenticated_capture_proved':False,'full_source_policy_realization_proved':False,'inherited_discharges':0,'authority_effect':'none'}
    (HERE/'source-capture.json').write_text(json.dumps(report,indent=2)+'\n');print('capture controls',len(names))
if __name__=='__main__':run()
