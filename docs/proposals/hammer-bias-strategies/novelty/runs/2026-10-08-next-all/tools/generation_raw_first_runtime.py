"""Prospective raw-before-summary native execution. Frozen predecessor unchanged.

Semantic disagreement remains explicit. Scalar adjudication is optional and is
not launched automatically; this adapter never supplies semantic judgments.
"""
import json
import copy
from pathlib import Path
import generation_runtime_v2 as g
import generation_disputes_v2 as d
import generation_publication_v3 as pub
import blind_generation_v2 as b
from generation_review_validation_v2 import read_json

R = Path(__file__).resolve().parents[1]
read, sha = read_json, g.sha
TERMINAL = {'valid', 'invalid', 'skipped'}

def jobs():
    return {j['job_id']:j for j in read(R/'generation-review-schedule.raw-first.json')['jobs']}

def sources():
    return {
        'tools/generation_raw_first_runtime.py',
        'tools/blind_generation_raw_first.py',
        'tools/generation_review_validation_raw_first.py',
        'generation-review-schedule.raw-first.json',
        'prompts/generation-review-raw-first.txt',
        'prompts/generation-review-post-first.txt',
        'prompts/raw-first-capacity-raw.txt',
        'prompts/raw-first-capacity-post.txt',
        'receipts/generation-raw-first-preparation-budget.json',
        'design/generation-raw-first-successor.draft.json',
        'fixtures/raw-first-capacity-inputs.json',
        'fixtures/raw-first-capacity-raw.json',
        'fixtures/raw-first-capacity-post.json',
        'fixtures/raw-first-capacity-post-raw.json',
        'fixtures/raw-first-capacity-post-lock.json',
        'reviews/raw-first-capacity-raw.json',
        'reviews/raw-first-capacity-post.json',
        'reports/raw-first-packet-code-check.json',
        'reports/raw-first-capacity-inputs.json',
        'reports/raw-first-capacity-validation.json',
        'reports/raw-first-runtime-code-check.json',
        'reports/raw-first-runtime-code-check-followup.json',
        'reports/raw-first-runtime-source-binding-check.json',
        'reports/raw-first-independent-verification.json',
        'reports/raw-first-repair-code-check.json',
        'reports/raw-first-repair-verification.json',
        'design/generation-raw-first-reviewed-round1/generation_raw_first_runtime.py',
        'design/generation-raw-first-reviewed-round1/blind_generation_raw_first.py',
        'design/generation-raw-first-reviewed-round1/generation_review_validation_raw_first.py',
    }

def ready():
    d.ready()
    files=read(R/'freeze-generation-raw-first.json')['files']
    assert isinstance(files,list) and len(files)==len(sources())
    paths=[x['path'] for x in files]
    assert len(set(paths))==len(paths) and set(paths)==sources(), 'exact successor source freeze'
    assert all(not Path(x).is_absolute() and '..' not in Path(x).parts and str(Path(x))==x for x in paths)
    assert all(sha(R/x['path'])==x['sha256'] for x in files), 'successor source drift'
    gate=read(R/'receipts/gates/generation-raw-first-admission.json')
    assert gate['status']=='pass' and gate['freeze_sha256']==sha(R/'freeze-generation-raw-first.json')
    assert read(R/'reports/raw-first-repair-verification.json')['classification']=='pass'

def review_status():
    states={k:'pending' for k in jobs()}
    for e in g.events():
        k=e.get('job_id')
        if k not in states:continue
        if e['event_kind']=='job_prepared':states[k]='ready'
        elif e['event_kind']=='native_spawn':states[k]='running'
        elif e['event_kind']=='native_terminal_join':states[k]='valid' if e['validation']['valid'] else 'invalid'
    return states

def case_jobs(study,case,phase=None):
    out=[j for j in g.jobs().values() if j['study_id']==study and j['case_id']==case]
    assert out and any(j['study_id']==study and j['case_id']==case for j in jobs().values()), 'unadmitted case (old I06 pilot excluded)'
    if phase=='raw':out=[j for j in out if j['role']!='compression']
    return out

def ref(study,case,phase,kind):
    base={'packet':'fixtures/generation-raw-first','map':'receipts/generation-raw-first-maps',
          'lock':'reports/generation-raw-first-locked'}[kind]
    return f'{base}/{study}-{case}-{phase}.json'

