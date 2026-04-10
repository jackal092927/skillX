# SkillX Round-0 `m × n` Runbook

本文档给一个最短可复用的操作路径，用来：

- 启动 round-0 的 `m × n` inner-loop / refine 实验
- 用本地 dashboard 监控运行进度和健康状态

这里的 `m × n` 含义是：

- `m`
  - 选中的 task 数量
- `n`
  - 当前 materialized manifest 里的 schema 数量
  - 当前默认是 `7`

所以：

- `1` = `1 × 7`
- `3` = `3 × 7`
- 如果后面 schema bank 变化，launcher 会自动按 manifest 展开，不需要手动改命令

## 相关脚本

- 实验 launcher
  - [`scripts/launch_skillx_round0.py`](/Users/Jackal/iWorld/projects/skillX/scripts/launch_skillx_round0.py)
- `tmux` 启动 helper
  - [`scripts/run_round0_experiment_tmux.sh`](/Users/Jackal/iWorld/projects/skillX/scripts/run_round0_experiment_tmux.sh)
- dashboard server
  - [`scripts/serve_round0_monitor.py`](/Users/Jackal/iWorld/projects/skillX/scripts/serve_round0_monitor.py)
- dashboard 启动 helper
  - [`scripts/run_round0_monitor.sh`](/Users/Jackal/iWorld/projects/skillX/scripts/run_round0_monitor.sh)

## 前提

- 在一个干净的实验 worktree 里运行
- 本机可用：
  - `uv`
  - `tmux`
  - `docker`
  - `caffeinate`
- Claude Code authentication 已可用

推荐实验 worktree 形态：

- `main` 保持干净
- 单独的 experiment worktree 用来跑长时间任务

## 先做 dry-run

先确认要跑哪些 pair：

```bash
uv run python scripts/launch_skillx_round0.py --dry-run 3
```

或先列出固定 task 顺序：

```bash
uv run python scripts/launch_skillx_round0.py --list-tasks
```

## 启动 `m × n` 实验

最简单的方式是直接用 tmux helper：

```bash
cd /Users/Jackal/iWorld/projects/skillX
scripts/run_round0_experiment_tmux.sh 3 run-3x7-2026-04-10 skillx-3x7
```

这条命令会做几件事：

- 进入默认 experiment worktree
- 用 `caffeinate` 包住 launcher，避免机器休眠
- 在 `tmux` 里启动
- 将标准输出写到 `launcher.stdout.log`

参数含义：

- 第 1 个参数：`target`
  - 比如 `3`，表示前 `3` 个 task
- 第 2 个参数：`run-label`
  - 比如 `run-3x7-2026-04-10`
- 第 3 个参数：`tmux session name`
  - 比如 `skillx-3x7`

启动后常用命令：

```bash
tmux ls
tmux attach -t skillx-3x7
```

## 结果和日志目录

给定一个 `run-label`，launcher 的核心日志目录是：

```text
<experiment-worktree>/experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-slice20-v0.2/launcher_logs/<run-label>/
```

其中最重要的几个文件是：

- `launcher.stdout.log`
  - launcher 的原始 stdout
- `events.ndjson`
  - pair 级别的开始 / 成功 / 失败事件流
- `summary.json`
  - 本次 run 的汇总状态

单个 pair 的输出则会落在：

```text
.../pairs/<task>__<schema>/refine_run_<run-label>/
```

## 启动 dashboard

最简单的方式：

```bash
cd /Users/Jackal/iWorld/projects/skillX
scripts/run_round0_monitor.sh run-3x7-2026-04-10 8765
```

然后浏览器打开：

```text
http://127.0.0.1:8765/
```

如果需要换默认 experiment worktree，可以设环境变量：

```bash
export SKILLX_EXP_WORKTREE=/abs/path/to/your/exp-worktree
scripts/run_round0_monitor.sh run-3x7-2026-04-10 8765
```

## Dashboard 会显示什么

页面会显示：

- 当前 run 的总体进度
  - `completed / total`
- 当前活跃 pair
  - task
  - schema
  - pair 状态
- 当前 pair 的更细粒度信息
  - 当前 round
  - 当前 stage
  - `executor / role_a / role_b` 哪些已经完成
- `Task / Pair Results` 总表
  - 每个 task 的 `C0 / C1`
  - 每个 pair 的 `R0 / R1 / R2 / R3`
  - `Best Round`
  - `Best Score`
  - `Δ vs C0`
  - `Δ vs C1`

分数显示约定：

- `C0 / C1` 使用官方 `0-100` 分数
- 本地 `R0-R3` reward 会被统一换算为 `0-100`
- `Δ` 用 percentage points 表示

## 推荐操作顺序

1. 在 experiment worktree 里先做 `--dry-run`
2. 用 `scripts/run_round0_experiment_tmux.sh` 起正式实验
3. 用 `scripts/run_round0_monitor.sh` 起 dashboard
4. 平时主要看 dashboard
5. 只有需要看原始 stdout 时再 `tmux attach`

## 常见判断

看到下面这些信号，通常说明运行是健康的：

- `events.ndjson` 在持续增长
- dashboard 的 `current pair` 会随 launcher 前进
- pair 级别状态能从 `running` 变成 `succeeded` 或 `failed`
- `completed / total` 会递增

下面这些则值得立刻检查：

- `current pair` 长时间不变，且目录 mtime 不再更新
- dashboard 显示 `stalled`
- `pair_failed` 连续出现
- `tmux` session 消失

## 补充说明

- round-0 launcher 默认是串行跑 `(task, schema)`
- 单个 pair 失败不会中断后续 pair
- terminal round 现在不会再多跑一轮无用的 `role_a / role_b`
- 如果当前 run 是用旧 launcher 启动的，dashboard 也会优先按 stdout 元数据纠正总 pair 数，不会把 `1/21` 错显示成 `1/1`

## 相关文档

- 详细 launcher 参数说明：
  [`skillx-round0-launcher-usage-v0.1.md`](/Users/Jackal/iWorld/projects/skillX/docs/plans/skillx/skillx-round0-launcher-usage-v0.1.md)
- 并行开发和 worktree 规范：
  [`skillx-parallel-development-playbook-v0.1.md`](/Users/Jackal/iWorld/projects/skillX/docs/plans/skillx/skillx-parallel-development-playbook-v0.1.md)
