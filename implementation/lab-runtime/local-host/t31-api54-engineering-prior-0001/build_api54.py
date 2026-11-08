"""No-replace API54 recut for exact engineering design and prior-output input."""
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-integration-v53-t31-schema-material-0001'
NEW = BASE / 'api-integration-v54-t31-engineering-prior-0001'
OLD_ADAPTER = ROOT / 'implementation/lab-runtime/local-host/t31-api53-schema-material-bootstrap-0001/bootstrap.py'
NEW_ADAPTER = ROOT / 'implementation/lab-runtime/local-host/t31-api54-engineering-bootstrap-0001/bootstrap.py'
OLD_SOURCE_SHA = '872df282f400a8ee814d1fdb7751aa5074250b3b073c4c63cf16567775ab436c'
OLD_PROFILE_SHA = 'fb8741bc5148f9002281dfd3a251d6b20706752a61efaaadf89e22feccf8213e'
KERNEL = BASE / 'workflow-transition-v2-t31'
ENGINEERING = ROOT / 'docs/proposals/0007-lab-integrated-schema-package/workflows/engineering.json'
PRIOR = Path(__file__).with_name('prior_contract.py')
CLAIM = ('Selected engineering template and exact prior design output as produced-current '
         'local input; no signed-Source or canonical admission for that output, no native '
         'transition observation, owner outcome, or original transition count increment.')


def sha(raw): return hashlib.sha256(raw).hexdigest()
def raw(path): return Path(path).read_bytes()
def row(path): return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(raw(path))}
def exact_replace(value, before, after, n=1):
    if value.count(before) != n: raise ValueError('recut anchor count differs: ' + before[:80])
    return value.replace(before, after)
