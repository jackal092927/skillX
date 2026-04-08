[Common wrapper]
You are revising a Task skill, not directly solving the task.
Use the provided Meta schema as class-level guidance.
Your goal is to improve the Task skill for this task while preserving useful existing structure.

[Meta schema block]
Category: engineering-composition
Semantic intent: Compose diagnosis, editing, execution, and verification into a disciplined engineering workflow.
Emphasize:
- diagnose -> patch/edit -> verify sequencing
- tool wrappers / execution interfaces / reproducible commands
- explicit precedence and dependency handling
- benchmark / build / test gate awareness
Avoid:
- vague reviewer-only advice without execution discipline
- unordered bundles of suggestions
- generic prose that does not tell the agent how to validate changes
Expected good fit:
- build fixes
- migrations
- code implementation tasks with compile/test/benchmark constraints
Expected bad fit:
- pure retrieval/synthesis
- simple output formatting tasks
Hypothesized primary failure modes:
- unavailable in prompt-bank-v0.1; use task-local evidence instead
Meta schema seed guidance:
You are revising a skill for an engineering-composition task.
Optimize the skill as a disciplined execution bundle, not as a generic writing prompt.

Prioritize:
1. diagnose-before-edit behavior,
2. explicit tool / command / wrapper interfaces where execution matters,
3. ordered patching with dependency awareness,
4. verification gates such as compile, test, or benchmark checks.

If the task fails, first ask whether the skill lacks:
- clear execution order,
- explicit interfaces,
- or a strong verify step.

Do not over-expand into broad research or synthesis unless the task truly requires it.

[Task context block]
Task name: setup-fuzzing-py
Task summary: You need to set up continuous fuzzing for some Python libraries. The libraries are available in the current directory `/app/`.
Task constraints:
- seed schema prior: engineering-composition
- verifier mode: deterministic-artifact-plus-stage-check
- workflow topology: staged-multi-step
- tool surface regime: tool-heavy-script-recommended
- primary pattern: pipeline
- annotation confidence: high
- secondary patterns: tool-wrapper, reviewer
Task output requirements:
- verifier note: deterministic-artifact-plus-stage-check
- current skill count: 3

[Current Task skill block]
Current Task skill:
## discover-important-function
---
name: discover-important-function
description: "When given a project codebase, this skill observes the important functions in the codebase for future action."
---

# Fuzz Target Localizer

## Purpose

This skill helps an agent quickly narrow a Python repository down to a small set of high-value fuzz targets. It produces:

- A ranked list of important files
- A ranked list of important functions and methods
- A summary of existing unit tests and inferred oracles
- A final shortlist of functions-under-test (FUTs) for fuzzing, each with a structured "note to self" for follow-up actions

## When to use

Use this skill when the user asks to:

- Find the best functions to fuzz in a Python package/library
- Identify parsers, decoders, validators, or boundary code that is fuzz-worthy
- Decide what to fuzz based on existing test coverage and API surface
- Produce a structured shortlist of fuzz targets with harness guidance
- Automating testing pipeline setup for a new or existing Python project.

Do not use this skill when the user primarily wants to fix a specific bug,
refactor code, or implement a harness immediately
(unless they explicitly ask for target selection first).

## Inputs expected from the environment

The agent should assume access to:

- Repository filesystem
- Ability to read files
- Ability to run local commands (optional but recommended)

Preferred repository listing command:

- Use `tree` to get a fast, high-signal view of repository structure (limit depth if needed).

If `tree` is not available, fall back to a recursive listing via other standard shell tooling.

## Outputs

Produce result:

A report in any format with the following information: - Localize important files - Localize important functions - Summarize existing unit tests - Decide function under test for fuzzing
This file should be placed in the root of the repository as `APIs.txt`,
which servers as the guidelines for future fuzzing harness implementation.

## Guardrails

- Prefer analysis and reporting over code changes.
- Do not modify source code unless the user explicitly requests changes.
- If running commands could be disruptive, default to read-only analysis.
- Avoid assumptions about runtime behavior; base conclusions on code and tests.
- Explicitly consider existing tests in the repo when selecting targets and deciding harness shape.
- Keep the final FUT shortlist small (typically 1–5).

