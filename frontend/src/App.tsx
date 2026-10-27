import { useEffect, useState } from "react";

import {
  getHealth,
  runRedTeamSuite,
  runBlueTeamSuite,
  createCommitment,
  runBlindEvaluation,
  revealEvaluation,
  getAuditEvents,
  verifyAuditChain,
  type HealthResponse,
  type CommitResponse,
  type BlindEvaluationResponse,
  type RevealEvaluationResponse,
  type AuditEvent,
} from "./api";

import "./App.css";

type Page =
| "Overview"
| "Red Team"
| "Blue Team"
| "Commit-Reveal"
| "Audit Explorer";

const navigation: { name: Page; icon: string }[] = [
{ name: "Overview", icon: "◈" },
{ name: "Red Team", icon: "⚔" },
{ name: "Blue Team", icon: "⬡" },
{ name: "Commit-Reveal", icon: "⛨" },
{ name: "Audit Explorer", icon: "≡" },
];

function App() {
const [activePage, setActivePage] = useState<Page>("Overview");

const [health, setHealth] = useState<HealthResponse | null>(null);
const [healthError, setHealthError] = useState<string | null>(null);

const [redTeamLoading, setRedTeamLoading] = useState(false);
const [redTeamResult, setRedTeamResult] = useState<unknown>(null);
const [redTeamError, setRedTeamError] = useState<string | null>(null);

const [blueTeamLoading, setBlueTeamLoading] = useState(false);
const [blueTeamResult, setBlueTeamResult] = useState<unknown>(null);
const [blueTeamError, setBlueTeamError] = useState<string | null>(null);

const [commitPayload, setCommitPayload] = useState("");
const [commitResult, setCommitResult] = useState<CommitResponse | null>(null);
const [blindResult, setBlindResult] = useState<BlindEvaluationResponse | null>(null);
const [revealResult, setRevealResult] = useState<RevealEvaluationResponse | null>(null);
const [commitLoading, setCommitLoading] = useState(false);
const [commitError, setCommitError] = useState<string | null>(null);


const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);
const [auditTotal, setAuditTotal] = useState(0);
const [auditLoading, setAuditLoading] = useState(false);
const [auditError, setAuditError] = useState<string | null>(null);
const [auditVerification, setAuditVerification] = useState<unknown>(null);


useEffect(() => {
let cancelled = false;

async function checkHealth() {
  try {
    const result = await getHealth();

    if (!cancelled) {
      setHealth(result);
      setHealthError(null);
    }
  } catch {
    if (!cancelled) {
      setHealth(null);
      setHealthError("API unavailable");
    }
  }
}

void checkHealth();

const interval = window.setInterval(() => {
  void checkHealth();
}, 15000);

return () => {
  cancelled = true;
  window.clearInterval(interval);
};

}, []);

async function handleRunRedTeam() {
setRedTeamLoading(true);
setRedTeamError(null);
setRedTeamResult(null);


try {
  const result = await runRedTeamSuite();
  setRedTeamResult(result);
} catch (error) {
  setRedTeamError(
    error instanceof Error
      ? error.message
      : "An unexpected error occurred.",
  );
} finally {
  setRedTeamLoading(false);
}

}

async function handleRunBlueTeam() {
setBlueTeamLoading(true);
setBlueTeamError(null);

try {
const result = await runBlueTeamSuite();
setBlueTeamResult(result);
} catch (error) {
setBlueTeamError(
error instanceof Error ? error.message : "Unknown error",
);
} finally {
setBlueTeamLoading(false);
}
}



async function handleCreateCommitment() {
  if (!commitPayload.trim()) {
    setCommitError("Please enter a payload first.");
    return;
  }

  setCommitLoading(true);
  setCommitError(null);
  setCommitResult(null);
  setBlindResult(null);
  setRevealResult(null);

  try {
    const result = await createCommitment(commitPayload);
    setCommitResult(result);
  } catch (error) {
    setCommitError(
      error instanceof Error ? error.message : "Commitment creation failed.",
    );
  } finally {
    setCommitLoading(false);
  }
}

async function handleRunBlindEvaluation() {
  if (!commitResult || !blindResult) return;

  setCommitLoading(true);
  setCommitError(null);

  try {
    const result = await runBlindEvaluation(commitResult.commitment_id);
    setBlindResult(result);
  } catch (error) {
    setCommitError(
      error instanceof Error ? error.message : "Blind evaluation failed.",
    );
  } finally {
    setCommitLoading(false);
  }
}

