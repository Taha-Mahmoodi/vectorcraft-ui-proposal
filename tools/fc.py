"""Tiny client for FigCraft's control channel (newline-delimited JSON on 127.0.0.1)."""
import json, socket

class FC:
    def __init__(self, port=7981):
        self.s = socket.create_connection(("127.0.0.1", port))
        self.s.settimeout(120)
        self.f = self.s.makefile("rw")
        self.n = 0

    def call(self, method, params=None):
        self.n += 1
        self.f.write(json.dumps({"id": self.n, "method": method, "params": params or {}}) + "\n")
        self.f.flush()
        r = json.loads(self.f.readline())
        if not r.get("ok"):
            raise RuntimeError(f"{method} {json.dumps(params)[:300]}: {r.get('error')}")
        return r.get("result")

    def run(self, command, **params):
        return self.call("engine.execute", {"command": command, "params": params})
