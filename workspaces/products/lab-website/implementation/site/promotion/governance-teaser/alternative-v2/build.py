"""Build a separate carousel and its comparison page. Current edition stays intact."""
from pathlib import Path
import hashlib
import html
import json
import shutil

ROOT = Path(__file__).resolve().parent
CURRENT = ROOT.parent
shutil.copytree(CURRENT / 'assets', ROOT / 'assets', dirs_exist_ok=True)

def icon(name):
    return f'<img src="assets/{name}.svg" alt="" aria-hidden="true">'

slides = [
    ('opening', 'Three governing lenses<br>for Agentic work', f'''
    <img class="orb" src="assets/orb.webp" alt="">
    <div class="opening-lenses diagram" role="img" aria-label="Authority governs meaning and permissions. Provenance traces the inputs and review history. Lifecycle tracks each record’s state and permitted changes. These three governing lenses remain distinct and apply together to agentic work.">
      <div class="authority-lens">{icon('book-open')}<strong>Authority</strong><span>Meaning and permissions</span></div>
      <div class="provenance-lens">{icon('route')}<strong>Provenance</strong><span>Inputs and review history</span></div>
      <div class="lifecycle-lens">{icon('refresh-cw')}<strong>Lifecycle</strong><span>State and permitted changes</span></div>
    </div>'''),
    ('selection', 'Customer 1 needs<br>an export.', f'''
    <div class="selection-body diagram" role="img" aria-label="Use the full database snapshot captured at one point in time. Select every entry whose customer is Customer 1 AND whose status is Active. Both filters apply across the full snapshot. The three rows below are only an excerpt. Entry 1 qualifies; entry 10001 is inactive and entry 10021 belongs to Customer 2, so they do not qualify. Every selected entry ID must be in the file. This definition checks required ID presence, not value accuracy, duplicates or extra IDs. Definition v1 is proposed here; owner acceptance follows on the next slide.">
      <p class="copy-line"><b>Snapshot 1:</b> database entries saved at one time.</p>
      <div class="filter"><div><span>Customer</span><strong>Customer 1</strong></div><b>AND</b><div><span>Status</span><strong>Active</strong></div></div>
      <p class="excerpt">Both filters must match. Sample entries:</p>
      <table><thead><tr><th>Unique ID</th><th>Customer</th><th>Status</th><th></th></tr></thead><tbody>
        <tr class="match"><td>1</td><td>Customer 1</td><td>Active</td><td>✓ Include</td></tr>
        <tr><td>10001</td><td>Customer 1</td><td>Inactive</td><td>×</td></tr>
        <tr><td>10021</td><td>Customer 2</td><td>Active</td><td>×</td></tr>
      </tbody></table>
      <div class="down" aria-hidden="true">↓</div>
      <div class="definition-line">{icon('book-open')}<div><span class="definition-version">Definition v1 · “Complete”</span><strong>Every selected ID<br>must be in the file.</strong></div></div>
    </div>'''),
    ('authority', 'Authority over<br>meaning', f'''
    <div class="authority-body diagram" role="img" aria-label="The service owner is authorized to set the service’s requirements. The owner accepts Definition v1 for Customer 1, Active status and the database snapshot. That accepted definition governs complete for both agents. It grants no action permissions and proves no code conformance.">
      <div class="owner">{icon('users')}<div><strong>Service owner</strong><span>Sets the requirements</span></div></div>
      <div class="accept"><span>accepts</span><b aria-hidden="true">↓</b></div>
      <div class="document"><div class="document-title">{icon('book-open')}<strong>Export completeness · v1</strong></div><p>Customer 1 · Active entries</p><p>Every selected ID in the file</p></div>
      <svg class="fork" viewBox="0 0 900 105" aria-hidden="true"><path d="M450 0V35H215V95M450 35H685V95"/><path d="m204 81 11 14 11-14m448 0 11 14 11-14"/></svg>
      <div class="actors"><div>{icon('bot')}<strong>Write code</strong></div><div>{icon('bot')}<strong>Check the file</strong></div></div>
    </div>'''),
    ('permissions', 'What each agent<br>is allowed to do', f'''
    <div class="permissions-body diagram" role="img" aria-label="The coding agent and reviewing agent have separate permissions, apart from their job assignments. The coding agent may edit proposed code and run it on the agreed database snapshot. The reviewer may inspect the agreed snapshot, code and file, compare IDs and save a review. Neither may change the accepted definition, accept the code or release it to customers under these permissions.">
      <div class="permissions-grid">
        <div class="permission-column"><div class="agent">{icon('bot')}<strong>Coding agent</strong></div><ul><li>{icon('briefcase-business')}<span>Edit code</span></li><li>{icon('refresh-cw')}<span>Run on Snapshot 1</span></li></ul></div>
        <div class="permission-column"><div class="agent">{icon('bot')}<strong>Reviewing agent</strong></div><ul><li>{icon('database')}<span>Read Snapshot 1,<br>code and file</span></li><li>{icon('route')}<span>Compare IDs<br>and save the review</span></li></ul></div>
      </div>
      <div class="excluded"><span>Neither agent has permission to</span><div><p><b aria-hidden="true">×</b> Change the definition</p><p><b aria-hidden="true">×</b> Accept or release code</p></div></div>
    </div>'''),
    ('review', 'Provenance of<br>Review 1', f'''
    <div class="review-body diagram" role="img" aria-label="Review 1 links four exact records: accepted Definition v1, Snapshot 1, Export code v1 and its exported file. These are references used by the review, not a sequence in which one record creates another. The reviewer uses Definition v1 to select every Customer 1 entry with Active status from the full fixed Snapshot 1, then checks every selected ID against the saved file produced by Export code v1. Of 10000 selected IDs, 9800 exact IDs appear and 200 are missing. The export is incomplete under Definition v1. Snapshot 1 names fictional S1; Export code v1 names candidate I1 and build B1; the file is E1; Review 1 names R1. No real run or admission is asserted.">
      <div class="review-references">
        <div class="rule-reference">{icon('book-open')}<strong>Definition v1</strong></div>
        <div>{icon('database')}<strong>Snapshot 1</strong></div>
        <div>{icon('briefcase-business')}<strong>Export code v1</strong></div>
        <div>{icon('database')}<strong>Exported file</strong></div>
      </div>
      <svg class="reference-join" viewBox="0 0 900 80" preserveAspectRatio="none" aria-hidden="true"><path d="M112.5 0V30H787.5V0M337.5 0V30M562.5 0V30M450 30V75"/><path d="m439 61 11 14 11-14"/></svg>
      <div class="linked-review">{icon('route')}<strong>Review 1</strong></div>
      <p class="review-method">Check every selected ID against the file.</p>
      <div class="result-counts"><div><strong>10,000</strong><span>selected IDs</span></div><div><strong>9,800</strong><span>of those IDs found</span></div></div>
      <div class="coverage" aria-hidden="true"><span></span><span></span></div>
      <div class="missing"><strong>200</strong><span>missing IDs</span><b>Export: incomplete</b></div>
    </div>'''),
    ('continuity', 'The next agent<br>gets the history', f'''
    <div class="continuity-body diagram" role="img" aria-label="Coding and reviewing agents are temporary sessions. Their private short-term memory ends with the session. Under project recording rules, the exact definition, input snapshot, code version and failed review contribute to shared Project State. A new agent receives selected relevant records and their connections through Context and Ontology Views, with new permissions. Neither private memory nor permissions are inherited; agent outputs are not automatically accepted project records.">
      <div class="temporary"><div>{icon('bot')}<strong>Coding session</strong></div><div>{icon('bot')}<strong>Review session</strong></div><span>Private memory ends with each session.</span></div>
      <div class="save-link"><span>save under project rules</span><b aria-hidden="true">↓</b></div>
      <div class="history"><strong>Project history</strong><div class="history-handoff">{icon('route')}<span>Review 1 + its linked records</span></div></div>
      <div class="save-link"><span>select for the next task</span><b aria-hidden="true">↓</b></div>
      <div class="next-agent">{icon('bot')}<div><strong>Next agent</strong><span>Selected history · New permissions</span></div></div>
    </div>'''),
    ('release', 'Lifecycle of<br>the export code', f'''
    <div class="release-body diagram" role="img" aria-label="Definition v1 is accepted but Export code v1 is awaiting acceptance and its file is missing 200 selected IDs. Definition and code retain separate lifecycle states. The dotted path is conditional: revise and run code, review the new file and seek owner acceptance of that exact version. Acceptance of code does not grant release permission. Only separately permitted release would put code into customer use. No later transition has happened in this example.">
      <div class="definition-state">{icon('book-open')}<strong>Definition v1: accepted</strong></div>
      <div class="now"><strong>Export code v1: pending</strong><span>200 IDs missing</span></div>
      <div class="future-path">
        <div class="gate">{icon('refresh-cw')}<div><strong>Revise and review.</strong><span>Run new code. Check the new file.</span></div></div>
        <div class="gate">{icon('users')}<div><strong>If the owner accepts the new version…</strong><span>Accepted code</span></div></div>
        <div class="gate">{icon('briefcase-business')}<div><strong>If release is separately permitted…</strong><span>Customer use</span></div></div>
      </div>
    </div>'''),
    ('closing', 'An open<br>company brain', f'''
    <img class="orb" src="assets/orb.webp" alt="">
    <div class="closing-body diagram" role="img" aria-label="CyberAlchemy Lab connects three distinct governance axes around shared project records. Authority identifies the admitted definitions, rules and permissions governing the work. Provenance traces which database snapshot, code and review produced a result. Lifecycle tracks each record’s state, acceptance and permitted changes. These lenses do not replace one another.">
      <div class="lens authority-lens">{icon('book-open')}<div><strong>Authority</strong><span>Definition v1 · Separate permissions</span></div></div>
      <div class="lens provenance-lens">{icon('route')}<div><strong>Provenance</strong><span>Review 1 and its linked records</span></div></div>
      <div class="lens lifecycle-lens">{icon('refresh-cw')}<div><strong>Lifecycle</strong><span>Definition v1 accepted · Export code v1 pending</span></div></div>
    </div>'''),
]

