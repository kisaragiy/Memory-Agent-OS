import React, { useState, useEffect, useCallback } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';

const API = '';

function App() {
  const [input, setInput] = useState('');
  const [output, setOutput] = useState('');
  const [trace, setTrace] = useState([]);
  const [memory, setMemory] = useState(null);
  const [rememberFact, setRememberFact] = useState('');
  const [tools, setTools] = useState([]);
  const [sessionId] = useState(() => {
    const key = 'agentos-session';
    let id = localStorage.getItem(key);
    if (!id) {
      id = 'web-' + Math.random().toString(36).slice(2, 10);
      localStorage.setItem(key, id);
    }
    return id;
  });
  const [health, setHealth] = useState('…');

  const loadMemory = useCallback(async () => {
    try {
      const res = await fetch(
        `${API}/api/memory?agent_id=${encodeURIComponent(sessionId)}`
      );
      const data = await res.json();
      setMemory(data.memory ?? data);
    } catch (error) {
      console.error(error);
    }
  }, [sessionId]);

  useEffect(() => {
    fetch(`${API}/api/health`)
      .then((r) => r.json())
      .then((h) => setHealth(h.status === 'ok' ? 'online' : 'degraded'))
      .catch(() => setHealth('offline'));
    loadMemory();
    fetch(`${API}/api/tools?agent_id=${encodeURIComponent(sessionId)}`)
      .then((r) => r.json())
      .then((d) => setTools(d.tools || []))
      .catch(console.error);
  }, [sessionId, loadMemory]);

  const handleRun = async () => {
    try {
      const response = await fetch(`${API}/api/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input, session_id: sessionId }),
      });
      const result = await response.json();
      setOutput(JSON.stringify(result.result ?? result, null, 2));
      await loadMemory();
    } catch (error) {
      console.error(error);
    }
  };

  const handleRemember = async () => {
    if (!rememberFact.trim()) return;
    try {
      await fetch(`${API}/api/memory/remember`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fact: rememberFact, session_id: sessionId }),
      });
      setRememberFact('');
      await loadMemory();
    } catch (error) {
      console.error(error);
    }
  };

  const handleStream = async () => {
    try {
      const response = await fetch(`${API}/api/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input, session_id: sessionId }),
      });
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      const steps = [];
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';
        for (const line of lines) {
          if (!line.trim()) continue;
          const step = JSON.parse(line);
          steps.push(step);
        }
      }
      setTrace(steps);
      await loadMemory();
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="app">
      <aside className="sidebar">
        <header className="sidebar-header">
          <h1>Agent OS</h1>
          <span className={`badge ${health === 'online' ? 'ok' : 'err'}`}>{health}</span>
        </header>
        <section className="memory-panel">
          <h2>Memory</h2>
          <p className="agent-id">
            Agent: <code>{sessionId}</code>
          </p>
          <div className="remember-row">
            <input
              value={rememberFact}
              onChange={(e) => setRememberFact(e.target.value)}
              placeholder="Remember a fact…"
            />
            <button type="button" onClick={handleRemember}>
              Save
            </button>
            <button type="button" onClick={loadMemory}>
              ↻
            </button>
          </div>
          <pre className="memory-content">
            {memory ? JSON.stringify(memory, null, 2) : 'Loading…'}
          </pre>
        </section>
        <section className="tools-panel">
          <h2>Tools</h2>
          <pre>{JSON.stringify(tools, null, 2)}</pre>
        </section>
      </aside>
      <main className="main">
        <section className="chat-panel">
          <div className="input-area">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Enter task…"
            />
            <button type="button" onClick={handleRun}>
              Run
            </button>
            <button type="button" onClick={handleStream}>
              Stream
            </button>
          </div>
          <div className="output-area">
            <pre>{output}</pre>
          </div>
        </section>
        <section className="trace-panel">
          <h2>Trace</h2>
          <div className="trace-viewer">
            {trace.map((step, index) => (
              <div key={index} className="trace-step">
                <div className="step-name">{step.step}</div>
                <pre>{JSON.stringify(step.data, null, 2)}</pre>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}

const root = createRoot(document.getElementById('root'));
root.render(<App />);