---

# Localize important files

## Goal

Produce a ranked list of files that are most likely to contain fuzz-worthy logic: parsing, decoding, deserialization, validation, protocol handling, file/network boundaries, or native bindings.

## Procedure

1. Build a repository map
    - Start with a repository overview using `tree` to identify:
        - Root packages and layouts (src/ layout vs flat layout)
        - Test directories and configs
        - Bindings/native directories
        - Examples, docs, and tooling directories
    - Identify packaging and metadata files such as:
        - pyproject.toml
        - setup.cfg
        - setup.py
    - Identify test configuration and entry points:
        - tests/
        - conftest.py
        - pytest.ini
        - tox.ini
        - noxfile.py

2. Exclude low-value areas
    - Skip: virtual environments, build outputs, vendored code, documentation-only directories, examples-only directories, generated files.

3. Score files using explainable heuristics
   Assign a file a higher score when it matches more of these indicators:
    - Public API exposure: **init**.py re-exports, **all**, api modules
    - Input boundary keywords in file path or symbols: parse, load, dump, decode, encode, deserialize, serialize, validate, normalize, schema, protocol, message
    - Format handlers: json, yaml, xml, csv, toml, protobuf, msgpack, pickle
    - Regex-heavy or templating-heavy code
    - Native boundaries: ctypes, cffi, cython, extension modules, bindings
    - Central modules: high import fan-in across the package
    - Test adjacency: directly imported or heavily referenced by tests

4. Rank and select
    - Produce a Top-N list (default 10–30) with a short rationale per file.

## Output format

For each file:

- path
- score (relative, not necessarily normalized)
- rationale (2–5 bullets)
- indicators_hit (list)

---

# Localize important functions

## Goal

From the important files, identify and rank functions or methods that are strong fuzz targets while minimizing full-body reading until needed.

## Approach 1: AST-based header and docstring scan

For each localized Python file, parse it using Python’s `ast` module and extract only:

- Module docstring
- Function and async function headers (name, args, defaults, annotations, decorators)
- Class headers and method headers
- Docstrings for modules, classes, and functions/methods

Do not read full function bodies during the initial pass unless needed for disambiguation or final selection.

### Procedure

1. Build per-file declarations via AST
    - Parse the file with `ast`
    - Enumerate:
        - Top-level functions
        - Classes and their methods
        - Nested functions only if they are likely to be directly fuzzable via an exposed wrapper
    - For each symbol, collect:
        - Fully-qualified name
        - Signature details (as available from AST)
        - Decorators
        - Docstring (if present)
        - Location information (file, line range if available)

2. Generate an initial candidate set using headers and docstrings
   Prioritize functions/methods that:
    - Accept bytes, str, file-like objects, dicts, or user-controlled payloads
    - Convert between representations (raw ↔ structured)
    - Perform validation, normalization, parsing, decoding, deserialization
    - Touch filesystem/network/protocol boundaries
    - Call into native extensions or bindings
    - Clearly document strictness, schemas, formats, or error conditions

3. Use tests to refine candidate selection early
    - Before reading full bodies, check if tests reference these functions/modules:
        - Direct imports in tests
        - Fixtures that exercise particular entry points
        - Parameterizations over formats and inputs
    - Down-rank candidates that are already well-covered unless they are high-risk boundaries (parsers/native bindings).

4. Confirm with targeted reading only for top candidates
   For the top candidates (typically 10–20), read the full function bodies and capture:
    - Preconditions and assumptions
    - Internal helpers called
    - Error handling style and exception types
    - Any obvious invariants and postconditions
    - Statefulness and global dependencies

5. Rank and shortlist
   Rank candidates using an explainable rubric:
    - Input surface and reachability
    - Boundary risk (parsing/decoding/native)
    - Structural complexity (from targeted reading only)
    - Existing test coverage strength and breadth
    - Ease of harnessing

### Output format

For each function/method:

- qualname
- file
- line_range (if available)
- score (relative)
- rationale (2–6 bullets)
- dependencies (key helpers, modules, external state)
- harnessability (low/medium/high)

