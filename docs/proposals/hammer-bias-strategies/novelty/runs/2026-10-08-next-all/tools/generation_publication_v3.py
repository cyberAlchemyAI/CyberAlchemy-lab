"""Prospective exclusive publication wrappers; frozen v2 evidence is unchanged.

Only preparation/copy publication differs; prompt and scoring semantics stay v2.
Current already-prepared v2 jobs retain their original receipts.
"""
from generation_runtime_v2 import *
import generation_runtime_v2 as generation
from generation_review_runtime_v2 import jobs as review_jobs, status as review_status
from generation_review_validation_v2 import validate_paths

def safe_sources():
    from generation_disputes_v2 import ready
    ready()

def exclusive_bytes(path,data):
    with path.open("xb") as stream:stream.write(data)

def exclusive_text(path,text):
    with path.open("x") as stream:stream.write(text)

def generation_prepare(k):
    safe_sources(); frozen(); j=jobs()[k]; st=status(); assert st[k]=='pending'
    bad=[x for x in j['depends_on'] if st[x] in ['invalid','skipped']]
    if bad:
        return event({'event_kind':'dependency_disposition','study_id':j['study_id'],'phase':j['phase'],'job_id':k,'status':'skipped','cause':'invalid_or_skipped_dependency','dependency_ids':bad,'semantic_assessment':None})
    assert all(st[x]=='valid' for x in j['depends_on']), 'dependency not terminal-valid'
    for ref, producer in prior_map(j).items():
        if jobs()[producer]['role']=='incumbent-seed' and not read(R/ref)['openings']:
            return event({'event_kind':'dependency_disposition','study_id':j['study_id'],'phase':j['phase'],'job_id':k,'status':'skipped','cause':'no_shared_incumbent','semantic_assessment':None})
    for gate in ['generation-v2-prelaunch', *j['requires_gates']]:
        p=R/'receipts/gates'/f'{gate}.json'; assert p.exists() and read(p).get('status')=='pass', 'gate: '+gate
    out=R/j['output_ref']; assert not out.exists(), 'first substantive save already exists'
    out.parent.mkdir(parents=True,exist_ok=True)
    inputs=[{'path':x,'sha256':sha(R/x)} for x in j['input_refs']]
    prompt=R/j['prompt_ref']; q=R/'prompts/generation-jobs'/f'{k}.txt';q.parent.mkdir(exist_ok=True);assert not q.exists()
    bound_role='D' if j['role']=='compression' else j['role']
    text=prompt.read_text()+ '\nExact job_id='+k+'; required role='+bound_role+'; exact case_id='+j['case_id']+'.\n'
    text+='Prior artifact/job map: '+json.dumps(prior_map(j))+'.\n'
    text+='Read only the instruction and assigned exact inputs: '+', '.join(str((R/x['path']).resolve()) for x in inputs)+'.\n'
    text+='Write only '+str(out.resolve())+'. Do not inspect schedule, archives, criteria, siblings, parent history, web or agents.\n'
    exclusive_text(q,text)
    return event({'event_kind':'job_prepared','study_id':j['study_id'],'phase':j['phase'],'job_id':k,'input_bindings':inputs,'prompt_ref':str(q.relative_to(R)),'prompt_sha256':sha(q),'output_ref':j['output_ref'],'schedule_sha256':sha(R/'generation-schedule.v2.json')})

def review_prepare(k):
    safe_sources(); generation.frozen();j=review_jobs()[k];assert review_status()[k]=='pending'
    source_status=generation.status()
    assert all(source_status[d] in ['valid','invalid','skipped'] for d in j['depends_on']),'nonterminal source units'
    gate=R/'receipts/gates/generation-v2-prelaunch.json';assert gate.exists() and read(gate)['status']=='pass'
    inputs=[{'path':ref,'sha256':generation.sha(R/ref)} for ref in j['input_refs']]
    packet=read(R/j['input_refs'][0]);assert packet['expected_total_rows']==sum(packet['matrix_counts'].values())
    out=R/j['output_ref'];assert not out.exists();out.parent.mkdir(parents=True,exist_ok=True)
    from blind_generation_v2 import opaque
    reviewer=opaque('V',k);assert reviewer in packet['review_job_ids'],'packet-bound reviewer identity'
    blind=R/'fixtures/generation-blind-opaque'/f"{packet['packet_id']}.json";blind.parent.mkdir(exist_ok=True)
    if blind.exists():assert generation.sha(blind)==generation.sha(R/j['input_refs'][0]),'opaque packet differs'
    else:exclusive_bytes(blind,(R/j['input_refs'][0]).read_bytes())
    opaque_out=R/'reviews/generation-opaque'/f'{reviewer}.json';opaque_out.parent.mkdir(exist_ok=True);assert not opaque_out.exists()
    pp=R/j['prompt_ref'];q=R/'prompts/generation-review-jobs'/f'{reviewer}.txt';q.parent.mkdir(exist_ok=True);assert not q.exists()
    text=pp.read_text()+'\nAssigned reviewer_id='+reviewer+'. Read only this instruction and exact packet '+str(blind.resolve())+'.\n'
    text+='Write only '+str(opaque_out.resolve())+'. No method mappings, siblings, scored files beyond this exact packet, web or agents.\n'
    exclusive_text(q,text)
    inputs.append({'path':str(blind.relative_to(R)),'sha256':generation.sha(blind)})
    return generation.event({'event_kind':'job_prepared','phase':j['phase'],'study_id':j['study_id'],'job_id':k,'input_bindings':inputs,'prompt_ref':str(q.relative_to(R)),'prompt_sha256':generation.sha(q),'output_ref':j['output_ref'],'opaque_output_ref':str(opaque_out.relative_to(R)),'assigned_reviewer_id':reviewer,'expected_rows':packet['expected_total_rows'],'review_schedule_sha256':generation.sha(R/'generation-review-schedule.v2.json')})

def review_join(k,handle):
    safe_sources(); generation.frozen();j=review_jobs()[k];assert review_status()[k]=='running'
    sp=[e for e in generation.events() if e.get('job_id')==k and e['event_kind']=='native_spawn'][-1];assert sp['agent_handle']==handle
    pe=[e for e in generation.events() if e.get('job_id')==k and e['event_kind']=='job_prepared'][-1]
    assert all(generation.sha(R/x['path'])==x['sha256'] for x in pe['input_bindings']);assert generation.sha(R/pe['prompt_ref'])==pe['prompt_sha256']
    raw=R/pe['opaque_output_ref'];p=R/j['output_ref'];assert not p.exists(),'first administrative save already exists'
    if raw.exists():exclusive_bytes(p,raw.read_bytes())
    result=validate_paths(R/j['input_refs'][0],p)
    if result['valid'] and read(p)['reviewer_id']!=pe['assigned_reviewer_id']:
        result['valid']=False;result['errors'].append('assigned reviewer identity mismatch')
    if p.exists():result.update(output_sha256=generation.sha(p),saved_words=len(p.read_text().split()))
    return generation.event({'event_kind':'native_terminal_join','phase':j['phase'],'study_id':j['study_id'],'job_id':k,'agent_handle':handle,'terminal_observed':True,'terminal_witness':'parent_received_NATIVE_FINAL_ANSWER','validation':result,'output_ref':j['output_ref']})
