# SkillX Parallel Development Playbook v0.1

This document defines the default Git, worktree, and coding-session workflow for
active SkillX development.

The goal is simple:

- keep `main` stable and easy to sync
- allow multiple coding tasks and experiment runs in parallel
- avoid dirty shared workspaces
- make every committed result traceable to a branch, worktree, and commit SHA

## Core Rule

Treat `branch`, `worktree`, and `coding session` as separate things:

- `branch`: the change history for one task
- `worktree`: one local checkout for one branch
- `coding session`: one write-capable terminal or agent session attached to one worktree

The object that gets merged is the `branch`, not the `worktree`.

## Default Policy

- `main` is the integration branch.
- The repository root should stay on `main` and remain as clean as possible.
- Any task that writes files should default to a new `branch + worktree`.
- Any write-capable coding session should default to its own worktree.
- If unsure, create a new `branch + worktree` instead of reusing a dirty workspace.

## Preferred Directory Layout

The default project-local worktree directory is:

- `.worktrees/`

Branch names may contain `/`, and the worktree path should mirror the branch
path under `.worktrees/`.

Examples:

- branch `docs/2026-04-10-parallel-playbook`
  - worktree `.worktrees/docs/2026-04-10-parallel-playbook`
- branch `exp/2026-04-10-round0-3x7`
  - worktree `.worktrees/exp/2026-04-10-round0-3x7`
- branch `fix/2026-04-10-codex-auth-wrapper`
  - worktree `.worktrees/fix/2026-04-10-codex-auth-wrapper`

This repository ignores both `.worktrees/` and `worktrees/`.

## Branch Naming

Use short-lived task branches cut from the latest `origin/main`.

Recommended prefixes:

- `feat/` for feature work
- `fix/` for bug fixes
- `docs/` for documentation-only changes
- `exp/` for experiment runners, configs, or result-summary work
- `followup/` for scoped follow-up work after a merge
- `chore/` for repository maintenance

Recommended format:

- `<prefix>/<YYYY-MM-DD>-<slug>`

Examples:

- `feat/2026-04-10-round0-launcher-hardening`
- `docs/2026-04-10-parallel-development-playbook`
- `exp/2026-04-10-round0-3x7`

## Decision Matrix

| Scenario | New branch? | New worktree? | New coding session? | Default action |
| --- | --- | --- | --- | --- |
| Read-only inspection, result reading, or code review | No | No | No | Reuse current clean workspace |
| Monitoring an already running experiment without editing files | No | No | No | Reuse the existing experiment workspace |
| Any code, config, script, or doc edit | Yes | Yes | Yes | Create a new task branch from `origin/main` |
| Long-running experiment with frozen code or config | Usually yes | Yes | Yes | Use a dedicated worktree and record commit SHA |
| Uploading collaborator code or config changes | Yes | Yes | Yes | Review and merge through a branch and PR |
| Uploading collaborator raw results only | Usually yes | Usually yes | Optional | Commit summaries and metadata, not raw scratch outputs |
| Continuing the same unfinished task later | No, reuse existing task branch | No, reuse its worktree | Optional | Reopen the same task workspace |

## Session Policy

Use this rule of thumb:

- one write-capable coding session per worktree
- multiple read-only sessions are fine
- do not run two independent writing sessions in the same worktree

If two sessions may edit different files at the same time, they should still use
different worktrees unless they are intentionally sharing one branch and are
actively coordinated.

## Standard Start Workflow

For a new coding task:

```bash
git fetch origin
git worktree add .worktrees/feat/2026-04-10-example \
  -b feat/2026-04-10-example \
  origin/main
cd .worktrees/feat/2026-04-10-example
```

After that:

- make code or doc changes only inside that worktree
- run verification there
- commit and push from there

## Standard Continue Workflow

If a task branch already exists and still represents the same scope:

```bash
cd .worktrees/feat/2026-04-10-example
git status
git fetch origin
```

Reuse the existing worktree if:

- the task scope has not changed
- the workspace is still understandable
- no other writing session is actively using it

