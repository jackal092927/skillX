# SkillsBench-Lite Eval Harness v0.1

## Status

Draft design memo written from the live discussion in `#cont-marc`.

## Purpose

This document captures a lightweight alternative evaluation lane for SkillX / SkillsBench work.

The goal is **not** to replace the official Docker-based SkillsBench pipeline. The goal is to add a second evaluation substrate that is:

- lighter than Docker
- more host-adjacent / semi-real
- still controlled and resettable
- suitable for measuring whether a Skill enhancement algorithm is genuinely improving skill quality, rather than merely overfitting to a containerized benchmark world

---

## 1. Problem Framing

Current SkillsBench-style evaluation typically relies on Docker because Docker gives:

1. reproducible environment setup
2. isolation from the host machine
3. task-level resetability
4. packaged dependencies

These are strong advantages for benchmark-faithful evaluation.

However, for SkillX and a general Skills Enhancement Framework, Docker also introduces a potential confound:

> We may end up measuring whether the enhanced skill performs better in a Dockerized benchmark world, rather than whether the enhancement improves the skill as a reusable artifact across lighter and more realistic execution settings.

So the design question is:

> Can we preserve task-level control and cleanup while replacing the full Docker substrate with a lighter-weight execution harness?

The proposed answer is **SkillsBench-Lite**.

---

## 2. High-Level Design

### 2.1 Core Idea

For each benchmark episode:

- create a fresh temporary task workspace
- copy in the required task fixtures
- run the agent/skill system inside that workspace
- restrict commands, paths, environment variables, and optionally network
- capture traces, file diffs, side effects, and task outputs
- score with the same or equivalent task scorer
- clean up automatically unless debugging is requested

This is a **task sandbox**, not a full container.

### 2.2 Design Objective

SkillsBench-Lite should answer four questions:

1. Does the enhancement still improve task performance outside Docker?
2. Does it reduce unnecessary actions or side effects?
3. Does it make the skill more portable across host-adjacent environments?
4. Does it expose behavioral signals that Docker-only evaluation obscures?

---

## 3. Architecture

```text
                    ┌──────────────────────────────┐
                    │      SkillsBench Task Set    │
                    │   (same tasks / same scorer) │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │      SkillsBench-Lite Runner │
                    │      (episode orchestrator)  │
                    └───────┬──────────┬───────────┘
                            │          │
                ┌───────────▼───┐   ┌──▼────────────────┐
                │ Episode Setup │   │ Policy Sandbox     │
                │               │   │                    │
                │ - temp dir    │   │ - path allowlist   │
                │ - task assets │   │ - cmd allowlist    │
                │ - env config  │   │ - net policy       │
                │ - overlay opt │   │ - resource limits  │
                └───────┬───────┘   └──────┬─────────────┘
                        │                  │
                        └────────┬─────────┘
                                 │
                     ┌───────────▼───────────┐
                     │  Agent + Skill System  │
                     │  (Skill X / enhanced)  │
                     └───────────┬───────────┘
                                 │
              ┌──────────────────▼──────────────────┐
              │ Tool Execution / Local Host Tools   │
              │ python / bash / pytest / scripts    │
              │ (restricted, logged, controllable)  │
              └──────────────────┬──────────────────┘
                                 │
                 ┌───────────────▼────────────────┐
                 │ Trace + Diff + Metrics Capture │
                 │                                │
                 │ - tool calls                   │
                 │ - stdout/stderr                │
                 │ - file diffs                   │
                 │ - latency/cost                 │
                 │ - side effects                 │
                 └───────────────┬────────────────┘
                                 │
                     ┌───────────▼───────────┐
                     │  Task Scorer / Eval    │
                     │  (same benchmark logic)│
                     └────────────────────────┘
```

---

## 4. Two-Lane Evaluation Strategy

The design assumes two complementary evaluation lanes.

### Lane A — Docker-Faithful Benchmark

Use the original SkillsBench Docker protocol.

**Purpose:**
- compare against official or existing baselines
- preserve benchmark-faithful execution
- maintain reviewer-defensible evaluation conditions

### Lane B — SkillsBench-Lite

Use temp workspace + restricted process sandbox instead of Docker.

**Purpose:**
- test whether gains transfer beyond Docker
- inspect action efficiency and environmental cleanliness
- detect overfitting to containerized benchmark worlds

