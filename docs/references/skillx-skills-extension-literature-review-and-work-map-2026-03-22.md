# SkillX / Skills Extension — Literature Review and Work Map

- **Project:** `projects/multi-agent-protocol-design`
- **Date:** 2026-03-22
- **Purpose:** build a rigorous literature review + work map for a stronger layer above today’s loose AI “skills” format
- **Research question:** if today’s skill formats are too prose-heavy and under-specified, what would a more declarative, verifiable, transferable, and evolvable skill framework look like, and what does current academic + industry evidence actually support?

---

## 0. Executive summary

The strongest conclusion from this review is that current skill ecosystems are usually **good at packaging and discoverability**, increasingly decent at **typed I/O**, but still weak at **task contracts**. In practice, this means most skills can tell an agent roughly *when* to use something and sometimes *how* to call a tool, but they do not reliably define what the task is, what is in or out of scope, what operations are allowed or forbidden, what counts as success, how failure should be classified, or how another agent in a different model/environment should adapt the same experience.

A second major conclusion is that **skill utility is conditional, not universal**. SkillsBench is the clearest direct evidence: curated skills can help substantially on average, but they also hurt on a meaningful subset of tasks, and self-generated skills show weak or inconsistent aggregate gains. This means a future SkillX system cannot assume “skill present = better.” It must encode explicit acceptance criteria, report per-task effects, and detect negative transfer.

A third conclusion is that the current wave of “self-improving agents” is often miscategorized. Many systems marketed as skill evolution are actually doing one of three different things: prompt refinement, memory refinement, or workflow/program optimization. True first-class **skill refinement**—where a named, versioned, reusable skill object is updated under evaluator control—exists, but it is much rarer than the discourse suggests. The most relevant exemplars are Voyager, SkillWeaver, SkillRL, MemSkill, and EvoSkill.

A fourth conclusion is that **memory is not transfer**. Most production memory stacks—LangGraph memory, Mem0, Letta, and similar systems—solve persistence and retrieval within a local agent/application. They do not by themselves solve cross-agent or cross-environment portability. Real transfer requires explicit mapping mechanisms across model, tool schema, environment, and policy layers. PromptBridge, PA-Tool, GTTA, and AgentRR each solve part of this broader transfer problem, but no single system yet solves the full stack end-to-end.

Taken together, the literature supports a stronger framing for SkillX: a skill should not be treated as a loose instruction blob. It should be treated as a **first-class task object** with at least four tightly connected layers: a declarative contract layer, an evaluator layer, a transfer/localization layer, and an evolution layer. In short:

> **SkillX should upgrade “skill” into a declarable, verifiable, transferable, and evolvable task object.**

---

## 1. Research objective and method

This review was designed around four themes:

1. **Declarative skill / task specification**
2. **Skill evaluation / acceptance / benchmarks**
3. **Automated skill refinement / discovery / evolution**
4. **Skills ↔ memory ↔ transfer / localization**

The review used a skeptical lens and explicitly tried to separate direct evidence from nearby but different topics. In particular, it distinguished:
- packaging vs semantics,
- typed I/O vs task contract,
- prompt optimization vs skill refinement,
- local memory persistence vs cross-agent transfer.

The source mix included both **academic papers** and **industry / open-source practice**, since many of the strongest current lessons are split across both worlds. Four research tracks were explored in parallel, each with at least two cycles: a broad landscape pass and a targeted deepening pass on the strongest primary sources.

---

## 2. Theme I — Declarative skill / task specification

### 2.1 Main finding

Current skill standards are mostly **discovery-oriented and prose-oriented**, not full declarative task contracts.

Agent Skills / Anthropic-style skills are useful because they make reusable guidance packageable and discoverable, but they are deliberately lightweight. The Agent Skills specification requires a `name` and `description`, while leaving the body largely unconstrained; even fields like `allowed-tools` are experimental and implementation-dependent. This is strong as a portability and packaging convention, but weak as a mechanism for enforcing semantics.

### 2.2 What current ecosystems do well

There is genuine progress on **typed interfaces**:
- **OpenAI function calling + Structured Outputs** provide strong JSON-schema-based argument and output constraints.
- **MCP** adds protocolized tool discovery/invocation and schema-based interoperability.
- **OpenAPI** provides a mature contract language for services and is increasingly used as a bridge into tool definitions.
- **PydanticAI** brings code-first type discipline to tools and outputs.
- **LangGraph** gives explicit graph/state structure and some compile-time checks for orchestration.
- **Semantic Kernel** offers organized plugin/function metadata and interoperability with OpenAPI/MCP-style tool descriptions.

