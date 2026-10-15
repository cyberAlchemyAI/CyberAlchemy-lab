"""Generate only the two pinned K04 source profiles with the verified compiler."""
from pathlib import Path
import hashlib, importlib.util, json, re

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'authority/artifact-types').is_dir())
COMPILER = HERE.parent/'K02-typed-payload-bodies/generate_profiles.py'
def binding(path):
    return {'path':str(path.relative_to(ROOT)), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def compile_profiles():
    spec=importlib.util.spec_from_file_location('k04_pinned_schema_compiler', COMPILER)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.PRIOR=HERE
    text,trace,roots=module.compile_profiles()
    assert [row['kind'] for row,_,_ in roots]==['lesson-application','operational-lesson']
    text=text.replace('namespace RelationalSuccessor.CandidateTypedBodies',
                      'namespace RelationalSuccessor.CandidateLessonSource\nopen CandidateTypedBodies')
    text=text.replace('end RelationalSuccessor.CandidateTypedBodies',
                      'end RelationalSuccessor.CandidateLessonSource')
    return text,trace
if __name__=='__main__':
    compiler=binding(COMPILER)
    text,trace=compile_profiles()
    assert binding(COMPILER)==compiler
    (HERE/'LessonBodyProfiles.lean').write_text(text)
    report={'result':'fixed-complete-k04-schema-generation-pass',
        'generator':binding(Path(__file__)), 'compiler':compiler,
        'manifest':binding(HERE/'profile-manifest.json'),
        'generated_source':binding(HERE/'LessonBodyProfiles.lean'),
        'record_type_count':len(re.findall(r'^structure ',text,re.M)),
        'complete_record_field_count':len(re.findall(r'^  \w+ : ',text,re.M)),
        'active_assertion_nodes':len(trace),'assertion_trace':trace,
        'unsupported_assertions_ignored':False,
        'general_schema_compiler_correspondence_proved':False,
        'inherited_discharges':0,'authority_effect':'none'}
    (HERE/'generation-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print({k:report[k] for k in ['result','record_type_count','complete_record_field_count','active_assertion_nodes']})
