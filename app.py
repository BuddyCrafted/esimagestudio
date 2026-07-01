"""
ES Image Studio — Eastern Studios
Multi-tool image processing suite.
Tool 1: AI Background Remover (BiRefNet)
"""

import io
import os
import time
import uuid
import threading
import logging
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from PIL import Image
from rembg import remove, new_session

# ── Config ────────────────────────────────────────────────────────────────────
PORT        = int(os.environ.get("PORT", 3000))
MAX_MB      = int(os.environ.get("MAX_UPLOAD_MB", 30))
MODEL       = os.environ.get("REMBG_MODEL", "birefnet-general")
CLEANUP_HRS = int(os.environ.get("CLEANUP_HOURS", 24))

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
log = logging.getLogger(__name__)

app = FastAPI(title="ES Image Studio")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ── Model ─────────────────────────────────────────────────────────────────────
rembg_session = None

@app.on_event("startup")
def load_model():
    global rembg_session
    log.info(f"Loading BiRefNet model — first run downloads ~500 MB…")
    rembg_session = new_session(MODEL)
    log.info("Model ready.")

# ── 24-hour cleanup ───────────────────────────────────────────────────────────
def _cleanup_loop():
    while True:
        cutoff = time.time() - (CLEANUP_HRS * 3600)
        deleted = 0
        for f in UPLOAD_DIR.iterdir():
            try:
                if f.is_file() and f.stat().st_mtime < cutoff:
                    f.unlink(); deleted += 1
            except Exception:
                pass
        if deleted:
            log.info(f"Cleanup: removed {deleted} file(s)")
        time.sleep(3600)

threading.Thread(target=_cleanup_loop, daemon=True).start()

# ── API ───────────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML_PAGE

