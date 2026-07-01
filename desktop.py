"""
ES Image Studio — Eastern Studios
Desktop launcher: starts FastAPI on a free local port,
then opens a native app window (Edge on Windows, WebKit on Mac, GTK on Linux).
"""

import sys, os, time, socket, threading, logging, platform
logging.basicConfig(level=logging.WARNING)

APP_TITLE = "ES Image Studio — Eastern Studios"
BG_COLOR  = "#07111a"

def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]

PORT = _free_port()
os.environ["PORT"] = str(PORT)

def _run_server():
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=PORT, log_level="warning", reload=False)

threading.Thread(target=_run_server, daemon=True, name="api-server").start()

def _wait_for_server(timeout=90):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", PORT), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.15)
    return False

SPLASH = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"/>
<style>
  *, *::before, *::after { margin:0; padding:0; box-sizing:border-box; }
  body {
    background:#07111a;
    display:flex; flex-direction:column;
    align-items:center; justify-content:center;
    height:100vh;
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
    color:#4a7a8a;
    user-select:none;
  }
  .badge {
    width:68px; height:68px; border-radius:18px;
    background:linear-gradient(135deg,#007a78,#00c8c0);
    display:flex; align-items:center; justify-content:center;
    font-size:1.5rem; font-weight:900; color:#fff;
    box-shadow:0 0 40px rgba(0,200,192,.3);
    margin-bottom:20px;
  }
  .studio {
    font-size:1.3rem; font-weight:800;
    color:#00c8c0;
    letter-spacing:-.3px;
    margin-bottom:4px;
  }
  .sub {
    font-size:.75rem; color:#2a5060;
    text-transform:uppercase; letter-spacing:.08em;
    margin-bottom:36px;
  }
  .ring {
    width:36px; height:36px;
    border:3px solid #112030;
    border-top-color:#00c8c0;
    border-radius:50%;
    animation:spin .8s linear infinite;
    margin-bottom:12px;
  }
  @keyframes spin { to { transform:rotate(360deg); } }
  .hint { font-size:.72rem; color:#1e3a4a; }
</style>
</head>
<body>
  <div class="badge">ES</div>
  <div class="studio">Eastern Studios</div>
  <div class="sub">Image Studio</div>
  <div class="ring"></div>
  <div class="hint">Loading AI model&hellip;</div>
</body>
</html>"""

def main():
    try:
        import webview
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pywebview"])
        import webview

    window = webview.create_window(
        title=APP_TITLE,
        html=SPLASH,
        width=1200, height=860,
        min_size=(900, 660),
        resizable=True,
        background_color=BG_COLOR,
    )

    def _on_shown():
        if _wait_for_server(120):
            window.load_url(f"http://127.0.0.1:{PORT}")
        else:
            window.load_html(f"""<body style='background:{BG_COLOR};color:#f87171;
                font-family:sans-serif;display:flex;align-items:center;
                justify-content:center;height:100vh;font-size:.9rem;text-align:center;padding:2rem'>
                Server failed to start.<br>Run <code style='background:#112030;padding:2px 6px;border-radius:4px'>
                python desktop.py</code> in a terminal to see the error.
            </body>""")

    # Pick the right native backend for each OS
    _os = platform.system()
    if _os == "Windows":
        webview.start(_on_shown, gui="edgechromium", debug=False)
    elif _os == "Darwin":
        webview.start(_on_shown, gui="cocoa", debug=False)
    else:
        webview.start(_on_shown, gui="gtk", debug=False)

if __name__ == "__main__":
    main()
