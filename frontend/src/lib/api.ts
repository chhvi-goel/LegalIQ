export const BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api/v1';

export function getStoredToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('legaliq_token');
}

export function setStoredToken(token: string) {
  if (typeof window !== 'undefined') {
    localStorage.setItem('legaliq_token', token);
  }
}

export function removeStoredToken() {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('legaliq_token');
  }
}

export function getAuthHeaders(extraHeaders: Record<string, string> = {}): Record<string, string> {
  const token = getStoredToken();
  const headers: Record<string, string> = { ...extraHeaders };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

export async function apiFetch(
  endpoint: string,
  options: RequestInit = {}
) {
  const headers = getAuthHeaders(
    (options.headers as Record<string, string>) || {}
  );

  return fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  confidence_score?: number;
  citations?: any[];
  action_steps?: any[];
  guided_questions?: string[];
  agents_executed?: string[];
  emergency_data?: any;
  pipeline_used?: string;
  timestamp: string;
}

export async function createSession(title: string, role_mode: string = 'citizen') {
  const res = await apiFetch('/chat/sessions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, role_mode }),
  });
  return res.json();
}

export async function fetchUserSessions(role_mode?: string) {
  const endpoint = role_mode ? `/chat/sessions?role_mode=${role_mode}` : '/chat/sessions';
  const res = await apiFetch(endpoint);
  return res.json();
}

export async function fetchSessionHistory(session_id: string) {
  const res = await apiFetch(`/chat/sessions/${session_id}/history`);
  if (!res.ok) return [];
  return res.json();
}

export async function pinSession(session_id: string) {
  const res = await apiFetch(`/chat/sessions/${session_id}/pin`, { method: 'PUT' });
  return res.json();
}

export async function renameSession(session_id: string, title: string) {
  const res = await apiFetch(`/chat/sessions/${session_id}/rename`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title }),
  });
  return res.json();
}

export async function searchSessions(query: string) {
  const res = await apiFetch(`/chat/sessions/search?q=${encodeURIComponent(query)}`);
  return res.json();
}

export async function deleteSession(session_id: string) {
  const res = await apiFetch(`/chat/sessions/${session_id}`, { method: 'DELETE' });
  return res.json();
}

export async function exportSession(session_id: string, format: string = 'markdown') {
  const res = await apiFetch(`/chat/sessions/${session_id}/export?format=${format}`);
  if (format === 'json') return res.json();
  const text = await res.text();
  const blob = new Blob([text], { type: format === 'markdown' ? 'text/markdown' : 'text/plain' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `LegalIQ_Chat_Export_${session_id}.${format === 'markdown' ? 'md' : 'txt'}`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}

export async function subscribeChatStream(
  query: string,
  session_id: string | null,
  role_mode: string,
  onStage: (stage: { stage: string; message: string; pipeline?: string }) => void,
  onMetadata: (meta: any) => void,
  onToken: (chunk: string) => void,
  onDone: (data: any) => void,
  onError: (err: any) => void
) {
  try {
    const res = await fetch(`${BASE_URL}/chat/stream`, {
      method: 'POST',
      headers: getAuthHeaders({
        'Content-Type': 'application/json',
      }),
      body: JSON.stringify({
        query,
        session_id,
        role_mode,
      }),
    });

    if (!res.ok) {
      onError({
        message: `Request failed with status ${res.status}`,
      });
      return;
    }

    if (!res.body) {
      onError({
        message: 'Response body missing',
      });
      return;
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { value, done } = await reader.read();

      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      const events = buffer.split('\n\n');
      buffer = events.pop() || '';

      for (const eventStr of events) {
        if (!eventStr.trim()) continue;

        const lines = eventStr.split('\n');

        let eventType = '';
        let dataStr = '';

        for (const line of lines) {
          if (line.startsWith('event: ')) {
            eventType = line.replace('event: ', '').trim();
          } else if (line.startsWith('data: ')) {
            dataStr = line.replace('data: ', '').trim();
          }
        }

        if (dataStr) {
          try {
            const data = JSON.parse(dataStr);

            if (eventType === 'stage') {
              onStage(data);
            } else if (eventType === 'metadata') {
              onMetadata(data);
            } else if (eventType === 'token') {
              onToken(data.chunk);
            } else if (eventType === 'done') {
              onDone(data);
            } else if (eventType === 'error') {
              onError(data);
            }
          } catch (e) {
            console.error('Failed to parse SSE payload', e);
          }
        }
      }
    }
  } catch (err) {
    onError(err);
  }
}

export async function searchLegalDatabase(searchParams: any) {
  const res = await apiFetch('/research/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(searchParams),
  });
  const data = await res.json();
  return data.results || data;
}

export async function generateDraft(draftParams: any) {
  const res = await apiFetch('/research/generate-draft', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(draftParams),
  });
  return res.json();
}

