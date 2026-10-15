"""UNRUN inert custody controls; no API, original callbacks, native or lease."""
import hashlib,importlib.util,json,os,sys,tempfile
from pathlib import Path
HERE=Path(__file__).absolute().parent

def main():
    name='_cal_bridge2_attachment_controls'
    spec=importlib.util.spec_from_file_location(name,HERE/'__init__.py',submodule_search_locations=[str(HERE)])
    pkg=importlib.util.module_from_spec(spec);sys.modules[name]=pkg;spec.loader.exec_module(pkg)
    B=__import__(name+'.protected_bridge',fromlist=['control_bytes'])
    fd0=len(os.listdir('/proc/self/fd'));checks=[]
    def refuse(label,fn):
        try:fn()
        except (ValueError,OSError):checks.append(label);return
        raise AssertionError(label)
    with tempfile.TemporaryDirectory(prefix='cal-bridge2-inert-custody-') as tmp:
        root=Path(tmp);root.chmod(0o700);s=root.stat()
        selected={'id':'inert','path':tmp,'device':s.st_dev,'inode':s.st_ino,'uid':s.st_uid,'mode':0o700}
        folder=root/'one';folder.mkdir(mode=0o700);nested=folder/'two';nested.mkdir(mode=0o700)
        leaf=nested/'control';raw=b'{"inert":true}\n';leaf.write_bytes(raw);leaf.chmod(0o600);s=leaf.stat()
        locator={'root_id':'inert','path':'one/two/control','size':len(raw),'device':s.st_dev,'inode':s.st_ino,'uid':s.st_uid,'mode':0o600}
        binding={'ref':'fixture:inert','sha256':hashlib.sha256(raw).hexdigest()}
        assert B.control_bytes(selected,locator,binding)==raw;checks.append('actual nested nofollow control_bytes returns exact independently selected bytes')
        handles=[];links=[]
        def identity(s):return (s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode)
        try:
            parent=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);handles.append(parent)
            for part in ['one','two']:
                fd=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent);handles.append(fd)
                links.append((parent,part,fd,identity(os.fstat(fd))));parent=fd
            B.verify_control_links(links);checks.append('actual held intermediate attachment verifier accepts selected chain')
            folder.rename(root/'retained-one');folder.mkdir(mode=0o700);(folder/'two').mkdir(mode=0o700)
            os.link(root/'retained-one/two/control',folder/'two/control')
            assert (folder/'two/control').stat().st_ino==(root/'retained-one/two/control').stat().st_ino
            refuse('same leaf inode and bytes cannot conceal changed intermediate attachment',lambda:B.verify_control_links(links))
        finally:
            for fd in reversed(handles):os.close(fd)
        refuse('unselected leaf digest refuses',lambda:B.control_bytes(selected,locator,{'ref':'fixture:inert','sha256':'0'*64}))
    assert len(os.listdir('/proc/self/fd'))==fd0
    print(json.dumps({'result':'PASS-inert-relative-custody-only','checks':checks,'FD_delta':0,
                      'API_native_install_or_lease_executed':False,'whole_bridge_qualified':False,'authority_effect':'none'},sort_keys=True))
if __name__=='__main__':main()
