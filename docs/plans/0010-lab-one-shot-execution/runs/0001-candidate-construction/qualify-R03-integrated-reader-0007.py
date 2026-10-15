"""Exercise actual independently selected Reader7 and account its domain catalog."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';HERE=BASE/'current-source-adapter-v7'
SOURCE_PIN='cc484b86ba0e8a2d1e07f1e8d640db055250f5aa5075450c8e8b7acc7cdebf36'
PACKAGE_PIN='c0a01500743d01c5b487b83b219b184fbc14259bc49dde2f36cad684a70e4f4f'
ADAPTER_PIN='78d8150086ed41f6f2c2218805a2387caab1e5931b2619a894330557cb30d23c'


def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    report=RUN/'integrated-reader-qualification-0007.json';assert not report.exists()
    name='_cal_R03_actual_integrated_reader_v7'
    spec=importlib.util.spec_from_file_location(name,HERE/'__init__.py',submodule_search_locations=[str(HERE)])
    package=importlib.util.module_from_spec(spec);sys.modules[name]=package;spec.loader.exec_module(package)
    module=__import__(name+'.reader',fromlist=['SelectedReader'])
    reader=module.SelectedReader(ADAPTER_PIN,SOURCE_PIN,PACKAGE_PIN)
    observed=None;fail=None
    try:
        with reader.open_signed(SOURCE_PIN,PACKAGE_PIN) as selected:
            view=selected.view;records=selected.records
            current={record.artifact['version_ref']:record for record in records}
            for identity,carrier in [(module.records.PRINCIPAL,'cal.artifact-type.principal/v1'),
                (module.records.ASSIGNMENT,'cal.artifact-type.agent-assignment/v1'),
                ('operational-lesson:R03-Machine-policy-custody','cal.artifact-type.operational-lesson/v1'),
                ('challenge-event:'+module.records.PREFIX+':contest','cal.artifact-type.challenge-event/v1')]:
                ref=identity+'@'+module.records.VERSION
                assert ref in current and current[ref].artifact['carrier_ref']==carrier,(identity,'current exact carrier missing')
            selected.guard();reader.guard()
            observed={'included_current_records':len(records),'accounted_subjects':len(selected.dispositions),
                'selected_carriers':sorted({record.artifact['carrier_ref'] for record in records}),
                'current_domain_versions':sorted(current),'source_cut':selected.source_cut,
                'source_body_sha256s':{ref:record.artifact['byte_sha256'] for ref,record in current.items()}}
    except Exception as error:
        fail={'error_class':type(error).__name__,'reason':str(error)}
    value={'schema_version':'lab-actual-integrated-reader-qualification/v1-candidate',
        'result':'PASS' if observed is not None and fail is None else 'FAIL','actual_cases':1,
        'observed':observed,'failure':fail,'files':[bind(path) for path in (HERE/'source-manifest.json',
            BASE/'current-participation-v8/source-manifest.json',BASE/'current-participation-v8/packages/0001/manifest.json',Path(__file__).resolve())],
        'source_guarded_exit_completed':observed is not None and fail is None,'original_adapter_cases_requalified':False,
        'public_resolution_qualified':False,'learning_context_qualified':False,'whole_API_qualified':False,
        'authority_effect':'none','actual_owner_outcome':None,'task_complete':False,'goal_complete':False,
        'claim_ceiling':'One actual independently selected Reader7 construction/catalog case only; inherited adapter cases, public resolution, mapped views and actual learning application remain required.'}
    with report.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':value['result'],'report_binding':bind(report),'observed':observed,
                      'failure':fail}),flush=True)
    return 0 if value['result']=='PASS' else 1


if __name__=='__main__':raise SystemExit(main())
