from pathlib import Path
import zipfile
from jarvis.config import load_config

ROOT = Path(__file__).resolve().parents[1]
from jarvis.system import JarvisSystem


def test_bundle_contains_checkpoint(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cfg = load_config(ROOT / "config.json")
    s = JarvisSystem(cfg)
    s.initialize()
    out = s.bundle(str(tmp_path / 'bundle' / 'jarvis_state'))
    z = Path(out['bundle'])
    assert z.exists()
    with zipfile.ZipFile(z) as f:
        names = f.namelist()
        assert any(name.endswith('.pt') for name in names)
