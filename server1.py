"""
flask_s2.py — Web UI for DFS node 2 (Go node on :9001).

Mirrors flask_s1.py but points at the second Go node.
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import io

from dfs_client import DFSClient, DFSError

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dfs-s2-secret")

NODE_HOST = os.environ.get("NODE2_HOST", "127.0.0.1")
NODE_PORT = int(os.environ.get("NODE2_PORT", "9001"))
client = DFSClient(NODE_HOST, NODE_PORT)


@app.route("/")
def index():
    try:
        files = client.list_files()
        peers = client.peers()
        healthy = client.ping()
    except Exception as e:
        flash(f"Node unreachable: {e}", "danger")
        files, peers, healthy = [], [], False
    return render_template(
        "index.html",
        files=files,
        peers=peers,
        healthy=healthy,
        node=f"{NODE_HOST}:{NODE_PORT}",
        server_name="Server 2",
    )


@app.route("/upload", methods=["POST"])
def upload():
    f = request.files.get("file")
    if not f or f.filename == "":
        flash("No file selected.", "warning")
        return redirect(url_for("index"))
    try:
        key = client.store(f.filename, f.read())
        flash(f"Stored as '{key}'", "success")
    except DFSError as e:
        flash(f"Upload failed: {e}", "danger")
    return redirect(url_for("index"))


@app.route("/download/<path:key>")
def download(key):
    try:
        data = client.retrieve(key)
        return send_file(io.BytesIO(data), download_name=key.split("/")[-1], as_attachment=True)
    except DFSError as e:
        flash(f"Download failed: {e}", "danger")
        return redirect(url_for("index"))


@app.route("/delete/<path:key>", methods=["POST"])
def delete(key):
    try:
        client.delete(key)
        flash(f"Deleted '{key}'", "success")
    except DFSError as e:
        flash(f"Delete failed: {e}", "danger")
    return redirect(url_for("index"))


if __name__ == "__main__":
    port = int(os.environ.get("S2_PORT", 5002))
    print(f"[s2] Server 2 UI → http://0.0.0.0:{port}  (Go node: {NODE_HOST}:{NODE_PORT})")
    app.run(host="0.0.0.0", port=port, debug=False)