### Recommended Positioning

Do **not** replace Lane A with Lane B.

Instead:
- Lane A = official benchmark lane
- Lane B = supplementary transfer / portability / behavioral lane

---

## 5. Docker vs Lite Protocol Comparison

| Dimension | SkillsBench Docker | SkillsBench-Lite |
|---|---|---|
| Main purpose | benchmark-faithful evaluation | lightweight host-adjacent evaluation |
| Execution substrate | Docker container | temp workspace + restricted launcher |
| Isolation | container isolation | policy-based process/file/env isolation |
| Resetability | high | high if cleanup is strict |
| Reproducibility | high | medium-high |
| Startup overhead | medium to high | low |
| Host realism | medium-low | medium |
| Dependency packaging | strong | weaker unless pre-bundled |
| Side-effect visibility | moderate | strong |
| Portability signal | weak | strong |
| Reviewer safety | high | medium |

### Interpretation

Docker is still better for strict, public benchmark comparability.

Lite is better for answering:
- whether enhancements generalize to non-container settings
- whether skills become cleaner, shorter-path, less contaminating artifacts

---

## 6. Scope for v0.1

### 6.1 What v0.1 should support

Only a limited task subset.

Recommended first subset:

1. file/text transformation tasks
2. light local script execution tasks
3. light multi-step tool orchestration tasks

### 6.2 What v0.1 should explicitly exclude

- complex service startup
- database-heavy tasks
- package installation as part of task logic
- browser-heavy or GUI-heavy tasks
- high-privilege system operations
- tasks requiring strong OS-level isolation guarantees

### 6.3 Why scope should be narrow

v0.1 is meant to validate the harness concept, not to fully replace Docker or fully cover all SkillsBench tasks.

---

## 7. Minimal Runtime Design

### 7.1 Episode Workspace Layout

For each task run, create a fresh workspace such as:

```text
/tmp/skillsbench_lite/
  run_20260402_001/
    task_001/
      input/
      work/
      output/
      logs/
      home/
```

### 7.2 Directory Semantics

- `input/` = copied task fixtures
- `work/` = agent working directory
- `output/` = expected result location
- `logs/` = stdout/stderr/trace metadata
- `home/` = fake isolated HOME

### 7.3 Cleanup Policy

- default: delete run directory after success
- keep failed runs by default for debugging
- optional flag: keep all runs

---

## 8. Minimal Policy Sandbox

The Lite harness should not attempt to be a full security system in v0.1.
It should implement a **minimal execution policy layer**.

### 8.1 Path Restriction

Allowed roots should be limited to:
- current run workspace
- explicitly declared read-only benchmark assets

Denied by default:
- user home
- personal project directories
- ssh/secrets/config paths

### 8.2 Command Allowlist

Initial allowlist can be small, e.g.:
- `python`
- `python3`
- `bash`
- `sh`
- `pytest`
- `ls`
- `cat`
- `grep`
- `sed`
- `awk`
- `echo`
- `cp`
- `mv`

Task-specific expansion should be possible later.

### 8.3 Environment Sanitization

The launcher should explicitly control environment variables.

Recommended defaults:
- set `HOME` to fake run home
- set `TMPDIR` under workspace
- provide minimal `PATH`
- remove unrelated personal secrets/tokens

### 8.4 Network Policy

For v0.1:
- default = no network
- task-specific allowlist possible later

A reasonable first move is to only support tasks that do not require network access.

---

## 9. Command Launcher Abstraction

A key design principle:

> The agent should not directly call `subprocess.run()` for benchmarked actions.

All command execution should go through a unified launcher.

### Launcher responsibilities

1. parse command
2. enforce command allowlist
3. enforce cwd under allowed roots
4. sanitize environment
5. enforce timeout
6. capture stdout/stderr
7. emit structured trace record
8. record policy violations when blocked

### Why this matters

This is the point where Lite evaluation differs most from Docker execution.

Instead of delegating execution safety to a container boundary, Lite makes the execution boundary explicit in the benchmark harness itself.

---

## 10. Required Traces and Metrics

A central advantage of SkillsBench-Lite is that it can expose behavioral signals more directly than Docker-based scoring alone.

### 10.1 Baseline outcome metrics

Keep the usual benchmark metrics:
- task success/failure
- score
- latency
- token/cost

### 10.2 Behavioral metrics

