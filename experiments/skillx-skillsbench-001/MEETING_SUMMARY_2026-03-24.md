# MARC / SkillX Project Summary

## Big Picture
Our broader research goal is to build **MARC (Multi-Agent Research Community)**: a framework where reusable agent-improvement artifacts can be authored, shared, evaluated, and iteratively improved. Within that agenda, **SkillX** is our current experimental line for turning loosely written skills into more structured, transferable, and testable objects.

## Motivation
Current skill ecosystems are good at packaging and discovery, but weak at **task contracts, conditional utility, and reliable transfer**. In practice, skills can help, do nothing, or actively hurt. We want to understand when a skill is useful, how to rewrite it into a better artifact, and whether bounded refinement can systematically improve it.

## What We Are Testing
We use **SkillsBench** as the first benchmark and compare:
- **C0**: no skill
- **C1**: original skill
- **C2**: SkillX minimal rewrite
- **C3**: SkillX derived/expanded version
- **C4**: bounded multi-round refinement of C3

## What Is Different From Existing Work
Our focus is not just “better prompting.” We treat skills as **first-class research objects** with explicit structure, evaluator-facing constraints, and iterative refinement. The key question is not average uplift alone, but **conditional utility, negative transfer, and whether refinement improves the artifact itself**.

## Current Status
We have completed the first **C3 + C4 batch** on three tasks. One task (`trend-anomaly-causal-inference`) showed a clear positive C4 improvement; two others did not. The strongest current signal is that refinement helps by **removing speculative and bloated derived content**, not by adding more rules.

## Next Step
Implement **C4 meta-protocol v0.2**, rerun the batch, and then connect a true held-out final evaluation.