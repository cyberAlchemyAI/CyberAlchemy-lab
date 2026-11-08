# Security

Report suspected vulnerabilities privately to the repository owner. Do not publish exploit details before triage.

The stable compiler product treats source files as untrusted, rejects symbolic-link traversal, verifies source digests, caps individual JSON inputs at 8 MiB, caps project graph cardinalities, and times out external validation tools. Generated output must still be reviewed and executed with least privilege.

The experimental runtime, including PostgreSQL integration, is not a production security boundary.

The stable deployment-recipe generator accepts only normalized contained
UTF-8 regular files, rejects symbolic links, secret-like inputs, Terraform
state, traversal, mutable base images, duplicate JSON keys, and oversized
trees, and binds every selected input and generated artifact by SHA-256. Its
AWS target requires private encrypted RDS, immutable ECR repositories,
digest-pinned task images, non-root read-only containers, Secrets Manager
references, and explicit network rules. Generated Terraform and Dockerfiles
are reviewable recipes, not deployment authorization; operators must validate
provider plans, costs, IAM, recovery, and environment-specific policy before
any separately authorized external effect.