Otherwise, cut a new branch from `origin/main`.

## Standard Experiment Workflow

For a new experiment that changes code, configs, or launcher logic:

1. Create a dedicated `exp/*` branch from `origin/main`.
2. Create a dedicated worktree for that branch.
3. Run the experiment only from that worktree.
4. Record at minimum:
   - branch name
   - commit SHA
   - config path
   - output directory
   - model names
   - relevant seed or slice identifier

If the experiment is only monitoring or re-running an existing frozen commit, a
new branch is optional, but a dedicated worktree is still preferred.

## Result And Artifact Policy

Do not treat all outputs as equally commit-worthy.

Prefer committing:

- scripts
- configs
- summaries
- manifests
- evaluation tables
- plots selected for reporting

Prefer not committing:

- large transient logs
- local caches
- scratch directories
- temporary smoke outputs
- machine-specific auth or environment files

If a collaborator needs to contribute experiment results, the default path is:

1. store large raw artifacts outside Git or under ignored paths
2. open a branch with the summarized result files and metadata
3. merge that branch through `main`

## Merge And Cleanup Workflow

When a task is done:

```bash
git status
git add <files>
git commit -m "..."
git push -u origin <branch>
```

Then:

1. open or update a PR
2. merge into `main`
3. sync the local `main` workspace
4. remove the old worktree
5. delete the merged branch

Typical cleanup commands:

```bash
git worktree remove .worktrees/feat/2026-04-10-example
git branch -d feat/2026-04-10-example
git push origin --delete feat/2026-04-10-example
```

Only delete the remote branch after the merge is complete and no active session
still depends on it.

## Main Workspace Policy

Keep one clean `main` workspace as the default integration point.

Use that workspace for:

- pulling the latest `origin/main`
- quick read-only inspection
- final verification after merges
- preparing the next task branch

Do not use the `main` workspace as the default location for active parallel
coding or long-running experimental branches.

## Assistant Execution Contract

When the user says to use this playbook, the coding agent should:

1. classify the task as read-only, code change, docs change, config change,
   experiment run, or result intake
2. decide whether to reuse an existing task branch and worktree or create a new one
3. propose or create:
   - branch name
   - worktree path
   - working directory
   - whether a new coding session is required
4. avoid writing in a dirty shared workspace unless explicitly instructed
5. report the selected path before substantial edits

Default agent behavior:

- if files will be edited, create or use a dedicated task worktree
- if the current workspace is dirty and the task is distinct, do not reuse it
- if a long experiment will run, prefer a dedicated experiment worktree
- if two parallel sessions may both write, give them different worktrees

## How To Invoke This Playbook

When asking the coding agent to prepare work, use wording like:

- `Use the parallel development playbook. I need to edit the round-0 launcher and add tests.`
- `Use the parallel development playbook. I want to run a 3x7 experiment on frozen code.`
- `Use the parallel development playbook. I need to ingest collaborator result summaries for task X.`

The expected agent response should include:

- whether a new branch is needed
- whether a new worktree is needed
- the proposed branch name
- the proposed working directory
- whether a new coding session is recommended

## Quick Examples

### Example A: documentation-only task

- branch: `docs/2026-04-10-parallel-development-playbook`
- worktree: `.worktrees/docs/2026-04-10-parallel-development-playbook`
- new coding session: yes

### Example B: round-0 launcher hardening

- branch: `feat/2026-04-10-round0-launcher-hardening`
- worktree: `.worktrees/feat/2026-04-10-round0-launcher-hardening`
- new coding session: yes

### Example C: run a 3x7 experiment on frozen code

- branch: `exp/2026-04-10-round0-3x7`
- worktree: `.worktrees/exp/2026-04-10-round0-3x7`
- new coding session: yes
- commit only summaries or manifests unless the raw outputs are intentionally versioned

## Short Version

If the task writes files, the default is:

- new branch
- new worktree
- one write-capable session inside that worktree

If the task is read-only, reuse a clean existing workspace.