async function handleRevealEvaluation() {
  if (!commitResult) return;

  setCommitLoading(true);
  setCommitError(null);

  try {
    const result = await revealEvaluation(
      commitResult.commitment_id,
      commitPayload,
      blindResult!.nonce,
    );
    setRevealResult(result);
  } catch (error) {
    setCommitError(
      error instanceof Error ? error.message : "Reveal verification failed.",
    );
  } finally {
    setCommitLoading(false);
  }
}


async function handleLoadAuditEvents() {
  setAuditLoading(true);
  setAuditError(null);

  try {
    const result = await getAuditEvents();
    setAuditEvents(result.events);
    setAuditTotal(result.total);
  } catch (error) {
    setAuditError(
      error instanceof Error ? error.message : "Failed to load audit events.",
    );
  } finally {
    setAuditLoading(false);
  }
}

async function handleVerifyAuditChain() {
  setAuditLoading(true);
  setAuditError(null);
  setAuditVerification(null);

  try {
    const result = await verifyAuditChain();
    setAuditVerification(result);

    const auditData = await getAuditEvents();
    setAuditEvents(auditData.events);
    setAuditTotal(auditData.total);
  }catch (error) {
    setAuditError(
      error instanceof Error ? error.message : "Audit verification failed.",
    );
  } finally {
    setAuditLoading(false);
  }
}