These systems reduce malformed calls and make tool use much more regular. But they mainly constrain **inputs/outputs and invocation structure**—not full task semantics.

### 2.3 The missing layer: task contract semantics

What remains weak or absent in modern skill formats:
- **scope contracts**: what the skill is for and what it must not do,
- **preconditions / postconditions**,
- **failure modes** and retry/rollback semantics,
- **allowed / forbidden operations** as first-class enforceable constraints,
- **acceptance criteria** linked to executable tests or verifiers,
- **composition semantics** when multiple skills conflict,
- **state transition semantics** across multi-step side effects.

This is where the literature points backward, somewhat surprisingly, to **classical planning languages**. PDDL2.1 and HDDL remain the clearest precedents for declarative task contracts with analyzable semantics: preconditions, effects, temporal constraints, decomposition, and validation. They are too heavy for most modern product workflows, but they demonstrate that stronger declarative task structure is possible and already well understood in other traditions.

### 2.4 Working conclusion from Theme I

Modern skill ecosystems are strongest when they combine:
- typed interfaces,
- explicit decomposition structures,
- protocolized discovery/invocation,
- and verifiability hooks.

But the central gap remains a **task-contract layer**. SkillX should not replace current packaging/tool ecosystems; it should add a stronger contract block above them.

---

## 3. Theme II — Skill evaluation / acceptance / benchmarks

### 3.1 Main finding

The evidence strongly supports Xin’s core hypothesis: many skills underperform because they do not encode explicit success standards, and because their evaluation is often too weak to distinguish real help from apparent help.

### 3.2 Direct evidence: skills help conditionally and can hurt

**SkillsBench** is the single most direct source for this question. It shows that curated skills can significantly improve average pass rate, but the gains vary sharply by domain and a meaningful subset of tasks get worse. Self-generated skills show weak or near-zero average gains.

This matters because it rules out a naive view of skills as monotonic improvements. A future SkillX layer must treat skill utility as:
- task-dependent,
- benchmark-dependent,
- evaluator-dependent,
- and potentially negative.

### 3.3 The strongest evaluators are outcome-grounded

Across modern agent benchmarks, the most trustworthy acceptance patterns are those grounded in **artifact or environment state**:
- **SWE-bench**: repo tests,
- **τ-bench**: final database state,
- **OSWorld / WebArena**: execution-based environment checks,
- **ToolSandbox**: milestone + dynamic scoring.

These are stronger than pure text similarity because they evaluate whether the world actually ended up in the right state.

### 3.4 Evaluator quality is itself a critical bottleneck

A major anti-theater lesson from recent work is that benchmarks themselves can be misleading when evaluators are weak. **WebArena Verified** exists largely because original evaluators were too fragile. Work around SWE-bench has shown that “plausible but incorrect” patches can pass inadequate tests, and OpenAI has publicly withdrawn SWE-bench Verified from frontier-model reporting due to test flaws and contamination issues.

This leads to an important meta-conclusion:

> **A skill benchmark is only as good as its evaluator.**

So SkillX must not only specify acceptance criteria for skills; it must also specify **evaluator hardening and benchmark governance**.

### 3.5 Process matters too: trajectory-level evaluation

Many skills are not only about end results, but about **how** an agent should solve a problem. This is why trajectory/session-log evaluation is increasingly important. LangSmith trajectory evaluation patterns and Anthropic’s agent-evals methodology both reflect this shift.

A robust evaluator stack therefore needs at least two perspectives:
- **outcome verification**,
- **process verification**.

### 3.6 Working conclusion from Theme II

The literature supports a layered evaluation model:
1. **Outcome verifier** — external state, tests, artifacts,
2. **Process verifier** — tool usage, ordering, policy compliance,
3. **Quality rubric** — LLM/human calibrated,
4. **Reliability layer** — multi-trial stability, pass@k/pass^k.

A SkillX promotion rule should never rely on a single-run aggregate score alone.

---

## 4. Theme III — Automated skill refinement / discovery / evolution

### 4.1 Main finding

Most current “self-improving agent” work does **not** update a first-class skill object. It usually updates either:
- prompts,
- memory summaries/reflections,
- or workflows/programs.

