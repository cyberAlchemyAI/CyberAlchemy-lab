"""Actual terminal evidence for full O07 coherence and selected native/query rebuilds."""
import datetime,subprocess,time
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from base import *
from successor import guard_successor,SUCCESSOR

def run(selection_pin):
 guard_successor(selection_pin)
 pin=binding(HERE/'manifest.json')['sha256'];source_guard(pin);proof=HERE/'proof/successor-0001';require(not proof.exists(),'refuse proof overwrite');proof.mkdir()
 commands={'guards':[sys.executable,'-B','-m','unittest','-v','test_audit','test_native']}
 for n in ['warm','cold']:
  commands['rebuild-'+n]=[sys.executable,'-B',str(SUCCESSOR/'rebuild.py'),'--selection-sha256',selection_pin,'--manifest-sha256',pin,'--output',str(proof/('rebuild-'+n))]
  commands['audit-'+n]=[sys.executable,'-B',str(HERE/'audit.py'),'--manifest-sha256',pin,'--output',str(proof/('audit-'+n+'.json'))]
 commands['queries']=[sys.executable,'-B',str(SUCCESSOR/'queries.py'),'--selection-sha256',selection_pin,'--manifest-sha256',pin]
 codes={};observations=[]
 for name,command in commands.items():
  started=datetime.datetime.now(datetime.timezone.utc).isoformat();tick=time.monotonic()
  with (proof/(name+'.stdout')).open('xb') as out,(proof/(name+'.stderr')).open('xb') as err:
   process=subprocess.Popen(command,cwd=HERE,stdout=out,stderr=err);pid=process.pid
   try:code=process.wait(timeout=1200)
   except subprocess.TimeoutExpired:process.terminate();process.wait(timeout=30);raise
  codes[name]=code;row={'process':name,'pid':pid,'command':command,'terminal_exit_code':code,'started_at':started,'duration_seconds':time.monotonic()-tick,
   'stdout_binding':binding(proof/(name+'.stdout')),'stderr_binding':binding(proof/(name+'.stderr'))};observations.append(row);emit(proof/(name+'-observation.json'),row)
  guard_successor(selection_pin)
  print(json.dumps({'process':name,'terminal_exit_code':code,'duration_seconds':row['duration_seconds']}),flush=True);require(code==0,'actual '+name+' failed; frozen attempt preserved')
 source_guard(pin);guard_successor(selection_pin);emit(proof/'terminal-observations.json',{'result':'PASS','exit_codes':codes,'processes':observations,'source_manifest_binding':binding(HERE/'manifest.json'),'authority_effect':'none','actual_owner_outcome':None})
 print(json.dumps({'result':'PASS','terminal_observations_binding':binding(proof/'terminal-observations.json')}),flush=True)

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--selection-sha256',required=True);a=p.parse_args();run(a.selection_sha256)
