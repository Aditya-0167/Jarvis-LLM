from pathlib import Path
import os
import tempfile
from jarvis.config import load_config
from jarvis.system import JarvisSystem


def test_growth_and_reload():
    with tempfile.TemporaryDirectory() as td:
        os.environ["JARVIS_ROOT"] = td
        cfg = load_config()
        cfg["training"]["batch_size"] = 2
        cfg["training"]["block_size"] = 64
        cfg["training"]["eval_batches"] = 1
        cfg["models"]["local"]["block_size"] = 64
        cfg["models"]["local"]["d_model"] = 48
        cfg["models"]["local"]["n_heads"] = 4
        cfg["models"]["local"]["n_layers"] = 2
        cfg["models"]["local"]["experts"] = 1
        cfg["models"]["local"]["top_k_experts"] = 1
        cfg["evolution"]["architecture_candidates"] = 1
        cfg["evolution"]["architecture_steps"] = 1
        cfg["evolution"]["steps_by_profile"]["local"] = 1
        s = JarvisSystem(cfg)
        s.bootstrap(steps=1)
        before = s.status()["generation"]
        result = s.evolve()
        after = s.status()["generation"]
        assert after == before + 1
        assert s.storage.latest_checkpoint() is not None
        model, model_cfg = s.storage.load_model()
        assert model_cfg["d_model"] > 0
        assert model is not None
    os.environ.pop("JARVIS_ROOT", None)