This distinction matters because SkillX aims at a stronger object: a named, reusable, versioned, evaluator-gated skill artifact.

### 4.2 A useful taxonomy

#### A. Prompt refinement
Examples: Promptbreeder, GEPA, many DSPy / TextGrad uses.
- Updated object: prompt or instruction block.
- Strength: often effective, easy to search/optimize.
- Weakness: can be brittle, context-coupled, hard to govern as a reusable artifact.

#### B. Memory refinement
Examples: Reflexion, ExpeL, MemP, many long-term memory systems.
- Updated object: reflections, episodic/procedural memory store.
- Strength: helps continuity and adaptation.
- Weakness: often retrieval-dependent, under-versioned, weakly composable.

#### C. True skill refinement
Examples: Voyager, SkillWeaver, SkillRL, MemSkill, EvoSkill.
- Updated object: explicit skill artifact/library/bank/API.
- Strength: highest potential for governance, versioning, portability, and reuse.
- Weakness: still relatively rare; evidence quality uneven.

### 4.3 What the strongest systems have in common

The strongest “true-skill-ish” systems share several design patterns:
- **explicit skill artifacts**,
- **failure-driven updates**,
- **hard-case pools or failure clustering**,
- **evaluation gates before promotion**,
- **versioning/frontier logic** rather than destructive overwrite,
- **some transfer or compositionality tests**.

This is a strong signal for SkillX: auto-evolution should not be imagined as unrestricted continual mutation. It should be a **failure-triggered, evaluator-gated, versioned search process**.

### 4.4 What remains weak in the literature

Common weaknesses across the “evolution” literature:
- overclaiming about what object is actually being improved,
- confounding skill updates with stronger teachers or RL tuning,
- limited variance/robustness reporting,
- benchmark-local transfer claims,
- weak governance/rollback semantics.

### 4.5 Working conclusion from Theme III

SkillX should explicitly separate three update channels:
- **prompt update**,
- **memory update**,
- **skill update**.

If these are not separated, attribution becomes impossible. A reported improvement may come from the wrong layer, making the resulting system scientifically weak and operationally hard to control.

---

## 5. Theme IV — Skills ↔ memory ↔ transfer / localization

### 5.1 Main finding

Most current memory systems solve **local persistence**, not true transfer.

LangGraph memory, LangChain long-term memory, Mem0, and Letta all provide useful ways to store/retrieve knowledge across sessions and agents. But without additional mapping layers, these systems do not ensure that an experience useful in one model/tool/environment becomes usable in another.

### 5.2 Real transfer requires explicit mapping mechanisms

The clearest evidence today points to a **transfer stack**, not a single transfer trick.

Relevant slices of the stack include:
- **PromptBridge** — prompt mapping across models,
- **PA-Tool** — tool-schema mapping to model priors,
- **GTTA** — deployment-time adaptation across environment mismatches,
- **AgentRR** — structured record/summarize/replay with checks,
- **MCP** — interface normalization and capability negotiation,
- **Voyager** — executable skill reuse within related environments.

No single system solves cross-model, cross-tool, cross-environment, and cross-policy adaptation together. But the literature already supports the basic idea that transfer should be decomposed into multiple mapping layers.

### 5.3 Portable knowledge vs local adaptation

A useful synthesis is:

**Portable knowledge should include:**
- task intent,
- strategy patterns,
- invariants,
- guardrails,
- failure patterns,
- evaluated experience capsules,
- capability/cost/risk metadata.

**Local adaptation should include:**
- tool schemas,
- environment observation/action formats,
- runtime assumptions,
- model-specific prompt style,
- local policy/safety constraints.

This distinction strongly supports a SkillX architecture in which portable skill capsules are separate from localized adapter packs.

### 5.4 Working conclusion from Theme IV

SkillX should treat transfer as a mapping stack:
- **prompt mapping**,
- **schema mapping**,
- **environment mapping**,
- **policy mapping**.

Memory retrieval alone is not enough.

---

## 6. Cross-cutting synthesis

### 6.1 The three-layer gap

Across all four themes, the same structural diagnosis keeps appearing. Current ecosystems are split across three partially developed layers:

1. **Packaging layer**
   - discovery, loading, distribution, context management.
2. **Tool-schema layer**
   - parameter typing, I/O validation, interface normalization.
3. **Task-contract layer**
   - scope, allowed operations, preconditions, postconditions, failure semantics, acceptance criteria, composition rules.

