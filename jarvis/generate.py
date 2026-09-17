from __future__ import annotations
import torch


def generate(model, prompt: str, max_new_tokens: int = 300, temperature: float = 0.8, device: str = "cpu") -> str:
    model.to(device)
    model.eval()
    raw = list(prompt.encode("utf-8", errors="replace"))
    ids = torch.tensor(raw, dtype=torch.long, device=device)[None, :]
    with torch.no_grad():
        for _ in range(int(max_new_tokens)):
            x = ids[:, -model.block_size:]
            logits, _ = model(x)
            next_logits = logits[:, -1, :] / max(0.05, float(temperature))
            probs = torch.softmax(next_logits, dim=-1)
            next_id = torch.multinomial(probs, 1)
            ids = torch.cat([ids, next_id], dim=1)
    out = ids[0].detach().cpu().tolist()
    return bytes(int(max(0, min(255, x))) for x in out).decode("utf-8", errors="replace")
