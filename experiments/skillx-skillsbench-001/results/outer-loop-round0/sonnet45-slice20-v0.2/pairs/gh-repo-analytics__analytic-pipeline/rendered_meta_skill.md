[Common wrapper]
You are revising a Task skill, not directly solving the task.
Use the provided Meta schema as class-level guidance.
Your goal is to improve the Task skill for this task while preserving useful existing structure.

[Meta schema block]
Category: analytic-pipeline
Semantic intent: Run an ordered analysis pipeline where intermediate processing quality strongly affects final correctness.
Emphasize:
- stage decomposition and stage ordering
- explicit intermediate artifacts / checkpoints
- handoff integrity between stages
- final output tied back to pipeline evidence
Avoid:
- collapsing multiple sensitive transforms into one vague step
- skipping intermediate validation
- overly generic prose-only guidance
Expected good fit:
- scientific / signal / video / security analysis workflows
- ordered transformation + measurement tasks
Expected bad fit:
- simple one-shot artifact tasks
- pure code patch / compile-test loops
Hypothesized primary failure modes:
- unavailable in prompt-bank-v0.1; use task-local evidence instead
Meta schema seed guidance:
You are revising a skill for an analytic-pipeline task.
Optimize the skill as a staged workflow whose correctness depends on preserving structure between stages.

Prioritize:
1. stage-by-stage decomposition,
2. explicit intermediate artifacts or checks when a later step depends on earlier processing quality,
3. clear handoff rules between extraction, transformation, analysis, and final reporting,
4. a final output step that summarizes the pipeline result without dropping critical constraints.

Strengthen stage contracts before adding more generic scaffolding.
If the task is failing, assume stage-handoff weakness before assuming the task needs more general instructions.

[Task context block]
Task name: gh-repo-analytics
Task summary: I’m preparing a short "December community pulse" write-up for the `cli/cli` repository, and I want you to help me turn raw activity into a clean, meeting-ready summary. For the period 2024-12-01 to 2024-12-31, I want you to gather the following:
Task constraints:
- seed schema prior: retrieval-heavy-synthesis
- verifier mode: deterministic-output-contract
- workflow topology: staged-multi-step
- tool surface regime: tool-medium
- primary pattern: pipeline
- annotation confidence: high
- secondary patterns: tool-wrapper, reviewer
Task output requirements:
- verifier note: deterministic-output-contract
- current skill count: 1

[Current Task skill block]
Current Task skill:
## gh-cli
---
name: gh-cli
description: "The gh CLI is GitHub's official command line tool for interacting with GitHub repositories, issues, pull requests, and more. When needs to interact with GitHub repositories, issues, pull requests, and more, use this skill."
license: Proprietary. LICENSE.txt has complete terms
---

# GitHub CLI (gh)

Work seamlessly with GitHub from the command line.

## Usage

```
gh <command> <subcommand> [flags]
```

## Core Commands

```
  issue:      Manage issues
  pr:         Manage pull requests
  repo:       Create, clone, fork, and view repositories
  api:        Make an authenticated GitHub API request
  run:        View details about workflow runs
```

Use `gh <command> --help` for more information about a command.

---

## gh pr

Work with GitHub pull requests.

```
USAGE
  gh pr <command> [flags]

CORE COMMANDS
  checkout:   Check out a pull request in git
  checks:     Show CI status for a single pull request
  close:      Close a pull request
  comment:    Create a new pr comment
  create:     Create a pull request
  diff:       View changes in a pull request
  edit:       Edit a pull request
  list:       List and filter pull requests in this repository
  merge:      Merge a pull request
  ready:      Mark a pull request as ready for review
  reopen:     Reopen a pull request
  review:     Add a review to a pull request
  status:     Show status of relevant pull requests
  view:       View a pull request

FLAGS
  -R, --repo [HOST/]OWNER/REPO   Select another repository using the [HOST/]OWNER/REPO format

INHERITED FLAGS
  --help   Show help for command

ARGUMENTS
  A pull request can be supplied as argument in any of the following formats:
  - by number, e.g. "123";
  - by URL, e.g. "https://github.com/OWNER/REPO/pull/123"; or
  - by the name of its head branch, e.g. "patch-1" or "OWNER:patch-1".

EXAMPLES
  $ gh pr checkout 353
  $ gh pr create --fill
  $ gh pr view --web

LEARN MORE
  Use 'gh <command> <subcommand> --help' for more information about a command.
  Read the manual at https://cli.github.com/manual
```

---

## gh issue

Work with GitHub issues.

