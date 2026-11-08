"""Execute the bounded inspection demanded by the selected fixture Lesson.

The native Session consumes a public discrepancy report. The observed result
is deliberately separate from candidate LessonApplication attribution.
"""
import hashlib
import importlib
import types
import json
from pathlib import Path
import uuid

ROOT=Path(__file__).resolve().parents[6]
EPISODE=ROOT/'implementation/lab-runtime/local-host/t22-api30-episode-inspection-0002/episode.py'


def require(value,reason):
    if not value:raise ValueError(reason)


def sha(raw):return hashlib.sha256(raw).hexdigest()

def execute(P,host,selection,*,episode_pin):
    """Caller selects code pin; accepted inputs are exact live Session output."""
    require(not EPISODE.is_symlink() and EPISODE.is_file(),'selected producer is linked or missing')
    producer_raw=EPISODE.read_bytes()
    require(type(episode_pin) is str and len(episode_pin)==64 and sha(producer_raw)==episode_pin,
            'selected inspection producer bytes changed')
    sid=selection['session_ref'];resource=host.sessions.live.get(sid)
    require(resource is not None,'inspection requires actual live Session')
    resource.guard()
    selected=resource.source
    binding=P.binding('selection:'+sid,P.compact(selection))
    proof=resource.lesson_selections.get(binding['sha256'])
    require(type(proof) is dict and proof['selection_original_sha256']==binding['sha256']
            and proof['source_cut']==selection['source_cut']==selected.source_cut,
            'inspection requires current actually generated selection')
    items=[row for row in selection['items'] if row['posture']=='selected' and not row['expired']]
    require(len(items)==1,'inspection requires exactly one applicable Lesson')
    artifact=items[0]['lesson'];subject=host.handlers.resolve_exact(artifact)
    model=importlib.import_module(P.__package__+'.artifact_model')
    raw=model.record_bytes(host.handlers.view,subject)[0]
    lesson=P.frame_parse(raw)
    require(subject['kind']=='operational-lesson' and sha(raw)==artifact['byte_sha256']
            and 'inspect the signed bounded Project State view for API30 discrepancies' in lesson['payload']['lesson_statement'],
            'selected Lesson does not authorize this bounded inspection procedure')
    name='_t03_later_inspection_'+uuid.uuid4().hex
    episode=types.ModuleType(name);episode.__file__=str(EPISODE)
    exec(compile(producer_raw,str(EPISODE),'exec'),episode.__dict__)
    inputs=episode.selection(ROOT)
    # Actual source bytes are re-read and compared by the producer, rather than
    # accepting an earlier report as the result of this invocation.
    current_state=inputs[2];api=inputs[0]
    require(current_state['payload']['project_ref']==selected.sources.scope_ref,
            'inspection Project differs from the Lesson Session scope')
    indexed={row['path']:row['sha256'] for row in api['files']}
    findings=[]
    for path in (episode.LOOKUP,episode.STATE):
        observed=episode.PINS[path]
        if indexed.get(path)!=observed:
            findings.append({'path':path,'candidate_sha256':indexed.get(path),'observed_sha256':observed,
                             'kind':'unselected' if path not in indexed else 'different-source-bytes'})
    baseline=selected.view.data['baseline']['materials']
    signed=[];public=[]
    for path,pin in sorted(episode.PINS.items()):
        row={'path':path,'sha256':pin}
        if path in baseline:
            require(baseline[path]==pin,'signed baseline diagnosis input differs')
            signed.append(row)
        else:public.append(row)
    report={'signed_baseline_input_bindings':signed,'separately_pinned_public_input_bindings':public,'schema_version':'lab-T03-live-Lesson-inspection-output/v1-candidate',
        'lesson':artifact,'selection_sha256':binding['sha256'],'source_cut':selected.source_cut,
        'producer_binding':{'path':str(EPISODE.relative_to(ROOT)),'sha256':episode_pin},
        'input_bindings':[{'path':path,'sha256':pin} for path,pin in sorted(episode.PINS.items())],
        'project_ref':current_state['payload']['project_ref'],'cursor':current_state['payload']['cursor'],
        'state_payload_sha256':sha(P.compact(current_state['payload'])),
        'observed_discrepancies':findings,'fixture_only':True,'authority_effect':'none'}
    counterevidence={'schema_version':'lab-T03-inspection-counterevidence/v1-candidate',
        'source_cut':selected.source_cut,'result':'observed-selection-does-not-establish-state-correctness',
        'evidence':{'api30_selected_current_lookup':indexed.get(episode.LOOKUP)==episode.PINS[episode.LOOKUP],
                    'api30_selected_current_state':indexed.get(episode.STATE)==episode.PINS[episode.STATE]},
        'limitation':'A pinned discrepancy report proves source selection differences; it does not prove the State content correct, API30 executable, or broad Lesson effectiveness.',
        'authority_effect':'none'}
    resource.guard()
    output=P.compact(report);require(len(output)<=4096,'inspection output exceeds native memory bound')
    before=len(resource.memory);resource.note(output)
    require(len(resource.memory)==before+1 and bytes(resource.memory[-1])==output,
            'native Session did not consume exact inspection output')
    resource.guard()
    return report,counterevidence
