#!/usr/bin/env python3
"""Run bounded collectors through playwright-cli, never through a test runner."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
OUT=ROOT/'website/output/playwright/ux-validator/20261012-whole-site'
CLI=Path('/home/vlad_/.npm/_npx/31e32ef8478fbf80/node_modules/@playwright/cli/playwright-cli.js')
AXE=Path('/home/vlad_/.npm/_npx/0f94ee7615faf582/node_modules/axe-core/axe.min.js')
BASE='http://127.0.0.1:33733/'

def cli(session,args):
    env=dict(os.environ,LD_LIBRARY_PATH='/home/vlad_/.cache/ms-playwright/user-libs/usr/lib/x86_64-linux-gnu')
    result=subprocess.run(['node',str(CLI),'-s='+session,'--json',*args],cwd=ROOT,env=env,text=True,capture_output=True)
    if result.returncode:raise RuntimeError(result.stderr[-4000:]+result.stdout[-1000:])
    value=json.loads(result.stdout)['result']
    while isinstance(value,str):
        try:value=json.loads(value)
        except json.JSONDecodeError:break
    return value

def routes():
    items=[]
    standalone=['index','company-brain','research','start-here','incident-walkthrough','concept-comparisons',
                'read-record','prepare-definition','prepare-incident-assessment','resume-agent-work','record-examples']
    for name in standalone:items.append(dict(key=name,path='governance-lab-series/'+name+'.html'))
    for name in ['start','foundations','governance','evidence','change','purpose','records','agent','learning','today','system-map','reading-next']:
        items.append(dict(key='guide-'+name,path='governance-lab-series/governance-lab-reference.html#'+name))
    for name in ['articles-library',*['essay-'+str(i) for i in range(1,9)],'reference','library-reading-guide','catalog-definitions','catalog-types','catalog-relations','catalog-endpoints','catalog-history','research']:
        items.append(dict(key='library-'+name,path='governance-lab-series/lab-reference-library.html#'+name))
    for name in ['craft-overview','modelling','failure-causes','taxonomy','process','definition','typed-model','architecture','compilation','enforcement','evolution','agent-sessions','governance']:
        items.append(dict(key='craft-'+name,path='craft-documentation-proposal/craft-model.html#'+name))
    items += [dict(key='robot',path='robot-learning-series/robot-learning-series.html'),dict(key='reader-form',path='governance-lab-series/research/reader-study.html')]
    return items

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--engine',default='chromium');parser.add_argument('--width',type=int,default=1440);parser.add_argument('--start',type=int,default=0);parser.add_argument('--limit',type=int,default=6);parser.add_argument('--label',default='');parser.add_argument('--no-axe',action='store_true')
    args=parser.parse_args();session='lab-whole-site-review'+('' if args.engine=='chromium' else '-'+args.engine)
    for folder in ['measurements','screenshots','accessibility','aria','traces']: (OUT/folder).mkdir(parents=True,exist_ok=True)
    states=[]
    for original in routes()[args.start:args.start+args.limit]:
        item=dict(original,width=args.width,key=original['key']+'-'+str(args.width))
        item['axe']=args.engine=='chromium' and args.width==1440 and not args.no_axe
        item['aria']=args.engine=='chromium' and args.width==1440
        item['screenshot']=args.engine=='chromium' and args.width in [1440,390]
        states.append(item)
    config=dict(base=BASE,output=str(OUT),engine=args.engine,states=states,axe=str(AXE))
    script=(HERE/'collect_browser.js').read_text().replace('/*CONFIG*/ {}',json.dumps(config))
    suffix='-'+args.label if args.label else ''
    filename=OUT/'measurements'/f'{args.engine}-{args.width}-{args.start}{suffix}.js';filename.write_text(script)
    data=cli(session,['run-code','--filename',str(filename)])
    if not isinstance(data,dict):raise RuntimeError(str(data)[:1000])
    for row in data['states']:
        snapshot=row.pop('aria',None)
        if isinstance(snapshot,str):(OUT/'aria'/f'{args.engine}-{row["key"]}.yml').write_text(snapshot)
        if 'accessibility' in row:(OUT/'accessibility'/f'{args.engine}-{row["key"]}.json').write_text(json.dumps(row.pop('accessibility'),indent=2)+'\n')
    (OUT/'measurements'/f'{args.engine}-{args.width}-{args.start}{suffix}.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(dict(engine=args.engine,width=args.width,states=len(data['states']),errors=[dict(key=r['key'],error=r['error']) for r in data['states'] if 'error' in r],overflow=[r['key'] for r in data['states'] if r.get('measurements',{}).get('pageHorizontalOverflow')],events=len(data['events']))),flush=True)

if __name__=='__main__':main()
