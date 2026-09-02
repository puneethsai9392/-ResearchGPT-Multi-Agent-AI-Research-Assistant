// ResearchGPT Netlify Frontend Application State
const state = {
  apiBaseUrl: localStorage.getItem('RESEARCHGPT_API_URL') || (window.location.origin.includes('netlify.app') ? '/api' : 'http://localhost:8000'),
  activeSessionId: null,
  activeReportText: '',
  isResearching: false
};

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
  initApiUrl();
  checkBackendHealth();
  fetchSources();
  fetchHistory();
});

// Setup API Base URL
function initApiUrl() {
  const input = document.getElementById('api-url-input');
  if (input) {
    input.value = state.apiBaseUrl === '/api' ? '' : state.apiBaseUrl;
  }
}

function getApiEndpoint(path) {
  let base = state.apiBaseUrl.replace(/\/$/, '');
  if (!path.startsWith('/')) path = '/' + path;
  return `${base}${path}`;
}

// Health Check
async function checkBackendHealth() {
  const statusPill = document.getElementById('backend-status');
  const statusText = document.getElementById('status-text');

  statusPill.className = 'status-pill status-connecting';
  statusText.textContent = 'Checking Backend...';

  try {
    const res = await fetch(getApiEndpoint('/health'), { method: 'GET' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    
    statusPill.className = 'status-pill status-online';
    statusText.textContent = `Online (${data.vector_store_chunks} Chunks)`;
    
    const badge = document.getElementById('vector-chunk-badge');
    if (badge) badge.textContent = data.vector_store_chunks || 0;
  } catch (err) {
    console.warn('Backend Health Check Failed:', err);
    statusPill.className = 'status-pill status-offline';
    statusText.textContent = 'Offline (Click to Config)';
  }
}

// Modal Config Functions
function openConfigModal() {
  document.getElementById('config-modal').classList.remove('hidden');
}

function closeConfigModal() {
  document.getElementById('config-modal').classList.add('hidden');
}

async function testConnection() {
  const inputVal = document.getElementById('api-url-input').value.trim();
  const pingResult = document.getElementById('modal-ping-result');
  pingResult.textContent = 'Testing connection...';
  
  const testUrl = (inputVal || 'http://localhost:8000').replace(/\/$/, '') + '/health';
  try {
    const res = await fetch(testUrl);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    pingResult.style.color = '#34d399';
    pingResult.textContent = `Connected successfully! Vector Store: ${data.vector_store_chunks} chunks.`;
  } catch (err) {
    pingResult.style.color = '#f87171';
    pingResult.textContent = `Failed to connect: ${err.message}. Make sure backend server is running.`;
  }
}

function saveConfigModal() {
  const inputVal = document.getElementById('api-url-input').value.trim();
  state.apiBaseUrl = inputVal || 'http://localhost:8000';
  localStorage.setItem('RESEARCHGPT_API_URL', state.apiBaseUrl);
  closeConfigModal();
  checkBackendHealth();
  fetchSources();
  fetchHistory();
}

// Navigation Tabs
function switchTab(tabId) {
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));

  const targetTab = document.getElementById(tabId);
  const targetNav = document.querySelector(`[data-tab="${tabId}"]`);

  if (targetTab) targetTab.classList.add('active');
  if (targetNav) targetNav.classList.add('active');

  if (tabId === 'tab-knowledge') fetchSources();
  if (tabId === 'tab-history') fetchHistory();
}

function setQuery(text) {
  document.getElementById('query-input').value = text;
}

