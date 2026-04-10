# SkillX Evaluator-In-The-Loop Evaluation Protocol v0.1

- **Project:** `projects/skillX`
- **Date:** 2026-04-10
- **Role:** 定义当前 round-0 / outer-loop pilot 的实验设定、汇报口径、以及后续可扩展的 evaluation 路线
- **Status:** working protocol

---

## 1. Purpose

本文档回答一个核心问题：

> 当 SkillX 把 evaluator 放进 inner loop / outer loop 里做优化时，我们到底应该如何定义方法、跑实验、以及汇报结果？

本协议的目标不是把所有 evaluation 争议一次性彻底解决，而是先把当前最重要的几件事固定下来：

- 当前主实验先采用什么设定
- 最终结果如何选择
- round budget 怎么定
- 什么 claim 可以安全地卖
- 后续有哪些高收益扩展

---

## 2. Core Framing

当前 SkillX 的主方法应被理解为：

> **an evaluator-in-the-loop skill optimization pipeline**

也就是说，SkillX 不是一个只做一次静态生成的系统，而是一个：

- 从 `C1` 起跑，
- 在固定 budget 下反复得到 evaluator / partial evaluator 信号，
- 通过 inner loop 更新 task skill，
- 再由 outer loop 更新 schema assignment / schema bank，
- 最终返回预算内最好 candidate 的系统。

这一定义很重要。

因为一旦方法被定义成上面的形式，那么：

- 在优化过程中使用 evaluator **不是作弊**
- 但实验结果必须被汇报成 **budgeted online optimization result**
- 而不是“单次静态 prompt / skill 的最终 test score”

---

## 3. Current Main Setting

## 3.1 Setting A: Oracle Evaluator

当前主实验采用：

> **Setting A — Oracle Evaluator**

定义：

- 直接使用 task 自带的 benchmark evaluator / verifier
- evaluator 信号进入 inner loop
- schema-conditioned task skill 在固定 round budget 下优化
- outer loop 再用 `task × schema` 的结果做 assignment / clustering

这个设定对应的生产假设是：

- 真实环境中存在 evaluator 或 partial evaluator
- 该 evaluator 是问题的一部分，而不是完全隐藏、完全不可访问的黑盒

对于当前 SkillsBench round-0 pilot，这个假设是可 defend 的，原因是：

- 许多 task 的 instruction 已经直接或近乎直接给出了目标函数、约束、验收条件或输出格式
- benchmark verifier 往往只是把这些 task-level success conditions 具体 operationalize 成 executable checks

注意：

- Setting A 是当前主线
- 它应该被明确写进实验设计和汇报口径

## 3.2 Setting B: Task-Derived Rubric

后续可选扩展：

> **Setting B — Task-Derived Rubric**

定义：

- 不直接把 benchmark evaluator 暴露给优化器
- 只给 task description / task context
- 让 agent 先写出它认为合理的 rubric / evaluator sketch
- inner loop 仅使用这个 task-derived rubric 做 candidate 选择或 early stop

这个设定更接近真实生产环境中的“弱 evaluator / partial evaluator”。

它的价值在于：

- 更 realistic
- 更能说明 SkillX 不是只会“贴着 benchmark verifier 做 overfit”
- 如果结果接近 Setting A，会显著增强方法说服力

当前阶段：

- Setting B **不是 blocker**
- 先把 Setting A 跑稳
- 有余力再补 Setting B

---

## 4. What We Sell

当前最稳、最值得卖的 claim 不是“我们发现了任务的真 taxonomy”，而是下面两个：

## 4.1 Claim A: Production Utility Under Evaluator Access

在存在 evaluator / partial evaluator 的真实设定下，
SkillX 的双层优化流程可以在固定预算内提升 skill 的实际任务表现。

关键词：

- evaluator-in-the-loop
- budgeted optimization
- production utility

## 4.2 Claim B: Schema Specialization Helps

不同 task 并不共享一个 universal schema。
使用一个小的 schema bank，并对 task 做 assignment，比单一 schema 更有效。

关键词：

- schema specialization
- assignment utility
- task-schema structure

注意：

- 我们要卖的是 `utility of specialization`
- 不是 `taxonomy correctness`

也就是说：

- clustering 只要在行为上有用即可
- 不要求它在语义上看起来像某种唯一正确的人类分类法

---

## 5. Final-Result Selection Rule

## 5.1 Required rule

当前主实验必须采用固定的、系统内置的 candidate 选择规则：

> **best-so-far incumbent selection under a fixed budget**

定义：

- 从 `R0` 开始
- 每轮都记录当前 evaluator score
- 维护一个 `best-so-far incumbent`
- 在预算结束时，自动返回该 incumbent

这里的关键是：

- 最终版本不是实验者事后人工挑的
- 而是系统定义里就写死的输出规则

## 5.2 What signal is allowed

在 Setting A 中，允许直接使用同一个 evaluator signal 来做：

- 每轮 candidate 比较
- incumbent 维护
- 预算结束时最终输出选择

原因是：

- evaluator access 本来就是方法定义的一部分
- 我们优化的对象是“预算内在线表现”
- 不是“完全不看 evaluator 的静态 prompt”

因此，当前不需要强行再引入一个额外的内部 judge。

如果未来加入 Setting B，则可以把：

- task-derived rubric
- self-proposed evaluator
- partial verifier

作为更弱的选择信号。

## 5.3 Reporting language

汇报时必须说清楚：

