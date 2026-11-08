"""Exercise the client against actual queued builds, Rust hosts and revision recovery."""
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import unittest
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'semantic-corrections-v1'))
import test_controller as previous
from client import Client,ClientError

class ServiceClientIntegration(previous.Controller):
    @classmethod
    def sdk(cls,user='alice'):
        return Client(f'http://127.0.0.1:{cls.port}',(user+'_fixture_')*5,timeout=100)
    @classmethod
    def build(cls,source):
        submitted=cls.sdk().build('shop',source)
        result=cls.sdk().wait_ready('shop',submitted['revision'],timeout=230)
        assert result['status']=='ready'
        return submitted['revision']
    @classmethod
    def cleanup(cls):
        # Preserve the prior candidate's evidence files; only this test's resources are owned here.
        cls.stop();keys=set()
        if (cls.root/'registry.sqlite').exists():
            with sqlite3.connect(cls.root/'registry.sqlite') as db:
                for table,column in [('function_states','state_key'),('migrations','old_key'),('migrations','new_key')]:
                    if db.execute('SELECT 1 FROM sqlite_master WHERE name=?',(table,)).fetchone():keys.update(r[0] for r in db.execute(f'SELECT {column} FROM {table}'))
        for key in keys:shutil.rmtree('/tmp/alch-provision-semantic-controller-'+key,ignore_errors=True)
        shutil.rmtree(cls.root,ignore_errors=True)
    def test_05_client_project_listing_invocation_and_cli(self):
        c=self.sdk();self.assertEqual(c.create_project('sdk')['project'],'sdk');self.assertEqual(c.functions('sdk')['functions'],[])
        selected=c.functions('shop')['functions'];self.assertEqual(selected[0]['revision'],self.new)
        self.assertEqual(c.revision('shop',self.new)['status'],'ready')
        self.assertEqual(c.invoke('shop','orders-local',self.body)['status'],'already-committed')
        self.assertEqual(self.sdk('bob').functions('shop')['functions'],[])
        with self.assertRaises(ClientError):self.sdk('bob').prepare('shop',self.new)
        self.assertEqual(c.activate('shop',self.new)['status'],'already-selected')
        p=subprocess.run([sys.executable,str(HERE/'client.py'),'--url',f'http://127.0.0.1:{self.port}','functions','shop'],env={**os.environ,'ALCH_SERVICE_TOKEN':('alice_fixture_')*5},text=True,capture_output=True,timeout=15)
        self.assertEqual(p.returncode,0,p.stderr);self.assertEqual(json.loads(p.stdout)['functions'],selected)

if __name__=='__main__':unittest.main(verbosity=2)