def bindings_valid(bindings):
    assert isinstance(bindings,list) and bindings, 'nonempty source binding required'
    assert len({x['path'] for x in bindings})==len(bindings), 'unique source bindings'
    assert all(sha(R/x['path'])==x['sha256'] for x in bindings), 'exact source binding drift'

def bound_lock(study,case,phase='raw'):
    p=ref(study,case,phase,'lock');body=read(R/p)
    bindings_valid(body['source_bindings'])
    observed=[e for e in g.events() if e['event_kind']=='raw_first_lock' and e.get('output_ref')==p]
    assert len(observed)==1 and observed[0]['output_sha256']==sha(R/p), 'observed immutable lock required'
    assert body['study_id']==study and body['case_id']==case and body['review_phase']==phase
    assert body['independent_review_complete'] is observed[0]['independent_review_complete']
    return body, observed[0]

def bound_packet(study,case,phase):
    packetref,mapref=ref(study,case,phase,'packet'),ref(study,case,phase,'map')
    observed=[e for e in g.events() if e['event_kind']=='raw_first_packet' and e.get('packet_ref')==packetref]
    assert len(observed)==1 and observed[0]['packet_sha256']==sha(R/packetref), 'observed immutable packet required'
    assert observed[0]['map_ref']==mapref and observed[0]['map_sha256']==sha(R/mapref), 'observed immutable method/source map required'
    admin=read(R/mapref);bindings_valid(admin['input_bindings'])
    return read(R/packetref),admin

def generation_prepare(k):
    ready();j=g.jobs()[k];case_jobs(j['study_id'],j['case_id'])
    if j['role']=='compression':
        assert g.status()[k]=='pending'
        lock,witness=bound_lock(j['study_id'],j['case_id'])
        # Every raw role and both raw reviews must have finished before any D.
        assert all(g.status()[x['job_id']] in TERMINAL for x in case_jobs(j['study_id'],j['case_id'],'raw'))
        if not lock['independent_review_complete']:
            return g.event({'event_kind':'dependency_disposition','study_id':j['study_id'],'case_id':j['case_id'],'phase':j['phase'],'job_id':k,'status':'skipped','cause':'incomplete_or_invalid_precompression_independent_review','semantic_assessment':None,'raw_lock_ref':ref(j['study_id'],j['case_id'],'raw','lock'),'raw_lock_sha256':witness['output_sha256']})
    result=pub.generation_prepare(k)
    if result['event_kind']=='job_prepared':
        g.event({'event_kind':'raw_first_generation_admission','job_id':k,'raw_lock_sha256':witness['output_sha256'] if j['role']=='compression' else None,'successor_freeze_sha256':sha(R/'freeze-generation-raw-first.json')})
    return result

def generation_spawn(k,handle):
    ready();return g.spawn(k,handle)

def generation_join(k,handle):
    ready();j=g.jobs()[k];assert g.status()[k]=='running'
    sp=next(e for e in reversed(g.events()) if e.get('job_id')==k and e['event_kind']=='native_spawn');assert sp['agent_handle']==handle
    pe=next(e for e in reversed(g.events()) if e.get('job_id')==k and e['event_kind']=='job_prepared')
    bindings_valid(pe['input_bindings']);assert sha(R/pe['prompt_ref'])==pe['prompt_sha256']
    result=g.validate(j)
    try:read(R/j['output_ref'])
    except (OSError,ValueError,UnicodeError) as error:
        result['valid']=False;result.setdefault('errors',[]).append('unique-key readable JSON required: '+str(error))
    return g.event({'event_kind':'native_terminal_join','job_id':k,'agent_handle':handle,'study_id':j['study_id'],'case_id':j['case_id'],'phase':j['phase'],'terminal_observed':True,'terminal_witness':'parent_received_NATIVE_FINAL_ANSWER','validation':result,'output_ref':j['output_ref']})