Today’s ecosystems are reasonably good at (1), improving on (2), and still weak on (3).

### 6.2 Why today’s skills feel “C-like” rather than declarative

Xin’s analogy is useful: many skills today feel more like loose procedural instructions than declarative task objects. The literature supports that intuition. Current skill formats generally say:
- when something might be useful,
- and maybe how to perform a procedure,

but usually do not formally define:
- the task boundary,
- the contract of success/failure,
- the permitted action space,
- or the conditions under which the skill should not be used.

### 6.3 The strongest unifying claim

The literature now supports a stronger project-level claim:

> **A skill should be represented as a first-class task object, not just a discoverable instruction bundle.**

That task object should be:
- declarable,
- verifiable,
- transferable,
- and evolvable.

---

## 7. Working design implications for SkillX

This review does not directly propose a final SkillX standard, but it does support a strong direction.

### 7.1 Minimal architectural layers

A reasonable SkillX stack would contain at least:

#### Layer A — Portable metadata / packaging
- name,
- description,
- compatibility,
- tags,
- discovery fields,
- references/examples.

#### Layer B — Enforceable task contract
- `scope`,
- `allowed_operations`,
- `forbidden_operations`,
- `preconditions`,
- `postconditions`,
- `failure_modes`,
- `policy_constraints`,
- `acceptance_tests`,
- optional `composition_rules`.

#### Layer C — Evaluator contract
- outcome verifier,
- process verifier,
- quality rubric,
- reliability criteria,
- negative-transfer reporting,
- benchmark/evaluator version.

#### Layer D — Transfer / localization adapters
- model adapter,
- tool-schema adapter,
- environment adapter,
- policy adapter,
- provenance of adaptation.

#### Layer E — Evolution / governance layer
- versioned candidates,
- failure-triggered updates,
- replay/held-out validation,
- regression gates,
- rollback,
- promotion/deprecation rules.

### 7.2 Evaluation discipline that SkillX should probably require

The literature strongly supports the following norms:
- no “skill accepted” status without evaluator-backed evidence,
- mandatory ablation at least across: **no skill / curated skill / adapted or self-generated skill**,
- per-task reporting, not only aggregate means,
- explicit negative-transfer accounting,
- versioned evaluators and documented evaluator failure modes,
- held-out/private or rotated evaluation where possible.

### 7.3 A likely future distinction inside SkillX

The literature suggests that SkillX should probably not treat all “improvements” as one kind of update. It will likely need separate update paths for:
- prompt deltas,
- memory deltas,
- skill-object deltas,
- and adapter/localization deltas.

This is important both scientifically and operationally.

---

## 8. Open questions and risks

### 8.1 Developer ergonomics vs formal semantics

Planning languages show what strong task contracts look like, but they are often too heavy for product iteration. SkillX will need to find a middle point: stronger than today’s skill markdown, lighter than full classical planning formalism.

### 8.2 Avoiding benchmark theater

A SkillX system could fail by looking rigorous on paper while hiding weak evaluators, contaminated benchmarks, or unreported negative transfer. Governance around evaluation is therefore not optional.

### 8.3 Overfitting to one model family or one environment

Transfer is a core project concern. Any SkillX design that ignores localization and portability testing will likely collapse into model-specific prompt engineering with better metadata.

### 8.4 Confusing memory accumulation with real reusable skill

This is one of the biggest conceptual risks. If every retrieved reflection is called a skill, the system loses the distinction that makes SkillX valuable.

### 8.5 Community maintenance burden

Once skills become more contract-heavy, there is a new maintenance burden: evaluator upkeep, migration, versioning, compatibility management, and benchmark refresh. The literature supports doing this, but it is not free.

---

## 9. Bottom line

The literature does **not** support the view that today’s loose skill standards are already sufficient. It also does **not** support the view that better prose alone will solve the problem. What the evidence points to is more specific:

1. **Skill packaging matters, but is not enough.**
2. **Typed I/O matters, but is not enough.**
3. **Acceptance criteria and evaluator quality are central.**
4. **Transfer requires explicit mapping layers.**
5. **True skill evolution requires first-class skill objects and evaluator-gated governance.**

Therefore the strongest current framing is:

> **SkillX should be designed as a framework that turns skills into declarable, verifiable, transferable, and evolvable task objects.**

