'use strict';

document.documentElement.classList.add('interactive');

const canonical = document.querySelector('[rel="canonical"]').href;
const share = document.querySelector('#share');
const shareStatus = document.querySelector('#share-status');
const shareFallback = document.querySelector('#share-fallback');
const shareUrl = document.querySelector('#share-url');

share.addEventListener('click', async () => {
  try {
    await navigator.clipboard.writeText(canonical);
    shareFallback.hidden = true;
    shareStatus.textContent = '已复制本集链接';
  } catch {
    shareFallback.hidden = false;
    shareUrl.focus();
    shareUrl.select();
    shareStatus.textContent = '请复制上方的本集链接';
  }
});

const audio = document.querySelector('audio');
const status = document.querySelector('#audio-status');
const follow = document.querySelector('#follow');
const transcript = document.querySelector('.transcript ol');
const rows = [...transcript.querySelectorAll('[data-time]')];
const times = rows.map(row => Number(row.dataset.time));
const positionKey = 'tianxi-podcasts:position:' + audio.dataset.positionPath;
let active;
let lastSave = -Infinity;

function loadPosition() {
  try {
    const saved = Number(localStorage.getItem(positionKey));
    if (saved > 0 && saved < audio.duration - 2) audio.currentTime = saved;
  } catch {
    // Storage may be disabled by the browser.
  }
}

function savePosition() {
  try {
    if (audio.ended) localStorage.removeItem(positionKey);
    else if (audio.readyState > 0) localStorage.setItem(positionKey, String(audio.currentTime));
  } catch {
    // Playback still works with storage disabled.
  }
}

function updateTranscript() {
  const next = rows[times.findLastIndex(time => time <= audio.currentTime)];
  if (active === next) return;
  active?.removeAttribute('aria-current');
  active = next;
  if (!active) return;
  active.setAttribute('aria-current', 'true');
  if (!follow.checked || audio.paused) return;

  const list = transcript.getBoundingClientRect();
  const line = active.getBoundingClientRect();
  if (line.top < list.top || line.bottom > list.bottom) {
    transcript.scrollTop += line.top - list.top - 12;
  }
}

function reportError() {
  status.textContent = '音频暂时无法载入，刷新页面后可重试。';
}

audio.addEventListener('loadedmetadata', loadPosition, { once: true });
if (audio.readyState > 0) loadPosition();
audio.addEventListener('timeupdate', () => {
  updateTranscript();
  if (performance.now() - lastSave > 5000) {
    savePosition();
    lastSave = performance.now();
  }
});
audio.addEventListener('pause', savePosition);
audio.addEventListener('seeked', savePosition);
audio.addEventListener('ended', savePosition);
audio.addEventListener('playing', () => { status.textContent = ''; });
audio.addEventListener('error', reportError, true);
window.addEventListener('pagehide', savePosition);

transcript.addEventListener('click', async (event) => {
  const button = event.target.closest('button.time');
  if (!button) return;
  const seconds = Number(button.parentElement.dataset.time);
  try {
    const pending = audio.play();
    if (audio.readyState > 0) audio.currentTime = seconds;
    else await pending.then(() => { audio.currentTime = seconds; });
    await pending;
  } catch {
    reportError();
  }
});
