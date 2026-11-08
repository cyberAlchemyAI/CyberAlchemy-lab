#!/usr/bin/env python3
"""Compatible drained handoff over the durable asynchronous Alch control plane."""
import argparse
import http.client
import importlib.util
import json
import os
from pathlib import Path
import secrets
import selectors
import signal
import subprocess
import sys
import threading
from compatibility import fingerprint

HERE=Path(__file__).resolve().parent
ASYNC=HERE.parent/'async-control-plane-v1'
spec=importlib.util.spec_from_file_location('alch_async_control',ASYNC/'control_plane.py')
queue=importlib.util.module_from_spec(spec);spec.loader.exec_module(queue)
base=queue.base
require,Rejected,sha,encoded=queue.require,queue.Rejected,queue.sha,queue.encoded


class Plane(queue.Plane):
    @staticmethod
    def support_binding():
        return {'schema':'alch.compatible-upgrades/v1','files':{str(f):sha(f.read_bytes()) for f in
                [HERE/'control_plane.py',HERE/'function_host.py',HERE/'compatibility.py',ASYNC/'control_plane.py',base.HERE/'control_plane.py']}}

    def __init__(self,root,config):
        self.running_revisions={}
        super().__init__(root,config)
        try:
            self.db.execute('''CREATE TABLE IF NOT EXISTS function_states(
                tenant TEXT,project TEXT,function TEXT,contract TEXT,state_key TEXT UNIQUE,
                PRIMARY KEY(tenant,project,function),
                FOREIGN KEY(tenant,project) REFERENCES projects(tenant,project))''')
            self.db.commit()
        except Exception:
            self.close();raise

    def state_key(self,tenant,project,function):
        return sha(encoded([str(self.root),tenant,project,function]))

    def run_root(self,key):
        return '/tmp/alch-provision-upgrade-'+key

    def runtime(self,row,user):
        self.verify_support()
        bundle,cfg=self.verify(row,user)
        return bundle,cfg,fingerprint(bundle)

    def state(self,tenant,project,function):
        return self.db.execute('SELECT * FROM function_states WHERE tenant=? AND project=? AND function=?',(tenant,project,function)).fetchone()

    def stop_host(self,key):
        if key not in self.children:return
        proc,_,_=self.children[key]
        if proc.poll() is None:
            proc.terminate()
            try:proc.wait(timeout=20)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid,signal.SIGKILL);proc.wait()
        if proc.stdout:proc.stdout.close()
        del self.children[key];self.running_revisions.pop(key,None)

    def launch(self,row,user,key,contract):
        bundle,cfg,actual=self.runtime(row,user)
        require(actual==contract,'INCOMPATIBLE_REVISION',409)
        if key in self.children:
            proc,port,token=self.children[key]
            if proc.poll() is None:
                require(self.running_revisions[key]==row['id'],'REVISION_SWITCH_REQUIRED',409)
                return port,token,cfg
            self.stop_host(key)
        require(len(self.children)<8,'HOST_CAPACITY',503)
        token=secrets.token_urlsafe(32)
        proc=subprocess.Popen([sys.executable,str(base.HERE/'control_plane.py'),'--host-launch',str(HERE/'function_host.py'),
                               '--bundle',str(bundle),'--run-root',self.run_root(key),'--contract',contract,'--state-key',key],
                              stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,start_new_session=True,
                              env={'PATH':'/usr/bin:/bin','PYTHONDONTWRITEBYTECODE':'1','ALCH_HOST_TOKEN':token,'ALCH_HOST_POLICY':json.dumps(user['policy'])})
        try:
            with selectors.DefaultSelector() as selector:
                selector.register(proc.stdout,selectors.EVENT_READ)
                require(bool(selector.select(30)),'HOST_START_FAILED',503)
                result=json.loads(proc.stdout.readline())
            require(result.get('status')=='listening','HOST_START_FAILED',503)
            port=int(result['url'].rsplit(':',1)[1])
            self.children[key]=(proc,port,token);self.running_revisions[key]=row['id']
            return port,token,cfg
        except Exception:
            if proc.poll() is None:
                proc.terminate()
                try:proc.wait(timeout=20)
                except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
            if proc.stdout:proc.stdout.close()
            raise Rejected('HOST_START_FAILED',503)

    def host(self,row,user):
        state=self.state(user['id'],row['project'],row['function'])
        require(state is not None,'STATE_BINDING_MISSING',409)
        key=self.state_key(user['id'],row['project'],row['function'])
        require(key==state['state_key'],'STATE_BINDING_DRIFT',409)
        return self.launch(row,user,key,state['contract'])

    def host_control(self,key,action):
        _,port,token=self.children[key]
        conn=http.client.HTTPConnection('127.0.0.1',port,timeout=40)
        try:
            conn.request('POST','/_host/'+action,b'',{'Authorization':'Bearer '+token})
            response=conn.getresponse();value=json.loads(response.read())
            require(response.status==200,value.get('error','HOST_CONTROL_FAILED'),409)
            return value
        except (OSError,TimeoutError,http.client.HTTPException):
            raise Rejected('HOST_CONTROL_UNKNOWN',503)
        finally:conn.close()

    def activate(self,user,project,revision):
        self.scope(user,project,'activate')
        row=self.revision(user,project,revision)
        _,cfg,contract=self.runtime(row,user)
        function=cfg['id'];key=self.state_key(user['id'],project,function)
        state=self.state(user['id'],project,function)
        if state is not None:
            require(state['contract']==contract and state['state_key']==key,'INCOMPATIBLE_REVISION',409)
        selected=self.db.execute('SELECT revision FROM routes WHERE tenant=? AND project=? AND function=?',(user['id'],project,function)).fetchone()
        old=self.revision(user,project,selected['revision']) if selected else None
        if old is not None and old['id']==revision:
            self.host(old,user)
            return {'function':function,'revision':revision,'state_key':key,'status':'already-selected'}
        with self.db:self.event(user['id'],project,revision,'upgrade-requested')
        try:
            if old is not None:
                self.host(old,user)
                self.host_control(key,'drain')
                with self.db:self.event(user['id'],project,revision,'old-revision-drained')
                self.stop_host(key)
            self.launch(row,user,key,contract)
            with self.db:
                self.db.execute('INSERT OR IGNORE INTO function_states VALUES(?,?,?,?,?)',(user['id'],project,function,contract,key))
                self.db.execute('INSERT INTO routes VALUES(?,?,?,?) ON CONFLICT(tenant,project,function) DO UPDATE SET revision=excluded.revision',(user['id'],project,function,revision))
                self.event(user['id'],project,revision,'route-selected')
            return {'function':function,'revision':revision,'state_key':key,'status':'selected'}
        except Exception:
            # The registry remains authoritative. If commit outcome is uncertain,
            # restore whichever revision is actually selected, never guess.
            selected=self.db.execute('SELECT revision FROM routes WHERE tenant=? AND project=? AND function=?',(user['id'],project,function)).fetchone()
            if selected:
                restore=self.revision(user,project,selected['revision'])
                if key in self.children and self.running_revisions[key]!=restore['id']:
                    self.stop_host(key)
                try:
                    self.host(restore,user)
                    self.host_control(key,'resume')
                except Exception:
                    with self.db:self.event(user['id'],project,revision,'host-recovery-required')
            else:self.stop_host(key)
            with self.db:self.event(user['id'],project,revision,'upgrade-not-confirmed')
            raise

    def restore_selected(self):
        # Called before listening: pending events resume even with no new invoke.
        for route in self.db.execute('SELECT * FROM routes ORDER BY tenant,project,function').fetchall():
            user=next((u for u in self.users.values() if u['id']==route['tenant']),None)
            require(user is not None,'SELECTED_OWNER_UNAVAILABLE',403)
            row=self.revision(user,route['project'],route['revision'])
            self.host(row,user)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',required=True);parser.add_argument('--config',required=True)
    parser.add_argument('--port',type=int,default=0)
    args=parser.parse_args();require(0<=args.port<=65535,'PORT_INVALID');os.umask(0o077)
    plane=Plane(args.root,json.loads(Path(args.config).read_bytes()));server=None
    try:
        plane.restore_selected()
        server=queue.serve(plane,args.port);plane.start_worker()
        def stop(*_):threading.Thread(target=server.shutdown,daemon=True).start()
        signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
        print(json.dumps({'status':'listening','url':f'http://127.0.0.1:{server.server_port}'}),flush=True)
        server.serve_forever(poll_interval=.1)
    finally:
        if server:server.server_close()
        plane.close()


if __name__=='__main__':main()
