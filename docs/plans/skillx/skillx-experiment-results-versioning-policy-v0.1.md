# SkillX Experiment Results Versioning Policy

本文档定义一个默认规则：

- 代码和运行工具进 `main`
- 具体实验结果默认进单独的 `exp/*` 分支
- 大体量原始产物默认不直接进 git

## 结论

实验输出目录和实验结果，通常不应该直接提交到 `main`。

默认做法：

- `main`
  - 只放稳定代码、脚本、文档、协议、轻量结果模板
- `exp/<date>-<run-name>`
  - 放某一轮实验的结果整理、结果摘要、必要元数据

## 为什么

这样做的好处是：

- `main` 保持干净，便于继续开发
- 结果和代码历史分离，便于回看和对账
- collaborator 提交实验结果时不容易污染主线
- 后续写 paper、做 figure、查某一轮 run 时更容易定位

## 什么时候开结果分支

下面这些情况，应该开新的 `exp/*` 分支：

- 一轮实验已经跑完，准备整理结果
- 要提交表格、图、summary、结论文档
- 要保留某次 run 的固定结果快照
- collaborator 要上传自己跑出来的一组结果

推荐命名：

- `exp/2026-04-10-round0-3x7-results`
- `exp/2026-04-10-earthquake-followup`
- `exp/2026-04-10-civ6-ablation`

## 什么应该提交

优先提交这些轻量且有复用价值的结果文件：

- run 级 `summary.json`
- 关键 pair 的 `refine_summary.json`
- 最终选中结果对应的 `RUN_STATUS.md`
- 汇总表、图表、分析 notebook 的导出结果
- 结论文档或简短结果 memo
- 能唯一定位 run 的 metadata
  - commit SHA
  - branch 名
  - run label
  - task slice
  - model
  - round budget

如果某个结果目录很大，优先只提交：

- summary
- final selection
- diagnostics 摘要
- paper 需要的表和图

## 什么默认不提交

下面这些默认不要直接进 git，除非有明确理由：

- 大量 trial 级原始日志
- 容器缓存
- 重复的 session transcript
- Harbor 中间产物全量拷贝
- 大量临时调试文件
- 可以从已提交 summary 重新定位出来的冗余文件
- `experiments/**/agent/**` 下面的原始 agent 运行目录
  - 包括 `claude-code.txt`
  - `trajectory.json`
  - `command-*`
  - `sessions/**`
  - setup/install stdout

一句话规则：

- 能摘要就不要全量提交
- 能提 metadata 就不要提整目录日志

## 提交前的敏感信息检查

从现在开始，结果分支也要经过同一套敏感信息检查。

默认命令：

```bash
python3 scripts/check_sensitive_info.py
```

如果只想检查当前 staged 改动：

```bash
python3 scripts/check_sensitive_info.py --staged
```

这个检查会重点拦截：

- 本机绝对 home 路径
- 硬编码 token / API key
- 原始 `agent/` 运行日志目录

所以如果某轮实验结果里还带着本机路径或整棵 agent transcript，应该先清理，再提交 summary。

## 推荐工作流

1. 在干净的代码分支上跑实验。
2. 实验完成后，从最新 `main` 或当前代码基线切一个 `exp/*` 分支。
3. 只挑选必要结果文件放进仓库。
4. 先运行 `python3 scripts/check_sensitive_info.py --staged`。
5. 写一份简短结果说明，记录 run 的背景和结论。
6. 提交到 `exp/*` 分支。
7. 需要 review 或归档时，再决定是否 PR。

## 推荐目录习惯

如果要把结果纳入 git，建议保留这几类结构：

- run summary
  - `launcher_logs/<run-label>/summary.json`
- pair summary
  - `pairs/<task>__<schema>/refine_run_<run-label>/refine/<task>/refine_summary.json`
- analysis doc
  - `docs/plans/skillx/` 下的 memo，或者结果分支自己的分析文档

不要默认提交整棵 `refine_run_<run-label>/`。

## 与 `main` 的关系

只有两类结果适合回到 `main`：

- 非常轻量、稳定、会被长期引用的汇总结论
- 文档中需要固定引用的小型结果样例

原始 run 结果本身，默认还是留在 `exp/*` 分支。

## 对当前项目的默认约定

从现在开始，建议按这个默认规则执行：

- 代码、监控脚本、dashboard、protocol 修正
  - 直接走 feature branch -> `main`
- 具体 round0 / round1 实验结果
  - 走 `exp/*` 分支
- 当前本地正在生成的 experiment output 目录
  - 暂不直接提交到 `main`

## Hook 安装

为了让本地提交默认带敏感信息检查，clone 后建议执行：

```bash
git config core.hooksPath .githooks
```

这样 `pre-commit` 会自动运行 `scripts/check_sensitive_info.py --staged`。

## 相关文档

- 并行开发和 worktree 规范：
  `docs/plans/skillx/skillx-parallel-development-playbook-v0.1.md`
- round0 `m × n` 运行和监控：
  `docs/plans/skillx/skillx-round0-mxn-runbook-v0.1.md`
