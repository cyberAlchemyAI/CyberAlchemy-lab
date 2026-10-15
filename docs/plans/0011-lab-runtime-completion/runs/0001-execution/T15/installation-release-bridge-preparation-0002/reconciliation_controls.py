"""UNRUN actual-original composite/R02 fixture controls; Root schedules effects.

Trusted selected bootstrap supplies genuine original environment/module/package
and a fresh empty0700 root. This deliberately uses a technical FixtureBuilder;
it does not replace any original host callback or qualify the API host boundary.
"""
import copy,hashlib,os
from pathlib import Path
from .composite_bridge import CompositeHostBridge

def exercise(environment,environment_module,environment_module_binding,repository,package,package_pin,root,fixture_guard):
    root=Path(root)
    assert root.is_absolute() and root.parent==Path('/tmp') and root.name.startswith('cal-bridge2-reconcile-')
    s=root.stat();assert s.st_uid==os.geteuid() and s.st_mode&0o777==0o700 and list(root.iterdir())==[]
    assert type(environment)is environment_module.CompositeEnvironment
    fixture_guard();env=environment;r02=env.r02;checks=[]
    scope=r02.OwnedScope(str(root))
    # Actual original installer creates one new technical generation/receipt.
    first=env.transition('install',package,package_pin,root/'generation-one',scope,None)
    receipt_path=root/'generation-one.environment.json';original=receipt_path.read_bytes()
    active_path=root/'active-composite.json';active_raw=active_path.read_bytes()
    retained=root/'fixture-retained-active.json';active_path.rename(retained)
    s=root.stat();root_anchor={'id':'fixture-install','path':str(root),'device':s.st_dev,'inode':s.st_ino,'uid':s.st_uid,'mode':0o700}
    s=(root/'.composite-install.lock').stat();lock={'name':'.composite-install.lock','device':s.st_dev,'inode':s.st_ino,'uid':s.st_uid,'mode':0o600}
    selection={'descriptor_binding':{'path':str(Path(env.path).relative_to(repository)),'sha256':env.pin},
               'root_anchor':root_anchor,'lock_anchor':lock,'active_binding':None,'retained_receipt_binding':None,
               'reconciliation_selection':{'generation':'generation-one','package_binding':{'path':str(package),'sha256':package_pin},
                                           'receipt_binding':first['active']['receipt_binding']}}
    class FixtureBuilder:
        # Own technical fixture guard only; original API Builder is not imported.
        plan={'install':{'root':str(root),'root_identity':[root_anchor['device'],root_anchor['inode']]}}
        def guard(self):fixture_guard()
    def bridge(value):
        B=CompositeHostBridge(value,env,environment_module,environment_module_binding,repository);B.bind(FixtureBuilder());return B
    installed_before=r02.tree(root/'generation-one')
    def inspect(value=selection):return bridge(value).reconcile(root,package,package_pin,'generation-one')
    observed=inspect()
    assert observed['posture']=='inspect-only' and observed['activation_performed']is False and not active_path.exists()
    assert observed['whole_receipt']==env.parse(original) and r02.tree(root/'generation-one')==installed_before
    checks.append('actual original composite guard R02 verify_install and whole receipt inspect-only positive')
    def refuse(label,value):
        try:inspect(value)
        except (ValueError,OSError,AssertionError):checks.append(label)
        else:raise AssertionError(label)
        assert not active_path.exists() and r02.tree(root/'generation-one')==installed_before
    omitted=copy.deepcopy(selection);omitted['reconciliation_selection']=None
    refuse('missing independent cold target refuses',omitted)
    missing=root/'fixture-retained-receipt.json';receipt_path.rename(missing)
    try:refuse('missing retained whole receipt refuses',selection)
    finally:missing.rename(receipt_path)
    receipt_path.write_bytes(original+b'\n')
    try:refuse('substituted receipt bytes refuse independently selected old pin',selection)
    finally:receipt_path.write_bytes(original)
    for label,mutation in [
        ('wrong generation with fresh pin refuses',lambda v:v.update(generation='other')),
        ('false installed file result with fresh pin refuses',lambda v:v['installed'].update(files=0)),
        ('missing authority field with fresh pin refuses',lambda v:v.pop('authority_effect')),
        ('unknown whole receipt field with fresh pin refuses',lambda v:v.update(unselected_field=True)),
        ('false authority/runtime flags with fresh pin refuse',lambda v:v.update(authority_effect='admit',runtime_activations=1))]:
        value=env.parse(original);mutation(value);raw=environment_module.encoded(value);receipt_path.write_bytes(raw)
        chosen=copy.deepcopy(selection);chosen['reconciliation_selection']['receipt_binding']={'path':str(receipt_path),'sha256':hashlib.sha256(raw).hexdigest()}
        try:refuse(label,chosen)
        finally:receipt_path.write_bytes(original)
    chosen=copy.deepcopy(selection);chosen['reconciliation_selection']['generation']='different'
    refuse('independently selected generation mismatch refuses',chosen)
    # Fresh active selection separately proves the current active whole receipt.
    retained.rename(active_path)
    active_selection=copy.deepcopy(selection);active_selection['active_binding']={'path':str(active_path),'sha256':hashlib.sha256(active_raw).hexdigest()}
    observed=inspect(active_selection)
    assert observed['observed_active']==env.parse(active_raw) and active_path.read_bytes()==active_raw
    assert r02.tree(root/'generation-one')==installed_before
    checks.append('whole selected active predecessor and target reverified without activation')
    fixture_guard()
    return {'result':'PASS-original-composite-cold-fixture-only','checks':checks,'actual_original_fixture_install_performed':True,
            'cold_reconciliation_activations':0,'actual_API_host_builder_qualified':False,'native_or_lease_executed':False,
            'whole_shared_bridge_qualified':False,'original_full_proof_status':'REFUSED','historical_unavailable_count':25,
            'authority_effect':'none'}
