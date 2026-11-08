"""Build the website-styled investigation edition without changing older editions."""
from pathlib import Path
import hashlib
import html
import json
import shutil

ROOT = Path(__file__).resolve().parent
PARENT = ROOT.parent
BASE = PARENT / 'alternative-v2'
SITE = PARENT.parents[1] / 'source' / 'governance-lab-series'
shutil.copytree(BASE / 'assets', ROOT / 'assets', dirs_exist_ok=True)
for source, destination in [
    ('assets/kep/design-system.css', 'design-system.css'),
    ('assets/kep/cyberalchemy-lab-logo-light-v2.svg', 'logo.svg'),
    ('assets/kep/cyberalchemy-orb-frozen.webp', 'orb.webp'),
    ('assets/brain-medallions/core-v1.png', 'company-brain.png'),
]:
    shutil.copy2(SITE / source, ROOT / 'assets' / destination)

def icon(name):
    return f'<img src="assets/{name}.svg" alt="" aria-hidden="true">'

slides = [
    ('cover', 'Three governing lenses<br>for <em>Agentic work</em>', f'''
      <img class="orb" src="assets/orb.webp" alt="">
      <div class="cover-lenses diagram" role="img" aria-label="The three governing lenses apply together to the same work. Authority asks what governs meaning and action. Provenance asks where a record came from and how it was produced. Lifecycle asks what state the subject is in and which changes are permitted.">
        <div class="authority">{icon('book-open')}<strong>Authority</strong><span>What governs<br>meaning and action?</span></div>
        <div class="provenance">{icon('route')}<strong>Provenance</strong><span>Where did<br>this come from?</span></div>
        <div class="lifecycle">{icon('refresh-cw')}<strong>Lifecycle</strong><span>What can<br>change from here?</span></div>
      </div>'''),
    ('incident', 'Customer 1 reports<br>missing entries.', f'''
      <div class="incident-body diagram" role="img" aria-label="A fictional customer reports missing entries in a saved export shared for review. The investigation is open. Snapshot 1 is a database snapshot captured at one point in time. Export code v1 produced the saved file. The report is assessed later by Review 1 against Definition v1. The report itself does not establish the omission or its cause.">
        <div class="ticket-top"><strong>Customer 1</strong><span>File under review</span></div>
        <blockquote>“Some entries are missing<br>from our export.”</blockquote>
        <div class="work-line">{icon('briefcase-business')}<strong>Investigate the saved export.</strong></div>
        <div class="input-line"><div>{icon('database')}<strong>Snapshot 1</strong></div><b aria-hidden="true">→</b><div>{icon('briefcase-business')}<strong>Export code v1</strong></div><b aria-hidden="true">→</b><div>{icon('database')}<strong>Exported file 1</strong></div></div>
        <div class="snapshot-note"><strong>Snapshot 1</strong><span>Database entries saved at one point in time.</span></div>
      </div>'''),
    ('meaning', 'Authority over<br>meaning', f'''
      <div class="definition-body diagram" role="img" aria-label="The review must recover the governing meaning before assessing the incident. Definition v1 is the service owner’s accepted completeness definition. For this assessment, select all entries from Snapshot 1 whose customer is Customer 1 AND whose status is Active. The returned ID set must exactly equal the snapshot/customer/filter selection. All selected IDs must be present, and every returned ID must be in that selection. Value accuracy and duplicate detection remain separate. Acceptance of the definition proves no code conformance and grants no action permissions.">
        <div class="definition-heading">{icon('book-open')}<div><strong>Complete customer export v1</strong></div><span class="accepted">Accepted</span></div>
        <div class="criterion"><strong>A customer export is complete when its returned entry IDs match exactly the IDs selected from the fixed database snapshot by the declared customer and filters.</strong></div>
        <dl><div><dt>Source</dt><dd>Snapshot 1</dd></div><div><dt>Filter</dt><dd>Customer = Customer 1<br><b>AND</b> Status = Active</dd></div></dl>
        <div class="owner">{icon('users')}<div><strong>Service owner</strong><span>Accepts this rule as Definition v1.</span></div></div>
      </div>'''),
    ('permission', 'What each agent<br>is allowed to do', f'''
      <div class="permission-body diagram" role="img" aria-label="Jobs and permissions remain separate. The reviewing agent has scoped permission to inspect Snapshot 1, Export code v1 and the saved file, compare selected IDs and record Review 1. A coding agent may replay code on Snapshot 1, inspect the trace and prepare and test proposed changes. Fresh scoped permissions cover the later revised-code review. These permissions do not authorize changing Definition v1, accepting revised code or releasing it to customers. These are illustrative scoped grants for the story, not real approvals.">
        <div class="permission-columns"><div><div class="actor">{icon('bot')}<strong>Review agent</strong></div><ul><li>Inspect the named inputs.</li><li>Compare IDs and inspect traces.</li><li>Record the review.</li></ul></div><div><div class="actor">{icon('bot')}<strong>Coding agent</strong></div><ul><li>Prepare proposed changes.</li><li>Replay and test code<br>on Snapshot 1.</li></ul></div></div>
        <div class="boundary"><strong>Neither may</strong><div><span>× Change Definition v1</span><span>× Accept or release code</span></div></div>
      </div>'''),
    ('review', 'Provenance of<br>Review 1', f'''
      <div class="review-body diagram" role="img" aria-label="Review 1 links exact references to Definition v1, Snapshot 1, Export code v1 and its saved exported file. The links mean review references, not creation effects. The review derives all 10000 required IDs from Customer 1 entries with Active status in Snapshot 1 independently of the export and compares each ID with the file. 9800 exact required IDs appear and 200 are absent. Comparing returned IDs back against the required set finds zero IDs outside the selection. The omission is established for this file; its cause is not established. Counts summarize ID membership, not arbitrary row totals. The names map to fictional definition version 1, S1, candidate I1/build B1, E1 and R1. No real run or admission is asserted.">
        <div class="references"><div class="authority">{icon('book-open')}<strong>Definition v1</strong></div><div>{icon('database')}<strong>Snapshot 1</strong></div><div>{icon('briefcase-business')}<strong>Export code v1</strong></div><div>{icon('database')}<strong>Exported file 1</strong></div></div>
        <svg class="join" viewBox="0 0 900 76" preserveAspectRatio="none" aria-hidden="true"><path d="M112.5 0V28H787.5V0M337.5 0V28M562.5 0V28M450 28V70"/><path d="m439 56 11 14 11-14"/></svg>
        <div class="review-name">{icon('route')}<strong>Review 1</strong></div>
        <p class="method">Check for missing IDs and IDs outside the filter.</p>
        <div class="counts"><div><strong>10,000</strong><span>selected IDs</span></div><div><strong>9,800</strong><span>of those IDs found</span></div></div>
        <div class="coverage" aria-hidden="true"><span></span><span></span></div>
        <div class="result"><strong>200 missing IDs</strong><div class="selection-result"><span>Outside the filter</span><strong>0 IDs</strong></div><dl><div><dt>Export</dt><dd>Incomplete</dd></div><div><dt>Cause</dt><dd>Not established</dd></div></dl></div>
      </div>'''),
    ('cause', 'The last page<br>was never read.', f'''
      <div class="cause-body diagram" role="img" aria-label="In the fictional incident, Trace 1 links Snapshot 1 to Export code v1 and records a controlled replay. Filtering Customer 1 with Active status selects 10000 IDs, paged into 50 pages of 200 entries. A loop starting at page 1 continues only while page is less than 50, so it reads pages 1 to 49 and never requests page 50. That final page holds the exact missing IDs 9801 to 10000. The source of the diagnosis is the trace and code inspection, not a count difference alone. No real replay or code diagnosis is asserted.">
        <div class="trace-header">{icon('route')}<strong>Trace 1</strong><span>Recorded page requests<br>Snapshot 1 · Export code v1</span></div>
        <p class="page-scope">Customer 1 · Active: 50 pages of 200 entries.</p>
        <div class="page-reading"><div class="read-pages"><span>Pages</span><strong>1–49</strong><b>9,800 IDs read</b></div><div class="page-stop" aria-hidden="true">→<span>stops</span></div><div class="skipped-page"><span>Page</span><strong>50</strong><b>200 IDs unread</b></div></div>
        <div class="cause-rule">Export code v1 stops the loop<br>one page too early.</div>
      </div>'''),
    ('repair review', 'Export code v2<br>reads the last page.', f'''
      <div class="review-body diagram" role="img" aria-label="The fictional coding agent prepares Export code v2, which follows pagination until no next page remains. It reads pages 1 through 50 of the same filtered Snapshot 1 and produces Exported file 2. A separately permitted fresh Review 2 links unchanged Definition v1, Snapshot 1, exact Export code v2 and File 2. The selected and returned ID sets both contain IDs 1 to 10000, with zero missing and zero outside the selection. This passes the criterion for this snapshot only. It is not general code correctness or automatic owner acceptance. No real code, run or test result is asserted.">
        <div class="references"><div class="authority">{icon('book-open')}<strong>Definition v1</strong></div><div>{icon('database')}<strong>Snapshot 1</strong></div><div>{icon('briefcase-business')}<strong>Export code v2</strong></div><div>{icon('database')}<strong>Exported file 2</strong></div></div>
        <svg class="join" viewBox="0 0 900 76" preserveAspectRatio="none" aria-hidden="true"><path d="M112.5 0V28H787.5V0M337.5 0V28M562.5 0V28M450 28V70"/><path d="m439 56 11 14 11-14"/></svg>
        <div class="review-name">{icon('route')}<strong>Review 2</strong></div>
        <p class="method">Compare selected IDs with Exported file 2.</p>
        <div class="counts"><div><strong>10,000</strong><span>selected IDs</span></div><div><strong>10,000</strong><span>of those IDs found</span></div></div>
        <div class="fixed-result"><div><strong>0</strong><span>missing IDs</span></div><div><strong>0</strong><span>outside the filter</span></div></div>
        <div class="criterion-match">Matches Definition v1 for Snapshot 1.</div>
      </div>'''),
    ('lifecycle-page resolved', 'Lifecycle of the code<br>and the incident', f'''
      <div class="resolution-body diagram" role="img" aria-label="In the fictional resolution, Review 2 matches unchanged Definition v1 for Snapshot 1. Separate decisions follow. The authorized owner accepts exact Export code v2, the release owner grants scoped permission for corrected delivery to Customer 1, Customer 1 confirms the selected IDs in File 2, and the responsible incident owner records a closure decision for the reported omission. These are separate illustrative records, not consequences automatically granted by a passing review. They are not real approvals, release or closure. Other customer accounts and wider impact remain outside this example.">
        <div class="definition-state">{icon('book-open')}<strong>Definition v1 stays unchanged.</strong></div>
        <div class="resolution-path"><div><span class="resolution-point">{icon('route')}</span><p><strong>Review 2 matches Definition v1.</strong><span>Exact version: Export code v2</span></p></div><div><span class="resolution-point">{icon('users')}</span><p><strong>Service owner accepts code v2.</strong></p></div><div><span class="resolution-point">{icon('briefcase-business')}</span><p><strong>Release owner permits delivery.</strong><span>Customer 1 · Exported file 2</span></p></div><div><span class="resolution-point">{icon('database')}</span><p><strong>Customer 1 receives the file.</strong></p></div><div><span class="resolution-point">{icon('users')}</span><p><strong>Customer 1 confirms the result.</strong><span>All selected IDs are present.</span></p></div><div><span class="resolution-point">{icon('refresh-cw')}</span><p><strong>Incident owner records closure.</strong></p></div></div>
      </div>'''),
    ('continuity', 'The history stays<br>in the project.', f'''
      <div class="continuity-body diagram" role="img" aria-label="Machine agents work in temporary sessions. Their private short-term memory ends with the session. Records saved under project rules contribute to durable Project State. The next agent receives relevant Reviews 1 and 2, Trace 1, linked inputs and separate delivery/closure records through task-specific Context and Ontology Views, with separately checked current permissions. Private memory and permissions are not inherited and agent outputs are not automatically admitted.">
        <div class="sessions"><div>{icon('bot')}<strong>Review session</strong></div><div>{icon('bot')}<strong>Coding session</strong></div><span>Private memory ends with the session.</span></div>
        <div class="connector"><span>record under project rules</span><b aria-hidden="true">↓</b></div>
        <div class="project-history"><strong>Shared project records</strong><div>{icon('route')}<span>Trace 1, Reviews 1 and 2,<br>their inputs and the closure records</span></div></div>
        <div class="connector"><span>select context for the next task</span><b aria-hidden="true">↓</b></div>
        <div class="next-session">{icon('bot')}<div><strong>Next agent</strong><span>Relevant context · Current permissions</span></div></div>
      </div>'''),
    ('closing incident-record', 'The fix has a record.', f'''
      <div class="incident-lens-map diagram" role="img" aria-label="Customer 1's export incident sits at the center of three colored branches. Authority connects to accepted Definition v1 and separate scoped permissions. Provenance connects to Snapshot 1, Trace 1 and Reviews 1 and 2, which reference the exact code versions and files. Lifecycle connects to accepted code v2, delivered File 2 and the closed incident. The lines show three complementary views of the same subject, not causal flows between lenses or automatic grants. Customer confirmation and separate delivery and closure records remain in the preceding slide and exact fictional example.">
        <svg class="lens-links" viewBox="0 0 900 790" aria-hidden="true"><path class="authority-link" d="M450 205V235"/><path class="provenance-link" d="M362 448C332 505 210 495 210 555"/><path class="lifecycle-link" d="M538 448C568 505 690 495 690 555"/><circle cx="450" cy="360" r="125"/></svg>
        <div class="map-lens map-authority authority">{icon('book-open')}<h3>Authority</h3><div class="authority-records"><span>Definition v1</span><span>Scoped permissions</span></div></div>
        <div class="incident-hub">{icon('briefcase-business')}<strong>Customer 1</strong><span>Export incident</span></div>
        <div class="map-lens map-provenance provenance">{icon('route')}<h3>Provenance</h3><div><span>Snapshot 1 · Trace 1</span><span>Reviews 1 &amp; 2</span></div></div>
        <div class="map-lens map-lifecycle lifecycle">{icon('refresh-cw')}<h3>Lifecycle</h3><div><span>Code v2 accepted</span><span>File 2 delivered</span><span>Incident closed</span></div></div>
      </div>'''),
]

