"""Reuse the bound compiler read-only for the exact complete Decision schema."""
from pathlib import Path
import hashlib, importlib.util, json, re

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[9]
COMPILER=HERE.parent/'K02-typed-payload-bodies/generate_profiles.py'
def binding(path): return {'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def compile_decision():
    spec=importlib.util.spec_from_file_location('bound_complete_schema_compiler',COMPILER)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.PRIOR=HERE
    text,trace,roots=module.compile_profiles()
    assert len(roots)==1 and roots[0][0]['kind']=='decision'
    start=text.index('\ninductive Kind where')
    end=text.index('\ntheorem decision_complete_record_exact')
    text=text[:start]+text[end:]
    text=text.replace('namespace RelationalSuccessor.CandidateTypedBodies',
                      'namespace RelationalSuccessor.CandidateSupportingSources\nopen CandidateTypedBodies')
    text=text.replace('end RelationalSuccessor.CandidateTypedBodies',
                      'end RelationalSuccessor.CandidateSupportingSources')
    return text,trace
def run():
    compiler=binding(COMPILER);text,trace=compile_decision()
    assert binding(COMPILER)==compiler
    (HERE/'DecisionBodyProfiles.lean').write_text(text)
    report={'task':'N01','unit':HERE.name,'result':'complete-decision-schema-generation-pass',
            'driver':binding(Path(__file__)),'bound_prior_compiler':compiler,
            'profile_manifest':binding(HERE/'profile-manifest.json'),
            'formalization':binding(HERE/'FORMALIZATION.md'),
            'generated_source':binding(HERE/'DecisionBodyProfiles.lean'),
            'record_type_count':len(re.findall(r'^structure ',text,re.M)),
            'complete_record_field_count':len(re.findall(r'^  \w+ : ',text,re.M)),
            'active_assertion_nodes':len(trace),'assertion_trace':trace,
            'all_declared_fields_required_verified':True,'unsupported_assertions_ignored':False,
            'general_schema_compiler_correspondence_proved':False,'inherited_discharges':0,'authority_effect':'none'}
    assert report['record_type_count']==3 and report['complete_record_field_count']==23
    (HERE/'generation-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print({k:report[k] for k in ['result','record_type_count','complete_record_field_count','active_assertion_nodes']})
if __name__=='__main__':run()
