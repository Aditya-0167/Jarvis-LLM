# JARVIS — From-Scratch Continual-Learning Research System

> **JARVIS is a research platform for studying error-driven continual learning and recursive system improvement in a small, from-scratch language model.**

JARVIS is not presented as a frontier-scale language model or as evidence of general intelligence. The project is built to make a harder question measurable:

> **Can a small neural system identify where it fails, choose an appropriate intervention, learn from targeted information, evaluate whether the change actually helped, and preserve the result as an auditable experimental state?**

The project combines a from-scratch neural language model with persistent checkpoints, lineage tracking, public-web information acquisition, answer-time retrieval, deterministic tools, benchmarking, failure diagnosis, and bounded architecture search.

---

## Research at a glance

### Archived Generation-10 baseline

| Property | Recorded value |
|---|---:|
| Generation | **10** |
| Tracked parameters | **156,144,084** |
| Training steps | **3,520** |
| Best recorded evaluation loss | **0.1163263097** |
| Corpus characters | **4,643,495** |
| Ingested web pages | **40** |
| Persistent memory records | **103** |
| Accepted architecture changes | **9** |
| Hardware | **CUDA / T4-class GPU** |
| Checkpoint | `checkpoints/generation_000010.pt` |

The Generation-10 configuration is:

```text
vocab_size      = 256
d_model         = 384
attention heads = 8
layers          = 12
experts         = 7
top-k experts   = 4
dropout         = 0.0
block size      = 1280
```

These values describe one experimental trajectory; they are not intended as normalized comparisons with unrelated models.

---

# What I built

JARVIS is a full experimental system rather than only a model checkpoint.

### 1. From-scratch neural model

The neural core is trained inside the project rather than starting from a pretrained language-model checkpoint.

The model uses a transformer-style architecture with mixture-of-experts routing and persistent learned checkpoints.

### 2. Persistent model lineage

Each generation is represented as a checkpoint plus machine-readable state describing configuration, lineage, experiments, and decisions.

A candidate is intended to be treated as a child of a parent checkpoint rather than silently overwriting the parent.

### 3. Public-web information acquisition

JARVIS can collect permitted public information into a versioned local corpus.

Acquisition records can preserve source URLs, timestamps, queries, content hashes, filtering decisions, and downstream training identifiers.

### 4. Answer-time retrieval

JARVIS can also retrieve public information at inference time.

This is deliberately separated from training:

```text
retrieval → changes the evidence available to the response
training  → changes neural parameters
```

A correct answer obtained from web retrieval is therefore not automatically counted as evidence that the neural model learned the fact.

### 5. Tool and task routing

Different tasks can use different computational paths.

Examples include:

```text
exact arithmetic      → deterministic calculator/tool
current information   → live public-web retrieval
conceptual questions  → model and/or evidence
code tasks            → controlled execution where appropriate
```

The research goal is to measure whether routing decisions improve reliability without confusing system-level gains with neural learning.

### 6. Benchmarking and evaluation

JARVIS is designed around held-out evaluation, regression testing, retrieval evaluation, routing measurements, latency, resource use, and experiment provenance.

Training loss is treated as an optimization diagnostic—not as a universal measure of capability.

### 7. Bounded architecture evolution

The V6 system experimented with discrete architecture mutations including expert/routing/context changes.

Candidates are supposed to be evaluated against a parent under a resource budget.

A larger model is not automatically treated as a better model.

---

# Research question

The central research question is:

> **Can a relatively small, from-scratch language-model system identify capability failures, acquire relevant permitted information, learn from targeted material, evaluate improvement on unseen tasks, and retain beneficial changes over repeated iterations?**

This leads to several separable hypotheses:

- targeted learning can outperform generic continuation under matched budgets;
- retrieval can improve factual performance without changing parameters;
- useful learning should improve the target while limiting regression;
- architecture changes should be accepted only when feasible and beneficial;
- versioned held-out evaluation is more informative than raw training loss when the data distribution changes.

---

# The research loop

The intended V7 research loop is:

```text
            ┌──────────────────────┐
            │      Evaluate        │
            │  fixed benchmark     │
            └──────────┬───────────┘
                       ↓
            ┌──────────────────────┐
            │ Diagnose the failure │
            └──────────┬───────────┘
                       ↓
       ┌───────────────┼────────────────┐
       ↓               ↓                ↓
   Acquire data     Train target     Improve routing
       │               │                │
       └───────────────┼────────────────┘
                       ↓
            ┌──────────────────────┐
            │ Evaluate candidate   │
            │ target + regression  │
            └──────────┬───────────┘
                       ↓
              Accept / reject
                       ↓
              Preserve lineage
                       ↓
                    Repeat
```

