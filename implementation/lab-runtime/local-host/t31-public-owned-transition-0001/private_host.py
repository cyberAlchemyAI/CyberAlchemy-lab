"""Named private host callbacks for original output-bearing public workflows.

Bootstrap supplies an independently bound protected input index, actual kernel
header/currentness types, and a live producer verifier. No API message installs
these objects. The public handler independently repeats record semantics/schema
checks and the selected durable store verifies committed originals.
"""
import copy
import importlib
import inspect
import json
from pathlib import Path

def need(ok,reason):
    if not ok:raise ValueError(reason)
def closed(value,fields,reason):need(type(value) is dict and set(value)==set(fields),reason)

class HostState:
    def __init__(self,host,*,input_binding,store,header_type,currentness_type,selection_type,producer_guard,scope_selection=None):
        self.host=host;self.binding=copy.deepcopy(input_binding);self.store=store
        self.header_type=header_type;self.currentness_type=currentness_type;self.selection_type=selection_type
        self.producer_guard=producer_guard;self.scope_selection=scope_selection
        pkg=type(host).__module__.rsplit('.',1)[0]
        self.P=importlib.import_module(pkg+'.protocol');self.M=importlib.import_module(pkg+'.artifact_model')
        self.C=importlib.import_module(pkg+'.handlers')
        self.original=host.vault.material(self.binding);self.index=self.P.frame_parse(self.original)
        i=self.index
        closed(i,('schema_version','scope_ref','source_cut','actor','run_ref','roles','inputs','outputs','producer_receipt_bindings','authority_effect'),
               'closed protected workflow host input index required')
        need(i['schema_version']=='lab-private-owned-workflow-host-inputs/v1' and i['authority_effect']=='none','explicit bounded private host input profile required')
        need(i['scope_ref']==host.channel.policy['scope_refs'][0] and i['source_cut']==self.C.cut(host.handlers.view), 'private host index Source/scope differs')
        closed(i['roles'],('intent','resolution','work','coordination','goal','decision','effects','decision_edges','goal_edges','decision_profile'),
               'exact protected semantic role closure required')
        need(type(i['inputs']) is dict and bool(i['inputs']),'closed exact input table required')
        need(type(i['outputs']) is dict and bool(i['outputs']) and type(i['producer_receipt_bindings']) is list and i['producer_receipt_bindings'],
               'actual original producer result and receipts required')
        for ref,rows in i['outputs'].items():
            need(type(ref) is str and ref.startswith('transition:') and type(rows) is list and rows,'closed actual producer transition output required')
            for row in rows:self._record(row)
        self.producer_identity=self._identity(producer_guard)
        self.guard()
    def _identity(self,fn):
        target=fn.__func__ if inspect.ismethod(fn) else fn
        need(inspect.isfunction(target),'actual named producer verifier required')
        path=Path(target.__code__.co_filename).resolve()
        need(path.is_relative_to(self.P.ROOT),'producer verifier origin outside selected repository')
        return target,getattr(fn,'__self__',None),target.__code__,path,self.P.source.sha(path.read_bytes())
    def _record(self,row):
        closed(row,('artifact','original_binding'),'closed independently selected original record required')
        raw=self.host.vault.material(row['original_binding'])
        need(self.P.source.sha(raw)==row['artifact']['byte_sha256'],'private original header/byte binding differs')
        return {'artifact':copy.deepcopy(row['artifact']),'original':raw}
    def guard(self):
        need(self.host.vault.material(self.binding)==self.original and self.P.compact(self.index)==self.P.compact(self.P.frame_parse(self.original)),
             'protected workflow host inputs changed')
        actual=self._identity(self.producer_guard);old=self.producer_identity
        need(all(actual[k] is old[k] for k in (0,1,2)) and actual[3:]==old[3:],'actual producer verifier changed')
        self.host.channel.termination_guard()
        need(self.C.cut(self.host.handlers.view)==self.index['source_cut'],'protected host input cut changed')
        self.producer_guard()
        for binding in self.index['producer_receipt_bindings']:self.host.vault.material(binding)
    def semantics(self,run,definition,grant):
        self.guard();need(run['run_ref']==self.index['run_ref'] and run['actor']==self.index['actor'],'actual semantic Run/Actor differs')
        result={}
        for key,value in self.index['roles'].items():
            result[key]=[self._record(row) for row in value] if key in ('effects','decision_edges','goal_edges') else self._record(value)
        result['inputs']=[]
        return result
    def headers(self,message,run,grant):
        self.guard();i=self.index
        need(run['actor']==i['actor'] and run['source_cut']==i['source_cut'] and run['run_ref']==i['run_ref'],'actual callback Actor/cut/Run differs')
        own=None;head,_=self.store.replay()
        if head['sequence']:
            producer_paths={b['ref']:self.host.vault.root/next(row['path'] for row in self.host.vault.manifest['materials']
                if row['ref']==b['ref'] and row['sha256']==b['sha256']) for b in i['producer_receipt_bindings']}
            kwargs={'source_cut':i['source_cut'],'actor':i['actor'],'work':run['work'],'run_ref':i['run_ref'],'scope_ref':i['scope_ref'],
              'producer_receipts':i['producer_receipt_bindings'],'producer_paths':producer_paths}
            if self.scope_selection is not None:kwargs['scope_selection']=self.scope_selection
            selected=self.selection_type.from_host(self.store,**kwargs);own=self.currentness_type(selected,host_guard=self.guard)
        def source_resolver(header):
            self.guard();subject=self.host.handlers.view.subjects.get(header['version_ref'])
            if subject is None or subject['effective_state'] not in ('admitted-current','local-admitted-current'):return None
            if self.M.artifact_ref(self.host.handlers.view,subject)!=header:return None
            raw,_=self.M.record_bytes(self.host.handlers.view,subject)
            need(self.P.source.sha(raw)==header['byte_sha256'],'actual signed source original differs')
            return {'artifact':header,'posture':subject['effective_state'],'semantic_kind':subject['kind']}
        def coordination_resolver(header):
            rows=[r for r in i['inputs'].values() if r['artifact']==header]
            if len(rows)!=1:return None
            raw=self._record(rows[0])['original'];body=self.P.frame_parse(raw)
            semantic=body.get('kind',header['carrier_ref'].split('cal.artifact-type.')[1].split('/')[0])
            return {'artifact':header,'posture':'owned-coordination-current','semantic_kind':semantic,'lineage_binding':copy.deepcopy(self.binding)}
        kwargs={'source_resolver':source_resolver,'owned_resolver':own,'coordination_resolver':coordination_resolver,'guard':self.guard}
        result=self.header_type(**kwargs)
        needed=message['input_artifacts']
        for sequence in range(1,head['sequence']+1):
            txraw=(self.store.root/'transactions'/f'{sequence:08d}.json').read_bytes();tx=json.loads(txraw)
            for header,raw in self.store.consume(sequence):
                if header in needed:result.select_owned(header,sequence=sequence,transaction_sha256=self.P.source.sha(txraw))
        # The handler asks for semantic input bytes independently of kernel
        # header resolution. The role callback is filled from this exact call.
        self.call_inputs=[self._record(i['inputs'][h['version_ref']]) for h in needed]
        return result
    def semantics_for_call(self,run,definition,grant):
        result=self.semantics(run,definition,grant);result['inputs']=copy.deepcopy(self.call_inputs);return result
    def outputs(self,message,plan,run,grant):
        self.guard();rows=self.index['outputs'].get(message['transition_ref'])
        need(rows is not None,'actual producer lacks this transition')
        records=[self._record(row) for row in rows]
        return {'artifacts':[r['artifact'] for r in records],'originals':{r['artifact']['version_ref']:r['original'] for r in records},
          'producer_receipt_bindings':copy.deepcopy(self.index['producer_receipt_bindings'])}
