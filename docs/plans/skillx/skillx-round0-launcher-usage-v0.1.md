# SkillX Round-0 Launcher 使用说明

本文档说明如何使用 `scripts/launch_skillx_round0.py` 启动 SkillX 的 round-0 outer-loop 任务。

## 目的

这个 launcher 的目标是：

- 固定读取当前 round-0 候选 task list
- 默认对每个选中的 task 自动展开全部 `7` 个 schema
- 你平时只需要关心“选哪些 task”，不需要手动拼 `task × schema`

当前默认读取的 task slice 是：

- `experiments/skillx-skillsbench-001/results/official-task-results/sonnet45-round0-candidate-slice-v0.2.json`

当前默认读取的 materialized round-0 root 是：

- `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-slice20-v0.2`

## 运行语义

launcher 默认按 `(task, schema)` 串行执行。

- 不并发
- 某一个 pair 失败时，不会中断后续 pair
- 每次 launcher 运行都会写一份持久化 summary 和事件日志

日志目录默认在：

- `<materialized-root>/launcher_logs/<run-label>/`

其中：

- 如果传了 `--output-suffix smoke5`
  - launcher log 目录就是 `launcher_logs/smoke5/`
- 如果没传 `--output-suffix`
  - launcher 会自动生成一个时间戳目录

当前主要会生成：

- `summary.json`
  - 本次所有 pair 的最终状态汇总
- `events.ndjson`
  - 逐 pair 的开始/成功/失败事件流

注意：

- launcher 会尽量继续跑完剩余 pair
- 但如果本次运行中存在任何失败，launcher 最终退出码仍然会是非 `0`
- 也就是说：
  - “不中断后续任务”
  - 不等于 “整批运行被判定为成功”

## 默认行为

如果你不传 schema，launcher 会自动：

1. 从固定 task slice 里按顺序选 task
2. 对每个 task 展开当前 manifest 里的全部 schema
3. 为每个 `(task, schema)` 生成并执行一条 refine 命令
4. refine 命令内部会走：
   - `uv run python`
   - `scripts/run_skillx_refine_benchmark.py`
   - `C1` 作为 starting skillpack
   - 显式 protocol path
   - `c4ar` orchestration mode

所以：

- `1` 的意思其实就是 `1 × 7`
- `3` 的意思其实就是 `3 × 7`
- 不传数字时，默认就是把当前 slice 里的全部 task 都跑掉

## 常用命令

### 1. 查看 task 顺序

```bash
uv run python scripts/launch_skillx_round0.py --list-tasks
```

说明：

- 这里显示的是固定 slice 的顺序
- 后面的 `--task-index` 就按这个顺序取值

### 2. 跑前 N 个 task

```bash
uv run python scripts/launch_skillx_round0.py 1
uv run python scripts/launch_skillx_round0.py 3
uv run python scripts/launch_skillx_round0.py 20
```

说明：

- `1` = 跑第一个 task 的全部 schema
- `3` = 跑前三个 task 的全部 schema
- `20` = 跑当前 slice 的前 20 个 task

### 3. 跑某个指定 task

```bash
uv run python scripts/launch_skillx_round0.py --task civ6-adjacency-optimizer
```

说明：

- 这会跑 `civ6-adjacency-optimizer` 的全部 schema
- 也就是一个标准的 `1 × 7`

### 4. 一次跑多个指定 task

```bash
uv run python scripts/launch_skillx_round0.py \
  --task civ6-adjacency-optimizer \
  --task earthquake-phase-association
```

说明：

- 可以重复传多个 `--task`
- launcher 会按固定 slice 的原始顺序去重

### 5. 用 task index 选 task

```bash
uv run python scripts/launch_skillx_round0.py --task-index 2
uv run python scripts/launch_skillx_round0.py --task-index 2 --task-index 5
```

说明：

- `--task-index` 是 `1-based`
- 也就是说：
  - `1` 表示 `--list-tasks` 里第 1 个 task
  - `2` 表示第 2 个 task

### 6. 混合 task id 和 task index

```bash
uv run python scripts/launch_skillx_round0.py \
  --task civ6-adjacency-optimizer \
  --task-index 2
```

