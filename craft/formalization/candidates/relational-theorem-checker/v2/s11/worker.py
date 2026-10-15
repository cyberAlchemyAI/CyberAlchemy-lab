"""Observed process/stage costs; inclusive stage timers are not summed as exclusive work."""
from pathlib import Path
import sys,time,resource as usage
sys.dont_write_bytecode=True
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'s06'));import runtime as r
s=r.s
sys.path.insert(0,str(BASE/'s09'));import bounded_qualification as bounded
r.qualify=bounded.qualify

def run(proposal,build):
 counters={};originals=[]
 def wrap(obj,name,label):
  old=getattr(obj,name);originals.append((obj,name,old))
  def timed(*args,**kwargs):
   start=time.monotonic()
   try:return old(*args,**kwargs)
   finally:
    row=counters.setdefault(label,{'seconds':0.,'calls':0});row['seconds']+=time.monotonic()-start;row['calls']+=1
  setattr(obj,name,timed)
 for obj,name,label in [(r,'prepare','dependency_preparation'),(r.projection,'project','projection'),(r,'evaluate','grounding_and_saturation'),(s,'compile_modules','compile_and_actual_witness_checks'),(r,'replay_general','fresh_general_kernel_replay'),(s,'digest','hashing'),(s,'identity','canonical_identity')]:wrap(obj,name,label)
 start=time.monotonic()
 try:out=r.qualify(proposal,build)
 finally:
  for obj,name,old in reversed(originals):setattr(obj,name,old)
 elapsed=time.monotonic()-start
 return {'status':out['status'],'seconds':elapsed,'inclusive_stages':counters,'work':out['counters'],'parent_max_rss_kib':usage.getrusage(usage.RUSAGE_SELF).ru_maxrss,'child_max_rss_kib':usage.getrusage(usage.RUSAGE_CHILDREN).ru_maxrss,'result':out,'timer_policy':'inclusive nested timers; do not sum stages; peak RSS is observed per worker process/cumulative child maximum within that worker'}
if __name__=='__main__':
 out=run(s.read(Path(sys.argv[1])),Path(sys.argv[2]));s.write(Path(sys.argv[3]),out);print('qualified benchmark '+str(round(out['seconds'],3))+' seconds')
