"""Build a local, searchable review package; no approval or external write actions."""
import html
import json
from catalog import TYPES, RELATIONS, LIFECYCLES, EVALUATIONS, DERIVED, LIMITS
from support import ROOT, load, dump, binding

def build():
    tests=load(ROOT/'receipts/target-validation.json'); entries=load(ROOT/'registry.json')['entries']; rows=[]
    for entry in entries:
        target=entry['target_id']; name=target.split('.',1)[1]; folder=ROOT/'targets'/target; contract=load(folder/'contract.json'); family=entry['family']; normalized=contract['normalization_contract']
        if family=='artifact-type':
            behavior='Closed record fields, exact graph references and target-specific consistency checks.'
            proposal='Use these record fields and reference constraints for '+normalized['name']+' in an explicitly named scope.'
            details={'fields':TYPES[name]}
        elif family=='profile':
            behavior='Pure evaluation of valid and adverse inputs, with exact scope matching and no effect execution.'
            proposal='Use these exact proposed parameters and rules for '+normalized['name']+'. Review the states, limits or criteria before adoption.'
            details={'parameters':load(folder/'parameters.json'),'positive':load(folder/'fixtures/expected.json'),'adverse':load(folder/'fixtures/adverse/expected.json')}
        elif family=='relation-kind':
            behavior='Direction, endpoint kinds, reference closure, ownership/evidence fields and applicable graph checks.'
            proposal='Use this directed relation and endpoint contract; its presence grants no authority.'
            details={'source_kinds':contract['source_kinds'],'target_kinds':contract['target_kinds'],'direction':contract['direction'],'inverse_projection':contract['inverse_projection']}
        else:
            behavior='Deterministic projection from the bound graph, independent of input ordering; invalid source graphs are rejected.'
            proposal='Use this derived view for navigation within the supplied data; it remains non-authoritative.'
            details={'source_kinds':contract['source_kinds'],'relation_kinds':contract['relation_kinds'],'as_of':'2026-09-07T00:00:00Z' if name=='team-roster' else None}
        rows.append({'target_id':target,'family':family,'result':tests['targets'][target]['result'],'purpose':normalized.get('distinct_validation_purpose',normalized.get('name',target)),'what_adoption_would_mean':proposal,'implemented_checks':behavior,'limits':LIMITS[family],'details':details,'review_path':'targets/'+target+'/REVIEW.md','contract_path':'targets/'+target+'/contract.json','binding':binding(folder/('artifact.json' if family=='artifact-type' else 'contract.json'))})
    dump(ROOT/'review-index.json',{'schema_version':'cal-83-target-review/v1','authority_effect':'none','review_action':'read-only; no adoption recorded','validation':binding(ROOT/'receipts/validation.json'),'targets':rows})
    intro='''# Review the remaining 83 candidates

83 missing targets -> bounded implementations -> passing checks -> your adoption review.

All 83 requested targets are constructed as candidates: 26 Artifact Types, 25 profiles, 25 relation kinds and 7 derived views. The original ledger is now 13 admitted + 182 constructed candidates = 195, with zero scaffold-only targets. Construction is complete for this bounded reconstruction; admission and production integration are separate.

Start with [the searchable local review page](REVIEW.html), or use the target table below. Each entry links to its exact contract, examples, implemented checks and limits. [Validation](receipts/validation.json) and [per-target results](receipts/target-validation.json) bind the tested scope. The entire batch is snapshotted by manifest.json.

What you would approve:

- Artifact Types -> use the exact fields and reference rules for a named purpose.
- Profiles -> use the proposed states, criteria, limits and routing rules. The displayed parameters are new proposals, not inherited approval.
- Relation kinds -> use the specified direction, endpoint types and evidence requirements.
- Derived views -> use the selected source data and projection rules for navigation, with no authority granted by the view.

Your earlier instruction authorized construction and testing. This package contains no adoption decisions and does not publish, deploy, delete records, authenticate people or retire the sibling source repository.

## Boundaries worth reviewing first

- The 51-node, 25-edge integration graph is illustrative. Twenty-three support nodes are explicitly fixture-only placeholders for earlier record kinds; they do not prove real runs, receipts, people or grants. The 28 native records include two additional identity examples.
- Exact file hashes protect graph membership. Reference consistency does not prove that observations are true, owners are authentic or evidence is sufficient.
- Profile evaluations are pure previews. A supplied approval or gate boolean is not authenticated authorization. Publication performs no publication; retention performs no deletion.
- The proposed profiles have their own input contracts. Earlier frozen Policy, Gate and Evaluation carriers are preserved; applying these broader profiles to live workflows requires separate integration.
- Stable identity revisions and immutable run/observation checks are local checks. A real identity migration or accepted successor needs its own owner record.
- Team roster current/history uses an explicit as-of instant and half-open periods. No identity-link relation merges people or implies permission.
- Derived views are complete only relative to supplied records. The promotion queue is a navigation view of gates, evaluations, decisions and their links, not a readiness or approval decision.
- Source verification preserves 32 inherited lineage residues and the prior D53 layout exception. Product and Project meanings reuse admitted Lab Definitions; candidate meanings remain candidates.

## Reproduce the checks

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/candidates/0026-remaining-targets-review-batch/validate.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/candidates/0026-remaining-targets-review-batch/check.py graph evidence/migrations/cyberalchemy-v2-to-lab/candidates/0026-remaining-targets-review-batch/examples/graph-manifest.json
```

The CLI also provides profile, view and revision modes. Use --help for arguments. Results never execute the represented domain operation. Revalidation preserves predecessor bytes; generated receipt files may be refreshed inside this batch.

## Targets

| Target | Family | What to review |
|---|---|---|
'''
    for row in rows: intro+='| ['+row['target_id']+']('+row['review_path']+') | '+row['family']+' | '+row['what_adoption_would_mean']+' |\n'
    (ROOT/'REVIEW.md').write_text(intro)
    cards=[]
    for row in rows:
        cards.append('<details data-family="'+row['family']+'"><summary><strong>'+html.escape(row['target_id'])+'</strong> <span>'+row['result']+'</span></summary><p>'+html.escape(row['purpose'])+'</p><p><b>Adoption would mean:</b> '+html.escape(row['what_adoption_would_mean'])+'</p><p><b>Checks:</b> '+html.escape(row['implemented_checks'])+'</p><p><b>Limits:</b> '+html.escape(row['limits'])+'</p><pre>'+html.escape(json.dumps(row['details'],indent=2))+'</pre><p><a href="'+row['contract_path']+'">Exact contract</a> · <a href="'+row['review_path']+'">Review notes</a></p></details>')
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>83 candidate review</title><style>body{font:16px system-ui;max-width:1000px;margin:40px auto;padding:0 20px;background:#f6f8fb;color:#182337}h1{font-size:30px}input,select{padding:12px;font:inherit;margin:6px;border:1px solid #aab6c5;border-radius:6px}input{width:55%}details{background:white;margin:12px 0;padding:18px;border:1px solid #d7deea;border-radius:8px}summary{cursor:pointer}span{float:right;color:#187246}pre{overflow:auto;background:#f1f4f8;padding:12px}p{line-height:1.6}a{color:#185bb0}.note{border-left:4px solid #e0a22d;padding:12px;background:#fff8e7}</style><h1>Review 83 constructed candidates</h1><p>Exact inputs → candidate checks → review evidence → owner adoption</p><p><b>26 artifact types · 25 profiles · 25 relation kinds · 7 derived views</b></p><p class="note">Construction and tests do not admit these candidates. Fixtures do not prove real execution or authenticated authority. Profile settings are proposals. Start with the <a href="REVIEW.md">review boundaries</a>.</p><p><a href="receipts/validation.json">Validation evidence</a> · <a href="review-index.json">Machine-readable review index</a> · <a href="reconciliation.json">195-target ledger</a></p><label>Search <input id="q" placeholder="Target, field, policy or limitation"></label><select id="family"><option value="">All families</option>artifact-type</option><option>profile</option><option>relation-kind</option><option>derived-surface</option></select><p id="count"></p>'''
    page=page.replace('<option>artifact-type</option>','<option>artifact-type</option>').replace('All families</option>artifact-type</option>','All families</option><option>artifact-type</option>')
    page+=''.join(cards)+'''<script>const q=document.querySelector('#q'), f=document.querySelector('#family'), cards=[...document.querySelectorAll('details')];function filter(){let n=0;for(const c of cards){const show=(!f.value||c.dataset.family===f.value)&&c.textContent.toLowerCase().includes(q.value.toLowerCase());c.hidden=!show;if(show)n++;}document.querySelector('#count').textContent=n+' of 83 targets shown';}q.addEventListener('input',filter);f.addEventListener('change',filter);filter();</script></html>'''
    (ROOT/'REVIEW.html').write_text(page)
if __name__=='__main__': build()
