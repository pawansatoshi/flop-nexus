# FLOP Nexus Production Checklist

## Product
- [x] Guided onboarding
- [x] Missions
- [x] Activity checker entry point
- [x] Reputation model
- [x] Rankings API
- [x] Agent discovery
- [x] Task/evidence foundation
- [x] Privacy-safe DID display
- [x] Independent reward disclaimer
- [x] X/Telegram farming excluded

## Security
- [x] Private keys/passphrases are not requested by the web UI
- [x] Signed-event verification uses the DID public identity
- [x] Self-interaction penalty exists in reputation
- [x] API models enforce bounded input fields
- [x] No secrets committed to the repository

## Reliability
- [x] `/healthz` endpoint
- [x] Ruff linting in CI
- [x] Pytest in CI
- [x] Python compile check in CI
- [x] Safe Ruff autofix self-healing job
- [x] No fabricated production metrics

## Deployment boundary

The repository is production-oriented, but durable production persistence must use a managed database. The default SQLite store is appropriate for local/demo execution and should not be treated as durable serverless storage. External integrations must use server-side environment secrets and only documented/public interfaces.

## Integration policy

Technocore is consumed as an interoperability layer. FLOP official repositories are not forked or merged into Nexus merely to claim affiliation. Upstream PRs are appropriate only for genuine, independently discovered interoperability or security improvements.

X/Twitter and Telegram missions are intentionally excluded from the product.

## Release gate

A release is considered technically ready only after:

1. CI passes.
2. `/healthz` returns `status=ok` in production.
3. The deployed homepage loads without runtime errors.
4. No secret or private credential is present in browser code.
5. Live integrations are labelled according to their verification status.
6. No Nexus metric is presented as an official FLOP allocation or airdrop guarantee.
