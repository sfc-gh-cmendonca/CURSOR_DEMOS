// Client for the backend /api/chat SSE stream (Cortex Agent run events).

export type AgentContent = Record<string, unknown> & { type: string };
export type AgentMessage = { role: "user" | "assistant"; content: AgentContent[] };

export type StepStatus = "running" | "success" | "error";

export interface Step {
  id: string;
  tool: string; // agent tool name, e.g. fund_metrics, portco_documents
  type: string; // tool type, e.g. cortex_search, system_execute_sql
  input: Record<string, unknown>;
  status: StepStatus;
  startedAt: number;
  endedAt?: number;
  summary?: string;
  sql?: string;
  rows?: { columns: string[]; data: unknown[][] };
  docs?: { title: string; text: string }[];
}

export interface Citation {
  docId: string;
  title: string;
  text: string;
}

export interface Turn {
  id: string;
  question: string;
  text: string;
  status: string;
  steps: Step[];
  charts: string[];
  citations: Citation[];
  suggested: string[];
  done: boolean;
  error?: string;
  startedAt: number;
  endedAt?: number;
  assistant?: AgentMessage;
}

export interface Handlers {
  onEvent: (event: string, data: any) => void;
}

export async function runAgent(messages: AgentMessage[], handlers: Handlers, signal?: AbortSignal) {
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages }),
    signal,
  });
  if (!res.ok || !res.body) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.error || `Request failed (${res.status})`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    let idx;
    while ((idx = buffer.indexOf("\n\n")) !== -1) {
      const raw = buffer.slice(0, idx);
      buffer = buffer.slice(idx + 2);
      let event = "message";
      const dataLines: string[] = [];
      for (const line of raw.split("\n")) {
        if (line.startsWith("event:")) event = line.slice(6).trim();
        else if (line.startsWith("data:")) dataLines.push(line.slice(5).trim());
      }
      const dataStr = dataLines.join("\n");
      if (!dataStr || dataStr === "[DONE]") continue;
      try {
        handlers.onEvent(event, JSON.parse(dataStr));
      } catch {
        // ignore malformed event
      }
    }
  }
}

export const TOOL_META: Record<string, { label: string; kind: "analyst" | "search" | "chart" | "other" }> = {
  system_agentic_semantic_context: { label: "Cortex Analyst · read semantic model", kind: "analyst" },
  cortex_analyst_text_to_sql: { label: "Cortex Analyst · text-to-SQL", kind: "analyst" },
  system_execute_sql: { label: "Cortex Analyst · run SQL", kind: "analyst" },
  cortex_search: { label: "Cortex Search · PortCo documents", kind: "search" },
  data_to_chart: { label: "Chart", kind: "chart" },
};

export function toolMeta(type: string, name: string) {
  return TOOL_META[type] || { label: name, kind: "other" as const };
}

// Apply a streamed agent event to a turn (returns a new turn object).
export function applyEvent(turn: Turn, event: string, d: any): Turn {
  const t: Turn = { ...turn };
  switch (event) {
    case "response.status":
      t.status = d.message || d.status || t.status;
      break;
    case "response.text.delta":
      t.text = t.text + (d.text || "");
      break;
    case "response.tool_use": {
      if (t.steps.some((s) => s.id === d.tool_use_id)) break;
      const step: Step = {
        id: d.tool_use_id,
        tool: d.name,
        type: d.type,
        input: d.input || {},
        status: "running",
        startedAt: Date.now(),
        sql: typeof d.input?.sql === "string" ? d.input.sql : undefined,
      };
      t.steps = [...t.steps, step];
      break;
    }
    case "response.tool_result":
      t.steps = t.steps.map((s) => (s.id === d.tool_use_id ? summariseResult(s, d) : s));
      break;
    case "response.chart":
      if (d.chart_spec) t.charts = [...t.charts, d.chart_spec];
      break;
    case "response.text.annotation": {
      const a = d.annotation || {};
      if (a.doc_id && !t.citations.some((c) => c.docId === a.doc_id)) {
        t.citations = [...t.citations, { docId: a.doc_id, title: a.doc_title || a.doc_id, text: a.text || "" }];
      }
      break;
    }
    case "response.suggested_queries":
      t.suggested = (d.suggested_queries || []).map((q: any) => q.query).filter(Boolean);
      break;
    case "response":
      t.assistant = { role: "assistant", content: d.content || [] };
      break;
    case "error":
      t.error = d.message || "The agent returned an error.";
      break;
  }
  return t;
}

function summariseResult(step: Step, d: any): Step {
  const s: Step = { ...step, status: d.status === "error" ? "error" : "success", endedAt: Date.now() };
  const json = d.content?.[0]?.json || {};
  if (step.type === "system_execute_sql") {
    const rs = json.result_set;
    if (rs) {
      const columns = (rs.resultSetMetaData?.rowType || []).map((c: any) => c.name);
      s.rows = { columns, data: rs.data || [] };
      s.summary = `${(rs.data || []).length} row(s) returned`;
    }
    if (json.sql && !s.sql) s.sql = json.sql;
  } else if (step.type === "cortex_search") {
    const results = json.search_results || [];
    s.docs = results.map((r: any) => ({ title: r.doc_title || r.doc_id, text: r.text || "" }));
    const titles = Array.from(new Set(s.docs!.map((x) => x.title)));
    s.summary = `${results.length} chunk(s) from ${titles.length} document(s)`;
  } else if (step.type === "system_agentic_semantic_context") {
    s.summary = "Loaded GTIF_FUND_SV semantic model";
  } else if (step.type === "data_to_chart") {
    s.summary = "Chart generated";
  }
  if (s.status === "error") s.summary = "Tool returned an error";
  return s;
}
