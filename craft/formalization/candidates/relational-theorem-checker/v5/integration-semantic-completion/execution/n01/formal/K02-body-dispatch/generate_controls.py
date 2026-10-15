"""Bind existing source controls and exercise automatic dispatch and all-occurrence alignment."""
from pathlib import Path
import hashlib, json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[9]
PRIOR=HERE.parent/'K02-typed-payload-bodies'
def binding(path): return {'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def save(path,value): path.write_text(json.dumps(value,indent=2)+'\n')
def literal(text): return json.dumps(text,ensure_ascii=False)

def run():
    fixture=json.loads((PRIOR/'fixture-validation.json').read_text())
    assert fixture['result']=='complete-typed-body-control-inputs-pass'
    manifest_path=HERE.parent/'K02-complete-payload-provider/profile-manifest.json'
    manifest=json.loads(manifest_path.read_text())
    cases=[]
    def case(identifier,expression,expected):
        cases.append({'id':identifier,'expression':expression,'expected':expected})
    header='''import TypedPayloadIntegration
import ScalarDocumentComposition
import CatalogRuntimeEncoding
import NestedControls
set_option autoImplicit false
set_option maxRecDepth 65536
set_option maxHeartbeats 10000000
namespace RelationalSuccessor.CandidateBodyDispatch.RuntimeControls
open CandidateCatalogSnapshots.RuntimeEncoding (encodeRef encodeBytes)
def checked (text : String) :=
  (CandidateScalarConversion.parseScalarDocumentBytes text.toUTF8.toList).bind decodeBody
def checkedForSourceKind (sourceKind text : String) :=
  (checked text).bind fun output =>
    if kindName (bodyKind output) = sourceKind then some output else none
def selected (text : String) :=
  (CandidateScalarConversion.parseScalarDocumentBytes text.toUTF8.toList).bind selectKind
def syntheticRef (identity : String) : RevisionRef :=
  ⟨⟨"synthetic-fixture-owner",identity,"fixture.1"⟩,"synthetic-fixture-digest"⟩
def artifactAst (text sourceKind identity : String) : Option CandidateBindingAst.J :=
  (CandidateScalarConversion.parseScalarDocumentBytes text.toUTF8.toList).map fun ast =>
    .object [("ref",encodeRef (syntheticRef identity)),("sourceKind",.string sourceKind),
      ("body",ast),("content",encodeBytes text.toUTF8.toList),
      ("ownerReview",encodeRef (syntheticRef "review:synthetic"))]
def checkedArtifact (text sourceKind identity : String) :=
  (artifactAst text sourceKind identity).bind alignedArtifact.decode
def alignmentOf (text sourceKind identity : String) (roots : Bool) : Bool :=
  match checkedArtifact text sourceKind identity with
  | none => false
  | some artifact =>
    let base := CandidateNestedProvenance.RuntimeControls.catalogs
    let wrong := {artifact with sourceKind := "wrong-source-kind"}
    let payload : CandidateFiniteSourceCatalog.Capture PayloadBody :=
      ⟨base.payload.frame,if roots then [artifact] else [artifact,wrong],[],
        if roots then [⟨.subject,wrong,base.payload.frame⟩] else []⟩
    alignmentCheck ⟨base.metadata,payload,base.owned⟩
'''
    for row in fixture['input_cases']:
        case('automatic:'+row['id'],f'(checkedForSourceKind {literal(row["kind"])} {literal(row["raw"])}).isSome','true' if row['expected'] else 'false')
    texts={}
    for profile in manifest['profiles']:
        source=ROOT/profile['positive_fixture']['path']
        assert binding(source)==profile['positive_fixture']
        raw=source.read_text();body=json.loads(raw)
        kind=profile['kind'];name=kind.replace('-','_');identity=body[profile['identity_field']]
        texts[kind]=(name,raw,identity)
        header+=f'\ndef text_{name} : String := {literal(raw)}\n'
        case(kind+':selected-kind',f'(checked text_{name}).map (fun output => kindName (bodyKind output))','some '+literal(kind))
        case(kind+':original-identity',f'(checked text_{name}).map CandidateTypedBodies.Body.identity','some '+literal(identity))
        for token in [p['kind'] for p in manifest['profiles']]:
            case(kind+':wrapper-kind:'+token,f'(checkedArtifact text_{name} {literal(token)} {literal(identity)}).isSome','true' if token==kind else 'false')
        case(kind+':wrapper-identity-mismatch',f'(checkedArtifact text_{name} {literal(kind)} "wrong-identity").isSome','false')
        for roots in [False,True]:
            case(kind+(':misaligned-root' if roots else ':misaligned-unused-record'),f'alignmentOf text_{name} {literal(kind)} {literal(identity)} {str(roots).lower()}','false')
    hostile=[
        ('unknown-kind','{"kind":"not-supported"}','none'),
        ('kind-case','{"kind":"Intent"}','none'),
        ('goal-kind-field','{"kind":"goal"}','none'),
        ('goal-version-only','{"schema_version":"cyberalchemy-lab-goal/v1"}','some "goal"'),
        ('goal-version-wrong','{"schema_version":"cyberalchemy-lab-goal/v2"}','none'),
        ('missing-discriminant','{}','none'),
        ('array','[]','none'),
        ('null','null','none'),
        ('duplicate-discriminant','{"kind":"intent","kind":"intent"}','none'),
        ('duplicate-unrelated','{"kind":"intent","x":1,"x":2}','none'),
        ('goal-version-and-kind','{"schema_version":"cyberalchemy-lab-goal/v1","kind":"goal"}','none'),
        ('supporting-decision-unimplemented','{"kind":"decision"}','none'),
    ]
    for identifier,text,expected in hostile:
        case('selector:'+identifier,f'(selected {literal(text)}).map kindName',expected)
    case('goal-tag-alone-is-not-a-body',f'(checked {literal(hostile[3][1])}).isSome','false')
    case('old-synthetic-full-entry-success','(CandidateNestedProvenance.RuntimeControls.result).toOption.isSome','true')
    case('typed-full-entry-refuses-synthetic-opaque-payloads',
         '(runTypedFull CandidateProfileEvidence.Controls.bootstrap CandidateNestedProvenance.RuntimeControls.limits CandidateEvidenceResources.Controls.numbers CandidateProfileEvidence.Controls.root CandidateNestedProvenance.GeneratedFixture.authorityRef CandidateNestedProvenance.RuntimeControls.inputs CandidateNestedProvenance.RuntimeControls.world CandidateNestedProvenance.RuntimeControls.claim).toOption.isSome','false')
    assert len(cases)==len({c['id'] for c in cases})
    code=header+'\n'+'\n'.join('#eval '+c['expression'] for c in cases)+'\nend RelationalSuccessor.CandidateBodyDispatch.RuntimeControls\n'
    (HERE/'DispatchControls.lean').write_text(code)
    index={'task':'N01','unit':HERE.name,'runtime_cases':cases,'schema_comparison_cases':len(fixture['input_cases']),
           'kind_count':7,'wrapper_kind_cases':49,'wrapper_identity_mismatch_cases':7,
           'unused_and_root_alignment_cases':14,'selector_boundary_cases':len(hostile),
           'identity_and_kind_cases':14,'goal_tag_insufficient_cases':1,'full_entry_boundary_cases':2,
           'prior_fixture_validation':binding(PRIOR/'fixture-validation.json'),'original_profile_manifest':binding(manifest_path),
           'generator':binding(Path(__file__)),'captured_context_is_synthetic':True,'independent_checker_run':False,
           'all_original_payload_roles_supported':False,'inherited_discharges':0,'authority_effect':'none'}
    save(HERE/'control-index.json',index)
    print('Generated',len(cases),'runtime observations.')

if __name__=='__main__': run()
