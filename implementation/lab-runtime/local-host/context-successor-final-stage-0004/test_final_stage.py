import copy,datetime as dt,hashlib,json,pathlib,types,unittest
from unittest import mock
HERE=pathlib.Path(__file__).parent
raw=(HERE/'final_stage.py').read_bytes()
S=types.ModuleType('context_selector4');S.__file__=str(HERE/'final_stage.py')
exec(compile(raw,S.__file__,'exec'),S.__dict__)
NOW=dt.datetime(2026,10,20,18,tzinfo=dt.timezone.utc)

class ActualMapperSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.b=S.load_actual()
    def changed(self,key,fn):
        b=copy.deepcopy(self.b);value=json.loads(b[key]);fn(value);b[key]=S.canonical(value);return b
    def semantics(self,b):return S._semantic_joins(b,b['source'],b['package'])
    def test_real_pinned_positive_and_1571_conditional_plan(self):
        x=S.select_after_mapper(NOW)
        self.assertEqual(x['mapper_effect_review_sha256'],S.ACTUAL_REVIEW_SHA)
        self.assertEqual(x['mapper_review_provenance'],'EXACT_ACTUAL_REVIEW_AND_ORIGINAL_OBSERVATIONS')
        self.assertEqual(x['bound_file_count'],1570);self.assertEqual(x['final_count_with_auth'],1571)
        self.assertEqual(len({r['path'] for r in x['bound_rows']}),1570)
        self.assertEqual(x['auth_placeholder']['sha256'],'UNMINTED_UNSELECTED')
        self.assertEqual(x['stage_copy'],'REFUSED');self.assertFalse(x['effect_enabled'])
        self.assertEqual(x['context_output']['child_mode'],'ro')
    def test_actual_raw_stdout_distinct_parsed_equal(self):
        self.assertNotEqual(S.sha(self.b['inner_stdout']),S.sha(self.b['final']))
        self.assertEqual(json.loads(self.b['inner_stdout']),json.loads(self.b['final']))
        self.semantics(self.b)
    def test_outside_review_pin_cannot_be_coherently_replaced(self):
        b=self.changed('review',lambda x:x.update(verdict='PASS_FAKE'))
        with self.assertRaisesRegex(S.Refused,'OUTSIDE_ACTUAL_PIN'):
            S.validate_evidence(b,b['source'],b['package'])
    def test_bool_float_os_exits_refuse_at_direct_semantics(self):
        for bad in (False,0.0,1):
            for key,field in [('outer_result','os_exit_code'),('terminal','client_exit'),('terminal','daemon_exit')]:
                with self.subTest(key=key,field=field,bad=bad):
                    b=self.changed(key,lambda x:x.__setitem__(field,bad))
                    with self.assertRaises(ValueError):self.semantics(b)
            b=self.changed('inner_capture',lambda x:x['capture'].__setitem__('exit_code',bad))
            with self.assertRaises(ValueError):self.semantics(b)
            b=self.changed('review',lambda x:x.__setitem__('outer_os_exit_code',bad))
            with self.assertRaisesRegex(S.Refused,'REVIEW_STRICT_EXIT'):self.semantics(b)
    def test_outer_stream_mismatch_and_failed_capture(self):
        for key,fn in [('outer_result',lambda x:x.update(stdout_sha256='0'*64)),
                       ('inner_capture',lambda x:x['capture'].update(overflow=True)),
                       ('inner_observation',lambda x:x.update(status='UNKNOWN_PRESERVE_NO_RETRY'))]:
            with self.subTest(key=key):
                with self.assertRaises(ValueError):self.semantics(self.changed(key,fn))
    def test_cid_nonce_cleanup_and_attempt_substitution(self):
        for key,fn in [('terminal',lambda x:x.update(container_absent=False)),
                       ('terminal',lambda x:x.update(forced_cleanup=True)),
                       ('prepared',lambda x:x.update(label='0'*32)),
                       ('inner_consumed',lambda x:x.update(attempt='/wrong/family'))]:
            with self.subTest(key=key):
                with self.assertRaises(ValueError):self.semantics(self.changed(key,fn))
    def test_review_cross_family_and_missing_original_hash(self):
        for field in ('source_manifest_sha256','reader_manifest_sha256','stage_effect_review_sha256','container_id'):
            b=self.changed('review',lambda x:x.__setitem__(field,'0'*64))
            with self.assertRaisesRegex(S.Refused,'REVIEW_LINEAGE'):self.semantics(b)
        b=self.changed('review',lambda x:x.update(final_sha256='0'*64))
        with self.assertRaisesRegex(S.Refused,'REVIEW_ORIGINAL_HASHES'):self.semantics(b)
    def test_complete_55_package_bytes(self):
        key=next(k for k in self.b['package_files'] if not k.endswith('manifest.json'))
        for mutation in ('missing','extra','changed'):
            b=copy.deepcopy(self.b)
            if mutation=='missing':del b['package_files'][key]
            if mutation=='extra':b['package_files']['extra']=b'x'
            if mutation=='changed':b['package_files'][key]+=b'x'
            with self.subTest(mutation=mutation):
                with self.assertRaises(ValueError):self.semantics(b)
    def test_exact_953_rows_before_projection(self):
        roles=[{'path':S.MAPPER_ROLE+'/'+n,'sha256':S.sha(self.b['role:'+n])}
               for n in ('__init__.py','base.py','build.py','policy.json')]
        roles.append({'path':S.MAPPER_ROLE+'/source-manifest.json','sha256':S.sha(self.b['source'])})
        for mutate in (lambda rows:rows.pop(), lambda rows:rows.__setitem__(0,rows[1])):
            x=json.loads(self.b['source']);mutate(x['files'])
            with self.assertRaisesRegex(S.Refused,'MAPPER_EXACT_953_SOURCE_ROWS'):
                S._project(mapper_source_manifest_raw=S.canonical(x),mapper_package_manifest_raw=self.b['package'],
                    mapper_role_rows=roles,evidence=self.b,now=NOW)
    def test_source_currentness_and_effect_interval(self):
        with self.assertRaises(ValueError):S.select_after_mapper(dt.datetime(2026,10,21,15,tzinfo=dt.timezone.utc))
        b=self.changed('outer_result',lambda x:x.update(finished_at_ns=1792600000000000000))
        with self.assertRaisesRegex(S.Refused,'SOURCE_EFFECT_INTERVAL'):self.semantics(b)
    def test_context_effects_remain_refused(self):
        for fn in (S.copy_stage,S.issue_authority,S.create_key_or_policy,S.launch_context):
            with self.assertRaises(S.Refused):fn()
    def test_selected_input_and_predecessor_drift(self):
        with mock.patch.object(S,'ACTUAL_PINS_SHA','0'*64):
            with self.assertRaises(S.Refused):S.load_actual()
        pins=S._actual_pins();pins['predecessors'][next(iter(pins['predecessors']))]='0'*64
        with mock.patch.object(S,'_actual_pins',return_value=pins):
            with self.assertRaises(S.Refused):S.load_actual()
