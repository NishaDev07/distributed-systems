"""
client1.py — Command-line client that talks to the load balancer (port 5000).

Usage:
    python client1.py store  <local-file>
    python client1.py get    <key>  [output-file]
    python client1.py delete <key>
    python client1.py list
    python client1.py peers
    python client1.py health
"""

import sys
import os
import requests

LB_BASE = os.environ.get("LB_URL", "http://127.0.0.1:5000")


def cmd_store(path: str):
    if not os.path.exists(path):
        print(f"Error: file not found: {path}")
        sys.exit(1)
    key = os.path.basename(path)
    with open(path, "rb") as fh:
        data = fh.read()
    r = requests.put(f"{LB_BASE}/files/{key}", data=data, timeout=30)
    r.raise_for_status()
    resp = r.json()
    print(f"Stored → key={resp['key']}")


def cmd_get(key: str, out_path: str | None = None):
    r = requests.get(f"{LB_BASE}/files/{key}", timeout=30, stream=True)
    if r.status_code == 404:
        print(f"Not found: {key}")
        sys.exit(1)
    r.raise_for_status()
    dest = out_path or key.split("/")[-1]
    with open(dest, "wb") as fh:
        for chunk in r.iter_content(4096):
            fh.write(chunk)
    print(f"Saved → {dest}")


def cmd_delete(key: str):
    r = requests.delete(f"{LB_BASE}/files/{key}", timeout=10)
    r.raise_for_status()
    print(f"Deleted: {key}")


def cmd_list():
    r = requests.get(f"{LB_BASE}/files", timeout=10)
    r.raise_for_status()
    keys = r.json().get("keys") or []
    if not keys:
        print("(no files)")
        return
    for k in keys:
        print(f"  {k}")


def cmd_peers():
    r = requests.get(f"{LB_BASE}/peers", timeout=10)
    r.raise_for_status()
    peers = r.json().get("peers") or []
    if not peers:
        print("(no peers)")
        return
    for p in peers:
        print(f"  {p.get('id')}  {p.get('addr')}")


def cmd_health():
    r = requests.get(f"{LB_BASE}/health", timeout=5)
    r.raise_for_status()
    info = r.json()
    print(f"LB status: {info['status']}")
    for n in info.get("nodes", []):
        status = "✓ UP" if n["healthy"] else "✗ DOWN"
        print(f"  {status}  {n['addr']}")


COMMANDS = {
    "store": lambda args: cmd_store(args[0]),
    "get":   lambda args: cmd_get(args[0], args[1] if len(args) > 1 else None),
    "delete": lambda args: cmd_delete(args[0]),
    "list":  lambda args: cmd_list(),
    "peers": lambda args: cmd_peers(),
    "health": lambda args: cmd_health(),
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        sys.exit(1)
    try:
        COMMANDS[sys.argv[1]](sys.argv[2:])
    except requests.RequestException as e:
        print(f"HTTP error: {e}")
        sys.exit(1)
