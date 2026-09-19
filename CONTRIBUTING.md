# Contributing

This portfolio favors small, reproducible changes that demonstrate real engineering judgment.

## Before opening a change

- Explain the problem and the behavior that changes.
- Keep the change focused on one project or one documentation concern.
- Run the documented validation command and any project-specific tests.
- Support every metric with a reproducible command, test, trace, or saved experiment artifact.
- Mark behavior honestly as `mock`, `fixture`, `locally verified`, or `public demo`.

## Data and secrets

- Use synthetic or clearly reusable public data only.
- Never commit credentials, private documents, personal identifiers, or proprietary company data.
- Keep secrets in environment variables and add safe names to `.env.example` instead.

## Review standard

A reviewer should be able to understand the change, reproduce the relevant check locally, and distinguish a design claim from implemented and verified behavior.
