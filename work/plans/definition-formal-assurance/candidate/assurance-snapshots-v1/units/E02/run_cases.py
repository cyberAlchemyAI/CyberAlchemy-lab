"""Retain actual controlled publications/attempts without installing fake sources."""
import copy
import json
import shutil
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[7]
IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1'
UNIT=Path(__file__).resolve().parent
sys.path[:0]=[str(IMPL),str(IMPL/'tests')]
import bundles as b
import test_E02 as controls


def main():
    control=controls.PublicationControls();control.setUp();control.parent=b.BASE+'/units/E02/controlled-publications';records=[]
    try:
        old_required=copy.deepcopy(control.required);first=control.publish();assert first['status']=='published-candidate'
        records.append({'case_id':'initial-v2','actual':first,'expected_required_set':old_required})
        collision=control.publish();assert collision['status']=='publication-collision';records.append({'case_id':'same-identity-collision','actual':collision})
        controls.advance_version(control);second=control.publish();assert second['status']=='published-candidate' and second['bundle_id']!=first['bundle_id']
        records.append({'case_id':'next-version-v3','actual':second,'expected_required_set':copy.deepcopy(control.required)})
        def interrupt(info):raise InterruptedError('Controlled interrupted publication')
        interrupted=control.publish(before_publish=interrupt);assert interrupted['status']=='publication-unresolved';records.append({'case_id':'interrupted-private-attempt','actual':interrupted})
        control.bundle['claim_ceiling']+=' Empty-directory collision control.';empty=[]
        def compete(info):
            path=control.root/info['output_parent']/info['target'];path.mkdir();empty.append(info['output_parent']+'/'+info['target'])
        raced=control.publish(before_publish=compete);assert raced['status']=='publication-collision';assert not list((control.root/empty[0]).iterdir());records.append({'case_id':'empty-directory-final-race','actual':raced,'preserved_empty_target_ref':empty[0]})
        source=control.root/control.parent;destination=ROOT/control.parent
        if destination.exists():raise FileExistsError(destination)
        shutil.copytree(source,destination)
        # Relocated packages contain synthetic source captures, never live Lab IDs.
        replays=[]
        for row in records:
            if row['actual']['status']=='published-candidate':
                report=b.inspect(ROOT,row['actual']['bundle_ref'],row['expected_required_set'],expected_contract=b.checked_contract());assert report['source_currentness']=='historical-capture-only';replays.append({'case_id':row['case_id'],'actual':report})
        packet={'schema_version':'definition-assurance-publication-controls/v1-candidate','authority_effect':'none','source_kind':'isolated-synthetic-source-captures','source_root_scope':'Publication currentness was checked in the temporary controlled source root; relocated packages are historical captures, not current Lab definition evidence.','records':records,'relocated_capture_replays':replays,'current_lab_whole_definition_proofs':0,'claim_ceiling':'Actual no-replace publication, version/identity and preservation controls. No Lab source translation, source-owner fidelity or readiness.'}
        with (UNIT/'worked-publications.json').open('x') as stream:json.dump(packet,stream,indent=2,sort_keys=True);stream.write('\n')
        print(json.dumps({'cases':len(records),'published_packages':len(replays),'preserved_attempts':sum(row['actual'].get('preserved_attempt_ref') is not None for row in records),'relocated_currentness':'historical-capture-only','whole_lab_definition_proofs':0},indent=2))
    finally:control.doCleanups()


if __name__=='__main__':main()