- `selected result` 是 **budgeted best-so-far incumbent**
- 它来自固定 round budget 内的自动选择
- 它不是 post-hoc hand-picked best round

推荐表述：

> We report the best-so-far incumbent selected automatically under a fixed `R`-round evaluator-in-the-loop budget.

---

## 6. Round Budget

## 6.1 Current default

当前主实验的推荐默认 budget 为：

- `round_budget = 3`

在现有 runner 语义下，这意味着：

- `R0` = bootstrap / starting-point evaluation
- `R1` 到 `R3` = 三轮 refine

所以总共会观察到：

- `R0, R1, R2, R3`

## 6.2 Why not larger by default

当前不建议一开始就把 round budget 拉得很大。

原因：

- 实际运行中，后面几轮并不稳定单调提升
- 多轮以后容易出现 candidate drift
- 成本增长很快
- 很多 task 的有效提升常常出现在前 1 到 2 次 refine

因此，当前的合理策略是：

- 默认 `R0 -> R3`
- 把它作为 round-0 pilot 的主设定

## 6.3 Optional extension

如果后续需要补更强一点的实验，可以增加一个可选扩展：

- `round_budget = 5`

但这应该被视为：

- optional extension
- 不是主实验的默认配置

而且必须额外报告：

- cost increase
- gain saturation / degradation pattern
- whether later rounds still help

---

## 7. Minimum Experimental Comparisons

为了让当前方法更有说服力，至少应包含下列比较对象。

## 7.1 For Claim A

至少比较：

- `C1` static starting skill
- generic refine without schema specialization
- single universal schema
- adaptive schema bank + task assignment

这些比较必须尽量控制：

- same task slice
- same starting point
- same evaluator
- same round budget
- same or comparable token / cost budget

## 7.2 For Claim B

必须至少比较：

- `per-task assigned schema`
- `globally best single schema`

如果前者显著优于后者，就已经足够支持：

- schema specialization helps

而不必额外证明：

- clustering 是唯一正确的

---

## 8. Current Reporting Metrics

在 Setting A 的当前阶段，建议至少报告下面这些量。

## 8.1 Per-pair metrics

对于每个 `(task, schema)`：

- `R0..Rk` reward trace
- final selected incumbent reward
- selected incumbent round index
- cost / token usage if available
- failure type summary if reward later collapses

## 8.2 Aggregate metrics

对于 task slice / schema bank：

- average selected reward
- nonzero-rate / success-rate
- win-rate against baseline
- per-task best schema distribution
- assignment matrix
- low-margin / ambiguous task fraction

## 8.3 Required interpretation note

当前结果必须被解释为：

- `tune-side, budgeted optimization result`

而不是：

- fully held-out static final test result

---

## 9. Overfitting Position

当前阶段，SkillX 不应声称“已经完全排除了 overfitting”。

更准确的说法是：

- 在 Setting A 里，evaluator access 被视为 deployment assumption 的一部分
- 因而使用 evaluator 做 optimization 是合理的
- 但我们仍然承认它可能带来 task-specific overfitting 风险

当前阶段可接受的处理方式：

- 先把 Setting A 跑通并报告清楚
- 把 overfitting 风险作为已知限制写明
- 有余力时再补更强泛化验证

---

## 10. High-Value Future Upgrades

以下修改是高收益的，但不应阻塞当前 round-0 主实验。

## 10.1 Task-derived rubric experiment

做 Setting B：

- 从 task description 自动写 rubric / evaluator sketch
- 用这个 rubric 而不是 benchmark verifier 来做 inner-loop selection
- 比较它和 Setting A 的差距

## 10.2 Light generalization check

对部分 task 额外构造：

- sibling task
- rewritten task
- alternate scenario / instance

用于验证：

- evolved skill 是否只是在单一 benchmark instance 上过拟合

## 10.3 Convergence analysis

统计不同 task 的：

- selected incumbent round
- round-wise improvement probability
- degradation after late rounds

用于支持：

- 为什么主实验先固定 `round_budget = 3`
- 为什么 `5` 轮只作为可选扩展

## 10.4 Variance analysis

对少量 task 做 repeated runs，估计：

- instability
- variance
- incumbent selection robustness

---

## 11. Immediate Action Items

当前立刻应该执行的不是大改 pipeline，而是把实验协议固定下来。

### Must-fix now

- 明确主实验采用 `Setting A`
- 明确最终输出采用 `best-so-far incumbent`
- 明确当前默认 `round_budget = 3`
- 汇报时明确说明这是 `budgeted evaluator-in-the-loop result`

### Next but not blocking

- 补 `single universal schema` baseline
- 补 `generic refine` baseline
- 做完整 `task × schema` round-0 matrix
- 观察 assignment structure

### Optional later

- `Setting B`
- light generalization checks
- repeated-run variance

---

## 12. Bottom Line

当前 SkillX 的主实验应被定义为：

> a budgeted evaluator-in-the-loop optimization system with schema-conditioned specialization

因此：

- evaluator 进入 inner loop 是合理的
- 使用 evaluator signal 维护 `best-so-far incumbent` 也是合理的
- 当前主实验默认只做 `R0 -> R3`
- `R0 -> R5` 只作为可选扩展
- 最值得卖的点是：
  - production utility under evaluator access
  - schema specialization helps

而不是：

- 静态、一次性、无反馈的 final test score
- 或者“我们发现了唯一正确的任务 taxonomy”
