import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { AgentMessage, Step, Turn, applyEvent, runAgent, toolMeta } from "./agent";
import { VegaChart } from "./VegaChart";

const SCENES = [
  { title: "1 · The fund at a glance", prompt: "What was total revenue and EBITDA last quarter, by PortCo, vs budget?" },
  { title: "2 · Drill into the miss", prompt: "Which Northsea vessels drove the shortfall?" },
  { title: "3 · Why?", prompt: "Why were those vessels underutilised?" },
  { title: "4 · Connect the dots", prompt: "Are any of our aircraft lessees showing signs of credit stress, and what's our exposure?" },
  { title: "5 · What's coming?", prompt: "Summarise the key risks and capex plans in HarbourLink's latest board pack" },
  { title: "6 · Prepare for Monday", prompt: "Draft a one-page IC summary: fund performance, top 3 risks, and recommended actions." },
];

const PORTCOS = ["Northsea Shipping", "AeroLease Partners", "HarbourLink Terminals"];

function newTurn(question: string): Turn {
  return {
    // crypto.randomUUID is unavailable over plain HTTP (non-secure context)
    id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
    question,
    text: "",
    status: "Starting…",
    steps: [],
    charts: [],
    citations: [],
    suggested: [],
    done: false,
    startedAt: Date.now(),
  };
}

