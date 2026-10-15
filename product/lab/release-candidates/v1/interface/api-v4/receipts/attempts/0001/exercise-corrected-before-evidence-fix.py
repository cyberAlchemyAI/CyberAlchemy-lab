"""Real authenticated corrected-history reads, historical residue and cold parity."""
from exercise_stdio import child_case
from fixtures import *


def run(destination):
    destination=Path(destination).resolve()
    source.require(destination.is_relative_to(ROOT/'product/lab/release-candidates/v1/examples/operator-journeys/api')
        and not destination.exists(),'fresh selected corrected reader episode required')
    destination.mkdir(parents=True);episodes=[];warm=None;generation=None;cursor=None
    with source.replay_source('reference-corrected') as view:
        carriers=sorted(view.data['projection']['contracts']);members=[source.parse(source.original(b)) for b in
            source.parse(source.original(view.handle.manifest['correction_profile_binding']))['member_bindings']]
        new_versions={m['version_ref'] for m in members};old_versions={m['predecessor_version_ref'] for m in members}
        original_streams=view.data['baseline']['histories'];genesis=view.data['transactions'][0]
    def configure(value):value['source_name']='reference-corrected'
    def start(client,key):
        challenge=client.receive();client.send(proof(key,challenge));context=client.receive()['context']
        status=client.invoke(call(context,'lab.status'));source.require(status['kind']=='result','corrected source did not authenticate/open')
        reasons=' '.join(g['reason'] for g in status['message']['gaps'])
        source.require('60 current closed, 0 current unclosed' in reasons and '10 historical unresolved' in reasons,'current/historical closure collapsed')
        return context,status['message']['source_cut']
    def result(client,message):
        response=client.invoke(message);source.require(response['kind']=='result','real corrected reader request failed');return response['message']
    def record(name,exit_code,checks):
        source.require(exit_code==0,'corrected reader child failed to close')
        episodes.append({'name':name,'result':'PASS','terminal_exit_code':exit_code,'checks':checks,'owned_credentials_removed':True,
            'authority_effect':'none','canonical_effects':0,'local_authoring_effects':0,'private_keys_exported':False})
    with child_case(destination,'corrected-head',configure) as (client,key,policy,out):
        context,selected=start(client,key)
        canonical=result(client,call(context,'artifact.query',selected,carrier_refs=carriers,limit=1000))
        projected=result(client,call(context,'artifact.query',selected,carrier_refs=carriers,limit=1000,query_basis='projection'))
        source.require(canonical['results']==projected['results'] and len(canonical['results'])==546,'corrected canonical/SQL inventory differs')
        source.require(canonical['gaps']==projected['gaps'],'canonical/SQL history residue differs')
        gaps=[g for g in canonical['gaps'] if 'Historical relation remains unresolved' in g['reason']]
        source.require({g['subject_ref'] for g in gaps}==old_versions,'exact ten historical predecessor gaps missing')
        by_version={h['version_ref']:h for h in canonical['results']};source.require(new_versions|old_versions<=by_version.keys(),'current or historical revision omitted')
        warm=canonical['results'];generation=projected['projection_generation']
        current=result(client,call(context,'artifact.inspect',selected,artifact=by_version[members[0]['version_ref']],
            include=['body','contract','authority','provenance','evidence','lifecycle','gaps']))
        original=result(client,call(context,'artifact.inspect',selected,artifact=by_version[members[0]['predecessor_version_ref']],
            include=['body','contract','authority','provenance','evidence','lifecycle','gaps']))
        source.require(current['status_facets']['admission']=='local-admitted-current' and original['status_facets']['admission']=='local-admitted-historical','independent lifecycle facets missing')
        source.require(current['envelope']['decoded_artifact']['body']==source.parse(source.original(members[0]['record_binding']))
            and original['envelope']['decoded_artifact']['body']==source.parse(source.original(members[0]['original_source_binding'])),'exact current/original bodies changed')
        source.require(len(current['evidence_bindings'])==4 and any('Historical exact relation' in g['reason'] for g in original['gaps']), 'correction evidence/historical closure gap missing')
        project=by_version['project:cyberalchemy-v2-to-lab-migration@foundation.1']
        traversal=result(client,call(context,'artifact.query',selected,carrier_refs=[project['carrier_ref']],identity_refs=[project['version_ref']],
            relation_kind_refs=['relation.member-of'],max_depth=1,limit=1000,query_basis='projection'))
        source.require(any(c['target']['semantic_kind']=='project' and c['target']['artifact']==project for c in traversal['connections']),
            'exact historical Project endpoint unavailable through corrected closed connection')
        first=result(client,call(context,'artifact.query',selected,limit=3,query_basis='projection'));cursor=first['next_page_cursor']
        source.require(cursor is not None,'corrected generation cursor missing')
        code=client.finish()
    record('corrected-head',code,['546 canonical/SQLite revisions','ten exact current and unchanged historical bodies','ten historical gaps; zero current gaps',
        'four correction evidence witnesses','exact historical Project membership tuple','separate admission facets and current carrier posture'])
    with child_case(destination,'corrected-genesis',configure) as (client,key,policy,out):
        context,selected=start(client,key);historical={**selected,'commit_sequence':0,'commit_sha256':genesis['digest'],
            'streams':[{'stream_ref':name,'cursor':len(record['payload']['events']),'head_sha256':source.sha(compact(record))}
                for name,record in sorted(original_streams.items())]}
        a=result(client,call(context,'artifact.query',historical,carrier_refs=carriers,limit=1000,freshness_requirement='exact-historical'))
        b=result(client,call(context,'artifact.query',historical,carrier_refs=carriers,limit=1000,freshness_requirement='exact-historical',query_basis='projection'))
        versions={h['version_ref'] for h in a['results']}
        source.require(a['results']==b['results'] and len(versions)==485 and old_versions<=versions and not new_versions&versions,'genesis reconstruction aliases later corrections')
        rejected=client.invoke(call(context,'artifact.query',historical));source.require(rejected['message']['code']=='stale-cut','current read accepted historical genesis')
        code=client.finish()
    record('corrected-genesis',code,['485 exact genesis revisions','no later correction/project setup aliases','historical canonical/SQLite parity','current requirement refuses historical cut'])
    with child_case(destination,'corrected-cold-rebuild',configure) as (client,key,policy,out):
        context,selected=start(client,key)
        cold=result(client,call(context,'artifact.query',selected,carrier_refs=carriers,limit=1000,query_basis='projection'))
        source.require(cold['results']==warm and cold['projection_generation']!=generation,'cold corrected projection differs or restored old generation')
        rejected=client.invoke(call(context,'artifact.query',selected,limit=3,query_basis='projection',page_cursor=cursor))
        source.require(rejected['message']['code']=='invalid-cursor','foreign corrected generation cursor accepted')
        code=client.finish()
    record('corrected-cold-rebuild',code,['fresh independent source signature replay','546 exact warm/cold references','new disposable generation','foreign cursor rejected'])
    report={'result':'PASS','episodes':episodes,'child_processes':3,'current_cut_revisions':546,'historical_cut_revisions':485,
        'current_closed_relations':60,'current_unclosed_relations':0,'historical_unclosed_relations':10,'authority_effect':'none','actual_owner_outcome':None,
        'private_keys_exported':False,'Session_memory_exported':False,'canonical_effects_applied':0,'local_authoring_transactions':0,'human_pilot':False}
    (destination/'result.json').write_bytes(source.encoded(report));print(json.dumps(report,sort_keys=True));return report


if __name__=='__main__':
    source.require(len(sys.argv)==2,'usage: exercise_corrected.py fresh-selected-example-root');run(sys.argv[1])
