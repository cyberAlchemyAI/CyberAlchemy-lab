#!/usr/bin/env python3
"""Candidate additive migrations over compatible upgrades; fresh registry roots only."""
import argparse
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import secrets
import signal
import sqlite3
import sys
import threading
from migration import validate_change,snapshot,transform,logical_digest

HERE=Path(__file__).resolve().parent
UPGRADE=HERE.parent/'compatible-upgrades-v1'
sys.path.insert(0,str(UPGRADE))
spec=importlib.util.spec_from_file_location('alch_compatible_control',UPGRADE/'control_plane.py')
upgrade=importlib.util.module_from_spec(spec);spec.loader.exec_module(upgrade)
base=upgrade.base;queue=upgrade.queue
require,Rejected,sha,encoded=upgrade.require,upgrade.Rejected,upgrade.sha,upgrade.encoded

class Plane(upgrade.Plane):
    @staticmethod
    def support_binding():
        return {'schema':'alch.state-migrations/v1','files':{**upgrade.Plane.support_binding()['files'],
                **{str(p):sha(p.read_bytes()) for p in (HERE/'control_plane.py',HERE/'migration.py')}}}

    def __init__(self,root,config):
        super().__init__(root,config)
        with self.db:self.db.execute('''CREATE TABLE IF NOT EXISTS migrations(
            id TEXT PRIMARY KEY,tenant TEXT,project TEXT,function TEXT,revision TEXT,
            old_key TEXT,new_key TEXT,stage TEXT,receipt TEXT)''')

    def run_root(self,key):return '/tmp/alch-provision-migration-'+key
    def database(self,key):return Path(self.run_root(key))/'target/state/runtime/function.sqlite'

    def status(self,user,project,revision):
        result=super().status(user,project,revision)
        if result['status']=='ready':
            row=self.revision(user,project,revision)
            bundle,_,contract=self.runtime(row,user)
            result['state_contract']=contract
            if (bundle/'migration.json').exists():
                declaration=json.loads((bundle/'migration.json').read_bytes())
                result['migration']={k:declaration[k] for k in ('id','from_contract','subject','field','mapper')}
        return result

    def host(self,row,user):
        state=self.state(user['id'],row['project'],row['function'])
        require(state is not None,'STATE_BINDING_MISSING',409)
        return self.launch(row,user,state['state_key'],state['contract'])

    def select(self,user,project,row,contract,key,attempt=None,receipt=None):
        with self.db:
            self.db.execute('INSERT INTO function_states VALUES(?,?,?,?,?) ON CONFLICT(tenant,project,function) DO UPDATE SET contract=excluded.contract,state_key=excluded.state_key',
                            (user['id'],project,row['function'],contract,key))
            self.db.execute('INSERT INTO routes VALUES(?,?,?,?) ON CONFLICT(tenant,project,function) DO UPDATE SET revision=excluded.revision',
                            (user['id'],project,row['function'],row['id']))
            if attempt:self.db.execute("UPDATE migrations SET stage='selected',receipt=? WHERE id=?",(json.dumps(receipt),attempt))
            self.event(user['id'],project,row['id'],'route-selected')

    def activate(self,user,project,revision):
        self.scope(user,project,'activate');row=self.revision(user,project,revision)
        bundle,cfg,contract=self.runtime(row,user);function=cfg['id']
        selected=self.db.execute('SELECT revision FROM routes WHERE tenant=? AND project=? AND function=?',(user['id'],project,function)).fetchone()
        old=self.revision(user,project,selected['revision']) if selected else None
        state=self.state(user['id'],project,function)
        require((state is None)==(old is None),'STATE_BINDING_DRIFT',409)
        old_key=state['state_key'] if state else self.state_key(user['id'],project,function)
        if old and old['id']==revision:
            self.host(old,user);return {'status':'already-selected','function':function,'revision':revision,'state_key':old_key}
        migrating=state is not None and state['contract']!=contract
        manifest=None;attempt=None;receipt=None;key=old_key
        if migrating:
            require((bundle/'migration.json').is_file(),'MIGRATION_REQUIRED_ROLLBACK_UNSAFE',409)
            old_bundle,_,_=self.runtime(old,user)
            try:manifest=validate_change(old_bundle,bundle,state['contract'])
            except (ValueError,KeyError,StopIteration) as e:raise Rejected(str(e),409)
            attempt=secrets.token_hex(16);key=sha(encoded([old_key,revision,attempt]))
            with self.db:self.db.execute('INSERT INTO migrations VALUES(?,?,?,?,?,?,?,?,?)',(attempt,user['id'],project,function,revision,old_key,key,'requested',None))
        elif state is None:
            require(not (bundle/'migration.json').exists(),'MIGRATION_SOURCE_REQUIRED',409)
        try:
            if old:
                self.host(old,user)
                if migrating:
                    work=self.root/'migration-attempts'/attempt;work.mkdir(parents=True,mode=0o700)
                    rehearsal=work/'rehearsal.sqlite';snapshot(self.database(old_key),rehearsal)
                    rehearsed_from=sha(rehearsal.read_bytes())
                    rehearsal_receipt=transform(rehearsal,bundle,manifest,base.NODE)
                    with self.db:self.db.execute("UPDATE migrations SET stage='rehearsed',receipt=? WHERE id=?",(json.dumps({'source_sha256':rehearsed_from,**rehearsal_receipt}),attempt))
                self.host_control(old_key,'drain');self.stop_host(old_key)
            if migrating:
                # Provision a fresh generation through the same RWO/Ansible path.
                self.launch(row,user,key,contract);self.stop_host(key)
                candidate=work/'candidate.sqlite';snapshot(self.database(old_key),candidate)
                source_digest=sha(candidate.read_bytes())
                receipt={'source_sha256':source_digest,'source_contract':state['contract'],'target_contract':contract,
                         'source_revision':old['id'],'target_revision':revision,'rehearsal':rehearsal_receipt,
                         **transform(candidate,bundle,manifest,base.NODE)}
                root=Path(self.run_root(key))
                with (root/'owner.lock').open('rb') as lock:
                    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
                    with sqlite3.connect(candidate) as src,sqlite3.connect(self.database(key)) as dst:src.backup(dst)
                    with sqlite3.connect(self.database(key)) as dst:
                        dst.execute('PRAGMA wal_checkpoint(TRUNCATE)')
                        require(dst.execute('PRAGMA integrity_check').fetchall()==[('ok',)],'DATABASE_INTEGRITY')
                        require(logical_digest(dst)==receipt['logical_sha256'],'INSTALLED_STATE_MISMATCH')
                    with self.database(key).open('rb') as stream:os.fsync(stream.fileno())
                    descriptor=os.open(self.database(key).parent,os.O_DIRECTORY)
                    try:os.fsync(descriptor)
                    finally:os.close(descriptor)
                with self.db:self.db.execute("UPDATE migrations SET stage='prepared',receipt=? WHERE id=?",(json.dumps(receipt),attempt))
            self.launch(row,user,key,contract)
            self.select(user,project,row,contract,key,attempt,receipt)
            return {'status':'selected','function':function,'revision':revision,'state_key':key,'migration':attempt}
        except Exception as error:
            # Route and generation commit together. On uncertain commit restore the durable selection.
            selected=self.db.execute('SELECT revision FROM routes WHERE tenant=? AND project=? AND function=?',(user['id'],project,function)).fetchone()
            current=self.state(user['id'],project,function)
            for candidate_key in {old_key,key}:
                if current is None or candidate_key!=current['state_key']:self.stop_host(candidate_key)
            if selected:
                restore=self.revision(user,project,selected['revision'])
                current_key=current['state_key']
                if current_key in self.children and self.running_revisions[current_key]!=restore['id']:self.stop_host(current_key)
                try:self.host(restore,user);self.host_control(current_key,'resume')
                except Exception:
                    with self.db:self.event(user['id'],project,revision,'host-recovery-required')
            if attempt:
                with self.db:self.db.execute("UPDATE migrations SET stage='not-confirmed' WHERE id=? AND stage!='selected'",(attempt,))
            if isinstance(error,Rejected):raise
            raise Rejected('MIGRATION_FAILED',409) from error

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',required=True);parser.add_argument('--config',required=True);parser.add_argument('--port',type=int,default=0)
    args=parser.parse_args();os.umask(0o077);require(0<=args.port<=65535,'PORT_INVALID')
    plane=Plane(args.root,json.loads(Path(args.config).read_bytes()));server=None
    try:
        plane.restore_selected();server=queue.serve(plane,args.port);plane.start_worker()
        def stop(*_):threading.Thread(target=server.shutdown,daemon=True).start()
        signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
        print(json.dumps({'status':'listening','url':f'http://127.0.0.1:{server.server_port}'}),flush=True)
        server.serve_forever(poll_interval=.1)
    finally:
        if server:server.server_close()
        plane.close()

if __name__=='__main__':main()
