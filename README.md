# JARVIS
## An Auditable Research Loop for Error-Driven Continual Learning in Small From-Scratch Language Models

**Author:** Aditya Bhatia  
**Project type:** Independent AI research  
**Research themes:** continual learning, recursive self-improvement, autonomous research systems, retrieval, evaluation, reproducibility, resource-aware architecture evolution

> JARVIS is a research platform for studying whether a small, from-scratch language-model system can identify capability failures, choose an appropriate intervention, learn from targeted information, evaluate whether the change actually helped, and preserve the result as an auditable experimental state.

This README is the engineering-facing companion to the JARVIS research program and ARRSI 2026 submission. It records the architecture, observed Generation-10 baseline, experimental history, recovery incidents, commands and code used during the Colab work, GitHub release workflow, GitHub Actions behavior, and the proposed V7 research protocol.

---

# Research integrity / claim status

The project deliberately separates **what has been executed** from **what is proposed**.

### Observed / executed

- A from-scratch transformer-style language model with persistent checkpoints.
- Explicit model-generation / lineage state.
- Architecture-evolution experiments.
- Continual training runs on CUDA / T4-class hardware.
- Public-web batch acquisition.
- Answer-time retrieval.
- Experiment and memory logging.
- A Gradio/Studio interface for interacting with the current checkpoint.
- Checkpoint hashing and release-artifact verification.
- Reproducibility packaging.
- Resource failures, including GPU-memory exhaustion for aggressive candidates.
- Retrieval-quality failures and user-visible routing problems.
- GitHub Actions workflows for bounded experiments and artifact generation.

### Proposed / under controlled investigation

- Error-driven targeted learning as the primary V7 intervention.
- Replay-based retention.
- Rigorous held-out transfer.
- Controlled retrieval-vs-parameter attribution.
- Factorial evaluation of parameter updates, retrieval, and tools.
- Resource-aware recursive architecture search.
- Autonomous end-to-end research.

**JARVIS does not claim frontier-model parity, general intelligence, or already-demonstrated open-ended recursive self-improvement.** The research question is whether the proposed loop can produce measurable, retained gains under controlled conditions.

---

# Why JARVIS exists

A conventional language-model workflow is approximately:

```text
choose architecture
    ↓
collect training data
    ↓
optimize parameters
    ↓
evaluate checkpoint
    ↓
deploy
```

JARVIS studies a different object:

```text
evaluate
    ↓
detect failure
    ↓
diagnose likely cause
    ↓
choose intervention
    ↓
acquire information / train / change routing
    ↓
evaluate target + regression
    ↓
accept or reject
    ↓
preserve provenance
    ↓
repeat
```

The central scientific problem is **attribution**. A system can appear to improve because retrieval supplied the missing fact, a deterministic tool solved the task, additional optimization fit the current corpus, the controller overfit a validation set, an architectural change altered capacity, or the answer improved while previous capabilities regressed.

JARVIS therefore treats the pathway to the answer as part of the result.

---

# ARRSI 2026 research framing

The ARRSI manuscript frames JARVIS as an **auditable research loop** rather than simply a chatbot or model-scale project.

The central question is:

> **Can repeated research actions produce auditable, transferable gains in the underlying system rather than merely better-looking outputs?**

The proposed scientific framing has four major pieces:

1. Parameterized learning must be separated from inference-time retrieval and tools.
2. Failures should map to explicit intervention families.
3. Candidates must be evaluated under controlled budgets and retention criteria.
4. Checkpoints, provenance, failures, and rejected candidates must remain inspectable.

The ARRSI manuscript explicitly distinguishes executed V6 evidence from proposed V7 hypothesis tests.

---

# Core system architecture

```text
                    ┌──────────────────────┐
                    │      Evaluation      │
                    │ target + regression  │
                    │ resources + latency  │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │ Failure diagnosis    │
                    │ knowledge             │
                    │ retrieval             │
                    │ reasoning             │
                    │ tool-routing          │
                    │ optimization          │
                    │ forgetting            │
                    │ infrastructure        │
                    └──────────┬───────────┘
                               ↓
          ┌────────────────────┼─────────────────────┐
          ↓                    ↓                     ↓
     acquire data        targeted learning      routing/tools
          │                    │                     │
          └────────────────────┼─────────────────────┘
                               ↓
                    candidate checkpoint
                               ↓
                    target + regression tests
                               ↓
                         accept / reject
                               ↓
                          lineage update
                               ↓
                             repeat
```

The observable answer can be represented as:

```text
y = F(x; M, R, T, C)
```

where:

- `M` = parameterized neural model
- `R` = retrieval subsystem
- `T` = deterministic tools
- `C` = controller / routing layer

This decomposition prevents a retrieved fact or calculator result from being misreported as evidence of parameterized learning.

---

# Archived Generation-10 baseline

The archived Gen-10 parent is the primary reproducibility baseline.