frames = []
for number, (kind, title, body) in enumerate(slides, 1):
    tag = 'h1' if number == 1 else 'h2'
    frames.append(f'''<div class="frame"{' hidden' if number > 1 else ''}><section class="slide {kind}" aria-labelledby="slide-{number}"><header><img class="logo" src="assets/logo.svg" alt="CyberAlchemy Lab"></header><{tag} id="slide-{number}">{title}</{tag}>{body}<footer>{number:02d} / {len(slides):02d}</footer></section></div>''')

viewer = '''<script>
const frames=[...document.querySelectorAll('.frame')];let current=0;
const previous=document.querySelector('#previous'),next=document.querySelector('#next'),position=document.querySelector('#position');
function size(){for(const frame of frames){const w=frame.clientWidth||Math.min(innerWidth-32,700);frame.style.height=(w*1.25)+'px';frame.firstElementChild.style.transform='scale('+(w/1080)+')';}}
function show(n){current=Math.max(0,Math.min(frames.length-1,n));frames.forEach((f,i)=>f.hidden=i!==current);previous.disabled=current===0;next.disabled=current===frames.length-1;position.textContent=(current+1)+' / '+frames.length;size();}
previous.addEventListener('click',()=>show(current-1));next.addEventListener('click',()=>show(current+1));addEventListener('resize',size);addEventListener('keydown',e=>{if(e.key==='ArrowRight')show(current+1);if(e.key==='ArrowLeft')show(current-1);});show(0);
</script>'''
(ROOT / 'index.html').write_text('''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Three governing lenses for Agentic work · CyberAlchemy Lab</title><link rel="icon" href="assets/logo.svg"><link rel="stylesheet" href="slides.css"></head><body><nav class="viewer" aria-label="Slideshow controls"><a href="../compare-v2.html">Compare versions</a><div><button id="previous" aria-label="Previous slide">←</button><span id="position" aria-live="polite">1 / 8</span><button id="next" aria-label="Next slide">→</button><a href="cyberalchemy-governance-teaser-v2.pdf">Download PDF</a></div></nav><main>'''+'\n'.join(frames)+'</main>'+viewer+'</body></html>')

