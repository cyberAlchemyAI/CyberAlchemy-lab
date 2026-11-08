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
from planner import derive_change,snapshot,transform,logical_digest,ontology,previous
from jsonschema import Draft202012Validator,FormatChecker
from http.server import BaseHTTPRequestHandler,HTTPServer
import re

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
        return {'schema':'alch.ontology-schema/v1','files':{**upgrade.Plane.support_binding()['files'],
                **{str(p):sha(p.read_bytes()) for p in (HERE/'control_plane.py',HERE/'planner.py',HERE.parent/'state-migrations-v1/migration.py')}}}

    def __init__(self,root,config):
        super().__init__(root,config)
        with self.db:self.db.execute('''CREATE TABLE IF NOT EXISTS migrations(
            id TEXT PRIMARY KEY,tenant TEXT,project TEXT,function TEXT,revision TEXT,
            old_key TEXT,new_key TEXT,stage TEXT,receipt TEXT)''')
        with self.db:self.db.execute('CREATE TABLE IF NOT EXISTS prepared(revision TEXT PRIMARY KEY,plan TEXT NOT NULL)')

    def run_root(self,key):return '/tmp/alch-provision-ontology-'+key
    def database(self,key):return Path(self.run_root(key))/'target/state/runtime/function.sqlite'

    def build(self,user,project,source):
        require(isinstance(source,str) and re.search(r'^profile ontology-host-v1$',source,re.M),'ONTOLOGY_PROFILE_REQUIRED')
        return super().build(user,project,source)

    def runtime(self,row,user):
        bundle,cfg,contract=super().runtime(row,user)
        try:ontology(bundle)
        except (OSError,ValueError,KeyError) as e:raise Rejected('ONTOLOGY_SCHEMA_INVALID',409) from e
        return bundle,cfg,contract

    def baseline(self,user,project,function):
        route=self.db.execute('SELECT revision FROM routes WHERE tenant=? AND project=? AND function=?',(user['id'],project,function)).fetchone()
        state=self.state(user['id'],project,function)
        require((route is None)==(state is None),'STATE_BINDING_DRIFT',409)
        if route is None:return None
        old=self.revision(user,project,route['revision'])
        epoch=self.db.execute('''SELECT MAX(j.seq) FROM journal j JOIN revisions r ON
            j.tenant=r.tenant AND j.project=r.project AND j.revision=r.id
            WHERE j.tenant=? AND j.project=? AND r.function=? AND j.stage='route-selected' ''',(user['id'],project,function)).fetchone()[0]
        return {'revision':old['id'],'artifact':old['artifact'],'contract':state['contract'],'state_key':state['state_key'],'route_epoch':epoch}

    def prepare(self,user,project,revision):
        self.scope(user,project,'build');row=self.revision(user,project,revision)
        bundle,cfg,contract=self.runtime(row,user);baseline=self.baseline(user,project,cfg['id'])
        saved=self.db.execute('SELECT plan FROM prepared WHERE revision=?',(revision,)).fetchone()
        if saved:
            plan=json.loads(saved['plan'])
            require(plan['baseline']==baseline,'BASELINE_CHANGED',409)
            require(plan['target_artifact']==row['artifact'] and plan['target_contract']==contract,'PREPARED_TARGET_CHANGED',409)
            return plan
        migration=None
        if baseline:
            old=self.revision(user,project,baseline['revision']);old_bundle,_,old_contract=self.runtime(old,user)
            require(old_contract==baseline['contract'],'STATE_BINDING_DRIFT',409)
            if old_contract!=contract:
                try:migration=derive_change(old_bundle,bundle,old_contract)
                except (ValueError,KeyError,StopIteration) as e:raise Rejected(str(e),409)
        plan={'schema_version':'alch.prepared-ontology-migration/v1','revision':revision,'target_artifact':row['artifact'],'target_contract':contract,
              'baseline':baseline,'migration':migration,'target_ontology_sha256':sha((bundle/'typed-ontology.json').read_bytes()),
              'kind':'initial' if baseline is None else 'additive' if migration else 'compatible','authority_effect':'none'}
        plan['digest']=sha(encoded(plan))
        with self.db:
            self.db.execute('INSERT INTO prepared VALUES(?,?)',(revision,json.dumps(plan)))
            self.event(user['id'],project,revision,'ontology-plan-prepared')
        return plan

    def invoke(self,user,project,function,body):
        self.scope(user,project,'invoke')
        require(isinstance(body,dict) and set(body)=={'facts','expected_version'},'REQUEST_FIELDS')
        route=self.db.execute('SELECT revision FROM routes WHERE tenant=? AND project=? AND function=?',(user['id'],project,function)).fetchone()
        require(route is not None,'NOT_FOUND',404)
        row=self.revision(user,project,route['revision']);bundle,cfg,_=self.runtime(row,user)
        typed=ontology(bundle);op=next(o for o in typed['operations'] if o['operation']==cfg['operation'])
        schemas=json.loads((bundle/'schemas.json').read_bytes())
        validator=Draft202012Validator(schemas['facts'][op['subject']],format_checker=FormatChecker())
        require(validator.is_valid(body['facts']),'INPUT_SCHEMA_INVALID')
        return super().invoke(user,project,function,body)

    def status(self,user,project,revision):
        result=super().status(user,project,revision)
        if result['status']=='ready':
            row=self.revision(user,project,revision)
            bundle,_,contract=self.runtime(row,user)
            result['state_contract']=contract
            result['ontology_sha256']=sha((bundle/'typed-ontology.json').read_bytes())
            prepared=self.db.execute('SELECT plan FROM prepared WHERE revision=?',(revision,)).fetchone()
            result['prepared_plan']=json.loads(prepared['plan']) if prepared else None
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
        saved=self.db.execute('SELECT plan FROM prepared WHERE revision=?',(revision,)).fetchone()
        require(saved is not None,'PREPARATION_REQUIRED',409)
        plan=json.loads(saved['plan'])
        require(plan['baseline']==self.baseline(user,project,function),'BASELINE_CHANGED',409)
        require(plan['target_artifact']==row['artifact'] and plan['target_contract']==contract,'PREPARED_TARGET_CHANGED',409)
        migrating=state is not None and state['contract']!=contract
        manifest=None;attempt=None;receipt=None;key=old_key
        if migrating:
            old_bundle,_,_=self.runtime(old,user)
            try:manifest=derive_change(old_bundle,bundle,state['contract'])
            except (ValueError,KeyError,StopIteration) as e:raise Rejected(str(e),409)
            require(manifest==plan['migration'],'PREPARED_MAPPING_CHANGED',409)
            attempt=secrets.token_hex(16);key=sha(encoded([old_key,revision,attempt]))
            with self.db:self.db.execute('INSERT INTO migrations VALUES(?,?,?,?,?,?,?,?,?)',(attempt,user['id'],project,function,revision,old_key,key,'requested',None))
        else:require(plan['migration'] is None,'PREPARED_MAPPING_CHANGED',409)
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
                         'source_revision':old['id'],'target_revision':revision,'prepared_plan_sha256':plan['digest'],'rehearsal':rehearsal_receipt,
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

