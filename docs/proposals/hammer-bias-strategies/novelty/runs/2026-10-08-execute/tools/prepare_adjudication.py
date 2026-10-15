#!/usr/bin/env python3
"""Encode declared disputes using the original bounded adjudicator instructions."""
import argparse,json,hashlib,datetime
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=argparse.ArgumentParser();a.add_argument('phase');a.add_argument('case');q=a.parse_args();phase=q.phase;case=q.case
d=json.loads((R/f'reports/{phase}-{case}-disagreements.json').read_text());assert d['disputed_pairs']>0
for j in ['J1','J2']:
 lock=json.loads((R/f'receipts/review-{phase}-{case}-{j}-lock.json').read_text());assert lock['native_terminal_observed'] and lock['output_sha256']==sha(R/f'reviews/{phase}-{case}-{j}.json')
n=sum(len(p['raw']) for p in d['pair_disagreements']);posts=[{'packet_id':p['packet_id'],'field':x['field']} for p in d['pair_disagreements'] for x in p.get('post',[])]
paths=[R/f'cases/{case}.json',R/f'archives/{case}.json',R/f'reports/{phase}-{case}-disagreements.json']+[R/f'reviews/{phase}-{case}-{j}.json' for j in ['J1','J2']]+sorted((R/f'blinded/{phase}/{case}').glob(f'{case}-P*.json'))
files=[{'path':str(p),'sha256':sha(p)} for p in paths]
txt=(R/'prompts/adjudicator.txt').read_text()+f'''
Operational scope: {phase}/{case}; {d['disputed_pairs']} disputed pairs, {n} disputed raw rows, {d['raw_count']-n} agreed raw rows and {len(posts)} post-field disagreements. Both reviews are terminal-locked. Exact differences do not necessarily imply substantive conflict.
Read only the explicit files below. No schedules, maps, operator labels, other cases or parent interpretation.
Output encoding (no new scoring criteria):
- resolutions: exactly the declared disputed raw IDs, with complete frozen scalar fields plus explicit kind, support and post_ids. Preserve every agreed scalar and agreed post_ids. Exclude fully agreed raw rows.
- family_resolutions: canonical C01,C02,... covering all {d['raw_count']} raw rows exactly once, including agreed rows as unchanged anchors. Include members, signature, archive_matches, equivalence, reason, kind, novelty, uncertain_equivalence_with. Keep uncertain links symmetric; no unchecked transitive merge.
- post_resolutions: exactly the declared post disagreements below. Each entry has packet_id, field, items, resolution_status (resolved|uncertain), reason. Preserve agreed dispositions. For fit or violation issues, retain actual post_id and issue. Resolving what should be recorded does not resolve an uncertain resource or world fact. Do not invent resources or repair the substantive probe.
- unresolved: structured entries with packet_id/raw_id or canonical_family/optional other_canonical_family, fields from novelty,usefulness,fit,observability,retention,family_equivalence,kind,support, and reason.
- If a packet has an execution failure and null post_distill, retention is unobservable: preserve uncertain and empty post_ids. Assess unchanged readable raw text without repairing its output contract. Failed trials cannot become complete workflows by review.
Declared post disagreements: {json.dumps(posts)}
SOFT total output allocation: {d['disputed_pairs']*600} tokens; one bounded assessment per disputed pair. Check exact resolution IDs, unique complete membership, preserved agreed fields, symmetric uncertain links and exact post fields before terminal. Save only the assigned substantive output.
Allowed files:
'''+json.dumps(files,indent=2)+f'\nExact output path: {R}/reviews/{phase}-{case}-adjudication.json\n'
p=R/f'prompts/jobs/adjudicate-{phase}-{case}.txt';assert not p.exists();p.write_text(txt)
m={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phase':phase,'case_id':case,'prompt_sha256':sha(p),'sources':files,'disputed_pairs':d['disputed_pairs'],'raw_resolutions':n,'agreed_raw':d['raw_count']-n,'post_disputes':posts,'criteria_changed':False,'preparer_sha256':sha(Path(__file__))}
p.with_suffix('.manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps({k:v for k,v in m.items() if k!='sources'},indent=2))
