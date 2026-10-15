"""Actual authenticated inspection/query calls and cold projection reconstruction."""
import base64
from exercise_stdio import child_case
from fixtures import *


def run(destination):
    destination=Path(destination).resolve()
    source.require(destination.is_relative_to(ROOT/'product/lab/release-candidates/v1/examples/operator-journeys/api')
        and not destination.exists(),'fresh exact reader example root required')
    destination.mkdir(parents=True);episodes=[];warm=None;warm_generation=None;foreign_cursor=None
    archive=source.parse(source.original(source.source_selection('engineering')['archive_binding']))
    baseline=source.parse(base64.b64decode(archive['files']['baseline.json']['base64_original_bytes'],validate=True))
    genesis=source.parse(base64.b64decode(archive['files']['transactions/0000000000.json']['base64_original_bytes'],validate=True))
    admission=source.parse(base64.b64decode(archive['files']['transactions/0000000001.json']['base64_original_bytes'],validate=True))
    work_versions={t['version_ref'] for t in admission['proposal']['targets'] if t['record'].get('kind')=='evidence-set'}
    carriers=sorted(baseline['contracts'])
    def started(client,key):
        challenge=client.receive();client.send(proof(key,challenge));context=client.receive()['context']
        status=client.invoke(call(context,'lab.status'));source.require(status['message']['supported_operations']==list(SUPPORTED),'actual successor status differs')
        return context,status['message']['source_cut']
    def result(client,message):
        reply=client.invoke(message);source.require(reply['kind']=='result','actual reader call failed');return reply['message']
    def record(name,code,checks):
        source.require(code==0,'reader child did not close cleanly')
        episodes.append({'name':name,'result':'PASS','terminal_exit_code':code,'checks':checks,
            'private_keys_exported':False,'owned_credentials_removed':True,'authority_effect':'none','canonical_effects':0})
        print(name,code,flush=True)
    with child_case(destination,'inspection-and-sql-query') as (client,key,policy,out):
        context,selected=started(client,key)
        canonical=result(client,call(context,'artifact.query',selected,carrier_refs=carriers,limit=1000))
        projected=result(client,call(context,'artifact.query',selected,carrier_refs=carriers,limit=1000,query_basis='projection'))
        source.require(canonical['results']==projected['results'] and len(projected['results'])==508
            and projected['query_basis']=='projection','actual canonical/SQL full inventory parity differs')
        warm=projected['results'];warm_generation=projected['projection_generation']
        definition=next(h for h in canonical['results'] if h['identity_ref']=='CAV2-D20')
        inspected=result(client,call(context,'artifact.inspect',selected,artifact=definition,
            include=['body','contract','authority','provenance','evidence','lifecycle','gaps']))
        source.require(inspected['envelope']['decoded_artifact']['body']['definition_id']=='CAV2-D20'
            and inspected['status_facets']['runtime_observation'] is None,'actual original Definition body/facets differ')
        minimal=result(client,call(context,'artifact.inspect',selected,artifact=definition,include=['lifecycle']))
        source.require(minimal['envelope'] is None and minimal['authority_bindings']==[] and minimal['provenance_bindings']==[],
            'excluded body/authority/provenance disclosed')
        work=next(h for h in canonical['results'] if h['version_ref'] in work_versions)
        embedded=result(client,call(context,'artifact.inspect',selected,artifact=work,include=['body','provenance','relations','gaps']))
        source.require('inherited-canonical-json' in embedded['envelope']['claim_ceiling'],'original selected signed body encoding not disclosed')
        traversal=result(client,call(context,'artifact.query',selected,carrier_refs=['cal.artifact-type.evidence-set/v1'],identity_refs=[work['version_ref']],
            relation_kind_refs=['relation.member-of'],max_depth=1,limit=1000,query_basis='projection'))
        source.require(any(c['target']['semantic_kind']=='project' for c in traversal['connections']), 'actual signed Project membership unavailable')
        first=result(client,call(context,'artifact.query',selected,limit=3,query_basis='projection'));foreign_cursor=first['next_page_cursor']
        second=result(client,call(context,'artifact.query',selected,limit=3,query_basis='projection',page_cursor=foreign_cursor))
        source.require(not ({h['version_ref'] for h in first['results']}&{h['version_ref'] for h in second['results']}),'actual SQL cursor repeats page')
        descriptor=next(h for h in canonical['results'] if h['version_ref']=='cal.artifact-type.work/v1')
        rejected=client.invoke(call(context,'artifact.inspect',selected,artifact=descriptor,include=['body']))
        source.require(rejected['kind']=='error' and rejected['message']['code']=='invalid-contract','descriptor body/root mismatch hidden')
        disclosed=result(client,call(context,'artifact.inspect',selected,artifact=descriptor,include=['contract','gaps']))
        source.require(disclosed['envelope'] is None and disclosed['gaps'],'descriptor gap metadata unavailable')
        code=client.finish()
    record('inspection-and-sql-query',code,['508 exact canonical/SQL references','original Definition body','excluded sections absent',
        'encoded selected signed Evidence Set body','raw Project membership traversal','generation-bound paging','descriptor/root mismatch disclosed'])
    with child_case(destination,'historical-query') as (client,key,policy,out):
        context,selected=started(client,key)
        historical={**selected,'commit_sequence':0,'commit_sha256':genesis['digest'],
            'streams':[{'stream_ref':name,'cursor':len(record['payload']['events']),'head_sha256':source.sha(compact(record))}
                for name,record in sorted(baseline['histories'].items())]}
        a=result(client,call(context,'artifact.query',historical,carrier_refs=carriers,limit=1000,freshness_requirement='exact-historical'))
        b=result(client,call(context,'artifact.query',historical,carrier_refs=carriers,limit=1000,freshness_requirement='exact-historical',query_basis='projection'))
        source.require(a['results']==b['results'] and len(b['results'])==485 and b['freshness']=='historical'
            and not work_versions&{h['version_ref'] for h in b['results']},'historical query includes later admitted targets or wrong cut')
        rejected=client.invoke(call(context,'artifact.query',historical))
        source.require(rejected['message']['code']=='stale-cut','current query accepted earlier prefix')
        code=client.finish()
    record('historical-query',code,['485 exact genesis references','historical canonical/SQL parity','later targets excluded','current requirement refuses historical prefix'])
    with child_case(destination,'cold-query-rebuild') as (client,key,policy,out):
        context,selected=started(client,key)
        cold=result(client,call(context,'artifact.query',selected,carrier_refs=carriers,limit=1000,query_basis='projection'))
        source.require(cold['results']==warm and cold['projection_generation']!=warm_generation,'cold reconstruction differs or prior generation reused')
        rejected=client.invoke(call(context,'artifact.query',selected,limit=3,query_basis='projection',page_cursor=foreign_cursor))
        source.require(rejected['message']['code']=='invalid-cursor','foreign connection/generation query cursor accepted')
        code=client.finish()
    record('cold-query-rebuild',code,['fresh original signature replay','new complete disposable generation','exact warm/cold references','foreign context/generation cursor refusal'])
    report={'result':'PASS','episodes':episodes,'child_processes':3,'eligible_current_cut_revisions':508,'historical_cut_revisions':485,
        'authority_effect':'none','actual_owner_outcome':None,'human_pilot':False,'private_keys_exported':False,
        'Session_memory_exported':False,'canonical_effects_applied':0,'local_authoring_transactions':0,
        'claim_ceiling':'Three real authenticated technical reader episodes only; no human pilot, owner response or full R03 completion.'}
    (destination/'result.json').write_bytes(source.encoded(report));return report


if __name__=='__main__':
    source.require(len(sys.argv)==2,'usage: exercise_readers.py fresh-selected-example-directory');run(sys.argv[1])
