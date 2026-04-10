[Common wrapper]
You are revising a Task skill, not directly solving the task.
Use the provided Meta schema as class-level guidance.
Your goal is to improve the Task skill for this task while preserving useful existing structure.

[Meta schema block]
Category: methodology-guardrail
Semantic intent: Prevent premature or unsafe completion by enforcing fit-checks, abstention, and rule-aware judgment.
Emphasize:
- fit-check before commitment
- abstention / unknown / needs-clarification behavior
- rule hierarchy and anti-hallucination discipline
- reviewer-style judgment over direct eager generation
Avoid:
- premature completion
- overconfident synthesis when the task is underdetermined
- unnecessary multi-stage pipeline expansion
Expected good fit:
- taxonomy merge / fit-check tasks
- citation / rule / policy screening tasks
- abstention-sensitive validation tasks
Expected bad fit:
- straightforward artifact generation
- benchmark-driven engineering loops
Hypothesized primary failure modes:
- unavailable in prompt-bank-v0.1; use task-local evidence instead
Meta schema seed guidance:
You are revising a skill for a methodology-heavy guardrail task.
Optimize the skill for disciplined judgment, fit-checking, and safe refusal when needed.

Prioritize:
1. checking whether the task instance actually fits the intended method,
2. explicit abstain / unknown / request-clarification behavior,
3. reviewer-style comparison against criteria or rules,
4. preventing premature commitment to a single answer path.

If the task is failing, prefer stronger judgment discipline over adding more execution scaffolding.

[Task context block]
Task name: syzkaller-ppdev-syzlang
Task summary: Write syzkaller syzlang support for the Linux parallel port driver (ppdev). Right now /dev/parport* isn’t described. Create:
Task constraints:
- seed schema prior: artifact-generation
- verifier mode: deterministic-output-contract
- workflow topology: single-step-with-review
- tool surface regime: tool-medium
- primary pattern: generator
- annotation confidence: high
- secondary patterns: reviewer
Task output requirements:
- verifier note: deterministic-output-contract
- current skill count: 3

[Current Task skill block]
Current Task skill:
## syz-extract-constants
---
name: syz-extract-constants
description: Defining and extracting kernel constants for syzkaller syzlang descriptions
---

# Defining Constants in Syzlang

## Overview

Syzkaller needs to know the actual values of kernel constants (ioctl numbers, flags, etc.) to generate valid fuzzing programs. There are two ways to provide these values:

1. **Manual `.const` file** - Define constants directly in a companion file
2. **`syz-extract` tool** - Extract values from kernel source headers (requires kernel source)

## Method 1: Manual Constants File (Recommended when no kernel source)

Create a `.const` file alongside your `.txt` file with the constant values:

### File naming
- Syzlang description: `sys/linux/dev_ppdev.txt`
- Constants file: `sys/linux/dev_ppdev.txt.const`

### Constants file format

```
# Constants for your syzlang descriptions
arches = 386, amd64, arm, arm64, mips64le, ppc64le, riscv64, s390x
PPCLAIM = 28811
PPRELEASE = 28812
IEEE1284_MODE_NIBBLE = 0
IEEE1284_MODE_BYTE = 1
```

The `arches` line declares which architectures these constants are valid for. For architecture-independent constants (like ioctls), list all architectures.

### Calculating ioctl values

Linux ioctl numbers are encoded as:
- `_IO(type, nr)` = `(type << 8) | nr`
- `_IOR(type, nr, size)` = `(2 << 30) | (size << 16) | (type << 8) | nr`
- `_IOW(type, nr, size)` = `(1 << 30) | (size << 16) | (type << 8) | nr`
- `_IOWR(type, nr, size)` = `(3 << 30) | (size << 16) | (type << 8) | nr`

For ppdev (type='p'=0x70):
- `PPCLAIM = _IO('p', 0x8b)` = `0x708b` = `28811`

## Method 2: Using syz-extract (Requires kernel source)

If kernel source is available:

```bash
cd /opt/syzkaller

# Extract constants for a specific file
make extract TARGETOS=linux SOURCEDIR=/path/to/linux FILES=sys/linux/dev_ppdev.txt
```

**Note:** This environment does not include kernel source. Use Method 1 (manual constants file) instead.

## After Defining Constants

After creating the `.const` file, build syzkaller:

```bash
cd /opt/syzkaller
make descriptions  # Compiles descriptions + constants
make all           # Full build
```

## Common Errors

