"""Independent normal path parity and own inert files only; no Lab runtime."""
import hashlib,importlib.abc,importlib.util,json,os,sys,tempfile,uuid
from pathlib import Path,PurePosixPath

ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE=Path(__file__).absolute().parent
INTERPRETER=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004/bin/python'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def main():
    assert Path(sys.executable)==INTERPRETER
    raw=(HERE/'selection.json').read_bytes();assert sha(raw)==sys.argv[1];selection=json.loads(raw)
    assert selection['authority_effect']=='none'
    for row in selection['files']:
        assert sha((ROOT/row['path']).read_bytes())==row['sha256']
    loaded=[]
    def captured(binding,leaf):
        path=ROOT/binding['path'];raw=path.read_bytes();assert sha(raw)==binding['sha256']
        class Loader(importlib.abc.SourceLoader):
            selected_source_sha256=binding['sha256']
            def get_filename(self,name):return str(path)
            def get_data(self,filename):assert filename==str(path);return raw
            def get_code(self,name):return compile(raw,str(path),'exec',dont_inherit=True)
        name='_cal_independent_normal_pathprep_'+leaf+'_'+uuid.uuid4().hex
        spec=importlib.util.spec_from_file_location(name,path,loader=Loader());module=importlib.util.module_from_spec(spec)
        sys.modules[name]=module;loaded.append((name,module));spec.loader.exec_module(module);return module
    checks=[];before=len(os.listdir('/proc/self/fd'))
    try:
        original=captured(selection['original'],'original');candidate=captured(selection['candidate'],'candidate');companion=captured(selection['caller'],'caller')
        contracts={}
        for label,module in [('original',original),('candidate',candidate)]:
            binding=selection[label];assert module.__file__==str(ROOT/binding['path'])
            contracts[label]=companion.select(module,expected_path=ROOT/binding['path'],expected_sha256=binding['sha256'])
            companion.check(contracts[label],module)
        rows=[{'path':p,'sha256':'a'*64} for p in ['a','a/b','a/.b','/a','//a','//','///a','a//b','a/./b','../a','a/../b','.','/','','a/','a\\b','a\0b']]
        rows += [None,[],{}, {'path':'a','sha256':'A'*64},{'path':'a','sha256':'0'*63},{'path':1,'sha256':'0'*64},{'path':'a','sha256':'0'*64,'extra':False}]
        roots=['/','//','/tmp','//tmp','/tmp//nested','.','relative','relative/..',Path('/tmp'),Path('relative'),PurePosixPath('//tmp/nested'),PurePosixPath('/tmp/../nested')]
        def outcome(callback):
            try:return ('value',callback())
            except (ValueError,TypeError,AttributeError) as error:return ('exception',type(error).__name__)
        count=0
        for root in roots:
            for row in rows:
                for external in [(),[row]]:
                    expected=outcome(lambda:original.selected(root,row,external))
                    assert expected==outcome(lambda:candidate.selected(root,row,external))==outcome(lambda:candidate.selected(PurePosixPath(root),row,external))
                    count+=1
        checks.append({'case':'direct-and-prepared-root-string-Path-PurePosixPath-selector-parity','combinations':count,'result':'PASS'})
        for label,module in [('original',original),('candidate',candidate)]:
            pin=selection[label]['sha256']
            with tempfile.TemporaryDirectory(prefix='owned-normal-files-',dir=HERE) as directory:
                root=Path(directory);(root/'branch').mkdir();data=[b'owned inert first\n',b'owned inert second\n'];rows=[]
                for index,raw in enumerate(data):
                    p=root/'branch'/str(index);p.write_bytes(raw);rows.append({'path':'branch/'+str(index),'sha256':sha(raw)})
                    assert module.capture_one(root,rows[-1],code_sha256=pin)==raw
                assert module.verify_all(root,list(reversed(rows)),code_sha256=pin)==2
                external={'path':str(root/'branch/0'),'sha256':rows[0]['sha256']}
                assert module.capture_one(root,external,code_sha256=pin,selected_external=[external])==data[0]
                for selected_rows,kwargs in [([rows[0],rows[0]],{}),([rows[0],external],{'selected_external':[external]}),([{**rows[0],'extra':False}],{}),([{**rows[0],'sha256':'0'*64}],{})]:
                    try:module.verify_all(root,selected_rows,code_sha256=pin,**kwargs)
                    except ValueError:pass
                    else:raise AssertionError('closed/duplicate/alias/hash refusal missing')
                assert not module._ACTIVE.value
                companion.check(contracts[label],module)
            checks.append({'case':label+'-normal-capture-whole-rows-explicit-external-and-closed-alias-digest-refusals','result':'PASS'})
        assert before==len(os.listdir('/proc/self/fd'))
        for row in selection['files']:assert sha((ROOT/row['path']).read_bytes())==row['sha256']
        value={'schema_version':'lab-T03-independent-pathprep-pure-controls/v1-candidate','authority_effect':'none','result':'PASS-normal-pure-selection-and-owned-files','checks':checks,'selector_parity_combinations':count,'descriptor_delta':0,'selection_sha256':sys.argv[1],'actual_interpreter':str(INTERPRETER),'runtime_constructor_or_lease':False,'callback_primitive_clock_or_global_mutation':False,'performance_measured':False,'task_complete':False}
        with (HERE/'pure-controls-result.json').open('x') as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n')
        print(json.dumps({'result':value['result'],'selector_parity_combinations':count,'descriptor_delta':0}))
    finally:
        for name,module in reversed(loaded):
            if sys.modules.get(name) is module:del sys.modules[name]
if __name__=='__main__':main()
