"""Report actual recorded phases and Session lease margins, without opening one."""
import argparse,hashlib,json,os
from datetime import datetime
from pathlib import Path

def need(v,m):
 if not v:raise ValueError(m)
def raw(path):
 p=Path(path);need(not any(x.is_symlink()for x in(p,*p.parents)),'linked evidence');return p.read_bytes()
def stamp(s):return datetime.fromisoformat(s.replace('Z','+00:00'))
def report(folder):
 p=Path(folder);events=[json.loads(v)for v in raw(p/'events.jsonl').splitlines()]
 def reply(op):
  paths=list(p.glob('*-'+op+'-reply.json'));need(len(paths)==1,'unique actual '+op+' reply required');body=json.loads(raw(paths[0]));need(body['kind']=='result','actual positive reply required');return body['message']
 opened=reply('session-open');closed=reply('session-close');start,end,expiry=map(stamp,(opened['started_at'],closed['ended_at'],opened['expires_at']))
 need(opened['session_ref']==closed['session_ref']and start<end<expiry,'actual Session did not complete inside its retained lease')
 need(0<(expiry-start).total_seconds()<=3600,'actual independently declared lease budget differs')
 phases=[{'phase':e['phase'],'state':e['state'],'elapsed_seconds':e['elapsed_seconds']}for e in events if e.get('state')in('passed','failed')and'elapsed_seconds'in e]
 need(not any(e['state']=='failed'for e in phases),'failed phase in accepted sequence')
 return {'session_ref_sha256':hashlib.sha256(opened['session_ref'].encode()).hexdigest(),'started_at':opened['started_at'],'ended_at':closed['ended_at'],'expires_at':opened['expires_at'],'actual_live_seconds':round((end-start).total_seconds(),6),'remaining_lease_seconds_at_explicit_close':round((expiry-end).total_seconds(),6),'actual_initial_lease_seconds':round((expiry-start).total_seconds(),6),'elapsed_event_window_seconds':round((stamp(events[-1]['at_utc'])-stamp(events[0]['at_utc'])).total_seconds(),6),'phases':phases,'events_sha256':hashlib.sha256(raw(p/'events.jsonl')).hexdigest()}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--first',required=True);p.add_argument('--later',required=True);p.add_argument('--consumer',required=True);p.add_argument('--output',required=True);a=p.parse_args()
 value={'schema_version':'lab-actual-learning-Session-timings/v1','authority_effect':'none','result':'PASS-three-actual-Sessions-completed-with-positive-lease-margin','Sessions':{k:report(getattr(a,k))for k in('first','later','consumer')},'declared_load':{'maximum_concurrent_Source_heavy_jobs':2,'host':'shared WSL build workstation','other_workstation_process_load_controlled':False,'diagnostic_margin_mode':True,'new_Session_maximum_seconds':3600,'old900_second_family_changed':False},'claim_ceiling':'Actual phase observations and retained independent Session leases on this fixture run; no production performance guarantee or extension of an old lease.'}
 need(len({x['session_ref_sha256']for x in value['Sessions'].values()})==3,'three distinct actual Sessions required');b=(json.dumps(value,sort_keys=True,indent=2)+'\n').encode();fd=os.open(a.output,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'wb')as f:f.write(b)
 print(json.dumps({'result':value['result'],'sha256':hashlib.sha256(b).hexdigest()}))
