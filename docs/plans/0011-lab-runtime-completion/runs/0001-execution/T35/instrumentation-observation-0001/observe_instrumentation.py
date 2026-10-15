"""Observe only the selected observer's own monitor reservation; no Lab imports."""
import argparse, hashlib, json, os, sys, types
from pathlib import Path

HERE = Path(__file__).absolute().parent
ROOT = HERE.parents[6]
OBSERVER = 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T35/full-learning-driver-0004/observe.py'
EXPECTED = 'ede4c6d057e65f6773aa94ecd8c23a0f983240f689980849dc8b93fff0431e06'

def snapshot():
    def hook(value):
        return None if value is None else {'module':type(value).__module__,'qualname':type(value).__qualname__}
    return {'schema_version':'lab-margin-instrumentation-observation/v1-candidate','authority_effect':'none',
            'profile_hook':hook(sys.getprofile()),'trace_hook':hook(sys.gettrace()),
            'monitoring_tools':{str(i):sys.monitoring.get_tool(i) for i in range(6)}}

def write(name,value):
    with (HERE/name).open('x') as stream:
        stream.write(json.dumps(value,sort_keys=True,indent=2)+'\n')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--observer-sha256',required=True)
    args = parser.parse_args()
    if args.observer_sha256 != EXPECTED:
        raise ValueError('selected independently reviewed observer required')
    path = ROOT/OBSERVER
    if path.is_symlink() or any(parent.is_symlink() for parent in path.parents):
        raise ValueError('true selected observer origin required')
    before_stat = path.stat(); raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != EXPECTED or path.stat() != before_stat:
        raise ValueError('selected observer input changed')
    initial = snapshot()
    if initial['profile_hook'] is not None or initial['trace_hook'] is not None or any(v is not None for v in initial['monitoring_tools'].values()):
        raise ValueError('isolated measurement process instrumentation differs')
    fd_before = len(list(Path('/proc/self/fd').iterdir()))
    module = types.ModuleType('_cal_T35_selected_instrumentation_observer')
    module.__file__ = str(path)
    exec(compile(raw,str(path),'exec',dont_inherit=True),module.__dict__)
    events = []
    observer = module.Observer(ROOT,lambda *args,**kwargs:events.append((args,kwargs)),profiling=False,source_rows={})
    try:
        observer.start()
        selected = snapshot(); reserved = observer.tool
        if reserved != 5 or selected['monitoring_tools']['5'] != 'cal-full-learning-measurement-v2' or any(selected['monitoring_tools'][str(i)] is not None for i in range(5)):
            raise ValueError('actual selected reservation differs')
        write('instrumentation.json',selected)
    finally:
        observer.close()
    final = snapshot()
    if final != initial or len(list(Path('/proc/self/fd').iterdir())) != fd_before:
        raise ValueError('owned observer cleanup differs')
    write('observation.json',{'schema_version':'lab-T35-selected-instrumentation-observation/v1-candidate','authority_effect':'none',
          'observer_binding':{'path':OBSERVER,'sha256':EXPECTED},'observer_true_filename':observer.start.__code__.co_filename,
          'actual_reserved_tool':reserved,'initial':initial,'selected':selected,'after_owned_cleanup':final,
          'FD_delta':0,'actual_Lab_or_native_constructor':False,'leases_opened':False,'empirical_margin_qualified':False,'task_complete':False})
    print(json.dumps({'result':'OBSERVED-selected-own-monitor-reservation','reserved_tool':reserved,'FD_delta':0,'runtime_started':False}))

if __name__ == '__main__':
    main()
