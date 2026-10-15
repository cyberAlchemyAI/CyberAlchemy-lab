import hashlib,importlib.metadata,importlib.util,json,sys
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');HERE=Path(__file__).resolve().parent;I=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
sys.path.append(str(I/'deps'))
from jsonschema import Draft202012Validator,FormatChecker
import jsonschema._format
def binding(path):
 raw=path.read_bytes();return {'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest(),'size_bytes':len(raw)}
selection=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json';assert binding(selection)['sha256']=='2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'
checker=FormatChecker();registered='date-time' in checker.checkers
original_accepts=Draft202012Validator({'type':'string','format':'date-time'},format_checker=checker).is_valid('not-a-date')
assert registered is False and original_accepts is True and importlib.util.find_spec('rfc3339_validator') is None
paths={Path(module.__file__).resolve() for module in list(sys.modules.values()) if isinstance(getattr(module,'__file__',None),str) and Path(module.__file__).is_relative_to(I/'deps')}
paths.update([I/'bin/python',I/'lib/abi/ld-linux-x86-64.so.2',I/'deps/jsonschema-4.23.0.dist-info/METADATA'])
report={'schema_version':'lab-T03-margin-exact-date-time-dependency-observation/v1-candidate','authority_effect':'none','task_complete':False,'jsonschema_version':importlib.metadata.version('jsonschema'),'dependency_selection':binding(selection),'date_time_checker_registered':registered,'optional_rfc3339_validator_available':False,'original_format_annotation_alone_accepts_inert_not_a_date':original_accepts,'global_format_registry_or_library_bytes_changed':False,'actual_Lab_constructor_native_domain_Service_Session_or_lease':False,'loaded_dependency_origins':[binding(path) for path in sorted(paths)],'claim_ceiling':'This exact installed FormatChecker capability and own inert policy fixture only; not whole original contract qualification or any checker replacement.'}
(HERE/'date-time-dependency-observation-0001.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n');print(json.dumps({'result':'CONFIRMED-policy-only','loaded_dependency_origins':len(paths),'output_sha256':hashlib.sha256((HERE/'date-time-dependency-observation-0001.json').read_bytes()).hexdigest()}))
