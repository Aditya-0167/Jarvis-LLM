from __future__ import annotations
import argparse
import json
from jarvis.config import load_config
from jarvis.system import JarvisSystem
from jarvis.cloud import make_manifest


def main():
    ap = argparse.ArgumentParser(description="JARVIS V4")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    p = sub.add_parser("bootstrap"); p.add_argument("--steps", type=int, default=None)
    p = sub.add_parser("train"); p.add_argument("--steps", type=int, default=None)
    sub.add_parser("evolve")
    p = sub.add_parser("autonomous"); p.add_argument("--cycles", type=int, default=None)
    sub.add_parser("status")
    sub.add_parser("benchmark")
    sub.add_parser("serve")
    p = sub.add_parser("ingest"); p.add_argument("url")
    p = sub.add_parser("ingest-file"); p.add_argument("path")
    p = sub.add_parser("crawl"); p.add_argument("seeds", nargs="*"); p.add_argument("--max-pages", type=int, default=None); p.add_argument("--depth", type=int, default=None)
    p = sub.add_parser("profile"); p.add_argument("name", choices=["local", "colab", "cloud"])
    p = sub.add_parser("chat"); p.add_argument("text", nargs="+")
    sub.add_parser("manifest")
    args = ap.parse_args()
    cfg = load_config()
    system = JarvisSystem(cfg)
    if args.cmd == "init": out = system.initialize()
    elif args.cmd == "bootstrap": out = system.bootstrap(args.steps)
    elif args.cmd == "train": out = system.train(args.steps)
    elif args.cmd == "evolve": out = system.evolve()
    elif args.cmd == "autonomous": out = system.autonomous_loop(args.cycles)
    elif args.cmd == "status": out = system.status()
    elif args.cmd == "benchmark": out = system.benchmark()
    elif args.cmd == "serve": system.serve(); return
    elif args.cmd == "ingest": out = system.ingest_url(args.url)
    elif args.cmd == "ingest-file": out = system.ingest_file(args.path)
    elif args.cmd == "crawl": out = system.crawl(args.seeds or None, args.max_pages, args.depth)
    elif args.cmd == "profile": out = system.set_profile(args.name)
    elif args.cmd == "chat": out = system.chat(" ".join(args.text))
    elif args.cmd == "manifest": out = make_manifest()
    else: raise SystemExit(2)
    if out is not None:
        print(json.dumps(out, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
