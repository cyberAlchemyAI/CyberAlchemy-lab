"""Versioned workspace scopes and dispatch onto one existing Lab runtime.

Workspace configuration is not a native permission or an identity admission.
"""
from __future__ import annotations
import argparse, copy, json, subprocess, sys, tempfile, hashlib, shutil
from pathlib import Path
import jsonschema

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[2]
MODEL = "lab-workspace-model/v2"
AREAS = ("product", "project", "work", "authority", "ontology", "architecture", "implementation", "docs")
READ_OPERATIONS = {"status", "verify", "inspect", "catalog", "query"}
PROJECT_OPERATIONS = {"review", "authorize", "apply", "example", "recover", "session"}
class Refusal(ValueError): pass
def need(value, code):
    if not value: raise Refusal(code)
def load(path): return json.loads(Path(path).read_text())
def validate(profile):
    try: jsonschema.Draft202012Validator(load(PACKAGE/"workspace.schema.json")).validate(profile)
    except jsonschema.ValidationError as exc: raise Refusal("workspace-schema:"+exc.json_path) from exc
    need(profile["model_version"] == MODEL, "workspace-model-incompatible")
    subject = profile["primary_subject"]
    need(subject["kind"] == profile["kind"], "workspace-subject-kind")
    if profile["kind"] == "project":
        need(bool(subject["ref"]), "primary-project-required")
        need(not profile["linked_project_refs"], "project-workspace-cannot-own-other-projects")
    need(len(profile["linked_project_refs"]) == len(set(profile["linked_project_refs"])), "duplicate-project")
    for goal in profile["goals"]:
        projects = project_refs(profile)
        need(goal["project_ref"] in projects, "goal-project-outside-workspace")
    return profile
def project_refs(profile):
    return ([profile["primary_subject"]["ref"]] if profile["kind"] == "project" else profile["linked_project_refs"])
def migrate_v1(old, *, home):
    """Explicit conversion; leaves old bytes and Goal membership untouched."""
    need(old.get("schema_version") == "lab-workspace-profile/v1-candidate", "legacy-version-unsupported")
    need(bool(old.get("project_ref")), "legacy-primary-project-required")
    result = {
        "schema_version":"lab-workspace/v2", "model_version":MODEL,
        "workspace_ref":old["workspace_ref"], "revision":old["revision"]+"+workspace-v2",
        "kind":"project", "primary_subject":{"kind":"project","key":old["project_ref"],"ref":old["project_ref"]},
        "linked_project_refs":[], "related_product_refs":[old["product_ref"]] if old.get("product_ref") else [],
        "purpose":old["purpose"], "scope_ref":old["scope_ref"],
        "home":{"mode":"hosted","path":home}, "areas":list(AREAS),
        "goals":[dict(g, project_ref=old["project_ref"]) for g in old.get("goals",[])],
        "runtime_selection":{"placement":"shared","runtime_ref":"lab:shared-runtime","behavior":"inherited","specialization_ref":None},
        "authority_effect":"none","model_binding_ref":old.get("model_binding_ref","legacy:explicit-conversion")}
    return validate(result)
def context(profile, *, project_ref=None, goal_ref=None, work=None, expected_revision=None):
    validate(profile)
    need(expected_revision is None or expected_revision == profile["revision"], "workspace-revision-mismatch")
    projects=project_refs(profile)
    if profile["kind"]=="project":
        need(project_ref in (None,profile["primary_subject"]["ref"]), "foreign-project")
        project_ref=profile["primary_subject"]["ref"]
    elif project_ref is not None:
        need(project_ref in projects, "foreign-project")
    if goal_ref is not None:
        need(project_ref is not None, "project-required-for-goal")
        goal=next((g for g in profile["goals"] if g["goal_ref"]==goal_ref),None)
        need(goal is not None and goal["project_ref"]==project_ref, "goal-project-mismatch")
    if work is not None:
        need(project_ref is not None, "project-required-for-work")
        need(work.get("payload",{}).get("project_ref")==project_ref, "work-project-mismatch")
    return {"model_version":MODEL,"workspace_ref":profile["workspace_ref"],"workspace_revision":profile["revision"],
            "workspace_kind":profile["kind"],"primary_subject":copy.deepcopy(profile["primary_subject"]),
            "project_ref":project_ref,"scope_ref":profile["scope_ref"],"goal_ref":goal_ref,
            "state_namespace_ref":profile["workspace_ref"],"authority_effect":"none"}
