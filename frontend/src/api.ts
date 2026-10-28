const API_BASE_URL = "https://jessica-mon-ken-alternatives.trycloudflare.com";

export interface HealthResponse {
status: string;
service: string;
}

export async function getHealth(): Promise<HealthResponse> {
const response = await fetch(`${API_BASE_URL}/health`);

if (!response.ok) {
throw new Error(`Health check failed: HTTP ${response.status}`);
}

return response.json() as Promise<HealthResponse>;
}


export async function runRedTeamSuite(): Promise<unknown> {
const response = await fetch(
`${API_BASE_URL}/evaluation/run-red-team-suite`,
{
method: "POST",
},
);

const data: unknown = await response.json();

if (!response.ok) {
throw new Error(
`Red Team evaluation failed (HTTP ${response.status}): ${JSON.stringify(data)}`,
);
}

return data;
}


export async function runBlueTeamSuite(): Promise<unknown> {
const response = await fetch(
`${API_BASE_URL}/evaluation/run-blue-team-suite`,
{ method: "POST" },
);

const data: unknown = await response.json();

if (!response.ok) {
throw new Error(
`Blue Team evaluation failed (HTTP ${response.status}): ${JSON.stringify(data)}`,
);
}

return data;
}




export interface CommitResponse {
  commitment_id: string;
  commitment_hash: string;
  status: string;
}

export interface BlindEvaluationResponse {
  commitment_id: string;
  status: string;
  decision: string;
  nonce: string;
}

export interface RevealEvaluationResponse {
  commitment_id: string;
  commitment_hash: string;
  decision: string;
  reason: string;
  commitment_valid: boolean;
  evaluation_passed: boolean;
}

export async function createCommitment(
  payload: string,
): Promise<CommitResponse> {
  const response = await fetch(
    `${API_BASE_URL}/commit-reveal/commit`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ payload }),
    },
  );

  const data: unknown = await response.json();

  if (!response.ok) {
    throw new Error(
      `Commit failed (HTTP ${response.status}): ${JSON.stringify(data)}`,
    );
  }

  return data as CommitResponse;
}

export async function runBlindEvaluation(
  commitmentId: string,
): Promise<BlindEvaluationResponse> {
  const response = await fetch(
    `${API_BASE_URL}/commit-reveal/run-evaluation?commitment_id=${encodeURIComponent(commitmentId)}`,
    { method: "POST" },
  );

  const data: unknown = await response.json();

  if (!response.ok) {
    throw new Error(
      `Blind evaluation failed (HTTP ${response.status}): ${JSON.stringify(data)}`,
    );
  }

  return data as BlindEvaluationResponse;
}

export async function revealEvaluation(
  commitmentId: string,
  payload: string,
  nonce: string,
): Promise<RevealEvaluationResponse> {
  const response = await fetch(
    `${API_BASE_URL}/commit-reveal/evaluate`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        commitment_id: commitmentId,
        payload,
        nonce,
      }),
    },
  );

  const data: unknown = await response.json();

  if (!response.ok) {
    throw new Error(
      `Reveal verification failed (HTTP ${response.status}): ${JSON.stringify(data)}`,
    );
  }

  return data as RevealEvaluationResponse;
}





export interface AuditEvent {
  sequence: number;
  event_id: string;
  timestamp: string;
  decision: string;
  reason: string;
  previous_hash: string;
  event_hash: string;
}

export interface AuditEventsResponse {
  total: number;
  events: AuditEvent[];
}

export async function getAuditEvents(): Promise<AuditEventsResponse> {
  const response = await fetch(`${API_BASE_URL}/audit/events`);

  const data: unknown = await response.json();

  if (!response.ok) {
    throw new Error(
      `Failed to load audit events (HTTP ${response.status}): ${JSON.stringify(data)}`,
    );
  }

  return data as AuditEventsResponse;
}

export async function verifyAuditChain(): Promise<unknown> {
  const response = await fetch(`${API_BASE_URL}/audit/verify`);

  const data: unknown = await response.json();

  if (!response.ok) {
    throw new Error(
      `Audit verification failed (HTTP ${response.status}): ${JSON.stringify(data)}`,
    );
  }

  return data;
}