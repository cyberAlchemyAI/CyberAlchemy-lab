"""Select the exact resolution implementation from the actual private policy."""
import importlib.util,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
def implementation(policy):
    version='v3' if policy['schema_version']=='lab-local-integrated-challenge-resolution-policy/v2-candidate' else 'v1'
    path=HERE.parent/('challenge-resolution-'+version)
    name='_cal_'+HERE.name.replace('-','_')+'_challenge_resolution_'+version
    if name not in sys.modules:
        spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)])
        module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    selected=__import__(name+'.preparation',fromlist=['ChallengeResolution'])
    assert Path(selected.__file__).resolve()==path/'preparation.py'
    return selected.ChallengeResolution,selected.RuleFailure