return ( <div className="app-shell"> <aside className="sidebar"> <div className="brand"> <div className="brand-mark">B</div> <div> <h1>
BAYORA<span>.</span> </h1> <p>AI SECURITY PLATFORM</p> </div> </div>

    <div className="workspace-label">WORKSPACE</div>

    <nav className="navigation">
      {navigation.map((item) => (
        <button
          key={item.name}
          className={`nav-item ${
            activePage === item.name ? "active" : ""
          }`}
          onClick={() => setActivePage(item.name)}
        >
          <span className="nav-icon">{item.icon}</span>
          <span>{item.name}</span>
          {activePage === item.name && (
            <span className="active-indicator" />
          )}
        </button>
      ))}
    </nav>

    <div className="sidebar-bottom">
      <div className="security-badge">
        <div className="badge-icon">⌘</div>
        <div>
          <strong>Security workspace</strong>
          <p>Adversarial AI testing</p>
        </div>
      </div>

      <div className="sidebar-footer">
        <span className="status-dot" />
        BAYORA SHIELD <span className="version">V1.0</span>
      </div>
    </div>
  </aside>

  <main className="main-area">
    <header className="topbar">
      <div className="breadcrumbs">
        <span>Workspace</span>
        <span className="breadcrumb-separator">/</span>
        <strong>{activePage}</strong>
      </div>

      <div className="topbar-right">
        <span className="environment">
          <span className="status-dot" />
          DEVELOPMENT
        </span>
        <div className="avatar">BS</div>
      </div>
    </header>

    <div className="page-content">
      <section className="welcome-row">
        <div>
          <div className="eyebrow">
            <span className="eyebrow-line" />
            AI SAFETY INFRASTRUCTURE
          </div>

          <h2>
            {activePage === "Overview"
              ? "Security command center."
              : activePage}
          </h2>

          <p className="welcome-description">
            {activePage === "Overview"
              ? "Monitor adversarial testing, inspect defenses, and verify evaluation integrity."
              : `Explore ${activePage.toLowerCase()} operations in Bayora Shield.`}
          </p>
        </div>

        <div className="date-chip">
          <span className="date-dot" />
          HACK IN HILLS '26
        </div>
      </section>

      {activePage === "Overview" ? (
        <>
          <section className="metrics-grid">
            <article className="metric-card">
              <div className="metric-heading">
                <span>PLATFORM</span>
                <span className="metric-icon green">⌁</span>
              </div>

              <div className="metric-value">
                {health?.status === "healthy"
                  ? "ONLINE"
                  : healthError
                    ? "OFFLINE"
                    : "CHECKING"}
              </div>

              <div className="metric-caption">
                <span
                  className={`status-dot ${
                    health?.status === "healthy" ? "" : "muted"
                  }`}
                />
                {health
                  ? `${health.service} · Connected`
                  : healthError ?? "Checking backend connection..."}
              </div>
            </article>

            <article className="metric-card">
              <div className="metric-heading">
                <span>RED TEAM</span>
                <span className="metric-icon red">⚔</span>
              </div>
              <div className="metric-value">01</div>
              <div className="metric-caption">
                Adversarial testing service
              </div>
            </article>

            <article className="metric-card">
              <div className="metric-heading">
                <span>BLUE TEAM</span>
                <span className="metric-icon blue">⬡</span>
              </div>
              <div className="metric-value">01</div>
              <div className="metric-caption">
                Defensive inspection service
              </div>
            </article>

            <article className="metric-card">
              <div className="metric-heading">
                <span>EVALUATION</span>
                <span className="metric-icon purple">◇</span>
              </div>
              <div className="metric-value">
                {redTeamLoading ? "RUNNING" : redTeamResult ? "DONE" : "READY"}
              </div>
              <div className="metric-caption">
                <span
                  className={`status-dot ${
                    redTeamResult ? "" : "muted"
                  }`}
                />
                {redTeamResult
                  ? "Red Team evaluation completed"
                  : "Ready for evaluation"}
              </div>
            </article>
          </section>

          <section className="section-heading">
            <div>
              <h3>Security operations</h3>
              <p>Access the core evaluation workflows.</p>
            </div>
            <span className="section-tag">CORE MODULES · 04</span>
          </section>

          <section className="operations-grid">
            <button
              className="operation-card red-card"
              onClick={() => setActivePage("Red Team")}
            >
              <div className="operation-top">
                <span className="operation-icon red">⚔</span>
                <span className="arrow">↗</span>
              </div>
              <span className="operation-label">MODULE 01</span>
              <h3>Red Team</h3>
              <p>
                Execute adversarial test suites and examine security
                weaknesses.
              </p>
              <span className="operation-link">
                Open testing workspace <span>→</span>
              </span>
            </button>

            <button
              className="operation-card blue-card"
              onClick={() => setActivePage("Blue Team")}
            >
              <div className="operation-top">
                <span className="operation-icon blue">⬡</span>
                <span className="arrow">↗</span>
              </div>
              <span className="operation-label">MODULE 02</span>
              <h3>Blue Team</h3>
              <p>
                Inspect inputs and evaluate defensive responses using
                the security backend.
              </p>
              <span className="operation-link">
                Open defense workspace <span>→</span>
              </span>
            </button>

            <button
              className="operation-card purple-card"
              onClick={() => setActivePage("Commit-Reveal")}
            >
              <div className="operation-top">
                <span className="operation-icon purple">⛨</span>
                <span className="arrow">↗</span>
              </div>
              <span className="operation-label">MODULE 03</span>
              <h3>Commit-Reveal</h3>
              <p>
                Explore commitment creation, blind evaluation, and
                payload verification.
              </p>
              <span className="operation-link">
                Open evaluation workflow <span>→</span>
              </span>
            </button>

            <button
              className="operation-card green-card"
              onClick={() => setActivePage("Audit Explorer")}
            >
              <div className="operation-top">
                <span className="operation-icon green">≡</span>
                <span className="arrow">↗</span>
              </div>
              <span className="operation-label">MODULE 04</span>
              <h3>Audit Explorer</h3>
              <p>
                Review recorded events and inspect audit integrity
                verification results.
              </p>
              <span className="operation-link">
                Open audit workspace <span>→</span>
              </span>
            </button>
          </section>

          <section className="bottom-grid">
            <article className="panel architecture-panel">
              <div className="panel-heading">
                <div>
                  <h3>System architecture</h3>
                  <p>Logical service topology</p>
                </div>
                <span className="live-label">OVERVIEW</span>
              </div>

              <div className="architecture-flow">
                <div className="architecture-node main-node">
                  <span className="node-symbol">B</span>
                  <div>
                    <strong>FastAPI Backend</strong>
                    <span>Orchestration · Evaluation · Audit</span>
                  </div>
                </div>

                <div className="flow-connector">
                  <span />
                  <span />
                </div>

                <div className="architecture-children">
                  <div className="architecture-node">
                    <span className="node-symbol red-symbol">R</span>
                    <div>
                      <strong>Red Team</strong>
                      <span>Adversarial tests</span>
                    </div>
                  </div>

                  <div className="architecture-node">
                    <span className="node-symbol blue-symbol">B</span>
                    <div>
                      <strong>Blue Team</strong>
                      <span>Defensive inspection</span>
                    </div>
                  </div>
                </div>

                <div className="architecture-note">
                  <span>ⓘ</span>
                  Logical architecture only. Network isolation has not
                  yet been conclusively verified.
                </div>
              </div>
            </article>

            <article className="panel integrity-panel">
              <div className="panel-heading">
                <div>
                  <h3>Trust &amp; integrity</h3>
                  <p>Security mechanisms</p>
                </div>
                <span className="shield-symbol">⛨</span>
              </div>

              <div className="integrity-row">
                <div className="integrity-icon green">✓</div>
                <div>
                  <strong>Audit verification</strong>
                  <span>Endpoint implemented</span>
                </div>
                <span className="state-label">AVAILABLE</span>
              </div>

              <div className="integrity-row">
                <div className="integrity-icon purple">◇</div>
                <div>
                  <strong>Commit-Reveal</strong>
                  <span>Evaluation workflow implemented</span>
                </div>
                <span className="state-label">AVAILABLE</span>
              </div>

              <div className="integrity-row">
                <div className="integrity-icon amber">!</div>
                <div>
                  <strong>Network isolation</strong>
                  <span>Requires end-to-end verification</span>
                </div>
                <span className="state-label warning">REVIEW</span>
              </div>
            </article>
          </section>

          <footer className="page-footer">
            <span>
              BAYORA SHIELD{" "}
              <span className="footer-separator">/</span> AI SECURITY
              INFRASTRUCTURE
            </span>
            <span>
              HACK IN HILLS '26{" "}
              <span className="footer-separator">·</span> PROTOTYPE
            </span>
          </footer>
        </>
      ) : activePage === "Red Team" ? (
        <section className="module-placeholder red-team-workspace">
          <div className="placeholder-icon">⚔</div>

          <span className="eyebrow">ADVERSARIAL SECURITY TESTING</span>
          <h3>Red Team Evaluation</h3>

          <p>
            Execute the backend's Red Team test suite and inspect the
            actual evaluation response.
          </p>

          <button
            className="back-button run-button"
            onClick={handleRunRedTeam}
            disabled={redTeamLoading}
          >
            {redTeamLoading
              ? "Running evaluation..."
              : "▶ Run Red Team Suite"}
          </button>

          {redTeamError && (
            <div className="result-error">
              <strong>Evaluation failed</strong>
              <pre>{redTeamError}</pre>
            </div>
          )}


          {redTeamResult !== null && (
            <div className="result-container">
              <h4>Red Team Evaluation Report</h4>

              {(() => {
                const report = redTeamResult as {
                  total_cases?: number;
                  passed?: number;
                  failed?: number;
                  pass_rate?: number;
                  audit_chain_valid?: boolean;
                  metrics?: {
                    precision?: number;
                    recall?: number;
                    accuracy?: number;
                    false_positive_rate?: number;
                  };
                  results?: Array<{
                    case_id: string;
                    expected_decision: string;
                    actual_decision: string;
                    passed: boolean;
                    reason: string;
                  }>;
                };

                const metrics = report.metrics;

                return (
                  <>
                    <div className="report-summary">
                      <div className="report-card">
                        <span>Total Test Cases</span>
                        <strong>{report.total_cases ?? "—"}</strong>
                      </div>

                      <div className="report-card">
                        <span>Passed</span>
                        <strong className="report-success">
                          {report.passed ?? "—"}
                        </strong>
                      </div>

                      <div className="report-card">
                        <span>Failed</span>
                        <strong className="report-failure">
                          {report.failed ?? "—"}
                        </strong>
                      </div>

                      <div className="report-card">
                        <span>Pass Rate</span>
                        <strong>
                          {report.pass_rate != null
                            ? `${report.pass_rate}%`
                            : "—"}
                        </strong>
                      </div>
                    </div>

                    <h4 className="report-section-title">
                      Security Metrics
                    </h4>

                    <div className="report-metrics">
                      <div>
                        <span>Precision</span>
                        <strong>
                          {metrics?.precision != null
                            ? `${(metrics.precision * 100).toFixed(1)}%`
                            : "—"}
                        </strong>
                      </div>

                      <div>
                        <span>Recall</span>
                        <strong>
                          {metrics?.recall != null
                            ? `${(metrics.recall * 100).toFixed(1)}%`
                            : "—"}
                        </strong>
                      </div>

                      <div>
                        <span>Accuracy</span>
                        <strong>
                          {metrics?.accuracy != null
                            ? `${(metrics.accuracy * 100).toFixed(1)}%`
                            : "—"}
                        </strong>
                      </div>

                      <div>
                        <span>False Positive Rate</span>
                        <strong>
                          {metrics?.false_positive_rate != null
                            ? `${(metrics.false_positive_rate * 100).toFixed(1)}%`
                            : "—"}
                        </strong>
                      </div>
                    </div>

                    <div className="audit-status">
                      <span
                        className={
                          report.audit_chain_valid
                            ? "status-dot status-dot-success"
                            : "status-dot status-dot-failure"
                        }
                      />
                      <span>
                        Audit Chain:{" "}
                        <strong>
                          {report.audit_chain_valid === true
                            ? "Verified"
                            : report.audit_chain_valid === false
                              ? "Verification Failed"
                              : "Not Reported"}
                        </strong>
                      </span>
                    </div>

                    <h4 className="report-section-title">
                      Test Case Explorer
                    </h4>

                    <div className="report-table-wrapper">
                      <table className="report-table">
                        <thead>
                          <tr>
                            <th>Test Case</th>
                            <th>Expected</th>
                            <th>Actual</th>
                            <th>Status</th>
                            <th>Reason</th>
                          </tr>
                        </thead>

                        <tbody>
                          {(report.results ?? []).map((testCase) => (
                            <tr key={testCase.case_id}>
                              <td>{testCase.case_id}</td>
                              <td>
                                <span className="decision-badge">
                                  {testCase.expected_decision}
                                </span>
                              </td>
                              <td>
                                <span className="decision-badge">
                                  {testCase.actual_decision}
                                </span>
                              </td>
                              <td>
                                <span
                                  className={
                                    testCase.passed
                                      ? "case-status case-status-pass"
                                      : "case-status case-status-fail"
                                  }
                                >
                                  {testCase.passed ? "PASS" : "FAIL"}
                                </span>
                              </td>
                              <td className="reason-cell">
                                {testCase.reason}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                    <p className="report-disclaimer">
                      Results reflect this evaluation suite only. They do not
                      establish that the system is secure against every attack.
                    </p>
                  </>
                );
              })()}
            </div>
          )}


          <button
            className="back-button"
            onClick={() => setActivePage("Overview")}
          >
            ← Return to overview
          </button>
        </section>
      ) : activePage === "Blue Team" ? (
        <section className="module-placeholder blue-team-workspace">
          <div className="placeholder-icon">⬡</div>

          <span className="eyebrow">DEFENSIVE SECURITY TESTING</span>
          <h3>Blue Team Evaluation</h3>

          <p>
            Execute the backend's Blue Team test suite and inspect
            its evaluation results.
          </p>

          <button
            className="back-button run-button"
            onClick={handleRunBlueTeam}
            disabled={blueTeamLoading}
          >
            {blueTeamLoading
              ? "Running evaluation..."
              : "▶ Run Blue Team Suite"}
          </button>

          {blueTeamError && (
            <div className="result-error">
              <strong>Evaluation failed</strong>
              <pre>{blueTeamError}</pre>
            </div>
          )}

          {blueTeamResult !== null && (
            <div className="result-container">
              <h4>Blue Team Evaluation Report</h4>

              {(() => {
                const report = blueTeamResult as {
                  total_cases?: number;
                  passed?: number;
                  failed?: number;
                  pass_rate?: number;
                  audit_chain_valid?: boolean;
                  metrics?: {
                    precision?: number;
                    recall?: number;
                    accuracy?: number;
                    false_positive_rate?: number;
                  };
                  results?: Array<{
                    case_id: string;
                    expected_decision: string;
                    actual_decision: string;
                    passed: boolean;
                    reason: string;
                  }>;
                };

                const metrics = report.metrics;

                return (
                  <>
                    <div className="report-summary">
                      <div className="report-card">
                        <span>Total Test Cases</span>
                        <strong>{report.total_cases ?? "—"}</strong>
                      </div>

                      <div className="report-card">
                        <span>Passed</span>
                        <strong className="report-success">
                          {report.passed ?? "—"}
                        </strong>
                      </div>

                      <div className="report-card">
                        <span>Failed</span>
                        <strong className="report-failure">
                          {report.failed ?? "—"}
                        </strong>
                      </div>

                      <div className="report-card">
                        <span>Pass Rate</span>
                        <strong>
                          {report.pass_rate != null
                            ? `${report.pass_rate}%`
                            : "—"}
                        </strong>
                      </div>
                    </div>

                    <h4 className="report-section-title">
                      Security Metrics
                    </h4>

                    <div className="report-metrics">
                      <div>
                        <span>Precision</span>
                        <strong>
                          {metrics?.precision != null
                            ? `${(metrics.precision * 100).toFixed(1)}%`
                            : "—"}
                        </strong>
                      </div>

                      <div>
                        <span>Recall</span>
                        <strong>
                          {metrics?.recall != null
                            ? `${(metrics.recall * 100).toFixed(1)}%`
                            : "—"}
                        </strong>
                      </div>

                      <div>
                        <span>Accuracy</span>
                        <strong>
                          {metrics?.accuracy != null
                            ? `${(metrics.accuracy * 100).toFixed(1)}%`
                            : "—"}
                        </strong>
                      </div>

                      <div>
                        <span>False Positive Rate</span>
                        <strong>
                          {metrics?.false_positive_rate != null
                            ? `${(
                                metrics.false_positive_rate * 100
                              ).toFixed(1)}%`
                            : "—"}
                        </strong>
                      </div>
                    </div>

                    <div className="audit-status">
                      <span
                        className={
                          report.audit_chain_valid === true
                            ? "status-dot status-dot-success"
                            : report.audit_chain_valid === false
                              ? "status-dot status-dot-failure"
                              : "status-dot muted"
                        }
                      />

                      <span>
                        Audit Chain:{" "}
                        <strong>
                          {report.audit_chain_valid === true
                            ? "Verified"
                            : report.audit_chain_valid === false
                              ? "Verification Failed"
                              : "Not Reported"}
                        </strong>
                      </span>
                    </div>

                    <h4 className="report-section-title">
                      Test Case Explorer
                    </h4>

                    <div className="report-table-wrapper">
                      <table className="report-table">
                        <thead>
                          <tr>
                            <th>Test Case</th>
                            <th>Expected</th>
                            <th>Actual</th>
                            <th>Status</th>
                            <th>Reason</th>
                          </tr>
                        </thead>

                        <tbody>
                          {(report.results ?? []).map((testCase) => (
                            <tr key={testCase.case_id}>
                              <td>{testCase.case_id}</td>

                              <td>
                                <span className="decision-badge">
                                  {testCase.expected_decision}
                                </span>
                              </td>

                              <td>
                                <span className="decision-badge">
                                  {testCase.actual_decision}
                                </span>
                              </td>

                              <td>
                                <span
                                  className={
                                    testCase.passed
                                      ? "case-status case-status-pass"
                                      : "case-status case-status-fail"
                                  }
                                >
                                  {testCase.passed ? "PASS" : "FAIL"}
                                </span>
                              </td>

                              <td className="reason-cell">
                                {testCase.reason}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                    <p className="report-disclaimer">
                      Results reflect this evaluation suite only.
                      They do not establish protection against every
                      possible attack.
                    </p>
                  </>
                );
              })()}
            </div>
          )}

          <button
            className="back-button"
            onClick={() => setActivePage("Overview")}
          >
            ← Return to overview
          </button>
        </section>
      ) : (
        <section className="module-placeholder">
          <div className="placeholder-icon">
            {navigation.find((item) => item.name === activePage)?.icon}
          </div>

          <span className="eyebrow">BAYORA SHIELD MODULE</span>
          <h3>{activePage}</h3>

          <p>
            Create a payload commitment, run a blind security evaluation,
            and verify the revealed payload against the original commitment.
          </p>

          {activePage === "Audit Explorer" ? (
            <section className="module-placeholder">
              <div className="placeholder-icon">🔍</div>
              <span className="eyebrow">BAYORA SHIELD SECURITY</span>
              <h3>Audit Explorer</h3>
              <p>
                Inspect security events, review recorded decisions, and verify
                the integrity of the audit chain.
              </p>

              <div className="result-container">
                <h4>Audit Log</h4>

                <button
                  className="back-button run-button"
                  onClick={handleLoadAuditEvents}
                  disabled={auditLoading}
                >
                  {auditLoading ? "Loading..." : "Load Audit Events"}
                </button>

                <button
                  className="back-button"
                  onClick={handleVerifyAuditChain}
                  disabled={auditLoading}
                >
                  {auditLoading ? "Verifying..." : "Verify Audit Chain"}
                </button>

                {auditError && (
                  <p role="alert" className="error-message">
                    {auditError}
                  </p>
                )}

                <p>Total recorded events: {auditTotal}</p>

                {auditEvents.map((event) => (
                  <article className="audit-event" key={event.event_id}>
                    <h4>
                      Event #{event.sequence} — {event.decision}
                    </h4>
                    <p>{event.reason}</p>
                    <small>{new Date(event.timestamp).toLocaleString()}</small>
                    <details>
                      <summary>View integrity details</summary>
                      <p>Event ID: {event.event_id}</p>
                      <p>Previous hash: {event.previous_hash}</p>
                      <p>Event hash: {event.event_hash}</p>
                    </details>
                  </article>
                ))}

                {auditVerification !== null && (
                  <div>
                    <h4>Audit Chain Verification Result</h4>
                    <pre>
                      {JSON.stringify(auditVerification, null, 2)}
                    </pre>
                  </div>
                )}
              </div>

              <button
                className="back-button"
                onClick={() => setActivePage("Overview")}
              >
                ← Return to overview
              </button>
            </section>
          ) : activePage === "Commit-Reveal" ? (
            <div className="result-container">
              <h4>Commit-Reveal Workflow</h4>

              <label htmlFor="commit-payload">Payload to evaluate</label>
              <textarea
                id="commit-payload"
                value={commitPayload}
                onChange={(event) => setCommitPayload(event.target.value)}
                placeholder="Enter a test payload..."
                rows={4}
                maxLength={10000}
                disabled={commitLoading || commitResult !== null}
              />

              <button
                className="back-button run-button"
                onClick={handleCreateCommitment}
                disabled={commitLoading || !commitPayload.trim() || commitResult !== null}
              >
                {commitLoading ? "Processing..." : "1. Create Commitment"}
              </button>

              {commitResult && (
                <>
                  <h4>Commitment Created</h4>
                  <p><strong>Commitment ID:</strong> {commitResult.commitment_id}</p>
                  <p><strong>Commitment Hash:</strong></p>
                  <code>{commitResult.commitment_hash}</code>

                  <button
                    className="back-button run-button"
                    onClick={handleRunBlindEvaluation}
                    disabled={commitLoading || blindResult !== null}
                  >
                    2. Run Blind Evaluation
                  </button>
                </>
              )}

              {blindResult && (
                <>
                  <h4>Blind Evaluation</h4>
                  <p><strong>Status:</strong> {blindResult.status}</p>
                  <p><strong>Decision:</strong> {blindResult.decision}</p>

                  <button
                    className="back-button run-button"
                    onClick={handleRevealEvaluation}
                    disabled={commitLoading || revealResult !== null}
                  >
                    3. Verify Reveal
                  </button>
                </>
              )}

              {revealResult && (
                <>
                  <h4>Final Verification</h4>
                  <p><strong>Decision:</strong> {revealResult.decision}</p>
                  <p><strong>Reason:</strong> {revealResult.reason}</p>
                  <p>
                    <strong>Commitment valid:</strong>{" "}
                    {revealResult.commitment_valid ? "Yes" : "No"}
                  </p>
                  <p>
                    <strong>Evaluation completed:</strong>{" "}
                    {revealResult.evaluation_passed ? "Yes" : "No"}
                  </p>
                </>
              )}

              {commitError && (
                <div className="result-error">
                  <strong>Workflow error</strong>
                  <pre>{commitError}</pre>
                </div>
              )}
            </div>
          ) : (
            <div className="placeholder-status">
              <span className="status-dot muted" />
              Backend integration pending
            </div>
          )}

          <button
            className="back-button"
            onClick={() => setActivePage("Overview")}
          >
            ← Return to overview
          </button>
        </section>
      )}
    </div>
  </main>
</div>

);
}

export default App;
