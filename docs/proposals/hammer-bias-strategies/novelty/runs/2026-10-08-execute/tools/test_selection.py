#!/usr/bin/env python3
"""Synthetic unit fixtures for rule implementation, NOT experiment outcomes."""
import copy,importlib.util,json
from pathlib import Path
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('selection',P/'select_finalists.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
def base():
 d={'judgments_locked':True,'equivalence_review_locked':True,'cases':{}}
 for case in ['D1','D2']:
  units=[]
  for condition in ['ordinary','creative']+[f'N{i:02d}' for i in range(1,13)]:
   for rep in [1,2]:units.append({'unit_id':case+'-'+condition+str(rep),'condition':condition,'repetition':rep,'terminal_status':'completed','execution_valid':True,'assessment_complete':True,'raw':[],'post_only':[],'output_words':100})
  d['cases'][case]={'units':units,'families':{}}
 return d
def add(d,op,case='both',rid='A1',family='novel',retention='retained',fit='preserves',novelty='new'):
 for c in (['D1','D2'] if case=='both' else [case]):
  cd=d['cases'][c];cd['families'][family]={'equivalence_status':'confirmed'}
  u=next(u for u in cd['units'] if u['condition']==op and u['repetition']==1)
  u['raw'].append({'raw_id':rid,'family_id':family,'novelty':novelty,'usefulness':1,'fit':fit,'observability':2,'retention':retention,'judgment_resolved':True})
def selected(d):return mod.select(d)['finalists']
checks=[]
def check(name,test):assert test,name;checks.append(name)
d=base();check('empty exploration selects zero',selected(d)==[])
add(d,'N01');check('A-origin novelty on both cases can advance',selected(d)==['N01'])
e=copy.deepcopy(d);add(e,'creative',retention='lost');check('raw control overlap blocks generation credit despite control loss',selected(e)==[])
e=base();add(e,'N01',rid='Z1');check('Z-only novelty cannot advance an operator',selected(e)==[])
e=base();add(e,'N01',retention='lost');check('lost novelty does not meet retained-advancement rule',selected(e)==[])
e=base();add(e,'N01',case='D1');check('one discovery case insufficient',selected(e)==[])
e=base();add(e,'N01',novelty='parameter');check('parameter variants do not qualify as new families',selected(e)==[])
e=base();add(e,'N01');add(e,'N02');check('equivalent family sets collapse to one finalist',len(selected(e))==1)
e=base();add(e,'N01',family='f1');add(e,'N02',family='f2');add(e,'N03',family='f3');expected=selected(e);check('seed selects at most two distinct equivalent-cost finalists',len(expected)==2)
for cd in e['cases'].values():cd['units'].reverse()
check('input order does not alter tie selection',selected(e)==expected)
e=base();add(e,'N01',family='f1');add(e,'N02',family='f2')
for cd in e['cases'].values():
 for u in cd['units']:
  if u['condition']=='N01':u['output_words']=None
check('missing output burden remains incomparable',set(selected(e))=={'N01','N02'})
e=base();e['cases']['D1']['units'].pop()
try:mod.select(e);raise RuntimeError('missing exposure accepted')
except AssertionError:checks.append('incomplete exposure table rejected')
e=base();e['cases']['D1']['units'][0]['assessment_complete']=False
try:mod.select(e);raise RuntimeError('unreviewed exposure accepted')
except AssertionError:checks.append('incomplete judgment table rejected')
result={'status':'pass','kind':'scoring-code-unit-checks-not-experiment-results','checks':checks}
(P.parent/'reports/selection-code-check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
