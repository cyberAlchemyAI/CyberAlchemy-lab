"""Bind retained real author observations; never manufacture review/authority."""
import bootstrap
from bootstrap import R,S,E,checked,PREFIX
import hashlib,json,os,re
from lab_contracts.codec import canonical

def bind(path):
    raw=checked(path)
    return {'kind':'evidence','root_id':'repository','relative_path':str(path.relative_to(R)),
        'sha256':hashlib.sha256(raw).hexdigest(),'size_bytes':len(raw)}

def main():
    runs=[]
    specs=[]
    for script,count in [('requirements',25),('elf',19),('origins',14),('composite',28),('input-guard',11)]:
        for optimized in (False,True):
            mode='optimized' if optimized else 'normal';revision='0003' if script=='input-guard' else '0001'
            specs.append(('final-author-'+script+'-'+mode+'-'+revision,'test_'+script.replace('-','_')+'.py',count,optimized))
    for stem,script,count,optimized in specs:
        out=E/(stem+'.stdout');err=E/(stem+'.stderr');terminal=json.loads(checked(out))
        if terminal!={'schema_version':'lab-case-command-result/v1','result':'PASS','checks':count,'effect_state':'owned-inert','cleanup':'clean'}:
            raise ValueError('author run incomplete')
        stderr=checked(err).decode();match=re.search(r'Ran (\d+) tests in ([0-9.]+)s',stderr)
        if not match or int(match.group(1))!=count or not stderr.endswith('\nOK\n'):raise ValueError('author test summary')
        runs.append({'stdout':bind(out),'stderr':bind(err),'terminal':terminal,
            'argv':['/usr/bin/python3.14','-B','-S']+(['-O'] if optimized else [])+
                [str(S/'tests/LC-U05-01'/script),'--temp-root',str(E)],
            'environment':{'PATH':'/usr/bin:/bin','PYTHONPYCACHEPREFIX':str(PREFIX)},
            'observed_os_exit':0,'os_exit_evidence':'Observed final fail-fast shell loop exit0; each selected child must exit0 to continue.',
            'reported_test_elapsed_seconds':match.group(2),'outer_started_at':None,'outer_finished_at':None,
            'source_selection':'author validation before immutable proposal; coordinator replay and independent review still required'})
    counter=['origins-tests-normal-0001.stdout','origins-tests-normal-0001.stderr',
        'final-author-input-guard-normal-0001.stdout','final-author-input-guard-normal-0001.stderr',
        'real-elf-development-0001.json','semantic-tests-normal-0002.stdout','semantic-tests-normal-0002.stderr']
    value={'schema_version':'lab-u0501-author-results/v1','runs':runs,'retained_counterevidence':[bind(E/n) for n in counter],
        'current_checks':sum(r['terminal']['checks'] for r in runs),'accepted_checkpoint_tests_preserved':True,
        'protected_original_bodies_read':0,'authority_effect':'none','actual_qualification':False,
        'timing_limits':'Outer start/end timestamps were not retained for these author shell observations; unittest durations are retained as reported, never substituted for process wall time.',
        'corrections':['Fixed full original selection pin prevents coherent closure omission/reordering.',
            'Corrected a test exception expectation for already-refused symlinks; source guard behavior was unchanged.',
            'Retained pre-test owned-root argument mismatch; corrected selected invocation ran14 cases in each mode.']}
    raw=canonical(value)+b'\n';path=E/'author-results-0001.json'
    with path.open('xb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
    print(json.dumps({'path':str(path),'sha256':hashlib.sha256(raw).hexdigest(),'checks':value['current_checks']}))

if __name__=='__main__':main()
