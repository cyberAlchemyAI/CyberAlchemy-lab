"""Dependency controls use isolated sources and explicit candidate declarations."""
import copy
import json
import sys
import unittest
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(HERE),str(HERE/'tests')]
import dependencies as d
import test_A02 as fixtures
sys.path.insert(0,str(d.PACKET_UNIT))
import build_review_packet as draft


class DependencyControls(unittest.TestCase):
    def setUp(self):
        self.fixture=fixtures.CaptureTests();self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
        row=copy.deepcopy(self.fixture.entries[-1]);row.update(definition_id='DEF-C',term='Gamma',path='authority/definitions/DEF-C-1.0.0.json')
        self.fixture.entries.append(row);self.fixture.registry['current_lookup']['DEF-C']='DEF-C@1.0.0'
        for row in self.fixture.entries:
            document={'definition_id':row['definition_id'],'version':row['version'],'term':row['term'],'voices':{'scientific_formal':{'normative_statement':'A scoped candidate concept.'}},'boundaries':{'note':'Meaning review is pending.'}}
            raw=json.dumps(document).encode();self.fixture.write(row['path'],raw);row['sha256']=d.r.digest(raw)
        self.fixture.save_registry();self.snapshot=d.r.capture(self.fixture.root)
        self.refs={row['definition_id']:d.source_ref(row) for row in self.snapshot['current_entries']}
        self.packets={key:draft.draft(ref,d.correspondence.source_document(self.snapshot,ref)) for key,ref in self.refs.items()}

    def use(self,left,right,kind='semantic-use',ref=None):
        packet=self.packets[left];ref=self.refs[right] if ref is None else ref
        if kind=='semantic-use' and ref not in packet['interpretation']['depends_on']:packet['interpretation']['depends_on'].append(copy.deepcopy(ref))
        packet['dependency_links'].append({'kind':kind,'clause_id':packet['interpretation']['clauses'][0]['clause_id'],'dependency_ref':copy.deepcopy(ref),'rationale':'An explicitly selected semantic dependency in this synthetic review control.'})

    def policy(self,left,right,value='joint-analysis'):
        return {'from_source':self.refs[left],'to_source':self.refs[right],'classification':value,'basis':'Explicit candidate policy for the synthetic cyclic pair.','review_ref':'review:synthetic-agent-control'}

    def compile(self,roots=('DEF-C',),packets=None,**kwargs):
        return d.compile_graph(self.snapshot,[self.refs[key] for key in roots],list(self.packets.values()) if packets is None else packets,**kwargs)

    def fault(self,code,callback):
        with self.assertRaises(d.GraphFault) as caught:callback()
        self.assertEqual(code,caught.exception.code)

    def chain(self):self.use('DEF-C','DEF-A');self.use('DEF-A','DEF-B')
    def mutual(self):self.use('DEF-C','DEF-A');self.use('DEF-A','DEF-B');self.use('DEF-B','DEF-A')

    def test_transitive_exact_closure_and_dependency_first_order(self):
        self.chain();out=self.compile()
        self.assertEqual([['DEF-B@1.0.0'],['DEF-A@2.0.0'],['DEF-C@1.0.0']],out['execution_order'])
        self.assertEqual(3,len(out['nodes']));self.assertEqual(2,len(out['edges']));self.assertEqual(self.refs['DEF-A'],out['edges'][0]['from_source'])
        self.assertFalse(out['semantic_ready']);self.assertEqual('requires-independent-review',out['edge_denominator'])

    def test_mutual_scc_accepted_only_for_joint_analysis(self):
        self.mutual();out=self.compile(cycle_policies=[self.policy('DEF-A','DEF-B'),self.policy('DEF-B','DEF-A')])
        self.assertEqual([['DEF-A@2.0.0','DEF-B@1.0.0'],['DEF-C@1.0.0']],out['execution_order'])
        self.assertEqual('accepted-for-joint-analysis',out['cycle_reviews'][0]['disposition']);self.assertFalse(out['semantic_ready'])
        self.assertIn('least-fixed-point',out['cycle_reviews'][0]['recursive_semantics'])

    def test_prohibited_constraining_cycle_separately_rejected(self):
        self.mutual();out=self.compile(cycle_policies=[self.policy('DEF-A','DEF-B','prohibited-constraining'),self.policy('DEF-B','DEF-A')])
        self.assertEqual('rejected-prohibited-cycle',out['status']);self.assertEqual(2,len(out['execution_order']))

    def test_unclassified_cycle_retains_unresolved_gate(self):
        self.mutual();out=self.compile(cycle_policies=[self.policy('DEF-A','DEF-B')])
        self.assertEqual('unresolved-cycle-classification',out['cycle_reviews'][0]['disposition'])

    def test_reverse_closure_includes_all_consumers_and_mutual_peers(self):
        self.mutual();out=self.compile()
        self.assertEqual(['DEF-A@2.0.0','DEF-B@1.0.0','DEF-C@1.0.0'],out['reverse_affected_closure']['DEF-A@2.0.0'])
        self.assertEqual(['DEF-C@1.0.0'],out['reverse_affected_closure']['DEF-C@1.0.0'])

    def test_missing_transitive_packet_is_explicitly_unresolved(self):
        self.chain();out=self.compile(packets=[self.packets['DEF-A'],self.packets['DEF-C']])
        self.assertEqual(['DEF-B@1.0.0'],out['missing_or_quarantined_interpretations']);self.assertEqual('DEF-B@1.0.0',out['unresolved'][0]['to'])
        self.assertEqual(2,len(out['edges']))

    def test_unbound_declared_edge_is_quarantined_not_silently_accepted(self):
        ref=copy.deepcopy(self.refs['DEF-B']);ref['version_ref']='DEF-B@9.0.0';self.use('DEF-C','DEF-B',ref=ref)
        out=self.compile(packets=[self.packets['DEF-C']])
        self.assertEqual([],out['edges']);self.assertEqual('invalid-correspondence-packet',out['unresolved'][0]['reason'])
        self.assertEqual('DEF-B@9.0.0',out['unresolved'][0]['declared_links'][0]['dependency_ref']['version_ref'])
        self.assertEqual('unbound-current-dependency',out['unresolved'][0]['check']['diagnostics'][0]['code'])

    def test_imported_and_unresolved_mentions_do_not_produce_semantic_edges(self):
        self.use('DEF-C','DEF-A','imported-traceability');self.use('DEF-C','DEF-B','unresolved')
        out=self.compile(packets=[self.packets['DEF-C']]);self.assertEqual([],out['edges']);self.assertEqual(1,len(out['nodes']));self.assertEqual(2,len(out['traceability_links']))
        self.assertTrue(all(not row['promoted_to_semantic_edge'] for row in out['traceability_links']))

    def test_independent_edge_denominator_cannot_omit_transitive_use(self):
        self.chain();expected=[{'from_source':self.refs['DEF-C'],'to_source':self.refs['DEF-A']},{'from_source':self.refs['DEF-A'],'to_source':self.refs['DEF-B']}]
        out=self.compile(required_edges=expected);self.assertEqual('separately-compared',out['edge_denominator'])
        self.fault('required-edge-denominator-mismatch',lambda:self.compile(required_edges=expected[:1]))

    def test_duplicate_selected_interpretation_or_root_cannot_choose_a_scope(self):
        self.fault('ambiguous-selected-interpretation',lambda:self.compile(packets=[self.packets['DEF-C'],self.packets['DEF-C']]))
        self.fault('duplicate-selected-root',lambda:self.compile(roots=('DEF-C','DEF-C'),packets=[]))

    def test_stale_source_and_wrong_version_never_rebind_by_label(self):
        bad=copy.deepcopy(self.packets['DEF-C']);bad['interpretation']['source']['sha256']='0'*64
        self.fault('unbound-packet-source',lambda:self.compile(packets=[bad]))
        ref=copy.deepcopy(self.refs['DEF-C']);ref['version_ref']='DEF-A@2.0.0'
        self.fault('unbound-selected-root',lambda:d.compile_graph(self.snapshot,[ref],[]))

    def test_self_loop_is_a_cycle_with_separate_policy(self):
        self.use('DEF-C','DEF-C');out=self.compile(packets=[self.packets['DEF-C']],cycle_policies=[self.policy('DEF-C','DEF-C')])
        self.assertEqual(1,len(out['cycle_reviews']));self.assertEqual('accepted-for-joint-analysis',out['cycle_reviews'][0]['disposition'])

    def test_policy_cannot_apply_without_declared_edge_or_replace_prior_classification(self):
        self.chain();self.fault('cycle-policy-without-declared-edge',lambda:self.compile(cycle_policies=[self.policy('DEF-B','DEF-A')]))
        self.fault('duplicate-cycle-policy',lambda:self.compile(cycle_policies=[self.policy('DEF-A','DEF-B'),self.policy('DEF-A','DEF-B')]))

    def test_hash_is_recomputed_and_independent_inputs_reject_forged_graph(self):
        self.chain();out=self.compile();bad=copy.deepcopy(out);bad['execution_order'].reverse();bad.pop('graph_sha256');bad['graph_sha256']=d.digest(bad)
        self.fault('dependency-graph-integrity-mismatch',lambda:d.verify_graph(bad,self.snapshot,[self.refs['DEF-C']],list(self.packets.values())))
        self.assertEqual('PASS',d.verify_graph(out,self.snapshot,[self.refs['DEF-C']],list(self.packets.values()))['result'])

    def test_deterministic_graph_projection_retains_original_input_digest(self):
        self.chain();one=self.compile();two=self.compile(packets=list(reversed(list(self.packets.values()))))
        for key in ['nodes','edges','strongly_connected_components','execution_order','reverse_affected_closure']:self.assertEqual(one[key],two[key])
        self.assertNotEqual(one['input_bindings']['packets_sha256'],two['input_bindings']['packets_sha256'])

    def test_long_chain_scc_walk_does_not_use_python_recursion(self):
        nodes=[str(i) for i in range(2500)];adjacency={node:{str(int(node)+1)} if int(node)<2499 else set() for node in nodes}
        groups=d.components(nodes,adjacency);order=d.execution_order(groups,adjacency);self.assertEqual(['2499'],order[0]);self.assertEqual(['0'],order[-1])


if __name__=='__main__':unittest.main()
