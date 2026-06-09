/**
 * Deep Research Engine — Client Application
 * Handles SSE streaming, phase tracking, markdown rendering, and confidence gauge animation.
 */

/* global marked */

// ---------------------------------------------------------------------------
// DOM refs
// ---------------------------------------------------------------------------
const form         = document.getElementById('search-form');
const queryInput   = document.getElementById('query-input');
const submitBtn    = document.getElementById('submit-btn');

const phasesWrap   = document.getElementById('phases');
const phaseCards   = document.querySelectorAll('.phase-card');

const feedWrap     = document.getElementById('feed');
const feedPanel    = document.getElementById('feed-panel');

const modelsWrap   = document.getElementById('models');
const modelBadges  = document.querySelectorAll('.model-badge');

const resultWrap   = document.getElementById('result');
const gaugeLabel   = document.getElementById('gauge-label');
const gaugeCircle  = document.getElementById('gauge-progress');
const noteContent  = document.getElementById('note-content');

const timingP1     = document.getElementById('timing-p1');
const timingP2     = document.getElementById('timing-p2');
const timingP3     = document.getElementById('timing-p3');
const timingTotal  = document.getElementById('timing-total');

const errorCard    = document.getElementById('error-card');
const errorMsg     = document.getElementById('error-msg');
const retryBtn     = document.getElementById('retry-btn');


// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------
let isRunning = false;


// ---------------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------------
form.addEventListener('submit', handleSubmit);
retryBtn.addEventListener('click', resetUI);


// ---------------------------------------------------------------------------
// Submit handler
// ---------------------------------------------------------------------------
async function handleSubmit(e) {
  e.preventDefault();
  const query = queryInput.value.trim();
  if (!query || isRunning) return;

  isRunning = true;
  submitBtn.disabled = true;
  submitBtn.textContent = 'Researching…';

  // Reset UI
  hideElement(resultWrap);
  hideElement(errorCard);
  feedPanel.innerHTML = '';
  resetPhases();
  resetModels();

  showElement(phasesWrap);
  showElement(feedWrap);
  showElement(modelsWrap);

  try {
    const resp = await fetch('/research', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });

    if (!resp.ok) throw new Error(`Server error: ${resp.status}`);

    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      // SSE frames are separated by double newlines
      const frames = buffer.split('\n\n');
      buffer = frames.pop();  // last item is incomplete

      for (const frame of frames) {
        processSSE(frame);
      }
    }

    // process any remaining
    if (buffer.trim()) processSSE(buffer);

  } catch (err) {
    showError(err.message || 'Something went wrong.');
  } finally {
    isRunning = false;
    submitBtn.disabled = false;
    submitBtn.textContent = 'Research';
  }
}


// ---------------------------------------------------------------------------
// SSE processing
// ---------------------------------------------------------------------------
function processSSE(frame) {
  const lines = frame.trim().split('\n');
  let eventType = 'message';
  let dataStr = '';

  for (const line of lines) {
    if (line.startsWith('event: ')) {
      eventType = line.slice(7).trim();
    } else if (line.startsWith('data: ')) {
      dataStr += line.slice(6);
    }
  }

  if (!dataStr) return;

  let data;
  try { data = JSON.parse(dataStr); } catch { return; }

  switch (eventType) {
    case 'phase':
      handlePhase(data);
      break;
    case 'result':
      handleResult(data);
      break;
    case 'error':
      showError(data.message || 'Pipeline error.');
      break;
    case 'done':
      // stream finished
      break;
  }
}


