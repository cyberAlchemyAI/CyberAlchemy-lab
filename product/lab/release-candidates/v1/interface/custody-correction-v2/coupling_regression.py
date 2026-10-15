"""Preserve all predecessor coupling assertions against the successor loader."""
import ast
import importlib.util
import types
import unittest
from episode import *


def run(output):
    output=Path(output).resolve();require(output.is_relative_to(HERE) and not output.exists(),'fresh selected coupling adaptation output required');output.mkdir()
    # Parent witness helpers consume the successor loader/pins supplied by this host.
    path=HERE.parent/'coupling/episode.py';spec=importlib.util.spec_from_file_location('_R03_original_coupling_witnesses',path)
    helpers=importlib.util.module_from_spec(spec);spec.loader.exec_module(helpers)
    import episode as host
    for name in ['proposal_for','target','selected_cases','case_targets','carrier_for','frozen_kind_rejection']:setattr(host,name,getattr(helpers,name))
    original_path=HERE.parent/'coupling/test_coupling.py';raw=original_path.read_text();edits=[]
    for before in ["self.pins.mapping_sha256,self.pins.profile_sha256)","'0'*64,self.pins.profile_sha256)"]:
        after=before[:-1]+',self.pins.correction_profile_sha256)';count=raw.count(before);require(count==1,'original selected pin constructor anchor differs')
        raw=raw.replace(before,after);edits.append({'before':before,'after':after,'occurrences':count})
    require(sum(isinstance(n,ast.FunctionDef) and n.name.startswith('test_') for n in ast.walk(ast.parse(raw)))==35,'all original coupling assertions required')
    emit(output/'adaptation.json',{'original_source_binding':bind(original_path),'original_helper_binding':bind(path),
        'edits':edits,'assertions_changed':False,'tests':35,'authority_effect':'none'})
    (output/'adapted-tests.py').write_text(raw)
    module=types.ModuleType('_R03_successor_original_coupling_guards');module.__file__=str(output/'adapted-tests.py');sys.modules[module.__name__]=module
    exec(compile(raw,module.__file__,'exec'),module.__dict__)
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(module))
    print(json.dumps({'result':'PASS' if result.wasSuccessful() else 'FAIL','tests':result.testsRun,'failures':len(result.failures),
        'errors':len(result.errors),'assertions_changed':False,'authority_effect':'none'},sort_keys=True))
    return result.wasSuccessful()


if __name__=='__main__':raise SystemExit(0 if run(Path(sys.argv[1])) else 1)
