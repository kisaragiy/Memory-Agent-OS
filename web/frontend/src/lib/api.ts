const API_BASE =
  (typeof import.meta !== 'undefined' &&
    (import.meta as { env?: { VITE_API_BASE?: string } }).env?.VITE_API_BASE) ||
  '';

export interface MemorySnapshot {
  agent_id?: string;
  memory?: MemoryPayload;
}

export interface MemoryPayload {
  facts?: MemoryFact[];
  conversation?: ConversationTurn[];
  episodes?: MemoryEpisode[];
  episode_count?: number;
  project?: Record<string, unknown>;
  narrative_schema?: Record<string, unknown>;
  world_state?: Record<string, unknown>;
}

export interface MemoryFact {
  id?: string;
  content: string;
  importance?: number;
  access_count?: number;
  created_at?: string;
  tags?: string[];
}

export interface ConversationTurn {
  role: string;
  content: string;
  timestamp?: string;
  created_at?: string;
}

export interface MemoryEpisode {
  id?: string;
  summary?: string;
  content?: string;
  importance?: number;
  timestamp?: string;
}

export interface StreamStep {
  step: string;
  data: Record<string, unknown>;
  timestamp?: number;
}

export interface TraceStep {
  step: string;
  timestamp?: string | number;
  data?: Record<string, unknown>;
}

export interface ExecutionGraphData {
  nodes: { id: string; name: string }[];
  edges: { from: string; to: string }[];
}

export type ControlMode = 'user' | 'developer' | 'debug';

async function parseError(res: Response): Promise<string> {
  try {
    const j = await res.json();
    const d = j.detail;
    if (typeof d === 'string') return d;
    if (d?.message) return d.message;
    if (d?.error) return d.error;
    return JSON.stringify(d);
  } catch {
    return (await res.text()) || res.statusText;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers || {}),
    },
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json() as Promise<T>;
}

export function getApiBase(): string {
  return API_BASE;
}

export async function fetchHealth(): Promise<Record<string, unknown>> {
  return request('/api/health');
}

export async function getControl(sessionId: string): Promise<Record<string, unknown>> {
  return request(`/api/control?session_id=${encodeURIComponent(sessionId)}`);
}

export async function setControl(
  sessionId: string,
  patch: { mode?: ControlMode; trace_enabled?: boolean; demo?: boolean }
): Promise<Record<string, unknown>> {
  return request('/api/control', {
    method: 'POST',
    body: JSON.stringify({ session_id: sessionId, ...patch }),
  });
}

export async function fetchMemory(
  agentId?: string,
  mode?: ControlMode
): Promise<MemorySnapshot> {
  const params = new URLSearchParams();
  if (agentId) params.set('agent_id', agentId);
  if (mode) params.set('mode', mode);
  const q = params.toString() ? `?${params}` : '';
  return request(`/api/memory${q}`);
}

export interface MemoryMutationIntent {
  op?: string;
  target?: string;
  action?: string;
  fact?: string;
  record_id?: string;
  kind?: string;
  snapshot_id?: string;
  reason?: string;
  inject_test?: boolean;
}

export async function rememberFact(
  fact: string,
  sessionId?: string
): Promise<{ id: string; content: string; agent_id: string; trace_id?: string }> {
  return request('/api/memory/remember', {
    method: 'POST',
    body: JSON.stringify({ fact, session_id: sessionId }),
  });
}

export async function mutateMemory(
  intent: MemoryMutationIntent,
  sessionId?: string
): Promise<Record<string, unknown>> {
  return request('/api/memory/mutate', {
    method: 'POST',
    body: JSON.stringify({ session_id: sessionId, ...intent }),
  });
}

export async function listMemoryMutations(
  sessionId: string
): Promise<{ mutations: unknown[] }> {
  return request(
    `/api/memory/mutations?agent_id=${encodeURIComponent(sessionId)}&mode=developer`
  );
}

export async function createMemorySnapshot(
  sessionId: string
): Promise<Record<string, unknown>> {
  return request(
    `/api/memory/snapshot?agent_id=${encodeURIComponent(sessionId)}&mode=developer`,
    { method: 'POST', body: '{}' }
  );
}