| Property | Recorded value |
|---|---:|
| Generation | **10** |
| Tracked parameters | **156,144,084** |
| Training steps | **3,520** |
| Best recorded evaluation loss | **0.11632630974054337** |
| Corpus characters | **4,643,495** |
| Ingested web pages | **40** |
| Memory records | **103** |
| Accepted architecture changes | **9** |
| Device | **CUDA / T4-class GPU** |
| Checkpoint | `checkpoints/generation_000010.pt` |

### Gen-10 architecture

```text
vocab_size      = 256
d_model         = 384
n_heads         = 8
n_layers        = 12
experts         = 7
top_k_experts   = 4
dropout         = 0.0
block_size      = 1280
```

These values describe one experimental trajectory; they are not normalized comparisons with unrelated models.

---

# Generation lineage

| Generation | Accepted action | Tracked parameters |
|---:|---|---:|
| 2 | `narrow_dropout` | 134,864,328 |
| 3 | `increase_top_k` | 134,864,328 |
| 4 | `add_expert` | 156,144,084 |
| 5 | `widen_context` | 156,144,084 |
| 6 | `narrow_dropout` | 156,144,084 |
| 7 | `widen_context` | 156,144,084 |
| 8 | `increase_top_k` | 156,144,084 |
| 9 | `widen_context` | 156,144,084 |
| 10 | `widen_context` | 156,144,084 |

The largest tracked-capacity increase came from adding an expert. Later accepted changes modified architecture without increasing the tracked parameter count.

---

# Information acquisition and retrieval

JARVIS has two deliberately distinct information paths.

## Batch acquisition

Public material can be collected into a versioned corpus for later training.

```text
public source
    ↓
query / acquisition
    ↓
source filtering
    ↓
content capture
    ↓
provenance record
    ↓
training corpus
```

The acquisition record should preserve:

```text
query
timestamp
source URL
source domain
content hash
filtering decision
downstream training identifier
```

## Answer-time retrieval

A current user question can trigger public-web retrieval. That changes the evidence available at inference time but does not by itself modify model parameters.

```text
web retrieval success
        ≠
parameterized learning success
```

A later parameter-only evaluation is required to establish transfer.

---

# Deterministic tools and routing

The intended routing model is:

```text
exact arithmetic      → deterministic computation
current information   → live public-web retrieval
conceptual task       → neural model ± evidence
code task             → controlled execution where appropriate
```

Tool routing and final answer correctness are separate measurements.

---

# Failure taxonomy

| Failure class | Example signal | Candidate intervention |
|---|---|---|
| Knowledge gap | Relevant fact absent | Acquire targeted public evidence |
| Retrieval failure | Irrelevant / duplicate evidence | Query rewrite / filtering |
| Reasoning failure | Evidence present, transformation wrong | Worked examples / decomposition |
| Tool-routing failure | Correct tool exists but is not selected | Routing-policy update |
| Optimization instability | Unstable loss / sensitivity | Schedule / optimizer intervention |
| Forgetting | New target improves while prior capability declines | Replay / retention pressure |
| Infrastructure failure | OOM / corrupted artifact / interruption | Resource-aware screening / recovery |

---

# V7 controlled experimental design

The proposed program uses matched, versioned comparisons.

| Condition | Intervention | Purpose |
|---|---|---|
| A | Generic continued training | Baseline continuation |
| B | Retrieval only | Measure information-access gains |
| C | Targeted learning, no replay | Measure targeted adaptation |
| D | Targeted learning + replay | Measure retention |
| E | Targeted learning + retrieval + tools | Measure integrated system |
| F | Bounded architecture mutation | Test whether architecture adds held-out value |

A candidate is retained only when:

```text
Δtarget ≥ δ
Δregression ≥ -τ
feasible(M') = 1
provenance(M') = 1
```

The ARRSI formulation also specifies a `2 × 2 × 2` factorial over parameter updates (`U`), retrieval (`R`), and tools (`T`).

| Cell | U | R | T | Interpretation |
|---:|---:|---:|---:|---|
| 1 | 0 | 0 | 0 | Model-only |
| 2 | 0 | 1 | 0 | Retrieval-only |
| 3 | 0 | 0 | 1 | Tool-only |
| 4 | 0 | 1 | 1 | Access + tool |
| 5 | 1 | 0 | 0 | Parameter-only |
| 6 | 1 | 1 | 0 | Parameter + retrieval |
| 7 | 1 | 0 | 1 | Parameter + tool |
| 8 | 1 | 1 | 1 | Integrated system |

---

# Benchmark structure and statistics

The intended benchmark separates:

```text
development
validation
regression
final test
```

Task families include:

```text
arithmetic
science concepts
general knowledge
reading comprehension
code reasoning
current-information QA
tool routing
```

The final-test set should remain inaccessible to acquisition and controller tuning.

For paired outcomes, the protocol calls for paired bootstrap confidence intervals and, where appropriate, exact, permutation, or McNemar-type tests for binary outcomes. Continuous metrics such as latency and loss should report paired estimates and dispersion across seeds.

Training loss remains an optimization diagnostic and is not a universal capability score.

---

# Reproducibility contract