def case_payload(study,case,phase):
    selected=case_jobs(study,case,'raw' if phase=='raw' else None)
    states=g.status();assert all(states[j['job_id']] in TERMINAL for j in selected), 'all selected units terminal'
    if phase=='raw':
        assert all(states[j['job_id']]=='pending' for j in case_jobs(study,case) if j['role']=='compression'), 'summary already prepared or started'
    terminal={e['job_id']:e for e in g.events() if e['event_kind']=='native_terminal_join'}
    skipped={e['job_id']:e for e in g.events() if e['event_kind']=='dependency_disposition'}
    artifacts,dispositions,bindings={},{},[]
    for j in selected:
        k=j['job_id'];state=states[k]
        if state=='skipped':cause=skipped[k]['cause']
        else:
            e=terminal[k];assert e.get('terminal_observed') is True, 'native terminal witness'
            prepared=next(e for e in reversed(g.events()) if e['event_kind']=='job_prepared' and e.get('job_id')==k)
            bindings_valid(prepared['input_bindings']);assert sha(R/prepared['prompt_ref'])==prepared['prompt_sha256']
            cause='Observed structurally '+state+' native artifact; semantic validity not asserted.'
        dispositions[k]={'execution':state,'cause':cause}
        p=R/j['output_ref']
        if p.exists():
            assert state!='skipped' and terminal[k]['validation'].get('output_sha256')==sha(p), 'terminal output drift'
            bindings.append({'path':j['output_ref'],'sha256':sha(p)})
            try:artifacts[k]=read(p)
            except (ValueError,UnicodeError):artifacts[k]={'unparsed_text':p.read_text(errors='replace')}
        else:assert state!='valid', 'valid terminal lacks saved artifact'
    return artifacts,dispositions,bindings

def make_packet(study,case,phase):
    ready();assert phase in ['raw','post']
    artifacts,dispositions,bindings=case_payload(study,case,phase)
    from blind_generation_raw_first import build_raw,build_post
    inputs=list(b.load_inputs(R));inputs[1]=read(R/'generation-review-schedule.raw-first.json')
    if phase=='raw':packet,admin=build_raw(study,case,artifacts,dispositions,R,tuple(inputs))
    else:
        lock,_=bound_lock(study,case)
        rawref=ref(study,case,'raw','packet');raw,_=bound_packet(study,case,'raw')
        packet,admin=build_post(study,case,artifacts,dispositions,raw,lock,R,tuple(inputs))
        bindings.extend([{'path':rawref,'sha256':sha(R/rawref)},{'path':ref(study,case,'raw','lock'),'sha256':sha(R/ref(study,case,'raw','lock'))}])
    # Source files and native output payloads are administrative, never in judge packet.
    allbindings={x['path']:x for x in [*admin['input_bindings'],*bindings,
        {'path':'generation-review-schedule.raw-first.json','sha256':sha(R/'generation-review-schedule.raw-first.json')}]}
    admin['input_bindings']=list(allbindings.values())
    b.save_new(R/ref(study,case,phase,'map'),admin)
    b.save_new(R/ref(study,case,phase,'packet'),packet)
    return g.event({'event_kind':'raw_first_packet','study_id':study,'case_id':case,'review_phase':phase,'packet_ref':ref(study,case,phase,'packet'),'packet_sha256':sha(R/ref(study,case,phase,'packet')),'map_ref':ref(study,case,phase,'map'),'map_sha256':sha(R/ref(study,case,phase,'map')),'expected_rows':packet['expected_total_rows']})

def review_prepare(k):
    ready();j=jobs()[k];assert review_status()[k]=='pending'
    packetref=j['input_refs'][0];packet,admin=bound_packet(j['study_id'],j['case_id'],j['review_phase'])
    assert all(g.status()[d] in TERMINAL for d in j['depends_on'])
    reviewer=b.opaque('V',k);assert reviewer in packet['review_job_ids']
    rawout=f'reviews/generation-raw-first-opaque/{reviewer}.json';out=R/rawout;out.parent.mkdir(parents=True,exist_ok=True);assert not out.exists()
    prompt=f'prompts/generation-raw-first-jobs/{reviewer}.txt';pp=R/prompt;pp.parent.mkdir(parents=True,exist_ok=True)
    # Only opaque packet path and assigned reviewer ID cross the native boundary.
    blindref=f'fixtures/generation-raw-first-opaque/{packet["packet_id"]}.json';blind=R/blindref;blind.parent.mkdir(parents=True,exist_ok=True)
    if blind.exists():assert sha(blind)==sha(R/packetref)
    else:pub.exclusive_bytes(blind,(R/packetref).read_bytes())
    text=(R/j['prompt_ref']).read_text()+f'\nAssigned reviewer_id={reviewer}. Read only this instruction and exact packet {blind.resolve()}. Write first substantive JSON only {out.resolve()}.\n'
    pub.exclusive_text(pp,text)
    bindings=[{'path':packetref,'sha256':sha(R/packetref)},{'path':blindref,'sha256':sha(blind)},*admin['input_bindings']]
    # Deduplicate shared fixed source refs while retaining exact bytes.
    bindings=list({x['path']:x for x in bindings}.values())
    return g.event({'event_kind':'job_prepared','phase':j['phase'],'review_phase':j['review_phase'],'study_id':j['study_id'],'case_id':j['case_id'],'job_id':k,'input_bindings':bindings,'prompt_ref':prompt,'prompt_sha256':sha(pp),'output_ref':j['output_ref'],'opaque_output_ref':rawout,'assigned_reviewer_id':reviewer,'expected_rows':packet['expected_total_rows'],'successor_schedule_sha256':sha(R/'generation-review-schedule.raw-first.json')})

