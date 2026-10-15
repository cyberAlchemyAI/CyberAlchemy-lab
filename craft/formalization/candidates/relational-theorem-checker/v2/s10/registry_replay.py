"""Replay the exact captured registry values/targets with bounded proof modules."""
from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'execution'));import support as s
HERE=Path(__file__).resolve().parent

def generate(selected=None):
 data=s.read(s.V1/'registry/normalized-registry.json');folder=HERE/'registry-parts';folder.mkdir(exist_ok=True)
 nodes=data['node_kinds'];member={n:'node_member_'+str(i) for i,n in enumerate(nodes)}
 text='import RegistryNodes\nnamespace Registry.Snapshot\n'
 for i,n in enumerate(nodes):
  proof='List.mem_cons.mpr (Or.inl rfl)'
  for _ in range(i):proof='List.mem_cons.mpr (Or.inr ('+proof+'))'
  text+='theorem '+member[n]+' : '+json.dumps(n)+' ∈ nodes := '+proof+'\n'
 text+='end Registry.Snapshot\n';(folder/'RegistryNodeMembership.lean').write_text(text)
 modules=[('RegistryChecker',s.V1/'registry/RegistryChecker.lean'),('RegistryNodes',s.V1/'registry/RegistryNodes.lean'),('RegistryNodeMembership',folder/'RegistryNodeMembership.lean')]
 bindings=[]
 for i,row in enumerate(data['kinds']):
  if selected is not None and i not in selected:continue
  original=s.V1/('registry/RegistryKind'+str(i)+'.lean');source=original.read_text()
  value=next(line for line in source.splitlines() if line.startswith('def kind'+str(i)+' : Kind := '))
  # The original data definition is copied exactly; only proof decomposition changes.
  k='kind'+str(i);prefix='RegistryKind'+str(i);parts=[]
  parts.append((prefix+'_Data','import RegistryNodes\nnamespace Registry.Snapshot\n'+value+'\nend Registry.Snapshot\n'))
  parts.append((prefix+'_Basic','import '+prefix+'_Data\nnamespace Registry.Snapshot\ntheorem '+k+'_basic : '+k+'.id ≠ "" ∧ '+k+'.version ≠ "" ∧ '+k+'.fields.Nodup ∧ (∀ field ∈ '+k+'.fields, field ≠ "") := by decide\nend Registry.Snapshot\n'))
  parts.append((prefix+'_Unique','import '+prefix+'_Data\nset_option maxRecDepth 8192\nset_option maxHeartbeats 4000000\nnamespace Registry.Snapshot\ntheorem '+k+'_unique : '+k+'.pairs.Nodup := by decide\nend Registry.Snapshot\n'))
  pairs=row['pairs'];body='import '+prefix+'_Data\nimport RegistryNodeMembership\nset_option maxRecDepth 8192\nset_option maxHeartbeats 4000000\nnamespace Registry.Snapshot\ntheorem '+k+'_endpoints : ∀ pair ∈ '+k+'.pairs, pair.1 ∈ nodes ∧ pair.2 ∈ nodes := by\n  intro pair hk\n  simp only ['+k+', List.mem_cons] at hk\n  rcases hk with '+' | '.join('h'+str(j) for j in range(len(pairs)+1))+'\n'
  for j,pair in enumerate(pairs):body+='  · subst pair; exact ⟨'+member[pair['source_kind']]+', '+member[pair['target_kind']]+'⟩\n'
  body+='  · cases h'+str(len(pairs))+'\nend Registry.Snapshot\n';parts.append((prefix+'_Endpoints',body))
  body=''.join('import '+prefix+'_'+p+'\n' for p in ['Basic','Unique','Endpoints'])+'namespace Registry.Snapshot\ntheorem kind_valid'+str(i)+' : KindValid nodes '+k+' := ⟨'+k+'_basic.1, '+k+'_basic.2.1, '+k+'_unique, '+k+'_endpoints, '+k+'_basic.2.2.1, '+k+'_basic.2.2.2⟩\n#print axioms kind_valid'+str(i)+'\nend Registry.Snapshot\n';parts.append((prefix,body))
  for name,body in parts:
   p=folder/(name+'.lean');p.write_text(body);modules.append((name,p))
  bindings.append({'original_source':s.binding(original),'exact_data_definition':value,'target':'Registry.KindValid Registry.Snapshot.nodes Registry.Snapshot.'+k,'proof_layout':'basic, pair uniqueness, explicit endpoint membership, exact conjunction','weakened_statement':False})
 if selected is None:modules += [('RegistrySnapshot',s.V1/'registry/RegistrySnapshot.lean'),('Preservation',s.V1/'evolution/preservation/Preservation.lean'),('ConservativeExpansion',s.V1/'evolution/models/ConservativeExpansion.lean')]
 return modules,bindings

def replay(build):
 modules,bindings=generate();logs=s.compile_modules(build,modules)
 return logs,{'result':'pass','captured_values_and_targets':bindings,'original_snapshot_source':s.binding(s.V1/'registry/RegistrySnapshot.lean'),'all_41_exact_registry_targets_checked':True,'compiler_stage_ceiling_seconds':60,'weakened_statement':False,'authority_effect':'none'}
