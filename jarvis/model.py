from __future__ import annotations
import copy
import math
from dataclasses import asdict, dataclass
import torch
import torch.nn as nn
import torch.nn.functional as F


@dataclass
class ModelConfig:
    vocab_size: int = 256
    d_model: int = 192
    n_heads: int = 6
    n_layers: int = 6
    experts: int = 2
    top_k_experts: int = 2
    dropout: float = 0.05
    block_size: int = 384

    def to_dict(self):
        return asdict(self)


class RMSNorm(nn.Module):
    def __init__(self, d: int, eps: float = 1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(d))
        self.eps = eps

    def forward(self, x):
        return x * torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + self.eps) * self.weight


def rotate_half(x):
    d = x.shape[-1]
    x1 = x[..., : d // 2]
    x2 = x[..., d // 2:]
    return torch.cat((-x2, x1), dim=-1)


class RotaryEmbedding(nn.Module):
    def __init__(self, dim: int, base: float = 10000.0):
        super().__init__()
        inv = 1.0 / (base ** (torch.arange(0, dim, 2).float() / dim))
        self.register_buffer("inv_freq", inv, persistent=False)

    def forward(self, x):
        # x: [B, H, T, D]
        t = x.shape[-2]
        pos = torch.arange(t, device=x.device, dtype=self.inv_freq.dtype)
        freqs = torch.outer(pos, self.inv_freq)
        emb = torch.cat([freqs, freqs], dim=-1)
        cos, sin = emb.cos()[None, None, :, :], emb.sin()[None, None, :, :]
        return x * cos + rotate_half(x) * sin


class Expert(nn.Module):
    def __init__(self, d_model: int):
        super().__init__()
        hidden = 4 * d_model
        self.w1 = nn.Linear(d_model, hidden)
        self.w2 = nn.Linear(d_model, hidden)
        self.w3 = nn.Linear(hidden, d_model)

    def forward(self, x):
        return self.w3(F.silu(self.w1(x)) * self.w2(x))


class ExpertBank(nn.Module):
    def __init__(self, d_model: int, experts: int, top_k: int = 2):
        super().__init__()
        self.router = nn.Linear(d_model, experts)
        self.experts = nn.ModuleList([Expert(d_model) for _ in range(experts)])
        self.top_k = max(1, min(int(top_k), int(experts)))

    def forward(self, x):
        logits = self.router(x)
        weights = torch.softmax(logits, dim=-1)
        if self.top_k < len(self.experts):
            vals, idx = torch.topk(weights, self.top_k, dim=-1)
            mask = torch.zeros_like(weights).scatter_(-1, idx, 1.0)
            weights = weights * mask
            weights = weights / weights.sum(-1, keepdim=True).clamp_min(1e-8)
        y = torch.zeros_like(x)
        for i, expert in enumerate(self.experts):
            w = weights[..., i:i+1]
            if torch.any(w != 0):
                y = y + w * expert(x)
        return y


class CausalBlock(nn.Module):
    def __init__(self, cfg: ModelConfig):
        super().__init__()
        if cfg.d_model % cfg.n_heads:
            raise ValueError("d_model must be divisible by n_heads")
        self.norm1 = RMSNorm(cfg.d_model)
        self.qkv = nn.Linear(cfg.d_model, 3 * cfg.d_model, bias=False)
        self.out = nn.Linear(cfg.d_model, cfg.d_model, bias=False)
        self.rotary = RotaryEmbedding(cfg.d_model // cfg.n_heads)
        self.norm2 = RMSNorm(cfg.d_model)
        self.experts = ExpertBank(cfg.d_model, cfg.experts, cfg.top_k_experts)
        self.drop = nn.Dropout(cfg.dropout)
        self.n_heads = cfg.n_heads
        self.head_dim = cfg.d_model // cfg.n_heads

    def forward(self, x):
        b, t, c = x.shape
        h = self.norm1(x)
        q, k, v = self.qkv(h).chunk(3, dim=-1)
        q = q.view(b, t, self.n_heads, self.head_dim).transpose(1, 2)
        k = k.view(b, t, self.n_heads, self.head_dim).transpose(1, 2)
        v = v.view(b, t, self.n_heads, self.head_dim).transpose(1, 2)
        q = self.rotary(q)
        k = self.rotary(k)
        attn = F.scaled_dot_product_attention(q, k, v, is_causal=True)
        attn = attn.transpose(1, 2).contiguous().view(b, t, c)
        x = x + self.drop(self.out(attn))
        x = x + self.drop(self.experts(self.norm2(x)))
        return x


class JarvisModel(nn.Module):
    def __init__(self, cfg: dict | ModelConfig):
        super().__init__()
        if isinstance(cfg, dict):
            cfg = ModelConfig(**cfg)
        self.cfg = copy.deepcopy(cfg)
        self.vocab_size = cfg.vocab_size
        self.block_size = cfg.block_size
        self.tok = nn.Embedding(cfg.vocab_size, cfg.d_model)
        self.blocks = nn.ModuleList([CausalBlock(cfg) for _ in range(cfg.n_layers)])
        self.norm = RMSNorm(cfg.d_model)
        self.head = nn.Linear(cfg.d_model, cfg.vocab_size, bias=False)
        self.head.weight = self.tok.weight
        self.apply(self._init)
        # A slightly scaled output projection is friendlier for a fresh LM.
        nn.init.normal_(self.tok.weight, mean=0.0, std=0.02)

    @staticmethod
    def _init(module):
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, idx, targets=None):
        b, t = idx.shape
        if t > self.block_size:
            idx = idx[:, -self.block_size:]
            t = idx.shape[1]
            if targets is not None:
                targets = targets[:, -self.block_size:]
        x = self.tok(idx)
        for block in self.blocks:
            x = block(x)
        logits = self.head(self.norm(x))
        loss = None
        if targets is not None:
            loss = F.cross_entropy(logits.reshape(-1, logits.size(-1)), targets.reshape(-1))
        return logits, loss


def make_model(cfg: dict) -> JarvisModel:
    return JarvisModel(cfg)


def parameter_count(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters())


def _copy_tensor_overlap(dst, src):
    if dst.ndim != src.ndim:
        return False
    slices = tuple(slice(0, min(a, b)) for a, b in zip(dst.shape, src.shape))
    with torch.no_grad():
        dst[slices].copy_(src[slices])
    return True


def transfer_compatible(base: JarvisModel, target: JarvisModel) -> JarvisModel:
    with torch.no_grad():
        src = base.state_dict()
        dst = target.state_dict()
        for key, value in src.items():
            if key in dst:
                _copy_tensor_overlap(dst[key], value)
        target.load_state_dict(dst, strict=False)
    return target