```
USAGE
  gh issue <command> [flags]

CORE COMMANDS
  close:      Close issue
  comment:    Create a new issue comment
  create:     Create a new issue
  delete:     Delete issue
  edit:       Edit an issue
  list:       List and filter issues in this repository
  reopen:     Reopen issue
  status:     Show status of relevant issues
  transfer:   Transfer issue to another repository
  view:       View an issue

FLAGS
  -R, --repo [HOST/]OWNER/REPO   Select another repository using the [HOST/]OWNER/REPO format

INHERITED FLAGS
  --help   Show help for command

ARGUMENTS
  An issue can be supplied as argument in any of the following formats:
  - by number, e.g. "123"; or
  - by URL, e.g. "https://github.com/OWNER/REPO/issues/123".

EXAMPLES
  $ gh issue list
  $ gh issue create --label bug
  $ gh issue view --web

LEARN MORE
  Use 'gh <command> <subcommand> --help' for more information about a command.
  Read the manual at https://cli.github.com/manual
```

---

## gh repo

Work with GitHub repositories.

```
USAGE
  gh repo <command> [flags]

CORE COMMANDS
  archive:    Archive a repository
  clone:      Clone a repository locally
  create:     Create a new repository
  delete:     Delete a repository
  edit:       Edit repository settings
  fork:       Create a fork of a repository
  list:       List repositories owned by user or organization
  rename:     Rename a repository
  sync:       Sync a repository
  view:       View a repository

INHERITED FLAGS
  --help   Show help for command

ARGUMENTS
  A repository can be supplied as an argument in any of the following formats:
  - "OWNER/REPO"
  - by URL, e.g. "https://github.com/OWNER/REPO"

EXAMPLES
  $ gh repo create
  $ gh repo clone cli/cli
  $ gh repo view --web
```

## Search Query Syntax

The `--search` flag uses GitHub search syntax. Full documentation: https://docs.github.com/en/search-github/getting-started-with-searching-on-github/understanding-the-search-syntax

### Comparison Operators

| Query | Description | Example |
|-------|-------------|---------|
| `>n` | Greater than | `stars:>1000` |
| `>=n` | Greater than or equal | `topics:>=5` |
| `<n` | Less than | `size:<10000` |
| `<=n` | Less than or equal | `stars:<=50` |

### Range Queries

| Query | Description | Example |
|-------|-------------|---------|
| `n..n` | Between range | `stars:10..50` |
| `n..*` | Greater than or equal | `stars:10..*` (same as `>=10`) |
| `*..n` | Less than or equal | `stars:*..10` (same as `<=10`) |

### Date Queries

Date format: `YYYY-MM-DD` (ISO8601). Optional time: `YYYY-MM-DDTHH:MM:SS+00:00`

| Query | Example |
|-------|---------|
| `>YYYY-MM-DD` | `created:>2024-04-29` — after April 29, 2024 |
| `>=YYYY-MM-DD` | `created:>=2024-04-01` — on or after April 1, 2024 |
| `<YYYY-MM-DD` | `pushed:<2024-07-05` — before July 5, 2024 |
| `<=YYYY-MM-DD` | `created:<=2024-07-04` — on or before July 4, 2024 |
| `YYYY-MM-DD..YYYY-MM-DD` | `created:2024-04-30..2024-07-04` — date range |
| `YYYY-MM-DD..*` | `created:2024-04-30..*` — on or after date |
| `*..YYYY-MM-DD` | `created:*..2024-07-04` — on or before date |

### Exclude Results

Prefix qualifier with `-` to exclude:

| Query | Example |
|-------|---------|
| `-QUALIFIER` | `stars:>10 -language:javascript` — exclude JavaScript repos |
| `NOT` | `hello NOT world` — has "hello" but not "world" |

### Usernames

| Query | Description |
|-------|-------------|
| `author:USERNAME` | Filter by specific user |
| `author:@me` | Filter by current user |
| `assignee:@me` | Assigned to current user |

### Queries with Whitespace

Use quotation marks for multi-word values:
- `label:"bug fix"` — label with space
- `cats NOT "hello world"` — exclude phrase

---

## JSON Output

Common fields for `--json`:

**PR**:

```
additions
assignees
author
baseRefName
body
changedFiles
closed
closedAt
comments
commits
createdAt
deletions
files
headRefName
headRepository
headRepositoryOwner
id
isCrossRepository
isDraft
labels
maintainerCanModify
mergeCommit
mergeStateStatus
mergeable
mergedAt
mergedBy
milestone
number
potentialMergeCommit
projectCards
reactionGroups
reviewDecision
reviewRequests
reviews
state
statusCheckRollup
title
updatedAt
url
```

**Issue**:

```
close
  comment
  create
  delete
  edit
  list
  reopen
  status
  transfer
  view
```

[Evidence block]
No Skills: `0`
With Skills: `0`
Delta: `0`
Failure summary: monthly GitHub PR/issue metrics require API-style retrieval, aggregation, and structured JSON reporting
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
