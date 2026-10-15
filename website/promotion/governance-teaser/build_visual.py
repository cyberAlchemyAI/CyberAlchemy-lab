"""Render the local capability-definition, implementation and review carousel."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
TOTAL = 9

def icon(name):
    return f'<img src="assets/{name}.svg" alt="" aria-hidden="true">'

def slide(number, cls, title, body, label, example=True):
    return f'''<div class="frame"{' hidden' if number>1 else ''}><section class="slide {cls}" aria-labelledby="slide-{number}">
<header><img class="logo" src="assets/logo.svg" alt="CyberAlchemy Lab"></header>
<h{'1' if number==1 else '2'} id="slide-{number}">{title}</h{'1' if number==1 else '2'}>
{body}<footer><span>{number:02d} / {TOTAL:02d}</span></footer></section></div>'''

lenses=''.join(f'<span class="{key}">{icon(asset)}<b>{label}</b><small>{meaning}</small></span>' for key,asset,label,meaning in [('authority','book-open','Authority','Who sets the rules'),('provenance','route','Provenance','How we got this result'),('lifecycle','refresh-cw','Lifecycle','Where things stand')])
slides=[]
slides.append(slide(1,'cover capability-cover','Who gets to define<br>a complete export?',f'''<img class="cover-orb" src="assets/orb.webp" alt=""><div class="cover-lenses">{lenses}</div>''','Governance for agent work',False))

slides.append(slide(2,'capability-overview story-overview','A customer’s request',f'''<p class="product-anchor">Customer 1 wants its active database entries in a file.</p>
<div class="overview-flow diagram" role="img" aria-label="A customer wants a file containing its active database entries. Define what complete means before an AI agent writes and runs code and another checks the exported file. Each agent needs its own permissions. An entry ID is unique within the saved database copy.">
<div class="outcome-node authority">{icon('book-open')}<strong>Define what “complete” means</strong></div>
<div class="story-stem" aria-hidden="true">↓</div>
<div class="overview-pair"><div>{icon('bot')}<strong>Write and run code</strong></div><div>{icon('bot')}<strong>Check the file</strong></div></div>
<div class="overview-link"><span>Code and exported file</span><b aria-hidden="true">→</b><span>Checked against the rule</span></div></div>''','Overview'))

slides.append(slide(3,'definition-page visual-definition','Which entries belong<br>in the export?',f'''<p class="selection-intro">Use the full database copy saved at one time.</p>
<div class="selection-visual diagram" role="img" aria-label="These three entries illustrate a rule applied to the entire database copy saved at one point in time. Entry 1 belongs to Customer 1 and is active, so its ID must be in the file. Entry 10001 belongs to Customer 1 but is inactive. Entry 10021 is active but belongs to Customer 2. Those two entries are excluded. The query filter is Customer equals Customer 1 AND Status equals Active. Both conditions must match. Select every entry for the chosen customer matching every chosen filter, then check that every selected ID appears in the file. This rule checks whether every selected entry ID appears in the file.">
<div class="query-filter"><span>Query filter · both conditions must match</span><strong>Customer = Customer 1 <b>AND</b> Status = Active</strong></div>
<p class="source-excerpt">A few entries from the full copy</p>
<table class="selection-records"><thead><tr><th>Entry ID</th><th>Customer</th><th>Status</th><th></th></tr></thead><tbody>
<tr class="selected-record"><td>1</td><td>Customer 1</td><td>Active</td><td><span class="selection-mark">✓</span> Required</td></tr>
<tr><td>10001</td><td>Customer 1</td><td>Inactive</td><td><span class="selection-mark" aria-label="Excluded">×</span></td></tr>
<tr><td>10021</td><td>Customer 2</td><td>Active</td><td><span class="selection-mark" aria-label="Excluded">×</span></td></tr>
</tbody></table>
<div class="selection-transfer" aria-hidden="true">↓</div>
<div class="export-rule authority">{icon('book-open')}<strong>Every selected entry’s ID<br>must be in the file.</strong></div>
</div>''','Definition content first'))

slides.append(slide(4,'meaning-page story-authority','Who accepts the rule?',f'''<div class="meaning-flow diagram" role="img" aria-label="The service owner is the person authorized to set the service’s requirements. The owner accepts this exact definition for the chosen customer, filters and saved database copy. Every selected entry ID must be in the exported file. Both agents use this rule. Accepting the definition does not prove the code works or give either agent permission to act.">
<div class="authority-owner">{icon('users')}<strong>Service owner<br>Sets the requirements</strong></div>
<div class="connector authority"><span>accepts this definition</span><b aria-hidden="true">↓</b></div>
<div class="shared-criterion authority">{icon('book-open')}<strong>Every selected entry’s ID<br>must be in the file.</strong></div>
<svg class="meaning-branches" viewBox="0 0 920 100" preserveAspectRatio="none" aria-hidden="true"><path d="M460 0V40M210 95V40H710V95"/><path d="m199 81 11 14 11-14m478 0 11 14 11-14"/></svg>
<div class="meaning-agents"><div>{icon('bot')}<strong>Write and run code</strong></div><div>{icon('bot')}<strong>Check the file</strong></div></div></div>''','Authority over meaning'))

slides.append(slide(5,'permissions-page visual-permissions','Permissions for two agents',f'''<div class="permissions-visual diagram" role="img" aria-label="Both agents follow the owner’s accepted definition. Neither has permission to change the rule. Separate permissions let the coding agent edit code and run it on the agreed saved database copy. The reviewing agent may read the agreed copy, code and exported file, compare entry IDs and save a review. Giving an agent a job does not grant these permissions. Neither agent may accept the code on the owner’s behalf or release it to customers.">
<div class="meaning-anchor authority">{icon('book-open')}<div><strong>Every selected entry’s ID must be in the file.</strong><p>Neither agent has permission to change this rule.</p></div></div>
<div class="action-lanes">
<div class="action-lane"><div class="action-actor">{icon('bot')}<strong>Agent writing code</strong></div>
<div class="allowed-action">{icon('briefcase-business')}<span>Edit the code</span></div>
<div class="allowed-action">{icon('refresh-cw')}<span>Run on the agreed<br>database copy</span></div></div>
<div class="action-lane"><div class="action-actor">{icon('bot')}<strong>Agent reviewing it</strong></div>
<div class="allowed-action">{icon('database')}<span>Read the agreed copy,<br>code and exported file</span></div>
<div class="allowed-action">{icon('route')}<span>Compare IDs<br>and save the review</span></div></div>
</div>
<div class="use-boundary"><span class="no-use-mark" aria-hidden="true">×</span><strong>Neither has permission to release this to customers.</strong></div>
</div>''','Two jobs, two permission scopes'))

slides.append(slide(6,'conformance-page story-provenance','200 missing IDs',f'''<p class="fixture-line">Customer 1’s active database entries.</p>
<div class="trace-story diagram" role="img" aria-label="The code uses a database copy saved at one point in time to produce an exported file. The reviewing agent follows the accepted definition to select all active entries for Customer 1 from that copy. It checks each selected ID against the file. All 10000 selected IDs should appear, but only 9800 of those exact IDs do. The file is missing 200 selected IDs, so it fails this check. Keep the exact definition, database copy, code version and exported file with the review. This example describes no real agent run.">
<div class="trace-inputs"><div>{icon('database')}<strong>Database copy</strong></div><span class="trace-arrow" aria-hidden="true">→</span><div>{icon('briefcase-business')}<strong>Code used</strong></div><span class="trace-arrow" aria-hidden="true">→</span><div>{icon('database')}<strong>Exported file</strong></div></div>
<div class="trace-review"><div>{icon('bot')}<strong>Check every selected entry’s ID</strong></div><p class="authority">{icon('book-open')}Using the owner’s accepted definition</p></div>
<div class="coverage-values"><div><strong>10,000</strong><span>IDs selected from the database copy</span></div><div><strong>9,800</strong><span>of those IDs in the file</span></div></div>
<div class="coverage-track" aria-hidden="true"><span></span><span></span></div>
<div class="trace-gap"><strong>200 missing IDs</strong><span>The file fails the accepted definition.</span></div></div>''','Provenance'))

slides.append(slide(7,'delivery-memory story-memory','For the next agent',f'''<p class="memory-intro">The next agent starts with the saved review.</p>
<div class="memory-story diagram" role="img" aria-label="Each agent works in a temporary session. Its private short-term memory ends with that session. Work saved under project rules contributes to shared project history, called Project State. The history includes the exact definition and decisions, code version, database copy, exported file and review. A new agent receives selected records and a view of their connections, through Context and Ontology Views. It needs its own permissions. Agent outputs do not automatically become accepted project records.">
<div class="session-endpoints"><div>{icon('bot')}<strong>Coding session</strong></div><div>{icon('bot')}<strong>Review session</strong></div></div>
<div class="connector"><span>save work under the project’s rules</span><b aria-hidden="true">↓</b></div>
<div class="memory-records"><strong>Saved project history</strong><div class="record-grid"><div class="authority">{icon('book-open')}<span>Definition and decisions</span></div><div>{icon('briefcase-business')}<span>Code version</span></div><div class="provenance">{icon('database')}<span>Database copy and file</span></div><div>{icon('route')}<span>Review: 200 missing IDs</span></div></div></div>
<div class="connector"><span>choose records and how they connect</span><b aria-hidden="true">↓</b></div>
<div class="new-session">{icon('bot')}<strong>Agent continuing the work</strong></div></div>''','Project continuity'))

slides.append(slide(8,'delivery-lifecycle story-lifecycle','Before customer release',f'''<div class="definition-status authority">{icon('book-open')}<span>The definition is accepted. The code still needs work.</span></div>
<div class="code-timeline diagram" role="img" aria-label="The definition is accepted. The code still needs work. The code is still awaiting acceptance because its exported file is missing 200 selected entry IDs. A possible next step is to fix the code, run it again and review the new file. If the owner accepts that exact revised code version, the code becomes accepted. Releasing it to customers still requires separate permission. The dashed path shows possible later steps, not completed decisions.">
<div class="code-state current-code"><span class="state-point">{icon('briefcase-business')}</span><div><strong>Code awaiting acceptance</strong><p>200 selected IDs missing</p></div></div>
<div class="state-change"><span class="state-line" aria-hidden="true"></span><p>Run revised code and review the new file.<br>If the owner accepts this code version…</p></div>
<div class="code-state future-code"><span class="state-point">{icon('users')}</span><strong>Accepted code</strong></div>
<div class="state-change"><span class="state-line" aria-hidden="true"></span><p>Get separate permission to release it to customers</p></div>
<div class="code-state future-code"><span class="state-point">{icon('refresh-cw')}</span><strong>Released to customers</strong></div></div>''','Lifecycle'))

slides.append(slide(9,'release story-release','An open<br>company brain',f'''<img class="release-orb" src="assets/orb.webp" alt="">
<div class="governance-ring diagram" role="img" aria-label="Authority identifies who sets the meaning and rules, and who may act. Provenance traces which inputs, code and decisions led to a result. Lifecycle tracks the state of each record and the decisions needed to move it forward. All three connect around shared project knowledge.">
<svg viewBox="0 0 920 530" aria-hidden="true"><path d="M170 165L350 215M750 165L570 215M460 355V365"/></svg>
<div class="ring-lens authority">{icon('book-open')}<strong>Authority</strong><span>Who sets the rules</span></div>
<div class="ring-lens provenance">{icon('route')}<strong>Provenance</strong><span>How we got this result</span></div>
<div class="ring-center">{icon('database')}<strong>Shared project knowledge</strong></div>
<div class="ring-lens lifecycle">{icon('refresh-cw')}<strong>Lifecycle</strong><span>Where things stand</span></div></div>
''','Website release in preparation',False))

page=(ROOT/'index.html').read_text()
page=re.sub(r'<main>.*?</main>','<main>\n'+'\n\n'.join(slides)+'\n</main>',page,flags=re.S)
page=page.replace('Math.min(7,index)','Math.min(frames.length-1,index)').replace("next.disabled=current===7","next.disabled=current===frames.length-1").replace("+' / 8'","+' / '+frames.length").replace('>1 / 8<','>1 / 9<')
(ROOT/'index.html').write_text(page)
print('Rendered nine slides: overview, definition, acceptance, agent work, evidence, continuity and lifecycle.')
