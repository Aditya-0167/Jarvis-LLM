from __future__ import annotations
import math
import torch


def byte_loss(model, corpus, split="val", batches=8, device="cpu"):
    model.to(device)
    model.eval()
    losses = []
    with torch.no_grad():
        for _ in range(int(batches)):
            x, y = corpus.batch(8, split)
            x, y = x.to(device), y.to(device)
            _, loss = model(x, y)
            losses.append(float(loss))
    model.train()
    return sum(losses) / max(1, len(losses))


def report(model, corpus, eval_batches, device):
    loss = byte_loss(model, corpus, "val", eval_batches, device)
    return {
        "validation_cross_entropy": loss,
        "perplexity": math.exp(min(20.0, loss)),
        "bytes_in_corpus": len(corpus.bytes()),
        "device": device,
        "note": "Lower validation loss/perplexity is better. Compare only across comparable data/model conditions."
    }
