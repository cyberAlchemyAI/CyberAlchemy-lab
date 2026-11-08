"""Audited host projection into the independent Registry graph profile."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'obligations'))
import generator as g
s=g.s
d=g.c.r.d
sys.path.insert(0,str(s.BASE/'registry'))
import build_registry as registry_projection


def kind_lean(kind):
    return registry_projection.theory_lean({'node_kinds':[],'kinds':[kind]}).split('kinds := [',1)[1][:-3]


def graph_lean(graph):
    def node(n):
        return '{ ref := '+d.refs(n['ref'])+', kind := '+d.literal(n['kind'])+', contentIdentity := '+d.literal(n['content_identity'])+' }'
    def assertion(e):
        return '{ id := '+d.literal(e['id'])+', kindId := '+d.literal(e['kind'])+', kindVersion := '+d.literal(e['kind_version'])+', source := '+d.refs(e['source'])+', target := '+d.refs(e['target'])+', qualifiers := '+d.rows(list(e['qualifiers'].items()),lambda item:'('+d.literal(item[0])+', '+d.literal(item[1])+')')+' }'
    return '{ nodes := '+d.rows(graph['nodes'],node)+', assertions := '+d.rows(graph['assertions'],assertion)+' }'


def captured_modules():
    result=[]
    for module in s.read(s.BASE/'registry/projection-audit.json')['modules']:
        s.check_binding(module['source']);result.append((module['module'],s.ROOT/module['source']['path']))
    return result


def extension_fixture(proposal):
    classification=g.c.classify(proposal)
    s.require(classification['profile']=='fresh-kind-extension','fixture requires append-only fresh-kind profile')
    g.source_projection(proposal)
    old=proposal['before']['registry'];new=proposal['after']['registry'];added=new['kinds'][len(old['kinds']):]
    text='import RegistrySnapshot\nimport Preservation\nset_option maxRecDepth 8192\nset_option maxHeartbeats 4000000\nnamespace Registry.Evolution.Captured\n'
    text+='def added : List Kind := '+d.rows(added,kind_lean)+'\n'
    text+='def expanded : Theory := { nodeKinds := Snapshot.captured.nodeKinds, kinds := Snapshot.captured.kinds ++ added }\n'
    text+='theorem added_valid : ∀ d ∈ added, KindValid Snapshot.captured.nodeKinds d := by decide\n'
    text+='theorem expanded_valid : TheoryValid expanded := by\n  refine ⟨Snapshot.valid_snapshot.1, Snapshot.valid_snapshot.2.1, by decide, ?_⟩\n  intro d hd\n  change d ∈ Snapshot.captured.kinds ++ added at hd\n  rcases List.mem_append.mp hd with old | fresh\n  · exact Snapshot.valid_snapshot.2.2.2 d old\n  · exact added_valid d fresh\n'
    text+='def extension : FreshExtension Snapshot.captured expanded := { added := added, nodes_equal := rfl, kinds_append := rfl, fresh_ids := by decide, base_valid := Snapshot.valid_snapshot, expanded_valid := expanded_valid }\n'
    text+='def selected : Graph := '+graph_lean(proposal['before']['graph'])+'\n'
    text+='theorem selected_base_valid : Inv Snapshot.captured selected := by\n  exact ⟨Snapshot.valid_snapshot, by decide, by decide, by decide, by decide⟩\n'
    text+='theorem selected_expanded_valid : Inv expanded selected := lift_model extension selected selected_base_valid\n'
    text+='#print axioms expanded_valid\n#print axioms selected_base_valid\n#print axioms selected_expanded_valid\nend Registry.Evolution.Captured\n'
    return text
