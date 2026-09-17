# JARVIS V6 — From-Scratch Continual-Learning Research AI

JARVIS V6 is a research system for training and evolving a small neural language model from random initialization. It combines a byte-level causal transformer, persistent data and memory, public-web ingestion, evaluation, architecture search, model scaling, checkpoint lineage, and interactive chat.

No pretrained language-model weights are required. The neural weights are created inside the project and trained by its own training loop.

## 0. Quick start

For the first interactive session, run:

```bash
python main.py studio
```

The browser page has a chat panel and a live monitor. Talk to the current JARVIS checkpoint first. Then use the **Train**, **Evolve**, **Learn from public web**, or **Autonomous run** buttons to watch the system change while it keeps the UI responsive.

For Colab, open `colab/JARVIS_Colab.ipynb`. Seed the persistent state from a GitHub artifact, verify the GPU, launch Studio, and chat first. After the first interactive check, close/interrupt the Studio process and continue with the GPU training cells, or use the Studio controls for bounded runs.

## 1. Core loop

JARVIS treats development as a measurable loop rather than an open-ended promise:

```text
persistent corpus
      ↓
train from current checkpoint
      ↓
evaluate on held-out data
      ↓
propose candidate architecture changes
      ↓
train candidate variants
      ↓
compare against parent
      ↓
accept only if the candidate clears the configured margin
      ↓
write checkpoint + experiment + lineage
      ↓
refresh data / choose next action
      ↺
```

The current implementation can automatically choose between additional training, public-web refresh, architecture evolution, and benchmarking. The policy adapts its action weights from measured validation-loss improvement.

## 2. Neural architecture

The model is a decoder-style transformer with:

- a byte vocabulary of 256 values, so there is no pretrained tokenizer;
- token embeddings with tied output weights;
- RMS normalization;
- rotary position embeddings;
- causal scaled dot-product attention;
- SwiGLU-style feed-forward experts;
- a routed expert bank with configurable top-k routing;
- configurable width, depth, context length, expert count, routing k, and dropout.

A new model is randomly initialized. When a model grows, compatible parent tensors are copied into overlapping regions of the child. Newly created dimensions, layers, or experts remain newly initialized. This gives the system a concrete lineage from one generation to the next.

The local, Colab, and cloud profiles are configuration targets rather than guarantees about hardware. Actual runtime speed depends on the machine that executes the code.

## 3. Continual learning and persistent state

The project persists four main kinds of state:

1. **Corpus** — text plus source provenance.
2. **Memory** — interactions and development events.
3. **Experiments** — candidate architecture trials with before/after metrics.
4. **Checkpoints** — model weights, model configuration, generation, and metrics.

By default these directories are:

```text
data/
checkpoints/
generations/
workspace/
```

Set `JARVIS_ROOT` to move all of these directories to persistent storage such as a mounted Google Drive directory.

Example:

```bash
export JARVIS_ROOT=/content/drive/MyDrive/JARVIS_STATE
```

On Windows PowerShell:

```powershell
$env:JARVIS_ROOT = "C:\Users\YOUR_NAME\Documents\JARVIS_STATE"
```

This keeps the code in the repository while keeping learned state outside the Git repository.

## 4. Public-web learning

JARVIS can ingest public HTTP/HTTPS pages. The crawler:

- uses a descriptive user-agent;
- checks robots.txt for automatic crawling;
- rate-limits requests;
- records the source URL;
- deduplicates source/content fingerprints;
- stays on seed hosts by default;
- does not use credentials or cookies;
- does not bypass authentication or access controls.

Single-page ingestion:

```bash
python main.py ingest https://example.org/page
```

Bounded crawling:

```bash
python main.py crawl
```

A web refresh is data collection. It does not by itself update the model weights; the autonomous loop can follow a successful web refresh with a training step.

## 5. Self-development and architecture growth

The evolution engine creates candidate architectures by mutating dimensions such as:

- number of layers;
- model width;
- number of experts;
- top-k routing;
- context length;
- dropout.

Each candidate is trained briefly and measured on the same evaluation procedure. A candidate is accepted only if its validation loss improves beyond `accept_margin`.

Every trial is written to:

```text
workspace/experiments.jsonl
```

and each accepted generation gets a record under:

```text
generations/generation_XXXXXX/result.json
```

The actual learned AI state is the corresponding:

```text
checkpoints/generation_XXXXXX.pt
```

This is the important distinction when moving between machines: **a new generation usually means a new checkpoint, not a new Python source file.** The source code stays in Git; the learned model state moves as checkpoints.

### Scaling to a larger profile

```bash
python main.py profile colab
```

This creates a larger model from the current model by transferring all compatible tensors and randomly initializing new capacity. It increments the generation and writes a new checkpoint.

For a stronger environment, the same mechanism can target the `cloud` profile:

```bash
python main.py profile cloud
```

The software cannot create compute or credentials by itself. An authorized environment must provide the hardware.

## 6. GitHub logs vs the learned AI

GitHub Actions is a remote worker, not the permanent home of the learned model. Its console log shows what JARVIS did on that runner. The learned model is stored in checkpoint files such as `checkpoints/generation_000001.pt`.

V6 also creates a portable `jarvis_v6_state.zip` artifact containing the checkpoint plus the data, generations, and workspace needed to resume. This fixes the earlier confusion where a run artifact could contain `LATEST.json` metadata without the actual `.pt` learned weights being obvious.

In other words:

```text
GitHub source code -> runner executes JARVIS -> logs + learned checkpoint
                                            ↓
                                   portable state bundle
                                            ↓
                                      Colab / GPU
```

## 7. Live Studio and chat