@app.post("/remove-bg")
async def remove_bg(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image.")
    data = await file.read()
    if len(data) > MAX_MB * 1024 * 1024:
        raise HTTPException(413, f"File exceeds {MAX_MB} MB limit.")
    try:
        img = Image.open(io.BytesIO(data)).convert("RGBA")
    except Exception:
        raise HTTPException(400, "Could not open image.")

    log.info(f"Processing {file.filename!r} ({img.size[0]}x{img.size[1]})")
    result = remove(img, session=rembg_session)

    out_path = UPLOAD_DIR / f"{uuid.uuid4().hex}.png"
    result.save(out_path, "PNG")

    buf = io.BytesIO()
    result.save(buf, "PNG")
    buf.seek(0)
    stem = Path(file.filename).stem if file.filename else "image"
    return Response(
        content=buf.read(),
        media_type="image/png",
        headers={"Content-Disposition": f'attachment; filename="{stem}_no_bg.png"'},
    )

@app.get("/health")
async def health():
    return {"status": "ok", "model": MODEL}

# ── UI ────────────────────────────────────────────────────────────────────────
HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>ES Image Studio</title>
<style>
/* ── Reset & tokens ─────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg:          #07111a;
  --surface:     #0c1c28;
  --card:        #102030;
  --border:      #173040;
  --border-lit:  #1f4560;

  --aqua:        #00c8c0;
  --aqua-bright: #00e8de;
  --aqua-dim:    rgba(0,200,192,.12);
  --aqua-glow:   rgba(0,200,192,.25);

  --text:        #e6f6f8;
  --text-muted:  #4a7a8a;
  --text-subtle: #2a5060;

  --white:       #ffffff;
  --radius-sm:   8px;
  --radius:      14px;
  --radius-lg:   20px;
  --sidebar-w:   230px;
  --trans:       .18s ease;
}

html, body {
  height: 100%; overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
  background: var(--bg);
  color: var(--text);
  font-size: 14px;
}

/* ── App shell ──────────────────────────────────────────────────────────── */
.app {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* ── Sidebar ────────────────────────────────────────────────────────────── */
.sidebar {
  width: var(--sidebar-w);
  flex-shrink: 0;
  background: #ffffff;
  border-right: 1px solid #e2e8ed;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-header {
  padding: 24px 20px 20px;
  border-bottom: 1px solid #e8edf0;
}

.brand {
  display: flex;
  align-items: center;
  gap: 11px;
}

.brand-badge {
  width: 36px; height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, #007a78, var(--aqua));
  display: flex; align-items: center; justify-content: center;
  font-size: .78rem; font-weight: 900; color: #fff;
  letter-spacing: -.3px;
  flex-shrink: 0;
  box-shadow: 0 0 16px var(--aqua-glow);
}

.brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.brand-name {
  font-size: .82rem;
  font-weight: 700;
  color: #111827;
  letter-spacing: .01em;
}

.brand-sub {
  font-size: .68rem;
  color: var(--aqua);
  font-weight: 500;
  letter-spacing: .04em;
  text-transform: uppercase;
}

/* ── Nav ────────────────────────────────────────────────────────────────── */
.nav {
  flex: 1;
  overflow-y: auto;
  padding: 12px 10px;
}

.nav-section-label {
  font-size: .65rem;
  font-weight: 700;
  letter-spacing: .1em;
  text-transform: uppercase;
  color: #9aaab4;
  padding: 10px 10px 6px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 9px 12px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background var(--trans), color var(--trans);
  color: #374151;
  user-select: none;
  margin-bottom: 2px;
  position: relative;
}

.nav-item:hover {
  background: #f0faf9;
  color: #111827;
}

.nav-item.active {
  background: #e6faf8;
  color: #007a78;
  border: 1px solid rgba(0,180,170,.2);
}

.nav-item.active .nav-icon { color: #00a89e; }

.nav-item.disabled {
  cursor: default;
  opacity: .5;
}
.nav-item.disabled:hover { background: none; color: #374151; }

.nav-icon {
  width: 18px; height: 18px;
  flex-shrink: 0;
  color: currentColor;
}

.nav-label { font-size: .82rem; font-weight: 500; }

.nav-badge {
  margin-left: auto;
  font-size: .6rem;
  font-weight: 700;
  letter-spacing: .04em;
  text-transform: uppercase;
  padding: 2px 6px;
  border-radius: 4px;
  background: #e6faf8;
  color: #007a78;
  border: 1px solid rgba(0,150,140,.18);
}

.nav-badge.soon {
  background: #f3f4f6;
  color: #9ca3af;
  border-color: #e5e7eb;
}

/* ── Sidebar footer ─────────────────────────────────────────────────────── */
.sidebar-footer {
  padding: 14px 20px;
  border-top: 1px solid #e8edf0;
  font-size: .68rem;
  color: #9ca3af;
  line-height: 1.5;
}

/* ── Main content ───────────────────────────────────────────────────────── */
.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--bg);
}

/* ── Top bar ────────────────────────────────────────────────────────────── */
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 28px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
  background: var(--surface);
}

.topbar-left { display: flex; flex-direction: column; gap: 2px; }
.topbar-title { font-size: 1rem; font-weight: 700; color: var(--white); }
.topbar-desc  { font-size: .75rem; color: var(--text-muted); }

.topbar-right { display: flex; align-items: center; gap: 10px; }

.status-dot {
  display: flex; align-items: center; gap: 6px;
  font-size: .72rem; color: var(--text-muted);
}

.dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--aqua);
  box-shadow: 0 0 8px var(--aqua-glow);
  animation: pulse 2.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50%       { opacity: .4; }
}

/* ── Content area ───────────────────────────────────────────────────────── */
.content {
  flex: 1;
  overflow-y: auto;
  padding: 32px 36px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* ── Upload panel ───────────────────────────────────────────────────────── */
.upload-panel {
  width: 100%;
  max-width: 680px;
}

/* ── Drop zone ──────────────────────────────────────────────────────────── */
#drop-zone {
  border: 1.5px dashed var(--border-lit);
  border-radius: var(--radius-lg);
  background: var(--surface);
  padding: 64px 40px;
  text-align: center;
  cursor: pointer;
  transition: border-color var(--trans), background var(--trans), box-shadow var(--trans);
  position: relative;
  overflow: hidden;
}

#drop-zone::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at 50% 0%, rgba(0,200,192,.06) 0%, transparent 70%);
  pointer-events: none;
}

#drop-zone:hover,
#drop-zone.drag-over {
  border-color: var(--aqua);
  background: #0e2030;
  box-shadow: 0 0 40px var(--aqua-dim), inset 0 0 40px rgba(0,200,192,.04);
}

.drop-icon {
  width: 52px; height: 52px;
  margin: 0 auto 18px;
  background: var(--aqua-dim);
  border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  border: 1px solid rgba(0,200,192,.2);
}

