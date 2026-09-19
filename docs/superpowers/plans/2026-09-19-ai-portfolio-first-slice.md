# AI Portfolio Hub First Slice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a credible local GitHub portfolio hub for junior AI Engineer / AI Application Engineer applications, with a documented flagship project and repeatable quality/security conventions.

**Architecture:** Keep the hub documentation-focused and link to separate project repositories when each project has independently reproducible code. The first slice creates the hub README, project catalogue, reusable project template, `enterprise-rag-evals` brief, roadmap, contribution/security hygiene, and a local validation script; it does not pretend that the AI system is already implemented.

**Tech Stack:** Markdown, Git, PowerShell validation, GitHub Actions-ready conventions; no paid AI provider, secret, or runtime dependency in this slice.

**Spec:** `docs/superpowers/specs/2026-09-19-ai-portfolio-design.md`

## Global Constraints

- Target role: junior **AI Engineer**, **AI Application Engineer**, or **AI Solutions Engineer**.
- Public data must be synthetic or clearly reusable; never add private documents or credentials.
- Quantitative claims require a reproducible command, test, trace, or documented experiment.
- The flagship project's public path must work without a paid external model by using fixture mode.
- The flagship technical baseline is Python 3.12+, FastAPI, Pydantic, pytest, PostgreSQL/pgvector, Docker Compose, GitHub Actions, and provider-neutral model adapters.
- Local verification is not described as production deployment.
- Publishing to GitHub is outside this implementation slice until the user is authenticated and confirms the final external action.

## Review Focus

- A recruiter must understand the target role and strongest project within one minute; Task 2 checks the README headings and first-screen summary.
- A reviewer must not mistake a plan for implemented software; Task 3 checks explicit status labels and demo/verified/production boundaries.
- Public documentation must not leak secrets or personal data; Task 1 and Task 5 scan for secret-shaped values and private-path references.
- Every project entry must include reproducible evidence rather than unsupported metrics; Task 3 and Task 5 check required evidence fields.
- Local links and required files must remain usable after future additions; Task 5 validates paths and reports missing required sections.

---

### Task 1: Add repository hygiene and contribution boundaries

**Files:**
- Create: `.gitignore`
- Create: `SECURITY.md`
- Create: `CONTRIBUTING.md`

**Interfaces:**
- Produces the privacy, secret-handling, and contribution rules referenced by the hub README and validation script.

- [ ] **Step 1: Write the ignore rules**

Create `.gitignore` with Python caches/virtual environments, Node dependencies/build output, local environment files, key files, local data, test artifacts, and OS/editor files. Preserve `.env.example` while ignoring all other `.env` files.

- [ ] **Step 2: Write the security policy**

Create `SECURITY.md` stating that public fixtures must be synthetic/public, secrets must use environment variables, suspected credential leaks must not be reproduced in issues, and this is a learning portfolio rather than a security support service. Do not add an email address that the user has not supplied.

- [ ] **Step 3: Write contribution rules**

Create `CONTRIBUTING.md` requiring focused changes, reproducible commands, evidence for metrics, tests for behavior changes, and explicit labels for mock, fixture, locally verified, and publicly deployed behavior. Pull requests must not add secrets or private data.

- [ ] **Step 4: Verify hygiene**

Run:

```powershell
git diff --check
git check-ignore -q .env
if ($LASTEXITCODE -ne 0) { throw '.env is not ignored' }
git check-ignore -q .venv/
if ($LASTEXITCODE -ne 0) { throw '.venv/ is not ignored' }
```

Expected: no whitespace errors and both paths are ignored.

- [ ] **Step 5: Commit**

```powershell
git add .gitignore SECURITY.md CONTRIBUTING.md
git -c user.name='Nacho' -c user.email='portfolio@localhost' commit -m 'chore: add portfolio hygiene rules'
```

### Task 2: Create the recruiter-facing hub README and project catalogue

**Files:**
- Create: `README.md`
- Create: `PROJECTS.md`

**Interfaces:**
- `README.md` links to `PROJECTS.md`, `ROADMAP.md`, `docs/project-template.md`, `docs/projects/enterprise-rag-evals.md`, `SECURITY.md`, and `CONTRIBUTING.md`.
- `PROJECTS.md` is the single catalogue used to track project status and evidence.

- [ ] **Step 1: Write the first-screen README**

Create `README.md` with the title `Nacho — AI Engineer Portfolio`, the sentence `Construyo aplicaciones de IA aplicadas: datos, APIs, RAG, agentes, evaluación y despliegue.`, a visible construction/status note, a featured-project link, grouped skills, a `What I prove` section, a projects link, and footer links. Keep the contact section empty until the user chooses a public contact.

Do not add invented job history, certificates, employers, model accuracy, customer numbers, or deployment URLs.

- [ ] **Step 2: Write the project catalogue**

Create `PROJECTS.md` with initial rows for `enterprise-rag-evals`, `agentops-ticket-resolver`, `document-intelligence-es`, and `mlops-forecasting`. Each row must include role signal, status, evidence, and next gate. Add an `Existing work to audit` section for ViralForge AI, Kinepolis experience, and Webloom without private filesystem paths.

- [ ] **Step 3: Verify hub links and claims**

Run:

```powershell
git diff --check
rg -n "enterprise-rag-evals|PROJECTS.md|ROADMAP.md|project-template|SECURITY.md|CONTRIBUTING.md" README.md PROJECTS.md
```

Expected: every required target appears in the hub and no diff whitespace errors are reported.

- [ ] **Step 4: Commit**

```powershell
git add README.md PROJECTS.md
git -c user.name='Nacho' -c user.email='portfolio@localhost' commit -m 'docs: add AI engineer portfolio hub'
```

