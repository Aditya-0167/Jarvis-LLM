from __future__ import annotations
import math
import time
import torch
from .data import Curriculum
from .benchmarks import byte_loss


class Trainer:
    def __init__(self, cfg, storage, device=None):
        self.cfg = cfg
        self.storage = storage
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        torch.set_num_threads(max(1, min(torch.get_num_threads(), 16)))
        self.curriculum = Curriculum(cfg.get("seed", 1701))
        self.amp_enabled = bool(cfg.get("training", {}).get("amp", True)) and self.device.startswith("cuda")
        self.amp_dtype = torch.bfloat16 if self.amp_enabled and torch.cuda.is_bf16_supported() else torch.float16

    def evaluate(self, model, batches=None):
        batches = batches or self.cfg["training"]["eval_batches"]
        return byte_loss(model, self.storage.corpus, "val", batches, self.device)

    def _curriculum_batch(self, batch_size: int, block_size: int):
        rows = self.curriculum.sample(batch_size, max(8, min(64, block_size // 2)))
        xs, ys = [], []
        for raw in rows:
            data = torch.tensor(list(raw), dtype=torch.long)
            if len(data) < block_size + 1:
                data = torch.cat([data, torch.full((block_size + 1 - len(data),), 32, dtype=torch.long)])
            max_start = max(0, len(data) - block_size - 1)
            start = self.curriculum.rng.randrange(max_start + 1) if max_start else 0
            xs.append(data[start:start + block_size])
            ys.append(data[start + 1:start + block_size + 1])
        return torch.stack(xs), torch.stack(ys)

    def train_model(self, model, model_cfg, steps, progress=None):
        model.to(self.device)
        opt = torch.optim.AdamW(
            model.parameters(),
            lr=float(self.cfg["training"]["learning_rate"]),
            weight_decay=float(self.cfg["training"]["weight_decay"]),
            betas=(0.9, 0.95)
        )
        before = self.evaluate(model)
        started = time.time()
        model.train()
        total = max(1, int(steps))
        warmup = max(1, int(self.cfg["training"].get("lr_warmup_steps", 10)))
        for step in range(total):
            x, y = self.storage.corpus.batch(self.cfg["training"]["batch_size"], "train")
            mix = float(self.cfg["training"].get("curriculum_mix", 0.0))
            if mix > 0 and torch.rand(()) < mix:
                x, y = self._curriculum_batch(self.cfg["training"]["batch_size"], int(model_cfg["block_size"]))
            x, y = x.to(self.device), y.to(self.device)
            opt.zero_grad(set_to_none=True)
            if self.amp_enabled:
                with torch.autocast(device_type="cuda", dtype=self.amp_dtype):
                    _, loss = model(x, y)
            else:
                _, loss = model(x, y)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), float(self.cfg["training"]["grad_clip"]))
            if step < warmup:
                scale = (step + 1) / warmup
                for group in opt.param_groups:
                    group["lr"] = float(self.cfg["training"]["learning_rate"]) * scale
            else:
                schedule_progress = (step - warmup) / max(1, total - warmup)
                lr = float(self.cfg["training"]["learning_rate"]) * (0.15 + 0.85 * 0.5 * (1 + math.cos(math.pi * schedule_progress)))
                for group in opt.param_groups:
                    group["lr"] = lr
            opt.step()
            current_loss = float(loss.detach())
            if progress is not None:
                progress({"step": step + 1, "total": total, "loss": current_loss})
            if (step + 1) % max(1, min(25, total)) == 0:
                print(f"    step {step+1}/{total} loss={current_loss:.4f}")
        after = self.evaluate(model)
        return {
            "loss_before": before,
            "loss_after": after,
            "steps": total,
            "seconds": time.time() - started,
            "device": self.device,
            "parameters": sum(p.numel() for p in model.parameters())
        }

    def train(self, model, model_cfg, steps=None, progress=None):
        return self.train_model(model, model_cfg, steps or self.cfg["training"]["steps_per_cycle"], progress=progress)
