"""Observe the selected native constructor and retain its actual terminal proof."""
import argparse,hashlib,importlib.util,json,os,subprocess,uuid
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('_cal_private_installer_controls',HERE/'configure_installation.py');C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)
def observe(root,package_pin,receipt_pin,stdout,stderr,returncode):
 root=Path(root).resolve();private=root.parent/'.cal-runtime';raw=(root/'.cal-package-manifest.json').read_bytes();C.need(C.sha(raw)==package_pin,'construction package selection differs');C.need(C.sha((private/'installation.json').read_bytes())==receipt_pin,'selected provisional receipt changed');manifest=json.loads(raw);receipt=json.loads((private/'installation.json').read_bytes());C.need(receipt['phase']=='construct-context','construction proof cannot overwrite ready selection')
 C.need(private.is_dir() and not private.is_symlink() and private.stat().st_uid==os.getuid() and private.stat().st_mode&0o777==0o700,'owned private construction observation root required')
 attempt=private/'construction-attempts'/uuid.uuid4().hex;attempt.mkdir(mode=0o700,parents=True,exist_ok=False)
 C.atomic_control(attempt/'stdout.log',stdout);C.atomic_control(attempt/'stderr.log',stderr)
 C.atomic_control(attempt/'observation.json',C.encoded({'schema_version':'lab-native-construction-process-observation/v1','package_manifest_sha256':package_pin,'construct_receipt_sha256':receipt_pin,'returncode':returncode,'stdout_sha256':C.sha(stdout),'stderr_sha256':C.sha(stderr),'result':'PROCESS-EXITED','authority_effect':'none'}))
 lines=[line for line in stdout.splitlines() if line.strip()];C.need(returncode==0 and lines,'actual native construction failed; captured outputs retained at '+str(attempt));final=json.loads(lines[-1]);C.need(final['result']=='PASS-construction-native-cold-and-fresh-Context','native construction terminal result differs')
 code='implementation/lab-runtime/local-host/t25-portable-family-0001/construction_child.py';row=next(row for row in manifest['members'] if row['path']==code);C.need(C.sha((root/code).read_bytes())==row['sha256'],'selected constructor code changed')
 outcome={'schema_version':'lab-observed-native-construction/v1','package_manifest_sha256':package_pin,'construct_receipt_sha256':receipt_pin,'returncode':returncode,'child_binding':{'path':code,'sha256':row['sha256']},'stdout_sha256':C.sha(stdout),'stderr_sha256':C.sha(stderr),'final_observation':final,'actual_process_observation_directory':str(attempt),'authority_effect':'none'}
 C.need(not (private/'construction-outcome.json').exists(),'actual construction observation already retained')
 C.atomic_control(private/'construction-stdout.log',stdout);C.atomic_control(private/'construction-stderr.log',stderr);C.atomic_control(private/'construction-outcome.json',C.encoded(outcome));return outcome

def run(root,package_pin,receipt_pin):
 root=Path(root).resolve();launcher=root/'implementation/lab-runtime/local-host/t25-native-launcher-0001/selected-python';child=root/'implementation/lab-runtime/local-host/t25-portable-family-0001/construction_child.py'
 try:
  result=subprocess.run([str(launcher),'-B',str(child),'--receipt-pin',receipt_pin],env={'PATH':'/usr/bin:/bin','LC_ALL':'C','PYTHONDONTWRITEBYTECODE':'1','HOME':str(root.parent/'.cal-runtime')},cwd=root,capture_output=True,timeout=2400,check=False)
 except subprocess.TimeoutExpired as error:
  return observe(root,package_pin,receipt_pin,error.stdout or b'',error.stderr or b'',-124)
 return observe(root,package_pin,receipt_pin,result.stdout,result.stderr,result.returncode)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('repository',type=Path);p.add_argument('package_sha256');p.add_argument('construct_receipt_sha256');p.add_argument('--existing-stdout',type=Path);p.add_argument('--existing-stderr',type=Path);p.add_argument('--existing-returncode',type=int);a=p.parse_args()
 if a.existing_stdout is None:result=run(a.repository,a.package_sha256,a.construct_receipt_sha256)
 else:
  C.need(a.existing_stderr is not None and a.existing_returncode is not None,'complete actual prior execution outputs required');result=observe(a.repository,a.package_sha256,a.construct_receipt_sha256,a.existing_stdout.read_bytes(),a.existing_stderr.read_bytes(),a.existing_returncode)
 print(json.dumps(result,sort_keys=True),flush=True)
