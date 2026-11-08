#!/usr/bin/env python3
"""Alch local host-service client. Tokens are supplied by the caller or environment."""
import argparse
import http.client
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib.parse import urlsplit

SLUG=r'[a-z][a-z0-9-]{0,63}'

class ClientError(Exception):
    def __init__(self,code,status=None):
        super().__init__(code);self.code=code;self.status=status

class Client:
    def __init__(self,url,token,timeout=10):
        parsed=urlsplit(url)
        if (parsed.scheme!='http' or parsed.hostname not in ('127.0.0.1','::1') or parsed.username or parsed.password
                or parsed.path not in ('','/') or parsed.query or parsed.fragment):raise ClientError('LOCAL_SERVICE_URL_REQUIRED')
        try:self.port=parsed.port or 80
        except ValueError:raise ClientError('LOCAL_SERVICE_URL_REQUIRED') from None
        if not isinstance(token,str) or not re.fullmatch(r'[A-Za-z0-9_-]{32,256}',token):raise ClientError('TOKEN_REQUIRED')
        if not isinstance(timeout,(int,float)) or not 0<timeout<=120:raise ClientError('TIMEOUT_RANGE')
        self.host=parsed.hostname;self.token=token;self.timeout=timeout

    @staticmethod
    def project_path(project):
        if not isinstance(project,str) or not re.fullmatch(SLUG,project):raise ClientError('PROJECT_ID')
        return '/v1/projects/'+project

    def revision_path(self,project,revision):
        if not isinstance(revision,str) or not re.fullmatch('[a-f0-9]{32}',revision):raise ClientError('REVISION_ID')
        return self.project_path(project)+'/revisions/'+revision

    def request(self,method,path,body=None,timeout=None):
        payload=None if body is None else json.dumps(body,allow_nan=False,separators=(',',':')).encode()
        if payload is not None and len(payload)>262144:raise ClientError('REQUEST_TOO_LARGE')
        conn=http.client.HTTPConnection(self.host,self.port,timeout=self.timeout if timeout is None else min(timeout,self.timeout))
        try:
            conn.request(method,path,payload,{'Authorization':'Bearer '+self.token,'Content-Type':'application/json'})
            response=conn.getresponse();raw=response.read(262145)
            if len(raw)>262144:raise ClientError('RESPONSE_LIMIT')
            try:value=json.loads(raw)
            except (ValueError,UnicodeError):raise ClientError('RESPONSE_PROTOCOL') from None
            if not isinstance(value,dict):raise ClientError('RESPONSE_PROTOCOL')
            if not 200<=response.status<300:
                code=value.get('error','HTTP_ERROR')
                raise ClientError(code if isinstance(code,str) and re.fullmatch('[A-Z_]+',code) else 'HTTP_ERROR',response.status)
            return value
        except ClientError as e:
            if method=='POST' and e.status is None:raise ClientError('OUTCOME_UNKNOWN') from None
            raise
        except (OSError,TimeoutError,http.client.HTTPException):
            raise ClientError('OUTCOME_UNKNOWN' if method=='POST' else 'SERVICE_UNAVAILABLE') from None
        finally:conn.close()

    def create_project(self,project):return self.request('POST',self.project_path(project),{})
    def project(self,project):return self.request('GET',self.project_path(project))
    def build(self,project,source):
        if not isinstance(source,str) or not source.strip():raise ClientError('SOURCE_REQUIRED')
        return self.request('POST',self.project_path(project)+'/revisions',{'source':source})
    def revision(self,project,revision):return self.request('GET',self.revision_path(project,revision))
    def wait_ready(self,project,revision,timeout=180,interval=.2):
        if not isinstance(timeout,(int,float)) or not 0<timeout<=3600 or not .05<=interval<=10:raise ClientError('WAIT_RANGE')
        path=self.revision_path(project,revision);deadline=time.monotonic()+timeout
        while True:
            remaining=deadline-time.monotonic()
            if remaining<=0:raise ClientError('BUILD_WAIT_TIMEOUT')
            value=self.request('GET',path,timeout=remaining);status=value.get('status')
            if status=='ready':return value
            if status=='failed':raise ClientError('BUILD_FAILED')
            if status not in ('queued','building'):raise ClientError('REVISION_PROTOCOL')
            time.sleep(min(interval,max(0,deadline-time.monotonic())))
    def functions(self,project):
        snapshot=self.project(project);revisions={r['id']:r for r in snapshot['revisions']};functions=[]
        for route in snapshot['routes']:
            revision=revisions.get(route['revision'])
            if revision is None or revision['status']!='ready':raise ClientError('SELECTION_INCONSISTENT')
            functions.append({'function':route['function'],'revision':route['revision'],'selection':'selected','source_sha256':revision['source'],'artifact_sha256':revision['artifact']})
        return {'project':project,'functions':sorted(functions,key=lambda f:f['function'])}
    def prepare(self,project,revision):return self.request('POST',self.revision_path(project,revision)+'/prepare',{})
    def activate(self,project,revision):return self.request('POST',self.revision_path(project,revision)+'/activate',{})
    def invoke(self,project,function,body):
        if not isinstance(function,str) or not re.fullmatch(SLUG,function):raise ClientError('FUNCTION_ID')
        if not isinstance(body,dict) or set(body)!={'facts','message_id','expected_version'}:raise ClientError('INVOCATION_ENVELOPE')
        if not isinstance(body['facts'],dict) or not isinstance(body['message_id'],str) or not body['message_id'] or type(body['expected_version']) is not int or not 0<=body['expected_version']<=9007199254740991:raise ClientError('INVOCATION_ENVELOPE')
        return self.request('POST',self.project_path(project)+'/functions/'+function+'/invoke',body)

    def function_path(self,project,function):
        if not isinstance(function,str) or not re.fullmatch(SLUG,function):raise ClientError('FUNCTION_ID')
        return self.project_path(project)+'/functions/'+function
    def status(self,project,function):return self.request('GET',self.function_path(project,function)+'/status')
    def lifecycle_request(self,project,function,request_id,timeout=None):
        if not isinstance(request_id,str) or not re.fullmatch('[a-zA-Z0-9_-]{1,64}',request_id):raise ClientError('REQUEST_ID')
        return self.request('GET',self.function_path(project,function)+'/requests/'+request_id,timeout=timeout)
    def control(self,project,function,action,expected,request_id):
        if action not in ('drain','resume','restart'):raise ClientError('ACTION_INVALID')
        if not isinstance(expected,str) or not re.fullmatch('[a-f0-9]{64}',expected):raise ClientError('FENCE_REQUIRED')
        if not isinstance(request_id,str) or not re.fullmatch('[a-zA-Z0-9_-]{1,64}',request_id):raise ClientError('REQUEST_ID')
        return self.request('POST',self.function_path(project,function)+'/'+action,{'expected':expected,'request_id':request_id})
    def wait_control(self,project,function,request_id,timeout=90):
        if not isinstance(timeout,(int,float)) or not 0<timeout<=3600:raise ClientError('WAIT_RANGE')
        deadline=time.monotonic()+timeout
        while True:
            remaining=deadline-time.monotonic()
            if remaining<=0:raise ClientError('CONTROL_WAIT_TIMEOUT')
            value=self.lifecycle_request(project,function,request_id,timeout=remaining)
            if value['status'] in ('succeeded','blocked','failed','outcome_unknown'):return value
            if value['status'] not in ('queued','running'):raise ClientError('CONTROL_PROTOCOL')
            time.sleep(min(.1,max(0,deadline-time.monotonic())))