.drop-icon svg { color: var(--aqua); }

#drop-zone h2 {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--white);
  margin-bottom: 8px;
}

#drop-zone p {
  font-size: .8rem;
  color: var(--text-muted);
  margin-bottom: 22px;
  line-height: 1.6;
}

#file-input { display: none; }

.btn-choose {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 10px 22px;
  background: var(--aqua);
  color: #042025;
  border-radius: var(--radius-sm);
  font-weight: 700;
  font-size: .82rem;
  cursor: pointer;
  border: none;
  transition: background var(--trans), transform .1s;
  letter-spacing: .02em;
}

.btn-choose:hover { background: var(--aqua-bright); transform: translateY(-1px); }

/* ── Processing state ───────────────────────────────────────────────────── */
#processing {
  display: none;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 64px 40px;
  background: var(--surface);
  border-radius: var(--radius-lg);
  border: 1.5px solid var(--border-lit);
}

.proc-ring {
  position: relative;
  width: 52px; height: 52px;
}

.proc-ring svg {
  animation: spin .9s linear infinite;
  width: 52px; height: 52px;
}

@keyframes spin { to { transform: rotate(360deg); } }

#processing h3 { font-size: .95rem; font-weight: 700; color: var(--white); }
#processing p  { font-size: .78rem; color: var(--text-muted); }

/* ── Result state ───────────────────────────────────────────────────────── */
#result { display: none; width: 100%; max-width: 860px; }

.result-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 18px;
}

.result-header h3 { font-size: .95rem; font-weight: 700; color: var(--white); }

.result-meta {
  font-size: .72rem;
  color: var(--aqua);
  background: var(--aqua-dim);
  border: 1px solid rgba(0,200,192,.2);
  border-radius: 6px;
  padding: 3px 10px;
}

.result-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  margin-bottom: 18px;
}

@media (max-width: 620px) { .result-grid { grid-template-columns: 1fr; } }

.img-card {
  border-radius: var(--radius);
  overflow: hidden;
  border: 1px solid var(--border);
  background: var(--card);
}

.img-card-header {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 14px;
  border-bottom: 1px solid var(--border);
}

.img-card-dot {
  width: 8px; height: 8px; border-radius: 50%;
}

