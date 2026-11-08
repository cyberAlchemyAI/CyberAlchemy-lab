"""Separately selected public export closure. All outputs are owned fixtures."""
import io,json,zipfile
from dataclasses import dataclass
from lab_contracts.codec import Refusal,canonical,closed,need,sha
from lab_selectors.anchors import AnchoredReader,relative
from environment.requirements import inspect_execution_requirements,ORIGINAL_SELECTION_SHA
from environment.origins import wheel_inventory
from environment.elf import inspect_elf,compare_abi_versions

SENTINEL=b'Lab selected regular file: bytecode cache directories are disabled.\n'
MAX_TOTAL=256*1024*1024
MAX_FILES=4096

def row(raw,mode):return {'sha256':sha(raw),'size_bytes':len(raw),'mode':mode}

def installed_rows(value):
    result={r['destination']:{k:r[k] for k in ('sha256','size_bytes','mode')} for r in value['inputs']}
    result.update(value['wheel_members'])
    result['lib/abi/ld-linux-x86-64.so.2']['mode']=0o755
    result['bytecode-disabled']=row(SENTINEL,0o644)
    return result

@dataclass
class Payload:
    files:dict
    manifest:dict
    _recheck:object
    def recheck(self):self._recheck()
    def verify(self):
        need(type(self.files)is dict and 1<=len(self.files)<=MAX_FILES,'PACKAGE_COUNT')
        need(set(self.files)==set(self.manifest['members']),'PACKAGE_COVERAGE')
        total=0
        for name,raw in self.files.items():
            parts=relative(name);need(len(name)<=4096 and len(parts)<=256,'PACKAGE_PATH_BOUND')
            need(type(raw)is bytes and len(raw)<=64*1024*1024,'PACKAGE_BYTES');total+=len(raw)
            expected=self.manifest['members'][name]
            need(row(raw,expected['mode'])==expected,'PACKAGE_CONTENT')
            need(expected['mode'] in (0o600,0o644,0o755),'PACKAGE_MODE')
        need(total<=MAX_TOTAL,'PACKAGE_TOTAL')
        return canonical(self.manifest)

def prepare(reader,policy_raw,expected_policy_sha256,original_raw,prior_raw,*,repository):
    """Policy SHA is supplied independently before reading it; no actual mode.

    Original public classification is necessary but not export authorization.
    Policy selects every exported byte/mode and independently maps all720 reads.
    Proof rows and original locators remain outside the public payload manifest.
    """
    try:
        need(type(reader)is AnchoredReader and type(policy_raw)is bytes and len(policy_raw)<=2*1024*1024,'PACKAGE_POLICY_BOUND')
        need(sha(policy_raw)==expected_policy_sha256,'PACKAGE_POLICY_PIN')
        from lab_contracts.codec import parse
        policy=parse(policy_raw,max_bytes=2*1024*1024)
        closed(policy,('schema_version','posture','purpose','original_selection_sha256','reads','exports','generated','authority_effect'))
        need(policy['schema_version']=='lab-public-package-policy/v1' and policy['posture']=='owned-fixture'
             and policy['purpose']=='offline-public-dependency-installation' and policy['authority_effect']=='none','PACKAGE_EXPORT_PERMISSION')
        need(policy['original_selection_sha256']==ORIGINAL_SELECTION_SHA,'PACKAGE_ORIGINAL')
        value=inspect_execution_requirements(original_raw,ORIGINAL_SELECTION_SHA,prior_raw=prior_raw,repository=repository)['original_value']
        expected=installed_rows(value)
        need(policy['exports']==expected and policy['generated']==['payload-manifest.json','bytecode-disabled'],'PACKAGE_EXPORT_COVERAGE')
        reads=policy['reads'];need(type(reads)is list and len(reads)==len(value['inputs'])==720,'PACKAGE_READ_COVERAGE')
        for selected,original in zip(reads,value['inputs']):
            closed(selected,('destination','binding'));b=selected['binding']
            closed(b,('kind','root_id','relative_path','sha256','size_bytes'))
            need(b['kind']=='public-package' and selected['destination']==original['destination']
                and (b['sha256'],b['size_bytes'])==(original['sha256'],original['size_bytes']),'PACKAGE_READ_SELECTION')
        need(len({(r['binding']['root_id'],r['binding']['relative_path']) for r in reads})==720,'PACKAGE_READ_ALIAS')
        files={};expanded={}
        for selected,original in zip(reads,value['inputs']):
            raw=reader.read(selected['binding'],max_bytes=64*1024*1024)
            name=selected['destination'];files[name]=raw
            if original['kind']=='wheel':
                members=wheel_inventory(raw)
                need(not set(members)&set(expanded),'PACKAGE_ARCHIVE_COLLISION');expanded.update(members)
                with zipfile.ZipFile(io.BytesIO(raw)) as z:
                    for entry in z.infolist():
                        if not entry.is_dir():files['deps/'+entry.filename]=z.read(entry)
        need(expanded==value['wheel_members'],'PACKAGE_ARCHIVE_COVERAGE')
        files['bytecode-disabled']=SENTINEL
        observed={name:inspect_elf(raw,sha(raw)) for name,raw in files.items() if raw.startswith(b'\x7fELF')}
        need(set(observed)==set(value['elf_graph']),'PACKAGE_ELF_COVERAGE')
        for name,obs in observed.items():
            declared=value['elf_graph'][name]
            need(sorted(obs['needed'])==declared['needed'] and
                 (obs['interpreter'].rsplit('/',1)[-1] if obs['interpreter'] else None)==declared['interpreter'],'PACKAGE_ELF_DECLARATION')
            compare_abi_versions(obs,{n:observed['lib/abi/'+n] for n in obs['needed']})
        manifest={'schema_version':'lab-public-prebuilt-payload/v1','construction':'exact-prebuilt',
            'original_selection_sha256':ORIGINAL_SELECTION_SHA,'public_policy_sha256':expected_policy_sha256,
            'input_occurrences':720,'wheel_members':len(expanded),'members':expected,
            'source_rebuild_reproduced':False,'authority_effect':'none'}
        def recheck():
            need(sha(policy_raw)==expected_policy_sha256,'PACKAGE_POLICY_DRIFT')
            for selected in reads:reader.read(selected['binding'],max_bytes=64*1024*1024)
        result=Payload(files,manifest,recheck);result.verify();recheck();return result
    except Exception:raise Refusal('PUBLIC_PACKAGE_REFUSED') from None