frames=[]
for number,(kind,title,body) in enumerate(slides,1):
    tag='h1' if number==1 else 'h2'
    frames.append(f'<div class="frame"'+(' hidden' if number>1 else '')+f'><section class="slide {kind}" aria-labelledby="slide-{number}"><header><img class="logo" src="assets/logo.svg" alt="CyberAlchemy Lab"></header><{tag} id="slide-{number}">{title}</{tag}>{body}<footer>{number:02d} / {len(slides):02d}</footer></section></div>')
viewer='''<script>
const frames=[...document.querySelectorAll('.frame')];let current=0;const previous=document.querySelector('#previous'),next=document.querySelector('#next'),position=document.querySelector('#position');
function size(){for(const f of frames){const w=f.clientWidth||Math.min(innerWidth-32,700);f.style.height=(w*1.25)+'px';f.firstElementChild.style.transform='scale('+(w/1080)+')';}}
function show(n){current=Math.max(0,Math.min(frames.length-1,n));frames.forEach((f,i)=>f.hidden=i!==current);previous.disabled=current===0;next.disabled=current===frames.length-1;position.textContent=(current+1)+' / '+frames.length;size();}
previous.addEventListener('click',()=>show(current-1));next.addEventListener('click',()=>show(current+1));addEventListener('resize',size);addEventListener('keydown',e=>{if(e.key==='ArrowRight')show(current+1);if(e.key==='ArrowLeft')show(current-1);});show(0);
</script>'''
(ROOT/'index.html').write_text('''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Three governing lenses · Investigation edition</title><link rel="icon" href="assets/logo.svg"><link rel="stylesheet" href="assets/design-system.css"><link rel="stylesheet" href="slides.css"></head><body><nav class="viewer" aria-label="Slideshow controls"><a href="../compare-v3.html">Compare versions</a><div><button id="previous" aria-label="Previous slide">←</button><span id="position" aria-live="polite">1 / 10</span><button id="next" aria-label="Next slide">→</button><a href="cyberalchemy-governance-investigation.pdf">Download PDF</a></div></nav><main>'''+''.join(frames)+'</main>'+viewer+'</body></html>')