def serve(plane,port=0):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*_): pass
        def setup(self):
            super().setup();self.connection.settimeout(5)
        def handle_request(self):
            try:
                auth=self.headers.get_all('Authorization',[])
                require(len(auth)==1 and auth[0].startswith('Bearer ') and not self.headers.get('Origin'),'UNAUTHORIZED',401)
                user=plane.auth(auth[0][7:]);body=None
                if self.command=='POST':
                    lengths=self.headers.get_all('Content-Length',[])
                    require(not self.headers.get('Transfer-Encoding') and len(lengths)==1 and re.fullmatch('[0-9]{1,7}',lengths[0]),'CONTENT_LENGTH_REQUIRED')
                    size=int(lengths[0]);require(size<=262144,'REQUEST_TOO_LARGE',413)
                    require(self.headers.get('Content-Type','').split(';')[0]=='application/json','JSON_REQUIRED',415)
                    raw=self.rfile.read(size);require(len(raw)==size,'INCOMPLETE_BODY')
                    body=json.loads(raw);require(isinstance(body,dict),'REQUEST_FIELDS')
                parts=self.path.split('/')
                require(len(parts)>=4 and parts[:3]==['','v1','projects'] and re.fullmatch(base.SLUG,parts[3]),'NOT_FOUND',404)
                project=parts[3];status=200
                if len(parts)==4 and self.command=='POST':
                    require(body=={},'REQUEST_FIELDS');value=plane.project(user,project)
                elif len(parts)==4 and self.command=='GET':value=plane.inspect(user,project)
                elif len(parts)==5 and parts[4]=='revisions' and self.command=='POST':
                    require(set(body)=={'source'},'REQUEST_FIELDS');value=plane.build(user,project,body['source']);status=202
                elif len(parts)==6 and parts[4]=='revisions' and re.fullmatch('[a-f0-9]{32}',parts[5]) and self.command=='GET':
                    value=plane.status(user,project,parts[5])
                elif len(parts)==7 and parts[4]=='revisions' and re.fullmatch('[a-f0-9]{32}',parts[5]) and parts[6]=='prepare' and self.command=='POST':
                    require(body=={},'REQUEST_FIELDS');value=plane.prepare(user,project,parts[5])
                elif len(parts)==7 and parts[4]=='revisions' and re.fullmatch('[a-f0-9]{32}',parts[5]) and parts[6]=='activate' and self.command=='POST':
                    require(body=={},'REQUEST_FIELDS');value=plane.activate(user,project,parts[5])
                elif len(parts)==7 and parts[4]=='functions' and re.fullmatch(base.SLUG,parts[5]) and parts[6]=='invoke' and self.command=='POST':
                    status,value=plane.invoke(user,project,parts[5],body)
                else:raise Rejected('NOT_FOUND',404)
            except Rejected as e:status,value=e.status,{'error':e.code}
            except (ValueError,UnicodeError):status,value=400,{'error':'INVALID_JSON'}
            except TimeoutError:status,value=408,{'error':'BODY_TIMEOUT'}
            except Exception:status,value=500,{'error':'CONTROL_PLANE_FAILURE'}
            data=encoded(value);self.send_response(status)
            self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)))
            self.send_header('Connection','close');self.send_header('Cache-Control','no-store');self.end_headers()
            self.close_connection=True
            try:self.wfile.write(data)
            except OSError:pass
        do_GET=handle_request
        do_POST=handle_request
    return HTTPServer(('127.0.0.1',port),Handler)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',required=True);parser.add_argument('--config',required=True);parser.add_argument('--port',type=int,default=0)
    args=parser.parse_args();os.umask(0o077);require(0<=args.port<=65535,'PORT_INVALID')
    plane=Plane(args.root,json.loads(Path(args.config).read_bytes()));server=None
    try:
        plane.restore_selected();server=serve(plane,args.port);plane.start_worker()
        def stop(*_):threading.Thread(target=server.shutdown,daemon=True).start()
        signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
        print(json.dumps({'status':'listening','url':f'http://127.0.0.1:{server.server_port}'}),flush=True)
        server.serve_forever(poll_interval=.1)
    finally:
        if server:server.server_close()
        plane.close()

if __name__=='__main__':main()