export default function App() {
  const [turns, setTurns] = useState<Turn[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [selected, setSelected] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [turns]);

  async function ask(question: string) {
    const q = question.trim();
    if (!q || busy) return;
    setInput("");
    setBusy(true);

    const history: AgentMessage[] = [];
    for (const t of turns) {
      if (!t.assistant) continue;
      history.push({ role: "user", content: [{ type: "text", text: t.question }] });
      history.push(t.assistant);
    }
    const messages: AgentMessage[] = [...history, { role: "user", content: [{ type: "text", text: q }] }];

    const turn = newTurn(q);
    setTurns((prev) => [...prev, turn]);
    setSelected(turn.id);
    const update = (fn: (t: Turn) => Turn) => setTurns((prev) => prev.map((t) => (t.id === turn.id ? fn(t) : t)));

    const controller = new AbortController();
    abortRef.current = controller;
    try {
      await runAgent(messages, { onEvent: (ev, data) => update((t) => applyEvent(t, ev, data)) }, controller.signal);
    } catch (err: any) {
      if (err.name !== "AbortError") update((t) => ({ ...t, error: err.message || String(err) }));
    } finally {
      update((t) => ({ ...t, done: true, status: "Done", endedAt: Date.now() }));
      setBusy(false);
      abortRef.current = null;
    }
  }

  function reset() {
    abortRef.current?.abort();
    setTurns([]);
    setSelected(null);
  }

  const traceTurn = turns.find((t) => t.id === selected) || turns[turns.length - 1];

  return (
    <div className="app">
      <header className="header">
        <div className="brand">
          <span className="logo">GTIF</span>
          <div>
            <h1>Fund Analyst</h1>
            <p>Cortex Agent over portfolio company data · Snowflake</p>
          </div>
        </div>
        <div className="chips">
          {PORTCOS.map((p) => (
            <span key={p} className="chip">
              {p}
            </span>
          ))}
        </div>
      </header>

      <div className="layout">
        <aside className="rail">
          <h2>Demo scenes</h2>
          {SCENES.map((s) => (
            <button key={s.title} className="scene" disabled={busy} onClick={() => ask(s.prompt)} title={s.prompt}>
              <strong>{s.title}</strong>
              <span>{s.prompt}</span>
            </button>
          ))}
          <button className="reset" onClick={reset}>
            New conversation
          </button>
        </aside>

        <main className="chat">
          {turns.length === 0 && (
            <div className="empty">
              <h2>Ask the fund</h2>
              <p>Ask about revenue, EBITDA, fleet utilisation, lessee credit, or anything in the PortCo board packs and reports.</p>
            </div>
          )}
          {turns.map((t) => (
            <section key={t.id} className={`turn ${t.id === traceTurn?.id ? "active" : ""}`} onClick={() => setSelected(t.id)}>
              <div className="question">{t.question}</div>
              <div className="answer">
                {!t.done && !t.text && <div className="thinking">{t.status}</div>}
                <ToolBadges steps={t.steps} />
                {t.text && <ReactMarkdown remarkPlugins={[remarkGfm]}>{t.text}</ReactMarkdown>}
                {t.charts.map((c, i) => (
                  <VegaChart key={i} spec={c} />
                ))}
                {t.citations.length > 0 && (
                  <div className="citations">
                    <span>Sources:</span>
                    {t.citations.map((c) => (
                      <details key={c.docId}>
                        <summary>{c.title}</summary>
                        <pre>{c.text}</pre>
                      </details>
                    ))}
                  </div>
                )}
                {t.error && <div className="error">{t.error}</div>}
                {t.done && t.suggested.length > 0 && turns[turns.length - 1].id === t.id && (
                  <div className="suggested">
                    {t.suggested.map((s) => (
                      <button key={s} disabled={busy} onClick={() => ask(s)}>
                        {s}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </section>
          ))}
          <div ref={endRef} />
          <form
            className="composer"
            onSubmit={(e) => {
              e.preventDefault();
              ask(input);
            }}
          >
            <input
              value={input}
              maxLength={2000}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question about the fund…"
              disabled={busy}
            />
            <button type="submit" disabled={busy || !input.trim()}>
              {busy ? "Working…" : "Ask"}
            </button>
          </form>
        </main>

        <aside className="trace">
          <h2>Under the hood</h2>
          {!traceTurn && <p className="muted">Each step the agent takes (planning, tools, SQL, documents) appears here.</p>}
          {traceTurn && <Trace turn={traceTurn} />}
        </aside>
      </div>
    </div>
  );
}

function ToolBadges({ steps }: { steps: Step[] }) {
  const kinds = Array.from(new Set(steps.map((s) => toolMeta(s.type, s.tool).kind)));
  if (kinds.length === 0) return null;
  const label: Record<string, string> = { analyst: "Analyst", search: "Search", chart: "Chart", other: "Tool" };
  return (
    <div className="badges">
      {kinds.map((k) => (
        <span key={k} className={`badge ${k}`}>
          {label[k]}
        </span>
      ))}
    </div>
  );
}

function Trace({ turn }: { turn: Turn }) {
  const elapsed = ((turn.endedAt || Date.now()) - turn.startedAt) / 1000;
  return (
    <div>
      <div className="trace-q">“{turn.question}”</div>
      <div className="trace-meta">
        {turn.steps.length} tool call(s) · {turn.done ? `${elapsed.toFixed(1)}s` : turn.status}
      </div>
      {turn.done && turn.steps.length === 0 && (
        <div className="step none">No tools called. Answered from conversation context.</div>
      )}
      <ol className="steps">
        {turn.steps.map((s, i) => {
          const meta = toolMeta(s.type, s.tool);
          const dur = s.endedAt ? `${((s.endedAt - s.startedAt) / 1000).toFixed(1)}s` : "running…";
          return (
            <li key={s.id} className={`step ${meta.kind} ${s.status}`}>
              <div className="step-head">
                <span className="step-n">{i + 1}</span>
                <span className="step-label">{meta.label}</span>
                <span className="step-dur">{dur}</span>
              </div>
              {typeof s.input.query === "string" && <div className="step-input">Query: {s.input.query}</div>}
              {s.sql && (
                <details>
                  <summary>SQL</summary>
                  <pre>{s.sql}</pre>
                </details>
              )}
              {s.summary && <div className="step-summary">{s.summary}</div>}
              {s.rows && s.rows.data.length > 0 && (
                <details>
                  <summary>Result preview</summary>
                  <div className="table-wrap">
                    <table>
                      <thead>
                        <tr>
                          {s.rows.columns.map((c) => (
                            <th key={c}>{c}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {s.rows.data.slice(0, 8).map((r, ri) => (
                          <tr key={ri}>
                            {r.map((v, vi) => (
                              <td key={vi}>{String(v ?? "")}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </details>
              )}
              {s.docs && s.docs.length > 0 && (
                <details>
                  <summary>Documents</summary>
                  <ul className="docs">
                    {Array.from(new Set(s.docs.map((d) => d.title))).map((t) => (
                      <li key={t}>{t}</li>
                    ))}
                  </ul>
                </details>
              )}
            </li>
          );
        })}
      </ol>
    </div>
  );
}
