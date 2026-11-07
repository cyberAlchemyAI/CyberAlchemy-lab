"""Trusted local filesystem wrapper over the same public API."""
import argparse
from pathlib import Path
import sys


def main(argv=None):
    from .integrity import verify
    args = None
    try:
        integrity = verify()
        from .api import API_VERSION, byte_members, encoded_members, invoke
        from .capture import bindings_in
        from .exact import Refusal, binding, bound, decode, encode, read, require, write_package
        p = argparse.ArgumentParser(description="Standalone Define: local candidate preparation and explicit adapters.")
        sub = p.add_subparsers(dest="command", required=True)
        sub.add_parser("doctor");sub.add_parser("api")
        sub.add_parser("capabilities")
        s=sub.add_parser("schema");s.add_argument("kind")
        s=sub.add_parser("example");s.add_argument("--output", required=True)
        for name in ("capture-local", "capture-lab-snapshot"):
            s=sub.add_parser(name);s.add_argument("--request", required=True);s.add_argument("--source-root", required=True)
            s.add_argument("--output", required=True);s.add_argument("--permit-retention", action="store_true")
            if name == "capture-local":s.add_argument("--catalog")
        s=sub.add_parser("prepare");s.add_argument("--request", required=True);s.add_argument("--capture", required=True);s.add_argument("--output", required=True)
        for name in ("inspect", "reconstruct", "materialize", "observe-use"):
            s=sub.add_parser(name);s.add_argument("directory")
            if name != "inspect":s.add_argument("--output", required=True)
            if name == "observe-use":
                s.add_argument("--requested-use", required=True);s.add_argument("--consumer", required=True);s.add_argument("--current-source")
        args=p.parse_args(argv)
        if args.command == "api":
            from .entrypoint import main as api_main
            return api_main()
        if args.command == "doctor":
            result={"version": "0.3.0rc2", "integrity": integrity, "lab_required": False,
                    "local_publication_platform": "Linux with renameat2", "qualification": "not-established", "authority_effect": "none"}
        elif args.command == "example":
            from .example import example_members
            write_package(args.output, example_members())
            result={"outcome": "prepared", "posture": "synthetic-authored-input", "authority_effect": "none"}
        elif args.command == "capture-lab-snapshot":
            from .adapters.lab import snapshot
            record, members, report = snapshot(read(args.request, maximum=1048576), args.source_root, permit_retention=args.permit_retention)
            write_package(args.output, {"capture.json": encode(record), "adapter-observation.json": encode(report),
                                        **{"inputs/"+path:raw for path,raw in members.items()}})
            result={"capture": record, "adapter_observation": report, "authority_effect": "none"}
        else:
            params={};operation=args.command
            if args.command == "schema":params={"kind":args.kind}
            elif args.command == "capture-local":
                operation="capture"
                request_raw=read(args.request,maximum=1048576);request=decode(request_raw)
                selected={}
                catalog_raw=read(args.catalog,maximum=1048576) if args.catalog else None
                for b in bindings_in(request):
                    raw=bound(args.source_root,b)
                    require(selected.setdefault(b["path"],raw)==raw,"mixed-source-epochs")
                if catalog_raw:
                    for row in decode(catalog_raw)["entries"]:
                        b=row["binding"];raw=bound(args.source_root,b)
                        require(selected.setdefault(b["path"],raw)==raw,"mixed-source-epochs")
                params={"request_utf8":request_raw.decode("utf-8"),"inputs":encoded_members(selected),"permit_retention":args.permit_retention}
                if catalog_raw is not None:params["catalog_utf8"]=catalog_raw.decode("utf-8")
            elif args.command == "prepare":
                root=Path(args.capture)
                record_raw=read(root/"capture.json",maximum=1048576);record=decode(record_raw)
                members={}
                for b in bindings_in(record):
                    raw=bound(root/"inputs",b)
                    require(members.setdefault(b["path"],raw)==raw,"mixed-source-epochs")
                params={"request_utf8":read(args.request,maximum=1048576).decode("utf-8"),
                        "capture_utf8":record_raw.decode("utf-8"),"inputs":encoded_members(members)}
            elif args.command in ("inspect","reconstruct","materialize","observe-use"):
                from .package import inspect_local
                raw,_,_,members=inspect_local(args.directory)
                params={"package_members":encoded_members({**members,"manifest.json":raw})}
                if args.command == "observe-use":
                    params.update(requested_use=args.requested_use,consumer=args.consumer)
                    if args.current_source:
                        params["current_source_base64"]=encoded_members({"source":read(args.current_source)})["source"]
            envelope={"api_version":API_VERSION,"id":"cli","operation":operation,"params":params}
            result=invoke(envelope)
            if result["data"] is not None and getattr(args,"output",None):
                data=result["data"]
                if operation=="capture":members={"capture.json":data["capture_utf8"].encode("utf-8"),**{"inputs/"+path:raw for path,raw in byte_members(data["inputs"]).items()}}
                elif operation in ("prepare","reconstruct"):members=byte_members(data["package_members"])
                elif operation=="materialize":members=byte_members(data["members"])
                else:members={"observation.json":encode(data)}
                write_package(args.output,members)
                # Avoid printing all retained source bytes in interactive CLI output.
                result={**result,"data":{k:v for k,v in data.items() if k not in ("package_members","members","inputs","capture_utf8")},
                        "observed_writes":[str(Path(args.output).absolute())]}
        sys.stdout.buffer.write(encode(result))
        return {"invalid-input":2,"blocked":3,"unsupported":4}.get(result.get("outcome"),0)
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        # CLI errors intentionally avoid echoing private filenames or values.
        code=getattr(exc,"code","invalid-input-or-unavailable-source")
        status=getattr(exc,"exit_code",2)
        outcome="outcome-unknown" if code=="publication-outcome-unknown" else {2:"invalid-input",3:"blocked",4:"unsupported"}.get(status,"invalid-input")
        message="Output may have been published; inspect the destination before retrying." if outcome=="outcome-unknown" else "Operation refused; input values withheld."
        sys.stdout.buffer.write((__import__("json").dumps({"api_version":"define.api/v1","id":"cli", "operation":getattr(args,"command",None),
             "outcome":outcome,"diagnostics":[{"code":code,"message":message}],"data":None,"authority_effect":"none"})+"\n").encode())
        return status
