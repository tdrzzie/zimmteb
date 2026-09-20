# Security

Do not commit tokens, cloud credentials, personal data, private datasets or model
weights. `.env.example` contains empty placeholders; `.env`, model binaries, run
directories and caches are ignored. CI needs no Hugging Face credentials.

Remote model code is disabled and rejected by Phase 1 configuration. Hub models
require immutable commit revisions. Numeric caches use `allow_pickle=False` and
content checksums. Load only trusted model artifacts; a checksum identifies content
but does not establish who authored it. Prefer safetensors checkpoints.

Use safe YAML parsing. Local dataset paths are confined to the dataset root.
Dependency changes require lockfile review and offline integration tests.
The pre-commit private-key hook and tracked-artifact guard complement code review;
they do not guarantee absence of every possible secret.

Report vulnerabilities privately to the repository owner; a public reporting URL
will be added after hosting is configured. Do not include a live credential in an
issue. Revoke leaked credentials first, then remove them from artifacts and history.
