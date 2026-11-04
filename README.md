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
| Knowledge only | 15.0% |
| Python only | 5.0% |

Across three backbones (DeepSeek-V3.2, GLM-5, Qwen3.5), DKG averages 93.3%.

`logs/` contains three runs per dataset for each configuration, with the full agent transcript and per-run verification output. `results/` contains the aggregated tables.

## What is not included

The measurement traces (about 350 MB) are not distributed with this repository because of their size. They are available from the authors on request.

The 166 source documents used to build the graph are third-party publications, standards, and vendor manuals, so they are not redistributed here. The extraction pipeline in `knowledge/extraction/` reproduces the graph from a corpus assembled according to the source categories described in the paper.

## Contact

Wenquan Zhou, An Wang, Jingqi Zhang, Yaoling Ding, Jiakun Li, Liehuang Zhu
