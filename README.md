# DKG: Dual-Layer Knowledge Graph and LLM Co-Driven Framework for Automated Side-Channel Analysis

DKG automates non-profiled correlation power analysis (CPA) on symmetric block ciphers. Expert knowledge is organized into a two-layer knowledge graph: an upper **configuration space** describing how attack components compose, and a lower **diagnostic space** mapping failure symptoms to causes and remedial actions. Cross-layer edges translate diagnostic conclusions into configuration changes. An LLM agent queries this graph in a closed loop and drives a suite of SCA tools until the key is recovered.

## Graph

| Layer | Entity types | Entities | Relationships |
|---|---|---|---|
| Upper (configuration space) | 12 | 462 | 953 |
| Lower (diagnostic space) | 4 | 871 | 860 |
| **Total** | **16** | **1,334** | **1,813** |

The graph is stored in two JSON files and loaded into Neo4j:

- `knowledge/upper_layer/round1/final_upper.json`
- `knowledge/lower_layer/round1/final_lower.json`

It was constructed from 166 technical documents by the three-step extraction pipeline in `knowledge/extraction/`: Locate & Rewrite, Triple Extraction, and Knowledge Fusion.

## Repository layout

```
eval/                         success evaluation and ablation aggregation
agent/
  main.py                     agent loop, planning, tool dispatch
  tools/                      11 tools: CPA (AES/DES/SM4), alignment, denoising,
                              key search, verification, correlation analysis,
                              graph retrieval, Python execution
knowledge/
  ontology/                   upper and lower layer schema definitions
  extraction/                 three-step extraction pipeline and prompts
  graph_db/                   Neo4j initialization and query
  sources/extract*.py         document parsing for corpus construction
  upper_layer/, lower_layer/  constructed graph (JSON)
results/                      result tables for all experiments (CSV/JSON/Markdown)
logs/                         per-run agent logs for the reported experiments
```

## Setup

```bash
pip install -r requirements.txt
cp config.example.yaml config.yaml      # then fill in API key and Neo4j password
```

Neo4j 5.x is required. Load the graph:

```bash
python knowledge/graph_db/init_graph.py
```

Place the trace datasets under `data/traces/` following the layout used in `agent/main.py`.

## Running

```bash
python agent/main.py
```

The agent takes a task description (cipher, device class, leakage type), retrieves configuration and diagnostic knowledge from the graph, and iterates until the key verifies.

## Results

End-to-end key-recovery success rate over eight datasets (AES, DES, SM4 on smartcards, FPGA, and MCUs), ten runs per dataset:

| Configuration | SR |
|---|---|
| DKG (DeepSeek-V3.2) | 97.5% |
| ReAct-RAG | 68.8% |
| Tools only | 56.2% |
| Python only | 17.5% |
| Knowledge only | 10.0% |

Across three backbones (DeepSeek-V3.2, GLM-5, Qwen3.5), DKG averages 93.3%.

Python only and Knowledge only runs were reviewed manually: a run counts only if the full key was computed by CPA code on the traces and printed. The manual verdicts are listed with reasons in `eval/final_ablation.py`. The other configurations use the automatic evaluator in `eval/re_evaluate_qwen_sessions.py`.

`results/final_ablation_per_run.csv` gives the verdict and efficiency metrics for every run behind the ablation numbers (80 per configuration). `logs/` contains, for each configuration and dataset, the three earliest runs by start time that produced a log, with the full agent transcript and per-run verification output. `results/` contains the aggregated tables.

To re-evaluate the published sample:

```bash
DKG_LOG_LAYOUT=artifact python eval/final_ablation.py
```

This writes `results/sample_final_ablation_*.csv`. Totals on the sample differ from the paper, which uses all runs.

## What is not included

The measurement traces (about 350 MB) are not distributed with this repository because of their size. They are available from the authors on request.

The 166 source documents used to build the graph are third-party publications, standards, and vendor manuals, so they are not redistributed here. The extraction pipeline in `knowledge/extraction/` reproduces the graph from a corpus assembled according to the source categories described in the paper.

## Contact

Wenquan Zhou, An Wang, Jingqi Zhang, Yaoling Ding, Jiakun Li, Liehuang Zhu
