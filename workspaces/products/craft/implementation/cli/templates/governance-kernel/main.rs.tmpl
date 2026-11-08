use smallest_governance_program::{
    evaluate, AuthorityDisposition, FactValue, GovernanceFact, GovernanceFactSet,
    GovernanceProgram, GovernanceRequest, GovernanceRequestInput, ProgramClause, ProgramId,
    VersionedRef,
};

fn request() -> GovernanceRequest {
    GovernanceRequest::form(GovernanceRequestInput {
        principal: "synthetic:demo-agent",
        subject: "candidate:demo-document",
        action: "publish",
        target: "public:demo-document",
        consequence: "demo-document-becomes-public",
        requested_effect: "publication",
        integration_surface: "synthetic:demo-surface",
        mode: "evaluate_only",
        context: "smallest-governance-program",
    })
    .expect("static request is valid")
}

fn refs() -> (VersionedRef, VersionedRef, VersionedRef) {
    (
        VersionedRef::form("demo-publication-rule", 1).expect("static ref is valid"),
        VersionedRef::form("demo-constitution", 1).expect("static ref is valid"),
        VersionedRef::form("demo-publication-binding", 1).expect("static ref is valid"),
    )
}

fn program(selector: GovernanceRequest) -> GovernanceProgram {
    let (rule, constitution, binding) = refs();
    GovernanceProgram::form(
        ProgramId::form("smallest-publication-governance").expect("static id is valid"),
        1,
        selector,
        vec![
            ProgramClause::RequireAdoptedRule {
                rule: rule.clone(),
                constitution,
            },
            ProgramClause::RequireApplicableRule { rule: rule.clone() },
            ProgramClause::RequireActiveBinding { rule, binding },
            ProgramClause::require_authority_permit("repository").expect("static layer is valid"),
            ProgramClause::require_authority_permit("publication").expect("static layer is valid"),
        ],
    )
    .expect("static program is valid")
}

fn fact(scope: &GovernanceRequest, value: FactValue) -> GovernanceFact {
    GovernanceFact::form(
        scope.clone(),
        "synthetic:demo-source",
        "synthetic:demo-verifier",
        value,
    )
    .expect("static fact is valid")
}

fn complete_facts(
    scope: &GovernanceRequest,
    publication: AuthorityDisposition,
) -> Vec<GovernanceFact> {
    let (rule, constitution, binding) = refs();
    vec![
        fact(
            scope,
            FactValue::RuleAdopted {
                rule: rule.clone(),
                constitution,
                adopted: true,
            },
        ),
        fact(
            scope,
            FactValue::RuleApplicable {
                rule: rule.clone(),
                applicable: true,
            },
        ),
        fact(
            scope,
            FactValue::EnforcementBindingActive {
                rule,
                binding,
                active: true,
            },
        ),
        fact(
            scope,
            FactValue::Authority {
                layer: "repository".to_owned(),
                disposition: AuthorityDisposition::Permit,
            },
        ),
        fact(
            scope,
            FactValue::Authority {
                layer: "publication".to_owned(),
                disposition: publication,
            },
        ),
    ]
}

fn facts_for(
    scenario: &str,
    scope: &GovernanceRequest,
) -> Result<Vec<GovernanceFact>, &'static str> {
    match scenario {
        "allow" => Ok(complete_facts(scope, AuthorityDisposition::Permit)),
        "deny" => Ok(complete_facts(scope, AuthorityDisposition::Forbid)),
        "abstain" => {
            let mut facts = complete_facts(scope, AuthorityDisposition::Permit);
            facts
                .retain(|fact| !matches!(fact.value(), FactValue::EnforcementBindingActive { .. }));
            Ok(facts)
        }
        "error" => {
            let mut facts = complete_facts(scope, AuthorityDisposition::Permit);
            facts.push(fact(
                scope,
                FactValue::Authority {
                    layer: "publication".to_owned(),
                    disposition: AuthorityDisposition::Forbid,
                },
            ));
            Ok(facts)
        }
        _ => Err("expected one scenario: allow, deny, abstain, or error"),
    }
}

fn main() {
    let scenario = std::env::args()
        .nth(1)
        .unwrap_or_else(|| "abstain".to_owned());
    let request = request();
    let program = program(request.clone());
    let facts = match facts_for(&scenario, &request) {
        Ok(facts) => facts,
        Err(message) => {
            eprintln!("error: {message}");
            std::process::exit(2);
        }
    };
    let evaluation = evaluate(&program, &request, &GovernanceFactSet::form(facts));

    println!("program={}/v{}", program.id().as_str(), program.version());
    println!("request={} {}", request.action(), request.target());
    println!("scenario={scenario}");
    println!("effect_ceiling=no_effect");
    println!("verdict={}", evaluation.verdict);
    println!("reason={}", evaluation.reason);
    println!("effect_executed=false");
}