## Approach 2: Scanning all important files yourself

For each localized Python file, read the file contents directly to extract:

- Module docstring and overall structure
- Function and async function definitions (name, args, defaults, annotations, decorators)
- Class definitions and their methods
- Full function bodies and implementation details
- Docstrings for modules, classes, and functions/methods

This approach reads complete file contents, allowing for deeper analysis at the cost of higher token usage.

### Procedure

1. Read important files sequentially
    - For each file from the important files list, read the full contents.
    - Extract by direct inspection:
        - Top-level functions and their complete implementations
        - Classes and their methods with full bodies
        - Nested functions if they are exposed or called by public APIs
    - For each symbol, collect:
        - Fully-qualified name
        - Complete signature (from source text)
        - Decorators
        - Docstring (if present)
        - Full function body
        - Location information (file, approximate line range)

2. Generate an initial candidate set using full source analysis
   Prioritize functions/methods that:
    - Accept bytes, str, file-like objects, dicts, or user-controlled payloads
    - Convert between representations (raw ↔ structured)
    - Perform validation, normalization, parsing, decoding, deserialization
    - Touch filesystem/network/protocol boundaries
    - Call into native extensions or bindings
    - Contain complex control flow, loops, or recursive calls
    - Handle exceptions or edge cases
    - Clearly document strictness, schemas, formats, or error conditions

3. Analyze implementation details from full bodies
   For each candidate function, inspect the body for:
    - Preconditions and assumptions (explicit checks, assertions, early returns)
    - Internal helpers called and their purposes
    - Error handling style and exception types raised
    - Invariants and postconditions (explicit or implicit)
    - Statefulness and global dependencies
    - Input transformations and data flow
    - Native calls or external process invocations
    - Resource allocation and cleanup patterns

4. Use tests to refine candidate selection
    - Check if tests reference these functions/modules:
        - Direct imports in tests
        - Fixtures that exercise particular entry points
        - Parameterizations over formats and inputs
    - Down-rank candidates that are already well-covered unless they are high-risk boundaries (parsers/native bindings).
    - Note which aspects of each function are tested vs untested.

5. Rank and shortlist
   Rank candidates using an explainable rubric:
    - Input surface and reachability
    - Boundary risk (parsing/decoding/native)
    - Structural complexity (from full body analysis)
    - Existing test coverage strength and breadth
    - Ease of harnessing
    - Observable implementation risks (unsafe operations, unchecked inputs, complex state)

### Output format

For each function/method:

- qualname
- file
- line_range (if available)
- score (relative)
- rationale (2–6 bullets)
- dependencies (key helpers, modules, external state)
- harnessability (low/medium/high)
- implementation_notes (key observations from body analysis)

---

# Summarize existing unit tests

## Goal

Summarize what is already tested, infer test oracles, and identify gaps that fuzzing can complement.

## Hard requirement

Always inspect and incorporate existing tests in the repository when:

- Ranking functions
- Selecting FUTs
- Designing input models and oracles
- Proposing seed corpus sources

## Procedure

1. Inventory tests
    - Locate tests and their discovery configuration (pytest.ini, pyproject.toml, tox.ini, noxfile.py).
    - Enumerate test modules and map them to source modules via imports.
    - Identify shared fixtures and data factories (conftest.py, fixture files, test utilities).

2. Summarize test intent
   For each test module:
    - What behaviors are asserted
    - What inputs are used
    - What exceptions are expected
    - What invariants are implied

3. Infer oracles and properties
   Common fuzz-friendly oracles include:
    - Round-trip properties
    - Idempotence of normalization
    - Parser consistency across equivalent inputs
    - Deterministic output given deterministic input
    - No-crash and no-hang for malformed inputs

4. Identify coverage gaps
    - FUT candidates with no direct tests
    - Input classes not covered by tests (size extremes, malformed encodings, deep nesting, edge unicode, invalid schemas)
    - Code paths guarded by complex conditionals or exception handlers with no tests

## Output format

- test_map: module_under_test → tests → asserted behaviors
- inferred_oracles: list of reusable invariants with the functions they apply to
- gaps: ranked list of untested or weakly-tested candidates

---

