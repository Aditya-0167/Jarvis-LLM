from __future__ import annotations
import gradio as gr


def launch(system, share: bool = True):
    def respond(message, history):
        result = system.chat(message)
        text = result.get("reply", "")
        sources = result.get("retrieval") or []
        if sources:
            # Retrieval results carry a score/chunk id/snippet, not a source URL,
            # so show that instead of a field that was never populated.
            source_lines = "\n\nRetrieved evidence:\n" + "\n".join(
                f"- chunk {s.get('chunk_id')} (score {s.get('score')}): {s.get('text', '')[:80].strip()}..."
                for s in sources[:4]
            )
            text += source_lines
        return text

    demo = gr.ChatInterface(
        fn=respond,
        title="JARVIS",
        description="From-scratch continual-learning research AI. The model and memory come from this project; no pretrained chat model is used.",
        examples=["Hello JARVIS", "What have you learned?", "What generation are you on?"],
    )
    demo.launch(share=share, show_error=True)
