from pathlib import Path
import sys

ROOT = Path(__file__).parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_core_imports():
    from jarvis.config import load_config
    from jarvis.model import make_model, parameter_count

    cfg = load_config(ROOT / "config.json")
    model = make_model(cfg["models"]["local"])
    assert parameter_count(model) > 0


def test_files_present():
    for rel in ["main.py", "README.md", "config.json", "requirements.txt"]:
        assert (ROOT / rel).exists()


def test_training_crosses_warmup_without_progress_crash(tmp_path, monkeypatch):
    import torch
    from jarvis.config import load_config
    from jarvis.system import JarvisSystem

    monkeypatch.chdir(tmp_path)
    cfg = load_config(ROOT / "config.json")
    cfg["training"]["batch_size"] = 2
    cfg["training"]["block_size"] = 32
    cfg["training"]["eval_batches"] = 1
    cfg["training"]["lr_warmup_steps"] = 10
    cfg["models"]["local"] = {
        "vocab_size": 256,
        "d_model": 32,
        "n_heads": 4,
        "n_layers": 2,
        "experts": 1,
        "top_k_experts": 1,
        "dropout": 0.05,
        "block_size": 32,
    }
    s = JarvisSystem(cfg)
    s.initialize()
    result = s.train(steps=12)
    assert result["steps"] == 12
    assert torch.isfinite(torch.tensor(result["loss_after"]))