A complete experiment is more than a `.pt` file.

```text
checkpoint
model configuration
checkpoint hash
controller version
source commit
corpus version
benchmark version
random seed
optimizer configuration
hardware description
web acquisition provenance
raw benchmark outputs
accept/reject decision
resource measurements
```

Rejected candidates, failures, and interrupted runs remain part of the scientific record.

---

# Repository layout

```text
jarvis-the-future/
├── jarvis/                    # Core implementation
├── tests/                     # Tests
├── colab/
│   └── JARVIS_Colab.ipynb     # Reproducibility / research notebook
├── .github/
│   └── workflows/
│       └── jarvis.yml         # Bounded GitHub Actions workflow
├── data/                      # Corpus, memory, provenance
├── generations/               # Generation metadata / lineage
├── workspace/                 # Persistent state
├── checkpoints/               # Learned checkpoints in runtime/local state
├── main.py                    # CLI entry point
├── config.json                # Configuration where present
├── requirements.txt           # Dependencies
└── README.md                  # This document
```

Large checkpoints belong in GitHub Releases or another persistent artifact store, not normal Git history.

---

# Core CLI operations used during the project

## Clone / install

```bash
git clone https://github.com/Aditya-0167/jarvis-the-future.git
cd jarvis-the-future
pip install -r requirements.txt
```

## Status

```bash
python main.py status
```

## Benchmark

```bash
python main.py benchmark
```

## Studio

```bash
python main.py studio
```

## Training

```bash
python main.py train --steps 800
python main.py train --steps 500
```

A 200-step run was considered as a smaller controlled budget:

```bash
python main.py train --steps 200
```

## Local-file ingestion

```bash
python main.py ingest-file /content/JARVIS_CONVERSATION_CURRICULUM.txt
```

## Profile transition

The notebook included:

```bash
python main.py profile colab
```

This creates a new generation/profile state and should not be used as a substitute for simply loading an archived parent checkpoint.

## Autonomous execution

```bash
python main.py autonomous --cycles 12
```

Longer exploratory autonomous loops were also used. Aggressive autonomous evolution encountered T4 GPU-memory limits and should not be treated as the default reproducibility path.

## Evolution

The repository includes bounded architecture evolution over discrete mutations. Candidate feasibility and held-out improvement matter more than raw size.

---

# Colab reproducibility notebook

Primary notebook:

```text
colab/JARVIS_Colab.ipynb
```

The intended workflow is:

```text
restore persistent state
    ↓
verify environment
    ↓
verify checkpoint
    ↓
run controlled experiment
    ↓
benchmark
    ↓
inspect state
    ↓
archive artifact
```

The notebook history also included early state-restore and crawl cells, including a Google Drive mount attempt that failed with credential propagation errors. Public-web crawling succeeded for some pages but was blocked for Wikipedia when `robots.txt` disallowed it.

---

# Gen-10 checkpoint verification

Recorded Gen-10 SHA-256:

```text
af7c0907329f43de0c11bd5d15aa52afce01430a9e8ec013474a675e778f85af
```

Verification code used:

```python
import hashlib
from pathlib import Path

p = Path("/content/jarvis_v6/checkpoints/generation_000010.pt")

h = hashlib.sha256()

with open(p, "rb") as f:
    for chunk in iter(
        lambda: f.read(4 * 1024 * 1024),
        b""
    ):
        h.update(chunk)

current_sha = h.hexdigest()

original_sha = (
    "af7c0907329f43de0c11bd5d15aa52afce01430a9e8ec013474a675e778f85af"
)

print("CURRENT SHA :", current_sha)
print("ORIGINAL SHA:", original_sha)

if current_sha == original_sha:
    print("✅ EXACT ORIGINAL GEN-10 CHECKPOINT")
else:
    print("⚠️ CHECKPOINT CHANGED")
```

Observed result:

```text
CURRENT SHA  = af7c0907329f43de0c11bd5d15aa52afce01430a9e8ec013474a675e778f85af
ORIGINAL SHA = af7c0907329f43de0c11bd5d15aa52afce01430a9e8ec013474a675e778f85af

✅ EXACT ORIGINAL GEN-10 CHECKPOINT
```

This established that the archived Gen-10 parent remained byte-identical after later experimental work.

---

# Checkpoint discovery / forensic inspection

The following diagnostic was used to enumerate runtime checkpoints and hashes:

```python
from pathlib import Path
import hashlib
import re
from datetime import datetime

print("=" * 80)
print("ALL JARVIS CHECKPOINTS IN /content")
print("=" * 80)

files = []

for p in Path("/content").rglob("generation_*.pt"):
    try:
        stat = p.stat()

        h = hashlib.sha256()

        with open(p, "rb") as f:
            for chunk in iter(
                lambda: f.read(4 * 1024 * 1024),
                b""
            ):
                h.update(chunk)

        m = re.search(r"generation_(\d+)", p.name)
        gen = int(m.group(1)) if m else -1

        files.append({
            "generation": gen,
            "path": str(p),
            "size_mb": stat.st_size / 1024**2,
            "mtime": datetime.fromtimestamp(
                stat.st_mtime
            ).strftime("%Y-%m-%d %H:%M:%S"),
            "sha256": h.hexdigest()
        })

    except Exception as e:
        print("ERROR:", p, e)

for x in sorted(
    files,
    key=lambda z: (z["generation"], z["mtime"])
):
    print()
    print("Generation :", x["generation"])
    print("Path       :", x["path"])
    print("Size       :", f"{x['size_mb']:.2f} MiB")
    print("Modified   :", x["mtime"])
    print("SHA-256    :", x["sha256"])

print("\nTOTAL CHECKPOINT FILES:", len(files))
```