For an interactive browser interface that shows chat and a live runtime monitor in the same page:

```bash
python main.py studio
```

The Studio lets you chat with the current checkpoint first. On the same page you can start a bounded training run, evolution trial, public-web refresh, or autonomous run. The monitor shows the current generation, step/loss, device, checkpoint, corpus size, and recent runtime events. Training runs in a background worker so the chat interface stays available.

The system's autonomous freedom is deliberately limited to the configured research sandbox: public web pages, user-provided data, model/architecture experimentation, benchmarking, memory, checkpointing, and authorized compute. It does not attempt to obtain credentials, private data, unauthorized compute, bypass access controls, or attack third-party systems.

## 8. Autonomous mode

Run a bounded autonomous research sequence:

```bash
python main.py autonomous --cycles 20
```

Each cycle can:

- train;
- refresh public data and then perform a small follow-up training run;
- test architecture candidates;
- benchmark;
- update the internal action policy;
- persist the result.

The loop is intentionally resumable. If a runtime disappears, start it again with the same `JARVIS_ROOT`; the saved checkpoint and workspace are reused.

## 9. Chat

Command-line chat:

```bash
python main.py chat "Hello JARVIS"
```

Browser chat on a local machine:

```bash
python main.py serve
```

then open:

```text
http://127.0.0.1:8765
```

Colab-friendly chat UI:

```bash
python main.py gradio
```

The Gradio interface exposes the conversational part of JARVIS without exposing the training/evolution control endpoints. It can show a temporary share URL when `share=True` is used by the launcher.

The chat stack uses:

```text
recent dialogue
      +
lexical retrieval from learned corpus
      +
current from-scratch neural generator
```

At early generations the neural model can produce repetitive or low-quality language. This is an expected property of a small randomly initialized model trained from limited data, not evidence of a frontier conversational model.

## 10. Data and evaluation

Training uses the persistent corpus as a next-byte prediction task. The trainer can also mix a small synthetic copy curriculum with the corpus.

The evaluator reports:

- held-out cross-entropy;
- perplexity;
- corpus size;
- device.

Run:

```bash
python main.py benchmark
```

Generate an HTML report:

```bash
python main.py report
```

For meaningful comparisons, keep the evaluation procedure fixed while changing one experimental factor at a time. Expanding the training corpus can change the data distribution, so reports should record corpus size and source counts alongside model metrics.

## 10. Checkpoints, manifests, and bundles

List checkpoint metadata:

```bash
python main.py manifest
```

Create a portable state bundle containing `data`, `checkpoints`, `generations`, and `workspace`:

```bash
python main.py bundle
```

The resulting ZIP can be moved to another authorized machine or uploaded into Colab. The bundle is state, not source code.

## 11. Google Colab workflow

The repository includes:

```text
colab/JARVIS_Colab.ipynb
```

The notebook is designed to keep source code and learned state separate:

- clone the repository into `/content`;
- mount Google Drive;
- set `JARVIS_ROOT` to a folder in Drive;
- optionally upload a GitHub Actions artifact or JARVIS state bundle;
- resume from the saved checkpoint;
- switch to the Colab profile;
- train/evolve/autonomously develop;
- launch the Gradio chat interface from the notebook.

This is important because managed Colab runtimes are temporary. Persistent state should live in Drive or another durable storage system rather than only on `/content`.

## 12. GitHub Actions

The workflow under `.github/workflows/` provides a bounded, headless research run. It:

1. checks out the source;
2. installs dependencies;
3. restores prior workspace/checkpoint cache when available;
4. runs a bounded autonomous sequence;
5. writes a research report;
6. uploads the resulting checkpoint/state artifacts.

GitHub Actions does **not** display the chat UI. It is the batch research layer. Downloaded checkpoints can then be continued in Colab or another authorized runtime.

## 13. Repository layout

```text
JARVIS_v5/
├── jarvis/
│   ├── model.py          # from-scratch neural architecture
│   ├── trainer.py        # training, evaluation, AMP
│   ├── evolution.py      # architecture mutation and selection
│   ├── autonomy.py       # experiment records and next-action suggestions
│   ├── policy.py         # adaptive action-selection policy
│   ├── crawler.py        # bounded public-web crawler
│   ├── web.py            # single-page web ingestion
│   ├── data.py           # corpus and curriculum
│   ├── memory.py         # persistent memory
│   ├── retrieval.py      # lexical retrieval
│   ├── chat.py           # conversational orchestration
│   ├── generate.py       # neural text generation
│   ├── benchmarks.py     # evaluation metrics
│   ├── storage.py        # durable state/checkpoints/bundles
│   ├── cloud.py          # checkpoint manifest helpers
│   ├── report.py         # research report
│   ├── server.py         # local browser/API interface
│   ├── gradio_app.py     # Colab-friendly chat UI
│   ├── system.py         # system orchestration
│   ├── config.py         # configuration loader
│   └── main.py           # package entry points
├── colab/
│   └── JARVIS_Colab.ipynb
├── .github/workflows/
│   └── jarvis.yml
├── tests/
├── config.json
├── requirements.txt
└── README.md
```

## 14. Reproducibility and boundaries

The system is designed to be auditable. It stores model configurations, measured scores, lineage, and source provenance. Development happens inside an explicit action space and an evaluation gate.

The repository does not implement credential theft, authentication bypass, destructive exploitation, uncontrolled propagation to third-party systems, or private-data collection. Internet learning means bounded collection of permitted public web content.

The project is a research prototype. It should be evaluated by its reproducible measurements and observed behavior rather than by labels such as AGI, consciousness, or unlimited autonomy.