// Handle Research Submission
async function handleResearchSubmit(event) {
  event.preventDefault();
  const queryInput = document.getElementById('query-input');
  const query = queryInput.value.trim();
  if (!query) return;

  const submitBtn = document.getElementById('submit-btn');
  const progressContainer = document.getElementById('progress-container');
  const reportContainer = document.getElementById('report-container');
  const logConsole = document.getElementById('log-console');

  // UI Reset
  state.isResearching = true;
  submitBtn.disabled = true;
  submitBtn.innerHTML = '<i class="fa-solid fa-spinner spin"></i> Processing...';
  
  progressContainer.classList.remove('hidden');
  reportContainer.classList.add('hidden');
  logConsole.innerHTML = '';

  addLog('system', 'Launching multi-agent LangGraph workflow...');
  activateStep('step-planner');

  try {
    // Simulated step animation timeline while waiting for backend execution
    const stepTimer1 = setTimeout(() => {
      activateStep('step-search');
      addLog('log-entry', 'Web Search & RAG Vector Search agents retrieving evidence...');
    }, 1200);

    const stepTimer2 = setTimeout(() => {
      activateStep('step-aggregator');
      addLog('log-entry', 'Evidence Aggregator deduplicating & structuring search chunks...');
    }, 3000);

    const stepTimer3 = setTimeout(() => {
      activateStep('step-critic');
      addLog('log-entry', 'Critic Agent auditing factual consistency & citations...');
    }, 4500);

    const response = await fetch(getApiEndpoint('/chat'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: query })
    });

    clearTimeout(stepTimer1);
    clearTimeout(stepTimer2);
    clearTimeout(stepTimer3);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Server returned error ${response.status}`);
    }

    const data = await response.json();
    
    activateStep('step-writer');
    addLog('system', 'Writer Agent successfully generated Markdown report.');

    // Save session info
    state.activeSessionId = data.session_id;
    state.activeReportText = data.final_report || '';

    // Render report
    renderReport(data, query);

  } catch (err) {
    console.error('Research task failed:', err);
    addLog('error', `Error executing research task: ${err.message}`);
    document.getElementById('progress-status-badge').textContent = 'Failed';
    document.getElementById('progress-status-badge').style.background = 'rgba(239, 68, 68, 0.2)';
    document.getElementById('progress-status-badge').style.color = '#f87171';
  } finally {
    state.isResearching = false;
    submitBtn.disabled = false;
    submitBtn.innerHTML = '<i class="fa-solid fa-paper-plane"></i> Launch Research';
  }
}

function activateStep(stepId) {
  document.querySelectorAll('.step-item').forEach(el => el.classList.remove('active'));
  const step = document.getElementById(stepId);
  if (step) step.classList.add('active');
}

function addLog(type, message) {
  const consoleEl = document.getElementById('log-console');
  const entry = document.createElement('div');
  entry.className = `log-entry ${type}`;
  entry.innerHTML = `<span style="opacity:0.6">[${new Date().toLocaleTimeString()}]</span> ${message}`;
  consoleEl.appendChild(entry);
  consoleEl.scrollTop = consoleEl.scrollHeight;
}

// Render Research Report
function renderReport(data, query) {
  const reportContainer = document.getElementById('report-container');
  const titleEl = document.getElementById('report-query-title');
  const metaEl = document.getElementById('report-meta');
  const bodyEl = document.getElementById('report-body');
  const criticBanner = document.getElementById('critic-banner');

  titleEl.textContent = query;
  metaEl.textContent = `Session ID: ${data.session_id} | Agents: Planner, Search, RAG, Critic, Writer`;

  if (data.critic_review) {
    criticBanner.classList.remove('hidden');
    document.getElementById('critic-details').textContent = data.critic_review.comments || 'Audit completed: Passed accuracy verification.';
  } else {
    criticBanner.classList.add('hidden');
  }

  bodyEl.innerHTML = parseMarkdown(data.final_report || 'No report generated.');
  reportContainer.classList.remove('hidden');
  reportContainer.scrollIntoView({ behavior: 'smooth' });
}

// Basic Markdown Parser
function parseMarkdown(md) {
  if (!md) return '';
  let html = md
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    .replace(/\*\*(.* animate?)\*\*/gim, '<strong>$1</strong>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/^\s*-\s+(.*$)/gim, '<li>$1</li>')
    .replace(/\n\n/g, '</p><p>');

  html = html.replace(/(<li>.*<\/li>)/g, '<ul>$1</ul>');
  return `<p>${html}</p>`;
}

// Rating & Feedback
async function rateSession(rating) {
  if (!state.activeSessionId) return;

  const stars = document.querySelectorAll('.star-rating i');
  stars.forEach((star, index) => {
    if (index < rating) {
      star.className = 'fa-solid fa-star';
      star.style.color = '#f59e0b';
    } else {
      star.className = 'fa-regular fa-star';
      star.style.color = '';
    }
  });

  try {
    await fetch(getApiEndpoint('/feedback'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: state.activeSessionId, rating: rating })
    });
    document.getElementById('feedback-msg').textContent = 'Thank you for your rating!';
  } catch (e) {
    console.error('Feedback failed:', e);
  }
}

// Copy & Download
function copyReport() {
  if (!state.activeReportText) return;
  navigator.clipboard.writeText(state.activeReportText);
  alert('Report copied to clipboard!');
}

function downloadReport() {
  if (!state.activeReportText) return;
  const blob = new Blob([state.activeReportText], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `Research_Report_${Date.now()}.md`;
  a.click();
  URL.revokeObjectURL(url);
}

// Document Upload Functions
function handleDragOver(e) { e.preventDefault(); e.target.classList.add('dragover'); }
function handleDragLeave(e) { e.preventDefault(); e.target.classList.remove('dragover'); }
function handleFileDrop(e) {
  e.preventDefault();
  if (e.dataTransfer.files.length) uploadFile(e.dataTransfer.files[0]);
}
function uploadSelectedFile(e) {
  if (e.target.files.length) uploadFile(e.target.files[0]);
}

async function uploadFile(file) {
  const statusEl = document.getElementById('upload-status');
  statusEl.classList.remove('hidden');
  statusEl.innerHTML = `<i class="fa-solid fa-spinner spin"></i> Uploading & embedding "${file.name}"...`;

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await fetch(getApiEndpoint('/upload'), {
      method: 'POST',
      body: formData
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    
    statusEl.innerHTML = `<i class="fa-solid fa-check-circle text-success"></i> ${data.message}`;
    fetchSources();
    checkBackendHealth();
  } catch (err) {
    statusEl.innerHTML = `<i class="fa-solid fa-exclamation-triangle text-danger"></i> Upload failed: ${err.message}`;
  }
}

// Fetch Ingested Sources
async function fetchSources() {
  const tbody = document.getElementById('sources-table-body');
  try {
    const res = await fetch(getApiEndpoint('/sources'));
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    if (!data.sources || data.sources.length === 0) {
      tbody.innerHTML = `<tr><td colspan="3" class="text-center text-muted">No documents uploaded yet.</td></tr>`;
      return;
    }

    tbody.innerHTML = data.sources.map(src => `
      <tr>
        <td><i class="fa-solid fa-file-lines" style="color:var(--primary); margin-right:8px;"></i> ${src}</td>
        <td><span class="badge" style="background:rgba(16,185,129,0.15); color:#34d399;">Indexed</span></td>
        <td>ChromaDB Vector Store</td>
      </tr>
    `).join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="3" class="text-center text-muted">Backend offline or unable to load sources.</td></tr>`;
  }
}

