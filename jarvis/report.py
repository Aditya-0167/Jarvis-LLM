from __future__ import annotations
import json
from pathlib import Path


def build_report(root: str = "."):
    root = Path(root)
    workspace = root / "workspace"
    gen_dir = root / "generations"
    state = json.loads((workspace / "state.json").read_text(encoding="utf-8")) if (workspace / "state.json").exists() else {}
    rows = []
    if gen_dir.exists():
        for p in sorted(gen_dir.glob("generation_*/result.json")):
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
                rows.append({
                    "generation": int(p.parent.name.split("_")[-1]),
                    "action": d.get("action"),
                    "accepted": d.get("accepted"),
                    "base_loss": d.get("base_loss"),
                    "best_loss": d.get("best_loss")
                })
            except Exception:
                continue
    html = [
        "<!doctype html><html><head><meta charset='utf-8'><title>JARVIS Research Report</title>",
        "<style>body{font-family:system-ui;max-width:1100px;margin:30px auto;padding:0 16px}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ddd;padding:7px;text-align:left}pre{background:#111;color:#eee;padding:12px;overflow:auto}</style></head><body>",
        "<h1>JARVIS Research Report</h1>",
        "<p>This report is an evidence log, not a claim of AGI, consciousness, or unrestricted autonomy.</p>",
        f"<h2>Current state</h2><pre>{json.dumps(state, indent=2)}</pre>",
        "<h2>Evolution history</h2><table><tr><th>Generation</th><th>Action</th><th>Accepted</th><th>Base loss</th><th>Best loss</th></tr>"
    ]
    for row in rows:
        html.append("<tr>" + "".join(f"<td>{row.get(k)}</td>" for k in ["generation","action","accepted","base_loss","best_loss"]) + "</tr>")
    html.append("</table></body></html>")
    out = workspace / "research_report.html"
    out.write_text("\n".join(html), encoding="utf-8")
    return out
