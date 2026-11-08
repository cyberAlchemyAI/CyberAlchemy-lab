"""Author the first reviewable UX source register. Run only when intentionally revising it."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'design/source.json'

def row(id, title, purpose, requirements, acceptance, **extra):
    return dict(id=id, title=title, purpose=purpose, requirements=requirements,
                acceptance=acceptance, **extra)

brand = [row('UX-BR-01', 'Engineer Assessment working identity',
    'Invite mixed software developers to a bounded three-case challenge and earn trust through precise claims.',
    ['Working descriptor: Engineer Assessment; public name, mark and domain require owner selection.',
     'Voice: direct, curious, specific, calm; explain what the participant does and what evidence supports feedback.',
     'Never imply a hiring verdict, personality diagnosis, surveillance or validated rank.',
     'Use participant, response and feedback in participant copy; use case and criterion when explained nearby.',
     'Visual direction: warm off-white canvas, dark ink, restrained blue action, amber caution, explicit text status; no ability color coding.'],
    ['Invitation and feedback copy pass claim review against MVP-EXPERIENCE and metric display gates.',
     'Comprehension study checks that a participant can explain the provisional nature of feedback.'],
    audiences=['mixed software developers', 'reviewers', 'research staff'],
    promise='Three short cases with evidence-linked reflection, subject to the published rules.',
    non_promises=['best-engineer identification', 'employment selection', 'trait or honesty assessment'],
    owner_route='product and research leads; name and mark owner unassigned',
    experiment_refs=['EA-E08'], metric_refs=['PS-04', 'PS-05'])]

system = [row('UX-DS-01', 'Assessment interface system',
    'Provide consistent, accessible interaction and status patterns across participant and staff surfaces.',
    ['Token source is design/tokens.json; semantic tokens map action, text, surface, border and status.',
     'Native controls first; keyboard, focus, label, error and screen reader behavior specified per component.',
     'Status is expressed with words and icons, never color alone; support reduced motion and 200% zoom.',
     'Recording limit is product policy: announce remaining time and preserve the server clock and recovery rules.',
     'Interface changes version screen and component records and receive accessibility and copy review.'],
    ['Candidate token contrast pairs pass WCAG 2.2 AA text contrast calculation.',
     'Automated browser fixtures cover keyboard order, visible focus, names, status changes and responsive reflow.',
     'Human participant tests cover understanding, burden and trust.'],
    token_ref='design/tokens.json', component_refs=[f'UX-CM-{i:02}' for i in range(1,11)],
    screen_refs=[f'UX-SC-{i:02}' for i in range(1,13)],
    source_refs=['https://www.w3.org/TR/WCAG22/', 'https://www.w3.org/WAI/ARIA/apg/',
                 'https://www.w3.org/community/reports/design-tokens/CG-FINAL-format-20251028/'])]

flow_specs = [
 ('participant', 'Invitation through data controls', ['invitation','purpose','access','practice','session-1','session-2','session-3','transcript','feedback','rights'], ['withdrawal','device-denied','upload-interrupted','ASR-failed','timeout']),
 ('reviewer', 'Blind independent rating and adjudication', ['queue','case-rubric','evidence','submit','discrepancy','adjudication'], ['conflict-of-interest','missing-source','rating-disagreement']),
 ('researcher', 'Pilot monitoring and purpose-filtered export', ['protocol','allocation','quality-dashboard','missingness','export-review','manifest'], ['withdrawal','small-cell','incident','case-exposure']),
 ('support', 'Accommodation, recovery and rights assistance', ['request','verify-scope','route','resolve','receipt'], ['identity-mismatch','unresolved-deletion','inaccessible-mode'])]
flows=[]
for i,(slug,title,steps,exceptions) in enumerate(flow_specs,1):
    flows.append(row(f'UX-FL-{i:02}',title,
      f'Give the {slug} role an explicit path, decision points and recoverable exits.',
      ['Every step has an actor, visible status, next action and required backend receipt.',
       'Exceptions preserve the original attempt and evidence lineage; no silent reset or hidden score penalty.',
       'Access policy and purpose are rechecked at staff and export actions.'],
      ['Walk through success and exception fixtures with role-specific permissions.',
       'A user can find the next action after every failure state.'],
      actor=slug, steps=steps, exception_paths=exceptions,
      policy_refs=['model/policies/README.md','software/RECOVERY-PROTOCOL.md'],
      metric_refs=['PS-02','PS-03','PS-06','PS-16']))

screen_specs = [
 ('invitation','participant','Invitation and scope','Open invite; show three topics, time estimate, help rules, feedback limit and access route.','invite_redeemed'),
 ('purposes','participant','Purpose choices','Separate required processing from optional research and contact; expandable adjacent detail and saved choice receipt.','purpose_chosen'),
 ('access','participant','Access and practice','Select response path, test camera/mic, request support and practice without scoring.','practice_completed'),
 ('ready','participant','Case ready','Show immutable case ID, help allowance, reveal rule and clock before explicit start.','case_shown'),
 ('record','participant','Recording','Visible camera preview, blur state, clock, stop action, reveal and local capture health.','recording_started'),
 ('upload','participant','Upload and recovery','Show byte progress, server receipt, retry same upload and explicit unresolved state.','media_committed'),
 ('transcript','participant','Transcript review','Show source-linked ASR, editable correction with original retained and missing-evidence flag.','transcript_corrected'),
 ('feedback','participant','Evidence-linked feedback','Qualitative default, coverage and uncertainty, cited evidence, practice step and no hiring verdict.','report_viewed'),
 ('rights','participant','Data controls','Show purpose and retention status, research withdrawal, export/correction/deletion routes and receipt.','rights_requested'),
 ('rating','reviewer','Blind rating','Pin case and rubric; mark evidence and 0–4/NA/UNK before independent submission.','rating_submitted'),
 ('adjudication','reviewer','Discrepancy review','Preserve both ratings and reason; show material disagreement and adjudication record.','adjudication_recorded'),
 ('operations','researcher','Pilot operations','Show funnel denominators, errors, strata/missingness and gated export with manifest.','export_created')]
screens=[]
for i,(slug,actor,title,content,event) in enumerate(screen_specs,1):
    screens.append(row(f'UX-SC-{i:02}',title,content,
      ['Render pending, success, failure and unavailable states with a next action.',
       'Show policy and uncertainty at the action where they matter.',
       'No raw answer, video or contact data in analytics or client error telemetry.'],
      ['Keyboard and screen reader path reaches primary action and error recovery.',
       'Relevant event is emitted once from server receipt where a durable outcome is claimed.'],
      slug=slug,actor=actor,flow_ref={'participant':'UX-FL-01','reviewer':'UX-FL-02','researcher':'UX-FL-03'}[actor],
      primary_event=event, states=['pending','ready','failure','unavailable'],
      policy_refs=['model/policies/README.md'],metric_refs=['PS-02','PS-04','PS-06']))

component_specs=[
 ('action-button','Button','Native button; loading, disabled reason and visible focus.'),
 ('disclosure','Adjacent detail','Native details/summary or equivalent expanded state for purpose and help rules.'),
 ('status','Status message','Polite live region for ordinary change; urgent alert only for blocking failure.'),
 ('timer','Session timer','Server-synchronized remaining time, nonvisual announcements and no reset on reconnect.'),
 ('recorder','Recording controls','Visible preview and blur state, start/stop labels, permission and failure status.'),
 ('upload','Upload progress','Accessible determinate/indeterminate progress and verified receipt state.'),
 ('reveal','Case reveal','Pinned reveal rule, explicit content state and event receipt.'),
 ('evidence','Evidence excerpt','Quoted transcript span, source link, missingness and correction lineage.'),
 ('rating','Criterion rating','0–4/NA/UNK options, anchor text and rater evidence requirement.'),
 ('recovery','Recovery notice','Cause, preserved state, retry or support action and nonpenalty copy.')]
components=[]
for i,(slug,title,behavior) in enumerate(component_specs,1):
    components.append(row(f'UX-CM-{i:02}',title,behavior,
      ['Expose accessible name, role, state and keyboard interaction.',
       'Support focus visibility, 200% zoom, reduced motion and non-color status.'],
      ['Known-good and known-bad fixture for accessible state and keyboard path.',
       'Human review of copy and context where automated checks cannot prove comprehension.'],
      slug=slug,states=['default','focus','disabled-or-unavailable','error'],
      screen_refs=[x['id'] for x in screens if slug in x['slug'] or (slug in ('action-button','status','recovery') and x['actor']=='participant')][:9],
      source_refs=['https://www.w3.org/TR/WCAG22/','https://www.w3.org/WAI/ARIA/apg/']))

event_names=['invited','invite_redeemed','notice_viewed','purpose_chosen','practice_started','practice_completed',
 'assigned','case_shown','recording_started','reveal_shown','recording_stopped','media_committed',
 'technical_failure','retry_assigned','asr_completed','asr_failed','transcript_corrected',
 'rating_submitted','adjudication_recorded','report_published','report_viewed','research_withdrawn',
 'rights_requested','rights_resolved','export_created','export_revoked','case_retired']
server_only={'invited','assigned','media_committed','retry_assigned','asr_completed','asr_failed','rating_submitted',
 'adjudication_recorded','report_published','research_withdrawn','rights_resolved','export_created','export_revoked','case_retired'}
events=[]
for i,name in enumerate(event_names,1):
    metric = ('PS-01' if name in ('invited','invite_redeemed','recording_started') else
              'PS-02' if name in ('assigned','case_shown','recording_stopped','media_committed','technical_failure','retry_assigned') else
              'PS-07' if name in ('asr_completed','asr_failed','transcript_corrected') else
              'PS-16' if name.startswith(('rights_','research_withdrawn','export_')) else
              'PS-04' if name.startswith('report_') else 'PS-08' if name=='case_retired' else 'PS-03')
    events.append(row(f'UX-EV-{i:02}',name.replace('_',' ').title(),
      f'Define the permitted operational observation for {name}; this is a schema proposal, not an observed event.',
      ['Deduplicate by event ID and causal operation ID; use server receipt for durable outcomes.',
       'Record only declared purpose, pseudonymous subject/attempt, version and timestamp needed for the metric.',
       'Never include transcript, answer text, media bytes, face data, contact address, IP or free-form error text.'],
      ['Synthetic duplicate delivery counts once.', 'A missing or withdrawn purpose blocks research extraction.',
       'Payload allowlist rejects forbidden fields.'],
      event_name=name, emitter='server' if name in server_only else 'client-intent/server-receipt',
      processing_purpose='service-operations; research reuse only when separately eligible',
      required_properties=['event_id','operation_id','occurred_at_server','actor_ref','purpose_ref','subject_pseudonym','attempt_ref','protocol_version','causal_parent_ref'],
      optional_properties=['case_version','session_slot','mode','reason_code','outcome_status'],
      forbidden_properties=['answer_text','transcript_text','media','face_embedding','contact','ip_address','free_text_error'],
      metric_refs=[metric],screen_refs=[x['id'] for x in screens if x['primary_event']==name],
      retention_ref='model/policies/retention-source.json',experiment_refs=['EA-E08']))

source={'schema_version':'ea.ux-source/v1','status':'candidate-design','authority_effect':'none',
 'audience':'invited adult mixed software developers',
 'families':{'brand-identity':brand,'design-system':system,'experience-flow':flows,
             'interface-screen':screens,'ui-component':components,'analytics-event-spec':events},
 'boundary':'Design and event specifications only; no participant event, issued policy, proven usability, or validated hiring claim.'}
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(source,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
print('Wrote',sum(len(v) for v in source['families'].values()),'UX source rows')