export async function listMemorySnapshots(
  sessionId: string
): Promise<{ snapshots: string[] }> {
  return request(
    `/api/memory/snapshots?agent_id=${encodeURIComponent(sessionId)}&mode=developer`
  );
}

export interface RunOptions {
  mode?: ControlMode;
  developer?: boolean;
  userConfirmed?: boolean;
  demo?: boolean;
  autonomousSession?: boolean;
  maxAutonomousSteps?: number;
}

export interface RunEnvelope {
  mode: string;
  status: string;
  display: string;
  session_id: string;
  result?: unknown;
  trace?: TraceStep[];
  trace_id?: string;
}

export async function runAgent(
  input: string,
  sessionId?: string,
  options?: RunOptions
): Promise<RunEnvelope> {
  return request('/api/run', {
    method: 'POST',
    body: JSON.stringify({
      input,
      session_id: sessionId,
      mode: options?.mode,
      developer: options?.developer ?? false,
      user_confirmed: options?.userConfirmed ?? false,
      demo: options?.demo ?? false,
      autonomous_session: options?.autonomousSession ?? false,
      max_autonomous_steps: options?.maxAutonomousSteps ?? 6,
    }),
  });
}

export function desktopStreamUrl(intervalMs = 1200): string {
  return `${API_BASE}/api/desktop/stream?interval_ms=${intervalMs}`;
}

export function desktopScreenshotUrl(): string {
  return `${API_BASE}/api/desktop/screenshot`;
}

export async function fetchTools(
  agentId?: string,
  mode?: ControlMode
): Promise<{ tools: string[] | { name: string }[] }> {
  const params = new URLSearchParams();
  if (agentId) params.set('agent_id', agentId);
  if (mode) params.set('mode', mode);
  const q = params.toString() ? `?${params}` : '';
  return request(`/api/tools${q}`);
}

export async function fetchTrace(
  sessionId: string,
  mode: ControlMode = 'developer'
): Promise<{ trace: TraceStep[]; graph: ExecutionGraphData }> {
  return request(
    `/api/trace/${encodeURIComponent(sessionId)}?mode=${encodeURIComponent(mode)}`
  );
}

export async function fetchReplay(
  traceId: string,
  mode: ControlMode = 'developer'
): Promise<{ trace_id: string; steps: TraceStep[] }> {
  return request(
    `/api/replay/${encodeURIComponent(traceId)}?mode=${encodeURIComponent(mode)}`
  );
}

export async function* streamAgent(
  input: string,
  sessionId?: string,
  options?: RunOptions
): AsyncGenerator<StreamStep> {
  const res = await fetch(`${API_BASE}/api/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      input,
      session_id: sessionId,
      mode: options?.mode,
      demo: options?.demo ?? false,
      autonomous_session: options?.autonomousSession ?? false,
      max_autonomous_steps: options?.maxAutonomousSteps ?? 6,
      user_confirmed: options?.userConfirmed ?? true,
    }),
  });
  if (!res.ok || !res.body) throw new Error(await parseError(res));
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';
    for (const line of lines) {
      if (!line.trim()) continue;
      yield JSON.parse(line) as StreamStep;
    }
  }
  if (buffer.trim()) yield JSON.parse(buffer) as StreamStep;
}

export function extractDisplayFromStream(
  steps: StreamStep[],
  finalResult: unknown,
  isUserMode: boolean
): string {
  for (const s of steps) {
    if (s.step === 'display' && typeof s.data?.text === 'string') {
      return s.data.text as string;
    }
    if (s.step === 'status' && isUserMode && typeof s.data?.label === 'string') {
      /* keep scanning for display */
    }
  }
  if (typeof finalResult === 'string') return finalResult;
  if (finalResult && typeof finalResult === 'object') {
    const r = finalResult as Record<string, unknown>;
    if (typeof r.display === 'string') return r.display;
    if (typeof r.result === 'string') return r.result;
  }
  return isUserMode ? '已完成。' : JSON.stringify(finalResult, null, 2);
}
