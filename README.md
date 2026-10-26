# 🛡️ Bayora Shield

### Secure Infrastructure for Adversarial AI Safety Testing

**Bayora Shield is an AI security testing platform designed to support controlled adversarial testing, defensive evaluation, and auditable security assessments of AI systems.**

The project explores how Red Team and Blue Team components can operate within a controlled testing architecture, helping teams identify potential AI security weaknesses while maintaining a structured evaluation process.

Built for **Hack in Hills '26 — Challenge 04: Securing Adversarial AI Safety Testing Infrastructure.**

---

## 📌 Table of Contents

* [The Problem](#-the-problem)
* [Our Solution](#-our-solution)
* [Key Features](#-key-features)
* [System Architecture](#-system-architecture)
* [Security Design](#-security-design)
* [Commit-Reveal Evaluation](#-commit-reveal-evaluation)
* [Technology Stack](#-technology-stack)
* [Getting Started](#-getting-started)
* [API Endpoints](#-api-endpoints)
* [Testing](#-testing)
* [Current Limitations](#-current-limitations)
* [Roadmap](#-roadmap)
* [Contributing](#-contributing)
* [License](#-license)

---

## 🎯 The Problem

AI safety testing often requires security researchers to simulate adversarial inputs, evaluate defensive mechanisms, and analyze the behavior of AI-powered systems.

However, an AI security testing environment must address several challenges:

* **Isolation:** Adversarial testing components should not have unrestricted access to defensive systems.
* **Controlled evaluation:** Testing workflows should follow defined evaluation procedures.
* **Auditability:** Security-related activities should be recorded and their integrity verifiable.
* **Evaluation integrity:** The system should support workflows that separate an evaluation commitment from the subsequent reveal of evaluation inputs.
* **Defensive assessment:** Security teams need a structured way to evaluate detection and defense mechanisms.

Without careful architectural controls, an adversarial testing environment can itself become a security risk.

## 💡 Our Solution

Bayora Shield provides a modular backend for orchestrating AI security evaluations.

It separates major responsibilities into dedicated services:

* **Red Team:** Supplies adversarial test cases and testing suites.
* **Blue Team:** Evaluates incoming inputs using defensive inspection logic.
* **API Backend:** Coordinates requests, evaluation workflows, audit operations, and Commit-Reveal interactions.
* **Model Gateway:** Provides an intermediary between the API and model-serving infrastructure.
* **Model Service:** Hosts the model-facing service component.

The architecture is designed to support controlled testing and improve the traceability of security evaluations.

> **Project goal:** Build a practical foundation for safer, more controlled, and more auditable AI security testing.

---

## ✨ Key Features

### 1. Red Team Testing

The Red Team component provides adversarial test cases for evaluating AI security defenses.

Capabilities include:

* Individual adversarial evaluations.
* Red Team test-suite execution.
* Integration with the API evaluation workflow.

### 2. Blue Team Defense

The Blue Team component performs defensive inspection of incoming inputs.

Capabilities include:

* Input inspection.
* Security validation workflows.
* Blue Team test-suite execution.
* Integration with the backend evaluation process.

Detection results should be interpreted within the scope of the implemented test cases and supported defensive logic.

### 3. Modular Service Architecture

Bayora Shield separates application responsibilities across multiple services.

This separation supports independent development, clearer service boundaries, and more controlled communication between components.

### 4. Audit Logging and Integrity Verification

The platform includes audit-related endpoints for retrieving recorded events and checking audit integrity.

Available operations include:

* Retrieving audit events.
* Verifying audit records.
* Supporting traceability during security evaluations.

Audit integrity verification does not, by itself, establish that every event is complete, authentic, or tamper-proof against an attacker with sufficient privileges.

### 5. Commit-Reveal Evaluation

Bayora Shield implements a Commit-Reveal workflow designed to separate commitment to evaluation data from its subsequent reveal and verification.

The workflow supports:

1. Creating a commitment.
2. Performing a blind evaluation.
3. Revealing the evaluation payload.
4. Verifying the payload against the commitment.
5. Rejecting invalid or conflicting evaluation operations.

The backend includes concurrency handling intended to prevent the same pending evaluation from being processed simultaneously more than once.

**Important:** The current implementation stores pending Commit-Reveal state in memory. Durable storage and recovery across service restarts remain future improvements.

### 6. Containerized Services

The project uses Docker-based service deployment.

Configured container hardening measures include:

* Read-only root filesystems for Red Team and Blue Team containers.
* Dropped Linux capabilities.
* No-new-privileges settings.
* Temporary filesystems for `/tmp`.
* Resource limits.
* Loopback-only host bindings for the Red Team and Blue Team services.

These controls reduce selected risks but do not guarantee complete isolation.

---

## 🏗️ System Architecture

```text
                   ┌──────────────────────────┐
                   │       User / Client      │
                   └────────────┬─────────────┘
                                │
                                ▼
                   ┌──────────────────────────┐
                   │      FastAPI Backend     │
                   │                          │
                   │  API Orchestration       │
                   │  Security Validation     │
                   │  Evaluation Workflows    │
                   │  Audit Operations        │
                   │  Commit-Reveal           │
                   └──────┬──────────┬────────┘
                          │          │
                ┌─────────┘          └─────────┐
                ▼                              ▼
    ┌─────────────────────┐        ┌─────────────────────┐
    │     Red Team        │        │     Blue Team       │
    │                     │        │                     │
    │ Adversarial Tests   │        │ Defensive Inspection│
    │ Test Suites         │        │ Security Evaluation │
    └─────────────────────┘        └─────────────────────┘

                   Model Interaction Path
                              │
                              ▼
                   ┌──────────────────────────┐
                   │       Model Gateway      │
                   └────────────┬─────────────┘
                                │
                                ▼
                   ┌──────────────────────────┐
                   │       Model Service      │
                   └──────────────────────────┘
```

*This diagram represents the logical architecture. It is not a complete network-isolation or deployment diagram.*

### Architecture Principles

* **Separation of responsibilities:** Each service has a defined role.
* **Controlled communication:** Services communicate through configured interfaces.
* **Defense in depth:** Container hardening complements application-level controls.
* **Auditable workflows:** Security operations have dedicated audit functionality.
* **Evaluation integrity:** Commit-Reveal mechanisms support structured evaluation procedures.

---

## 🔐 Security Design

Bayora Shield incorporates multiple security-oriented design measures.

| Security area         | Implemented approach                                                                              | Important qualification                                           |
| --------------------- | ------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| Container hardening   | Read-only root filesystem, dropped capabilities, and no-new-privileges for Red Team and Blue Team | Does not eliminate all container escape or host risks             |
| Temporary storage     | `/tmp` mounted as temporary storage                                                               | Does not establish complete data isolation                        |
| Resource management   | Container resource limits                                                                         | Effectiveness depends on the configured limits                    |
| Host exposure         | Red Team and Blue Team ports bound to loopback                                                    | Other host and container communication paths still require review |
| Service communication | Dedicated Docker networks                                                                         | Network membership alone does not guarantee isolation             |
| Audit integrity       | Audit retrieval and verification endpoints                                                        | Guarantees depend on the implementation and threat model          |
| Evaluation integrity  | Commit-Reveal workflow                                                                            | Current pending state is held in memory                           |
| Concurrent evaluation | Locking and an in-progress state                                                                  | Tested behavior is limited to the exercised scenarios             |

### Network Isolation: Current Status

The architecture uses separate Docker networks to separate service responsibilities.

However, a network separation design is not proof that all unauthorized communication paths are blocked. End-to-end Red Team-to-Blue Team isolation still requires conclusive verification of the actual routing, firewall rules, and service communication paths.

**Bayora Shield does not claim complete or production-grade network isolation at this stage.**

---

## 🔏 Commit-Reveal Evaluation

The Commit-Reveal mechanism is intended to help structure evaluation workflows so that a commitment is established before the corresponding evaluation data is revealed.

### Workflow

```text
      1. Create Commitment
               │
               ▼
      2. Store Commitment
               │
               ▼
      3. Run Blind Evaluation
               │
               ▼
      4. Reveal Evaluation Data
               │
               ▼
      5. Verify Commitment
               │
               ▼
      6. Accept or Reject
         the Operation
```

### Intended Benefits

* Separates commitment from reveal.
* Supports verification of revealed evaluation data.
* Rejects invalid or conflicting operations.
* Includes handling for concurrent evaluation requests.

### Current Implementation Considerations

* Pending commitments are stored in application memory.
* Pending state is lost if the API process restarts.
* Persistent storage and recovery are not yet provided by the current in-memory design.
* The mechanism does not independently guarantee the truthfulness of an evaluation result or prevent every possible attack.

---

## 🧰 Technology Stack

| Technology             | Purpose                               |
| ---------------------- | ------------------------------------- |
| Python                 | Application development               |
| FastAPI                | Backend API framework                 |
| Docker                 | Containerization                      |
| Docker Compose         | Multi-service orchestration           |
| Pytest                 | Automated testing                     |
| Ruff                   | Python linting                        |
| Git and GitHub         | Version control and source management |
| Linux networking tools | Network and firewall configuration    |

The exact dependencies and service configuration are defined by the repository's dependency and Docker configuration files.

---

## 🚀 Getting Started

### Prerequisites

Install the following tools:

* Git
* Docker Desktop with Docker Compose
* Python version compatible with the project
* PowerShell on Windows, or an appropriate terminal on Linux/macOS

### 1. Clone the Repository

```bash
git clone https://github.com/praveena-pawar/bayora-shield.git
cd bayora-shield
```

### 2. Configure the Environment

Review the repository for environment configuration files and documented variables.

Create any required local environment file using the variable names expected by the application.

**Do not commit API keys, credentials, or other secrets to GitHub.**

### 3. Start the Services

From the directory containing `compose.yaml`, run:

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

> These are the standard Docker Compose commands. Confirm the actual service configuration, required environment variables, and startup dependencies in the repository before relying on them for a clean installation.

### 4. Check the API

If the API is configured to publish host port `8001`, open:

```text
http://localhost:8001/health
```

If FastAPI documentation is enabled, visit:

```text
http://localhost:8001/docs
```

The configured API port and endpoint availability depend on the Compose configuration.

### 5. Run the Automated Tests

Create and activate a virtual environment if required by your development setup, then install the project's declared development dependencies.

Run:

```bash
python -m pytest -v
```

Run Ruff against the application-code directories:

```bash
python -m ruff check backend security evaluator
```

These commands reflect the project's existing test and lint workflow. They assume the relevant dependencies are installed.

---

## 🔌 API Endpoints

The backend includes the following endpoint groups.

| Endpoint                               | Purpose                                   |
| -------------------------------------- | ----------------------------------------- |
| `GET /health`                          | Health check                              |
| `GET /audit/events`                    | Retrieve audit events                     |
| `GET /audit/verify`                    | Verify audit integrity                    |
| `POST /security/inspect`               | Inspect an input using security logic     |
| `/inference`                           | Inference workflow                        |
| `POST /security/validate`              | Validate security-related inputs          |
| `POST /evaluation/run`                 | Run an evaluation                         |
| `POST /evaluation/run-red-team`        | Run a Red Team evaluation                 |
| `POST /evaluation/run-red-team-suite`  | Run the Red Team suite                    |
| `POST /evaluation/run-blue-team-suite` | Run the Blue Team suite                   |
| `/commit-reveal/commit`                | Create an evaluation commitment           |
| `/commit-reveal/verify`                | Verify a revealed payload                 |
| `/commit-reveal/run-evaluation`        | Run a blind evaluation                    |
| `/commit-reveal/evaluate`              | Perform the Commit-Reveal evaluation flow |

**Note:** The table identifies endpoint paths and their intended roles. Confirm each HTTP method, request schema, response schema, and status code in the running API documentation before integrating a client.

---

## 🧪 Testing

Testing is an important part of the Bayora Shield development process.

### Recorded Test Results

| Test area                        | Result                                         |
| -------------------------------- | ---------------------------------------------- |
| Full automated test suite        | 144 tests passed in a previous run             |
| Commit-Reveal API tests          | 11 tests passed in a targeted run              |
| Application-code Ruff checks     | Passed in a previous run                       |
| Red Team security detector suite | 15 of 15 test cases passed in the recorded run |

The full-suite result predates the addition of the eleventh Commit-Reveal API test. Therefore, the 144-test result should not be presented as a verified result for the latest complete test suite.

The Red Team detector results describe performance on the tested cases only. They do not establish general security effectiveness against unseen attacks.

---

## ⚠️ Current Limitations

Bayora Shield is a hackathon prototype, not a production-certified security platform.

Known areas for further work include:

1. **Network isolation verification:** End-to-end isolation between adversarial and defensive services requires conclusive verification.
2. **Persistent state:** Commit-Reveal state is stored in memory and does not survive API restarts.
3. **Audit hardening:** Stronger guarantees against privileged tampering require additional controls.
4. **Evaluation coverage:** Larger, more diverse adversarial datasets are needed to assess defensive performance.
5. **Observability:** More comprehensive metrics, structured logs, and operational monitoring would improve debugging and evaluation.
6. **Production readiness:** Authentication, authorization, secret management, deployment hardening, and recovery procedures require further assessment.

These limitations are explicitly acknowledged so that the prototype's demonstrated capabilities are distinguishable from future goals.

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

* [ ] Build the frontend dashboard.
* [ ] Display security inspection results.
* [ ] Provide an interface for running evaluations.
* [ ] Display audit and verification results.
* [ ] Demonstrate the Commit-Reveal workflow.

### Phase 3 — Security Verification

* [ ] Verify service-to-service isolation end to end.
* [ ] Validate firewall behavior using repeatable tests.
* [ ] Expand adversarial test coverage.
* [ ] Document verified security guarantees and remaining risks.

### Phase 4 — Reliability and Deployment

* [ ] Add persistent storage for evaluation state.
* [ ] Improve error reporting and operational visibility.
* [ ] Add recovery and restart-handling procedures.
* [ ] Prepare repeatable deployment and demonstration instructions.

---

## 🤝 Contributing

Contributions that improve the platform's reliability, security, testing, documentation, and usability are welcome.

Suggested contribution workflow:

1. Fork the repository.
2. Create a feature branch.
3. Make a focused change.
4. Add or update tests.
5. Run the relevant test suite.
6. Open a pull request explaining the change and its verification.

Please do not include secrets, credentials, or sensitive testing data in commits.

---

## 📜 License

A license has not been specified in this README.

Before publishing the project for reuse, add an appropriate `LICENSE` file and ensure that any third-party dependencies and assets are used according to their licenses.

---

## 👥 Project

**Project:** Bayora Shield
**Event:** Hack in Hills '26
**Challenge:** Challenge 04 — Securing Adversarial AI Safety Testing Infrastructure

**Repository:** [bayora-shield](https://github.com/praveena-pawar/bayora-shield)

---

### Building Safer AI Security Testing Infrastructure

Bayora Shield explores how adversarial testing, defensive evaluation, controlled service communication, and auditable workflows can contribute to more responsible AI security testing.

*The project is under active development. Security claims should be interpreted according to the implemented controls and available test evidence.*
