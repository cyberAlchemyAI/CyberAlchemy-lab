"""Own diagnostic margin inputs for the current legacy fixture lifecycle.

No empirical load qualification is claimed. The selected production adapter
checks the actual source, installed dependencies, Session and clocks again at
the effect boundary.
"""
import hashlib
import importlib
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import platform
import stat
import sys
import tempfile
import uuid

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[4]
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v73-t15-learning-selector-0001'
INSTALL = Path('/home/vlad_/.local/share/cyberalchemy-lab/native-install/t22-0001')
SELECTION = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json'
COMPOSITION = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T03/observed-margin-adapter-0003/postimages/composition.py'
SOFTWARE = HERE / 'research-native-margin-software-selection-0001.json'
INSTRUMENTATION = HERE / 'research-native-margin-instrumentation.json'
LOCAL_ENV = HERE / 'research-native-local-source-environment.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def binding(path):
    return {'path':path.relative_to(ROOT).as_posix(), 'sha256':sha(path.read_bytes())}


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True)+'\n').encode()


def public_inputs(margin):
    selected=json.loads((API/'source-manifest.json').read_bytes())
    rows={row['path']:row for row in selected['files']}
    names=[(API/(name+'.py')).relative_to(ROOT).as_posix() for name in margin.MODULES]
    names.extend([(API/'observed-margin-policy.schema.json').relative_to(ROOT).as_posix(),
        'product/lab/release-candidates/v1/interface/lesson-assessment-v4-t03-independent-effect-0001/preparation.py'])
    if any(name not in rows or sha((ROOT/name).read_bytes())!=rows[name]['sha256'] for name in names):
        raise ValueError('closed current margin software selection differs')
    software={'schema_version':'lab-T03-observed-margin-software/v1-candidate',
              'authority_effect':'none','files':[rows[name] for name in sorted(set(names))]}
    specification={'schema_version':'lab-margin-instrumentation-observation/v1-candidate',
                   'authority_effect':'none','profile_hook':None,'trace_hook':None,
                   'monitoring_tools':{str(n):None for n in range(6)}}
    for path,value in ((SOFTWARE,software),(INSTRUMENTATION,specification)):
        raw=encoded(value)
        if path.exists() and path.read_bytes()!=raw:
            raise ValueError('existing selected margin input changed')
        if not path.exists():path.write_bytes(raw)
    return binding(SOFTWARE),binding(INSTRUMENTATION)


def local_environment(package):
    current=importlib.import_module(package+'.current_legacy_context_sessions')
    source=current.D.reader.adapter.source
    signed=Path(source.HERE)/'source-manifest.json'
    environment={'python':platform.python_version(),
                 'jsonschema':importlib.metadata.version('jsonschema'),
                 'cryptography':importlib.metadata.version('cryptography')}
    modules={}
    for name in ('jsonschema','cryptography'):
        imported=importlib.import_module(name);path=Path(imported.__file__)
        modules[name]={'version':environment[name],'path':str(path),'sha256':sha(path.read_bytes())}
    executable=Path(sys.executable).resolve(strict=True)
    value={'schema_version':'lab-T03-local-source-environment/v1-candidate',
           'authority_effect':'none','source_manifest_binding':binding(signed),
           'interpreter_binding':{'path':str(executable),'sha256':sha(executable.read_bytes())},
           'environment':environment,'modules':modules}
    raw=encoded(value)
    if LOCAL_ENV.exists() and LOCAL_ENV.read_bytes()!=raw:
        raise ValueError('selected local source environment changed')
    if not LOCAL_ENV.exists():LOCAL_ENV.write_bytes(raw)
    return binding(LOCAL_ENV)


def prepare(package,source_sha,profile_sha,period_path):
    installed=Path(sys.executable)==INSTALL/'bin/python'
    system=Path(sys.executable)==Path('/usr/bin/python3')
    if not (installed or system):raise ValueError('selected current Python is required')
    margin=importlib.import_module(package+'.observed_margin')
    software,instrumentation=public_inputs(margin)
    dependency=binding(SELECTION) if installed else local_environment(package)
    config={'schema_version':'lab-protected-observed-margin-runtime/v1-candidate',
            'authority_effect':'none','mode':'diagnostic-measurement',
            'api_directory':API.relative_to(ROOT).as_posix(),
            'api_source_binding':binding(API/'source-manifest.json'),
            'profile_binding':binding(API/'contract-profile.json'),
            'software_binding':software,'period_binding':binding(period_path),
            'dependency_selection_binding':dependency,
            'dependency_installation':str(INSTALL) if installed else 'system-current-source-diagnostic',
            'instrumentation_binding':instrumentation,'policy_binding':None,'load_binding':None}
    if config['api_source_binding']['sha256']!=source_sha or config['profile_binding']['sha256']!=profile_sha:
        raise ValueError('selected current API source/profile differs')
    root=Path(tempfile.mkdtemp(prefix='cal-T03-margin-',dir='/tmp'))
    root.chmod(0o700)
    name='configuration.json';raw=encoded(config)
    fd=os.open(root/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as output:output.write(raw)
    identity=os.stat(root)
    control={'root':str(root),'identity':(identity.st_dev,identity.st_ino,identity.st_uid,stat.S_IMODE(identity.st_mode)),
             'configuration_binding':{'path':name,'sha256':sha(raw)}}
    return control


def compose(package,host,parent,attachment,control):
    margin=importlib.import_module(package+'.observed_margin')
    modules={name:importlib.import_module(package+'.'+name) for name in margin.MODULES}
    helpers=[]
    for name in ('margin_capture','margin_kernel','margin_seal','observed_margin'):
        module=modules[name];path=API/(name+'.py');raw=path.read_bytes()
        helpers.append((name,module,str(path),sha(raw),raw))
    name='_cal_t03_margin_composition_'+uuid.uuid4().hex
    spec=importlib.util.spec_from_file_location(name,COMPOSITION)
    composition=importlib.util.module_from_spec(spec);sys.modules[name]=composition;spec.loader.exec_module(composition)
    return composition.compose(host,parent,modules,attachment,
        control_root=Path(control['root']),root_identity=control['identity'],
        selection_binding=control['configuration_binding'],helper_capture=tuple(helpers))
