"""Pure AST, retained public text and ELF metadata; no executor/module imports."""
import ast,hashlib,json,re,struct,signal,types
from pathlib import Path
HERE=Path(__file__).absolute().parent
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
def main():
    tree=ast.parse((HERE/'execute.py').read_bytes());functions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
    env={'hashlib':hashlib,'re':re,'struct':struct}
    unit=ast.Module(body=[functions[name]for name in('need','test_accounting','elf_metadata')],type_ignores=[]);ast.fix_missing_locations(unit)
    exec(compile(unit,str(HERE/'execute.py'),'exec'),env)
    checks=[]
    def check(name,fn,refuses=False):
        try:fn()
        except ValueError:
            if not refuses:raise
        else:
            if refuses:raise ValueError('missing negative refusal: '+name)
        checks.append(name)
    inputs=json.loads((HERE/'inputs.json').read_bytes());proposal_binding=inputs['references']['proposal'];proposal_path=ROOT/proposal_binding['path'];proposal_raw=proposal_path.read_bytes()
    check('exact-original-five-command-proposal',lambda:env['need'](hashlib.sha256(proposal_raw).hexdigest()=='ab91688ab8ad0c581447b310a7bbc9ab6e7609a5508938398eb11301fe7e0e67','proposal changed'))
    proposal=json.loads(proposal_raw);check('five-original-argv-env-from-selected-proposal',lambda:env['need'](len(proposal['commands'])==5 and all(c['environment']==proposal['commands'][0]['environment']for c in proposal['commands']),'commands changed'))
    selection=json.loads((HERE/'execution-selection-INACTIVE.json').read_bytes());check('inactive-dispatch-unbound',lambda:env['need'](selection['root_dispatch_binding']is None,'activation claimed'))
    run=functions['run'];popens=[n for n in ast.walk(run)if isinstance(n,ast.Call)and ast.unparse(n.func)=='subprocess.Popen'];check('one-serial-subprocess-port',lambda:env['need'](len(popens)==1,'unexpected port'))
    call=popens[0];keywords={v.arg:ast.unparse(v.value)for v in call.keywords}
    check('exact-argv-and-no-environment-inheritance',lambda:env['need'](ast.unparse(call.args[0])=="command['argv']"and keywords['env']=="dict(command['environment'])"and 'shell'not in keywords,'argv/env changed'))
    check('child-FDs-and-group-isolated',lambda:env['need'](keywords['close_fds']=='True'and keywords['start_new_session']=='True'and keywords['stdin']=='subprocess.DEVNULL','unsafe child ports'))
    retained=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T32/production-regression-0002.stdout';raw=retained.read_bytes()
    original=json.loads((ROOT/inputs['references']['inputs110']['path']).read_bytes());names=[n for rows in original['original_test_names'].values()for n in rows]
    check('full-original23-retained-output-positive',lambda:env['test_accounting'](raw,names))
    check('missing-original-name-refuses',lambda:env['test_accounting'](raw.replace(names[0].encode(),b'invented_name'),names),True)
    check('failed-original-test-refuses',lambda:env['test_accounting'](raw.replace(b' ... ok',b' ... FAILED',1),names),True)
    check('ignored-test-summary-refuses',lambda:env['test_accounting'](raw.replace(b'0 ignored',b'1 ignored',1),names),True)
    check('filtered-test-summary-refuses',lambda:env['test_accounting'](raw.replace(b'0 filtered out',b'1 filtered out',1),names),True)
    observations=json.loads((ROOT/inputs['references']['observations']['path']).read_bytes());native=observations['native_bin_binding'];body=(ROOT/native['path']).read_bytes()
    check('existing574-exact-input-only',lambda:env['need'](hashlib.sha256(body).hexdigest()==native['sha256'],'selected binary changed'))
    metadata=env['elf_metadata'](body)
    check('ELF64-metadata-parser-current574-positive',lambda:env['need'](metadata['machine']==62 and metadata['type']==3 and metadata['interpreter']=='/lib64/ld-linux-x86-64.so.2'and metadata['needed']==['ld-linux-x86-64.so.2','libc.so.6','libgcc_s.so.1']and metadata['comment']==observations['ELF']['comment_section'],'metadata differs'))
    check('invalid-ELF-refuses',lambda:env['elf_metadata'](b'not-an-ELF'),True)
    def group_fixture(stop,refuses=False):
        state={'alive':stop!='already-gone','clock':0,'signals':[]};pid=123456
        def killpg(selected,sig):
            env['need'](selected==pid,'unrelated process group touched')
            if not state['alive']:raise ProcessLookupError()
            if sig:
                state['signals'].append(sig)
                if sig==stop:state['alive']=False
        class Child:
            returncode=None
            def poll(self):
                if not state['alive']:self.returncode=0 if stop=='already-gone'else -int(stop)
                return self.returncode
        child=Child();child.pid=pid
        def monotonic():state['clock']+=3;return state['clock']
        scope={'os':types.SimpleNamespace(killpg=killpg),'signal':signal,'time':types.SimpleNamespace(monotonic=monotonic,sleep=lambda _:None),'need':env['need']}
        block=ast.Module(body=[functions['group_alive'],functions['stop_owned_group']],type_ignores=[]);ast.fix_missing_locations(block);exec(compile(block,str(HERE/'execute.py'),'exec'),scope)
        actions=[];scope['stop_owned_group'](child,actions)
        env['need'](not state['alive'] and child.returncode is not None,'group not reaped')
        expected=[] if stop=='already-gone'else [signal.SIGTERM]if stop==signal.SIGTERM else [signal.SIGTERM,signal.SIGKILL]
        env['need'](state['signals']==expected and all(a['process_group']==pid for a in actions),'group signal sequence differs')
    check('owned-group-TERM-reap-inert-positive',lambda:group_fixture(signal.SIGTERM))
    check('owned-group-TERM-KILL-reap-inert-positive',lambda:group_fixture(signal.SIGKILL))
    check('already-gone-group-no-signals-inert-positive',lambda:group_fixture('already-gone'))
    check('unreaped-owned-group-refuses-inert',lambda:group_fixture('never'),True)
    # Exact independent finally loop with inert selected ports only.
    outer=next(n for n in run.body if isinstance(n,ast.Try));final=outer.finalbody
    loop=next(n for n in final if isinstance(n,ast.For))
    seen=[];errors=[]
    def port(label,refuse=False):
        def invoke():
            seen.append(label)
            if refuse:raise ValueError('owned inert refusal')
        return invoke
    scope={'checks':[(str(i),port(i,i in(0,2)))for i in range(5)],'measure':lambda label,fn:fn(),'errors':errors,'diagnostic':lambda:{'exception_class':'ValueError'}}
    block=ast.Module(body=[loop],type_ignores=[]);ast.fix_missing_locations(block);exec(compile(block,str(HERE/'execute.py'),'exec'),scope)
    check('all-five-exit-checks-independent-on-failure',lambda:env['need'](seen==list(range(5))and len(errors)==2,'exit suppressed'))
    return {'result':'PASS','checks':checks,'check_count':len(checks),'actual_commands_Source_guards_API_native_or_setup_executed':False,'mode':'AST-text-and-public-ELF-metadata-only'}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True))