def resolve(profile, catalog, **kwargs):
    ctx=context(profile,**kwargs)
    choice=profile["runtime_selection"]
    runtime=catalog.get("runtimes",{}).get(choice["runtime_ref"])
    need(runtime is not None,"runtime-unavailable")
    need(runtime["placement"]==choice["placement"],"runtime-placement-mismatch")
    need(MODEL in runtime["supported_model_versions"],"runtime-model-incompatible")
    need(profile["workspace_ref"] in runtime["workspace_refs"],"runtime-workspace-unsupported")
    if choice["placement"]=="dedicated":
        need(runtime.get("bound_workspace_ref")==profile["workspace_ref"],"dedicated-workspace-mismatch")
    overrides={}
    if choice["behavior"]=="specialized":
        specialization=catalog.get("specializations",{}).get(choice["specialization_ref"])
        need(specialization is not None,"specialization-unavailable")
        need(specialization["workspace_ref"]==profile["workspace_ref"] and specialization["model_version"]==MODEL,"specialization-scope-mismatch")
        overrides=specialization["configuration_overrides"]
        need(set(overrides)<= {"context_budget_tokens","operator_note"},"specialization-outside-configuration")
        if "context_budget_tokens" in overrides: need(type(overrides["context_budget_tokens"]) is int and 0<overrides["context_budget_tokens"]<=32768,"specialization-budget")
        if "operator_note" in overrides: need(isinstance(overrides["operator_note"],str) and len(overrides["operator_note"])<=160,"specialization-note")
    else: need(choice["specialization_ref"] is None,"unexpected-specialization")
    return {**ctx,"runtime_ref":choice["runtime_ref"],"placement":choice["placement"],"behavior":choice["behavior"],
            "entrypoint":runtime["entrypoint"],"configuration_overrides":copy.deepcopy(overrides),
            "runtime_created":False,"runtime_code_copied":False,"operational_authorization":"native-host-required"}
def profiles(root=ROOT):
    current=load(root/"implementation/lab-workspaces/CURRENT.json")
    digest=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
    need(current["model_version"]==MODEL,"current-model-incompatible")
    need(digest(root/current["operating_model"])==current["operating_model_sha256"],"operating-model-drift")
    need(digest(root/"implementation/lab-workspaces/v2/workspace.schema.json")==current["profile_schema_sha256"],"profile-schema-drift")
    need(digest(root/"ontology/lab-workspace/v2/definition.json")==current["definition_sha256"],"workspace-definition-drift")
    catalog=load(root/"implementation/lab-workspaces/v2/catalog.json")
    selected={key:validate(load(root/rel)) for key,rel in catalog["profiles"].items()}
    workspace_refs=[p["workspace_ref"] for p in selected.values()]
    need(len(workspace_refs)==len(set(workspace_refs)),"duplicate-workspace-identity")
    subjects=[(p["kind"],p["primary_subject"]["ref"] or p["primary_subject"]["key"]) for p in selected.values()]
    need(len(subjects)==len(set(subjects)),"duplicate-primary-subject")
    for key,profile in selected.items():
        path=Path(profile["model_binding_ref"])
        need(not path.is_absolute() and ".." not in path.parts,"unsafe-model-binding")
        need((root/path).resolve().is_relative_to(root.resolve()),"model-binding-escape")
        binding=load(root/path)
        need(binding["profile_sha256"]==digest(root/catalog["profiles"][key]),"model-binding-profile-drift")
        need(binding["operating_model_sha256"]==current["operating_model_sha256"],"model-binding-parent-drift")
        need(binding["workspace_ref"]==profile["workspace_ref"] and binding["profile_revision"]==profile["revision"],"model-binding-workspace-mismatch")
        need(binding["model_version"]==MODEL and binding["primary_subject"]==profile["primary_subject"],"model-binding-subject-mismatch")
        need(binding["authority_grants"]==[] and binding["authority_effect"]=="none","model-binding-grants-authority")
        need(binding["format"]=="lab-workspace-model-binding/v2" and binding["inherited_areas"]==list(AREAS),"model-binding-contract-mismatch")
    return catalog,selected
