def selected_workflow_instance(host, factory, ref, binding, registry, *, authorization=None):
    """Select one source-backed execution instance of the public workflow template.

    The public document is a template: its decision-profile ArtifactRef has a
    zero digest, and the current signed Source has Work but lacks the example's
    Delegation and ContextRequest inputs. Only the first agent-context phase
    may specialize those two fields. All other template bytes remain semantic
    constraints on the private, hash-selected executable definition.
    """
    need(ref == 'transition:agent-context:context-ready',
         'only the selected agent-context instance is available')
    source_binding = registry['definition_binding']
    need((source_binding['path'], source_binding['sha256']) in factory.source_rows,
         'public agent-context template absent from selected API Source')
    public_raw = factory.read_public(source_binding)
    need(sha(public_raw) == source_binding['sha256'],
         'public agent-context template bytes changed')
    public = parse(public_raw)
    need(public['decision_profile']['byte_sha256'] == '0' * 64 and
         [t['transition_ref'] for t in public['transitions']] == [
             'transition:agent-context:context-ready',
             'transition:agent-context:session-ready'] and
         public['transitions'][0]['input_carriers'] == [
             'cal.artifact-type.agent-assignment/v1',
             'cal.artifact-type.delegation/v1',
             'cal.artifact-type.context-request/v1'],
         'original public agent-context placeholder/signature differs')
    need(binding['sha256'] != source_binding['sha256'],
         'uninstantiated public workflow example cannot run')
    raw = (host.vault.material(binding) if authorization is None
           else authorization.material(binding))
    need(sha(raw) == binding['sha256'],
         'private executable workflow definition changed')
    executable = parse(raw)
    need(type(executable) is dict and type(executable.get('decision_profile')) is dict,
         'closed executable workflow instance required')
    profile = executable['decision_profile']
    need(set(profile) == {'scope_ref', 'identity_ref', 'version_ref',
                          'carrier_ref', 'byte_sha256'} and
         profile['carrier_ref'] == 'cal.artifact-type.workflow-decision-profile/v1' and
         profile['scope_ref'] == factory.plan['scope_ref'] and
         profile['byte_sha256'] != '0' * 64,
         'exact current decision-profile header required')
    expected = copy.deepcopy(public)
    expected['decision_profile'] = copy.deepcopy(profile)
    expected['transitions'][0]['input_carriers'] = ['cal.artifact-type.work/v1']
    need(executable == expected,
         'executable agent-context instance differs outside selected Source profile/Work input')
    return executable
