"""
flask_lb.py — Flask load balancer for the distributed file storage system.

Sits in front of multiple Go DFS nodes.  Forwards every API request to the
next healthy node using round-robin.  Exposes the same HTTP API as the
individual server nodes so clients don't need to know about the topology.
"""

import os
import time
import threading
from flask import Flask, request, jsonify, send_file
import io

from dfs_client import DFSClient, DFSError

app = Flask(__name__)

# ── Node pool ────────────────────────────────────────────────────────────── #

NODE_ADDRS = [
    addr.strip()
    for addr in os.environ.get("DFS_NODES", "127.0.0.1:9000,127.0.0.1:9001,127.0.0.1:9002").split(",")
    if addr.strip()
]

_clients = [
    DFSClient(host, int(port))
    for host, port in (a.rsplit(":", 1) for a in NODE_ADDRS)
]
_healthy   = {i: True for i in range(len(_clients))}
_rr_index  = 0
_lock      = threading.Lock()


def _get_client() -> DFSClient:
    """Return the next healthy client (round-robin)."""
    global _rr_index
    with _lock:
        start = _rr_index
        for _ in range(len(_clients)):
            idx = _rr_index % len(_clients)
            _rr_index += 1
            if _healthy.get(idx):
                return _clients[idx]
        # All unhealthy — try anyway with the first one
        return _clients[start % len(_clients)]


def _health_loop():
    """Background thread — pings every node every 5 s."""
    while True:
        for i, client in enumerate(_clients):
            alive = client.ping()
            with _lock:
                if _healthy[i] != alive:
                    status = "UP" if alive else "DOWN"
                    print(f"[lb] node {client} → {status}")
                _healthy[i] = alive
        time.sleep(5)


threading.Thread(target=_health_loop, daemon=True).start()

# ── Routes ───────────────────────────────────────────────────────────────── #

@app.route("/health")
def health():
    with _lock:
        nodes = [
            {"addr": str(_clients[i]), "healthy": _healthy[i]}
            for i in range(len(_clients))
        ]
    return jsonify({"status": "ok", "nodes": nodes})


@app.route("/files", methods=["GET"])
def list_files():
    try:
        keys = _get_client().list_files()
        return jsonify({"ok": True, "keys": keys})
    except DFSError as e:
        return jsonify({"ok": False, "error": str(e)}), 502


@app.route("/files/<path:key>", methods=["PUT", "POST"])
def upload(key):
    data = request.get_data()
    if not data:
        return jsonify({"ok": False, "error": "empty body"}), 400
    try:
        stored_key = _get_client().store(key, data)
        return jsonify({"ok": True, "key": stored_key}), 201
    except DFSError as e:
        return jsonify({"ok": False, "error": str(e)}), 502


@app.route("/files/<path:key>", methods=["GET"])
def download(key):
    try:
        data = _get_client().retrieve(key)
        return send_file(
            io.BytesIO(data),
            download_name=key.split("/")[-1],
            as_attachment=True,
        )
    except DFSError as e:
        return jsonify({"ok": False, "error": str(e)}), 404


@app.route("/files/<path:key>", methods=["DELETE"])
def delete(key):
    try:
        _get_client().delete(key)
        return jsonify({"ok": True})
    except DFSError as e:
        return jsonify({"ok": False, "error": str(e)}), 502


@app.route("/peers")
def peers():
    try:
        ps = _get_client().peers()
        return jsonify({"ok": True, "peers": ps})
    except DFSError as e:
        return jsonify({"ok": False, "error": str(e)}), 502


if __name__ == "__main__":
    port = int(os.environ.get("LB_PORT", 5000))
    print(f"[lb] Load balancer → http://0.0.0.0:{port}")
    print(f"[lb] Backend nodes: {NODE_ADDRS}")
    app.run(host="0.0.0.0", port=port, debug=False)