That claim is now supported by a meaningful cross-section of academic literature, benchmarks, and industry/open-source practice.

---

## 10. Selected source map

### Directly relevant specification / contract sources
- Agent Skills specification — <https://agentskills.io/specification>
- Anthropic Agent Skills overview — <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview>
- Anthropic skill best practices — <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices>
- OpenAI function calling — <https://developers.openai.com/api/docs/guides/function-calling>
- OpenAI Structured Outputs — <https://developers.openai.com/api/docs/guides/structured-outputs>
- MCP specification — <https://modelcontextprotocol.io/specification/2025-11-25/server/tools>
- OpenAPI specification — <https://spec.openapis.org/oas/latest.html>
- PydanticAI tools — <https://ai.pydantic.dev/tools/>
- LangGraph graph API — <https://docs.langchain.com/oss/python/langgraph/graph-api>
- Semantic Kernel plugins — <https://learn.microsoft.com/en-us/semantic-kernel/concepts/plugins/>
- PDDL2.1 — <https://arxiv.org/abs/1106.4561>
- HDDL — <https://aaai.org/papers/09883-hddl-an-extension-to-pddl-for-expressing-hierarchical-planning-problems/>

### Directly relevant evaluation / benchmark sources
- SkillsBench — <https://arxiv.org/abs/2602.12670>
- SkillsBench site — <https://www.skillsbench.ai/>
- SWE-bench — <https://openreview.net/forum?id=VTF8yNQM66>
- SWE-bench correctness study — <https://arxiv.org/abs/2503.15223>
- WebArena — <https://arxiv.org/abs/2307.13854>
- WebArena Verified — <https://openreview.net/forum?id=CSIo4D7xBG>
- OSWorld — <https://arxiv.org/abs/2404.07972>
- τ-bench — <https://arxiv.org/abs/2406.12045>
- ToolSandbox — <https://arxiv.org/abs/2408.04682>
- BFCL — <https://openreview.net/forum?id=2GmDdhBdDk>
- Anthropic agent evals — <https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents>
- OpenAI eval best practices — <https://developers.openai.com/api/docs/guides/evaluation-best-practices>
- LangSmith trajectory evals — <https://docs.langchain.com/langsmith/trajectory-evals>

### Directly relevant evolution / refinement sources
- Voyager — <https://arxiv.org/abs/2305.16291>
- SkillWeaver — <https://arxiv.org/abs/2504.07079>
- SkillRL — <https://arxiv.org/abs/2602.08234>
- MemSkill — <https://arxiv.org/abs/2602.02474>
- EvoSkill — <https://arxiv.org/abs/2603.02766>
- Reflexion — <https://arxiv.org/abs/2303.11366>
- ExpeL — <https://arxiv.org/abs/2308.10144>
- MemP — <https://arxiv.org/abs/2508.06433>
- DSPy — <https://arxiv.org/abs/2310.03714>
- TextGrad — <https://arxiv.org/abs/2406.07496>
- Promptbreeder — <https://arxiv.org/abs/2309.16797>
- GEPA — <https://arxiv.org/abs/2507.19457>
- AFlow — <https://arxiv.org/abs/2410.10762>

### Directly relevant memory / transfer sources
- CoALA — <https://arxiv.org/abs/2309.02427>
- Generative Agents — <https://arxiv.org/abs/2304.03442>
- MemGPT — <https://arxiv.org/abs/2310.08560>
- AgentRR — <https://arxiv.org/abs/2505.17716>
- PromptBridge — <https://arxiv.org/abs/2512.01420>
- GTTA — <https://arxiv.org/abs/2511.04847>
- PA-Tool — <https://arxiv.org/abs/2510.07248>
- Mem0 paper — <https://arxiv.org/abs/2504.19413>
- LangGraph memory docs — <https://docs.langchain.com/oss/python/langgraph/memory>
- LangChain long-term memory docs — <https://docs.langchain.com/oss/python/langchain/long-term-memory>
- Mem0 docs — <https://docs.mem0.ai/open-source/overview>
- Letta docs — <https://docs.letta.com>

---

## 11. Suggested next documents after this review

1. A short **SkillX project-facing synthesis memo** translating this literature into design implications.
2. A candidate **SkillX minimal contract schema** with explicit evaluator hooks.
3. A concrete **SkillsBench-to-SkillX rewrite experiment plan**.
4. A **benchmark governance checklist** for avoiding evaluation theater.
