# 🛡️ Bayora Shield

### Secure Infrastructure for Adversarial AI Safety Testing

**Bayora Shield is an AI security testing platform prototype designed to support controlled adversarial testing, defensive evaluation, and auditable security assessments of AI systems.**

Built for **Hack in Hills '26 — Challenge 04: Securing Adversarial AI Safety Testing Infrastructure**.

> **Project Status:** Working demonstration prototype. Security guarantees are limited to implemented controls and tested scenarios. This project is not a production-certified security platform.

---

## 🌐 Project Links

* **Live Demo:** https://bayora-shield.vercel.app/
* **GitHub Repository:** https://github.com/praveena-pawar/bayora-shield
* **API Health Check:** https://barbie-nothing-gary-solomon.trycloudflare.com/health
* **API Documentation:** https://barbie-nothing-gary-solomon.trycloudflare.com/docs

> **Demo Availability:** The frontend is hosted on Vercel, while the backend currently runs locally and is exposed through a temporary Cloudflare Tunnel. The backend depends on the host computer, Docker services, internet connectivity, and the tunnel remaining available. The tunnel URL may change.

---

## 📑 Table of Contents

* [Problem Statement](#-problem-statement)
* [Our Solution](#-our-solution)
* [Key Features](#-key-features)
* [System Architecture](#-system-architecture)
* [Security Design](#-security-design)
* [Commit-Reveal Workflow](#-commit-reveal-workflow)
* [Technology Stack](#-technology-stack)
* [Getting Started](#-getting-started)
* [API Endpoints](#-api-endpoints)
* [Testing](#-testing)
* [Current Limitations](#-current-limitations)
* [Roadmap](#-roadmap)
* [Contributing](#-contributing)
* [License](#-license)

---

## 🎯 Problem Statement

Adversarial AI security testing requires an environment where attacks can be evaluated, defensive mechanisms can be assessed, and the resulting evidence can be inspected.

However, a poorly isolated testing environment can introduce additional risks:

* **Payload Exposure:** Adversarial inputs may become visible to defensive components prematurely.
* **Cross-Service Access:** Testing components may gain unintended access to other services.
* **Context Contamination:** Data from one evaluation may affect another.
* **Resource Contention:** Uncontrolled resource usage can interfere with evaluation results.
* **Audit Integrity Risks:** Evaluation records may be modified without reliable detection.
* **Unreliable Evaluation:** Environmental weaknesses can undermine the validity of security results.

Bayora Shield explores how service separation, controlled evaluation workflows, and audit verification can help address these challenges.

---

## 💡 Our Solution

Bayora Shield provides a modular architecture for coordinating AI security evaluations.

The system separates responsibilities across several services:

* **Red Team:** Executes the available adversarial test cases and test suites.
* **Blue Team:** Performs defensive inspection using the implemented security logic.
* **FastAPI Backend:** Coordinates evaluation workflows, security operations, and audit functionality.
* **Model Gateway:** Acts as an intermediary for model-related requests.
* **Model Service:** Provides the model-facing service component.
* **Web Dashboard:** Presents the available testing and evaluation workflows.

The goal is to make AI security testing more structured, observable, and auditable.

---

## ✨ Key Features

### 🔴 1. Red Team Testing

The Red Team component provides adversarial testing capabilities.

Features include:

* Execution of the available Red Team test suite.
* Evaluation of implemented adversarial test cases.
* Integration with backend evaluation workflows.
* Results that help assess the implemented defensive mechanisms.

The current dashboard supports the available testing workflows. Arbitrary user-supplied Red Team payloads should not be considered supported unless that capability is implemented and verified.

### 🔵 2. Blue Team Defensive Evaluation

The Blue Team component evaluates inputs using the implemented defensive inspection logic.

Features include:

* Execution of the available Blue Team test suite.
* Defensive evaluation results.
* Integration with backend security workflows.
* Evaluation of the implemented detection mechanisms.

**Note:** Results apply to the tested cases and implemented detection logic. They do not guarantee detection of every real-world attack.

### 🔐 3. Commit-Reveal Workflow

The Commit-Reveal workflow separates the creation of a commitment from the later reveal and verification of an evaluation payload.

The workflow supports:

1. Creating a commitment.
2. Running blind evaluation.
3. Revealing the evaluation payload.
4. Verifying the payload against the commitment.
5. Accepting or rejecting operations according to the implemented verification logic.

The current implementation stores pending Commit-Reveal state in application memory. Pending operations may be lost if the API process restarts.

### 📋 4. Audit Explorer

The Audit Explorer provides access to available audit records and integrity checks.

Features include:

* Retrieving audit events.
* Verifying audit integrity.
* Inspecting records associated with evaluation activity.

Audit verification can identify changes that violate the implemented verification scheme. It does not independently guarantee that every event is complete or protect against all privileged attacks.

### 🐳 5. Containerized Service Architecture

The project uses Docker and Docker Compose to run its services.

The current configuration includes selected hardening measures for Red Team and Blue Team containers, including:

* Read-only root filesystems.
* Dropped Linux capabilities.
* No-new-privileges settings.
* Temporary filesystems.
* Resource limits.
* Loopback-only host bindings for their published ports.

These controls reduce selected risks but do not guarantee complete isolation.

---

## 🏗️ System Architecture

```text
                    Browser / User
                          |
                          v
                  Web Dashboard (Vite)
                          |
                          v
                   FastAPI Backend
                    /      |      \
                   v       v       v
              Red Team  Blue Team  Audit /
               Service  Service   Commit-Reveal
                    \      |      /
                     \     |     /
                      v    v    v
                      Model Gateway
                            |
                            v
                       Model Service
```

### Architecture Components

| Component           | Responsibility                                                  |
| ------------------- | --------------------------------------------------------------- |
| Frontend            | Displays the available evaluation workflows and results         |
| FastAPI Backend     | Coordinates API requests and evaluation operations              |
| Red Team Service    | Executes adversarial test cases                                 |
| Blue Team Service   | Performs defensive inspection and evaluation                    |
| Model Gateway       | Intermediates model-related requests                            |
| Model Service       | Provides the model-facing component                             |
| Audit Functionality | Supports event retrieval and integrity verification             |
| Commit-Reveal       | Supports commitment, evaluation, reveal, and verification steps |

> This is a logical architecture diagram, not proof of complete network isolation. Actual communication paths and security boundaries must be verified against the active Docker configuration and runtime behavior.

---

## 🔒 Security Design

Bayora Shield incorporates multiple security-oriented controls while acknowledging the limitations of a hackathon prototype.

| Security Area       | Current Approach                                                                         | Important Qualification                                 |
| ------------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| Container Hardening | Read-only filesystems, dropped capabilities, and no-new-privileges for selected services | Does not eliminate all container or host risks          |
| Temporary Storage   | Temporary filesystem for `/tmp` where configured                                         | Does not prove complete data isolation                  |
| Resource Management | Container resource limits                                                                | Effectiveness depends on the active configuration       |
| Host Exposure       | Red Team and Blue Team published ports bound to loopback                                 | Other communication paths require review                |
| Service Networking  | Dedicated Docker networks as configured                                                  | Network membership alone does not prove isolation       |
| Audit Integrity     | Audit retrieval and verification endpoints                                               | Guarantees depend on the implemented scheme             |
| Commit-Reveal       | Commitment, blind evaluation, reveal, and verification                                   | Pending state is stored in memory                       |
| Evaluation Coverage | Automated tests and implemented adversarial cases                                        | Does not establish effectiveness against unseen attacks |

### Security Scope

Bayora Shield does **not** claim complete or production-grade network isolation at this stage.

End-to-end isolation requires repeatable verification of actual routing, service communication paths, and unauthorized-access attempts.

The platform should be treated as a demonstration prototype rather than a production-certified security boundary.

---

## 🔏 Commit-Reveal Workflow

The Commit-Reveal mechanism helps structure evaluation workflows so that a commitment is created before the corresponding payload is revealed.

```text
       1. Create Commitment
                |
                v
       2. Run Blind Evaluation
                |
                v
       3. Reveal Payload
                |
                v
       4. Verify Commitment
                |
                v
       5. Accept or Reject
          the Operation
```

### Intended Benefits

* Separates commitment creation from reveal.
* Supports verification of revealed evaluation data.
* Rejects invalid or conflicting operations where implemented.
* Includes handling for concurrent evaluation requests.

### Current Limitations

* Pending commitment state is stored in application memory.
* Pending state is lost if the API process restarts.
* Persistent storage and recovery are not provided by the current in-memory design.
* The workflow does not independently prove that an evaluation result is truthful or prevent every possible attack.

---

## 🧰 Technology Stack

| Technology        | Purpose                                                |
| ----------------- | ------------------------------------------------------ |
| Python            | Backend and service implementation                     |
| FastAPI           | Backend API framework                                  |
| TypeScript        | Frontend development                                   |
| React             | Frontend user interface                                |
| Vite              | Frontend development and build tooling                 |
| Docker            | Containerization                                       |
| Docker Compose    | Multi-service orchestration                            |
| Pytest            | Automated testing                                      |
| Ruff              | Python linting                                         |
| Git               | Version control                                        |
| GitHub            | Source code hosting                                    |
| Vercel            | Frontend hosting                                       |
| Cloudflare Tunnel | Temporary public access to the locally running backend |

The repository's dependency manifests, Dockerfiles, and Compose configuration define the exact dependencies and service settings.

---

## 🚀 Getting Started

### Prerequisites

Install the following tools:

* Git
* Docker Desktop with Docker Compose
* Python compatible with the project
* Node.js and npm for frontend development

### 1. Clone the Repository

```bash
git clone https://github.com/praveena-pawar/bayora-shield.git
cd bayora-shield
```

### 2. Configure Environment Variables

Review the repository's configuration and service files for required environment variables.

Create local environment files only where the project expects them.

**Never commit API keys, credentials, access tokens, or other secrets to GitHub.**

### 3. Build and Start the Services

From the repository root, run:

```bash
docker compose up -d --build
```

Check the service status:

```bash
docker compose ps
```

Inspect service logs when troubleshooting:

```bash
docker compose logs --tail=100
```

### 4. Check the Backend API

If the Compose configuration publishes the API on host port `8001`, open:

* **Health Check:** http://localhost:8001/health
* **API Documentation:** http://localhost:8001/docs

The available endpoints depend on the active service configuration.

### 5. Run Backend Tests

Install the project's declared dependencies and development dependencies, then run:

```bash
python -m pytest -q
```

Run lint checks if Ruff is installed:

```bash
python -m ruff check backend security evaluator
```

### 6. Stop the Services

```bash
docker compose down
```

This stops and removes the Compose containers and network. Persistent volumes, if configured, may remain.

---

## 🔌 API Endpoints

The backend includes endpoint groups for health checks, security inspection, evaluation, audit operations, and Commit-Reveal.

| Endpoint                               | Purpose                                           |
| -------------------------------------- | ------------------------------------------------- |
| `GET /health`                          | Health check                                      |
| `GET /audit/events`                    | Retrieve audit events                             |
| `GET /audit/verify`                    | Verify audit integrity                            |
| `POST /security/inspect`               | Inspect an input using implemented security logic |
| `/inference`                           | Model-related inference workflow                  |
| `POST /security/validate`              | Validate security-related inputs                  |
| `POST /evaluation/run`                 | Run an evaluation                                 |
| `POST /evaluation/run-red-team`        | Run a Red Team evaluation                         |
| `POST /evaluation/run-red-team-suite`  | Run the Red Team test suite                       |
| `POST /evaluation/run-blue-team-suite` | Run the Blue Team test suite                      |
| `/commit-reveal/commit`                | Create an evaluation commitment                   |
| `/commit-reveal/verify`                | Verify a revealed payload                         |
| `/commit-reveal/run-evaluation`        | Run blind evaluation                              |
| `/commit-reveal/evaluate`              | Run the Commit-Reveal evaluation flow             |

**Important:** This table describes intended endpoint roles. Use the running API documentation at `/docs` to confirm exact HTTP methods, request schemas, response schemas, and status codes.

---

## 🧪 Testing

The project has an automated backend test suite and recorded manual UI checks.

| Test Area                    | Recorded Result                              |
| ---------------------------- | -------------------------------------------- |
| Backend automated test suite | 145 tests passed in the latest reported run  |
| Red Team detector suite      | 15 of 15 test cases passed in a recorded run |
| Red Team UI                  | Manually checked                             |
| Blue Team UI                 | Manually checked                             |
| Commit-Reveal workflow       | Manually checked                             |
| Audit Explorer               | Manually checked                             |

These results reflect the tested version and scenarios. They do not guarantee general security effectiveness or production readiness.

Re-run the tests against the exact commit being submitted to confirm the current results.

---

## ⚠️ Current Limitations

Bayora Shield is a hackathon prototype, not a production-certified security platform.

Known areas for further improvement include:

1. **Network Isolation Verification:** End-to-end Red Team-to-Blue Team isolation needs repeatable tests against actual runtime communication paths.
2. **Persistent State:** Commit-Reveal state is stored in memory and does not survive API restarts.
3. **Audit Hardening:** Stronger protections against privileged tampering and independent audit evidence anchoring require further work.
4. **Evaluation Coverage:** Broader adversarial datasets are needed to evaluate defensive performance.
5. **Observability:** More comprehensive metrics, structured logs, and operational monitoring would improve troubleshooting.
6. **Production Readiness:** Authentication, authorization, secret management, rate limiting, deployment hardening, and recovery procedures require further assessment.
7. **Public Demo Availability:** The backend currently depends on the maintainer's computer, Docker, internet connection, and temporary Cloudflare Tunnel.

---

## 🗺️ Roadmap

### Phase 1 — Core Backend

* [x] Build the FastAPI backend.
* [x] Implement Red Team and Blue Team service components.
* [x] Integrate model-facing services.
* [x] Implement audit endpoints.
* [x] Implement Commit-Reveal workflows.
* [x] Add automated tests for core functionality.

### Phase 2 — Interactive Demonstration

* [x] Deploy the frontend demonstration.
* [x] Display evaluation results.
* [x] Demonstrate Red Team and Blue Team workflows.
* [x] Demonstrate the Commit-Reveal workflow.
* [x] Demonstrate audit retrieval and verification.

### Phase 3 — Security Verification

* [ ] Verify service-to-service isolation end to end.
* [ ] Validate network and unauthorized-access behavior with repeatable tests.
* [ ] Expand adversarial test coverage.
* [ ] Document verified guarantees and residual risks.

### Phase 4 — Reliability and Deployment

* [ ] Add persistent storage for pending evaluation state.
* [ ] Improve error reporting and operational visibility.
* [ ] Add recovery and restart-handling procedures.
* [ ] Prepare repeatable deployment and monitoring instructions.
* [ ] Evaluate custom user-supplied Red Team and Blue Team payloads with server-side validation and safe execution.

---

## 🤝 Contributing

Contributions focused on reliability, security, testing, documentation, and usability are welcome.

1. Fork the repository.
2. Create a focused feature branch.
3. Implement the change and add or update tests.
4. Run the relevant tests and lint checks.
5. Open a pull request explaining the change and how it was verified.

Please do not commit secrets, credentials, or sensitive testing data.

---

## 📜 License

A license has not yet been specified. Until a license is added to the repository, reuse and redistribution permissions should not be assumed.

Add an appropriate `LICENSE` file before explicitly inviting reuse of the code.

---

## 👥 Project Information

* **Project:** Bayora Shield
* **Event:** Hack in Hills '26
* **Challenge:** Challenge 04 — Securing Adversarial AI Safety Testing Infrastructure
* **Repository:** https://github.com/praveena-pawar/bayora-shield
* **Live Demo:** https://bayora-shield.vercel.app/

---

### Building Safer AI Security Testing Infrastructure

Bayora Shield explores how adversarial testing, defensive evaluation, controlled service communication, and auditable workflows can support more trustworthy AI security testing.

*Security claims should be interpreted according to the implemented controls and available test evidence.*
