"""Resolve actual original result members without guessed revisions or digests.

Supported original materializer maps supply their own identity/version/digest
triples. API routes must actually return typed headers. Missing original typed
contracts refuse; their full workflow obligations remain in the registry.
"""
import copy
from pathlib import Path
from .protocol import compact
from .workflow_output_contracts import need,sha,pointer
from .workflow_output_registry import selected_transition

class OriginalFileResolver:
    def __init__(self,producer,route_rows,carriers):
        self.producer=producer;self.routes=copy.deepcopy(route_rows);self.carriers=carriers
    def relative(self,path):
        roots={row['output_custody']['root'] for row in self.routes.values()};need(len(roots)==1,'one invocation uses one selected output custody')
        root=Path(next(iter(roots)));path=Path(path)
        need(path.is_absolute() and path.is_relative_to(root),'actual produced path outside independently selected custody')
        return path.relative_to(root).as_posix()
    def carrier(self,body,required):
        rows=[]
        for ref in required:
            row=self.carriers.rows[ref]
            try:value=pointer(body,row['instance_discriminator']['path'])
            except (KeyError,TypeError,IndexError):continue
            if value==row['instance_discriminator']['value']:rows.append(ref)
        need(len(rows)<=1,'ambiguous original body carrier/version')
        return None if not rows else rows[0]
    def resolve(self,view):
        need(set(view['transition_refs'])==set(self.routes),'resolver selects another original invocation group')
        families={selected_transition(ref)['family'] for ref in self.routes};need(len(families)==1,'one resolver keeps one original producer family')
        family=next(iter(families));value=view['original_result']
        if type(value)is dict and 'original_output_material' in value:
            need(set(value['original_output_material']['slots'])=={r['output_slot_ref'] for r in self.routes.values()},'actual successor selects another original slot closure')
            material=copy.deepcopy(value['original_output_material'])
            for members in material['slots'].values():
                for member in members:member.setdefault('scope_proof',None)
            return material
        required={c for ref in self.routes for c in selected_transition(ref)['output_carriers']};outputs=[];receipts=[]
        if family in ('engineering','research'):
            review=value['review'];members=review['member_records'] if family=='engineering' else review['selected_candidate_members']
            if family=='engineering':need(review['work_effect']['from_version_ref']==view['work_ref'] and review['work_effect']['applied'] is False,'actual original engineering Work lineage differs')
            else:need(review['process_completed'] is True and any(v['version_ref']==view['work_ref'] for v in review['input_dependencies']),'actual original research Work/completion differs')
            directory=self.producer.output_root if family=='engineering' else self.producer.output
            candidates=value['candidates']
            for name,body in candidates.items():
                carrier=self.carrier(body,required)
                if carrier is None:continue
                matches=[m for m in members if m['identity_ref']==body['node_id'] and m['kind']==body['kind']]
                need(len(matches)==1,'actual original materialization tuple missing/ambiguous');m=matches[0];pin=m['record_sha256'] if family=='engineering' else m['sha256']
                h={'scope_ref':body['scope_ref'],'identity_ref':m['identity_ref'],'version_ref':m['version_ref'],'carrier_ref':carrier,'byte_sha256':pin}
                outputs.append({'artifact':h,'path':self.relative(directory/(name+'.json')),'original_binding':{'ref':m['version_ref'],'sha256':pin}})
            # The actual original materializer writes exactly this review object.
            # Its original serializer supplies the expected byte digest.
            import sys
            module=sys.modules[type(self.producer).__module__];raw=module.encoded(review)
            receipts.append({'path':self.relative(directory/'review-effects.json'),'original_binding':{'ref':'original-producer-review:'+sha(raw),'sha256':sha(raw)}})
        elif family=='operational-learning':
            sources=self.producer.e
            for row in value['original_learning_outputs']:
                file,pin=sources.records[row['version_ref']];body=sources.get(row['version_ref']);carrier=self.carrier(body,required)
                if carrier is None:continue
                need(pin==row['sha256'] and body['node_id']==row['identity_ref'],'actual original CandidateSources result changed')
                h={'scope_ref':body['scope_ref'],'identity_ref':row['identity_ref'],'version_ref':row['version_ref'],'carrier_ref':carrier,'byte_sha256':pin}
                material={'path':self.relative(file),'original_binding':{'ref':row['version_ref'],'sha256':pin}}
                outputs.append({'artifact':h,**material});receipts.append(material)
        else:
            host=self.producer if hasattr(self.producer,'vault') else getattr(self.producer,'host',getattr(self.producer,'service',None))
            need(host is not None and hasattr(host,'vault'),'actual original API producer vault unavailable')
            vault=host.vault
            def walk(node):
                if type(node)is dict:
                    if set(node) in ({'scope_ref','identity_ref','version_ref','carrier_ref','byte_sha256'},{'scope_ref','identity_ref','version_ref','carrier_ref','byte_sha256','candidate_contract_binding'}) and node['carrier_ref'] in required:
                        node={k:node[k] for k in ('scope_ref','identity_ref','version_ref','carrier_ref','byte_sha256')}
                        b={'ref':'workspace-object:'+vault.manifest['workspace_ref']+':'+node['byte_sha256'],'sha256':node['byte_sha256']}
                        outputs.append({'artifact':copy.deepcopy(node),'path':self.relative(vault.root/'objects'/(b['sha256']+'.json')),'original_binding':b})
                    if set(node)=={'ref','sha256'} and node['ref']=='workspace-object:'+vault.manifest['workspace_ref']+':'+node['sha256']:
                        receipts.append({'path':self.relative(vault.root/'objects'/(node['sha256']+'.json')),'original_binding':copy.deepcopy(node)})
                    for child in node.values():walk(child)
                elif type(node)in (tuple,list):
                    for child in node:walk(child)
            walk(value)
            # Context/other original handlers return their actual domain object
            # and store its canonical bytes in this same actual selected vault.
            domain=value[0] if type(value)in (tuple,list) and value and type(value[0])is dict else value
            if not receipts and type(domain)is dict:
                raw=compact(domain);b={'ref':'workspace-object:'+vault.manifest['workspace_ref']+':'+sha(raw),'sha256':sha(raw)}
                receipts.append({'path':self.relative(vault.root/'objects'/(b['sha256']+'.json')),'original_binding':b})
        unique={}
        for row in outputs:
            key=row['artifact']['version_ref'];need(key not in unique or unique[key]==row,'conflicting actual original headers');unique[key]=row
        outputs=list(unique.values())
        for member in outputs:member['scope_proof']=None
        slots={}
        for ref,row in self.routes.items():
            categories=set(selected_transition(ref)['output_carriers']);selected=[copy.deepcopy(v) for v in outputs if v['artifact']['carrier_ref'] in categories]
            need({v['artifact']['carrier_ref'] for v in selected}==categories,'actual producer lacks original typed output contract; obligation retained')
            slots[row['output_slot_ref']]=selected
        deduplicated={}
        for row in receipts:
            key=(row['original_binding']['ref'],row['original_binding']['sha256']);need(key not in deduplicated or deduplicated[key]==row,'conflicting actual receipt origins');deduplicated[key]=row
        return {'schema_version':'lab-private-produced-workflow-material/v2-candidate','slots':slots,'action_receipts':list(deduplicated.values()),'authority_effect':'none'}