// Fetch Session History
async function fetchHistory() {
  const container = document.getElementById('history-list');
  try {
    const res = await fetch(getApiEndpoint('/history'));
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    if (!data.sessions || data.sessions.length === 0) {
      container.innerHTML = `<div class="text-center text-muted pad-v">No research history sessions recorded yet.</div>`;
      return;
    }

    container.innerHTML = data.sessions.map(sess => `
      <div class="card" style="margin-bottom:1rem; padding:1.2rem;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <h3 style="font-size:1.05rem;">${sess.query || 'Research Session'}</h3>
          <span style="font-size:0.75rem; color:var(--text-dim);">${sess.created_at || ''}</span>
        </div>
        <p style="font-size:0.85rem; color:var(--text-muted); margin-top:0.4rem;">Session ID: ${sess.session_id}</p>
      </div>
    `).join('');
  } catch (err) {
    container.innerHTML = `<div class="text-center text-muted pad-v">Unable to fetch history (Backend offline).</div>`;
  }
}

async function clearAllHistory() {
  if (!confirm('Are you sure you want to clear all research history?')) return;
  try {
    await fetch(getApiEndpoint('/history'), { method: 'DELETE' });
    fetchHistory();
  } catch (err) {
    alert('Failed to clear history: ' + err.message);
  }
}