The important part is **attribution**.

The same visible answer can arise from:

```text
M = neural model
R = retrieval
T = deterministic tools
C = controller / routing
```

and can be represented conceptually as:

```text
y = F(x; M, R, T, C)
```

A research result is stronger when the experiment can distinguish which component caused the observed gain.

---

# What the archived experiments taught me

The first trajectory produced a deliberately mixed result.

The infrastructure was able to preserve successive generations, run training, perform architecture experiments, ingest public information, and maintain machine-readable state.

At the same time, several failures became central research observations:

### Loss did not equal capability

Low optimization loss did not guarantee reliable user-visible behavior.

### Retrieval could be wrong

A system could retrieve useful information while also exposing irrelevant material.

### Tools can confound apparent learning

A deterministic tool can make a task easier without improving the neural model.

### Bigger candidates can hit the hardware boundary

Some architecture candidates exceeded the available GPU memory budget.

These failures changed the research direction from:

> “How large can JARVIS become?”

toward:

> **“How efficiently can JARVIS determine what should change next?”**

That is the motivation for the V7 controlled-learning program.

---

# V7 experimental program

The intended controlled comparison includes:

| Condition | Intervention | Purpose |
|---|---|---|
| A | Generic continued training | Baseline continuation |
| B | Retrieval only | Measure information-access gains |
| C | Targeted learning, no replay | Measure targeted adaptation |
| D | Targeted learning + replay | Measure retention |
| E | Targeted learning + retrieval + tools | Measure integrated system behavior |
| F | Bounded architecture mutation | Measure whether capacity changes add held-out value |

The central rule is that candidates should be evaluated on:

```text
target improvement
+
regression / retention
+
resource feasibility
+
provenance completeness
```

rather than accepted merely because training loss decreased.

---

# Evaluation design

The planned benchmark separates:

- arithmetic
- science concepts
- general knowledge
- reading comprehension
- code reasoning
- current-information QA
- tool routing

The evaluation design separates:

```text
development
validation
regression
final test
```

The final-test partition should remain untouched during intervention selection.

For paired before/after outcomes, the research protocol calls for paired analyses such as bootstrap confidence intervals and, where appropriate, exact/permutation or McNemar-type tests for binary outcomes.

---

# Reproducibility

A complete JARVIS run is more than a `.pt` file.

The reproducible experimental state includes:

```text
model checkpoint
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
raw evaluation outputs
accept/reject decision
```

The parent checkpoint should remain available after a candidate is created.

### Research artifacts

The project can be distributed as:

```text
source code
research manuscript
Colab reproduction notebook
checkpoint release
experimental state / logs
benchmark outputs
screenshots and demo material
```

Large learned checkpoints are distributed through GitHub Releases rather than normal repository files.

---

# Reproducing the archived baseline

## Colab

Open:

`colab/JARVIS_Colab.ipynb`

The notebook is designed to:

1. restore the persistent state / release artifact;
2. verify the checkpoint and environment;
3. launch the JARVIS interface;
4. reproduce controlled training/evaluation operations.

Large `.pt` files are intentionally kept outside normal Git history.

## Local

```bash
git clone https://github.com/Aditya-0167/Jarvis-LM.git
cd Jarvis-LM
pip install -r requirements.txt
python main.py studio
```

The archived Generation-10 checkpoint can be obtained from the linked GitHub Release artifact.

---

# GitHub Actions

GitHub Actions is used for **bounded, reproducible research runs and artifact generation**.

## Manual-trigger policy

The main bounded research workflow should be **manual-trigger only**:

```yaml
on:
  workflow_dispatch:
```

There should be **no `schedule:` trigger** on this research workflow.

This matters because a `schedule:` event is an automatic cron trigger. Your recent GitHub run history showed:

```text
Triggered via schedule
```

and the run executed:

```text
python main.py autonomous --cycles 12
```

before being cancelled after roughly 20 minutes.

The intended workflow is:

```text
You decide to run experiment
        ↓
GitHub Actions → Run workflow
        ↓
bounded experiment
        ↓
logs + metrics + artifacts
```

not:

```text
clock
  ↓
unattended autonomous experiment
  ↓
runner consumption
  ↓
failure email
```

## How to fix the current workflow

Open:

