[Common wrapper]
You are revising a Task skill, not directly solving the task.
Use the provided Meta schema as class-level guidance.
Your goal is to improve the Task skill for this task while preserving useful existing structure.

[Meta schema block]
Category: orchestration-delegation
Semantic intent: Coordinate ordered external actions or substeps where sequence and dependency management matter.
Emphasize:
- constraint extraction before action
- ordering across dependent steps / systems
- state handoff between stages or tools
- fail-safe finalization and side-effect awareness
Avoid:
- eager direct completion without dependency checks
- reviewer-only prompts that lack execution choreography
- over-abstract synthesis that ignores operational order
Expected good fit:
- scheduling / delegation workflows
- multi-system action coordination
- tasks where one substep creates constraints for the next
Expected bad fit:
- static artifact-only tasks
- deep scientific analysis pipelines
Hypothesized primary failure modes:
- unavailable in prompt-bank-v0.1; use task-local evidence instead
Meta schema seed guidance:
You are revising a skill for an orchestration/delegation task.
Optimize the skill as a coordination protocol, not just as a content-generation prompt.

Prioritize:
1. extracting constraints before taking actions,
2. preserving correct action order across dependent systems or stages,
3. making state handoffs explicit,
4. preventing side effects from happening before prerequisites are checked.

If the task is failing, first strengthen dependency ordering and handoff logic before adding more general reasoning guidance.

[Task context block]
Task name: taxonomy-tree-merge
Task summary: I need to unify product category taxonomies from three different e-commerce platforms (Amazon, Facebook, and Google Shopping). Each platform has its own way of classifying products, and we want to create one unified category catalog that works for all of them such that I can use one single category system for downstream works like tracking metrics of product category from multiple platforms! The available data files are in /root/data/ as your input:
Task constraints:
- seed schema prior: methodology-guardrail
- verifier mode: abstention-and-fit-check
- workflow topology: branching-abstention-aware
- tool surface regime: tool-light
- primary pattern: inversion
- annotation confidence: high
- secondary patterns: reviewer, pipeline
Task output requirements:
- verifier note: abstention-and-fit-check
- current skill count: 1

[Current Task skill block]
Current Task skill:
## hierarchical-taxonomy-clustering
---
name: hierarchical-taxonomy-clustering
description: Build unified multi-level category taxonomy from hierarchical product category paths from any e-commerce companies using embedding-based recursive clustering with intelligent category naming via weighted word frequency analysis.
---

# Hierarchical Taxonomy Clustering

Create a unified multi-level taxonomy from hierarchical category paths by clustering similar paths and automatically generating meaningful category names.

## Problem

Given category paths from multiple sources (e.g., "electronics -> computers -> laptops"), create a unified taxonomy that groups similar paths across sources, generates meaningful category names, and produces a clean N-level hierarchy (typically 5 levels). The unified category taxonomy could be used to do analysis or metric tracking on products from different platform.

## Methodology

1. **Hierarchical Weighting**: Convert paths to embeddings with exponentially decaying weights (Level i gets weight 0.6^(i-1)) to signify the importance of category granularity
2. **Recursive Clustering**: Hierarchically cluster at each level (10-20 clusters at L1, 3-20 at L2-L5) using cosine distance
3. **Intelligent Naming**: Generate category names via weighted word frequency + lemmatization + bundle word logic
4. **Quality Control**: Exclude all ancestor words (parent, grandparent, etc.), avoid ancestor path duplicates, clean special characters

## Output

DataFrame with added columns:
- `unified_level_1`: Top-level category (e.g., "electronic | device")
- `unified_level_2`: Second-level category (e.g., "computer | laptop")
- `unified_level_3` through `unified_level_N`: Deeper levels

Category names use ` | ` separator, max 5 words, covering 70%+ of records in each cluster.

## Installation

```bash
pip install pandas numpy scipy sentence-transformers nltk tqdm
python -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4')"
```

## 4-Step Pipeline

### Step 1: Load, Standardize, Filter and Merge (`step1_preprocessing_and_merge.py`)
- **Input**: List of (DataFrame, source_name) tuples, each of the  with `category_path` column
- **Process**: Per-source deduplication, text cleaning (remove &/,/'/-/quotes,'and' or "&", "," and so on, lemmatize words as nouns), normalize delimiter to ` > `, depth filtering, prefix removal, then merge all sources. source_level should reflect the processed version of the source level name
- **Output**: Merged DataFrame with `category_path`, `source`, `depth`, `source_level_1` through `source_level_N`

### Step 2: Weighted Embeddings (`step2_weighted_embedding_generation.py`)
- **Input**: DataFrame from Step 1
- **Output**: Numpy embedding matrix (n_records × 384)
- Weights: L1=1.0, L2=0.6, L3=0.36, L4=0.216, L5=0.1296 (exponential decay 0.6^(n-1))
- **Performance**: For ~10,000 records, expect 2-5 minutes. Progress bar will show encoding status.

### Step 3: Recursive Clustering (`step3_recursive_clustering_naming.py`)
- **Input**: DataFrame + embeddings from Step 2
- **Output**: Assignments dict {index → {level_1: ..., level_5: ...}}
- Average linkage + cosine distance, 10-20 clusters at L1, 3-20 at L2-L5
- Word-based naming: weighted frequency + lemmatization + coverage ≥70%
- **Performance**: For ~10,000 records, expect 1-3 minutes for hierarchical clustering and naming. Be patient - the system is working through recursive levels.

### Step 4: Export Results (`step4_result_assignments.py`)
- **Input**: DataFrame + assignments from Step 3
- **Output**:
  - `unified_taxonomy_full.csv` - all records with unified categories
  - `unified_taxonomy_hierarchy.csv` - unique taxonomy structure

## Usage

**Use `scripts/pipeline.py` to run the complete 4-step workflow.**

See `scripts/pipeline.py` for:
- Complete implementation of all 4 steps
- Example code for processing multiple sources
- Command-line interface
- Individual step usage (for advanced control)

[Evidence block]
No Skills: `40.8`
With Skills: `0`
Delta: `-40.8`
Failure summary: fit checks, assumption control, and premature-commitment avoidance dominate
Competing schema note: No prior round-0 pair evidence available.

[Output contract block]
Return YAML with fields:
revised_task_skill, change_summary{keep/add/remove/sharpen}, rationale

```yaml
revised_task_skill: |
  ...
change_summary:
  keep:
    - ...
  add:
    - ...
  remove:
    - ...
  sharpen:
    - ...
rationale: |
  ...
```
