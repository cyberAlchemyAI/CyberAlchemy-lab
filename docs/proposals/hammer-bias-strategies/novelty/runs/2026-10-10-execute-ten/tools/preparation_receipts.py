import argparse, hashlib, json, datetime
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('kind');p.add_argument('job');p.add_argument('handle');p.add_argument('--prompt');p.add_argument('--output');p.add_argument('--witness');a=p.parse_args()
def h(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
d={'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'kind':a.kind,'job':a.job,'agent_handle':a.handle,'native_turn':1,'scored':False}
if a.prompt: d['prompt']={'path':a.prompt,'sha256':h(a.prompt)}
if a.output: d['output']={'path':a.output,'sha256':h(a.output)} if Path(a.output).exists() else {'path':a.output,'missing':True}
if a.witness: d['terminal_witness']=a.witness
d['budget_sha256']=h(R/'PREPARATION-BUDGET.json')
with (R/'receipts/events.jsonl').open('a') as f: f.write(json.dumps(d)+'\n')
print(json.dumps(d))
