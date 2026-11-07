from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parents[1]

import json
FORMS = json.loads((ROOT/'hackathon-forms.json').read_text(encoding='utf-8'))

def block(label, value, key):
    return (f'<div class="form-copy-block"><h4>{escape(label)}</h4>'
            f'<pre id="{key}">{escape(value)}</pre>'
            f'<button type="button" data-copy-target="{key}">Copy text</button></div>')

parts = ['<!-- FORM-COPY-START -->', '<section id="form-copy"><h2>Copy-ready form content</h2>',
         '<p>Your registration form registers a person; project submission is separate. Use the exact text below, one field at a time. Agreements are required checkboxes with one option. Eligibility is confirmed as 18+; include the age acknowledgment.</p>',
         '<p>Jump to: <a href="#registration-copy">Registration</a> · <a href="#submission-copy">Project submission</a> · <a href="#voting-copy">Voting</a> · <a href="FORMS-COPY.txt" download>Download all text</a></p>']
plain = ['CYBERALCHEMY LAB × CRAFT HACKATHON — FORM CONTENT',
         'Rules v1.1: registration October 16 at 18:00 to October 23 at 23:59:59; project month October 24 at 00:00 to November 23 at 23:59:59; voting November 24 at 12:00 to November 25 at 18:00; final results November 25 at 23:59:59, 2026. Brasília time (UTC-3).',
         'Individual new projects only. One project in one category. One final ballot with at most one vote per category.',
         'Eligibility: 18+. Prize: reimbursement up to US$200 for one month of ChatGPT Pro at the US$200 tier. Organizer contact: hello@cyberalchemize.com. Replace public-link and project-title placeholders before publishing.']

for form in FORMS:
    parts.append(f'<section id="{form["id"]}"><h3>{escape(form["label"])}</h3>')
    parts.append(block('Form title', form['title'], form['id'] + '-title'))
    parts.append(block('Form description', form['description'], form['id'] + '-description'))
    plain += ['\n' + '=' * 60, form['label'].upper(), '=' * 60, '\nFORM TITLE', form['title'], '\nFORM DESCRIPTION', form['description']]
    for i, (title, kind, helptext, options) in enumerate(form['questions'], 1):
        parts.append(f'<div class="form-copy-question"><p><strong>Question {i}</strong> · {escape(kind)}</p>')
        parts.append(block('Question title', title, f'{form["id"]}-q{i}-title'))
        parts.append(block('Question description', helptext, f'{form["id"]}-q{i}-help'))
        if options:
            parts.append(block('Answer option(s)', options, f'{form["id"]}-q{i}-options'))
        parts.append('</div>')
        plain += [f'\nQUESTION {i} — {kind}', title, 'Description: ' + helptext]
        if options:
            plain += ['Answer option(s):', options]
    parts.append(block('Confirmation message', form['confirmation'], form['id'] + '-confirmation'))
    parts.append('<h4>Form settings</h4><ul>' + ''.join(f'<li>{escape(s)}</li>' for s in form['settings']) + '</ul></section>')
    plain += ['\nCONFIRMATION MESSAGE', form['confirmation'], '\nSETTINGS'] + ['- ' + s for s in form['settings']]
parts += ['</section>', '''<style>
#form-copy{border-block:1px solid #d8d1c4;margin-top:2rem;padding-bottom:2rem}
#form-copy section{padding-top:1.5rem}#form-copy h3{font:400 1.8rem/1.3 Georgia,serif;border-top:1px solid #d8d1c4;padding-top:1.5rem}
.form-copy-block{margin-bottom:1.2rem}.form-copy-block h4{margin:.4rem 0;font-size:.9rem;color:#625e57}
.form-copy-block pre{white-space:pre-wrap;overflow-wrap:anywhere;line-height:1.65;font-family:inherit;font-size:.95rem}
.form-copy-block button{font-size:.85rem;padding:.4rem .8rem}.form-copy-question{padding:1rem 0;border-top:1px solid #d8d1c4}
@media print{.form-copy-block button{display:none}.form-copy-block pre{background:none;border-left:2px solid #d8d1c4}}
</style>
<script>
document.addEventListener('click',async function(event){
  const button=event.target.closest('[data-copy-target]');if(!button)return;
  const target=document.getElementById(button.dataset.copyTarget);const text=target.textContent;
  try{
    if(navigator.clipboard&&window.isSecureContext){await navigator.clipboard.writeText(text);}
    else{const input=document.createElement('textarea');input.value=text;input.style.position='fixed';input.style.opacity='0';document.body.append(input);input.select();const copied=document.execCommand('copy');input.remove();if(!copied)throw new Error('copy unavailable');}
    button.textContent='Copied';setTimeout(()=>button.textContent='Copy text',1500);
  }catch(error){const range=document.createRange();range.selectNodeContents(target);const selected=getSelection();selected.removeAllRanges();selected.addRange(range);button.textContent='Text selected — copy manually';}
});
</script>''', '<!-- FORM-COPY-END -->']

guide = ROOT / 'GOOGLE-FORMS-SETUP.html'
raw = guide.read_text()
start = raw.find('<!-- FORM-COPY-START -->')
if start >= 0:
    end = raw.index('<!-- FORM-COPY-END -->', start) + len('<!-- FORM-COPY-END -->')
    raw = raw[:start] + raw[end:]
raw = raw.replace('<h2>1. Create the registration form.</h2>', '\n'.join(parts) + '\n<h2>1. Create the registration form.</h2>', 1)
guide.write_text(raw)
(ROOT / 'FORMS-COPY.txt').write_text('\n'.join(plain) + '\n')
print(f'Added copy-ready text for {len(FORMS)} forms, {sum(len(f["questions"]) for f in FORMS)} questions, and {len(FORMS)} confirmation messages.')