# Decide function under test for fuzzing

## Goal

Select a final set of FUTs (typically 1–5) and produce a structured "note to self" for each FUT so the agent can proceed to harness implementation, corpus seeding, and fuzz execution.

## Selection criteria

Prefer FUTs that maximize:

- Security/robustness payoff (parsing, decoding, validation, native boundary)
- Reachability with minimal setup
- Low existing test assurance or narrow test input coverage
- High fuzzability (simple input channel, clear oracle or crash-only target)

Explicitly weigh:

- What tests already cover (and what they do not)
- What seeds can be extracted from tests, fixtures, and sample data

## Required "note to self" template

For each selected FUT, produce exactly this structure:

Fuzzing Target Note

- Target:
- File / location:
- Why this target:
    - Input surface:
    - Boundary or native considerations:
    - Complexity or path depth:
    - Current test gaps:
- Callable contract:
    - Required imports or initialization:
    - Preconditions:
    - Determinism concerns:
    - External dependencies:
- Input model:
    - Primary payload type:
    - Decoding or parsing steps:
    - Constraints to respect:
    - Edge classes to emphasize:
- Oracles:
    - Must-hold properties:
    - Acceptable exceptions:
    - Suspicious exceptions:
    - Crash-only vs correctness-checking:
- Harness plan:
    - Recommended approach:
    - Minimal harness signature:
    - Seed corpus ideas:
    - Timeouts and resource limits:
- Risk flags:
    - Native extension involved:
    - Potential DoS paths:
    - External I/O:
- Next actions:
    1.
    2.
    3.
    4.

## Output format

- selected_futs: list of chosen FUTs with brief justification
- notes_to_self: one "Fuzzing Target Note" per FUT

---

# Final JSON block

At the end of the report, include a JSON object with:

- important_files: [{path, score, rationale, indicators_hit}]
- important_functions: [{qualname, file, line_range, score, rationale, dependencies, harnessability}]
- test_summary: {test_map, inferred_oracles, gaps}
- selected_futs: [{qualname, file, line_range, justification}]
- notes_to_self: [{target_qualname, note}]

## fuzzing-python
---
name: fuzzing-python
description: "Creating fuzz driver for Python libraries using LibFuzzer. This skill is useful when agent needs to work with creating fuzz drivers / fuzz targets for Python project and libraries."
license: Apache License 2.0. https://github.com/google/atheris/blob/775b08fb1a781142540995e8a2817c48ffae343f/LICENSE
---

# Python Fuzzing Skill

## Setting up fuzzing for a Python project

Fuzz testing for Python projects are Atheris.
Atheris is a coverage-guided Python fuzzing engine.
It supports fuzzing of Python code, but also native extensions written for CPython.
Atheris is based off of libFuzzer.
When fuzzing native code,
Atheris can be used in combination with Address Sanitizer or Undefined Behavior Sanitizer to catch extra bugs.

You can install prebuilt versions of Atheris with pip:

```sh
pip3 install atheris
```

These wheels come with a built-in libFuzzer,
which is fine for fuzzing Python code.
If you plan to fuzz native extensions,
you may need to build from source to ensure the libFuzzer version in Atheris matches your Clang version.

## Using Atheris

### Example

```python
#!/usr/bin/python3

import atheris

with atheris.instrument_imports():
  import some_library
  import sys

def TestOneInput(data):
  some_library.parse(data)

atheris.Setup(sys.argv, TestOneInput)
atheris.Fuzz()
```

When fuzzing Python, Atheris will report a failure if the Python code under test throws an uncaught exception.

### Python coverage

Atheris collects Python coverage information by instrumenting bytecode.
There are 3 options for adding this instrumentation to the bytecode:

- You can instrument the libraries you import:

  ```python
  with atheris.instrument_imports():
    import foo
    from bar import baz
  ```

  This will cause instrumentation to be added to `foo` and `bar`, as well as
  any libraries they import.

- Or, you can instrument individual functions:

  ```python
  @atheris.instrument_func
  def my_function(foo, bar):
    print("instrumented")
  ```

