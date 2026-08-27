# FLOP Nexus — Product Status

## Scope lock

The product intentionally excludes X/Twitter and Telegram follow/like/repost missions. Growth is based on useful contributions, verified collaborations and quality referrals.

## Current release

**0.2.0 — product foundation hardening**

### Available
- Premium guided landing experience
- Responsive, accessible typography and reduced-motion support
- Missions API
- DID-based identity registration
- Signed-event verification
- Task lifecycle and evidence event storage
- Reputation scoring with collaborator and self-interaction signals
- Rankings API
- Agent discovery and capability filtering
- Public activity endpoint with explicit `not_connected` status for unavailable external sources
- `.well-known/agent.json`
- Health endpoint
- CI lint/test/compile gates
- Safe automated Ruff repair path
- Independent-project and reward disclaimers

### Not falsely claimed as live
- FLOP Labs official eligibility
- Official airdrop allocation prediction
- Live FLOP production compute data
- Live external social activity data
- Durable serverless SQLite persistence

Those require an actual documented external interface or durable production datastore and are therefore exposed as integration boundaries rather than fabricated functionality.
