"""Invoke an existing registered carrier renderer; never rewrite its fixtures."""
from pathlib import Path
import importlib.util,json,sys
q=json.load(sys.stdin)
generator=Path(q["generator"]).resolve()
spec=importlib.util.spec_from_file_location("selected_record_generator",generator)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
renderer=getattr(module,"module",module)
print(json.dumps({"markdown":renderer.render_instance(q["descriptor"],q["body"])}))
