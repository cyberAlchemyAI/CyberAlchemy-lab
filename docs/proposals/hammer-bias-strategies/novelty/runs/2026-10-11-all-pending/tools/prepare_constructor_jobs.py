from pathlib import Path
import json,hashlib,datetime
RUN=Path(__file__).resolve().parents[1]
def main():
 cards=json.loads((RUN/'preparation/PROVISIONAL-CARDS.json').read_text())
 case_paths=[RUN/'inputs/game-cases/CASES.json',RUN/'inputs/long-cases/CASES.json']
 for p in case_paths:
  if not p.exists():raise SystemExit('Missing '+str(p))
 sources={str(p):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'data':json.loads(p.read_text())} for p in case_paths}
 batches={'RT-A':[f'RT{i:02}' for i in range(1,8)],'RT-B':[f'RT{i:02}' for i in range(8,15)],'PR-A':[f'PR{i:02}' for i in range(1,6)],'PR-B':[f'PR{i:02}' for i in range(6,11)],'MG-A':[f'MG{i:02}' for i in range(1,9)],'MG-B':[f'MG{i:02}' for i in range(9,17)],'LL-A':[f'LL{i:02}' for i in range(1,7)],'LL-B':[f'LL{i:02}' for i in range(7,13)],'FO-A':[f'FO{i:02}' for i in range(1,6)],'FO-B':[f'FO{i:02}' for i in range(6,11)]}
 for batch,ids in batches.items():
  job='CONSTRUCT-'+batch;directory=RUN/'preparation/jobs'/job;directory.mkdir(exist_ok=False)
  family=batch[:2]; selected={k:v for k,v in sources.items() if ('long-cases' in k)==(family in ('LL','FO'))}
  payload={'job_id':job,'strategy_ids':ids,'methods':[x for x in cards if x['id'] in ids],'cases':selected,'role':'constructor','claim_ceiling':'Actual native authoring and paper/documentary comparisons; no real human or game outcomes. Paired authored conditions within this one role, not randomized independent arms.','output_path':str(RUN/'raw'/f'{job}.json')}
  (directory/'PAYLOAD.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
  prompt=f"""You are the actual native construction role for {job}. User objective is run all pending strategies; human chose native-agent investigations. Workspace /home/vlad_/projects/CyberAlchemy-lab. Read only PAYLOAD.json in this job directory and the run preparation/PROTOCOL.md. Sources/cases are embedded; do not read other outputs, browse or create helpers. Write exclusively {payload['output_path']} using exclusive first creation; no edits of source/goal/report. Save a substantive structured JSON body, not a save-summary. At most 750 words per assigned card (budget counts the card's method and controls together, same 750 cap each; internal compute unmeasured). No additional strategies.

APPLY every method literally to a supplied case; do not merely propose how someone could run it. For each card, preserve an evidence lane (case IDs, fixed facts, allowed changes, unknowns) and a construction lane. Execute the named operations, including a specific attributed expectation, actual causal inversion/attack and reconstruction, scoped contradiction or documentary coding as relevant. Produce a concrete rule/artifact and actual paper comparisons, with the method-specific control conditions in the original card; a plain strongest ordinary construction plus generic creativity comparator also receive explicit finite operations. A single operator-authored paired control is not an independent treatment arm and cannot prove efficacy.

Output top-level job_id, role, source_access, rows. Every row must have strategy_id, case_id, evidence_lane, operator_steps (ordered actual actions), artifact (literal finite rules/action structure, costs, feedback, alternatives, counter), ordinary_control, generic_control, required_comparisons (each named condition with actual artifact/state/prediction or documentary coding and comparison finding), dependency_delta, burden, defeat, native_disposition (applied / explicit_no_opening / incomplete), outcome_limits, handoff (protected facts, discrepancy, residue, permitted variable, concise construction request). Use available numeric states and demonstrate a short same-initial-state action/result pair where strategic mechanics change. Mark predicted consequences as paper predictions; only an executed model trace may be called simulated observation. Reject impossible rules, accidental limitless loops, auto wins, dropped one-of-three hero choice, stage structure or six-rule autoplay constraint. Native classification of supplied participant-like observations must say synthetic; no measurement of human surprise/enjoyment/retention is supplied. LL10 must actually code supplied literary windows, preserve selection and canon caveats. FO09/10 must actually separate documentary timelines and evidence denominators, explicitly retain unavailable origin/share/lineage contrasts; never turn invented descendants into real adoption.

A result may be a tie, nearest ordinary equivalent, or precise source-backed no opening. No requirement to invent a positive. Save and return output path and completion caveats."""
  (directory/'PROMPT.md').write_text(prompt+'\n')
 print('Prepared',len(batches),'constructor batches; 62 method rows')
if __name__=='__main__':main()
