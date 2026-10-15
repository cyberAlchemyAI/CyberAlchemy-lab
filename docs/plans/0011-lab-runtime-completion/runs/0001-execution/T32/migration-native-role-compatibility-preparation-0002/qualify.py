"""Future Root-dispatched complete current574 migration qualification.

No implicit CLI/bootstrap or governing actor. Source and selected factory guards
remain active. Calling this function performs native work and publishes only the
explicitly selected new candidate destination; it is NOT a pure/static control.
"""
import sys,unittest,os,tempfile
from .private_io import write,canonical,directory
from pathlib import Path
from .execution_contract import MigrationExecutionContract,need,sha,ROOT
from . import migration,validate,import_guards

def diagnostic(info):
    kind,_,tb=info;frames=[]
    while tb:
        p=Path(tb.tb_frame.f_code.co_filename)
        if p.is_relative_to(ROOT):frames.append({'path':p.relative_to(ROOT).as_posix(),'function':tb.tb_frame.f_code.co_name,'line':tb.tb_lineno})
        tb=tb.tb_next
    return {'exception_class':kind.__name__,'frames':frames}

def fresh_validate(files,pin,contract):
    with migration.signed_catalog()as(catalog,operations):
        translator=migration.SourceTranslation(catalog,operations,
            producer_bindings=migration.runtime_producers(contract),execution_contract=contract)
        return validate.validate_payload(files,translator,pin,native=True)

def cold_consume(*,execution_contract,independent_manifest_sha256):
    """Root may invoke in a fresh selected process; no new trust in package data."""
    need(type(execution_contract)is MigrationExecutionContract,'actual selectedv2 contract required')
    execution_contract.guard();files=validate.load_package(ROOT/execution_contract.scope['output_root'])
    need(sha(files['manifest.json'])==independent_manifest_sha256,'independent cold package manifest differs')
    verified=fresh_validate(files,independent_manifest_sha256,execution_contract)
    rebuilt=migration.build(execution_contract=execution_contract)
    need(files==rebuilt,'fresh source reconstruction differs from exact selected package bytes')
    execution_contract.guard()
    return {'result':'PASS','authority_effect':'none','actual_owner_outcome':None,
        'same_original_bytes':True,'files_compared':len(files),'native_original_replay':verified,
        'source_execution':False,'source_effects_applied':0,'separate_process_claimed_by_this_function':False}

def qualify(*,execution_contract):
    """Complete build/validator/original hostile suite; Root closes scheduling."""
    need(type(execution_contract)is MigrationExecutionContract,'actual selectedv2 contract required')
    execution_contract.guard()
    progress=Path(tempfile.mkdtemp(prefix='cal-O05-v2-qualification-',dir=execution_contract.factory.selection['owned_parent']))
    write(progress/'00-start.json',canonical({'authority_effect':'none','scope_binding':execution_contract.scope_binding}))
    first=migration.build(execution_contract=execution_contract)
    write(progress/'01-first-build.json',canonical({'manifest_sha256':sha(first['manifest.json'])}))
    second=migration.build(execution_contract=execution_contract)
    write(progress/'02-second-build.json',canonical({'manifest_sha256':sha(second['manifest.json'])}))
    need(first==second,'two complete original-source migration builds differ')
    pin=sha(first['manifest.json']);positive=fresh_validate(first,pin,execution_contract)
    migration.publish(first,ROOT/execution_contract.scope['output_root'],execution_contract=execution_contract)
    durable=validate.load_package(ROOT/execution_contract.scope['output_root'])
    need(durable==first,'published selected candidate differs from full produced bytes')
    case=import_guards.ImportGuards;case.execution_contract=execution_contract
    case.selected_package_bytes=durable;case.independent_manifest_sha256=pin
    outcomes=[]
    class Result(unittest.TestResult):
        def startTest(self,test):
            execution_contract.guard();super().startTest(test)
        def durable(self):
            write(progress/('case-'+str(len(outcomes)).zfill(3)+'.json'),canonical(outcomes[-1]))
        def addSuccess(self,test):
            super().addSuccess(test);outcomes.append({'test':test._testMethodName,'status':'PASS'});self.durable()
        def addFailure(self,test,err):
            super().addFailure(test,err);outcomes.append({'test':test._testMethodName,'status':'FAIL',**diagnostic(err)});self.durable()
        def addError(self,test,err):
            super().addError(test,err);outcomes.append({'test':getattr(test,'_testMethodName',str(type(test).__name__)),'status':'ERROR',**diagnostic(err)});self.durable()
    result=Result();unittest.defaultTestLoader.loadTestsFromTestCase(case).run(result)
    execution_contract.guard()
    receipt={'schema_version':'lab-O05-current-native-migration-qualification/v1-candidate',
        'result':'PASS'if result.wasSuccessful()else'FAIL','authority_effect':'none','actual_owner_outcome':None,
        'scope_binding':execution_contract.scope_binding,'manifest_sha256':pin,'all_file_sha256':{k:sha(v)for k,v in sorted(first.items())},
        'two_builds_exact':True,'carriers_and_native':positive,'original_hostile_cases':outcomes,
        'historical480_byte_identity':False,'full_historical_proof_status':'REFUSED','historical_missing_inputs':25,
        'fresh_process_reconstruction_verified':False,
        'private_progress_root':str(progress),
        'remaining':'Root must independently bind this result and run cold_consume in a fresh selected process, plus selected native source regressions/build provenance. No governing/owner/coupled admission claim.'}
    write(progress/'result.json',canonical(receipt));return receipt

if __name__=='__main__':raise SystemExit('Root must close explicitv2 scope/private factory/current Source/dependency custody and exclusive dispatch before these native functions are called.')
