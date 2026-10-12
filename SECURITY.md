# Security Policy

## Supported versions

Business Master is pre-1.0. Security fixes are applied to the current `main` branch; older development snapshots are not maintained as supported releases.

## Reporting a vulnerability

Please do not publish exploit details in a public issue before maintainers have had a reasonable opportunity to assess the report.

Use GitHub's private vulnerability reporting/security advisory mechanism for this repository when available. If private reporting is unavailable, open a minimal issue asking for a private contact channel without including exploit details or secrets.

## Security boundaries

Business Master treats external observations and integration payloads as untrusted input.

Core rules include:

- no raw credentials in Git, logs, evidence records, or model context;
- deterministic capital, accounting, risk, and authorization gates;
- durable idempotency/identity before irreversible external effects;
- explicit source-of-truth ownership across integrations;
- external execution remains behind replaceable boundaries;
- `OBSERVE`, `SHADOW`, and `CONTROL` authority modes must not be silently collapsed.

Business Master is not a hostile-code sandbox. Integrations that execute arbitrary code, browse untrusted content, or hold powerful credentials must provide their own process/network/credential isolation appropriate to their threat model.
