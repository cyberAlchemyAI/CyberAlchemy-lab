"""Read-only cProfile of one actual original signed-source guard."""
import cProfile,hashlib,importlib.util,json,pstats,sys,time
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');BASE=ROOT/'product/lab/release-candidates/v1/interface';OUT=Path('/tmp/cal-session-diagnostic-action-0148');API=BASE/'api-integration-v7'
n='_cal_actual_signed_source_cost_action_0148';s=importlib.util.spec_from_file_location(n,API/'__init__.py',submodule_search_locations=[str(API)]);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m)
source=__import__(n+'.source_bridge',fromlist=['*']);start=time.monotonic();reader=source.custody_delivery().reader
with reader.open_signed(source.custody_delivery().SOURCE_PIN,source.custody_delivery().SOURCE_PACKAGE) as selected:
 constructed=time.monotonic();print(json.dumps({'phase':'actual-signed-source-open','elapsed_seconds':constructed-start,'records':len(selected.records),'schemas':len(selected.schemas),'baseline_materials':len(selected.view.data['baseline']['materials'])}),flush=True)
 profiler=cProfile.Profile();profiler.enable();selected.guard();profiler.disable();elapsed=time.monotonic()-constructed
 profiler.dump_stats(OUT/'original-signed-guard.profile')
 with (OUT/'original-signed-guard-profile.txt').open('x') as f:pstats.Stats(profiler,stream=f).sort_stats('cumulative').print_stats(45)
 print(json.dumps({'phase':'actual-original-signed-guard','elapsed_seconds':elapsed,'authority_effect':'none','actual_owner_outcome':None}),flush=True)
print(json.dumps({'phase':'original-source-exit-completed','total_seconds':time.monotonic()-start}),flush=True)
