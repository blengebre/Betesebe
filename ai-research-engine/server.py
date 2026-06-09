"""
Flask Web Server for the Deep Research Engine
Exposes the multi-agent pipeline as an SSE-streaming HTTP API.

Endpoints:
  GET  /           → SPA (templates/index.html)
  GET  /health     → {"status": "ok"}
  POST /research   → SSE stream of phase events + final result
"""
import json
import queue
import threading
import asyncio
from flask import Flask, Response, request, jsonify, render_template
from flask_cors import CORS
from config import validate_api_keys

app = Flask(__name__)
CORS(app)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.route("/health")
def health():
    return jsonify({"status": "ok"})


# ---------------------------------------------------------------------------
# SPA entry point
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


# ---------------------------------------------------------------------------
# Research endpoint — SSE stream
# ---------------------------------------------------------------------------

@app.route("/research", methods=["POST"])
def research():
    """
    Accepts JSON body: {"query": "..."}
    Returns a Server-Sent Events stream.

    Event types emitted:
      event: phase   — phase status updates (running / done)
      event: result  — final research note + metadata
      event: error   — pipeline failure message
      event: done    — signals stream end
    """
    body = request.get_json(silent=True) or {}
    query = (body.get("query") or "").strip()

    if not query:
        def error_stream():
            yield _sse("error", {"message": "No query provided."})
        return Response(error_stream(), mimetype="text/event-stream")

    # A thread-safe queue bridges the async pipeline into the sync SSE generator
    event_queue: queue.Queue = queue.Queue()

    def event_callback(event_type: str, payload):
        """Called from the asyncio thread; puts events into the queue."""
        event_queue.put((event_type, payload))

    def run_pipeline():
        """Runs the async pipeline in a dedicated thread with its own event loop."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            from executor import full_research_pipeline
            loop.run_until_complete(
                full_research_pipeline(query, event_callback=event_callback)
            )
        except Exception as e:
            event_queue.put(("error", {"message": str(e)}))
            event_queue.put(("done", {}))
        finally:
            loop.close()
            event_queue.put(_SENTINEL)  # always signal stream end

    # Start the pipeline in a background thread
    worker = threading.Thread(target=run_pipeline, daemon=True)
    worker.start()

    def sse_generator():
        """Pulls events from the queue and formats them as SSE."""
        while True:
            item = event_queue.get()
            if item is _SENTINEL:
                break
            event_type, payload = item
            yield _sse(event_type, payload)
            if event_type in ("done", "error"):
                break

    return Response(
        sse_generator(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # disables Nginx buffering if proxied
        },
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_SENTINEL = object()  # signals that the background thread is finished


def _sse(event: str, data: dict) -> str:
    """Format a single Server-Sent Event frame."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🚀 DEEP RESEARCH ENGINE — WEB SERVER")
    print("=" * 70)
    validate_api_keys()
    print("\n🌐 Starting Flask server at http://localhost:5000")
    print("   Open your browser and navigate to http://localhost:5000")
    print("=" * 70 + "\n")
    app.run(host="0.0.0.0", port=5001, threaded=True, debug=False)
