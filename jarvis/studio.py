from __future__ import annotations
import threading
import traceback
import gradio as gr

class StudioController:
    def __init__(self, system):
        self.system = system
        self.lock = threading.Lock()
        self.worker = None
        self.last_error = None

    def _run_background(self, name, fn):
        if self.lock.locked():
            return {"ok": False, "message": "JARVIS is already running an operation."}
        def worker():
            with self.lock:
                try:
                    fn()
                except Exception as exc:
                    self.last_error = repr(exc)
                    self.system.storage.events.emit("error", {"operation": name, "error": repr(exc), "traceback": traceback.format_exc()})
                    state = self.system.storage.load_state()
                    state["last_error"] = repr(exc)
                    state["runtime"] = {"running": False, "operation": None, "step": 0, "total": 0, "loss": None}
                    self.system.storage.save_state(state)
        self.worker = threading.Thread(target=worker, name=f"jarvis-{name}", daemon=True)
        self.worker.start()
        return {"ok": True, "message": f"Started {name}."}

    def start_train(self, steps):
        steps = max(1, int(steps))
        return self._run_background("train", lambda: self.system.train(steps))

    def start_evolve(self):
        return self._run_background("evolve", self.system.evolve)

    def start_crawl(self):
        return self._run_background("crawl", self.system.crawl)

    def start_autonomous(self, cycles):
        cycles = max(1, int(cycles))
        return self._run_background("autonomous", lambda: self.system.autonomous_loop(cycles))

    def status_view(self):
        status = self.system.status()
        events = self.system.runtime_events(80)
        lines = []
        for e in events[-30:]:
            kind = e.get("kind", "event")
            if kind == "train_step":
                lines.append(f"TRAIN step {e.get('step')}/{e.get('total')} loss={float(e.get('loss', 0)):.4f}")
            elif kind == "train_start":
                lines.append(f"TRAIN started: {e.get('steps')} steps on {e.get('device')}")
            elif kind == "train_end":
                lines.append(f"TRAIN finished: loss {float(e.get('loss_before', 0)):.4f} -> {float(e.get('loss_after', 0)):.4f}")
            elif kind == "evolve_start":
                lines.append(f"EVOLVE generation {e.get('generation')} ({e.get('profile')})")
            elif kind == "evolve_end":
                lines.append(f"EVOLVE {e.get('action')} accepted={e.get('accepted')} best_loss={e.get('best_loss')}")
            elif kind == "error":
                lines.append(f"ERROR {e.get('operation')}: {e.get('error')}")
            elif kind == "web":
                lines.append(f"WEB pages={e.get('pages_seen')} added={e.get('pages_added')}")
        return status, "\n".join(lines[-30:])

def launch(system, share: bool = True):
    ctl = StudioController(system)

    def respond(message, history):
        result = system.chat(message)
        text = result.get("reply", "")
        retrieval = result.get("retrieval") or []
        if retrieval:
            # Retrieval results carry a score/chunk id/snippet, not a source URL,
            # so show that instead of a field that was never populated.
            text += "\n\nRetrieved evidence:\n" + "\n".join(
                f"- chunk {s.get('chunk_id')} (score {s.get('score')}): {s.get('text', '')[:80].strip()}..."
                for s in retrieval[:4]
            )
        return text

    with gr.Blocks(title="JARVIS Studio") as demo:
        gr.Markdown("# JARVIS Studio\nChat with the current checkpoint while watching training, evolution, public-web ingestion, and benchmark state.")
        with gr.Row():
            with gr.Column(scale=2):
                gr.ChatInterface(
                    fn=respond,
                    title="JARVIS",
                    description="From-scratch continual-learning research AI.",
                    examples=["Hello JARVIS", "What generation are you on?", "What have you learned?"]
                )
            with gr.Column(scale=1):
                gr.Markdown("## Live system monitor")
                status_box = gr.JSON(label="Status", value={})
                log_box = gr.Textbox(label="Live event log", lines=18, interactive=False)
                with gr.Row():
                    train_steps = gr.Number(value=25, label="Train steps", precision=0)
                    cycles = gr.Number(value=10, label="Autonomous cycles", precision=0)
                with gr.Row():
                    train_btn = gr.Button("Train")
                    evolve_btn = gr.Button("Evolve")
                with gr.Row():
                    crawl_btn = gr.Button("Learn from public web")
                    auto_btn = gr.Button("Autonomous run")
                refresh = gr.Button("Refresh now")
                action_box = gr.Textbox(label="Action", interactive=False)

        train_btn.click(lambda n: ctl.start_train(n), inputs=train_steps, outputs=action_box)
        evolve_btn.click(lambda: ctl.start_evolve(), outputs=action_box)
        crawl_btn.click(lambda: ctl.start_crawl(), outputs=action_box)
        auto_btn.click(lambda n: ctl.start_autonomous(n), inputs=cycles, outputs=action_box)
        refresh.click(ctl.status_view, outputs=[status_box, log_box])
        demo.load(ctl.status_view, outputs=[status_box, log_box])
        gr.Timer(1.0).tick(ctl.status_view, outputs=[status_box, log_box])
    demo.launch(share=share, show_error=True)
