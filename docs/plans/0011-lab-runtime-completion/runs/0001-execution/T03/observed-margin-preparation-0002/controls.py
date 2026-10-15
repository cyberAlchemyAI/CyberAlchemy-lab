"""Actual installed validator; inert timestamps/numbers, no runtime calibration."""
import copy,hashlib,importlib.util,json,re,sys
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE=Path(__file__).resolve().parent
OLD=HERE.with_name('observed-margin-preparation-0001')
I=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
sys.path.append(str(I/'deps'))
from jsonschema import Draft202012Validator,FormatChecker
schema=json.loads((HERE/'observed-margin-policy.schema.json').read_bytes())
Draft202012Validator.check_schema(schema)
checker=FormatChecker();assert 'date-time' not in checker.checkers
validator=Draft202012Validator(schema,format_checker=checker)
spec=importlib.util.spec_from_file_location('_T03_revision2_unchanged_margin',HERE/'margin.py')
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
assert (HERE/'margin.py').read_bytes()==(OLD/'margin.py').read_bytes()
identity={name:'1'*64 for name in M.IDENTITY_FIELDS}
policy={'schema_version':'lab-observed-lifetime-margin/v1-candidate','authority_effect':'none',
        'status':'empirically-qualified','execution_identity':identity,
        'evidence_bindings':[{'path':'synthetic/inert.json','sha256':'2'*64}],
        'uncertainty_method':'observed-maximum-plus-reviewed-uncertainty','sample_count':1,
        'phase_upper_bounds_us':{name:1000000 for name in M.REMAINING['application-preclaim']},
        'uncertainty_reserve_us':2000000,'gate_overhead_upper_bound_us':1000000,
        'valid_until':'2030-01-01T12:00:00Z'}
deadlines={name:'2030-01-01T00:01:00Z' for name in M.DEADLINE_FIELDS}
cases=[]
def decide(value):
    assert validator.is_valid(value)
    return M.decide(value,identity,deadlines,'2030-01-01T00:00:00Z',
                    'application-preclaim',load_current=True)
old_pattern=json.loads((OLD/'observed-margin-policy.schema.json').read_bytes())['properties']['valid_until']['pattern']
assert re.fullmatch(old_pattern,'2030-01-01T12:00:00+00:00') is not None
assert re.fullmatch(old_pattern,'2030-01-01T12:00:00.123Z') is not None
cases.append({'case':'actual decoded revision1 regex refutes display double-escape assumption','result':'PASS-counterevidence'})
valid=['2030-01-01T12:00:00Z','2030-01-01T12:00:00+00:00']
for digits in range(1,7):
    fraction='123456'[:digits]
    valid.extend(['2030-01-01T12:00:00.'+fraction+suffix for suffix in ['Z','+00:00']])
for stamp in valid:
    candidate={**policy,'valid_until':stamp};assert decide(candidate)['remaining_margin_us']==48000000
    cases.append({'case':'valid UTC timestamp '+stamp,'result':'PASS-schema-and-calendar'})
invalid_shapes=['2030-01-01T12:00:00.Z','2030-01-01T12:00:00.1234567Z',
                '2030-01-01T12:00:00+01:00','2030-01-01T12:00:00+00:01',
                '2030-01-01T12:00:00-00:00','2030-01-01T12:00:00',
                '2030-01-01','2030-01-01 12:00:00Z','2030-01-01T12:00:00z',
                'not-a-date','2030-01-01T12:00:00Zextra','2030-01-01T12:00:00\\+00:00']
for stamp in invalid_shapes:
    assert not validator.is_valid({**policy,'valid_until':stamp})
    cases.append({'case':'invalid UTC shape or offset '+stamp,'result':'PASS-schema-refused'})
for stamp in ['2030-02-30T12:00:00Z','2030-02-29T12:00:00+00:00',
              '2030-00-01T12:00:00Z','2030-13-01T12:00:00Z',
              '2030-01-32T12:00:00Z','2030-01-01T25:00:00Z',
              '2030-01-01T12:60:00Z','2030-01-01T12:00:60Z']:
    candidate={**policy,'valid_until':stamp};assert validator.is_valid(candidate)
    try:decide(candidate)
    except M.MarginRefusal as error:assert error.reason=='invalid-real-deadline'
    else:raise AssertionError('calendar date accepted')
    cases.append({'case':'impossible calendar '+stamp,'schema_shape_accepts':True,
                  'result':'PASS-unchanged-helper-calendar-refused'})
for name,value in [('valid_until',None),('valid_until',True),('valid_until',123),
                   ('sample_count',True),('sample_count','1'),('sample_count',1.5),
                   ('uncertainty_reserve_us',True),('uncertainty_reserve_us',0),
                   ('gate_overhead_upper_bound_us',None)]:
    candidate={**policy,name:value};assert not validator.is_valid(candidate)
    cases.append({'case':'invalid type/value '+name+':'+repr(value),'result':'PASS-schema-refused'})
candidate={**policy,'sample_count':1.0}
assert validator.is_valid(candidate)
try:decide(candidate)
except M.MarginRefusal as error:assert error.reason=='empirical-evidence-missing'
else:raise AssertionError('float empirical sample count accepted by helper')
cases.append({'case':'mathematically integer float is not exact integer sample count',
              'schema_accepts_mathematical_integer':True,'result':'PASS-helper-type-refused'})
assert not validator.is_valid({**policy,'extend_original_deadline':True})
cases.append({'case':'undeclared deadline override field','result':'PASS-schema-refused'})
assert not validator.is_valid(json.loads((HERE/'UNQUALIFIED-POLICY-TEMPLATE.json').read_bytes()))
cases.append({'case':'unknown empirical template remains unqualified','result':'PASS-schema-refused'})
# A full tail bounded by the current operator can refuse even though a later
# separately permitted operator could hypothetically have a later deadline.
# This pure fixture authorizes no such later grant or deadline extension.
short={**deadlines,'operator_reader':'2030-01-01T00:00:11Z'}
try:M.decide(policy,identity,short,'2030-01-01T00:00:00Z','application-preclaim',load_current=True)
except M.MarginRefusal as error:assert error.reason=='real-lease-cannot-fit-observed-tail'
else:raise AssertionError('current operator deadline extended')
cases.append({'case':'conservative current operator bound is retained','result':'PASS-helper-refused'})
manifest=json.loads((OLD/'source-manifest-0002.json').read_bytes())
for row in manifest['files']:
    raw=(ROOT/row['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==row['sha256'] and len(raw)==row['size_bytes']
cases.append({'case':'all 28 frozen revision1 rows remain unchanged','result':'PASS'})
report={'schema_version':'lab-T03-margin-revision2-pure-controls/v1-candidate','authority_effect':'none',
        'task_complete':False,'result':'PASS-pure-UTC-shape-and-calendar-only','cases':cases,'case_count':len(cases),
        'original_v1_rows_rechecked':len(manifest['files']),'helper_bytes_unchanged':True,
        'optional_installed_date_time_checker_present':False,'schema_alone_proves_calendar_validity':False,
        'synthetic_values_are_actual_empirical_thresholds':False,'actual_Lab_constructor_native_domain_Service_Session_or_lease':False,
        'existing_global_schema_library_or_clock_callback_changed':False}
(HERE/'controls-result.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
print(json.dumps({'result':report['result'],'case_count':len(cases),'result_sha256':hashlib.sha256((HERE/'controls-result.json').read_bytes()).hexdigest()}))
