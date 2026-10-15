"""Native review receipts for the frozen complete case-block matrices."""
from pathlib import Path
import json, sys
import generation_runtime_v2 as generation
from generation_review_validation_v2 import validate_paths

R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def jobs():return {j['job_id']:j for j in read(R/'generation-review-schedule.v2.json')['jobs']}
def status():
    out={k:'pending' for k in jobs()}
    for e in generation.events():
        k=e.get('job_id')
        if k not in out:continue
        if e['event_kind']=='job_prepared':out[k]='ready'
        elif e['event_kind']=='native_spawn':out[k]='running'
        elif e['event_kind']=='native_terminal_join':out[k]='valid' if e['validation']['valid'] else 'invalid'
    return out
def prepare(k):
    generation.frozen();j=jobs()[k];assert status()[k]=='pending'
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
    else:blind.write_bytes((R/j['input_refs'][0]).read_bytes())
    opaque_out=R/'reviews/generation-opaque'/f'{reviewer}.json';opaque_out.parent.mkdir(exist_ok=True);assert not opaque_out.exists()
    pp=R/j['prompt_ref'];q=R/'prompts/generation-review-jobs'/f'{reviewer}.txt';q.parent.mkdir(exist_ok=True);assert not q.exists()
    text=pp.read_text()+'\nAssigned reviewer_id='+reviewer+'. Read only this instruction and exact packet '+str(blind.resolve())+'.\n'
    text+='Write only '+str(opaque_out.resolve())+'. No method mappings, siblings, scored files beyond this exact packet, web or agents.\n'
    q.write_text(text)
    inputs.append({'path':str(blind.relative_to(R)),'sha256':generation.sha(blind)})
    return generation.event({'event_kind':'job_prepared','phase':j['phase'],'study_id':j['study_id'],'job_id':k,'input_bindings':inputs,'prompt_ref':str(q.relative_to(R)),'prompt_sha256':generation.sha(q),'output_ref':j['output_ref'],'opaque_output_ref':str(opaque_out.relative_to(R)),'assigned_reviewer_id':reviewer,'expected_rows':packet['expected_total_rows'],'review_schedule_sha256':generation.sha(R/'generation-review-schedule.v2.json')})
def spawn(k,handle):
    j=jobs()[k];assert status()[k]=='ready'
    return generation.event({'event_kind':'native_spawn','phase':j['phase'],'study_id':j['study_id'],'job_id':k,'agent_handle':handle,'host_spawn_observed':True,'fresh_context':True,'turn':1})
def join(k,handle):
    generation.frozen();j=jobs()[k];assert status()[k]=='running'
    sp=[e for e in generation.events() if e.get('job_id')==k and e['event_kind']=='native_spawn'][-1];assert sp['agent_handle']==handle
    pe=[e for e in generation.events() if e.get('job_id')==k and e['event_kind']=='job_prepared'][-1]
    assert all(generation.sha(R/x['path'])==x['sha256'] for x in pe['input_bindings']);assert generation.sha(R/pe['prompt_ref'])==pe['prompt_sha256']
    raw=R/pe['opaque_output_ref'];p=R/j['output_ref'];assert not p.exists(),'first administrative save already exists'
    if raw.exists():p.write_bytes(raw.read_bytes())
    result=validate_paths(R/j['input_refs'][0],p)
    if result['valid'] and read(p)['reviewer_id']!=pe['assigned_reviewer_id']:
        result['valid']=False;result['errors'].append('assigned reviewer identity mismatch')
    if p.exists():result.update(output_sha256=generation.sha(p),saved_words=len(p.read_text().split()))
    return generation.event({'event_kind':'native_terminal_join','phase':j['phase'],'study_id':j['study_id'],'job_id':k,'agent_handle':handle,'terminal_observed':True,'terminal_witness':'parent_received_NATIVE_FINAL_ANSWER','validation':result,'output_ref':j['output_ref']})
if __name__=='__main__':
    a=sys.argv[1:];cmd=a.pop(0)
    if cmd=='status':print(json.dumps(status(),indent=2))
    elif cmd=='prepare':print(json.dumps(prepare(a[0])))
    elif cmd=='spawn':print(json.dumps(spawn(*a)))
    elif cmd=='join':print(json.dumps(join(*a)))
    else:raise SystemExit('unknown command')
