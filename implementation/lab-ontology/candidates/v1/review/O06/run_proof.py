"""Record actual build, complete guards and independent cold completion."""
import datetime,platform,subprocess,sys,time
from package import *

def main():
 require(not (HERE/'proof').exists(),'refuse proof overwrite')
 source_guard();pin=binding(HERE/'manifest.json')['sha256'];proof=HERE/'proof';proof.mkdir()
 commands={
  'build':[sys.executable,'-B',str(HERE/'package.py'),'--output',str(HERE/'packages/0001'),'--manifest-sha256',pin],
  'guards':[sys.executable,'-B','-m','unittest','-v','test_package'],
  'cold':[sys.executable,'-B',str(HERE/'cold.py'),'--package',str(HERE/'packages/0001'),'--manifest-sha256',pin]}
 observations=[];codes={}
 for name,command in commands.items():
  started=datetime.datetime.now(datetime.timezone.utc).isoformat();tick=time.monotonic()
  with (proof/f'{name}.stdout').open('xb') as out,(proof/f'{name}.stderr').open('xb') as err:
   process=subprocess.Popen(command,cwd=HERE,stdout=out,stderr=err);pid=process.pid
   try:code=process.wait(timeout=1800)
   except subprocess.TimeoutExpired:process.terminate();process.wait(timeout=30);raise
  codes[name]=code;observation={'process':name,'pid':pid,'command':command,'terminal_exit_code':code,'started_at':started,
   'duration_seconds':time.monotonic()-tick,'stdout_binding':binding(proof/f'{name}.stdout'),'stderr_binding':binding(proof/f'{name}.stderr')}
  observations.append(observation);put(proof/f'{name}-observation.json',observation)
  print(json.dumps({'process':name,'terminal_exit_code':code,'duration_seconds':observation['duration_seconds']}),flush=True)
  require(code==0,'actual '+name+' process failed; frozen evidence retained')
 put(proof/'terminal-observations.json',{'schema_version':'lab-O06-terminal-observations/v1-candidate','source_manifest_binding':binding(HERE/'manifest.json'),
  'exit_codes':codes,'processes':observations,'python_version':platform.python_version(),'authority_effect':'none','actual_owner_outcome':None})
 print(json.dumps({'result':'PASS','exit_codes':codes,'source_manifest_binding':binding(HERE/'manifest.json')}),flush=True)

if __name__=='__main__':main()