The important runtime files discovered during the recovery session were:

```text
generation_000004.pt
generation_000010.pt
```

The Gen-10 copy matched the archived SHA.

---

# Checkpoint metadata inspection

The checkpoint was also loaded directly with PyTorch:

```python
import torch
from pathlib import Path

p = Path("/content/jarvis_v6/checkpoints/generation_000010.pt")

ckpt = torch.load(
    p,
    map_location="cpu",
    weights_only=False
)

print("Checkpoint loaded:", type(ckpt))
print("Keys:", ckpt.keys())
print("generation:", ckpt.get("generation"))
print("model_cfg:", ckpt.get("model_cfg"))
print("metrics:", ckpt.get("metrics"))
```

Verified Gen-10 configuration:

```text
vocab_size = 256
d_model = 384
n_heads = 8
n_layers = 12
experts = 7
top_k_experts = 4
dropout = 0.0
block_size = 1280
```

The state-dict tensor count was observed as:

```text
tensor count = 579
raw parameter count = 156,242,388
```

The project's tracked parameter count was:

```text
156,144,084
```

The difference was:

```text
98,304 = 256 × 384
```

which matched the vocabulary-size × model-width product and reflected the distinction between raw state-dict accounting and the project's tracked parameter metric.

---

# Gen-10 release recovery

The verified release path used in the Colab recovery was:

```text
https://github.com/Aditya-0167/jarvis-the-future/releases/download/gen10/JARVIS_GENERATION_10.zip
```

Verification sequence:

```text
exact release download
    ↓
download size
    ↓
ZIP SHA-256
    ↓
ZIP integrity test
    ↓
search for generation_000010.pt
    ↓
final archive check
```

Example verification code:

```python
import urllib.request
import hashlib
import zipfile
from pathlib import Path

URL = (
    "https://github.com/Aditya-0167/"
    "jarvis-the-future/releases/download/"
    "gen10/JARVIS_GENERATION_10.zip"
)

ZIP_PATH = Path(
    "/content/JARVIS_GENERATION_10_GITHUB.zip"
)

urllib.request.urlretrieve(URL, ZIP_PATH)

h = hashlib.sha256()

with open(ZIP_PATH, "rb") as f:
    for chunk in iter(
        lambda: f.read(4 * 1024 * 1024),
        b""
    ):
        h.update(chunk)

print("ZIP SHA-256:", h.hexdigest())

with zipfile.ZipFile(ZIP_PATH, "r") as z:
    bad = z.testzip()

    if bad:
        raise RuntimeError(
            f"ZIP FAILED INTEGRITY TEST: {bad}"
        )

    names = z.namelist()

checkpoint_entries = [
    n for n in names
    if n.endswith("generation_000010.pt")
]

print("Checkpoint entries:", checkpoint_entries)
```

The successful Gen-10 archive was approximately:

```text
552.89 MiB
```

and passed the ZIP integrity test.

---

# Release-artifact failure history

A previous release download reported:

```text
Downloaded: 417.64 MiB
```

but the ZIP integrity check failed with:

```text
Error -3 while decompressing data: invalid block type
```

That artifact was treated as **corrupt** and not trusted.

The later `gen10` release passed integrity verification. This incident is retained because artifact validation is part of reproducibility.

---

# Conversational adaptation experiment

A conversational curriculum was generated and ingested during an exploratory attempt.

The generated curriculum reported:

```text
examples = 9,920
characters = 818,580
```

It was ingested with:

```bash
python main.py ingest-file /content/JARVIS_CONVERSATION_CURRICULUM.txt
```

The ingestion output reported:

```text
added = 813,178 characters
```

This experiment is preserved as a failure-analysis branch, not as a validated improvement.

---

# 800-step conversational training

Command:

```bash
python main.py train --steps 800
```

Recorded result:

```text
loss_before = 4.40890645980835
loss_after  = 0.07960955301920573
steps       = 800
seconds     = 917.9333810806274
device      = cuda
parameters  = 156144084
```

The low loss was not treated as proof of improved conversation quality.

---

# 500-step conversational continuation

Command:

```bash
python main.py train --steps 500
```

Recorded result:

```text
loss_before = 4.354532877604167
loss_after  = 0.5820587277412415
steps       = 500
seconds     = 602.7904536724091
device      = cuda
parameters  = 156144084
```

The continuation was not accepted as a better conversational state.