def save(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')


def main():
    if sha(raw(OLD / 'source-manifest.json')) != OLD_SOURCE_SHA or sha(raw(OLD / 'contract-profile.json')) != OLD_PROFILE_SHA:
        raise ValueError('API53 exact input changed')
    if NEW.exists() or NEW_ADAPTER.exists(): raise ValueError('successor already exists')
    manifest = json.loads(raw(OLD / 'source-manifest.json'))
    profile = json.loads(raw(OLD / 'contract-profile.json'))
    old_prefix = OLD.relative_to(ROOT).as_posix() + '/'
    new_prefix = NEW.relative_to(ROOT).as_posix() + '/'
    own = [r for r in manifest['files'] if r['path'].startswith(old_prefix)]
    if len(manifest['files']) != 210 or len(own) != 201 or len(profile['files']) != 33425:
        raise ValueError('closed predecessor inventory differs')
    physical = {p.relative_to(OLD).as_posix() for p in OLD.rglob('*') if p.is_file()
                and p.name not in ('source-manifest.json', 'rebind-receipt.json')
                and '__pycache__' not in p.parts and 'receipts' not in p.parts and p.suffix != '.pyc'}
    if physical != {r['path'][len(old_prefix):] for r in own}:
        raise ValueError('predecessor physical/source closure differs')
    for selected in own:
        if sha(raw(OLD / selected['path'][len(old_prefix):])) != selected['sha256']:
            raise ValueError('predecessor byte changed')
    changes = {}
    name = 'workflow-output-plan.schema.json'
    changes[name] = exact_replace(raw(OLD / name).decode(), old_prefix + 'service.py', new_prefix + 'service.py', 2).encode()
    name = 'workflow_output_registry.py'
    changes[name] = exact_replace(raw(OLD / name).decode(), old_prefix + 'workflow_', new_prefix + 'workflow_', 7).encode()
    name = 'source_bridge.py'
    value = raw(OLD / name).decode()
    value = exact_replace(value, '_cal_api53_t31_legacy_local_20261023_0001', '_cal_api54_t31_legacy_local_20261023_0001')
    value = exact_replace(value, '_cal_api53_t31_source8_local_20261023_0001', '_cal_api54_t31_source8_local_20261023_0001')
    changes[name] = value.encode()
    name = 'guard.py'
    value = raw(OLD / name).decode()
    value = exact_replace(value, OLD_ADAPTER.relative_to(ROOT).as_posix(), NEW_ADAPTER.relative_to(ROOT).as_posix())
    value = exact_replace(value, "    helper_paths.add('docs/proposals/0007-lab-integrated-schema-package/workflows/agent-context.json')",
                          "    helper_paths.add('docs/proposals/0007-lab-integrated-schema-package/workflows/agent-context.json')\n"
                          "    helper_paths.add('docs/proposals/0007-lab-integrated-schema-package/workflows/engineering.json')")
    changes[name] = value.encode()
    name = 'workflow_transition.py'
    value = raw(OLD / name).decode()
    value = exact_replace(value, "PACKAGE=HERE.parent/'workflow-transition-v1';NAME='_cal_selected_workflow_transition_v1'",
                          "PACKAGE=HERE.parent/'workflow-transition-v2-t31';NAME='_cal_selected_workflow_transition_v2_t31'")
    prior_method = '''    def selected_prior_design(self,header,run,message):
        from . import workflow_prior_input as prior
        from .workflow_output_contracts import need
        need(self.output_reader is not None,'selected private original output reader required')
        ref='transition:engineering:designed';factory=self.output_reader.factory
        result=factory.result(ref);route=factory.live_routes[ref]
        rows,_=result.material.selected(route['output_slot_ref'])
        need(len(rows)==1,'one exact prior design output required')
        with self.store.locked():
            head,current=self.store.replay()
            need(head['sequence']>=1,'committed design predecessor required')
            transaction=source.parse(J.read(self.store.root/'transactions'/('%08d.json'%head['sequence'])))
            prior.verify_prior_design(message=message,run=run,head=head,current_raw=current,
                transaction=transaction,result=result,row=rows[0],header=header)
            self.store.replay()
            need(J.read(self.store.root/'HEAD.json')==J.encoded(head),'prior design journal head changed')
        return {'record':source.parse(rows[0]['raw']),'effective_state':'produced-current','kind':'generated-output'}
'''
    value = exact_replace(value, '    def current_identity(self,ref,kind):\n', prior_method + '    def current_identity(self,ref,kind):\n')
    value = exact_replace(value,
        "            for header in [run[k] for k in ('intent','intent_resolution','work','coordination_context')]+message['input_artifacts']:\n                row=self.selected(header);headers[header['version_ref']]={'artifact':header,'posture':row['effective_state'],'semantic_kind':row['kind']}",
        "            for header in [run[k] for k in ('intent','intent_resolution','work','coordination_context')]+message['input_artifacts']:\n                row=(self.selected_prior_design(header,run,message) if message['transition_ref']=='transition:engineering:implemented' and header['carrier_ref']=='cal.artifact-type.generated-output/v2' else self.selected(header))\n                headers[header['version_ref']]={'artifact':header,'posture':row['effective_state'],'semantic_kind':row['kind']}")
    changes[name] = value.encode()
    name = 'workflow_producer_outputs.py'
    value = raw(OLD / name).decode()
    branch = '''    if ref in ('transition:engineering:designed','transition:engineering:implemented'):
        source_binding=registry['definition_binding']
        need((source_binding['path'],source_binding['sha256']) in factory.source_rows,
             'original engineering template absent from selected API Source')
        public_raw=factory.read_public(source_binding)
        need(sha(public_raw)==source_binding['sha256'],'original engineering template bytes changed')
        public=parse(public_raw)
        need(public['decision_profile']['byte_sha256']=='0'*64 and
             [t['transition_ref'] for t in public['transitions']]==[
                'transition:engineering:designed','transition:engineering:implemented',
                'transition:engineering:assessed'] and
             public['transitions'][0]['input_carriers']==[
                'cal.artifact-type.intent-resolution/v1','cal.artifact-type.work/v1',
                'cal.artifact-type.implementation/v1'] and
             public['transitions'][1]['input_carriers']==[
                'cal.artifact-type.intent-resolution/v1','cal.artifact-type.work/v1',
                'cal.artifact-type.implementation/v1','cal.artifact-type.generated-output/v2'],
             'original public engineering phase signatures differ')
        actual_raw=(host.vault.material(binding) if authorization is None
                    else authorization.material(binding))
        need(sha(actual_raw)==binding['sha256'],'private engineering instance changed')
        executable=parse(actual_raw);profile=executable['decision_profile']
        need(set(profile)=={'scope_ref','identity_ref','version_ref','carrier_ref','byte_sha256'} and
             profile['carrier_ref']=='cal.artifact-type.workflow-decision-profile/v1' and
             profile['scope_ref']==factory.plan['scope_ref'] and
             profile['byte_sha256']!='0'*64,'exact current engineering profile header required')
        expected=copy.deepcopy(public);expected['decision_profile']=copy.deepcopy(profile)
        need(executable==expected,'engineering executable differs outside current decision profile')
        return executable
'''
    value = exact_replace(value,
        "    need(ref == 'transition:agent-context:context-ready',\n",
        branch + "    need(ref == 'transition:agent-context:context-ready',\n")
    changes[name] = value.encode()
    changes['workflow_prior_input.py'] = raw(PRIOR)
    adapter = exact_replace(raw(OLD_ADAPTER).decode(), OLD.name, NEW.name)
    NEW_ADAPTER.parent.mkdir(mode=0o700, parents=True)
    NEW_ADAPTER.write_text(adapter)
    NEW.mkdir(mode=0o700)
    for selected in own:
        name = selected['path'][len(old_prefix):]
        if name == 'contract-profile.json': continue
        target = NEW / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(changes.get(name, raw(OLD / name)))
    (NEW / 'workflow_prior_input.py').write_bytes(changes['workflow_prior_input.py'])
    new_profile = []
    for selected in profile['files']:
        path = selected['path']
        if path.startswith(old_prefix): new_profile.append(row(NEW / path[len(old_prefix):]))
        elif path == OLD_ADAPTER.relative_to(ROOT).as_posix(): new_profile.append(row(NEW_ADAPTER))
        else: new_profile.append(selected)
    for path in [KERNEL / '__init__.py', KERNEL / 'kernel.py', KERNEL / 'fixtures.py']:
        new_profile.append(row(path))
    new_profile.append(row(NEW / 'workflow_prior_input.py'))
    if len({r['path'] for r in new_profile}) != len(new_profile): raise ValueError('profile duplicate')
    profile['files'] = sorted(new_profile, key=lambda r:r['path'])
    profile['integration_members_binding'] = row(NEW / 'integration-members.json')
    profile['claim_ceiling'] = CLAIM
    save(NEW / 'contract-profile.json', profile)
    new_source = []
    for selected in manifest['files']:
        path = selected['path']
        if path.startswith(old_prefix): new_source.append(row(NEW / path[len(old_prefix):]))
        elif path == OLD_ADAPTER.relative_to(ROOT).as_posix(): new_source.append(row(NEW_ADAPTER))
        else: new_source.append(selected)
    new_source.append(row(NEW / 'workflow_prior_input.py'))
    new_source.append(row(ENGINEERING))
    if len({r['path'] for r in new_source}) != len(new_source): raise ValueError('source duplicate')
    manifest['files'] = sorted(new_source, key=lambda r:r['path'])
    manifest['profile_binding'] = row(NEW / 'contract-profile.json')
    manifest['predecessor_source_manifest_binding'] = row(OLD / 'source-manifest.json')
    manifest['claim_ceiling'] = CLAIM
    save(NEW / 'source-manifest.json', manifest)
    save(NEW / 'rebind-receipt.json', {
        'schema_version':'lab-T31-API54-engineering-prior/v1-candidate',
        'predecessor_source_binding':row(OLD / 'source-manifest.json'),
        'successor_source_binding':row(NEW / 'source-manifest.json'),
        'successor_profile_binding':row(NEW / 'contract-profile.json'),
        'adapter_binding':row(NEW_ADAPTER),
        'engineering_template_binding':row(ENGINEERING),
        'kernel_binding':row(KERNEL / 'kernel.py'),
        'prior_input_binding':row(NEW / 'workflow_prior_input.py'),
        'source_files':len(new_source),'profile_files':len(new_profile),
        'authority_effect':'none','observed_workflow_transitions':0,
        'claim_ceiling':CLAIM})
    print(json.dumps({'source_sha256':sha(raw(NEW / 'source-manifest.json')),
                      'profile_sha256':sha(raw(NEW / 'contract-profile.json')),
                      'source_files':len(new_source),'profile_files':len(new_profile)},sort_keys=True))


if __name__ == '__main__':main()
