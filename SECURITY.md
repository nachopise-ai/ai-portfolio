# Security policy

This repository is a public learning portfolio for AI engineering. It is not a security support service or a place to submit confidential material.

## Safe contributions

- Use synthetic or clearly reusable public documents in fixtures.
- Keep provider keys, passwords, tokens, certificates, and local configuration in environment variables.
- Commit `.env.example` with names and safe example values only; never commit a real `.env` file.
- Do not add personal documents, customer data, employer data, or copied proprietary datasets.
- If a secret appears in a local checkout, remove it from the working tree and rotate it before publishing. Do not reproduce it in an issue or pull request.

## Reporting a possible leak

After publication, use a private GitHub security advisory for a suspected repository secret or sensitive-data exposure. Do not open a public issue containing the secret or the affected document.

## Scope boundary

The project documents local verification and production-shaped patterns. It does not claim to be production-ready or to provide a security guarantee.