---

# Conversational failure: retrieval contamination

During Studio testing, ordinary prompts such as:

```text
hey
hey dude
```

could surface unrelated learned conversation snippets as retrieval evidence, including material such as:

```text
today was awful
I finally solved it
```

The root cause was that conversational curriculum text had entered:

```text
data/corpus.txt
```

rather than remaining purely a parameter-learning dataset.

Undesired path:

```text
casual message
    ↓
local retrieval
    ↓
conversation-curriculum fragment
    ↓
generation
```

Intended path:

```text
casual message
    ↓
direct conversational generation
```

This was a major design lesson: training data and retrieval data must be separated.

---

# Conversation-corpus cleanup

Before modifying the active corpus, backups were created:

```text
data/corpus_BEFORE_CONVERSATION_CLEANUP.txt
data/memory_BEFORE_CONVERSATION_CLEANUP.jsonl
```

The active corpus cleanup removed sections originating from:

```text
JARVIS_CONVERSATION_CURRICULUM.txt
JARVIS_NATURAL_CONVERSATION_CURRICULUM.txt
```

A broad grep continued to find the old text because the backup file itself contained the old material. The active `data/corpus.txt` therefore had to be inspected separately.

---

# State / generation bookkeeping failure

During the conversational experiment, the adapted 156M checkpoint appeared as:

```text
generation_000004.pt
```

while the persistent status metadata could still describe the old Gen-4 / ~10.7M model.

A manual promotion created:

```text
generation_000011.pt
```

and attempted to synchronize:

```text
generation = 11
parent_generation = 10
adaptation = natural_conversation
```

However, Studio later demonstrated that other authoritative state still referred to the old Gen-4 lineage. The clean baseline was therefore restored to the verified Gen-10 parent rather than relying on manual renaming.

**Research rule:** never call a checkpoint a new generation merely by changing its filename; generation metadata, state, parent relationship, and checkpoint contents must agree.

---

# Exact state-synchronization code used during the experiment

The following shows the manual synchronization approach that was used to diagnose the state split. It is retained for historical completeness; it is **not** the preferred future mechanism.

```python
from pathlib import Path
import json
import shutil
import torch

ROOT = Path("/content/jarvis_v6")
STATE_PATH = ROOT / "workspace" / "state.json"
CKPT_PATH = ROOT / "checkpoints" / "generation_000011.pt"
BACKUP_PATH = ROOT / "workspace" / "state_before_gen11_sync.json"

if not STATE_PATH.exists():
    raise FileNotFoundError(f"Missing state file: {STATE_PATH}")

if not CKPT_PATH.exists():
    raise FileNotFoundError(f"Missing Gen-11 checkpoint: {CKPT_PATH}")

shutil.copy2(STATE_PATH, BACKUP_PATH)

state = json.loads(
    STATE_PATH.read_text(encoding="utf-8")
)

ckpt = torch.load(
    CKPT_PATH,
    map_location="cpu",
    weights_only=True
)

model_cfg = ckpt.get("model_cfg")

state["generation"] = 11
state["architecture"] = model_cfg
state["parameters"] = 156144084
state["parent_generation"] = 10
state["adaptation"] = "natural_conversation"

lineage = state.get("lineage")
if not isinstance(lineage, list):
    lineage = []

if not any(
    isinstance(x, dict) and x.get("generation") == 11
    for x in lineage
):
    lineage.append({
        "generation": 11,
        "parent_generation": 10,
        "action": "natural_conversation_adaptation",
        "accepted": True,
        "parameters": 156144084
    })

state["lineage"] = lineage

STATE_PATH.write_text(
    json.dumps(state, indent=2, ensure_ascii=False),
    encoding="utf-8"
)
```

This was followed by `python main.py status` to confirm whether the runtime agreed with the manually updated state. Studio later revealed that additional internal state remained inconsistent, motivating rollback.

---

# Gen-10 rollback / recovery

The verified Gen-10 release was tested before restoration. The rollback preserved the experimental Gen-11 candidate separately and restored the main checkpoint/state path to Gen-10.

The recovery sequence was:

```text
verify Gen-10 release
    ↓
preserve newer candidate separately
    ↓
restore checkpoints
    ↓
restore generations
    ↓
restore workspace
    ↓
inspect data separately
    ↓
verify Gen-10 SHA
```

The parent checkpoint remained untouched and reproducible.

---

# Final clean backup engineering

An early attempt to package everything recursively created an archive of approximately:

```text
3.9 GB
```

because backup directories contained duplicate copies of checkpoints and were then packaged again.

A corrected clean backup contained only one copy of each intended large checkpoint plus source/state files.

The resulting artifact was:

```text
ZIP size: 1106.15 MiB
ZIP INTEGRITY PASS
```

It contained:

```text
experimental_checkpoints/generation_000011_candidate.pt
jarvis_v6/checkpoints/generation_000010.pt
```

The ~1.1 GiB archive is the clean two-checkpoint safety backup created during the recovery session.

---

# Clean-backup code used

