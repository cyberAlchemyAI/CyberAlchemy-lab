from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent;Q=P/"workspace-records"
sys.path.insert(0,str(R/"implementation/lab-runtime/v2"));sys.path.insert(0,str(R/"implementation/lab-runtime/alchlang/ports"));sys.path.insert(0,str(R/"implementation/lab-runtime/alchlang/shared-records"))
from schema_metadata_cache import install
from jsonschema import Draft202012Validator
install(Draft202012Validator)
from lab_runtime.store import Store
from lab_runtime.common import encoded,load
from creation import draft_from_file,compiled_creation_check,prepare_bundle
active=load(R/"implementation/lab-runtime/shared-workflow.json");store=Store(R/active["native_store"],R);data=store.replay(require_current=True)
if not (Q/"proposal.json").exists():
 drafts=[]
 for row in load(Q/"TARGETS.json")["records"]:
  draft=draft_from_file(data,R/row["file"],kind="record",project=data["projection"]["state"]["payload"]["project_ref"],scope="project",work=None,carrier=row["carrier"],version=row["version"],decision="decision:workspace-records:"+row["version"],owner_field=row["owner_field"])
  compiled_creation_check(data,draft);drafts.append(draft)
 proposal=prepare_bundle(data,drafts,"workspace-operating-records-nine-findings")
 (Q/"proposal.json").write_bytes(encoded(proposal))
 (Q/"context.json").write_bytes(encoded({"head":data["head"],"source_cut":data["baseline"]["snapshot_digest"],"project":data["projection"]["state"]["payload"]["project_ref"],"compiled_creation_checks":len(drafts)}))
proposal=load(Q/"proposal.json")
if not (Q/"review.json").exists():(Q/"review.json").write_bytes(encoded(store.review(proposal)))
if not (Q/"approval.json").exists():(Q/"approval.json").write_bytes(encoded(store.authorize(proposal,Path.home()/".config/cyberalchemy-lab/shared-records/operator.pem")))
print(json.dumps({"status":"prepared","targets":len(proposal["targets"]),"authority_effect":"none"}))
