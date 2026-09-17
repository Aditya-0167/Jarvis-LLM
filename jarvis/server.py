from __future__ import annotations
from flask import Flask, jsonify, request, render_template_string

HTML = """
<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>JARVIS V4</title>
<style>body{font-family:system-ui;max-width:1100px;margin:30px auto;padding:0 16px;line-height:1.4}button{padding:9px 13px;margin:3px;border:0;border-radius:7px;cursor:pointer}textarea{width:100%;min-height:90px;padding:10px;font:inherit}pre{background:#111;color:#eee;padding:12px;border-radius:8px;overflow:auto}.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}.card{border:1px solid #ddd;padding:14px;border-radius:12px}@media(max-width:800px){.grid{grid-template-columns:1fr}}</style>
</head><body><h1>JARVIS V4</h1><p>From-scratch continual-learning and self-development research system.</p>
<div class='grid'><div class='card'><h2>System</h2><button onclick='refresh()'>Refresh</button><button onclick='train()'>Train</button><button onclick='evolve()'>Evolve</button><button onclick='crawl()'>Learn Web</button><pre id='status'>Loading...</pre></div>
<div class='card'><h2>Chat</h2><textarea id='q' placeholder='Ask JARVIS something about its learned corpus or memories'></textarea><button onclick='chat()'>Send</button><pre id='a'></pre></div></div>
<script>
async function jsonfetch(url,opts){let r=await fetch(url,opts);return await r.json()}
async function refresh(){document.getElementById('status').textContent=JSON.stringify(await jsonfetch('/api/status'),null,2)}
async function train(){document.getElementById('status').textContent=JSON.stringify(await jsonfetch('/api/train',{method:'POST'}),null,2)}
async function evolve(){document.getElementById('status').textContent=JSON.stringify(await jsonfetch('/api/evolve',{method:'POST'}),null,2)}
async function crawl(){document.getElementById('status').textContent=JSON.stringify(await jsonfetch('/api/crawl',{method:'POST'}),null,2)}
async function chat(){let q=document.getElementById('q').value;document.getElementById('a').textContent=JSON.stringify(await jsonfetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:q})}),null,2)} refresh();
</script></body></html>
"""


def create_app(system):
    app = Flask(__name__)

    @app.get("/")
    def home():
        return render_template_string(HTML)

    @app.get("/api/status")
    def status():
        return jsonify(system.status())

    @app.post("/api/train")
    def train():
        return jsonify(system.train())

    @app.post("/api/evolve")
    def evolve():
        return jsonify(system.evolve())

    @app.post("/api/crawl")
    def crawl():
        return jsonify(system.crawl())

    @app.post("/api/chat")
    def chat():
        payload = request.get_json(silent=True) or {}
        return jsonify(system.chat(str(payload.get("text", ""))))

    return app