```python
from pathlib import Path
import shutil
import zipfile
import hashlib
import json
from google.colab import files

ROOT = Path("/content/jarvis_v6")
OUT = Path("/content/JARVIS_CLEAN_FINAL")
ZIP = Path("/content/JARVIS_CLEAN_FINAL.zip")

if OUT.exists():
    shutil.rmtree(OUT)

if ZIP.exists():
    ZIP.unlink()

OUT.mkdir()

src_out = OUT / "jarvis_v6"

for folder in ["jarvis", "tests", ".github"]:
    src = ROOT / folder
    if src.exists():
        shutil.copytree(src, src_out / folder)

for f in [
    "main.py",
    "README.md",
    "requirements.txt",
    "pyproject.toml",
]:
    src = ROOT / f
    if src.exists():
        (src_out / f).parent.mkdir(
            parents=True,
            exist_ok=True
        )
        shutil.copy2(src, src_out / f)

for folder in ["data", "generations", "workspace"]:
    src = ROOT / folder
    if src.exists():
        shutil.copytree(
            src,
            src_out / folder
        )

ckpt_out = src_out / "checkpoints"
ckpt_out.mkdir(parents=True)

gen10 = ROOT / "checkpoints" / "generation_000010.pt"

if gen10.exists():
    shutil.copy2(
        gen10,
        ckpt_out / gen10.name
    )

gen11 = Path("/content/JARVIS_GEN11_CANDIDATE.pt")

extra_out = OUT / "experimental_checkpoints"
extra_out.mkdir()

if gen11.exists():
    shutil.copy2(
        gen11,
        extra_out / "generation_000011_candidate.pt"
    )

def sha256(path):
    h = hashlib.sha256()

    with open(path, "rb") as f:
        for chunk in iter(
            lambda: f.read(4 * 1024 * 1024),
            b""
        ):
            h.update(chunk)

    return h.hexdigest()

manifest = {
    "artifact": "JARVIS clean research backup",
    "active_generation": 10,
    "gen10_checkpoint": None,
    "gen11_candidate": None
}

if gen10.exists():
    manifest["gen10_checkpoint"] = {
        "file": (
            "jarvis_v6/checkpoints/"
            "generation_000010.pt"
        ),
        "size_bytes": gen10.stat().st_size,
        "sha256": sha256(gen10)
    }

if gen11.exists():
    manifest["gen11_candidate"] = {
        "file": (
            "experimental_checkpoints/"
            "generation_000011_candidate.pt"
        ),
        "size_bytes": gen11.stat().st_size,
        "sha256": sha256(gen11)
    }

(
    OUT / "REPRODUCIBILITY_MANIFEST.json"
).write_text(
    json.dumps(manifest, indent=2),
    encoding="utf-8"
)

with zipfile.ZipFile(
    ZIP,
    "w",
    compression=zipfile.ZIP_DEFLATED,
    compresslevel=6
) as z:
    for p in OUT.rglob("*"):
        if p.is_file():
            z.write(
                p,
                p.relative_to(OUT)
            )

with zipfile.ZipFile(ZIP, "r") as z:
    bad = z.testzip()
    if bad:
        raise RuntimeError(
            f"ZIP integrity failure: {bad}"
        )

print("✅ ZIP integrity PASS")
files.download(str(ZIP))
```

---

# Studio / chat behavior lessons

The Studio displayed:

```text
Chatbot
Live system monitor
Live event log
```

The monitor is useful for research, but the following failure showed why the UI cannot be treated as the only authority: it briefly reported Gen-4 / ~10.7M parameters while a verified Gen-10 156M checkpoint existed.

The intended user-facing behavior is:

```text
casual conversation
    ↓
fast direct response

current factual question
    ↓
live public-web retrieval
    ↓
evidence-grounded response

exact arithmetic
    ↓
deterministic computation
```

Casual conversation should not trigger expensive retrieval merely because conversation examples exist in the corpus.

---

# Latency is a research metric

During the exploratory conversational branch, simple chat became much slower than expected because the system invoked unnecessary retrieval/training-state work.

Future evaluation should therefore measure:

```text
median end-to-end latency
p95 latency
retrieval latency
generation latency
tool latency
```

The objective is not just better answers but better answers through the intended route.

---

# GitHub Releases

Large checkpoint artifacts are distributed through GitHub Releases rather than normal Git history.

The repository used during this research:

```text
https://github.com/Aditya-0167/jarvis-the-future.git
```

The verified Gen-10 release asset was uploaded as a Release attachment rather than a regular repository file.

A later release was also used to host the larger clean research backup. The principle remains the same: keep multi-hundred-megabyte learned artifacts out of normal Git history and verify every downloaded archive before using it.

---

# GitHub Actions

GitHub Actions was used for bounded, reproducible research workflows and artifact generation.

## Automatic-run incident

GitHub failure emails were received even when no manual Colab experiment was being run. The cause was a repository workflow configured with automatic triggering, including a scheduled execution path.

A forensic note recorded that a scheduled run executed a command equivalent to:

