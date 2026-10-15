"""Create the fresh verifier from the established byte-candidate evidence protocol."""
from pathlib import Path
import hashlib,json,re,urllib.request
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[9]
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
# Preserve exact external reference bytes; never execute content from the standard.
standard=HERE/'standard/NIST.FIPS.180-4.2015.pdf';standard.parent.mkdir(exist_ok=True)
if not standard.exists():
 with urllib.request.urlopen('https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf',timeout=30) as response:standard.write_bytes(response.read())
assert standard.read_bytes().startswith(b'%PDF-')
modules=['DigestMeaning','DigestEvaluator','DigestRefinement','DigestProfile','DigestControls','DigestRuntimeControls']
for stem in modules:
 p=HERE/f'{stem}.lean';s=p.read_text();names=re.findall(r'^theorem (\w+)',s,re.M)
 if '#print axioms' not in s and names:
  marker='end RelationalSuccessor.CandidateDigest.Controls' if stem=='DigestControls' else 'end RelationalSuccessor.CandidateDigest'
  s=s.replace(marker,'\n'.join('#print axioms '+name for name in names)+'\n'+marker)
  p.write_text(s)
original=HERE.parent/'K02-binding-bytes/verify_candidate.py'
s=original.read_text()
a=s.index('    dependencies =');b=s.index('    sources = dependencies + new_sources')
s=s[:a]+"    dependencies = [BASE/'v3/e00/ExpressionSemantics.lean', SUCCESSOR/'SharedSemantics.lean']\n    new_sources = [HERE/name for name in "+repr([x+'.lean' for x in modules])+']\n'+s[b:]
a=s.index('    # Match kernel-input UInt8 literals');b=s.index('    records = []',a)
s=s[:a]+'''    controls = json.loads((HERE/'runtime-control-index.json').read_text())
    runtime_source = (HERE/'DigestRuntimeControls.lean').read_text()
    for i,case in enumerate(controls['cases']):
        match=re.search(r'^def bytes'+str(i)+r' : Bytes := \\[(.*?)\\]$',runtime_source,re.M)
        assert match
        data=bytes(int(x) for x in match.group(1).split(',') if x.strip())
        assert data.hex()==case['input_hex'] and len(data)==case['byte_length']
        assert hashlib.sha256(data).hexdigest()==case['expected_sha256']
        if case.get('original_bytes'):assert data==(ROOT/case['original_bytes']['path']).read_bytes()

'''+s[b:]
marker='            records.append(record)'
insert='''            if source.stem=='DigestRuntimeControls':
                lines=result.stdout.strip().splitlines()
                expected_runtime=[json.dumps(c['expected_sha256']) for c in controls['cases']]+[c['expected'] for c in controls['refusal_cases']]
                assert lines==expected_runtime, (source.stem,len(lines),len(expected_runtime))
                record['runtime_digest_cases']=len(controls['cases'])
                record['runtime_submitted_capture_cases']=len(controls['refusal_cases'])
'''
s=s.replace(marker,insert+marker)
a=s.index('    report = {');b=s.index('    (HERE / "verification.json").write_text',a)
report='''    report = {"task":"N01","unit":"K02-digest","result":"candidate-fragment-pass",
      "method":"fresh pinned Lean compilation and separate fresh same-kernel replay; differential runtime cases against Python hashlib",
      "toolchain_lock":binding(lock_path),"compiler":binding(lean),"kernel_library":binding(kernel),
      "driver":binding(Path(__file__)),"context_pack":binding(HERE/'context-pack.json'),"source_capture":binding(capture_path),
      "sources":captured,"records":records,"new_declarations":declarations,"new_declaration_count":len(declarations),
      "new_general_declarations":48,"new_worked_control_declarations":13,"allowed_axioms":sorted(allowed),
      "digest_algorithm_realized":True,"digest_independent_meaning_exactness_proved":True,
      "digest_algorithm_domain_totality_proved":True,"digest_hex_representation_proved":True,
      "digest_full_profile_ref_equality_proved":True,"digest_outcome_exactness_proved":True,
      "runtime_digest_cases":len(controls['cases']),"runtime_submitted_capture_cases":len(controls['refusal_cases']),
      "runtime_control_index":binding(HERE/'runtime-control-index.json'),
      "claim_scope":"SHA-256 byte-domain padding, ordered lossless block partition, 64-word schedule, 64-round compression, ordered message chain and exact lowercase full digest. Complete submitted RevisionRef equality and budget/profile/digest outcomes. External standard translation and authentic profile selection remain pending.",
      "digest_capture_pipeline_composed":False,"authenticated_digest_profile_selection_proved":False,
      "authenticated_capture_proved":False,"whole_K02_source_refinement_proved":False,
      "raw_source_refinement_proved":False,"independent_checker_run":False,
      "external_standard_translation_reviewed":False,"NIST_FIPS_validated":False,
      "collision_freedom_proved":False,"supported_resource_envelope_measured":False,
      "inherited_discharges":0,"N01_accepted":False,"authority_effect":"none"}
    assert len(declarations)==61
'''
s=s[:a]+report+s[b:]
s=s.replace('Rebuild and replay the K02 original byte-record/capture/catalog candidate; never accept or discharge it.','Rebuild and replay the exact-byte digest candidate; never accept or discharge it.')
(HERE/'verify_candidate.py').write_text(s)
s=(HERE.parent/'K02-binding-bytes/audit_imports.py').read_text().replace('K02 byte-record/capture/catalog','K02 digest candidate').replace('K02-binding-bytes','K02-digest')
(HERE/'audit_imports.py').write_text(s)
selected=[HERE/'FORMALIZATION.md',HERE.parents[3]/'SharedSemantics.lean',HERE.parent/'K02-binding-capture/CapturePolicies.lean',HERE.parent/'K02-binding-bytes/NEXT-IMPLEMENTATION.md']
context={'task':'N01','unit':'K02-digest','selected_sources':[bind(p) for p in selected],'full_plan_scope_retained':True,'K04_pending':True,'authority_effect':'none'}
(HERE/'context-pack.json').write_text(json.dumps(context,indent=2)+'\n')
capture={'task':'N01','unit':'K02-digest','independent_formalization':bind(HERE/'FORMALIZATION.md'),
 'standard':{'content':bind(standard),'url':'https://nvlpubs.nist.gov/nistpubs/fips/nist.fips.180-4.pdf','edition':'August 2015','sections':['3.2','4.1.2','4.2.2','5.1.1','5.2.1','5.3.3','6.2.2']},
 'runtime_controls':bind(HERE/'runtime-control-index.json'),'runtime_control_generator':bind(HERE/'generate_runtime_controls.py'),
 'profile_reference_is_synthetic':True,'authenticated_expected_profile':False,'external_standard_translation_reviewed':False,
 'inherited_discharges':0,'authority_effect':'none'}
(HERE/'source-capture.json').write_text(json.dumps(capture,indent=2)+'\n')
print('Fresh digest verifier and exact source capture created')
