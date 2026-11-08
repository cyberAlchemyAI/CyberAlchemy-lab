"""Assemble an isolated Docker namespace from exact public snapshot members.

Only the fresh context tree is written. WSL system paths are read-only inputs;
this does not build/run an image or claim container qualification.
"""
import argparse,hashlib,importlib.util,json,os,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('_cal_docker_materialize',HERE/'materialize.py');M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
BASE='python:3.12.15-slim-bookworm@sha256:57d96f71de145a98e7ceca18ee4ade77bba4103a33a72dfaea026b23625c6bf0'
TOOLS=('install_from_archive.py','archive.py','materialize.py','native_install.py','configure_installation.py','construction_runner.py')
def build(view,archive,archive_sha,output):
 view=Path(view);archive=Path(archive);output=Path(output);M.need(output.is_absolute() and not output.exists(),'fresh Docker context required');output.mkdir(mode=0o700,parents=True)
 raw=(view/'PACKAGE-MANIFEST.json').read_bytes();package_pin=M.sha(raw);manifest=json.loads(raw);inputs=json.loads((view/'BUILD-INPUTS.json').read_bytes());M.need(inputs['package_manifest_sha256']==package_pin,'Docker public package selection differs')
 actual=hashlib.sha256()
 with archive.open('rb') as stream:
  while data:=stream.read(1024*1024):actual.update(data)
 M.need(actual.hexdigest()==archive_sha,'Docker artifact byte selection differs')
 shutil.copyfile(archive,output/'product.tgz')
 for row in manifest['host_inputs']:
  locator=row['path'];M.need(Path(locator).is_absolute() and '..'not in Path(locator).parts,'closed Docker namespace snapshot locator required')
  selected=inputs['host_inputs'][locator];M.need(all(selected[k]==row[k] for k in ('sha256','size_bytes','mode')),'Docker host snapshot descriptor differs')
  M.write_new(output/'namespace'/locator.lstrip('/'),M.exact(selected['input_path'],row),row['mode'])
 rows={r['path']:r for r in manifest['members']}
 for name in TOOLS:
  rel=str((HERE/name).relative_to(Path(__file__).resolve().parents[4]));row=rows[rel]
  source=inputs['repository_inputs'][rel]['input_path'];M.write_new(output/'tools'/name,M.exact(source,row),row['mode'])
 dockerfile=f'''FROM {BASE}
RUN groupadd --gid 20001 labruntime && useradd --uid 20001 --gid 20001 --create-home --home-dir /home/lab --shell /usr/sbin/nologin labruntime && mkdir -p /home/lab/installations && chmod 700 /home/lab/installations && chown 20001:20001 /home/lab/installations
COPY --chown=20001:20001 namespace/ /
COPY tools/ /opt/lab-tools/
COPY product.tgz /opt/product.tgz
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1 TMPDIR=/tmp
USER 20001:20001
WORKDIR /home/lab
CMD ["python", "-B", "/opt/lab-tools/install_from_archive.py", "/opt/product.tgz", "{archive_sha}", "{package_pin}", "/home/lab/installations/demo"]
'''
 (output/'Dockerfile').write_text(dockerfile);(output/'.dockerignore').write_text('**/__pycache__/\n**/*.pyc\n')
 result={'schema_version':'lab-exact-Docker-namespace-context/v1','result':'CONTEXT-PREPARED-NOT-RUN','base':BASE,'archive_sha256':archive_sha,'package_manifest_sha256':package_pin,'host_namespace_snapshots':len(manifest['host_inputs']),'WSL_system_paths_written':False,'container_started':False,'container_qualified':False,'authority_effect':'none'}
 (output/'CONTEXT-INPUTS.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('view',type=Path);p.add_argument('archive',type=Path);p.add_argument('archive_sha256');p.add_argument('output',type=Path);a=p.parse_args();print(json.dumps(build(a.view,a.archive,a.archive_sha256,a.output),sort_keys=True))