```bash
python main.py autonomous --cycles 12
```

This was undesirable for a controlled research workflow because it consumed runner resources without a deliberate experiment decision.

## Intended policy

The bounded research workflow should be manual-only:

```yaml
name: JARVIS V6 bounded research run

on:
  workflow_dispatch:

concurrency:
  group: jarvis-bounded-research
  cancel-in-progress: false
```

Do not add `schedule:` unless unattended experiments are intentionally part of the study.

Do not add `push:` unless commit-triggered runs are intentional.

Do not add `workflow_run:` unless another workflow is deliberately supposed to launch this workflow.

---

# Manual-only GitHub Actions workflow used during repair

```yaml
name: JARVIS V6 bounded research run

# Manual-only research workflow.
# Start runs from GitHub -> Actions -> Run workflow.

on:
  workflow_dispatch:

concurrency:
  group: jarvis-bounded-research
  cancel-in-progress: false

permissions:
  contents: read

jobs:
  run:
    runs-on: ubuntu-latest
    timeout-minutes: 60

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then
            pip install -r requirements.txt
          fi

      # Keep the research command explicit and bounded.
      - name: Run bounded autonomous development
        run: |
          python main.py autonomous --cycles 12

      - name: Generate report
        if: always()
        run: |
          mkdir -p artifacts
          python main.py status > artifacts/status.txt || true
          python main.py benchmark > artifacts/benchmark.txt || true

      - name: Upload research logs
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: jarvis-v6-run
          path: artifacts/
          if-no-files-found: warn
```

The trigger policy and the autonomous command are separate controls: the workflow can contain a bounded autonomous experiment while still being manually launched.

---

# GitHub Actions diagnostic principle

When a failure email appears:

```text
GitHub → Actions → select run → inspect trigger/event
```

The relevant trigger may be:

```text
push
schedule
workflow_dispatch
workflow_run
release
```

The workflow YAML is the source of truth.

An automatic GitHub run is not evidence that JARVIS escaped the Colab environment; it means a hosted runner was started according to repository workflow configuration.

---

# Resource-aware architecture search

The main archived experiments used approximately:

```text
CUDA
T4-class GPU
~15 GB VRAM
```

Some larger candidates produced GPU-memory exhaustion.

The intended search logic is:

```text
architecture proposal
    ↓
resource screening
    ↓
feasible?
    ├── yes → evaluate
    └── no  → reject / archive failure
```

A candidate that cannot fit the available hardware envelope should not become a parent merely because its validation loss is lower.

---

# Provenance and contamination controls

Future experiments should record:

```text
source URL
query
timestamp
source domain
content hash
filtering result
training-task identifier
checkpoint hash
benchmark version
source commit
```

Contamination controls should include:

```text
exact overlap checks
near-duplicate checks
source-level separation
version locking
raw output archival
```

A final-test question should never silently enter training through a web-acquisition shortcut.

---

# Example V7 experiment manifest

```json
{
  "trial_id": "v7_00017",
  "parent_generation": 10,
  "parent_checkpoint_sha256": "stored hash",
  "controller_version": "controller_0.4",
  "benchmark_version": "bench_0.3",
  "target_capability": "science_qa",
  "diagnosis_distribution": {
    "knowledge": 0.55,
    "retrieval": 0.25,
    "reasoning": 0.20
  },
  "intervention": "targeted_learning",
  "compute_budget": 100,
  "seed": 17,
  "target_score_before": "stored value",
  "target_score_after": "stored value",
  "regression_before": "stored value",
  "regression_after": "stored value",
  "retrieval_sources": 5,
  "accepted": true,
  "reason": "retention criterion passed"
}
```

---

# Recovery checklist

Before continuing from any notebook/runtime:

```text
[ ] intended release identified
[ ] ZIP integrity verified
[ ] checkpoint file present
[ ] checkpoint SHA verified
[ ] parent generation identified
[ ] authoritative state identified
[ ] corpus version identified
[ ] benchmark version identified
[ ] environment recorded
[ ] source commit recorded
[ ] no unintended training process running
[ ] no scheduled GitHub workflow unexpectedly active
```

Only after these checks should a new intervention begin.

---

# Minimal clean workflow for future experiments

```text
1. Freeze parent
2. Hash parent
3. Freeze benchmark
4. Run baseline
5. Diagnose failure
6. Declare intervention + budget
7. Acquire permitted information if necessary
8. Train candidate
9. Evaluate target
10. Evaluate regression
11. Evaluate retrieval / routing / latency / memory
12. Accept or reject using predeclared rules
13. Archive checkpoint + provenance
14. Repeat
```

---

# What not to do

Do not:

```text
train indefinitely because loss is falling
```

Do not:

```text
rename a checkpoint to a higher generation without authoritative lineage updates
```

Do not:

```text
place training-only dialogue into the retrieval corpus
```

Do not:

```text
trust a large ZIP without integrity testing
```

Do not:

```text
overwrite the parent checkpoint
```

Do not:

```text
treat a retrieved answer as evidence of parameterized learning
```

