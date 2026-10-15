"""Memory-only I13 tests. No temp trees, live starts, events, gates or saves.

Source reading verifies the exact assigned immutable corpus. All fake parent
receipts and witnesses exist solely inside these test functions; they are not
actual host observations and are never published as experimental evidence.
"""
import copy
import json
import unittest
from unittest.mock import patch
from pathlib import Path
import composition_i13_runtime_v2 as m


def dump(value):
    return (json.dumps(value,indent=2,ensure_ascii=False)+'\n').encode()


def binding(path, data):
    return {'path':path,'sha256':m.digest(data)}


def witness(review, reviewer, packet=None, purpose='capacity', handle=None):
    """UNSAVED memory-test schema fixture; no host process is created."""
    payload = dump(review) if review is not None else None
    start = {'job_id':reviewer,'study_id':'I13','phase':'capacity' if purpose=='capacity' else 'confirmation',
             'agent_handle':handle or 'MEMORY_ONLY_UNOBSERVED/'+reviewer,'native_call_id':'MEMORY_ONLY_CALL/'+reviewer,
             'turn':1,'prompt_binding':binding(m.PROMPT_DIR+'/review.txt',b'UNSCORED'),
             'input_bindings':[binding(m.FIXTURE_PACKET,b'UNSCORED')],
             'freeze_binding':binding(m.PACK,b'UNSCORED'),
             'assessed_packet_payload_sha256':None if packet is None else m.digest(packet),
             'time_utc':'2026-10-09T00:00:00.000000+00:00','purpose':purpose,
             'event_kind':'native_spawn','host_spawn_observed':True,'fresh_context':True}
    final = {k:copy.deepcopy(v) for k,v in start.items() if k not in ('event_kind','host_spawn_observed','fresh_context')}
    final.update(event_kind='native_terminal_join',time_utc='2026-10-09T00:01:00.000000+00:00',
                 terminal_observed=True,terminal_witness='parent_received_NATIVE_FINAL_ANSWER',
                 output_binding=None if payload is None else binding('reviews/UNSCORED-'+reviewer+'.json',payload),
                 output_payload_sha256=None if review is None else m.digest(review),
                 output_state='missing' if review is None else 'valid',
                 saved_words=0 if payload is None else len(payload.decode().split()),
                 first_substantive_save=True,scored_retries=0)
    return {'start':start,'FINAL':final}