def review_spawn(k,handle):
    ready();j=jobs()[k];assert review_status()[k]=='ready'
    return g.event({'event_kind':'native_spawn','job_id':k,'agent_handle':handle,'study_id':j['study_id'],'case_id':j['case_id'],'phase':j['phase'],'review_phase':j['review_phase'],'host_spawn_observed':True,'fresh_context':True,'turn':1})

def review_join(k,handle):
    ready();j=jobs()[k];assert review_status()[k]=='running'
    e=next(e for e in reversed(g.events()) if e.get('job_id')==k and e['event_kind']=='native_spawn');assert e['agent_handle']==handle
    pe=next(e for e in reversed(g.events()) if e.get('job_id')==k and e['event_kind']=='job_prepared')
    bindings_valid(pe['input_bindings']);assert sha(R/pe['prompt_ref'])==pe['prompt_sha256']
    out=R/j['output_ref'];out.parent.mkdir(parents=True,exist_ok=True);assert not out.exists()
    raw=R/pe['opaque_output_ref']
    if raw.exists():pub.exclusive_bytes(out,raw.read_bytes())
    from generation_review_validation_raw_first import validate_review
    try:
        packet=read(R/j['input_refs'][0]);body=read(out)
        kw={} if j['review_phase']=='raw' else {'raw_packet':read(R/ref(j['study_id'],j['case_id'],'raw','packet')),'raw_lock':bound_lock(j['study_id'],j['case_id'])[0]}
        result=validate_review(packet,body,**kw)
        if body.get('reviewer_id')!=pe['assigned_reviewer_id']:result['valid']=False;result['errors'].append('assigned reviewer mismatch')
    except (OSError,ValueError,UnicodeError,TypeError,KeyError) as error:result={'valid':False,'errors':['missing or malformed review: '+str(error)]}
    if out.exists():result.update(output_sha256=sha(out),saved_words=len(out.read_text().split()))
    return g.event({'event_kind':'native_terminal_join','job_id':k,'agent_handle':handle,'study_id':j['study_id'],'case_id':j['case_id'],'phase':j['phase'],'review_phase':j['review_phase'],'terminal_observed':True,'terminal_witness':'parent_received_NATIVE_FINAL_ANSWER','validation':result,'output_ref':j['output_ref']})

def carry_raw_rows(report,prior,post_review_complete):
    """Copy actual pre-D judgments, preserving uncertainty and provenance."""
    from blind_generation_raw_first import canonical_hash
    current={(row['table'],row['row_id']):row for row in report['rows']}
    original={(row['table'],row['row_id']):row for row in prior['rows']}
    assert len(current)==len(report['rows']) and len(original)==len(prior['rows'])
    assert set(original)<=set(current), 'missing carried raw row in post lock'
    for key,source in original.items():
        target=current[key]
        assert target['identity']==source['identity'], 'carried raw identity drift'
        if post_review_complete:
            assert canonical_hash(target['values'])==canonical_hash(source['values']), 'carried native values or evidence drift'
        target['values']=copy.deepcopy(source['values'])
        target['field_status']=copy.deepcopy(source['field_status'])
    report['carried_family_disagreements']=copy.deepcopy(prior['family_disagreements'])
    report['carried_independent_raw_review_complete']=prior['independent_review_complete']
    report['carried_independent_grade_credit']=0
    report['uncertainty_counts_by_origin']={}
    for origin,rows in [('carried',prior['rows']),('fresh',[row for key,row in current.items() if key not in original])]:
        report['uncertainty_counts_by_origin'][origin]={
            'scalar_unresolved':sum(s=='scalar_unresolved' for row in rows for s in row['field_status'].values()),
            'family_unresolved':sum(s=='family_unresolved' for row in rows for s in row['field_status'].values())}
    return report