def main(argv=None):
    parser=argparse.ArgumentParser(description='Use the local Alch host service; token comes from ALCH_SERVICE_TOKEN.')
    parser.add_argument('--url',default=os.environ.get('ALCH_SERVICE_URL','http://127.0.0.1:8080'))
    parser.add_argument('--timeout',type=float,default=10)
    commands=parser.add_subparsers(dest='command',required=True)
    for name in ['create-project','project','functions']:
        commands.add_parser(name).add_argument('project')
    build=commands.add_parser('build');build.add_argument('project');build.add_argument('source',type=Path);build.add_argument('--wait',action='store_true');build.add_argument('--wait-seconds',type=float,default=180)
    for name in ['revision','prepare','activate']:
        command=commands.add_parser(name);command.add_argument('project');command.add_argument('revision')
    invoke=commands.add_parser('invoke');invoke.add_argument('project');invoke.add_argument('function');invoke.add_argument('--input',type=Path,required=True)
    for name in ['status','drain','resume','restart','lifecycle-request']:
        command=commands.add_parser(name);command.add_argument('project');command.add_argument('function')
        if name=='lifecycle-request':command.add_argument('request_id')
        elif name!='status':
            command.add_argument('--expected',required=True);command.add_argument('--request-id',required=True)
            command.add_argument('--wait',action='store_true');command.add_argument('--wait-seconds',type=float,default=90)
    args=parser.parse_args(argv)
    try:
        client=Client(args.url,os.environ.get('ALCH_SERVICE_TOKEN',''),args.timeout)
        if args.command=='status':value=client.status(args.project,args.function)
        elif args.command=='lifecycle-request':value=client.lifecycle_request(args.project,args.function,args.request_id)
        elif args.command in ('drain','resume','restart'):
            value=client.control(args.project,args.function,args.command,args.expected,args.request_id)
            if args.wait:value=client.wait_control(args.project,args.function,args.request_id,args.wait_seconds)
        elif args.command=='create-project':value=client.create_project(args.project)
        elif args.command in ('project','functions'):value=getattr(client,args.command)(args.project)
        elif args.command=='build':
            if args.source.suffix!='.alch':raise ClientError('ALCH_SOURCE_REQUIRED')
            source=args.source.read_text();value=client.build(args.project,source)
            if args.wait:
                revision=value['revision']
                try:value=client.wait_ready(args.project,revision,args.wait_seconds)
                except ClientError as e:
                    print(json.dumps({'error':e.code,'revision':revision}),file=sys.stderr);return 1
        elif args.command in ('revision','prepare','activate'):value=getattr(client,args.command)(args.project,args.revision)
        else:value=client.invoke(args.project,args.function,json.loads(args.input.read_bytes()))
        print(json.dumps(value,indent=2));return 1 if args.command in ('drain','resume','restart','lifecycle-request') and value.get('status') in ('blocked','failed','outcome_unknown') else 0
    except ClientError as e:
        value={'error':e.code}
        if hasattr(args,'request_id'):value['request_id']=args.request_id
        if e.status is not None:value['http_status']=e.status
        if e.code=='OUTCOME_UNKNOWN':value['next_action']='Inspect lifecycle-request using the same request ID.' if hasattr(args,'request_id') else 'Inspect service state; retry invocations only with the identical message ID, facts and expected version.'
        print(json.dumps(value),file=sys.stderr);return 1
    except (OSError,ValueError,KeyError,TypeError):
        print(json.dumps({'error':'INVALID_INPUT_OR_RESPONSE'}),file=sys.stderr);return 1

if __name__=='__main__':raise SystemExit(main())