Do not:

```text
let an autonomous workflow run on a schedule accidentally
```

Do not:

```text
package backup directories inside other backup directories
```

---

# Artifact map

The intended project package is:

```text
JARVIS/
├── research manuscript
├── ARRSI 2026 submission
├── 1–2 page project summary
├── GitHub source repository
├── Colab reproducibility notebook
├── Gen-10 parent checkpoint
├── experimental candidate checkpoints
├── benchmark / experimental results
├── logs
├── reproducibility manifest
├── short demo video
└── selected screenshots
```

The manuscript provides the scientific framing.

The repository provides implementation.

The checkpoint provides learned state.

The notebook provides a runnable reproduction path.

The logs provide the trail.

The manifest provides integrity and provenance.

The screenshots/demo provide a human-readable view of the system.

---

# Current research status

### Archived / observed

- Generation-10 model and checkpoint.
- Persistent model lineage.
- Architecture-evolution experiments.
- Continual training runs.
- Public-web ingestion.
- Answer-time retrieval.
- Benchmarking infrastructure.
- Resource-bound failures.
- Reproducibility and state-archival infrastructure.
- Conversational adaptation attempts and their negative results.
- GitHub release validation and recovery procedures.
- GitHub Actions trigger failures and manual-only repair.

### Proposed / under controlled investigation

- Error-driven targeted learning as the primary V7 intervention.
- Retention through replay.
- Rigorous held-out transfer.
- Controlled retrieval-versus-parameter attribution.
- Resource-aware recursive architecture search.
- Stronger routing evaluation.
- Repeated-seed experiments.

This distinction is intentional.

---

# Research lessons

The project deliberately preserves negative results.

### Loss did not equal capability

Lower training loss did not guarantee stronger user-visible behavior.

### Retrieval could be wrong

A system could find useful web evidence while also exposing irrelevant learned fragments.

### Training and retrieval data can interfere

Putting conversational training examples into the retrieval corpus caused unrelated examples to be surfaced during chat.

### More optimization was not automatically better

An 800-step conversational run reached a much lower recorded loss than the later 500-step continuation, but neither was accepted as evidence of broad conversational improvement.

### State bookkeeping is part of science

Generation numbering, parent relationships, checkpoint contents, and authoritative state must agree.

### Resource failures are data

OOM events reveal the feasible architecture frontier and should remain archived.

### Artifact integrity matters

A ZIP that downloads successfully is not necessarily a valid ZIP. Integrity must be tested before restoration.

### Negative results are useful

A rejected candidate, bad retrieval result, corrupt artifact, or failed workflow narrows the next research question.

---

# What the V6 evidence supports

The strongest defensible statement is:

> JARVIS demonstrates an executable, persistent research platform around a small from-scratch language model, including checkpoint lineage, public-web acquisition, answer-time retrieval, evaluation infrastructure, bounded architecture experimentation, and reproducibility controls. The archived trajectory also demonstrates important failure modes: optimization loss can diverge from user-visible capability, retrieval can surface irrelevant evidence, conversational training data can contaminate retrieval when the pipelines are not separated, and resource constraints can block candidate architectures. These observations motivate the controlled V7 program that tests whether error-driven intervention can produce measurable, retained gains under matched conditions.

The project does **not** claim that the current V6 trajectory proves recursive self-improvement of research ability.

---

# Research philosophy

> **Measure the pathway to improvement, not just the appearance of improvement.**

A successful experiment is not simply:

```text
"the model answered better"
```

It is:

```text
what failed
    ↓
what was diagnosed
    ↓
what changed
    ↓
what information was used
    ↓
how much compute was spent
    ↓
what improved
    ↓
what regressed
    ↓
why the candidate was accepted or rejected
```

That audit trail is the central design principle of JARVIS.

---

# References / related work

The ARRSI manuscript cites and builds on work including:

1. Vaswani et al. — *Attention Is All You Need*.
2. Lewis et al. — *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*.
3. Schick et al. — *Toolformer: Language Models Can Teach Themselves to Use Tools*.
4. Yao et al. — *ReAct: Synergizing Reasoning and Acting in Language Models*.
5. Madaan et al. — *Self-Refine: Iterative Refinement with Self-Feedback*.
6. Lu et al. — *The AI Scientist: Towards Fully Automated Open-Ended Scientific Discovery*.
7. Shi et al. — *Continual Learning of Large Language Models: A Comprehensive Survey*.
8. Wu et al. — *Continual Learning for Large Language Models: A Survey*.
9. Hoffmann et al. — *Training Compute-Optimal Large Language Models*.
10. Kaplan et al. — *Scaling Laws for Neural Language Models*.
11. Kirkpatrick et al. — *Overcoming Catastrophic Forgetting in Neural Networks*.
12. Shazeer et al. — *Sparsely-Gated Mixture-of-Experts Layer*.

See the manuscript for full bibliographic entries.

---

# Author

**Aditya Bhatia**  
Independent research in artificial intelligence, machine learning, language models, continual learning, AI systems, and AI security.

---