.img-card-dot.original  { background: #4a7a8a; }
.img-card-dot.processed { background: var(--aqua); box-shadow: 0 0 6px var(--aqua-glow); }

.img-card-label {
  font-size: .72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .06em;
  color: var(--text-muted);
}

.img-card img {
  width: 100%; display: block;
  object-fit: contain;
  max-height: 380px;
}

.checker {
  background-image:
    linear-gradient(45deg, #162030 25%, transparent 25%),
    linear-gradient(-45deg, #162030 25%, transparent 25%),
    linear-gradient(45deg, transparent 75%, #162030 75%),
    linear-gradient(-45deg, transparent 75%, #162030 75%);
  background-size: 18px 18px;
  background-position: 0 0, 0 9px, 9px -9px, -9px 0;
  background-color: #0e1e2c;
}

.result-actions { display: flex; gap: 10px; flex-wrap: wrap; }

.btn {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 11px 24px;
  border-radius: var(--radius-sm);
  font-weight: 700;
  font-size: .82rem;
  cursor: pointer;
  border: none;
  transition: background var(--trans), transform .1s, opacity var(--trans);
  letter-spacing: .02em;
}

.btn:hover { transform: translateY(-1px); opacity: .92; }

.btn-primary {
  background: var(--aqua);
  color: #042025;
}
.btn-primary:hover { background: var(--aqua-bright); }

.btn-ghost {
  background: transparent;
  color: var(--text);
  border: 1px solid var(--border-lit);
}
.btn-ghost:hover { background: var(--aqua-dim); border-color: var(--aqua); color: var(--aqua); }

/* ── Error ──────────────────────────────────────────────────────────────── */
#error-msg {
  display: none;
  margin-top: 14px;
  padding: 13px 18px;
  background: rgba(239,68,68,.08);
  border: 1px solid rgba(239,68,68,.25);
  border-radius: var(--radius-sm);
  color: #f87171;
  font-size: .8rem;
  width: 100%;
  max-width: 680px;
  text-align: center;
}

/* ── Scrollbar ──────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--border-lit); }
</style>
</head>
<body>
<div class="app">

  <!-- ── Sidebar ────────────────────────────────────────────────────────── -->
  <aside class="sidebar">
    <div class="sidebar-header">
      <div class="brand">
        <div class="brand-badge">ES</div>
        <div class="brand-text">
          <span class="brand-name">Eastern Studios</span>
          <span class="brand-sub">Image Studio</span>
        </div>
      </div>
    </div>

    <nav class="nav">
      <div class="nav-section-label">Image Tools</div>

      <div class="nav-item active" onclick="setTool('bg-remove')">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <rect x="3" y="3" width="18" height="18" rx="3"/>
          <path d="M3 9h18M9 21V9"/>
        </svg>
        <span class="nav-label">Background Remover</span>
        <span class="nav-badge">Active</span>
      </div>

      <div class="nav-item disabled">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="17 8 12 3 7 8"/>
          <line x1="12" y1="3" x2="12" y2="15"/>
        </svg>
        <span class="nav-label">Image Resizer</span>
        <span class="nav-badge soon">Soon</span>
      </div>

      <div class="nav-item disabled">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <polyline points="16 3 21 3 21 8"/>
          <line x1="4" y1="20" x2="21" y2="3"/>
          <polyline points="21 16 21 21 16 21"/>
          <line x1="15" y1="15" x2="21" y2="21"/>
        </svg>
        <span class="nav-label">Format Converter</span>
        <span class="nav-badge soon">Soon</span>
      </div>

      <div class="nav-item disabled">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
          <rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>
        </svg>
        <span class="nav-label">Batch Processor</span>
        <span class="nav-badge soon">Soon</span>
      </div>

      <div class="nav-item disabled">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <circle cx="12" cy="12" r="3"/>
          <path d="M19.07 4.93a10 10 0 0 1 0 14.14"/>
          <path d="M4.93 4.93a10 10 0 0 0 0 14.14"/>
        </svg>
        <span class="nav-label">AI Enhance</span>
        <span class="nav-badge soon">Soon</span>
      </div>

      <div class="nav-section-label" style="margin-top:8px">Studio</div>

      <div class="nav-item disabled">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
        </svg>
        <span class="nav-label">Project History</span>
        <span class="nav-badge soon">Soon</span>
      </div>
    </nav>

    <div class="sidebar-footer">
      Eastern Studios &copy; 2026<br>
      ES Image Studio v1.0
    </div>
  </aside>

  <!-- ── Main ───────────────────────────────────────────────────────────── -->
  <div class="main">

    <!-- Top bar -->
    <div class="topbar">
      <div class="topbar-left">
        <span class="topbar-title">Background Remover</span>
        <span class="topbar-desc">Remove any background instantly — full resolution PNG output</span>
      </div>
      <div class="topbar-right">
        <div class="status-dot">
          <div class="dot"></div>
          BiRefNet AI &bull; Ready
        </div>
      </div>
    </div>

    <!-- Content -->
    <div class="content">

      <!-- Drop zone -->
      <div id="drop-zone" class="upload-panel">
        <div class="drop-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="17 8 12 3 7 8"/>
            <line x1="12" y1="3" x2="12" y2="15"/>
          </svg>
        </div>
        <h2>Drop your image here</h2>
        <p>PNG, JPG, WEBP &mdash; up to 30 MB<br>Output is always full resolution with transparent background</p>
        <label class="btn-choose">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
          Choose File
          <input type="file" id="file-input" accept="image/*"/>
        </label>
      </div>

      <!-- Processing -->
      <div id="processing" class="upload-panel">
        <div class="proc-ring">
          <svg viewBox="0 0 52 52" fill="none">
            <circle cx="26" cy="26" r="22" stroke="#173040" stroke-width="3"/>
            <circle cx="26" cy="26" r="22" stroke="#00c8c0" stroke-width="3"
              stroke-dasharray="138" stroke-dashoffset="100" stroke-linecap="round"/>
          </svg>
        </div>
        <h3>Removing background&hellip;</h3>
        <p>AI is analyzing your image &mdash; full resolution is preserved</p>
      </div>

      <!-- Result -->
      <div id="result">
        <div class="result-header">
          <h3>Result</h3>
          <span class="result-meta" id="result-meta">PNG &bull; Transparent</span>
        </div>

        <div class="result-grid">
          <div class="img-card">
            <div class="img-card-header">
              <div class="img-card-dot original"></div>
              <span class="img-card-label">Original</span>
            </div>
            <img id="orig-img" src="" alt="Original"/>
          </div>
          <div class="img-card checker">
            <div class="img-card-header" style="background:rgba(7,17,26,.7);backdrop-filter:blur(4px)">
              <div class="img-card-dot processed"></div>
              <span class="img-card-label" style="color:#00c8c0">Background Removed</span>
            </div>
            <img id="result-img" src="" alt="Result"/>
          </div>
        </div>

        <div class="result-actions">
          <button class="btn btn-primary" id="download-btn">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            Download PNG
          </button>
          <button class="btn btn-ghost" id="new-btn">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 .49-3.67"/></svg>
            New Image
          </button>
        </div>
      </div>

      <div id="error-msg"></div>

    </div><!-- /content -->
  </div><!-- /main -->
</div><!-- /app -->

<script>
function setTool(t) { /* future routing hook */ }

const dropZone    = document.getElementById('drop-zone');
const fileInput   = document.getElementById('file-input');
const processing  = document.getElementById('processing');
const resultEl    = document.getElementById('result');
const origImg     = document.getElementById('orig-img');
const resultImg   = document.getElementById('result-img');
const downloadBtn = document.getElementById('download-btn');
const newBtn      = document.getElementById('new-btn');
const errorMsg    = document.getElementById('error-msg');
const resultMeta  = document.getElementById('result-meta');

let resultBlob = null;
let origFilename = 'image';

// Drag & drop
dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('drag-over'); });
dropZone.addEventListener('dragleave', ()  => dropZone.classList.remove('drag-over'));
dropZone.addEventListener('drop', e => {
  e.preventDefault(); dropZone.classList.remove('drag-over');
  if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]);
});
dropZone.addEventListener('click', e => {
  if (e.target !== fileInput && !e.target.closest('label')) fileInput.click();
});
fileInput.addEventListener('change', () => { if (fileInput.files[0]) handleFile(fileInput.files[0]); });

