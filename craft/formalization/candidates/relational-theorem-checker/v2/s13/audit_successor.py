"""Strict predecessor audit with checked normalization of its documentary copies."""
from pathlib import Path
import sys,copy
sys.dont_write_bytecode=True
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'s10'));import audit as predecessor
s=predecessor.s

def binding_closure(paths):
 reader=s.read;root=None;normalized=[]
 def read(path):
  nonlocal root
  value=reader(path)
  if not isinstance(value,dict) or 'toolchain_relative_bindings' not in value:return value
  # Only documentary copies in an audit report are changed in memory. The
  # resolved binding remains authoritative and is rechecked independently.
  result=copy.deepcopy(value)
  for entry in result['toolchain_relative_bindings']:
   original=entry['original'];resolved=entry['resolved'];relative=Path(original['path'])
   s.require(not relative.is_absolute() and '..' not in relative.parts and original['path'].startswith('lib/lean/'),'invalid captured toolchain path')
   if root is None:root=s.lean_path().parent.parent
   expected={'path':str((root/relative).relative_to(s.ROOT)),'sha256':original['sha256']}
   s.require(resolved==expected,'captured/resolved toolchain binding mismatch');s.check(resolved)
   entry['original']={'captured_toolchain_path':original['path'],'captured_sha256':original['sha256'],'resolved_and_hash_verified':True}
   normalized.append({'report':s.binding(path),'resolved':resolved})
  return result
 s.read=read
 try:result=predecessor.binding_closure(paths)
 finally:s.read=reader
 result['documentary_toolchain_copies_verified']=normalized
 result['successor_reader']=s.binding(Path(__file__).resolve())
 return result