mapping=[('Opening',1,1),('Incident and context',2,2),('Authority: meaning',3,3),('Authority: permissions',4,4),('Provenance: Review 1',5,5),('Cause: Trace 1',5,6),('Fix and fresh review: Export code v2',5,7),('Lifecycle and incident closure',7,8),('Project continuity after closure',6,9),('Three lenses on the incident record',8,10)]
options=''.join(f'<option value="{i}">{html.escape(name)}</option>' for i,(name,_,_) in enumerate(mapping))
captions=[html.escape((BASE/'post.txt').read_text()),html.escape((ROOT/'post.txt').read_text())]
(PARENT/'compare-v3.html').write_text('''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Carousel comparison · Website investigation version</title><link rel="icon" href="investigation-v3/assets/logo.svg"><link rel="stylesheet" href="investigation-v3/assets/design-system.css"><link rel="stylesheet" href="investigation-v3/compare.css"></head><body><header><img src="investigation-v3/assets/logo.svg" alt="CyberAlchemy Lab"><h1>Compare the investigation version</h1><p>The same customer example, now followed through diagnosis, a fresh review and separate closure decisions.</p><nav><a href="alternative-v2/index.html">Version 2</a><a href="investigation-v3/index.html">Investigation slideshow</a><a href="#captions">Compare captions</a><a href="compare-v2.html">Original comparison</a></nav></header><main><section class="controls" aria-label="Choose a story section"><button id="previous" aria-label="Previous section">←</button><label for="section">Story section</label><select id="section">'''+options+'''</select><button id="next" aria-label="Next section">→</button><span id="count" aria-live="polite"></span></section><section class="pair"><article><h2>Version 2</h2><a href="alternative-v2/cyberalchemy-governance-teaser-v2.pdf">Download PDF</a><div id="old-images" class="images"></div></article><article><h2>Website investigation version</h2><a href="investigation-v3/cyberalchemy-governance-investigation.pdf">Download PDF</a><div id="new-images" class="images"></div></article></section><section id="captions"><h2>Captions</h2><div class="pair"><article><h3>Version 2</h3><p class="caption">'''+captions[0]+'''</p><a href="alternative-v2/post.txt">Caption file</a></article><article><h3>Investigation version</h3><p class="caption">'''+captions[1]+'''</p><a href="investigation-v3/post.txt">Caption file</a></article></div></section></main><script>
const mapping='''+json.dumps(mapping)+''';let active=0;const select=document.querySelector('#section'),previous=document.querySelector('#previous'),next=document.querySelector('#next');
function picture(src,label){const a=document.createElement('a');a.href=src;a.target='_blank';a.rel='noopener';const img=document.createElement('img');img.src=src;img.alt=label;a.append(img);return a;}
function show(n){active=Math.max(0,Math.min(mapping.length-1,n));select.value=active;const [name,oldId,newId]=mapping[active];document.querySelector('#old-images').replaceChildren(picture('alternative-v2/slide-'+oldId+'.png','Version 2: '+name));document.querySelector('#new-images').replaceChildren(picture('investigation-v3/slide-'+newId+'.png','Investigation version: '+name));previous.disabled=active===0;next.disabled=active===mapping.length-1;document.querySelector('#count').textContent=(active+1)+' / '+mapping.length;}
select.addEventListener('change',()=>show(Number(select.value)));previous.addEventListener('click',()=>show(active-1));next.addEventListener('click',()=>show(active+1));show(0);
</script></body></html>''')

