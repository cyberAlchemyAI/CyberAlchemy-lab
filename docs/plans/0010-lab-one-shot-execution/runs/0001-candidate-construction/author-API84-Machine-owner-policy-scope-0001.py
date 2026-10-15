"""Select the actual owner policy custodian for Machine Context generation."""
import ast
import json
from pathlib import Path
import shutil

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
OLD,API=BASE/'api-v83',BASE/'api-v84'


def replace(path,before,after):
    text=path.read_text();assert text.count(before)==1,(path,before)
    path.write_text(text.replace(before,after,1))


def main():
    assert not API.exists() and not (BASE/'lesson-host-composition-v34').exists()
    ignore=shutil.ignore_patterns('receipts','__pycache__','source-manifest.json','contract-profile.json')
    shutil.copytree(OLD,API,ignore=ignore)
    shutil.copytree(BASE/'lesson-host-composition-v33',BASE/'lesson-host-composition-v34',ignore=ignore)
    replace(BASE/'lesson-host-composition-v34/host.py','api-v83/service.py','api-v84/service.py')
    replace(API/'lesson_selection.py','lesson-host-composition-v33','lesson-host-composition-v34')
    (API/'machine_context_scope.py').write_text(
        '"""Select the private original-owner Machine Context scope composition."""\n'
        'import importlib.util,sys\nfrom pathlib import Path\n'
        'HERE=Path(__file__).resolve().parent\nPATH=HERE.parent/"machine-context-scope-v1"\n'
        'NAME="_cal_"+HERE.name.replace("-","_")+"_machine_context_scope_v1"\n'
        'if NAME not in sys.modules:\n'
        '    spec=importlib.util.spec_from_file_location(NAME,PATH/"__init__.py",submodule_search_locations=[str(PATH)])\n'
        '    module=importlib.util.module_from_spec(spec);sys.modules[NAME]=module;spec.loader.exec_module(module)\n'
        'selected=__import__(NAME+".generation",fromlist=["generate"])\n'
        'assert Path(selected.__file__).resolve()==PATH/"generation.py"\n'
        'generate=selected.generate\n')
    path=API/'custody_context_sessions.py'
    replace(path,'        bodies,refs,delivery,proof,lesson=D.generate(self.source,self.bridge,message,raw,MAPPING_PIN,self.schemas)',
        '        if type(self) is MachineContextSessions:\n'
        '            from .machine_context_scope import generate\n'
        '            bodies,refs,delivery,proof,lesson=generate(self,message,raw,MAPPING_PIN,self.schemas)\n'
        '        else:bodies,refs,delivery,proof,lesson=D.generate(self.source,self.bridge,message,raw,MAPPING_PIN,self.schemas)')
    replace(API/'service.py',"'lesson_assessment.py','lesson_application.py')",
            "'lesson_assessment.py','lesson_application.py','machine_context_scope.py')")
    for path in API.glob('*.py'):ast.parse(path.read_text())
    print(json.dumps({'result':'AUTHORED','authored_handlers':23,'remaining_handlers':11,
                      'runtime_qualified':False,'authority_effect':'none'}),flush=True)


if __name__=='__main__':main()
