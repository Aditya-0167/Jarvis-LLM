from pathlib import Path
from jarvis.config import load_config

ROOT = Path(__file__).resolve().parents[1]
from jarvis.system import JarvisSystem
from jarvis.studio import StudioController


def test_studio_controller_and_runtime_events(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cfg = load_config(ROOT / "config.json")
    s = JarvisSystem(cfg)
    s.initialize()
    ctl = StudioController(s)
    status, log = ctl.status_view()
    assert status['generation'] == 0
    assert isinstance(log, str)
