"""One complete selected public occurrence projection through the reviewed reader.

No locator contained in an original table is followed. The owned role selection
is a metadata fixture, not an assertion of an actual branch/store source cut.
"""
import bootstrap
from bootstrap import R, S, E, checked
import argparse, json, os, tempfile, time
from pathlib import Path
from unittest.mock import patch
from lab_contracts.codec import canonical, sha, need
from lab_selectors.anchors import AnchoredReader, RootAnchor, identity, legacy_json
from lab_selectors.public_projection import build, policy_inputs, pointer, projection_digest
from dependency_graph.reader import RoleReader, ReaderSelection

POLICY = {'kind':'evidence','root_id':'repository',
    'relative_path':'implementation/lab-runtime/candidates/runtime-completion-0001/selectors/public-source-role-policy.json',
    'sha256':'35129f426ee6048e73366129ae4e9c0bf9ef5cb487717719337ad42dfbd410dc','size_bytes':16873}
PROJECTION_SHA = '6fa0cd021b6fc338ab62209dba88283b9ae1b8396fa429717ccb288494b4a25c'
CLASSIFICATIONS = {
    'historical-proof':'original-proof-metadata',
    'historical-host-declaration':'original-proof-metadata',
    'historical-public-payload':'public-payload-metadata',
    'historical-protected-metadata':'protected-dependency-metadata',
    'current-source-declaration':'current-execution-metadata',
    'current-profile-declaration':'current-execution-metadata',
    'current-external-host-declaration':'current-execution-metadata',
    'current-contribution-evidence':'original-proof-metadata',
    'current-schema-execution':'current-execution-metadata'}

def run(report):
    start=time.monotonic_ns();checks=0
    root=RootAnchor('repository',str(R),identity(os.stat(R)))
    policy=legacy_json(AnchoredReader([root],[POLICY]).read(POLICY))
    inputs=policy_inputs(policy); reads=[]; original_read=AnchoredReader.read
    def logged(reader,binding,*args,**kwargs):
        reads.append(binding.copy())
        return original_read(reader,binding,*args,**kwargs)
    with tempfile.TemporaryDirectory(prefix='owned-full-inventory-',dir=E) as directory:
        owned=Path(directory)
        with patch.object(AnchoredReader,'read',logged):
            reader=AnchoredReader([root],[POLICY,*inputs])
            projection=build(reader,POLICY)
            need(projection_digest(projection)==PROJECTION_SHA,'SELECTED_FULL_PROJECTION');checks+=1
            need(projection['counts']=={'historical_tables':17,'historical_occurrences':172533,
                'all_tables':22,'all_occurrences':241598},'COMPLETE_COUNTS');checks+=1
            documents={d['id']:d['binding'] for d in policy['documents']}
            descriptors=[{'document_binding':documents[t['document_id']], 'selector':t['selector'],
                'row_count':t['row_count'],'classification':CLASSIFICATIONS[t['role']]} for t in policy['tables']]
            source=documents['current-source'];profile=documents['current-profile']
            cut={'branch_ref':'owned-metadata-fixture','store_ref':'owned-metadata-fixture',
                'commit_sequence':0,'commit_sha256':'0'*64,'source_profile_sha256':profile['sha256'],'streams':[]}
            roles={'schema_version':'lab-original-role-selection/v1','source_binding':source,
                'profile_binding':profile,'source_cut':cut,'table_descriptors':descriptors,
                'authority_effect':'none','files':[]}
            raw=canonical(roles); (owned/'roles.json').write_bytes(raw)
            role_binding={'kind':'execution','root_id':'owned-fixture','relative_path':'roles.json',
                'sha256':sha(raw),'size_bytes':len(raw)}
            held=AnchoredReader([root,RootAnchor('owned-fixture',str(owned),identity(os.stat(owned)))],
                [POLICY,*inputs,role_binding])
            role=RoleReader(held,ReaderSelection(role_binding,source,profile,cut,descriptors))
            retained=role.inventory(descriptors)
            need(retained['occurrences']==241598 and retained['member_bodies_read']==0,'READER_FULL_ROWS');checks+=1
            offset=0
            for index,(selected,table) in enumerate(zip(projection['tables'],retained['tables'],strict=True)):
                need(table['rows']==selected['rows'] and table['document_binding']==documents[selected['document_id']]
                    and table['selector']==selected['selector'],'EXACT_ORDERED_TABLE')
                for row_index,row in enumerate(table['rows']):
                    node=projection['graph']['occurrence_nodes'][offset]
                    edge=projection['graph']['occurrence_edges'][offset]
                    selector=selected['selector'] if selected['selector']=='/host_native_binding' else selected['selector']+'/'+str(row_index)
                    need((node['table_id'],node['row_index'],node['original_selector'])==(selected['id'],row_index,selector),
                        'EXACT_OCCURRENCE_IDENTITY')
                    need((edge['from'],edge['to'],edge['kind'])==(selected['document_id'],node['id'],selected['kind']),
                        'EXACT_ORIGINAL_EDGE_ROLE')
                    offset+=1
            need(offset==241598,'ALL_OCCURRENCES_VISITED');checks+=1
            need(projection['occurrence_kind_counts']=={'semantic':0,'execution':69064,'evidence':149022,
                'host-custody':23512},'ORIGINAL_ROLE_COUNTS');checks+=1
            need(not projection['graph']['semantic_artifact_edges'] and
                projection['member_byte_resolution']['members_read']==0,'NO_MEMBER_PROMOTION');checks+=1
            protected=next(t for t in retained['tables'] if t['classification']=='protected-dependency-metadata')
            need(len(protected['rows'])==23486 and all(r['public_body_export_allowed'] is False for r in protected['rows']),
                'PROTECTED_METADATA_CEILING');checks+=1
            allowed={canonical(b) for b in [POLICY,*inputs,role_binding]}
            need({canonical(b) for b in reads}==allowed,'EXACT_SELECTED_READ_SET');checks+=1
            # Re-read every selected original after the complete comparison.
            for binding in [POLICY,*inputs]:reader.read(binding)
            summary={'schema_version':'lab-u0501-full-public-inventory-observation/v1',
                'policy_binding':POLICY,'input_bindings':inputs,'projection_sha256':PROJECTION_SHA,
                'counts':projection['counts'],'occurrence_kind_counts':projection['occurrence_kind_counts'],
                'table_observations':[{'document_binding':t['document_binding'],'selector':t['selector'],
                    'classification':t['classification'],'occurrences':len(t['rows']),
                    'ordered_rows_sha256':projection_digest(t['rows'])} for t in retained['tables']],
                'checks':checks,'member_bodies_read':0,'original_task_acceptance_changed':False,
                'source_cut_posture':'owned metadata fixture; no actual cut asserted',
                'semantic_body_closure':'unselected-gated','authority_effect':'none',
                'elapsed_ns':time.monotonic_ns()-start}
    need(not owned.exists(),'OWNED_CLEANUP')
    if report:
        need(report.parent==E and report.name.startswith('full-inventory-observation-'),'OWNED_REPORT_PATH')
        with report.open('xb') as stream:
            stream.write((json.dumps(summary,sort_keys=True,indent=2)+'\n').encode());stream.flush();os.fsync(stream.fileno())
    return checks

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--temp-root',type=Path,required=True);p.add_argument('--report',type=Path)
    a=p.parse_args();need(a.temp_root==E and E.is_dir(),'OWNED_ROOT')
    count=run(a.report)
    print(json.dumps({'schema_version':'lab-case-command-result/v1','result':'PASS','checks':count,
        'effect_state':'owned-inert','cleanup':'clean'}))