说明：

- 这会取两者并集
- 仍然按固定 slice 顺序展开

### 7. 只打印命令，不实际执行

```bash
uv run python scripts/launch_skillx_round0.py --dry-run 3
uv run python scripts/launch_skillx_round0.py --dry-run --task civ6-adjacency-optimizer
```

说明：

- 推荐先用 `--dry-run` 检查一下即将运行哪些 pair
- 这对于确认 task 选择范围很有用

### 8. 使用新的输出目录后缀

```bash
uv run python scripts/launch_skillx_round0.py \
  --task civ6-adjacency-optimizer \
  --output-suffix smoke4
```

说明：

- 默认输出目录是 `refine_run`
- 如果传了 `--output-suffix smoke4`，则输出目录会变成 `refine_run_smoke4`
- 对应的 `run-id` 也会加上 `__smoke4`
- 这个参数很适合：
  - 不想覆盖已有 run
  - 想做 smoke test
  - 想并排保留多次试跑结果
  - 想让 launcher log 目录也稳定落到同名后缀下

## 推荐用法

### 先做 dry-run

```bash
uv run python scripts/launch_skillx_round0.py --dry-run 1
```

### 再做单 task smoke test

```bash
uv run python scripts/launch_skillx_round0.py \
  --task civ6-adjacency-optimizer \
  --output-suffix smoke5
```

### 再扩大到前 3 个 task

```bash
uv run python scripts/launch_skillx_round0.py 3
```

### 最后再跑完整 slice

```bash
uv run python scripts/launch_skillx_round0.py
```

## 参数说明

### 位置参数

- `target`
  - 如果是数字，比如 `3`
    - 表示跑固定 task slice 里的前 `3` 个 task
  - 如果不是数字，比如 `civ6-adjacency-optimizer`
    - 表示把它当成一个 task id

### 主要选项

- `--task`
  - 指定某个 task id
  - 可重复传入

- `--task-index`
  - 指定 task slice 中的第几个 task
  - `1-based`
  - 可重复传入

- `--dry-run`
  - 只打印命令，不执行

- `--list-tasks`
  - 打印固定 task list 的顺序并退出

- `--output-suffix`
  - 给本次运行的输出目录和 run-id 加后缀
  - 适合 smoke / retry / 避免覆盖

### 低层参数

通常不需要改：

- `--task-slice`
- `--materialized-root`
- `--oauth-file`
- `--refine-protocol-path`
- `--bundle-contract-path`
- `--round-budget`
- `--agent`
- `--model`

## Help 速查

查看 help：

```bash
uv run python scripts/launch_skillx_round0.py --help
```

当前 help 输出摘要如下：

```text
usage: launch_skillx_round0.py [-h] [--task TASK] [--task-index TASK_INDEX]
                               [--dry-run] [--list-tasks]
                               [--task-slice TASK_SLICE]
                               [--materialized-root MATERIALIZED_ROOT]
                               [--oauth-file OAUTH_FILE]
                               [--refine-protocol-path REFINE_PROTOCOL_PATH]
                               [--bundle-contract-path BUNDLE_CONTRACT_PATH]
                               [--round-budget ROUND_BUDGET] [--agent AGENT]
                               [--model MODEL] [--output-suffix OUTPUT_SUFFIX]
                               [target]
```

重点可以记成下面这几个：

- `uv run python scripts/launch_skillx_round0.py --list-tasks`
- `uv run python scripts/launch_skillx_round0.py 3`
- `uv run python scripts/launch_skillx_round0.py --task <task-id>`
- `uv run python scripts/launch_skillx_round0.py --task-index <n>`
- `uv run python scripts/launch_skillx_round0.py --dry-run ...`
- `uv run python scripts/launch_skillx_round0.py --output-suffix smokeX ...`

## 备注

1. 当前 launcher 默认总是按“选 task -> 自动展开全部 schema”的方式工作。
2. 也就是说，平时不需要手动思考 `1×7 / 3×7 / 20×7` 里的 `×7`。
3. 如果后面 schema bank 数量变化，launcher 会直接从 materialized manifest 里读取当前 schema 列表，不需要手动改命令。