export async function compareCases(input: any) {
  let queries: string[] = [];
  if (Array.isArray(input)) {
    queries = input;
  } else if (input && typeof input === 'object') {
    queries = input.case_queries || input.case_ids || [];
  }

  const res = await apiFetch('/research/compare-cases', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ case_queries: queries, case_ids: queries }),
  });
  return res.json();
}

export async function summarizeJudgment(params: any) {
  const res = await apiFetch('/research/summarize-judgment', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  return res.json();
}

export async function createResearchNote(params: any) {
  const res = await apiFetch('/research/notes', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  return res.json();
}

export async function fetchResearchNotes(notebook?: string) {
  const endpoint = notebook ? `/research/notes?notebook=${encodeURIComponent(notebook)}` : '/research/notes';
  const res = await apiFetch(endpoint);
  return res.json();
}

export async function deleteResearchNote(id: number) {
  const res = await apiFetch(`/research/notes/${id}`, { method: 'DELETE' });
  return res.json();
}

export async function createBookmark(params: any) {
  const res = await apiFetch('/research/bookmarks', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  return res.json();
}

export async function fetchBookmarks() {
  const res = await apiFetch('/research/bookmarks');
  return res.json();
}

export async function deleteBookmark(id: number) {
  const res = await apiFetch(`/research/bookmarks/${id}`, { method: 'DELETE' });
  return res.json();
}

export async function uploadDocument(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  const res = await apiFetch('/documents/upload', {
    method: 'POST',
    body: formData,
  });
  return res.json();
}

export async function queryDocument(filename: string, extracted_text: string, question: string) {
  const res = await apiFetch('/documents/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filename, extracted_text, question }),
  });
  return res.json();
}

export async function getMCPServers() {
  const res = await apiFetch('/mcp/servers');
  return res.json();
}

export async function executeMCPTool(server_name: string, tool_name: string, args: any) {
  const res = await apiFetch('/mcp/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ server_name, tool_name, arguments: args }),
  });
  return res.json();
}

export async function generatePDFReport(session_id: string, report_type: string = 'citizen_legal_advice') {
  const res = await apiFetch('/reports/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id, report_type }),
  });
  return res.json();
}

export async function downloadReportFile(reportId: number | string) {
  const res = await apiFetch(`/reports/download/${reportId}`);
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `LegalIQ_Advice_Report_${reportId}.pdf`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}

export async function loginUser(email: string, password: string) {
  const res = await apiFetch('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Login failed');
  }
  const data = await res.json();
  if (data.access_token) {
    setStoredToken(data.access_token);
  }
  return data;
}

export async function registerUser(email: string, password: string, full_name: string, role: string = 'citizen') {
  const res = await apiFetch('/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, full_name, role }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Registration failed');
  }
  const data = await res.json();
  if (data.access_token) {
    setStoredToken(data.access_token);
  }
  return data;
}

export async function fetchCurrentUserProfile() {
  const token = getStoredToken();
  if (!token) return null;
  const res = await apiFetch('/auth/me');
  if (!res.ok) {
    removeStoredToken();
    return null;
  }
  return res.json();
}