Add:
- command count
- tool call count
- retry count
- timeout count
- policy violation count

### 10.3 Environment interaction metrics

Add:
- files created
- files modified
- writes outside expected output scope
- attempted out-of-scope access
- blocked command attempts

### 10.4 Why these matter for Skill enhancement

A stronger skill may not only improve final success rate. It may also:
- take fewer unnecessary actions
- create fewer spurious files
- violate fewer execution constraints
- produce shorter, cleaner action trajectories

This is especially important when evaluating a general Skills Enhancement Framework.

---

## 11. Workspace Diff Capture

v0.1 should at least capture a simple before/after file snapshot and diff summary.

### Minimal diff summary

- created files
- modified files
- deleted files

This is enough to start measuring environmental cleanliness.

### Later upgrade path

A future v0.2 can add an overlay-style workspace mode where:
- baseline task tree is read-only
- all writes go to an explicit write layer
- diffs become easier to compute and analyze

---

## 12. Experimental Protocol Recommendation

### Step 1 — Reproduce baseline on Docker lane

Confirm the benchmark baseline under official Docker execution.

### Step 2 — Reproduce baseline on Lite lane

Before testing the enhancement, confirm that the baseline can run in the Lite environment on the selected task subset.

### Step 3 — Evaluate enhanced skill on Docker lane

Measure official benchmark gains.

### Step 4 — Evaluate enhanced skill on Lite lane

Measure transfer of gains outside the Docker world.

### Step 5 — Compare both lanes

For each skill variant, compare:
- score delta
- variance
- command count
- side effects
- contamination indicators

### Main interpretation questions

1. Do enhancement gains persist in Lite?
2. Does the enhanced skill become more stable across execution substrates?
3. Does the enhanced skill reduce unnecessary environmental interaction?
4. Are some gains revealed to be Docker-specific?

---

## 13. Minimal v0.1 Implementation Checklist

### A. Task scope
- [ ] choose 3–10 lightweight offline tasks
- [ ] exclude network-heavy / service-heavy tasks

### B. Core runner
- [ ] implement episode runner
- [ ] create temp workspace per task
- [ ] add cleanup policy

### C. Policy layer
- [ ] implement command allowlist
- [ ] implement cwd/path checks
- [ ] sanitize environment variables
- [ ] default to no-network tasks

### D. Command launcher
- [ ] centralized command execution wrapper
- [ ] timeout support
- [ ] stdout/stderr capture
- [ ] structured trace records

### E. Evaluation
- [ ] reuse original or equivalent scorer
- [ ] score baseline in Lite
- [ ] score enhanced version in Lite

### F. Trace and metrics
- [ ] write per-run summary JSON
- [ ] record command traces
- [ ] record workspace diff
- [ ] record policy violations

---

## 14. Non-Goals for v0.1

v0.1 should **not** attempt to provide:

- full container-grade security isolation
- browser or GUI benchmarking
- complete SkillsBench task coverage
- package-install-heavy environments
- cross-platform perfection
- full overlay filesystem semantics
- microVM-level threat containment

These would risk turning the project into a replacement container runtime rather than a research harness.

---

## 15. Proposed Research Value

If successful, SkillsBench-Lite creates a useful second evaluation lane for SkillX work.

It enables claims of the form:

1. **Benchmark-faithful claim:**
   - the enhancement improves performance on official Docker-based SkillsBench execution

2. **Transfer/robustness claim:**
   - the enhancement also improves performance, or at least preserves gains, in a lighter and more host-adjacent evaluation substrate

3. **Behavioral claim:**
   - the enhancement improves action efficiency, reduces side effects, or reduces environmental contamination risk

This is potentially more informative than reporting a single Docker benchmark number alone.

---

## 16. Suggested Next Steps

### Immediate next step

Build a minimal prototype with:
- temp workspace mode
- command allowlist
- environment sanitization
- trace logging
- 3–5 lightweight offline tasks

### Next design upgrade after v0.1

1. overlay workspace mode
2. task-specific network policy
3. richer action-efficiency metrics
4. protocol section for paper framing

---

## 17. One-Sentence Summary

**SkillsBench-Lite v0.1 is a lightweight, task-sandbox-based supplementary evaluation lane for SkillX that preserves task-level control and cleanup while testing whether Skill enhancement gains transfer beyond Dockerized benchmark environments.**