style_sources=['assets/kep/design-system.css','assets/research-site.css','assets/company-brain-map.css','assets/kep/cyberalchemy-lab-logo-light-v2.svg','assets/kep/cyberalchemy-orb-frozen.webp','assets/brain-medallions/core-v1.png']
preserved={str(path.relative_to(PARENT)):hashlib.sha256(path.read_bytes()).hexdigest() for folder in [BASE] for path in folder.rglob('*') if path.is_file()}
for name in ['index.html','post.txt','cyberalchemy-governance-teaser.pdf','compare-v2.html']:
    preserved[name]=hashlib.sha256((PARENT/name).read_bytes()).hexdigest()
production={'title':'Three governing lenses for Agentic work','edition':'Website-style resolved investigation v3','standing':'Local fictional content. No real report, grant, agent run, review, acceptance or customer release is asserted.','audience':'Founders and AI teams','slides':len(slides),'dimensions_px':[1080,1350],'exact_example':'example.json','reader_names':{'Definition v1':'example.definition.complete-customer-export@1','Snapshot 1':'S1','Export code v1':{'candidate':'I1','build':'B1'},'Exported file 1':'E1','Review 1':'R1','Trace 1':'T1','Export code v2':{'candidate':'I2','build':'B2'},'Exported file 2':'E2','Review 2':'R2'},'story':[name for name,_,_ in mapping],'definition_revision':{'term':'Complete customer export v1','criterion':'Returned IDs exactly match the declared snapshot/customer/filter selection','scope':'Adds eligibility to ID coverage in a separate fictional example. Original comparisons and canonical records unchanged.'},'semantic_boundaries':['Definition acceptance supplies meaning within scope and grants no action permissions.','Assignments and permissions are separate.','Review 1 establishes the omission. Trace 1 supplies the separate fictional diagnosis. Review 2 assesses exact new code and output against the unchanged criterion.','Private memory ends with the session. Project records, selected views and current permissions support continuation.','Fresh review, code acceptance, scoped release permission, customer confirmation and incident closure are separate fictional records.','Review outputs and agent work do not become admitted project state automatically.'],'style_sources':{str((SITE/name).relative_to(PARENT.parents[2])):hashlib.sha256((SITE/name).read_bytes()).hexdigest() for name in style_sources},'preserved_hashes':preserved,'reader_evidence':'Editorial and browser rendering review only; no new-reader observations.','comparison':'../compare-v3.html'}
(ROOT/'production.json').write_text(json.dumps(production,indent=2,ensure_ascii=False)+'\n')
print('Built ten website-style investigation slides with cause, fresh review and closure.')
