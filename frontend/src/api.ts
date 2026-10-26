const API_BASE_URL = "http://localhost:8001";

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