// ---------------------------------------------------------------------------
// Phase handling
// ---------------------------------------------------------------------------
function handlePhase(data) {
  const { phase, status, label, time_s } = data;
  const card = document.querySelector(`.phase-card[data-phase="${phase}"]`);
  if (!card) return;

  if (status === 'running') {
    card.classList.remove('done');
    card.classList.add('running');
    appendFeed(`⚙️ Phase ${phase} started: ${label}`);
  } else if (status === 'done') {
    card.classList.remove('running');
    card.classList.add('done');
    const timeEl = card.querySelector('.phase-card__time');
    if (timeEl && time_s != null) timeEl.textContent = `${time_s}s`;
    appendFeed(`✅ Phase ${phase} complete: ${label} (${time_s}s)`);

    // Light up model badges after phase 1 (data gathering)
    if (phase === 1) {
      modelBadges.forEach(b => b.classList.add('active'));
    }
  }
}


// ---------------------------------------------------------------------------
// Result handling
// ---------------------------------------------------------------------------
function handleResult(data) {
  const { note, confidence_score, timings, models } = data;

  // Mark phase 4 done
  const p4 = document.querySelector('.phase-card[data-phase="4"]');
  if (p4) { p4.classList.remove('running'); p4.classList.add('done'); }

  // Timings
  if (timings) {
    timingP1.textContent    = `${timings.phase1 || 0}s`;
    timingP2.textContent    = `${timings.phase2 || 0}s`;
    timingP3.textContent    = `${timings.phase3 || 0}s`;
    timingTotal.textContent = `${timings.total  || 0}s`;
  }

  // Render markdown note
  if (note) {
    noteContent.innerHTML = marked.parse(note);
  }

  // Animate confidence ring
  animateRing(confidence_score || 0);

  // Show result
  showElement(resultWrap);
  resultWrap.scrollIntoView({ behavior: 'smooth', block: 'start' });

  appendFeed(`🏁 Research complete — Confidence: ${confidence_score}/100`);
}


// ---------------------------------------------------------------------------
// Confidence ring animation
// ---------------------------------------------------------------------------
function animateRing(score) {
  const circumference = 2 * Math.PI * 65;  // matches SVG r=65
  const target = circumference - (score / 100) * circumference;

  // Animate the number
  let current = 0;
  const duration = 1400;
  const start = performance.now();

  function step(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    // Ease out cubic
    const eased = 1 - Math.pow(1 - progress, 3);
    current = Math.round(eased * score);
    gaugeLabel.innerHTML = `${current}<small>/100</small>`;

    if (progress < 1) {
      requestAnimationFrame(step);
    }
  }
  requestAnimationFrame(step);

  // Animate the SVG stroke (via CSS transition set in stylesheet)
  requestAnimationFrame(() => {
    gaugeCircle.style.strokeDashoffset = target;
  });
}


// ---------------------------------------------------------------------------
// Feed
// ---------------------------------------------------------------------------
function appendFeed(text) {
  const line = document.createElement('div');
  line.className = 'feed__line';
  const now = new Date().toLocaleTimeString();
  line.innerHTML = `<span class="time">[${now}]</span> <span class="event">${escapeHtml(text)}</span>`;
  feedPanel.appendChild(line);
  feedPanel.scrollTop = feedPanel.scrollHeight;
}


// ---------------------------------------------------------------------------
// Error
// ---------------------------------------------------------------------------
function showError(msg) {
  errorMsg.textContent = msg;
  showElement(errorCard);
}


// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function showElement(el) { el.classList.add('visible'); }
function hideElement(el) { el.classList.remove('visible'); }

function resetPhases() {
  phaseCards.forEach(c => {
    c.classList.remove('running', 'done');
    const t = c.querySelector('.phase-card__time');
    if (t) t.textContent = '';
  });
}

function resetModels() {
  modelBadges.forEach(b => b.classList.remove('active'));
}

function resetUI() {
  hideElement(errorCard);
  hideElement(resultWrap);
  hideElement(phasesWrap);
  hideElement(feedWrap);
  hideElement(modelsWrap);
  feedPanel.innerHTML = '';
  resetPhases();
  resetModels();

  // Reset gauge
  gaugeCircle.style.strokeDashoffset = 408;
  gaugeLabel.innerHTML = '0<small>/100</small>';
}

function escapeHtml(s) {
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}