### Task 3: Add the reusable project template and flagship brief

**Files:**
- Create: `docs/project-template.md`
- Create: `docs/projects/enterprise-rag-evals.md`

**Interfaces:**
- The template defines the README sections every later project must fill.
- The flagship brief is a design/status document, not an implementation claim.

- [ ] **Step 1: Write the project template**

Create `docs/project-template.md` with these required headings in order:

```markdown
# Project title
## Status
## Problem
## Why it matters
## Architecture
## Data and privacy
## Evaluation
## Security and failure modes
## Local quick start
## Evidence
## Cost and latency
## What is not implemented
## Next improvement
```

Under `Status`, require one of `planned`, `in progress`, `locally verified`, or `public demo`. Under `Evidence`, require a command or artifact for every metric.

- [ ] **Step 2: Write the flagship brief**

Create `docs/projects/enterprise-rag-evals.md` covering the operations-document problem, PDF/Markdown/text ingestion, normalization, chunking, keyword/semantic retrieval, citations, typed API, fixture model adapter, evaluation runner, structured logs, request IDs, and Docker-shaped local deployment. State that data is synthetic or reusable public data only.

Include an evaluation plan for retrieval hit rate, citation coverage, fixture-answer correctness, refusal behavior, latency, and estimated cost, with a versioned dataset and regression tolerance. Include threats for prompt injection in retrieved text, malformed files, unsupported types, secrets/PII, empty indexes, ambiguity, provider timeouts, and ungrounded answers.

Add a Mermaid data-flow diagram and explicit sections saying that no live provider, public deployment, customer data, or production SLA exists yet. Define the next slice as fixture document -> index -> question -> cited answer -> regression test.

- [ ] **Step 3: Verify status boundaries**

Run:

```powershell
rg -n "Status|not implemented|production|synthetic|evaluation|citation|prompt injection" docs/project-template.md docs/projects/enterprise-rag-evals.md
```

Expected: both documents distinguish design, local verification, and production deployment.

- [ ] **Step 4: Commit**

```powershell
git add docs/project-template.md docs/projects/enterprise-rag-evals.md
git -c user.name='Nacho' -c user.email='portfolio@localhost' commit -m 'docs: define reusable project template and flagship brief'
```

### Task 4: Add the career-oriented roadmap

**Files:**
- Create: `ROADMAP.md`

**Interfaces:**
- `ROADMAP.md` is linked by `README.md` and tracks the sequence from portfolio setup to interview-ready evidence.

- [ ] **Step 1: Write the roadmap**

Create four phases: Foundation; Flagship vertical slice; Production-shaped AI engineering; Portfolio expansion. For each phase include the expected artifact, evidence required, and interview question it enables Nacho to answer.

Include the explicit anti-sprawl rule: `No se añade otro proyecto destacado hasta que el actual tenga README reproducible, tests y evidencia.`

- [ ] **Step 2: Verify roadmap**

Run:

```powershell
rg -n "Foundation|Flagship|Production-shaped|Portfolio expansion|artifact|Evidence|interview|No se añade" ROADMAP.md
```

Expected: all four phases and the anti-sprawl rule are present.

- [ ] **Step 3: Commit**

```powershell
git add ROADMAP.md
git -c user.name='Nacho' -c user.email='portfolio@localhost' commit -m 'docs: add AI engineer portfolio roadmap'
```

### Task 5: Add repeatable portfolio validation

**Files:**
- Create: `scripts/validate-portfolio.ps1`

**Interfaces:**
- The script exits with code `0` only when required files exist, required README headings are present, local Markdown targets resolve, and obvious secret-shaped values are absent.
- The script accepts no network, provider key, or user-specific argument.

- [ ] **Step 1: Write the validation script**

The script must set `$ErrorActionPreference = 'Stop'`, derive the repository root from `$PSScriptRoot`, check the required files from Tasks 1–4, check the README headings `AI Engineer`, `Featured project`, `Projects`, and `What I prove`, scan tracked Markdown/PowerShell files for token-shaped values (`sk-`, `AKIA`, private-key headers, and `ghp_`), and resolve local Markdown links from `README.md` and `PROJECTS.md`. On success it prints `Portfolio validation passed.`.

- [ ] **Step 2: Run validation**

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\\scripts\\validate-portfolio.ps1
git diff --check
git status --short
```

Expected: validation passes, no diff errors appear, and only intended files are changed.

- [ ] **Step 3: Commit**

```powershell
git add scripts/validate-portfolio.ps1
git -c user.name='Nacho' -c user.email='portfolio@localhost' commit -m 'test: add portfolio documentation validator'
```

### Task 6: Final local review and handoff

**Files:**
- Modify: none unless validation finds a defect in Tasks 1–5.

**Interfaces:**
- Produces the verified local repository path and commit history needed for the later GitHub publication step.

- [ ] **Step 1: Run the complete local audit**

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\\scripts\\validate-portfolio.ps1
git diff --check
git log --oneline --decorate --max-count=8
git status --short --branch
```

Expected: validation passes, the branch has no uncommitted files, and the history contains the design commit plus the implementation commits.

- [ ] **Step 2: Review the public boundary**

Run:

```powershell
rg -n -i "C:\\\\Users|C:/Users|portfolio@localhost|sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}" README.md PROJECTS.md ROADMAP.md SECURITY.md CONTRIBUTING.md docs scripts
```

Expected: no personal filesystem paths, token-shaped values, or invented contact details.

- [ ] **Step 3: Commit only review corrections**

```powershell
git add -A
git -c user.name='Nacho' -c user.email='portfolio@localhost' commit -m 'docs: polish portfolio handoff'
```

Run the complete local audit again after this commit.