mapping = [
    ('Opening', [1], 1), ('Request and definition', [2, 3], 2),
    ('Authority: meaning', [4], 3), ('Authority: permissions', [5], 4),
    ('Provenance: failed review', [6], 5), ('Provenance: next agent', [7], 6),
    ('Lifecycle: customer release', [8], 7), ('Closing', [9], 8),
]
options = ''.join(f'<option value="{i}">{html.escape(name)}</option>' for i,(name,_,_) in enumerate(mapping))
current_caption = html.escape((CURRENT / 'post.txt').read_text())
new_caption = html.escape((ROOT / 'post.txt').read_text())
comparison = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Carousel comparison · CyberAlchemy Lab</title><link rel="stylesheet" href="alternative-v2/compare.css"><link rel="icon" href="assets/logo.svg"></head><body><header><img src="assets/logo.svg" alt="CyberAlchemy Lab"><h1>Compare the two carousels</h1><p>The same example, with a different pace and visual structure.</p><nav><a href="index.html">Current slideshow</a><a href="alternative-v2/index.html">New slideshow</a><a href="#captions">Compare captions</a></nav></header><main><section class="controls" aria-label="Choose a story section"><button id="previous" aria-label="Previous section">←</button><label for="section">Story section</label><select id="section">'''+options+'''</select><button id="next" aria-label="Next section">→</button><span id="count" aria-live="polite"></span></section><section class="pair"><article><h2>Current version <small>9 slides</small></h2><a href="cyberalchemy-governance-teaser.pdf">Download PDF</a><div id="current-images" class="images"></div></article><article><h2>New version <small>8 slides</small></h2><a href="alternative-v2/cyberalchemy-governance-teaser-v2.pdf">Download PDF</a><div id="new-images" class="images"></div></article></section><section id="captions"><h2>Captions</h2><div class="pair"><article><h3>Current</h3><p class="caption">'''+current_caption+'''</p><a href="post.txt">Caption file</a></article><article><h3>New</h3><p class="caption">'''+new_caption+'''</p><a href="alternative-v2/post.txt">Caption file</a></article></div></section></main><script>
const mapping='''+json.dumps(mapping)+''';let active=0;const select=document.querySelector('#section'),previous=document.querySelector('#previous'),next=document.querySelector('#next');
function picture(src,label){const a=document.createElement('a');a.href=src;a.target='_blank';a.rel='noopener';const img=document.createElement('img');img.src=src;img.alt=label;a.append(img);return a;}
function show(n){active=Math.max(0,Math.min(mapping.length-1,n));select.value=active;const [name,oldIds,newId]=mapping[active];const old=document.querySelector('#current-images'),fresh=document.querySelector('#new-images');old.replaceChildren();fresh.replaceChildren();for(const id of oldIds)old.append(picture('slide-'+id+'.png','Current slide '+id+': '+name));fresh.append(picture('alternative-v2/slide-'+newId+'.png','New slide '+newId+': '+name));previous.disabled=active===0;next.disabled=active===mapping.length-1;document.querySelector('#count').textContent=(active+1)+' / '+mapping.length;}
select.addEventListener('change',()=>show(Number(select.value)));previous.addEventListener('click',()=>show(active-1));next.addEventListener('click',()=>show(active+1));show(0);
</script></body></html>'''
(CURRENT / 'compare-v2.html').write_text(comparison)

original_files = ['build_visual.py', 'index.html', 'slides.css', 'post.txt', 'capability-example.json', 'production.json', 'export.json', 'cyberalchemy-governance-teaser.pdf', 'cyberalchemy-governance-teaser-kit.zip']
production = {
    'title': 'Three governing lenses for Agentic work', 'edition': 'Separate eight-slide alternative', 'standing': 'Local fictional presentation. No real decisions, runs, results or release are asserted.',
    'audience': 'Founders and AI teams', 'format_px': [1080, 1350], 'slides': len(slides),
    'story': [name for name,_,_ in mapping],
    'reader_names': {'Definition v1': 'example.definition.id-complete-export@1', 'Snapshot 1': 'S1', 'Export code v1': {'candidate': 'I1', 'build': 'B1'}, 'Exported file': 'E1', 'Review 1': 'R1'},
    'review_links': ['Definition v1', 'Snapshot 1', 'Export code v1', 'Exported file'],
    'clarity_revision': {'definition': 'v1 shown before owner acceptance and named in review and lifecycle', 'snapshot': 'Database snapshot explained once, then referenced consistently', 'provenance': 'One review trail; continuity shows handoff rather than repeating the record list', 'scope': 'Exact fictional case and formal records unchanged'},
    'lens_alignment': {'authority': [3, 4], 'provenance': [5, 6], 'lifecycle': [7], 'closing': 'All lenses applied to the same Customer 1 export', 'boundary': 'No formal model changes; conditional code acceptance and release remain separate'},
    'changes': ['New copy and layouts throughout', 'Request and explicit AND filter combined', 'Definition shown before owner acceptance', 'Separate agent permissions', 'Exact ID membership review', 'Shared history before possible release', 'No bottom commentary or release CTA on slides'],
    'exact_example': '../capability-example.json',
    'original_file_hashes': {name: hashlib.sha256((CURRENT/name).read_bytes()).hexdigest() for name in original_files},
    'comparison': '../compare-v2.html', 'reader_evidence': 'Editorial and browser review; no first-time-reader observations.',
    'assets': 'Existing KEP brand assets and licensed Lucide icons copied locally.',
}
(ROOT / 'production.json').write_text(json.dumps(production, indent=2, ensure_ascii=False)+'\n')
print('Built eight new slides and the comparison page; current edition unchanged.')
