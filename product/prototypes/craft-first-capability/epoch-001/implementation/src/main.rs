mod generated_contract;

fn main() {
    if !generated_contract::verify_contract() {
        eprintln!("system-ontology contract verification failed");
        std::process::exit(1);
    }
    println!("{}", generated_contract::smoke_payload());
}

#[cfg(test)]
mod tests {
    use super::generated_contract;

    #[test]
    fn selected_system_obligations_are_present() {
        assert!(generated_contract::verify_contract());
    }

    #[test]
    fn smoke_result_preserves_identity_and_zero_authority() {
        let result = generated_contract::smoke_payload();
        assert!(result.contains("DS-D1.1"));
        assert!(result.contains("Entity"));
        assert!(result.contains("definition_snapshot_witness"));
        assert!(result.contains("\"authority_effect\":\"none\""));
    }
}