async function handleFile(file) {
  if (!file.type.startsWith('image/')) { showError('Please upload an image file (PNG, JPG, WEBP).'); return; }
  if (file.size > 30 * 1024 * 1024)   { showError('File exceeds 30 MB limit.'); return; }
  origFilename = file.name.replace(/\.[^.]+$/, '');
  origImg.src = URL.createObjectURL(file);
  showState('processing');
  hideError();

  const form = new FormData();
  form.append('file', file);
  try {
    const res = await fetch('/remove-bg', { method: 'POST', body: form });
    if (!res.ok) {
      let msg = 'Server error.';
      try { msg = (await res.json()).detail || msg; } catch {}
      throw new Error(msg);
    }
    resultBlob = await res.blob();
    resultImg.src = URL.createObjectURL(resultBlob);

    // Show dimensions in meta tag
    const bmp = await createImageBitmap(resultBlob);
    resultMeta.textContent = `PNG • ${bmp.width}×${bmp.height} • Transparent`;

    showState('result');
  } catch (err) {
    showState('drop');
    showError(err.message || 'Something went wrong — please try again.');
  }
}

downloadBtn.addEventListener('click', () => {
  if (!resultBlob) return;
  const a = document.createElement('a');
  a.href = URL.createObjectURL(resultBlob);
  a.download = origFilename + '_no_bg.png';
  a.click();
});

newBtn.addEventListener('click', () => {
  resultBlob = null; fileInput.value = '';
  origImg.src = ''; resultImg.src = '';
  showState('drop'); hideError();
});

function showState(s) {
  dropZone.style.display   = s === 'drop'       ? 'block' : 'none';
  processing.style.display = s === 'processing' ? 'flex'  : 'none';
  resultEl.style.display   = s === 'result'     ? 'block' : 'none';
}
function showError(m) { errorMsg.textContent = m; errorMsg.style.display = 'block'; }
function hideError()  { errorMsg.style.display = 'none'; }
</script>
</body>
</html>"""

if __name__ == "__main__":
    log.info(f"Starting ES Image Studio on port {PORT}")
    uvicorn.run("app:app", host="0.0.0.0", port=PORT, reload=False)
