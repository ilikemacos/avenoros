#!/usr/bin/env python3
import base64
import json
import socket
import sys
import time


def call(sock, cmd, args=None):
    msg = {"execute": cmd}
    if args is not None:
        msg["arguments"] = args
    sock.sendall(json.dumps(msg).encode() + b"\n")
    buf = b""
    while not buf.endswith(b"\n"):
        buf += sock.recv(65536)
    reply = json.loads(buf)
    if "error" in reply:
        raise RuntimeError(reply["error"]["desc"])
    return reply["return"]


def connect(path, timeout):
    deadline = time.monotonic() + timeout
    while True:
        try:
            sock = socket.socket(socket.AF_UNIX)
            sock.settimeout(5)
            sock.connect(path)
            sock.sendall(b'\xff{"execute":"guest-sync-delimited","arguments":{"id":1}}\n')
            data = b""
            while b'"return"' not in data:
                data += sock.recv(4096)
            sock.settimeout(120)
            return sock
        except OSError:
            if time.monotonic() > deadline:
                raise
            time.sleep(1)


def run(sock, argv):
    pid = call(sock, "guest-exec", {"path": argv[0], "arg": argv[1:], "capture-output": True})["pid"]
    while True:
        st = call(sock, "guest-exec-status", {"pid": pid})
        if st["exited"]:
            break
        time.sleep(0.5)
    out = base64.b64decode(st.get("out-data", "")).decode(errors="replace")
    err = base64.b64decode(st.get("err-data", "")).decode(errors="replace")
    return st.get("exitcode", 0), out + err


def main():
    path, timeout, argv = sys.argv[1], float(sys.argv[2]), sys.argv[3:]
    sock = connect(path, timeout)
    if not argv:
        return 0
    code, out = run(sock, argv)
    sys.stdout.write(out)
    return code


sys.exit(main())
