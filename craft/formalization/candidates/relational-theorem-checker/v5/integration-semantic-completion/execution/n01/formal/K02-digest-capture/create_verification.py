"""Create exact source capture and fresh isolated compilation/replay protocol."""
from pathlib import Path
import hashlib,json,re,os
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[9]
def b(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
modules=['DigestCapture','DigestCapturePolicies','DigestCaptureOutcomes','DigestCaptureCatalog','DigestCaptureControls','DigestCaptureRuntimeControls']
for stem in modules:
 p=HERE/f'{stem}.lean';s=p.read_text();names=re.findall(r'^theorem (\w+)',s,re.M)
 if names and '#print axioms' not in s:
  marker='end RelationalSuccessor.CandidateDigestCapture.Controls' if stem=='DigestCaptureControls' else 'end RelationalSuccessor.CandidateDigestCapture'
  s=s.replace(marker,'\n'.join('#print axioms '+name for name in names)+'\n'+marker);p.write_text(s)
base=HERE.parent/'K02-binding-bytes';digest=HERE.parent/'K02-digest'
vb=json.loads((base/'verification.json').read_text());vd=json.loads((digest/'verification.json').read_text())
deps=[]
for item in vb['sources']+vd['sources']:
 p=ROOT/item['path']
 if p.stem=='DigestRuntimeControls':continue
 if p not in deps:deps.append(p)
assert len(deps)==64
s=(base/'verify_candidate.py').read_text()
a=s.index('    dependencies =');z=s.index('    sources = dependencies + new_sources')
s=s[:a]+"    dependencies = [(HERE.parent/name).resolve() for name in "+repr([os.path.relpath(p,HERE.parent) for p in deps])+']\n    new_sources = [HERE/name for name in '+repr([x+'.lean' for x in modules])+']\n'+s[z:]
a=s.index('    # Match kernel-input UInt8 literals');z=s.index('    records = []',a)
s=s[:a]+'''    controls=json.loads((HERE/'control-index.json').read_text())
    literal_source=(HERE.parent/'K02-binding-bytes/OriginalByteControls.lean').read_text()
    fixture_source=(HERE/'DigestCaptureControls.lean').read_text()
    runtime_source=(HERE/'DigestCaptureRuntimeControls.lean').read_text()
    for row in controls['original_fixtures']:
        name=row['kind']
        match=re.search(r'^def '+name+r'Bytes : CandidateJsonBytes.Bytes := \\[(.*?)\\]$',literal_source,re.M)
        assert match
        data=bytes(int(x) for x in match.group(1).split(',') if x.strip())
        assert data==(ROOT/row['original_bytes']['path']).read_bytes()
        assert len(data)==row['byte_count'] and hashlib.sha256(data).hexdigest()==row['computed_sha256']
        expected='def '+name+'Capture : CandidateBindingCapture.Envelope := ⟨'+name+'Bytes,'+str(row['byte_count'])+',profile.ref,'+json.dumps(row['computed_sha256'])+'⟩'
        assert expected in fixture_source
    actual_expressions=re.findall(r'^#eval (.*)$',runtime_source,re.M)
    assert actual_expressions==[row['expression'] for row in controls['runtime_cases']]

'''+s[z:]
marker='            records.append(record)'
s=s.replace(marker,'''            if source.stem=='DigestCaptureRuntimeControls':
                expected_runtime=[row['expected_json'] for row in controls['runtime_cases']]
                assert result.stdout.strip().splitlines()==expected_runtime, source.stem
                record['runtime_composed_cases']=len(controls['runtime_cases'])
'''+marker)
a=s.index('    report = {');z=s.index('    (HERE / "verification.json").write_text',a)
s=s[:a]+'''    report={"task":"N01","unit":"K02-digest-capture","result":"candidate-fragment-pass",
      "method":"fresh isolated pinned Lean compilation and separate fresh same-kernel replay; exact computed-fixture byte and runtime outcome comparisons",
      "toolchain_lock":binding(lock_path),"compiler":binding(lean),"kernel_library":binding(kernel),
      "driver":binding(Path(__file__)),"context_pack":binding(HERE/'context-pack.json'),"source_capture":binding(capture_path),
      "sources":captured,"records":records,"new_declarations":declarations,"new_declaration_count":len(declarations),
      "new_general_declarations":49,"new_worked_control_declarations":12,"allowed_axioms":sorted(allowed),
      "control_index":binding(HERE/'control-index.json'),"runtime_composed_cases":len(controls['runtime_cases']),
      "digest_capture_pipeline_composed":True,"digest_capture_exactness_proved":True,
      "digest_capture_all_input_catalog_exactness_proved":True,"digest_capture_envelope_order_retention_proved":True,
      "digest_capture_direct_refusal_meanings_proved":True,"capture_parse_digest_policy_adapters_implemented":True,
      "capture_remaining_policies_unchanged_proved":True,"capture_conditional_authentication_bridge_proved":True,
      "configured_catalog_resource_guards_proved":True,"whole_original_fixture_runtime_composition_checked":True,
      "original_positive_kernel_hash_controls":False,"profile_and_owner_review_roots_synthetic":True,
      "claim_scope":"Exact candidate SHA-256/profile/resource and original bytes-to-binding/frame capture composition, lossless ordered all-input records and roots, existing structural catalog meaning, explicit aggregate/count budgets and independent direct refusal meanings. Parse/digest policy adapter implemented; authentic profile ownership, Schema and review remain separate premises.",
      "authenticated_digest_profile_selection_proved":False,"authenticated_capture_proved":False,
      "authenticated_full_source_policy_realization_proved":False,"JSON_schema_semantics_interpreter_proved":False,
      "whole_K02_source_refinement_proved":False,"raw_source_refinement_proved":False,"independent_checker_run":False,
      "external_standard_translation_reviewed":False,"collision_freedom_proved":False,
      "supported_resource_envelope_measured":False,"public_outcome_classification_implemented":False,
      "inherited_discharges":0,"N01_accepted":False,"authority_effect":"none"}
    assert len(declarations)==61
'''+s[z:]
s=s.replace('Rebuild and replay the K02 original byte-record/capture/catalog candidate; never accept or discharge it.','Rebuild and replay digest-checked byte capture/catalog composition; never accept or discharge it.')
(HERE/'verify_candidate.py').write_text(s)
s=(base/'audit_imports.py').read_text().replace('K02 byte-record/capture/catalog','K02 digest-capture composition').replace('K02-binding-bytes','K02-digest-capture');(HERE/'audit_imports.py').write_text(s)
selected=[HERE/'FORMALIZATION.md',base/'verification.json',digest/'verification.json',base/'CaptureBytes.lean',base/'CaptureBytesCatalog.lean',digest/'DigestProfile.lean']
(HERE/'context-pack.json').write_text(json.dumps({'task':'N01','unit':'K02-digest-capture','selected_sources':[b(p) for p in selected],'full_plan_scope_retained':True,'K04_pending':True,'authority_effect':'none'},indent=2)+'\n')
controls=json.loads((HERE/'control-index.json').read_text())
capture={'task':'N01','unit':'K02-digest-capture','independent_formalization':b(HERE/'FORMALIZATION.md'),
 'original_fixtures':controls['original_fixtures'],'control_index':b(HERE/'control-index.json'),
 'control_generator':b(HERE/'generate_controls.py'),'byte_preparation_evidence':b(base/'verification.json'),
 'digest_computation_evidence':b(digest/'verification.json'),'profile_and_owner_review_roots_synthetic':True,
 'original_positive_kernel_hash_controls':False,'authenticated_capture_proved':False,'inherited_discharges':0,'authority_effect':'none'}
(HERE/'source-capture.json').write_text(json.dumps(capture,indent=2)+'\n')
print({'fresh_dependencies':len(deps),'new_modules':len(modules),'new_declarations':61})
