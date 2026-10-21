"""Screenshot a running VectorCraft (control channel) with the poster document, per scheme/brightness/tab.

Usage: shoot.py PORT PREFIX SCHEME BRIGHTNESS[,BRIGHTNESS...]
Writes PREFIX-<brightness>-<tab>.png and PREFIX.json (canvas rects) next to it.
"""
import json, sys, time
from fc import FC

port, prefix, scheme, brightnesses = int(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4].split(",")
v = FC(port)
v.call("ui.resize", {"width": 1440, "height": 900})
v.run("file.new", width=800, height=600)
e = v.run("shape.ellipse", x=120, y=150, width=260, height=260)["id"]
r = v.run("shape.rectangle", x=420, y=210, width=240, height=200)["id"]
t = v.run("text.create", x=120, y=530, text="Poster draft", size=46)["id"]
for i, c in [(e, "#F2B134"), (r, "#2A6F97"), (t, "#1B1B1B")]:
    v.run("select.set", ids=[i]); v.run("paint.setFill", color=c); v.run("paint.setStroke", none=True)
if scheme != "-":
    v.run("prefs.set", key="uiColorScheme", value=scheme)
v.run("select.set", ids=[e])
out = {}
for b in brightnesses:
    v.call("ui.set", {"brightness": b})
    for tab in ["properties", "layers"]:
        v.call("ui.set", {"panel": tab})
        time.sleep(1.2)
        path = f"{prefix}-{b}-{tab}.png"
        v.call("ui.screenshot", {"path": path})
        out[path] = v.call("ui.inspect")["canvasRect"]
v.call("ui.set", {"panel": "properties"})
json.dump(out, open(f"{prefix}.json", "w"), indent=1)
print(json.dumps(out))