- Or finally, you can instrument everything:

  ```python
  atheris.instrument_all()
  ```

  Put this right before `atheris.Setup()`. This will find every Python function
  currently loaded in the interpreter, and instrument it.
  This might take a while.

Atheris can additionally instrument regular expression checks, e.g. `re.search`.
To enable this feature, you will need to add:
`atheris.enabled_hooks.add("RegEx")`
To your script before your code calls `re.compile`.
Internally this will import the `re` module and instrument the necessary functions.
This is currently an experimental feature.

Similarly, Atheris can instrument str methods; currently only `str.startswith`
and `str.endswith` are supported. To enable this feature, add
`atheris.enabled_hooks.add("str")`. This is currently an experimental feature.

#### Why am I getting "No interesting inputs were found"?

You might see this error:

```
ERROR: no interesting inputs were found. Is the code instrumented for coverage? Exiting.
```

You'll get this error if the first 2 calls to `TestOneInput` didn't produce any
coverage events. Even if you have instrumented some Python code,
this can happen if the instrumentation isn't reached in those first 2 calls.
(For example, because you have a nontrivial `TestOneInput`). You can resolve
this by adding an `atheris.instrument_func` decorator to `TestOneInput`,
using `atheris.instrument_all()`, or moving your `TestOneInput` function into an
instrumented module.

### Visualizing Python code coverage

