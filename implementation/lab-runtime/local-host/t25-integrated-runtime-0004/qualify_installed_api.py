"""Fresh installed API guard/schema/Agent Source proof via selected bootstrap."""
import importlib
from datetime import datetime,timezone
import json
import os
import resource
from pathlib import Path
import sys
import time
P=sys.modules.get('cal_installed_runtime_selection_v1')
if P is None:raise ValueError('selected installed bootstrap is required')
P.require_runtime_ready();root=P.root();started=time.monotonic()
api=root/P.current().package['entrypoint']['api_directory'];sys.path.insert(0,str(api.parent))
guard=importlib.import_module(api.name+'.guard');source=P.binding('api.source')['sha256'];profile=P.binding('api.profile')['sha256'];guard.verify(source)
protocol=importlib.import_module(api.name+'.protocol');schemas=protocol.Schemas(profile);schemas.guard()
grant=importlib.import_module(api.name+'.agent_challenge_grant');records,period=grant.source_records();cut=grant.native_cut()
observed_at=datetime.now(timezone.utc)
if not grant.utc(period['not_before'])<=observed_at<grant.utc(period['expires_at']):
    raise ValueError('Actual fixture Source period is not current for installed startup; generate a new fixture')
print(json.dumps({'result':'PASS-installed-cold-source-schemas-grant','source_sha256':source,'profile_sha256':profile,'current_contest_input_kinds':sorted(records),'source_cut':cut,'source_expires_at':period['expires_at'],'source_period_current_observed_at':observed_at.isoformat(),'elapsed_seconds':round(time.monotonic()-started,3),'process_proof':P.process_proof(),'resources':{'RLIMIT_NOFILE':list(resource.getrlimit(resource.RLIMIT_NOFILE)),'open_descriptors_at_terminal':len(os.listdir('/proc/self/fd')),'max_resident_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},'live_Session_observed':False,'full345_qualified':False,'authority_effect':'none'},sort_keys=True),flush=True)