### "is defined for none of the arches"
This means the constant is used in the `.txt` file but not defined in the `.const` file.
- Add the missing constant to your `.const` file
- Ensure `arches` line lists the target architectures
PPCLAIM is defined for none of the arches
```

Solution: Run `make extract` with the correct kernel source path and FILES parameter.

### Missing headers
```
cannot find include file: uapi/linux/ppdev.h
```

Solution: Check the kernel source path and ensure headers are properly configured.

### "unknown file"
```
unknown file: sys/linux/dev_ppdev.txt
```

Solution: Use `make extract FILES=...` instead of calling `bin/syz-extract` directly.

## Example Workflow

1. Write the syzlang description file (`sys/linux/dev_ppdev.txt`)
2. Run `make extract TARGETOS=linux SOURCEDIR=/opt/linux/source FILES=sys/linux/dev_ppdev.txt`
3. Run `make generate` to regenerate Go code
4. Run `make` to build syzkaller
5. Test with `make descriptions` to verify everything compiles

## syzkaller-build-loop
---
name: syzkaller-build-loop
description: Full build workflow for adding new syscall descriptions to syzkaller
---

# Syzkaller Description Workflow

## Full Build Loop for New Descriptions

When adding new syscall descriptions, follow this workflow:

```bash
cd /opt/syzkaller

# 1. Write/edit your .txt file in sys/linux/

# 2. Create a .const file with constant values (see syz-extract-constants skill)
#    The .const file should be named: sys/linux/your_file.txt.const

# 3. Compile descriptions
make descriptions

# 4. Build syzkaller
make all
```

## Quick Rebuild (After Minor Edits)

If you only changed descriptions (not constants):

```bash
cd /opt/syzkaller
make descriptions   # Runs syz-sysgen to compile descriptions
```

If you add new constants, update the `.const` file first.

## Common Errors

### Unknown type
```
unknown type foo_bar
```
- Type not defined, or defined after first use
- Define all types before using them

### Constant not available / defined for none of the arches
```
SOME_CONST is defined for none of the arches
```
- The constant isn't in the `.const` file
- Add it to `sys/linux/your_file.txt.const` with the correct value

### Missing reference
```
undefined reference to 'some_type'
```
- Type defined in another file not being found
- Check includes or existing type definitions

## Exploring Existing Code

Find examples of patterns:
```bash
grep -r "pattern" /opt/syzkaller/sys/linux/
```

Useful searches:
- `resource fd_` - How other fd resources are defined
- `ioctl\$` - Ioctl definition patterns
- `read\$` / `write\$` - Read/write specializations
- `struct.*{` - Struct definition patterns

## Files to Reference

- `sys/linux/socket.txt` - Network types (ifreq_t, sockaddr, etc.)
- `sys/linux/sys.txt` - Basic syscall patterns
- `sys/linux/fs.txt` - File operations

## syzlang-ioctl-basics
---
name: syzlang-ioctl-basics
description: Syzkaller syzlang syntax basics for describing ioctl syscalls
---

# Syzlang Ioctl Basics

Syzkaller's description language (syzlang) describes syscalls for fuzzing.
Description files are located at `/opt/syzkaller/sys/linux/*.txt`.

## Syscall Syntax

Basic form:
```
syscall_name(arg1 type1, arg2 type2, ...) return_type
```

Specialized syscalls use `$` suffix:
```
syscall$VARIANT(args...) return_type
```

## Common Type Patterns

| Pattern | Meaning |
|---------|---------|
| `const[VALUE]` | Fixed constant value |
| `flags[flag_set, type]` | Bitfield from flag set |
| `ptr[direction, type]` | Pointer (in, out, inout) |
| `intptr[min:max]` | Integer pointer with range |
| `int8`, `int16`, `int32` | Fixed-size integers |
| `int16be`, `int32be` | Big-endian integers |
| `array[type]` | Variable-length array |
| `array[type, count]` | Fixed-length array |

## Ioctl Patterns

For ioctls with output:
```
ioctl$CMD(fd fd_type, cmd const[CMD], arg ptr[out, int32])
```

For ioctls with input:
```
ioctl$CMD(fd fd_type, cmd const[CMD], arg ptr[in, struct_type])
```

For simple value ioctls:
```
ioctl$CMD(fd fd_type, cmd const[CMD], arg intptr[0:1])
```

For ioctls using ifreq structure (from socket.txt):
```
ioctl$CMD(fd fd_type, cmd const[CMD], arg ptr[in, ifreq_t[flags[flag_set, int16]]])
```

## Struct Definitions

Structs must have typed fields:
```
struct_name {
    field1    type1
    field2    type2
}
```

## Flag Sets

Define reusable flag sets:
```
flag_set_name = FLAG1, FLAG2, FLAG3
```

Then use with `flags[flag_set_name, int16]`.

## Resources

File descriptor resources:
```
resource resource_name[fd]
```

## Read/Write Syscalls

For specialized read/write:
```
read$suffix(fd fd_type, buf ptr[out, buffer_type], count len[buf])
write$suffix(fd fd_type, buf ptr[in, buffer_type], count len[buf])
```

## Tips

1. Check existing files for patterns (e.g., `sys/linux/socket.txt`)
2. Run `make descriptions` after edits to validate syntax
3. Some constants only exist on certain architectures
4. Use `ptr[in, ...]` for input, `ptr[out, ...]` for output

[Evidence block]
No Skills: `0`
With Skills: `20`
Delta: `20`
Failure summary: create syzlang description files for ppdev ioctls; verified by make descriptions + make all compilation
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