def verify_layout(root=ROOT):
    catalog,selected=profiles(root)
    homes={}
    workspace_refs=[p["workspace_ref"] for p in selected.values()]
    need(len(workspace_refs)==len(set(workspace_refs)),"duplicate-workspace-identity")
    subjects=[(p["kind"],p["primary_subject"]["ref"] or p["primary_subject"]["key"]) for p in selected.values()]
    need(len(subjects)==len(set(subjects)),"duplicate-primary-subject")
    for key,profile in selected.items():
        home=profile["home"]
        if home["mode"]=="external":
            need(Path(home["path"]).is_absolute(),"external-home-must-be-absolute")
            continue
        path=Path(home["path"])
        need(not path.is_absolute() and ".." not in path.parts,"unsafe-workspace-home")
        physical=root/path
        need(physical.resolve().is_relative_to(root.resolve()),"workspace-home-escape")
        need(physical.is_dir() and not physical.is_symlink(),"workspace-home-not-canonical")
        need(all((physical/a).is_dir() for a in AREAS),"missing-workspace-area")
        need(str(physical.resolve()) not in homes,"duplicate-workspace-home")
        homes[str(physical.resolve())]=key
        if home["mode"]=="repository-root": need(path==Path("."),"root-registration-home")
        elif profile["kind"]=="product": need(path.parent==Path("workspaces/products"),"product-home-namespace")
        else: need(path.parent==Path("workspaces/projects"),"project-home-namespace")
        resolve(profile,catalog)
    return {"status":"pass","model_version":MODEL,"workspace_profiles":len(selected),"physical_homes":len(homes),
            "shared_runtime_targets":len({p["runtime_selection"]["runtime_ref"] for p in selected.values()}),
            "runtime_copies":0,"authority_effect":"none"}
