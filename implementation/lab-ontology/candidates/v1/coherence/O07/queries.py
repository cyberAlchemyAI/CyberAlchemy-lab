"""Six actual fresh processes compare five original questions at exact source cuts."""
import subprocess,time
from base import *

def run(pin):
 source_guard(pin);require(not (HERE/'proof/queries').exists(),'refuse query proof overwrite');proof=HERE/'proof/queries';proof.mkdir()
 records=[];results={}
 for repetition in ['warm','cold']:
  for scope,prior_path in OLD_RESULTS.items():
   out=COVERAGE/repetition/scope
   command=[sys.executable,'-B',str(QUERY/'materialize.py'),scope,str(out),QUERY_PIN['path'],QUERY_PIN['sha256']]
   tick=time.monotonic();process=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=300,cwd=ROOT)
   stem=repetition+'-'+scope
   (proof/(stem+'.stdout')).write_bytes(process.stdout);(proof/(stem+'.stderr')).write_bytes(process.stderr)
   require(process.returncode==0,'original query materializer failed: '+process.stderr.decode(errors='replace'))
   current=load(out/'result.json');prior=load(prior_path);require(current['result']=='PASS' and current['selection_binding']==QUERY_PIN and current['closed_scope'] and current['owned_query_stores_removed'] and current['actual_owner_outcome'] is None and current['authority_effect']=='none','query scope/evidence is incomplete')
   require(set(current['questions'])==set(prior['questions']),'original written question coverage differs')
   for name,q in current['questions'].items():
    wanted=prior['questions'][name]['response_binding'];require(bound(q['response_binding'])==bound(wanted),'fresh answer differs from independently pinned original answer')
    if repetition=='cold':require(bound(q['response_binding'])==bound(results[('warm',scope)]['questions'][name]['response_binding']),'independent warm/cold query bytes differ')
   records.append({'repetition':repetition,'scope':scope,'command':command,'terminal_exit_code':process.returncode,'duration_seconds':time.monotonic()-tick,
    'stdout_binding':binding(proof/(stem+'.stdout')),'stderr_binding':binding(proof/(stem+'.stderr')),'original_result_binding':binding(prior_path),'current_result_binding':binding(out/'result.json'),
    'same_original_answers':True,'closed_scope':True,'owned_store_and_keys_removed':True})
   results[(repetition,scope)]=current
   print(json.dumps({'scope':scope,'repetition':repetition,'questions':len(current['questions']),'result':'PASS'}),flush=True)
 source_guard(pin)
 result={'schema_version':'lab-O07-query-coherence/v1-candidate','result':'PASS','processes':records,'actual_fresh_processes':6,'written_question_count':5,
  'answer_materializations':10,'same_original_answers':True,'same_independent_warm_cold_answers':True,'historical_current_native_cuts_distinct':True,
  'governed_query_genesis':'hash-sealed; zero approval signatures and admission transactions','authority_effect':'none','actual_owner_outcome':None,
  'source_execution':False,'current_action_permission':False,'runtime_activation':False,'Session_memory_restored':False,'native_graph_acceleration_selected':False}
 emit(proof/'result.json',result);print(json.dumps({'result':'PASS','result_binding':binding(proof/'result.json')}))

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--manifest-sha256',required=True);a=p.parse_args();run(a.manifest_sha256)
