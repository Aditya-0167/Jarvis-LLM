from __future__ import annotations
import re
from .generate import generate

WEB_HINTS = re.compile(r"\b(latest|today|current|recent|news|search|web|internet|who is|what is)\b", re.I)


def compose_context(retrieved: list[dict], memories: list[dict], max_chars: int = 7600) -> str:
    parts = []
    for item in retrieved:
        parts.append(f"[SOURCE CHUNK]\n{item['text']}")
    for item in memories:
        parts.append(f"[MEMORY]\n{item}")
    return "\n\n".join(parts)[:max_chars]


def _recent_dialogue(memories: list[dict], max_turns: int = 6) -> str:
    turns = []
    for row in memories[-max_turns:]:
        if row.get("kind") == "interaction":
            turns.append(f"User: {row.get('user','')}\nJARVIS: {row.get('reply','')}")
    return "\n".join(turns)


def answer(system, user_text: str):
    retrieved = system.retriever.search(user_text, limit=6)
    memories = system.storage.memory.search(user_text, limit=4)
    recent = _recent_dialogue(system.storage.memory.recent(30))
    context = compose_context(retrieved, memories)

    prompt = (
        "JARVIS is a from-scratch research AI. Answer the user conversationally. "
        "Use learned evidence when relevant. Do not invent facts. If evidence is missing, say so.\n\n"
        f"RECENT DIALOGUE:\n{recent}\n\n"
        f"RETRIEVED CONTEXT:\n{context}\n\n"
        f"USER: {user_text}\nJARVIS:"
    )
    model_reply = generate(system.model_for_chat(), prompt, 220, 0.72, system.trainer.device)
    model_reply = model_reply.split("USER:", 1)[0].split("JARVIS:", 1)[-1].strip()
    bad = (
        len(model_reply) < 2
        or "RECENT DIALOGUE:" in model_reply
        or "RETRIEVED CONTEXT:" in model_reply
        or "JARVIS is a from-scratch research AI" in model_reply[:160]
    )
    if bad:
        state = system.storage.load_state()
        if re.search(r"\b(hello|hi|hey)\b", user_text, re.I):
            model_reply = "Hello. I am JARVIS, a from-scratch continual-learning research prototype."
        elif retrieved:
            model_reply = "I found relevant learned evidence. The strongest matching passage is: " + retrieved[0]["text"][:600]
        else:
            model_reply = (
                f"I am JARVIS generation {state['generation']} with {state['parameters']:,} parameters. "
                "I do not have enough learned evidence to answer that reliably yet."
            )

    return {
        "reply": model_reply,
        "retrieval": retrieved,
        "memory": memories,
        "web_suggested": bool(WEB_HINTS.search(user_text)),
        "generation": system.storage.load_state()["generation"],
    }