Examining which lines are executed is helpful for understanding the
effectiveness of your fuzzer. Atheris is compatible with
[`coverage.py`](https://coverage.readthedocs.io/): you can run your fuzzer using
the `coverage.py` module as you would for any other Python program. Here's an
example:

```bash
python3 -m coverage run your_fuzzer.py -atheris_runs=10000  # Times to run
python3 -m coverage html
(cd htmlcov && python3 -m http.server 8000)
```

Coverage reports are only generated when your fuzzer exits gracefully. This
happens if:

- you specify `-atheris_runs=<number>`, and that many runs have elapsed.
- your fuzzer exits by Python exception.
- your fuzzer exits by `sys.exit()`.

No coverage report will be generated if your fuzzer exits due to a
crash in native code, or due to libFuzzer's `-runs` flag (use `-atheris_runs`).
If your fuzzer exits via other methods, such as SIGINT (Ctrl+C), Atheris will
attempt to generate a report but may be unable to (depending on your code).
For consistent reports, we recommend always using
`-atheris_runs=<number>`.

If you'd like to examine coverage when running with your corpus, you can do
that with the following command:

```
python3 -m coverage run your_fuzzer.py corpus_dir/* -atheris_runs=$(( 1 + $(ls corpus_dir | wc -l) ))
```

This will cause Atheris to run on each file in `<corpus-dir>`, then exit.
Note: atheris use empty data set as the first input even if there is no empty file in `<corpus_dir>`.
Importantly, if you leave off the `-atheris_runs=$(ls corpus_dir | wc -l)`, no
coverage report will be generated.

Using coverage.py will significantly slow down your fuzzer, so only use it for
visualizing coverage; don't use it all the time.

### Fuzzing Native Extensions

In order for fuzzing native extensions to be effective, your native extensions
must be instrumented. See [Native Extension Fuzzing](https://github.com/google/atheris/blob/master/native_extension_fuzzing.md)
for instructions.

### Structure-aware Fuzzing

Atheris is based on a coverage-guided mutation-based fuzzer (LibFuzzer). This
has the advantage of not requiring any grammar definition for generating inputs,
making its setup easier. The disadvantage is that it will be harder for the
fuzzer to generate inputs for code that parses complex data types. Often the
inputs will be rejected early, resulting in low coverage.

Atheris supports custom mutators
[(as offered by LibFuzzer)](https://github.com/google/fuzzing/blob/master/docs/structure-aware-fuzzing.md)
to produce grammar-aware inputs.

Example (Atheris-equivalent of the
[example in the LibFuzzer docs](https://github.com/google/fuzzing/blob/master/docs/structure-aware-fuzzing.md#example-compression)):

```python
@atheris.instrument_func
def TestOneInput(data):
  try:
    decompressed = zlib.decompress(data)
  except zlib.error:
    return

  if len(decompressed) < 2:
    return

  try:
    if decompressed.decode() == 'FU':
      raise RuntimeError('Boom')
  except UnicodeDecodeError:
    pass
```

To reach the `RuntimeError` crash, the fuzzer needs to be able to produce inputs
that are valid compressed data and satisfy the checks after decompression.
It is very unlikely that Atheris will be able to produce such inputs: mutations
on the input data will most probably result in invalid data that will fail at
decompression-time.

To overcome this issue, you can define a custom mutator function (equivalent to
`LLVMFuzzerCustomMutator`).
This example produces valid compressed data. To enable Atheris to make use of
it, pass the custom mutator function to the invocation of `atheris.Setup`.

```python
def CustomMutator(data, max_size, seed):
  try:
    decompressed = zlib.decompress(data)
  except zlib.error:
    decompressed = b'Hi'
  else:
    decompressed = atheris.Mutate(decompressed, len(decompressed))
  return zlib.compress(decompressed)

atheris.Setup(sys.argv, TestOneInput, custom_mutator=CustomMutator)
atheris.Fuzz()
```

As seen in the example, the custom mutator may request Atheris to mutate data
using `atheris.Mutate()` (this is equivalent to `LLVMFuzzerMutate`).

You can experiment with [custom_mutator_example.py](example_fuzzers/custom_mutator_example.py)
and see that without the mutator Atheris would not be able to find the crash,
while with the mutator this is achieved in a matter of seconds.

```shell
$ python3 example_fuzzers/custom_mutator_example.py --no_mutator
[...]
#2      INITED cov: 2 ft: 2 corp: 1/1b exec/s: 0 rss: 37Mb
#524288 pulse  cov: 2 ft: 2 corp: 1/1b lim: 4096 exec/s: 262144 rss: 37Mb
#1048576        pulse  cov: 2 ft: 2 corp: 1/1b lim: 4096 exec/s: 349525 rss: 37Mb
#2097152        pulse  cov: 2 ft: 2 corp: 1/1b lim: 4096 exec/s: 299593 rss: 37Mb
#4194304        pulse  cov: 2 ft: 2 corp: 1/1b lim: 4096 exec/s: 279620 rss: 37Mb
[...]

$ python3 example_fuzzers/custom_mutator_example.py
[...]
INFO: found LLVMFuzzerCustomMutator (0x7f9c989fb0d0). Disabling -len_control by default.
[...]
#2      INITED cov: 2 ft: 2 corp: 1/1b exec/s: 0 rss: 37Mb
#3      NEW    cov: 4 ft: 4 corp: 2/11b lim: 4096 exec/s: 0 rss: 37Mb L: 10/10 MS: 1 Custom-
#12     NEW    cov: 5 ft: 5 corp: 3/21b lim: 4096 exec/s: 0 rss: 37Mb L: 10/10 MS: 7 Custom-CrossOver-Custom-CrossOver-Custom-ChangeBit-Custom-
 === Uncaught Python exception: ===
RuntimeError: Boom
Traceback (most recent call last):
  File "example_fuzzers/custom_mutator_example.py", line 62, in TestOneInput
    raise RuntimeError('Boom')
[...]
```

Custom crossover functions (equivalent to `LLVMFuzzerCustomCrossOver`) are also
supported. You can pass the custom crossover function to the invocation of
`atheris.Setup`. See its usage in [custom_crossover_fuzz_test.py](src/custom_crossover_fuzz_test.py).

#### Structure-aware Fuzzing with Protocol Buffers

[libprotobuf-mutator](https://github.com/google/libprotobuf-mutator) has
bindings to use it together with Atheris to perform structure-aware fuzzing
using protocol buffers.

See the documentation for
[atheris_libprotobuf_mutator](contrib/libprotobuf_mutator/README.md).

## Integration with OSS-Fuzz

Atheris is fully supported by [OSS-Fuzz](https://github.com/google/oss-fuzz), Google's continuous fuzzing service for open source projects. For integrating with OSS-Fuzz, please see [https://google.github.io/oss-fuzz/getting-started/new-project-guide/python-lang](https://google.github.io/oss-fuzz/getting-started/new-project-guide/python-lang).

## API

The `atheris` module provides three key functions: `instrument_imports()`, `Setup()` and `Fuzz()`.

In your source file, import all libraries you wish to fuzz inside a `with atheris.instrument_imports():`-block, like this:

```python
# library_a will not get instrumented
import library_a

with atheris.instrument_imports():
    # library_b will get instrumented
    import library_b
```

Generally, it's best to import `atheris` first and then import all other libraries inside of a `with atheris.instrument_imports()` block.

Next, define a fuzzer entry point function and pass it to `atheris.Setup()` along with the fuzzer's arguments (typically `sys.argv`). Finally, call `atheris.Fuzz()` to start fuzzing. You must call `atheris.Setup()` before `atheris.Fuzz()`.

#### `instrument_imports(include=[], exclude=[])`

- `include`: A list of fully-qualified module names that shall be instrumented.
- `exclude`: A list of fully-qualified module names that shall NOT be instrumented.

This should be used together with a `with`-statement. All modules imported in
said statement will be instrumented. However, because Python imports all modules
only once, this cannot be used to instrument any previously imported module,
including modules required by Atheris. To add coverage to those modules, use
`instrument_all()` instead.

A full list of unsupported modules can be retrieved as follows:

```python
import sys
import atheris
print(sys.modules.keys())
```

#### `instrument_func(func)`

- `func`: The function to instrument.

This will instrument the specified Python function and then return `func`. This
is typically used as a decorator, but can be used to instrument individual
functions too. Note that the `func` is instrumented in-place, so this will
affect all call points of the function.

This cannot be called on a bound method - call it on the unbound version.

#### `instrument_all()`

This will scan over all objects in the interpreter and call `instrument_func` on
every Python function. This works even on core Python interpreter functions,
something which `instrument_imports` cannot do.

This function is experimental.

#### `Setup(args, test_one_input, internal_libfuzzer=None)`

- `args`: A list of strings: the process arguments to pass to the fuzzer, typically `sys.argv`. This argument list may be modified in-place, to remove arguments consumed by the fuzzer.
  See [the LibFuzzer docs](https://llvm.org/docs/LibFuzzer.html#options) for a list of such options.
- `test_one_input`: your fuzzer's entry point. Must take a single `bytes` argument. This will be repeatedly invoked with a single bytes container.
- `internal_libfuzzer`: Indicates whether libfuzzer will be provided by atheris or by an external library (see [native_extension_fuzzing.md](./native_extension_fuzzing.md)). If unspecified, Atheris will determine this
  automatically. If fuzzing pure Python, leave this as `True`.

#### `Fuzz()`

This starts the fuzzer. You must have called `Setup()` before calling this function. This function does not return.

In many cases `Setup()` and `Fuzz()` could be combined into a single function, but they are
separated because you may want the fuzzer to consume the command-line arguments it handles
before passing any remaining arguments to another setup function.

#### `FuzzedDataProvider`

Often, a `bytes` object is not convenient input to your code being fuzzed. Similar to libFuzzer, we provide a FuzzedDataProvider to translate these bytes into other input forms.

You can construct the FuzzedDataProvider with:

```python
fdp = atheris.FuzzedDataProvider(input_bytes)
```

The FuzzedDataProvider then supports the following functions:

```python
def ConsumeBytes(count: int)
```

Consume `count` bytes.

```python
def ConsumeUnicode(count: int)
```

Consume unicode characters. Might contain surrogate pair characters, which according to the specification are invalid in this situation. However, many core software tools (e.g. Windows file paths) support them, so other software often needs to too.

```python
def ConsumeUnicodeNoSurrogates(count: int)
```

Consume unicode characters, but never generate surrogate pair characters.

```python
def ConsumeString(count: int)
```

Alias for `ConsumeBytes` in Python 2, or `ConsumeUnicode` in Python 3.

```python
def ConsumeInt(int: bytes)
```

Consume a signed integer of the specified size (when written in two's complement notation).

```python
def ConsumeUInt(int: bytes)
```

Consume an unsigned integer of the specified size.

```python
def ConsumeIntInRange(min: int, max: int)
```

Consume an integer in the range [`min`, `max`].

```python
def ConsumeIntList(count: int, bytes: int)
```

Consume a list of `count` integers of `size` bytes.

```python
def ConsumeIntListInRange(count: int, min: int, max: int)
```

Consume a list of `count` integers in the range [`min`, `max`].

```python
def ConsumeFloat()
```

Consume an arbitrary floating-point value. Might produce weird values like `NaN` and `Inf`.

```python
def ConsumeRegularFloat()
```

Consume an arbitrary numeric floating-point value; never produces a special type like `NaN` or `Inf`.

```python
def ConsumeProbability()
```

Consume a floating-point value in the range [0, 1].

```python
def ConsumeFloatInRange(min: float, max: float)
```

Consume a floating-point value in the range [`min`, `max`].

```python
def ConsumeFloatList(count: int)
```

Consume a list of `count` arbitrary floating-point values. Might produce weird values like `NaN` and `Inf`.

```python
def ConsumeRegularFloatList(count: int)
```

Consume a list of `count` arbitrary numeric floating-point values; never produces special types like `NaN` or `Inf`.

```python
def ConsumeProbabilityList(count: int)
```

Consume a list of `count` floats in the range [0, 1].

```python
def ConsumeFloatListInRange(count: int, min: float, max: float)
```

Consume a list of `count` floats in the range [`min`, `max`]

```python
def PickValueInList(l: list)
```

Given a list, pick a random value

```python
def ConsumeBool()
```

Consume either `True` or `False`.

## Important considerations for fuzz targets

Some important things to remember about fuzz targets:

- The fuzzing engine will execute the fuzz target many times with different inputs in the same process.
- It must tolerate any kind of input (empty, huge, malformed, etc).
- It must not exit() on any input.
- It may use threads but ideally all threads should be joined at the end of the function.
- It must be as deterministic as possible. Non-determinism (e.g. random decisions not based on the input bytes) will make fuzzing inefficient.
- It must be fast. Try avoiding cubic or greater complexity, logging, or excessive memory consumption.
- Ideally, it should not modify any global state (although that’s not strict).
- Usually, the narrower the target the better. E.g. if your target can parse several data formats, split it into several targets, one per format.

## setup-env
---
name: setup-env
description: "When given a Python project codebase, this skill helps the agent to set up virtual environments, install dependencies, and run scripts."
---

# Skill: Use uv to manage Python environments

## Scope

1. Create a virtual environment
2. Install dependencies
3. Run Python scripts/commands

Assume `uv` is already available on PATH.

---

## Workflow selection

- If `pyproject.toml` exists: use **project workflow** (`uv sync`, `uv run`)
- Else if `requirements.txt` exists: use **pip workflow** (`uv venv`, `uv pip install -r ...`, `.venv/bin/python ...`)
- Else: stop with an error ("No pyproject.toml or requirements.txt found.")

---

## Project workflow (pyproject.toml)

### Create venv + install dependencies

From the repo root (where `pyproject.toml` is):

- `uv sync`

Notes:

- uv maintains a persistent project environment at `.venv` and installs deps there.

### Run scripts / commands (preferred)

Always run within the project environment:

- `uv run -- python <script.py> [args...]`
- `uv run -- python -m <module> [args...]`

Notes:

- `uv run` executes inside the project environment and ensures it is up-to-date.

---

## Pip workflow (requirements.txt)

### Create venv

From the repo root:

- `uv venv` # creates `.venv` by default

### Install dependencies

- `uv pip install -r requirements.txt`

### Run scripts / commands

Run using the venv interpreter directly (no activation required):

- `.venv/bin/python <script.py> [args...]`
- `.venv/bin/python -m <module> [args...]`

(uv will also automatically find and use the default `.venv` in subsequent invocations when you use `uv pip ...` commands.)

---

## Minimal sanity checks (optional)

- `test -x .venv/bin/python`
- `uv pip list` (verify packages installed)

[Evidence block]
No Skills: `0`
With Skills: `9.8`
Delta: `9.8`
Failure summary: discover libraries, analyze functions, write fuzz drivers, set up venvs, run 10s fuzzing validation; 5-step ordered workflow
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