**GitHub → `Jarvis-LM` → `.github/workflows/jarvis.yml`**

At the top, replace the trigger section with:

```yaml
name: JARVIS V6 bounded research run

on:
  workflow_dispatch:

concurrency:
  group: jarvis-bounded-research
  cancel-in-progress: false
```

Delete the existing:

```yaml
schedule:
  - cron: ...
```

Do not leave both `schedule:` and `workflow_dispatch:` if you want strictly manual execution.

Commit the change to the **`main`** branch.

Then:

**Actions → JARVIS V6 bounded research run → Run workflow**

GitHub's documentation confirms that `schedule` creates time-based runs, while `workflow_dispatch` creates the manual **Run workflow** control. citeturn659951search0turn659951search5

### Important

A workflow can still have multiple trigger types if you explicitly configure them. The fix is specifically to remove the automatic schedule from this research workflow.

If another workflow such as `JARVIS Continuous Development` also contains `schedule:`, repeat the same change there or disable that workflow from the Actions page. GitHub provides a Disable workflow control for this. citeturn659951search2turn659951search9

---

# Current research status

### Archived / observed

- Generation-10 model and checkpoint
- persistent model lineage
- architecture evolution experiments
- continual training runs
- public-web ingestion
- answer-time retrieval
- benchmarking infrastructure
- resource-bound failures
- reproducibility and state-archival infrastructure

### Proposed / under controlled investigation

- error-driven targeted learning as the primary V7 intervention
- retention through replay
- rigorous held-out transfer
- controlled retrieval-versus-parameter attribution
- resource-aware recursive architecture search
- stronger routing evaluation
- repeated-seed experiments

This distinction is intentional.

The project does **not** claim that the current system demonstrates general intelligence, human-level reasoning, or open-ended recursive self-improvement.

---

# Known limitations

The current system remains constrained by:

- small training-data scale relative to modern foundation models;
- a relatively small byte-level vocabulary;
- limited benchmark maturity in the archived V6 phase;
- changing training distributions across earlier experiments;
- search-provider and source-quality dependence;
- limited GPU memory on T4-class hardware;
- potential retrieval contamination if training and retrieval corpora are not separated;
- the need for stronger held-out and repeated-seed evaluation.

These limitations are part of the research record rather than hidden from it.

---

# Research integrity

JARVIS treats negative results as useful evidence.

A failed experiment can reveal:

```text
wrong diagnosis
weak retrieval
poor target data
catastrophic regression
optimization instability
resource infeasibility
routing error
incomplete provenance
```

Rejected candidates and interrupted runs should remain archived rather than deleted.

The purpose of the system is therefore not “autonomy for its own sake.”

The purpose is **measurable, auditable adaptation**.

---

# Project structure

```text
Jarvis-LM/
├── jarvis/                    # Core research implementation
├── tests/                     # Tests
├── colab/
│   └── JARVIS_Colab.ipynb     # Reproducibility notebook
├── .github/
│   └── workflows/
│       └── jarvis.yml         # Bounded research workflow
├── data/                      # Corpus / memory / provenance
├── generations/               # Generation metadata
├── workspace/                 # Persistent experiment state
├── README.md
├── config.json
├── main.py
└── requirements.txt
```

---

# Research artifacts

### Manuscript

**JARVIS: A Controlled Framework for Error-Driven Continual Learning and Recursive Self-Improvement**

The manuscript documents the archived Generation-10 baseline and specifies a controlled V7 research program.

### Checkpoint

`generation_000010.pt`

The archived Generation-10 checkpoint is the reproducibility parent for the proposed V7 experiments.

### Colab

`colab/JARVIS_Colab.ipynb`

### Release artifacts

Large checkpoints and complete learned-state bundles belong in GitHub Releases.

Do not place multi-hundred-megabyte `.pt` checkpoints directly into normal Git history.

---

# Why this project exists

Most model-development pipelines optimize a fixed objective and then evaluate the result.

JARVIS asks a different question:

> **Can the system itself become better at deciding what it needs to change next?**

That requires more than a larger model.

It requires:

```text
failure detection
→ diagnosis
→ information acquisition
→ targeted intervention
→ evaluation
→ retention / rejection
→ provenance
→ another iteration
```

JARVIS is an attempt to build that loop as an inspectable research instrument.

---

## Author

**Aditya Bhatia**

Independent research in AI, machine learning, language models, continual learning, and AI systems security.

---

## Research philosophy

> **Measure the pathway to improvement, not just the appearance of improvement.**
