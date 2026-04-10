# SkillCraft Onboarding Note v0.1

- **Project:** `projects/skillX`
- **Date:** 2026-04-10
- **Role:** onboarding memo for evaluating SkillCraft as a later native bridge benchmark for SkillX
- **Status:** deferred native benchmark note

---

## 1. Why SkillCraft is relevant but not first

SkillCraft is relevant because it is genuinely about skillful behavior.

But its center of gravity is different from the current first-wave SkillX question.

It focuses more on:
- composing atomic tools into higher-level skills,
- saving and reusing those skills,
- efficiency gains from reusable compositions,
- persistent skill-library behavior.

So the core question is closer to:

> can the agent learn to form and reuse tool skills?

rather than:

> how should we write an external skill artifact so that it improves performance on a matched task?

That makes SkillCraft important, but better as a second-wave or bridge benchmark.

---

## 2. Task format

SkillCraft appears to use long-horizon, compositional tool-use tasks.

For SkillX purposes, treat each evaluation unit as something like:

```text
(task, tool_set, reusable_skill_library, execution_trace, verifier)
```

### Expected task surface
- highly compositional,
- tool-heavy,
- repeated opportunities for reuse,
- runtime discovery of reusable procedures.

This differs from SkillsBench because the benchmark object is not only the external skill artifact, but also the agent’s ability to create and manage reusable skills.

---

## 3. Verifier type

### Expected verifier profile
- task completion outcome,
- possibly reuse efficiency or token-efficiency readouts,
- success under multi-step compositional tool use,
- quality of reusable skill formation indirectly reflected in downstream results.

### Strength for SkillX
SkillCraft can reveal whether SkillX artifacts become good substrates for:
- reusable abstraction,
- skill compression,
- procedural transfer,
- internalization-like behavior.

### Limitation for current SkillX
The evaluation signal is less cleanly about the marginal utility of an externally authored skill alone.
It mixes in:
- the agent’s discovery ability,
- library management behavior,
- runtime composition quality.

---

## 4. Skill attachment point

Skill attachment here is not the same as in SkillsBench.

### Likely attachment modes
1. **No reusable skill mode / direct atomic tool usage**
2. **Native SkillCraft skill mode**
3. **SkillX-authored seed skills or scaffold templates injected into the library workflow**
4. **SkillX-guided rewrite or compression policy for saved skills**

### Why this is interesting
SkillCraft may let us test a future SkillX question:

> do better external skill artifacts lead to better downstream self-composed reusable skills?

That is highly relevant to the internalization track.

---

## 5. Paired evaluation protocol

## Recommended protocol for later use

### First useful comparison
- `K0` native tool use without SkillX-style support
- `K1` native SkillCraft skill mode
- `K2` SkillX-seeded skill mode or SkillX-guided saved-skill format

### Possible later comparison
- `K3` SkillX-guided compression or refinement of generated skills
- `K4` SkillX-guided withdrawal or simplification probes

### Main readouts
- task success,
- token / cost efficiency,
- reuse frequency,
- stability of saved skills,
- error propagation from composed skills,
- portability of generated skills across tasks.

---

## 6. Adapter complexity

**Assessment:** medium to high

### Why it is higher than SkillsBench
- The runtime likely depends on benchmark-specific skill-library primitives.
- Skill saving, retrieval, execution, and persistence may need custom handling.
- The benchmark object is more procedural and stateful.

### Practical implication
Using SkillCraft too early would risk spending more time adapting the benchmark’s own skill protocol than measuring the current SkillX object.

---

## 7. Likely task-class coverage

SkillCraft probably over-indexes toward:
- tool-heavy analytic pipelines,
- reusable tool wrappers,
- compositional multi-step tasks,
- procedural abstraction and reuse.

This makes it attractive for a later SkillX line focused on:
- internalization readiness,
- decomposition quality,
- compact reusable protocol fragments,
- shallow robust skill hierarchies.

---

## 8. Main risks

1. **Research-question drift**
   - We may accidentally pivot from external skill design to agent self-skill-formation too early.

2. **High protocol adaptation cost**
   - Too much engineering effort may go into integrating the benchmark’s native skill library mechanics.

3. **Mixed attribution**
   - Gains may come from better runtime discovery rather than better authored SkillX artifacts.

4. **Hierarchy fragility**
   - Deeply nested or over-composed generated skills may propagate errors quickly.

---

## 9. Recommended use in the SkillX roadmap

### Current role
- **Deferred native bridge benchmark**
- not first-wave evidence
- future link between augmentation and internalization/composition lines

### Best use case
Bring in SkillCraft after the current SkillsBench-first story is already stable.
Then use it to test whether SkillX artifacts are not only helpful at inference time, but also good substrates for:
- reusable abstraction,
- skill formation,
- compression and retirement,
- self-composed tool workflows.

---

## 10. Operational next step

1. Do not treat SkillCraft as the primary benchmark now.
2. Record its likely protocol primitives and runtime assumptions.
3. Revisit it after the SkillsBench and SWE-Skills-Bench lines are stable.
4. Use it first for a small bridge experiment rather than full benchmark adoption.

---

## 11. Bottom line

> SkillCraft is useful for SkillX, but mainly as a later bridge benchmark for composition and internalization questions, not as a replacement for SkillsBench-style native measurement of external skill marginal utility.
