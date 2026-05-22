/**
 * Agent OS web console — Control Layer + Presentation (user vs developer).
 */
(function () {
  const API = '';
  const MODE_KEY = 'agentos-control-mode';
  const DEMO_KEY = 'agentos-demo';

  let controlMode = localStorage.getItem(MODE_KEY) || 'user';
  let demoMode = localStorage.getItem(DEMO_KEY) === '1';

  const agentId = (() => {
    const key = 'agentos-session';
    let id = localStorage.getItem(key);
    if (!id) {
      id = 'web-' + Math.random().toString(36).slice(2, 10);
      localStorage.setItem(key, id);
    }
    return id;
  })();

  const el = (id) => document.getElementById(id);

  el('agent-id-label').textContent = agentId;

  function isUserMode() {
    return controlMode === 'user' && !demoMode;
  }

  function applyModeUI() {
    document.querySelectorAll('.mode-btn[data-mode]').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.mode === controlMode);
    });
    const demoBtn = el('btn-demo');
    if (demoBtn) demoBtn.classList.toggle('active', demoMode);
    const tracePanel = el('trace-panel');
    if (tracePanel) {
      tracePanel.classList.toggle('hidden', isUserMode());
    }
    const toolsPanel = document.querySelector('.tools-panel');
    if (toolsPanel) toolsPanel.classList.toggle('hidden', isUserMode());
  }

  async function syncControl() {
    try {
      await api('/api/control', {
        method: 'POST',
        body: JSON.stringify({
          session_id: agentId,
          mode: controlMode,
          demo: demoMode,
        }),
      });
    } catch (e) {
      console.warn('control sync', e);
    }
  }

  async function setMode(mode) {
    controlMode = mode;
    demoMode = false;
    localStorage.setItem(MODE_KEY, mode);
    localStorage.setItem(DEMO_KEY, '0');
    applyModeUI();
    await syncControl();
    loadMemory();
    loadTools();
  }

  async function toggleDemo() {
    demoMode = !demoMode;
    localStorage.setItem(DEMO_KEY, demoMode ? '1' : '0');
    if (demoMode) controlMode = 'user';
    applyModeUI();
    await syncControl();
  }

  document.querySelectorAll('.mode-btn[data-mode]').forEach((btn) => {
    btn.addEventListener('click', () => setMode(btn.dataset.mode));
  });
  el('btn-demo').addEventListener('click', toggleDemo);

  async function api(path, options) {
    const res = await fetch(API + path, {
      headers: { 'Content-Type': 'application/json', ...(options && options.headers) },
      ...options,
    });
    if (!res.ok) {
      let msg = res.statusText;
      try {
        const j = await res.json();
        msg = j.detail?.message || j.detail?.error || JSON.stringify(j.detail) || msg;
      } catch (_) {
        msg = await res.text();
      }
      throw new Error(msg);
    }
    const ct = res.headers.get('content-type') || '';
    if (ct.includes('application/json')) return res.json();
    return res.text();
  }

  function setStatus(text) {
    const s = el('status-line');
    if (s) s.textContent = text;
  }

  async function checkHealth() {
    const badge = el('health-badge');
    try {
      const h = await api('/api/health');
      badge.textContent = h.status === 'ok' ? '在线' : '异常';
      badge.className = 'badge ok';
    } catch (e) {
      badge.textContent = '离线';
      badge.className = 'badge err';
    }
  }

  function renderMemory(snapshot) {
    const box = el('memory-content');
    const mem = snapshot.memory || snapshot;
    const facts = mem.facts || [];
    const episodes = mem.episodes || [];
    const conv = mem.conversation || [];
    const epCount = mem.episode_count ?? episodes.length;

    let html = '';
    if (facts.length) {
      html += '<h3>已记住</h3><ul class="mem-list">';
      facts.forEach((f) => {
        html += `<li>${escapeHtml(f.content)}</li>`;
      });
      html += '</ul>';
    }
    if (!isUserMode() && episodes.length) {
      html += '<h3>Episodes</h3><ul class="mem-list">';
      episodes.slice(-8).reverse().forEach((ep) => {
        html += `<li>${escapeHtml(ep.summary || ep.content || '(episode)')}</li>`;
      });
      html += '</ul>';
    } else if (epCount > 0 && isUserMode()) {
      html += `<p class="muted">历史任务记录：${epCount} 条</p>`;
    }
    if (!isUserMode() && conv.length) {
      html += '<h3>Conversation</h3><ul class="mem-list">';
      conv.slice(-6).forEach((t) => {
        html += `<li><span class="role">${escapeHtml(t.role)}</span> ${escapeHtml(
          (t.content || '').slice(0, 100)
        )}</li>`;
      });
      html += '</ul>';
    }
    if (!html) html = '<p class="muted">暂无记忆</p>';
    box.innerHTML = html;
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  async function loadMemory() {
    const errEl = el('memory-error');
    errEl.classList.add('hidden');
    el('memory-content').textContent = '加载中…';
    try {
      const q = `agent_id=${encodeURIComponent(agentId)}&mode=${encodeURIComponent(controlMode)}`;
      const snap = await api(`/api/memory?${q}`);
      renderMemory(snap);
    } catch (e) {
      errEl.textContent = e.message;
      errEl.classList.remove('hidden');
      el('memory-content').textContent = '';
    }
  }

  async function loadTools() {
    if (isUserMode()) return;
    try {
      const q = `agent_id=${encodeURIComponent(agentId)}&mode=${encodeURIComponent(controlMode)}`;
      const data = await api(`/api/tools?${q}`);
      el('tools-list').textContent = JSON.stringify(data.tools, null, 2);
    } catch (e) {
      el('tools-list').textContent = String(e.message);
    }
  }

  function appendMessage(role, text) {
    const div = document.createElement('div');
    div.className = 'msg ' + role;
    div.textContent = text;
    el('messages').appendChild(div);
    el('messages').scrollTop = el('messages').scrollHeight;
    return div;
  }

  function appendTrace(step, data) {
    if (isUserMode()) return;
    const box = el('trace-viewer');
    const div = document.createElement('div');
    div.className = 'trace-step';
    div.innerHTML = `<div class="step-name">${escapeHtml(step)}</div><pre>${escapeHtml(
      JSON.stringify(data, null, 2)
    )}</pre>`;
    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
  }

  function extractReply(ev, finalResult) {
    if (ev.step === 'display' && ev.data?.text) return ev.data.text;
    if (typeof finalResult === 'string') return finalResult;
    if (finalResult?.display) return finalResult.display;
    return Presentation_extract(finalResult);
  }

  function Presentation_extract(raw) {
    if (!raw) return '';
    if (typeof raw === 'string') return raw;
    if (raw.display) return raw.display;
    if (raw.result) {
      if (typeof raw.result === 'string') return raw.result;
      if (raw.result.display) return raw.result.display;
    }
    return JSON.stringify(raw, null, 2);
  }

  async function sendChat() {
    const input = el('chat-input');
    const text = input.value.trim();
    if (!text) return;
    input.value = '';
    appendMessage('user', text);
    const pending = appendMessage('assistant', demoMode ? '演示运行中…' : '正在思考…');
    setStatus(demoMode ? '演示模式' : '正在执行任务…');
    el('trace-viewer').innerHTML = '';

    const body = {
      input: text,
      session_id: agentId,
      mode: controlMode,
      demo: demoMode,
    };

    try {
      const res = await fetch(API + '/api/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let finalResult = null;
      let lastDisplay = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';
        for (const line of lines) {
          if (!line.trim()) continue;
          const ev = JSON.parse(line);
          if (ev.step === 'status' && ev.data?.label) {
            pending.textContent = ev.data.label;
            setStatus(ev.data.label);
          }
          if (ev.step === 'display') {
            lastDisplay = ev.data?.text || ev.data?.label || lastDisplay;
            pending.textContent = lastDisplay;
          }
          appendTrace(ev.step, ev.data);
          if (ev.step === 'execution_complete') finalResult = ev.data.result;
        }
      }

      const reply = lastDisplay || extractReply({}, finalResult) || '已完成。';
      pending.textContent = reply;
      setStatus('就绪');
      await loadMemory();
    } catch (e) {
      pending.textContent = isUserMode() ? '任务未能完成，请稍后重试。' : '错误: ' + e.message;
      setStatus('就绪');
    }
  }

  el('btn-refresh-memory').addEventListener('click', loadMemory);
  el('btn-remember').addEventListener('click', async () => {
    const fact = el('remember-input').value.trim();
    if (!fact) return;
    try {
      await api('/api/memory/remember', {
        method: 'POST',
        body: JSON.stringify({ fact, session_id: agentId }),
      });
      el('remember-input').value = '';
      await loadMemory();
    } catch (e) {
      const errEl = el('memory-error');
      errEl.textContent = e.message;
      errEl.classList.remove('hidden');
    }
  });
  el('btn-send').addEventListener('click', sendChat);
  el('chat-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendChat();
    }
  });

  applyModeUI();
  syncControl();
  checkHealth();
  loadMemory();
  loadTools();
  setInterval(checkHealth, 30000);
})();
