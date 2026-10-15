"""Join independently verified candidate components without merging their authority."""
from __future__ import annotations
import copy
from dataclasses import dataclass
from pathlib import Path
import sys

PACKAGE=Path(__file__).resolve().parent;ROOT=PACKAGE.parents[3]
RUNTIME=ROOT/'implementation/lab-runtime/candidates/repeatable-operation'
BOOTSTRAP=ROOT/'implementation/lab-bootstrap/candidates/v1'
CONTEXT=ROOT/'implementation/lab-context/candidates/v1'
for path in [RUNTIME,BOOTSTRAP,CONTEXT]:
    if str(path) not in sys.path:sys.path.insert(0,str(path))
from lab_runtime.common import byte_digest,digest,load,require
from lab_runtime.store import VerifiedLegacyReadStore
from lab_runtime.transition import BranchPins,LocalPolicy,replay_successor
import bootstrap
from context import ContextSession


@dataclass(frozen=True)
class JoinPins:
    source_profile_sha256: str
    source_snapshot_digest: str
    project_head: str
    catalog_digest: str
    transition_head_digest: str


def inspect_successor(project_store, source_snapshot, catalog_path, catalog_pins, catalog_policy,
                      transition_path, transition_pins, transition_policy, native_store,
                      join_pins, *, context_options):
    """Read-only verification surface, not a public API permission adapter."""
    require(isinstance(project_store,VerifiedLegacyReadStore),'pinned Project read adapter required')
    require(isinstance(join_pins,JoinPins),'independent joined inspection pins required')
    require(isinstance(catalog_pins,bootstrap.CatalogPins) and isinstance(catalog_policy,bootstrap.RehearsalPolicy),'independent catalog read controls required')
    require(isinstance(transition_pins,BranchPins) and isinstance(transition_policy,LocalPolicy),'independent reconstructed-branch controls required')
    catalog=bootstrap.replay(catalog_path,catalog_pins,catalog_policy)
    branch=replay_successor(transition_path,transition_pins,transition_policy)
    project=project_store.verify_full(require_current=True)
    c=catalog['catalog'];source=c['source']
    require(source['profile_sha256']==source_snapshot['source_profile_sha256']==join_pins.source_profile_sha256,'joined source profile mismatch')
    require(source['snapshot_digest']==source_snapshot['snapshot_digest']==join_pins.source_snapshot_digest,'joined source snapshot mismatch')
    require(c['digest']==join_pins.catalog_digest,'joined catalog digest mismatch')
    require(digest(branch['head'])==join_pins.transition_head_digest,'joined transition head mismatch')
    require(branch['baseline']['source_profile_sha256']==join_pins.source_profile_sha256 and branch['baseline']['snapshot_digest']==join_pins.source_snapshot_digest,'reconstructed branch selected a different baseline')
    require(project['baseline']['materials']==source_snapshot['materials'] and project['head']['transaction_digest']==join_pins.project_head,'joined Project state source/head mismatch')
    # Existing source contract semantics and candidate additions stay separate.
    require(c['source_subjects']==source_snapshot['subjects'],'catalog inherited subjects differ from verified source')
    for ref,contract in source_snapshot['contracts'].items():
        selected=c['contracts'][ref]
        require(selected['schema_sha256']==contract['schema_sha256'] and selected['artifact_sha256']==contract['artifact_sha256'],'catalog inherited carrier bytes changed')
    candidates=copy.deepcopy(c['candidate_subjects'])
    for version,row in candidates.items():
        require(row['effective_state']=='candidate-unadmitted' and version not in project['projection']['subjects'],'candidate catalog member cannot shadow a Project subject')
    reconstructed={}
    for version,record in branch['records'].items():
        row=branch['subjects'][version]
        require(row['effective_state']=='candidate-reconstructed' and row['decision_ref'] is None,'reconstructed result cannot claim admitted authority')
        require(version not in project['projection']['subjects'] and version not in candidates,'reconstructed subject collides with another joined source')
        require(not row['provenance']['signatures_copied'],'historical signature cannot become successor authority')
        reconstructed[version]=copy.deepcopy(row)
    options=copy.deepcopy(context_options)
    require(options['expected_profile_sha256']==join_pins.source_profile_sha256 and options['expected_snapshot_digest']==join_pins.source_snapshot_digest,'context selected a different joined source')
    session=None
    try:
        session=ContextSession(project_store,source_snapshot,native_store,**options)
        pack=session.context()
        require(pack['head']==join_pins.project_head,'context selected a different Project head')
        require(digest(pack['project_state'])==digest(project['projection']['state']),'context Project State differs from full verifier')
        result={'schema_version':'lab-joined-successor-inspection/v1-candidate','authority_effect':'none',
                'source_cut':source_snapshot['expected_cut'],'join_pins':dict(vars(join_pins)),
                'project_state':copy.deepcopy(project['projection']['state']),
                'catalog_summary':{'contract_versions':len(c['contracts']),'source_subjects':len(c['source_subjects']),'candidate_subjects':len(candidates),'relation_kinds':len(c['relation_contracts'])},
                'candidate_catalog':candidates,'reconstructed_candidates':reconstructed,
                'context':pack,'session_closure':None,'actual_owner_outcome':None,
                'real_work_satisfaction_claimed':False,'action_permission':'none',
                'limitations':['Read-only integration over separately headed stores; no cross-store atomic commit.','Catalog/reconstructed candidates remain separate from governed Project State.','Native ontology retains its supported empty-property profile; domain Artifact mappings remain O02.','This interface is a verification surface; no trusted public API authority adapter is claimed.'],
                'claim_ceiling':'Observed isolated candidate integration only; no canonical admission, human pilot, completed real Work or power-loss durability.'}
        result['session_closure']=session.close()
        # After reconstruction, verify each primary input again. Close erased memory.
        require(bootstrap.replay(catalog_path,catalog_pins,catalog_policy)==catalog,'catalog changed during joined inspection')
        require(replay_successor(transition_path,transition_pins,transition_policy)==branch,'reconstructed branch changed during joined inspection')
        require(project_store.verify_full(require_current=True)==project,'Project store changed during joined inspection')
        result['inspection_digest']=digest(result)
        return result
    finally:
        if session is not None:session.close()