def lock(study,case,phase):
    ready();selected=[j for j in jobs().values() if j['study_id']==study and j['case_id']==case and j['review_phase']==phase];assert len(selected)==2
    if phase=='raw':assert all(g.status()[x['job_id']]=='pending' for x in case_jobs(study,case) if x['role']=='compression'), 'cannot backdate raw lock'
    terminals={e['job_id']:e for e in g.events() if e['event_kind']=='native_terminal_join'}
    witnesses=[terminals[j['job_id']] for j in selected]
    assert all(x.get('terminal_observed') is True for x in witnesses)
    assert len({x['agent_handle'] for x in witnesses})==2, 'independent fresh contexts required'
    spawns=[next(e for e in reversed(g.events()) if e['event_kind']=='native_spawn' and e.get('job_id')==j['job_id']) for j in selected]
    assert all(e.get('fresh_context') is True and e.get('host_spawn_observed') is True for e in spawns)
    packetref=ref(study,case,phase,'packet');packet,admin=bound_packet(study,case,phase)
    adminref=ref(study,case,phase,'map')
    bindings={x['path']:x for x in [*admin['input_bindings'],{'path':packetref,'sha256':sha(R/packetref)},{'path':adminref,'sha256':sha(R/adminref)}]}
    complete=all(e['validation']['valid'] for e in witnesses)
    for j,w in zip(selected,witnesses):
        pe=next(e for e in reversed(g.events()) if e['event_kind']=='job_prepared' and e.get('job_id')==j['job_id']);bindings_valid(pe['input_bindings'])
        path=R/j['output_ref']
        if path.exists():
            assert sha(path)==w['validation'].get('output_sha256'), 'review bytes drift'
            bindings[j['output_ref']]={'path':j['output_ref'],'sha256':sha(path)}
    if complete:report=d.compare(packet,*[read(R/j['output_ref']) for j in selected])
    else:
        rows=[]
        for table,obligations in packet['expected_matrix'].items():
            for ob in obligations:
                values={c:ob['identity'].get(c,ob['fixed_values'].get(c)) for c in packet['contract']['columns'][table]};values['evidence']='Independent assessment invalid/unavailable; semantic fields null.'
                rows.append({'table':table,'row_id':ob['row_id'],'identity':ob['identity'],'values':values,'field_status':{c:'unobservable' for c in packet['contract']['columns'][table] if c not in ob['identity'] and c not in ob['fixed_values'] and c!='evidence'}})
        report={'case_packet_id':packet['packet_id'],'rows':rows,'disputes':[],'family_disagreements':[]}
    from blind_generation_raw_first import canonical_hash,raw_context_hash
    if phase=='post':
        prior,witness=bound_lock(study,case);report=carry_raw_rows(report,prior,complete)
        report['carried_raw_lock_binding']={'path':ref(study,case,'raw','lock'),'sha256':witness['output_sha256']}
    report.update(study_id=study,case_id=case,review_phase=phase,independent_review_complete=complete,meaning_status='locked_source_bound_model_judgments' if complete else 'gated_incomplete_review',source_bindings=list(bindings.values()),raw_packet_sha256=canonical_hash(packet) if phase=='raw' else canonical_hash(read(R/ref(study,case,'raw','packet'))),raw_packet_context_sha256=raw_context_hash(packet) if phase=='raw' else raw_context_hash(read(R/ref(study,case,'raw','packet'))),adjudication={'status':'unused_optional_scalar_turn','scalar_uncertainty_preserved':True},unresolved_scalar_count=sum(s=='scalar_unresolved' for row in report['rows'] for s in row['field_status'].values()),family_unresolved_count=sum(s=='family_unresolved' for row in report['rows'] for s in row['field_status'].values()))
    out=ref(study,case,phase,'lock');d.first_save(R/out,report)
    return g.event({'event_kind':'raw_first_lock','study_id':study,'case_id':case,'review_phase':phase,'output_ref':out,'output_sha256':sha(R/out),'independent_review_complete':complete,'unresolved_scalar_count':report['unresolved_scalar_count'],'family_unresolved_count':report['family_unresolved_count'],'no_new_semantic_judgments_by_parent':True})