class I13Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = {p:(m.ROOT/p).read_bytes() for p in m.ASSIGNED_SOURCE_HASHES}
        m.validate_bindings([{'path':p,'sha256':h} for p,h in m.ASSIGNED_SOURCE_HASHES.items()],cls.corpus)
        cls.inputs = m.fixture_inputs()
        cls.packet = m.build_fixture_packet(cls.inputs)
        cls.review = m.fixture_review(cls.packet,cls.packet['reviewer_ids'][0])
        cls.contexts = {case:m.source_context(case,cls.corpus) for case in m.CASES}
        cls.old_columns = copy.deepcopy(m.frozen.EXACT_COLUMNS)
        cls.old_identities = copy.deepcopy(m.frozen.IDENTITIES)

    def invalid(self, mutate):
        review = copy.deepcopy(self.review)
        mutate(review)
        result = m.validate_review(self.packet,review)
        self.assertFalse(result['valid'],result)

    def memory_receipt_chain(self):
        """An entirely UNSAVED prospective schema graph, never native evidence."""
        corpus=copy.deepcopy(self.corpus)
        schedule,reviews=m.build_schedule()
        bodies={m.SCHEDULE:schedule,m.REVIEW_SCHEDULE:reviews,m.FIXTURE_INPUTS:self.inputs,
                m.FIXTURE_PACKET:self.packet,m.FIXTURE_COMPLETE:m.build_complete_fixture(self.inputs),
                m.CHECK:{'classification':'UNSCORED_MEMORY_ONLY_CODECHECK_PLACEHOLDER'}}
        corpus.update({p:dump(body) for p,body in bodies.items()})
        for path in (m.CODE,m.TEST):
            corpus[path]=(m.ROOT/path).read_bytes() if (m.ROOT/path).exists() else b'UNSAVED_MEMORY_ONLY_VERSIONED_CODE_BINDING'
        corpus.update({p:text.encode() for p,text in m.build_prompts(corpus['prompts/generation-v2/compression.txt'].decode()).items()})
        closure=m.source_closure_required()
        def binds(paths):return [binding(p,corpus[p]) for p in paths]
        def observed(body,job,purpose,phase,prompt,outpath,startminute):
            w=witness(body,job,purpose=purpose)
            for part in ('start','FINAL'):
                w[part]['phase']=phase;w[part]['prompt_binding']=binding(prompt,corpus[prompt])
                w[part]['input_bindings']=[binding(m.PACK,corpus[m.PACK]),binding(m.FIXTURE_PACKET,corpus[m.FIXTURE_PACKET])]
                w[part]['freeze_binding']=binding(m.PACK,corpus[m.PACK])
                minute=startminute+(part=='FINAL')
                w[part]['time_utc']=f'2026-10-09T00:{minute:02d}:00.000000+00:00'
            w['FINAL']['output_binding']=binding(outpath,corpus[outpath])
            w['FINAL']['output_payload_sha256']=m.digest(body)
            w['FINAL']['saved_words']=len(corpus[outpath].decode().split())
            return w
        author=observed(bodies[m.CHECK],getattr(self,'author_job_override',m.AUTHOR_JOB),'code_author','preparation',
                        getattr(self,'author_prompt_override',m.AUTHOR_PROMPT),m.CHECK,0)
        corpus[m.CAPACITY_BODY]=dump(self.review)
        capw=observed(self.review,getattr(self,'capacity_job_override',m.CAPACITY_JOB),'capacity','capacity',
                      m.PROMPT_DIR+'/maximal-capacity.txt',m.CAPACITY_BODY,2)
        for part in ('start','FINAL'):
            ref=getattr(self,'capacity_freeze_override',m.PACK)
            capw[part]['freeze_binding']=binding(ref,corpus[ref])
        capw['start']['assessed_packet_payload_sha256']=m.digest(self.packet)
        capw['FINAL']['assessed_packet_payload_sha256']=m.digest(self.packet)
        capacity={'classification':'structural_capacity_only_not_semantic_adequacy','study_id':'I13',
                  'packet_binding':binding(m.FIXTURE_PACKET,corpus[m.FIXTURE_PACKET]),
                  'output_binding':binding(m.CAPACITY_BODY,corpus[m.CAPACITY_BODY]),'native_witness':capw,
                  'typed_review_valid':True,'expected_native_rows':444,'complete_fixture_rows':612,
                  'source_bindings':binds(closure['exact_capacity_source_paths'])}
        corpus[m.CAPACITY_RECEIPT]=dump(capacity)
        corpus[m.INDEPENDENT_INPUTS]=dump({'classification':'UNSCORED_MEMORY_ONLY_ASSIGNED_PACK',
            'source_bindings':binds([p for p in closure['exact_independent_source_paths'] if p!=m.INDEPENDENT_INPUTS])})
        independent_body={'study_id':'I13','classification':'pass',
            'checks':{k:True for k in m.INDEPENDENT_BODY_SCHEMA['properties']['checks']['properties']},
            'findings':[],'source_bindings':binds(closure['exact_independent_source_paths']),
            'experimental_admission_claim':False,'claim_limit':'UNSAVED_MEMORY_TEST_STRUCTURE_ONLY'}
        corpus[m.INDEPENDENT_BODY]=dump(independent_body)
        independentw=observed(independent_body,'PREP-I13-INDEPENDENT','independent_prelaunch','preparation',
                             m.PROMPT_DIR+'/independent-prelaunch.txt',m.INDEPENDENT_BODY,4)
        independent={'study_id':'I13','classification':'pass','native_witness':independentw,
            'author_native_witness':author,'output_binding':binding(m.INDEPENDENT_BODY,corpus[m.INDEPENDENT_BODY]),
            'source_bindings':binds(closure['exact_independent_source_paths']),
            'author_handle':author['start']['agent_handle'],'reviewer_handle':independentw['start']['agent_handle'],
            'literal_prompt_policy_verified':True,'exact_source_reuse_verified':True,'runtime_mechanics_verified':True,
            'experimental_admission_claim':False}
        corpus[m.INDEPENDENT_RECEIPT]=dump(independent)
        freeze={'version':m.VERSION,'study_id':'I13','source_bindings':binds(closure['exact_freeze_paths']),
                'independent_receipt_binding':binding(m.INDEPENDENT_RECEIPT,corpus[m.INDEPENDENT_RECEIPT])}
        corpus[m.FREEZE]=dump(freeze)
        admission={'study_id':'I13','status':'pass','freeze_binding':binding(m.FREEZE,corpus[m.FREEZE]),
            'capacity_receipt_binding':binding(m.CAPACITY_RECEIPT,corpus[m.CAPACITY_RECEIPT]),
            'independent_receipt_binding':binding(m.INDEPENDENT_RECEIPT,corpus[m.INDEPENDENT_RECEIPT]),
            'parent_verified':True,'raw_creation_credit':0}
        corpus[m.ADMISSION]=dump(admission)
        decision={'study_id':'I13','phase':'confirmation','status':'pass','case_ids':list(m.CASES[2:]),
            'pilot_creation_valid':False,'pilot_D_skipped':8,'pilot_reviews_gated':2,'pilot_views_gated':16,
            'informative_original_four_block_justification':'UNSAVED synthetic receipt-shape test only; no decision admitted.',
            'independent_source_bound_verification':True,
            'source_bindings':binds(closure['exact_confirmation_decision_source_paths'])}
        corpus[m.PHASE_DECISION]=dump(decision)
        return {m.CAPACITY_RECEIPT:capacity,m.INDEPENDENT_RECEIPT:independent,m.FREEZE:freeze,
                m.ADMISSION:admission,m.PHASE_DECISION:decision},corpus

    def test_01_exact_24_6_48_schedule_factorial(self):
        schedule,reviews=m.build_schedule()
        self.assertEqual((len(schedule['jobs']),len(reviews['jobs']),len(schedule['view_cells'])),(24,6,48))
        self.assertEqual({(j['case_id'],j['pool'],j['compressor'],j['view']) for j in schedule['view_cells']},
                         set(__import__('itertools').product(m.CASES,m.POOLS,m.COMPRESSORS,m.VIEWS)))
        self.assertEqual([j['case_ids'] for j in reviews['jobs']],[list(s) for s in m.SHARDS for _ in (1,2)])
        self.assertEqual(schedule['planned_denominators'],{'D':24,'reviews':6,'views':48})

    def test_02_pilot_original8_2_16_gated(self):
        schedule,reviews=m.build_schedule()
        self.assertEqual(sum(j['planned_disposition']=='skipped_diagnostic_original_pilot' for j in schedule['jobs']),8)
        self.assertEqual(sum(j['planned_disposition']=='administratively_gated_original_pilot' for j in reviews['jobs']),2)
        self.assertEqual(sum(j['planned_disposition']=='diagnostic_gated' for j in schedule['view_cells']),16)
        for case in m.CASES[:2]:
            self.assertFalse(self.contexts[case]['creation_valid'])
            self.assertTrue(self.contexts[case]['diagnostic_only'])
            self.assertEqual(len(self.contexts[case]['raw_packet']['units']),6)
            self.assertEqual(self.contexts[case]['raw_lock']['case_packet_id'],self.contexts[case]['raw_packet']['packet_id'])

    def test_03_proper_raw_before_D_old_HC2_failure_separate(self):
        for case in m.CASES[2:]:
            context=self.contexts[case]
            self.assertTrue(context['creation_valid'])
            self.assertTrue(context['raw_lock']['independent_review_complete'])
            self.assertEqual(len(context['native_raw_witnesses']),5)
            self.assertEqual(len(context['original_full_artifacts']),6)
            self.assertEqual(set(context['producers']),{'ordinary','backcast','generic'})
        self.assertTrue(self.contexts['H-C2']['old_post_failure'])
        self.assertFalse(self.contexts['H-C2']['old_post_context']['lock']['independent_review_complete'])

    def test_04_full_generic_and_exact_raw_carry_identity(self):
        for context in self.contexts.values():
            raw_units={u['unit_id'] for u in context['raw_packet']['units'] if u['content_kind']=='source'}
            expected=[r for r in context['raw_lock']['rows'] if r['table'] in m.CARRY_TABLES and
                      (r['table']!='unit_rows' or r['identity']['unit_id'] in raw_units)]
            self.assertEqual(context['carried_raw_rows'],expected)
            self.assertEqual(sum(r['table']=='unit_rows' for r in expected),3)
            self.assertTrue(context['generic_context_preserved'])
            for pool,producer in context['producers'].items():
                self.assertEqual(producer['job_id'],m.BINDINGS[context['case_id']][(*m.POOLS,'generic').index(pool)])

    def test_05_source_reuse_every_field_no_drift(self):
        source=self.contexts['H-C2']
        self.assertTrue(m.validate_source_reuse(source,copy.deepcopy(source))['valid'])
        for field in ['novelty','evidence']:
            reused=copy.deepcopy(source);reused['carried_raw_rows'][0]['values'][field]='changed'
            self.assertFalse(m.validate_source_reuse(source,reused)['valid'])
        reused=copy.deepcopy(source);reused['carried_raw_rows'][0]['field_status']['novelty']='agreed'
        self.assertFalse(m.validate_source_reuse(source,reused)['valid'])

    def test_06_max444_literal_identities_counts(self):
        self.assertEqual(self.packet['expected_native_rows'],444)
        for case in self.packet['cases']:
            self.assertEqual(case['matrix_counts'],{'raw_rows':0,'archive_pairs':0,'candidate_pairs':0,
                'post_rows':24,'retention_rows':8,'lineage_rows':8,'addition_rows':8,'attack_rows':0,
                'contradiction_rows':0,'unit_rows':4})
            self.assertEqual((case['copied_raw_count'],case['new_source_pair_count'],case['expected_native_rows']),(48,48,148))
            for table,rows in case['expected_matrix'].items():
                ids=[tuple(r['identity'][k] for k in m.FRESH_IDENTITIES[table]) for r in rows]
                self.assertEqual(len(ids),len(set(ids)))
            pairs=[tuple(r['identity'][k] for k in m.PAIR_COLUMNS[:2]) for r in case['source_pair_matrix']]
            self.assertEqual(len(pairs),len(set(pairs)))

    def test_07_max612_complete_rebuild_and_memberships(self):
        result=m.build_complete_fixture(self.inputs)
        self.assertEqual(result['expected_total_rows'],612)
        self.assertEqual(result['native_review_rows'],444)
        for case in result['cases']:
            self.assertEqual(case['complete_row_count'],204)
            v=case['views'];self.assertEqual(len(v['view_status_rows']),8);self.assertEqual(len(v['D_membership_rows']),48)
            self.assertEqual(len({(r['view_cell_id'],r['post_card_id']) for r in v['D_membership_rows']}),48)
        self.assertEqual(result,m.build_complete_fixture(copy.deepcopy(self.inputs)))

    def test_08_valid_full_review(self):
        self.assertTrue(m.validate_review(self.packet,self.review)['valid'])
        self.assertEqual(m.validate_review(self.packet,self.review)['expected_rows'],444)

    def test_09_same_source_two_D_unique_retention(self):
        rows=self.review['cases'][0]['new_review']['retention_rows']
        self.assertEqual(len(rows),8)
        self.assertEqual(len({tuple(r[:2]) for r in rows}),8)
        self.assertEqual(len({r[1] for r in rows}),4)
        self.invalid(lambda r:r['cases'][0]['new_review']['retention_rows'].__setitem__(1,copy.deepcopy(rows[0])))

    def test_10_all_D_times_all_assigned_sources_including_undeclared(self):
        for case in self.packet['cases']:
            expected=set()
            for unit in case['D_units']:
                source=case['source_context']['producers'][unit['pool']]['local_to_original']
                expected.update((m.qualified(unit['unit_id'],card['id']),s) for card in unit['artifact']['openings'] for s in source.values())
            self.assertEqual(expected,{(o['identity']['post_card_id'],o['identity']['source_card_id']) for o in case['source_pair_matrix']})

    def test_11_literal_nested_prompt_schemas(self):
        prompts=m.build_prompts(self.corpus['prompts/generation-v2/compression.txt'].decode())
        for path,text in prompts.items():
            schema=m.parse_json(text.split('BEGIN_LITERAL_JSON_SCHEMA\n')[1].split('\nEND_LITERAL_JSON_SCHEMA')[0])
            self.assertEqual(schema,m.D_SCHEMA if path.endswith(('ordinary_D.txt','source_D.txt')) else
                             m.INDEPENDENT_BODY_SCHEMA if path.endswith('independent-prelaunch.txt') else m.REVIEW_SCHEMA)
            self.assertIn('additionalProperties',text)
            self.assertIn('zero retries',text)
        ordinary=prompts[m.PROMPT_DIR+'/ordinary_D.txt'];source=prompts[m.PROMPT_DIR+'/source_D.txt']
        self.assertNotIn('Source-bound repair:',ordinary)
        repair=self.corpus['prompts/generation-v2/compression.txt'].decode().split('Source-bound repair:',1)[1].split('Generation-source adapter:',1)[0]
        self.assertIn('Source-bound repair:'+repair,source)
        for text in (ordinary,source):self.assertIn('Generation-source adapter:',text)

    def test_12_outer_metadata_echo_rejected(self):
        self.invalid(lambda r:r.update(version=m.VERSION))
        self.invalid(lambda r:r['cases'][0].update(case_id='UNSCORED-F1'))

    def test_13_missing_table_and_unknown_columns(self):
        self.invalid(lambda r:r['cases'][0]['new_review'].pop('attack_rows'))
        self.invalid(lambda r:r['cases'][0]['new_review']['columns']['retention_rows'].remove('compressor_id'))

    def test_14_raw_regrading_prohibited(self):
        self.invalid(lambda r:r['cases'][0]['new_review']['raw_rows'].append(['new',True,2,2,'preserves','stipulated','new','met',True,'x']))

    def test_15_truncation_missing_case(self):
        self.invalid(lambda r:r['cases'].pop())
        self.invalid(lambda r:r['cases'][0]['new_review']['post_rows'].pop())
        self.invalid(lambda r:r['cases'][0]['source_pairs'].pop())

    def test_16_duplicate_case_or_pair(self):
        self.invalid(lambda r:r['cases'].__setitem__(1,copy.deepcopy(r['cases'][0])))
        self.invalid(lambda r:r['cases'][0]['source_pairs'].__setitem__(1,copy.deepcopy(r['cases'][0]['source_pairs'][0])))

    def test_17_unknown_source_and_post_ids(self):
        self.invalid(lambda r:r['cases'][0]['source_pairs'][0].__setitem__(1,'UNASSIGNED'))
        self.invalid(lambda r:r['cases'][0]['new_review']['post_rows'][0].__setitem__(0,'UNASSIGNED'))

    def test_18_bool_as_int_or_string_bool(self):
        self.invalid(lambda r:r['cases'][0]['new_review']['retention_rows'][0].__setitem__(5,1))
        self.invalid(lambda r:r['cases'][0]['new_review']['post_rows'][0].__setitem__(2,'true'))
        self.assertTrue(m.schema_errors({'type':'integer','enum':[0,1,2]},True))

    def test_19_nulls_and_enum_strictness(self):
        self.invalid(lambda r:r['cases'][0]['new_review']['post_rows'][0].__setitem__(2,None))
        self.invalid(lambda r:r['cases'][0]['new_review']['retention_rows'][0].__setitem__(2,'equivalent'))
        self.invalid(lambda r:r['cases'][0]['source_pairs'][0].__setitem__(2,None))

    def test_20_carry_drift_evidence_status_and_order(self):
        self.invalid(lambda r:r['cases'][0]['carried_raw_rows'][0]['values'].__setitem__('evidence','changed'))
        self.invalid(lambda r:r['cases'][0]['carried_raw_rows'][0]['values'].__setitem__('usefulness',True))
        self.invalid(lambda r:r['cases'][0]['carried_raw_rows'][0]['field_status'].__setitem__('novelty','family_unresolved'))
        self.invalid(lambda r:r['cases'][0]['carried_raw_rows'].reverse())

    def test_21_fresh_fixed_source_ids_and_lineage(self):
        self.invalid(lambda r:r['cases'][0]['new_review']['post_rows'][0].__setitem__(1,['R1']))
        self.invalid(lambda r:r['cases'][0]['new_review']['lineage_rows'][0].__setitem__(2,'parked'))

    def test_22_duplicate_JSON_key_and_nonfinite(self):
        for text in ['{"a":1,"a":2}','{"a":NaN}','{"a":Infinity}']:
            with self.assertRaises(ValueError):m.parse_json(text)

    def test_23_no_silent_packet_matrix_truncation(self):
        packet=copy.deepcopy(self.packet);review=copy.deepcopy(self.review)
        packet['cases'][0]['source_pair_matrix'].pop();packet['cases'][0]['new_source_pair_count']-=1
        packet['cases'][0]['expected_native_rows']-=1;packet['expected_native_rows']-=1
        review['cases'][0]['source_pairs'].pop()
        self.assertFalse(m.validate_review(packet,review)['valid'])

    def test_24_D_schema_known_local_only(self):
        unit=self.inputs['cases'][0]['D_units'][0];source=self.inputs['cases'][0]['source_context']['producers']['ordinary']['artifact']
        self.assertTrue(m.validate_D(unit['artifact']['case_id'],source,unit['artifact'])['valid'])
        body=copy.deepcopy(unit['artifact']);body['openings'][0]['source_ids']=['UNASSIGNED:R1']
        self.assertFalse(m.validate_D(body['case_id'],source,body)['valid'])
        body=copy.deepcopy(unit['artifact']);body['proposals'][0]['novelty']='new'
        self.assertFalse(m.validate_D(body['case_id'],source,body)['valid'])

    def test_25_D_reciprocal_mapping_parked_rejected(self):
        unit=self.inputs['cases'][0]['D_units'][0];source=self.inputs['cases'][0]['source_context']['producers']['ordinary']['artifact']
        for alter in [lambda b:b['lineage'][0].update(disposition='parked'),
                      lambda b:b['lineage'][0]['target_ids'].remove('D1'),
                      lambda b:b['openings'][1].update(source_ids=['R2'])]:
            body=copy.deepcopy(unit['artifact']);alter(body)
            self.assertFalse(m.validate_D(body['case_id'],source,body)['valid'])

    def test_26_D_empty_source_and_optional_separation(self):
        source={'openings':[]};body={'case_id':'empty','role':'D','openings':[],'lineage':[],
                                  'decision':'No current raw; optional cannot fabricate source.'}
        self.assertTrue(m.validate_D('empty',source,body)['valid'])
        body['openings']=[copy.deepcopy(self.inputs['cases'][0]['D_units'][0]['artifact']['openings'][0])]
        self.assertFalse(m.validate_D('empty',source,body)['valid'])

    def test_27_actual_native_start_and_FINAL_enforced(self):
        w=witness(self.review,self.packet['reviewer_ids'][0]);self.assertTrue(m.validate_native_witness(w,{}))
        for field,value in [('host_spawn_observed',False),('fresh_context',False),('turn',True)]:
            bad=copy.deepcopy(w);bad['start'][field]=value
            with self.assertRaises(ValueError):m.validate_native_witness(bad,{})
        for field,value in [('terminal_observed',False),('terminal_witness','file_exists'),('first_substantive_save',False),('scored_retries',1)]:
            bad=copy.deepcopy(w);bad['FINAL'][field]=value
            with self.assertRaises(ValueError):m.validate_native_witness(bad,{})

    def test_28_native_binding_hash_prompt_freeze_handle_call(self):
        w=witness(self.review,self.packet['reviewer_ids'][0])
        for field,value in [('agent_handle','another'),('native_call_id','another'),('prompt_binding',binding('a',b'a')),
                            ('freeze_binding',binding('b',b'b')),('input_bindings',[binding('c',b'c')])]:
            bad=copy.deepcopy(w);bad['FINAL'][field]=value
            with self.assertRaises(ValueError):m.validate_native_witness(bad,{})

    def test_29_dual_distinct_native_review_enforced(self):
        review2=m.fixture_review(self.packet,self.packet['reviewer_ids'][1])
        ws=[witness(self.review,self.packet['reviewer_ids'][0],self.packet),witness(review2,self.packet['reviewer_ids'][1],self.packet)]
        locked=m.reconcile_reviews(self.packet,[self.review,review2],ws)
        self.assertTrue(locked['independent_review_complete'])
        for field in ('agent_handle','native_call_id'):
            bad=copy.deepcopy(ws);bad[1]['start'][field]=bad[0]['start'][field];bad[1]['FINAL'][field]=bad[0]['FINAL'][field]
            with self.assertRaises(ValueError):m.reconcile_reviews(self.packet,[self.review,review2],bad)
        with self.assertRaises(ValueError):m.reconcile_reviews(self.packet,[self.review],ws[:1])

    def test_30_missing_review_preserves_every_fresh_row_null(self):
        ws=[witness(self.review,self.packet['reviewer_ids'][0],self.packet),witness(None,self.packet['reviewer_ids'][1],self.packet)]
        locked=m.reconcile_reviews(self.packet,[self.review,None],ws)
        self.assertFalse(locked['independent_review_complete'])
        for case,original in zip(locked['cases'],self.packet['cases']):
            self.assertEqual(case['carried_raw_rows'],original['carried_raw_rows'])
            self.assertEqual(len(case['fresh_rows']),100)
            self.assertTrue(all(v=='unobservable' for r in case['fresh_rows'] for v in r['field_status'].values()))
            self.assertTrue(all(r['values'][k] is None for r in case['fresh_rows'] for k in r['field_status']))

    def test_31_invalid_review_does_not_crash_or_zero(self):
        bad={'reviewer_id':self.packet['reviewer_ids'][1],'cases':[{'broken':True}]}
        ws=[witness(self.review,self.packet['reviewer_ids'][0],self.packet),witness(bad,self.packet['reviewer_ids'][1],self.packet)]
        ws[1]['FINAL']['output_state']='invalid'
        locked=m.reconcile_reviews(self.packet,[self.review,bad],ws)
        self.assertFalse(locked['independent_review_complete'])
        self.assertEqual(sum(len(c['fresh_rows']) for c in locked['cases']),300)

    def test_32_scalar_and_direct_pair_disputes_separate(self):
        other=m.fixture_review(self.packet,self.packet['reviewer_ids'][1])
        other['cases'][0]['new_review']['post_rows'][0][2]=False
        other['cases'][0]['source_pairs'][0][2]='distinct'
        ws=[witness(self.review,self.packet['reviewer_ids'][0],self.packet),witness(other,self.packet['reviewer_ids'][1],self.packet)]
        lock=m.reconcile_reviews(self.packet,[self.review,other],ws)
        disputes=lock['cases'][0]['disputes']
        self.assertEqual(len(disputes),2)
        self.assertEqual({d['scalar_adjudication_allowed'] for d in disputes},{True,False})
        self.assertEqual(lock['forced_family_merges'],0)
        self.assertEqual(lock['scalar_adjudication'],'unused_unless_separately_prospectively_admitted')

    def test_33_fixture_cannot_launder_as_live(self):
        packet=copy.deepcopy(self.packet);packet['live_admissible']=True
        r2=m.fixture_review(packet,packet['reviewer_ids'][1])
        ws=[witness(self.review,packet['reviewer_ids'][0],packet,purpose='experiment'),witness(r2,packet['reviewer_ids'][1],packet,purpose='experiment')]
        with self.assertRaises(ValueError):m.reconcile_reviews(packet,[self.review,r2],ws)

    def test_34_output_payload_hash_exact(self):
        r2=m.fixture_review(self.packet,self.packet['reviewer_ids'][1])
        ws=[witness(self.review,self.packet['reviewer_ids'][0],self.packet),witness(r2,self.packet['reviewer_ids'][1],self.packet)]
        ws[0]['FINAL']['output_payload_sha256']='0'*64
        with self.assertRaises(ValueError):m.reconcile_reviews(self.packet,[self.review,r2],ws)

    def test_35_P10_partial_not_met_null_falsefamily(self):
        for contract in ('partial','not_met'):
            c={'id':'a','fit':'preserves','usefulness':2,'observability':2,'intelligible':True,
               'support':'stipulated','novelty':'new','retention':'retained','family_id':'a','family_confirmed':True,
               'uncertain_links':False,'raw_order':0,'contract':contract}
            self.assertEqual(m.p10.views([c])['eligible_ids'],['a'])
            c['contract']=None;self.assertEqual(m.p10.views([c])['eligible_ids'],[])
            c['contract']=contract;c['family_confirmed']=False
            self.assertEqual(m.p10.views([c])['status'],'evaluable')
            self.assertEqual(m.p10.views([c])['eligible_ids'],[])
            c['uncertain_links']=True;self.assertEqual(m.p10.views([c])['status'],'not_evaluable')

    def test_36_P10_two_source_invariance_and_empty(self):
        report=m.build_complete_fixture(self.inputs)
        self.assertTrue(all(d['identical_source_sets_by_two_source_design'] for c in report['cases'] for d in c['views']['details']))
        self.assertEqual(m.p10.views([])['ordinary'],[])
        self.assertEqual(m.p10.views([])['alternative'],[])

    def test_37_all_multisource_D_carriers_complete_mapping(self):
        case=self.packet['cases'][0];views=m.build_views_and_memberships(case['source_context'],m.fixture_locked_case(case))
        for detail in views['details']:
            self.assertEqual(len(detail['all_D_source_mapping']),6)
            for burden in detail['burden'].values():
                self.assertEqual(len(burden['displayed_D_carriers']),6)
                self.assertEqual(len(burden['displayed_D_carriers'][0]['complete_source_mapping']),2)
                self.assertGreater(burden['actual_D_carrier_saved_words_proxy'],0)
            for proposal in detail['optional_proposals']:
                self.assertIsNone(proposal['inherited_raw_grades']);self.assertEqual(proposal['preservation_credit'],0)
        self.assertTrue(all(r['raw_family_creation_credit']==0 for r in views['D_membership_rows']))

    def test_38_unsupported_D_mapping_gates_not_creates_novelty(self):
        case=self.packet['cases'][0];lock=m.fixture_locked_case(case)
        next(r for r in lock['fresh_rows'] if r['table']=='source_pairs')['values']['relation']='uncertain'
        views=m.build_views_and_memberships(case['source_context'],lock)
        self.assertEqual(sum(r['status']=='not_evaluable' for r in views['view_status_rows']),2)
        self.assertTrue(all(r['member'] is None for r in views['D_membership_rows'][:12]))

    def test_39_retention_lost_uncertain_unobservable(self):
        case=self.packet['cases'][0];lock=m.fixture_locked_case(case)
        row=next(r for r in lock['fresh_rows'] if r['table']=='retention_rows')
        self.assertEqual(m.retention_status(row),'retained')
        row['values']['fit_preserved']=False;self.assertEqual(m.retention_status(row),'lost')
        row['field_status']['fit_preserved']='scalar_unresolved';self.assertEqual(m.retention_status(row),'uncertain')
        self.assertEqual(m.retention_status(None),'unobservable')

    def test_40_full48_view_dispositions_no_silent_empty_omission(self):
        rows=m.planned_view_dispositions(list(self.contexts.values()),{})
        self.assertEqual(len(rows),48)
        self.assertEqual(sum(r['diagnostic_only'] for r in rows),16)
        self.assertTrue(all(r['source_ids'] is None for r in rows))

    def test_41_future_exact_closure_no_recursive_freeze(self):
        closure=m.source_closure_required();paths=closure['exact_freeze_paths']
        self.assertEqual(len(paths),len(set(paths)))
        self.assertTrue(set(m.ASSIGNED_SOURCE_HASHES)<=set(paths))
        self.assertTrue(set(m.OWNED_PATHS)<=set(paths))
        self.assertTrue({m.CAPACITY_BODY,m.CAPACITY_RECEIPT,m.INDEPENDENT_RECEIPT}<=set(paths))
        self.assertFalse({m.FREEZE,m.ADMISSION,m.PHASE_DECISION}&set(paths))
        self.assertIn(m.EXTENSION,paths)
        for key in ('capacity_receipt_schema','independent_receipt_schema','freeze_schema','admission_schema','confirmation_decision_schema'):
            self.assertFalse(closure[key]['additionalProperties'])

    def test_42_capacity_missing_rejects_every_mutating_entrypoint(self):
        with self.assertRaises(ValueError):m.ready({},self.corpus)
        with self.assertRaises(ValueError):m.prepare_D('I13-H-C1-ordinary-ordinary_D',{},self.corpus,{})
        with self.assertRaises(ValueError):m.prepare_review('RF-I13-S2-1',{},self.corpus,{})
        with self.assertRaises(ValueError):m.native_start({}, {},{},self.corpus)
        with self.assertRaises(ValueError):m.native_join({}, {},b'{}',{},self.corpus)
        with self.assertRaises(ValueError):m.lock_reviews(self.packet,[],[],{},self.corpus)
        with patch.object(Path,'mkdir',side_effect=AssertionError('write before readiness')):
            with self.assertRaises(ValueError):m.save_first('outputs/composition-i13-v2/a.json',b'{}',{},self.corpus,{})

    def test_43_source_binding_duplicate_extra_missing_drift(self):
        data={'a':b'a','b':b'b'};bindings=[binding('a',b'a'),binding('b',b'b')]
        self.assertTrue(m.validate_bindings(bindings,data,{'a','b'}))
        for items,paths in [(bindings[:1],{'a','b'}),(bindings,{'a'}),(bindings+[bindings[0]],{'a','b'}),
                            ([binding('a',b'changed'),bindings[1]],{'a','b'})]:
            with self.assertRaises(ValueError):m.validate_bindings(items,data,paths)

    def test_44_normalized_paths_escape_rejected(self):
        for path in ('../a','/a','a/../b','a//b','a/./b','a\\b',''):
            with self.assertRaises(ValueError):m.normalized(path)
        self.assertEqual(m.normalized('a/b.json'),'a/b.json')

    def test_45_source_before_after_hashes_and_frozen_globals(self):
        self.assertEqual(m.frozen.EXACT_COLUMNS,self.old_columns)
        self.assertEqual(m.frozen.IDENTITIES,self.old_identities)
        self.assertNotIn('compressor_id',m.frozen.EXACT_COLUMNS['retention_rows'])
        for path,expected in m.ASSIGNED_SOURCE_HASHES.items():
            self.assertEqual(m.digest((m.ROOT/path).read_bytes()),expected,path)

    def test_46_schema_missing_nested_required_and_wrong_shapes(self):
        for value in (None,[],True,0,'invalid'):
            self.assertFalse(m.validate_review(self.packet,value)['valid'])
        self.invalid(lambda r:r['cases'][0].pop('carried_raw_rows'))
        self.invalid(lambda r:r['cases'][0]['new_review'].update(post_rows={}))
        self.invalid(lambda r:r['cases'][0]['source_pairs'][0].__setitem__(3,''))

    def test_47_no_new_optional_raw_grade_fields(self):
        for case in self.review['cases']:
            self.assertEqual(case['new_review']['columns']['addition_rows'],['card_id','fit','support','evidence'])
        self.assertEqual(self.packet['raw_creation_credit'],0)
        self.assertEqual(self.packet['native_view_judgment_credit'],0)

    def test_48_all_skipped_D_retains_source_lineage_unit_obligations(self):
        context=self.contexts['H-C1'];units=[]
        for pool,comp in __import__('itertools').product(m.POOLS,m.COMPRESSORS):
            units.append({'unit_id':f'I13-H-C1-{pool}-{comp}','pool':pool,'compressor':comp,'execution':'skipped','artifact':None})
        case=m.fresh_case(context,units)
        self.assertEqual(case['copied_raw_count'],21)
        self.assertEqual(case['matrix_counts']['unit_rows'],4)
        self.assertEqual(case['matrix_counts']['retention_rows'],4)
        self.assertEqual(case['matrix_counts']['lineage_rows'],4)
        self.assertTrue(all(o['null_semantics'] for rs in case['expected_matrix'].values() for o in rs))

    def test_49_faithful_merged_carrier_distinct_direct_relation_allowed(self):
        case=self.packet['cases'][0];lock=m.fixture_locked_case(case)
        next(r for r in lock['fresh_rows'] if r['table']=='source_pairs')['values']['relation']='distinct'
        views=m.build_views_and_memberships(case['source_context'],lock)
        self.assertTrue(all(r['status']=='evaluable' for r in views['view_status_rows']))
        self.assertTrue(all(r['raw_family_creation_credit']==0 for r in views['D_membership_rows']))

    def test_50_prospective_receipt_graph_memory_only_positive(self):
        receipts,corpus=self.memory_receipt_chain()
        self.assertTrue(m.ready(receipts,corpus)['ready'])

    def test_51_receipt_capacity_or_independent_exact_closure_rejects(self):
        for which in (m.CAPACITY_RECEIPT,m.INDEPENDENT_RECEIPT,m.FREEZE,m.PHASE_DECISION):
            receipts,corpus=self.memory_receipt_chain();receipts[which]['source_bindings'].pop()
            corpus[which]=dump(receipts[which])
            with self.assertRaises(ValueError):m.ready(receipts,corpus)

    def test_52_native_capacity_file_presence_not_actual_FINAL(self):
        receipts,corpus=self.memory_receipt_chain()
        receipts[m.CAPACITY_RECEIPT]['native_witness']['FINAL']['terminal_witness']='saved_file_exists'
        corpus[m.CAPACITY_RECEIPT]=dump(receipts[m.CAPACITY_RECEIPT])
        with self.assertRaises(ValueError):m.ready(receipts,corpus)

    def test_53_actual_author_FINAL_before_capacity_required(self):
        receipts,corpus=self.memory_receipt_chain()
        receipts[m.INDEPENDENT_RECEIPT]['author_native_witness']['FINAL']['time_utc']='2026-10-09T00:03:00.000000+00:00'
        corpus[m.INDEPENDENT_RECEIPT]=dump(receipts[m.INDEPENDENT_RECEIPT])
        with self.assertRaises(ValueError):m.ready(receipts,corpus)

    def test_54_confirmation_prepare_and_original_pilot_rejected(self):
        receipts,corpus=self.memory_receipt_chain()
        with self.assertRaises(ValueError):m.prepare_D('I13-H-P-ordinary-ordinary_D',receipts,corpus,{})
        prepared=m.prepare_D('I13-H-C1-ordinary-ordinary_D',receipts,corpus,{})
        self.assertEqual(prepared['job']['input_refs'],['cases/H-C1.json','outputs/generation/G0247.json'])
        self.assertEqual(len(prepared['input_bindings']),2)
        with self.assertRaises(ValueError):m.prepare_D(prepared['job']['job_id'],receipts,corpus,{prepared['job']['job_id']:prepared})

    def test_55_literal_prompt_mismatch_rejected_on_prepare(self):
        receipts,corpus=self.memory_receipt_chain()
        corpus[m.PROMPT_DIR+'/ordinary_D.txt']=corpus[m.PROMPT_DIR+'/source_D.txt']
        with self.assertRaises(ValueError):m.prepare_D('I13-H-C1-ordinary-ordinary_D',receipts,corpus,{})

    def test_56_first_save_uses_exclusive_creation_without_overwrite(self):
        schedule,_=m.build_schedule();job=next(j for j in schedule['jobs'] if j['phase']=='confirmation')
        observed=witness({},job['job_id'],purpose='experiment')['start']
        started={'state':'started','job':job,'start':observed}
        with patch.object(m,'ready',return_value={'ready':True}),patch.object(Path,'mkdir'),\
             patch.object(Path,'open',side_effect=FileExistsError('existing first substantive output')) as open_file:
            with self.assertRaises(FileExistsError):m.save_first(job['output_ref'],b'{}',{},self.corpus,started)
            self.assertEqual(open_file.call_args.args,('xb',))

    def test_57_actual_start_freshness_blocks_used_handles(self):
        receipts,corpus=self.memory_receipt_chain()
        prepared=m.prepare_D('I13-H-C1-ordinary-ordinary_D',receipts,corpus,{})
        start=witness({},prepared['job']['job_id'],purpose='experiment')['start']
        for k in ('prompt_binding','input_bindings','freeze_binding'):start[k]=prepared[k]
        self.assertEqual(m.native_start(prepared,start,receipts,corpus)['state'],'started')
        start['agent_handle']=prepared['used_agent_handles'][0]
        with self.assertRaises(ValueError):m.native_start(prepared,start,receipts,corpus)

    def test_58_malformed_invalid_D_preserves_unit_and_sources_without_crash(self):
        context=self.contexts['H-C1']
        for malformed in (None,True,{'openings':None},{'openings':[{'id':[]} ]},
                          {'openings':[{'id':'D1','source_ids':[{}]}]}):
            units=[{'unit_id':f'I13-H-C1-{pool}-{comp}','pool':pool,'compressor':comp,'execution':'invalid',
                    'artifact':copy.deepcopy(malformed)} for pool,comp in __import__('itertools').product(m.POOLS,m.COMPRESSORS)]
            case=m.fresh_case(context,units)
            self.assertEqual(case['matrix_counts']['unit_rows'],4)
            self.assertEqual(case['matrix_counts']['retention_rows'],4)
            self.assertEqual(case['matrix_counts']['lineage_rows'],4)
            self.assertEqual(case['carried_raw_rows'],context['carried_raw_rows'])

    def test_59_native_join_malformed_first_output_still_terminal_invalid(self):
        receipts,corpus=self.memory_receipt_chain()
        prepared=m.prepare_D('I13-H-C1-ordinary-ordinary_D',receipts,corpus,{})
        initial=witness({},prepared['job']['job_id'],purpose='experiment')['start']
        for k in ('prompt_binding','input_bindings','freeze_binding'):initial[k]=prepared[k]
        started=m.native_start(prepared,initial,receipts,corpus)
        for payload in (b'{',b'null',b'[]',b'true',b'{"openings":null}',b'{"case_id":1,"case_id":2}'):
            final={k:copy.deepcopy(v) for k,v in initial.items() if k not in ('event_kind','host_spawn_observed','fresh_context')}
            try:phash=m.digest(m.parse_json(payload))
            except ValueError:phash=None
            final.update(event_kind='native_terminal_join',time_utc='2026-10-09T00:20:00.000000+00:00',
                terminal_observed=True,terminal_witness='parent_received_NATIVE_FINAL_ANSWER',
                output_binding=binding(prepared['job']['output_ref'],payload),output_payload_sha256=phash,
                output_state='invalid',saved_words=len(payload.decode().split()),first_substantive_save=True,scored_retries=0)
            joined=m.native_join(started,final,payload,receipts,corpus)
            self.assertEqual(joined['state'],'invalid')
            self.assertEqual(joined['output_bytes_sha256'],m.digest(payload))

    def test_60_original_source_packet_or_lock_drift_rejected(self):
        for path in ('reports/generation-locked/I06-H-P.json','fixtures/generation-raw-first/I06-H-C1-raw.json',
                     'outputs/generation/G0251.json'):
            corpus=copy.deepcopy(self.corpus);corpus[path]+=b' '
            with self.assertRaises(ValueError):m.source_context('H-P' if 'H-P' in path else 'H-C1',corpus)

    def test_61_source_context_packet_hash_drift_rejected_even_matching_carry(self):
        packet=copy.deepcopy(self.packet);review=copy.deepcopy(self.review)
        packet['cases'][0]['source_context']['producers']['generic']['artifact']['assessment']='changed'
        self.assertFalse(m.validate_review(packet,review)['valid'])

    def test_62_actual_output_words_and_payload_not_metadata_echo(self):
        receipts,corpus=self.memory_receipt_chain()
        w=copy.deepcopy(receipts[m.CAPACITY_RECEIPT]['native_witness'])
        w['FINAL']['saved_words']+=1
        with self.assertRaises(ValueError):m.validate_native_witness(w,{},corpus)

    def test_63_saved_templates_schedules_fixtures_rebuild_when_present(self):
        schedule,reviews=m.build_schedule()
        expected={m.SCHEDULE:schedule,m.REVIEW_SCHEDULE:reviews,m.FIXTURE_INPUTS:self.inputs,
                  m.FIXTURE_PACKET:self.packet,m.FIXTURE_COMPLETE:m.build_complete_fixture(self.inputs)}
        for path,body in expected.items():
            if (m.ROOT/path).exists():self.assertEqual(m.parse_json((m.ROOT/path).read_bytes()),body,path)
        for path,text in m.build_prompts(self.corpus['prompts/generation-v2/compression.txt'].decode()).items():
            if (m.ROOT/path).exists():self.assertEqual((m.ROOT/path).read_text(),text,path)

    def test_64_UNSCORED_does_not_make_assessable_fields_null(self):
        prompts=m.build_prompts(self.corpus['prompts/generation-v2/compression.txt'].decode())
        for name in ('review','maximal-capacity'):
            text=prompts[m.PROMPT_DIR+'/'+name+'.txt']
            self.assertIn('null_semantics=false requires a permitted typed grade/enumeration',text)
            self.assertIn('never invent successful effects',text)
            self.assertIn('Copied original raw rows keep their exact existing values',text)
        self.invalid(lambda r:r['cases'][0]['new_review']['unit_rows'][0].__setitem__(3,None))

    def test_65_fictional_packet_has_exact_rubric_and_assigned_D_instructions(self):
        self.assertEqual(m.FROZEN_CRITERIA_GENERATION,m.parse_json(self.corpus['criteria-generation.v2.json']))
        self.assertEqual(m.FROZEN_REVIEW_CONTRACT,m.parse_json(self.corpus['generation-review-contract.v2.json']))
        self.assertEqual(m.FROZEN_COMPRESSION_SOURCE,self.corpus['prompts/generation-v2/compression.txt'].decode())
        for case in self.packet['cases']:
            self.assertEqual(case['source_context']['raw_packet']['criteria'],m.FROZEN_CRITERIA_GENERATION)
            for unit in case['D_units']:
                policy=case['fresh_semantic_contracts'][unit['semantic_contract_ref']]
                self.assertEqual('Source-bound repair:' in policy,unit['compressor']=='source_D')

    def test_66_whole_shard_packet_hash_required_at_actual_review_start(self):
        r2=m.fixture_review(self.packet,self.packet['reviewer_ids'][1])
        ws=[witness(self.review,self.packet['reviewer_ids'][0],self.packet),witness(r2,self.packet['reviewer_ids'][1],self.packet)]
        ws[0]['start']['assessed_packet_payload_sha256']='0'*64
        ws[0]['FINAL']['assessed_packet_payload_sha256']='0'*64
        with self.assertRaises(ValueError):m.reconcile_reviews(self.packet,[self.review,r2],ws)

    def test_67_review_packet_save_also_requires_capacity_and_admission(self):
        with patch.object(Path,'mkdir',side_effect=AssertionError('packet write before readiness')):
            with self.assertRaises(ValueError):m.save_review_packet({}, {},self.corpus)

    def test_68_fresh_live_D_cannot_be_old_post_file_or_unwitnessed(self):
        contexts=[self.contexts[c] for c in m.SHARDS[1]]
        units={}
        for context in contexts:
            case=context['case_id'];units[case]=[]
            for pool,comp in __import__('itertools').product(m.POOLS,m.COMPRESSORS):
                source=context['producers'][pool]['artifact']
                ids=[c['id'] for c in source['openings']]
                body={'case_id':case,'role':'D','openings':[{'id':f'D{i+1}','source_ids':[local],
                    'claim':'UNSCORED memory-only D proposal.','discriminator':'Unexecuted bounded test.',
                    'fit':'uncertain','probe':'No physical execution.','uncertainty':'Unknown.'} for i,local in enumerate(ids)],
                    'lineage':[{'source_id':local,'disposition':'retained','target_ids':[f'D{i+1}'],
                                'reason':'UNSCORED memory-only source.'} for i,local in enumerate(ids)],
                    'decision':'UNSAVED memory-only; no actual D native witness.'}
                units[case].append({'unit_id':f'I13-{case}-{pool}-{comp}','pool':pool,'compressor':comp,
                                    'execution':'valid','artifact':body})
        packet=m.build_packet(contexts,units,['RF-I13-S2-1','RF-I13-S2-2'])
        with self.assertRaises(ValueError):m.validate_live_packet_sources(packet,self.corpus)



    def test_69_exact_repair468_closure_binds_prompt_pack_without_cycles(self):
        closure=m.source_closure_required()
        pack=m.parse_json(self.corpus[m.PACK])
        original={b['path']:b['sha256'] for b in pack['assigned_source_bindings']}
        self.assertEqual(len(original),466)
        self.assertEqual(m.ASSIGNED_SOURCE_HASHES,{**original,
            m.PACK:m.digest(self.corpus[m.PACK]),m.AUTHOR_PROMPT:m.digest(self.corpus[m.AUTHOR_PROMPT])})
        self.assertEqual(m.ASSIGNED_SOURCE_HASHES[m.PACK],
            '95c9c408274bbbed9ab891e42c4bd2e79d67072f3ee096dc1bef8b8536ee8582')
        self.assertEqual(m.ASSIGNED_SOURCE_HASHES[m.AUTHOR_PROMPT],
            '308e5d01a05bee117c77a2718c7be6df682f63bfdc0b551e0fb3f979216437d8')
        for key in ('exact_freeze_paths','exact_capacity_source_paths','exact_independent_source_paths'):
            paths=closure[key]
            self.assertTrue({m.PACK,m.AUTHOR_PROMPT,m.ORIGINAL_AUTHOR_VALIDATION,
                m.ORIGINAL_CAPACITY_FAILURE,m.ORIGINAL_PREPARATION_BUDGET,
                'receipts/I13-v1-capacity-failure-events.json'}<=set(paths))
            self.assertFalse({m.FREEZE,m.ADMISSION,m.PHASE_DECISION}&set(paths))
        self.assertFalse({m.CODE,m.TEST,m.CHECK}&set(original))

    def test_70_versioned_runtime_paths_and_consistent_new_capacity_identity(self):
        self.assertEqual(m.VERSION,'composition-i13-native-v2')
        self.assertNotIn('CAPACITY-I13-1',self.packet['reviewer_ids'])
        self.assertEqual(self.packet['reviewer_ids'],list(m.CAPACITY_REVIEWERS))
        self.assertEqual(self.review['reviewer_id'],m.CAPACITY_JOB)
        self.assertTrue(all(c['new_review']['reviewer_id']==m.CAPACITY_JOB for c in self.review['cases']))
        prompts=m.build_prompts(self.corpus['prompts/generation-v2/compression.txt'].decode())
        capacity=prompts[m.PROMPT_DIR+'/maximal-capacity.txt']
        self.assertIn('Assigned reviewer_id='+m.CAPACITY_JOB,capacity)
        self.assertIn(str(m.ROOT/m.CAPACITY_BODY),capacity)
        self.assertNotIn('Assigned reviewer_id=CAPACITY-I13-1.',capacity)
        for path in m.OWNED_PATHS:
            self.assertTrue('.v2.' in path or '_v2.py' in path or 'draft-v2' in path,path)
        for path in (m.CAPACITY_BODY,m.CAPACITY_RECEIPT,m.INDEPENDENT_RECEIPT,m.INDEPENDENT_BODY,
                     m.INDEPENDENT_INPUTS,m.FREEZE,m.ADMISSION,m.PHASE_DECISION):
            self.assertIn('.v2.',path)
        self.assertEqual(m.CONTRACT,'contracts/I13-native-preparation-contract.v1.json')

    def test_71_original_author_and_missing_capacity_history_preserved_no_diagnosis(self):
        result=m.validate_preparation_history(self.corpus)
        self.assertTrue(result['original_author_FINAL_verified'])
        self.assertTrue(result['original_missing_capacity_FINAL_verified'])
        self.assertFalse(result['capacity_body_saved'])
        self.assertIsNone(result['capacity_failure_cause'])
        failure=m.parse_json(self.corpus[m.ORIGINAL_CAPACITY_FAILURE])
        self.assertIsNone(failure['native_witness']['FINAL']['output_binding'])
        self.assertEqual(failure['actual_FINAL_text'],
            'No file saved. A pre-save assertion failed; no retry or overwrite was performed. SHA256 unavailable.')
        self.assertEqual(result['scored_credit'],0)
        changed=copy.deepcopy(self.corpus)
        body=copy.deepcopy(failure);body['semantic_judgment']='invented cause'
        changed[m.ORIGINAL_CAPACITY_FAILURE]=dump(body)
        with self.assertRaises(ValueError):m.validate_preparation_history(changed)

    def test_72_original_budget_current3_capacity4_independent5_six_and_one(self):
        schedule,_=m.build_schedule();b=schedule['budget']
        self.assertEqual((b['preparation_maximum'],b['completion_audit_maximum']),(6,1))
        self.assertEqual((b['preparation_ordinal'],b['next_capacity_ordinal'],b['independent_prelaunch_ordinal']),(3,4,5))
        self.assertEqual(b['original_budget_binding'],binding(m.ORIGINAL_PREPARATION_BUDGET,
            self.corpus[m.ORIGINAL_PREPARATION_BUDGET]))
        self.assertEqual((b['pilot_ceiling'],b['confirmation_base'],b['confirmation_ceiling']),(11,20,22))
        self.assertEqual((schedule['pilot_administrative_disposition']['actual_native_calls'],
                          b['pilot_actual_authorized_calls']),(0,0))
        self.assertTrue(b['no_pool_transfer'])

    def test_73_pre_save_work_allowed_without_substantive_retry_failure_diagnostics(self):
        prompts=m.build_prompts(self.corpus['prompts/generation-v2/compression.txt'].decode())
        for name in ('ordinary_D','source_D','review','maximal-capacity'):
            text=prompts[m.PROMPT_DIR+'/'+name+'.txt']
            self.assertIn('Pre-save computation and working checks are preparation',text)
            self.assertIn('until the first substantive artifact is saved once',text)
            self.assertIn('no substantive-output replacement or scored retry',text)
        text=prompts[m.PROMPT_DIR+'/maximal-capacity.txt']
        self.assertIn('exact assertion/error or validator diagnostics',text)
        self.assertIn('whether any substantive file was saved',text)
        self.assertIn('not an actual completed or substantive trial',text)
        self.assertIn('null_semantics=false requires a permitted typed grade/enumeration',text)
        self.assertIn('No diagnostics file or other extra write',text)
        self.assertIn('call4of6',text)

    def test_74_ready_rejects_original_capacity_ID_with_consistently_rebound_chain(self):
        self.capacity_job_override='CAPACITY-I13-1'
        try:receipts,corpus=self.memory_receipt_chain()
        finally:del self.capacity_job_override
        with self.assertRaisesRegex(ValueError,'assigned native job_id'):m.ready(receipts,corpus)

    def test_75_new_capacity_reviewer_ID_outer_and_each_fresh_wrapper_enforced(self):
        for mutate in (lambda r:r.__setitem__('reviewer_id','CAPACITY-I13-1'),
                       lambda r:r['cases'][0]['new_review'].__setitem__('reviewer_id','CAPACITY-I13-1'),
                       lambda r:r['cases'][2]['new_review'].__setitem__('reviewer_id',m.CAPACITY_REVIEWERS[1])):
            self.invalid(mutate)

    def test_76_ready_rejects_original_author_ID_with_consistently_rebound_chain(self):
        self.author_job_override='PREP-I13-NATIVE-CODE'
        try:receipts,corpus=self.memory_receipt_chain()
        finally:del self.author_job_override
        with self.assertRaisesRegex(ValueError,'assigned native job_id'):m.ready(receipts,corpus)

    def test_77_ready_rejects_original_author_prompt_with_consistently_rebound_chain(self):
        self.author_prompt_override='prompts/I13-native-author.v1.txt'
        try:receipts,corpus=self.memory_receipt_chain()
        finally:del self.author_prompt_override
        with self.assertRaisesRegex(ValueError,'assigned native prompt_binding'):m.ready(receipts,corpus)

    def test_78_self_FINAL_or_status_cannot_satisfy_native_terminal_witness(self):
        receipts,corpus=self.memory_receipt_chain()
        w=copy.deepcopy(receipts[m.INDEPENDENT_RECEIPT]['author_native_witness'])
        w['FINAL']['terminal_witness']='author_self_FINAL'
        with self.assertRaisesRegex(ValueError,'actual parent-observed'):m.validate_native_witness(w,{},corpus)
        w=copy.deepcopy(receipts[m.CAPACITY_RECEIPT]['native_witness'])
        w['FINAL']['terminal_observed']=False
        with self.assertRaisesRegex(ValueError,'actual parent-observed'):m.validate_native_witness(w,{},corpus)

    def test_79_original_all_six_contexts_reused_exact_in_new_runtime(self):
        import composition_i13_runtime_v1 as baseline
        originals={p:self.corpus[p] for p in baseline.ASSIGNED_SOURCE_HASHES}
        for case in m.CASES:
            context=baseline.source_context(case,originals)
            self.assertTrue(m.validate_source_reuse(context,self.contexts[case]))
            self.assertEqual(context,self.contexts[case])
            self.assertTrue(self.contexts[case]['generic_context_preserved'])

    def test_80_packet_and_full_matrix_have_no_schema_or_rubric_changes(self):
        import composition_i13_runtime_v1 as baseline
        self.assertEqual(m.REVIEW_SCHEMA,baseline.REVIEW_SCHEMA)
        self.assertEqual(m.D_SCHEMA,baseline.D_SCHEMA)
        self.assertEqual(m.FRESH_COLUMNS,baseline.FRESH_COLUMNS)
        self.assertEqual(m.FRESH_IDENTITIES,baseline.FRESH_IDENTITIES)
        self.assertEqual(m.FROZEN_CRITERIA_GENERATION,baseline.FROZEN_CRITERIA_GENERATION)
        self.assertEqual(m.FROZEN_REVIEW_CONTRACT,baseline.FROZEN_REVIEW_CONTRACT)
        self.assertEqual(m.FROZEN_COMPRESSION_SOURCE,baseline.FROZEN_COMPRESSION_SOURCE)
        for case in self.packet['cases']:
            self.assertEqual(case['copied_raw_count'],48)
            self.assertEqual(sum(case['matrix_counts'].values()),52)
            self.assertEqual(case['new_source_pair_count'],48)
        self.assertEqual(self.packet['expected_native_rows'],444)
        self.assertEqual(m.build_complete_fixture(self.inputs)['expected_total_rows'],612)

    def test_81_new_schedule_entire_matrix_new_output_paths_zero_retry(self):
        schedule,reviews=m.build_schedule()
        for job in schedule['jobs']:
            self.assertTrue(job['output_ref'].startswith('outputs/composition-i13-v2/'))
            self.assertTrue(job['prompt_ref'].startswith(m.PROMPT_DIR+'/'))
            self.assertEqual(job['scored_retries'],0)
        for job in reviews['jobs']:
            self.assertTrue(job['output_ref'].startswith('reviews/composition-i13-v2/'))
            self.assertTrue(job['packet_ref'].endswith('.v2.json'))
            self.assertEqual(job['scored_retries'],0)
        self.assertEqual(schedule['planned_denominators'],{'D':24,'reviews':6,'views':48})

    def test_82_original_history_missing_from_prospective_closure_rejected(self):
        receipts,corpus=self.memory_receipt_chain()
        del corpus['receipts/I13-v1-capacity-failure-events.json']
        with self.assertRaises(ValueError):m.ready(receipts,corpus)
        for p in (m.PACK,m.AUTHOR_PROMPT,m.ORIGINAL_AUTHOR_VALIDATION,m.ORIGINAL_CAPACITY_FAILURE):
            changed=copy.deepcopy(self.corpus);del changed[p]
            with self.assertRaises(ValueError):m.validate_preparation_history(changed)



    def test_83_capacity_cannot_adopt_original_pack_as_current_repair_freeze(self):
        self.capacity_freeze_override='receipts/I13-native-author-inputs.v1.json'
        try:receipts,corpus=self.memory_receipt_chain()
        finally:del self.capacity_freeze_override
        with self.assertRaisesRegex(ValueError,'assigned native freeze_binding'):m.ready(receipts,corpus)


if __name__ == '__main__':
    unittest.main(verbosity=2)