def dispatch(profile,catalog,operation,arguments=(),*,project_ref=None,goal_ref=None,store=None,root=ROOT):
    """Run existing native commands; no extra mutation/permission route is introduced."""
    selected=resolve(profile,catalog,project_ref=project_ref,goal_ref=goal_ref)
    need(operation in READ_OPERATIONS|PROJECT_OPERATIONS,"unsupported-workspace-operation")
    need(not any(a in ("--repo","--store") or a.startswith(("--repo=","--store=")) for a in arguments),"dispatch-context-override")
    entry=Path(selected["entrypoint"])
    need(not entry.is_absolute() and ".." not in entry.parts,"unsafe-runtime-entrypoint")
    host=root/entry
    need(host.resolve().is_relative_to(root.resolve()) and host.is_file(),"runtime-entrypoint-unavailable")
    if host.suffix == ".mjs":
        launcher=shutil.which("node")
        need(launcher is not None,"node-runtime-unavailable")
        cmd=[launcher,str(host),"--repo",str(root)]
    else:
        cmd=[sys.executable,"-B",str(host),"--repo",str(root)]
    if operation in PROJECT_OPERATIONS:
        need(selected["project_ref"] is not None,"project-required-for-operation")
        need(profile["home"]["mode"]!="external","external-workspace-write-forbidden")
        need(store is not None,"explicit-native-store-required")
    if store is not None:
        store=Path(store).resolve()
        bindings=catalog.get("native_store_bindings",[])
        binding=next((b for b in bindings if b["workspace_ref"]==profile["workspace_ref"] and
                      b["project_ref"]==selected["project_ref"] and Path(b["store_path"]).resolve()==store),None)
        need(binding is not None,"native-store-binding-required")
        # Replay verifies the sealed configuration, baseline, signatures and source freshness.
        sys.path.insert(0,str(root/"implementation/lab-runtime/v2"))
        from lab_runtime.store import Store
        from lab_runtime.common import RuntimeFault
        try: data=Store(store,root).replay(require_current=True)
        except (RuntimeFault,OSError,ValueError) as exc: raise Refusal("native-store-invalid") from exc
        need(data["config"]["scope_ref"]==binding["native_scope_ref"],"native-store-scope-mismatch")
        need(data["projection"]["state"]["payload"]["project_ref"]==selected["project_ref"],"native-store-project-mismatch")
        if operation in {"review","authorize","apply"}:
            need(bool(arguments) and not arguments[0].startswith("--"),"proposal-argument-required")
            proposal=load(arguments[0])
            targets=proposal.get("targets",[]) if isinstance(proposal,dict) else []
            need(isinstance(targets,list),"proposal-targets-invalid")
            for target in targets:
                if not isinstance(target,dict):continue
                record=target.get("record")
                if record is None and target.get("operation")=="withdraw":
                    record=data["projection"]["subjects"].get(target.get("version_ref"),{}).get("record")
                if not isinstance(record,dict):continue
                payload=record.get("payload",{})
                owner_project=payload.get("project_ref") if isinstance(payload,dict) else None
                if owner_project is not None:
                    need(owner_project==selected["project_ref"],"proposal-project-mismatch")
        cmd += ["--store",str(store)]
        p=subprocess.run([*cmd,operation,*arguments],cwd=root,text=True,capture_output=True)
    else:
        # A source-only read must not fall through to the operator's default private store.
        with tempfile.TemporaryDirectory(prefix="lab-workspace-inspection-") as temporary:
            p=subprocess.run([*cmd,"--store",str(Path(temporary)/"uninitialized"),operation,*arguments],
                             cwd=root,text=True,capture_output=True)
    try: result=json.loads(p.stdout) if p.stdout else None
    except json.JSONDecodeError: result=None
    return {"workspace_context":selected,"native_exit_code":p.returncode,"native_result":result,
            "native_stderr":p.stderr,"authority_effect":"none"},p.returncode
def main(argv=None):
    parser=argparse.ArgumentParser(description="Shared Lab workspace model and native runtime dispatch")
    sub=parser.add_subparsers(dest="command",required=True)
    sub.add_parser("verify");sub.add_parser("list")
    for name in ("inspect","resolve","dispatch"):
        p=sub.add_parser(name);p.add_argument("workspace");p.add_argument("--project");p.add_argument("--revision");p.add_argument("--goal")
        if name=="dispatch":
            p.add_argument("--operation",required=True);p.add_argument("--store",type=Path)
    args,unknown=parser.parse_known_args(argv)
    if unknown and args.command!="dispatch": parser.error("unexpected arguments")
    try:
        catalog,selected=profiles()
        if args.command=="verify": result=verify_layout()
        elif args.command=="list": result={"model_version":MODEL,"workspaces":selected,"authority_effect":"none"}
        else:
            need(args.workspace in selected,"workspace-not-selected");profile=selected[args.workspace]
            context(profile,project_ref=args.project,goal_ref=args.goal,expected_revision=args.revision)
            if args.command=="inspect":result=profile
            elif args.command=="resolve":result=resolve(profile,catalog,project_ref=args.project,goal_ref=args.goal)
            else:
                remaining=unknown[1:] if unknown[:1]==["--"] else unknown
                result,code=dispatch(profile,catalog,args.operation,remaining,project_ref=args.project,goal_ref=args.goal,store=args.store)
                print(json.dumps(result,indent=2));return code
        print(json.dumps(result,indent=2));return 0
    except (Refusal,OSError,ValueError,KeyError) as exc:
        print(json.dumps({"result":"REFUSED","reason":str(exc),"authority_effect":"none"}),file=sys.stderr);return 2
if __name__=="__main__":raise SystemExit(main())
