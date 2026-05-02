[Common wrapper]
You are revising a Task skill, not directly solving the task.
Use the provided Meta schema as class-level guidance.
Your goal is to improve the Task skill for this task while preserving useful existing structure.

[Meta schema block]
Category: engineering-composition
Semantic intent: Compose diagnosis, editing, execution, and verification into a disciplined engineering workflow.
Emphasize:
- diagnose -> patch/edit -> verify sequencing
- tool wrappers and execution infrastructure when build/test/deployment gates matter, not just script orchestration
- explicit precedence and dependency handling
- benchmark / build / test gate awareness
- extract task-specific engineering constraints (build/compile/test/deploy requirements) before adding procedural scaffolding
- make the staged-multi-step workflow assumption explicit when rendering task guidance
- articulate why engineering verification gates (compile/test/benchmark) are load-bearing for this task vs pure output validation
Avoid:
- vague advice that doesn't specify which engineering gates (compile/test/deploy/benchmark) to validate against
- unordered bundles of suggestions
- generic prose that does not tell the agent how to validate changes
- treating all pipeline-structured tasks as engineering tasks without identifying engineering verification gates
Expected good fit:
- build fixes
- migrations
- code implementation tasks with compile/test/benchmark constraints
- tasks requiring code modification with cross-file dependency tracking or compilation
Expected bad fit:
- pure retrieval/synthesis
- simple output formatting tasks
- pure analytical pipelines where the pipeline output is the final deliverable
- tasks with only output-contract or result verification, no build/compile/test gates
Hypothesized primary failure modes:
- unavailable in prompt-bank-v0.1; use task-local evidence instead
Meta schema seed guidance:
You are revising a skill for a engineering-composition task.
Schema intent: Compose diagnosis, editing, execution, and verification into a disciplined engineering workflow.

Outer-loop update mode: differentiating. Keep the Render layer fixed and change only schema-level guidance.

Prioritize:
1. diagnose -> patch/edit -> verify sequencing
2. tool wrappers and execution infrastructure when build/test/deployment gates matter, not just script orchestration
3. explicit precedence and dependency handling
4. benchmark / build / test gate awareness
5. extract task-specific engineering constraints (build/compile/test/deploy requirements) before adding procedural scaffolding
6. make the staged-multi-step workflow assumption explicit when rendering task guidance
7. articulate why engineering verification gates (compile/test/benchmark) are load-bearing for this task vs pure output validation

Avoid:
1. vague advice that doesn't specify which engineering gates (compile/test/deploy/benchmark) to validate against
2. unordered bundles of suggestions
3. generic prose that does not tell the agent how to validate changes
4. treating all pipeline-structured tasks as engineering tasks without identifying engineering verification gates

Good fit when:
- build fixes
- migrations
- code implementation tasks with compile/test/benchmark constraints
- tasks requiring code modification with cross-file dependency tracking or compilation

Bad fit when:
- pure retrieval/synthesis
- simple output formatting tasks
- pure analytical pipelines where the pipeline output is the final deliverable
- tasks with only output-contract or result verification, no build/compile/test gates

Primary failure modes to guard against:
- boundary ambiguity with analytic-pipeline: losing tasks that have pipeline structure but lack clear engineering verification gates

Regenerate task-specific skill guidance from these slots; do not invent a new policy outside them.

[Task context block]
Task name: court-form-filling
Task summary: Fill the California Small Claims Court form at `/root/sc100-blank.pdf` based on the case description below, and save the filled one to `/root/sc100-filled.pdf`. Only fill in the necessary fields and leave the court-filled, optional fields or fields not mentioned in the case description below empty. Use this date format: xxxx-xx-xx. Case Description: I am Joyce He. It's my first time suing by small claims. I live in 655 S Fair Oaks Ave, Sunnyvale, CA 94086, my phone # is 4125886066, email: he1998@gmail.com. I want to sue Zhi Chen  in 299 W Washington Ave, Sunnyvale, CA 94086. His phone #: 5125658878. He failed to return my security deposit of amount $1500 based on the signed roommate sublease contract after moving out. This situation happened from 2025-09-30 until 2026-01-19.
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
- current skill count: 1

[Current Task skill block]
Current Task skill:
## pdf
---
name: pdf
description: Comprehensive PDF manipulation toolkit for extracting text and tables, creating new PDFs, merging/splitting documents, and handling forms. When Claude needs to fill in a PDF form or programmatically process, generate, or analyze PDF documents at scale.
license: Proprietary. LICENSE.txt has complete terms
---

# PDF Processing Guide

## Overview

This guide covers essential PDF processing operations using Python libraries and command-line tools. For advanced features, JavaScript libraries, and detailed examples, see reference.md. If you need to fill out a PDF form, read forms.md and follow its instructions.

## Quick Start

```python
from pypdf import PdfReader, PdfWriter

# Read a PDF
reader = PdfReader("document.pdf")
print(f"Pages: {len(reader.pages)}")

# Extract text
text = ""
for page in reader.pages:
    text += page.extract_text()
```

## Python Libraries

### pypdf - Basic Operations

#### Merge PDFs
```python
from pypdf import PdfWriter, PdfReader

writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf", "doc3.pdf"]:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)

with open("merged.pdf", "wb") as output:
    writer.write(output)
```

#### Split PDF
```python
reader = PdfReader("input.pdf")
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    with open(f"page_{i+1}.pdf", "wb") as output:
        writer.write(output)
```

#### Extract Metadata
```python
reader = PdfReader("document.pdf")
meta = reader.metadata
print(f"Title: {meta.title}")
print(f"Author: {meta.author}")
print(f"Subject: {meta.subject}")
print(f"Creator: {meta.creator}")
```

#### Rotate Pages
```python
reader = PdfReader("input.pdf")
writer = PdfWriter()

page = reader.pages[0]
page.rotate(90)  # Rotate 90 degrees clockwise
writer.add_page(page)

with open("rotated.pdf", "wb") as output:
    writer.write(output)
```

### pdfplumber - Text and Table Extraction

#### Extract Text with Layout
```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
```

#### Extract Tables
```python
with pdfplumber.open("document.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for j, table in enumerate(tables):
            print(f"Table {j+1} on page {i+1}:")
            for row in table:
                print(row)
```

#### Advanced Table Extraction
```python
import pandas as pd

with pdfplumber.open("document.pdf") as pdf:
    all_tables = []
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if table:  # Check if table is not empty
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)

# Combine all tables
if all_tables:
    combined_df = pd.concat(all_tables, ignore_index=True)
    combined_df.to_excel("extracted_tables.xlsx", index=False)
```

### reportlab - Create PDFs

#### Basic PDF Creation
```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

c = canvas.Canvas("hello.pdf", pagesize=letter)
width, height = letter

# Add text
c.drawString(100, height - 100, "Hello World!")
c.drawString(100, height - 120, "This is a PDF created with reportlab")

# Add a line
c.line(100, height - 140, 400, height - 140)

# Save
c.save()
```

#### Create PDF with Multiple Pages
```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("report.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = []

# Add content
title = Paragraph("Report Title", styles['Title'])
story.append(title)
story.append(Spacer(1, 12))

body = Paragraph("This is the body of the report. " * 20, styles['Normal'])
story.append(body)
story.append(PageBreak())

# Page 2
story.append(Paragraph("Page 2", styles['Heading1']))
story.append(Paragraph("Content for page 2", styles['Normal']))

# Build PDF
doc.build(story)
```

## Command-Line Tools

### pdftotext (poppler-utils)
```bash
# Extract text
pdftotext input.pdf output.txt

# Extract text preserving layout
pdftotext -layout input.pdf output.txt

# Extract specific pages
pdftotext -f 1 -l 5 input.pdf output.txt  # Pages 1-5
```

### qpdf
```bash
# Merge PDFs
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf

# Split pages
qpdf input.pdf --pages . 1-5 -- pages1-5.pdf
qpdf input.pdf --pages . 6-10 -- pages6-10.pdf

# Rotate pages
qpdf input.pdf output.pdf --rotate=+90:1  # Rotate page 1 by 90 degrees

# Remove password
qpdf --password=mypassword --decrypt encrypted.pdf decrypted.pdf
```

### pdftk (if available)
```bash
# Merge
pdftk file1.pdf file2.pdf cat output merged.pdf

# Split
pdftk input.pdf burst

# Rotate
pdftk input.pdf rotate 1east output rotated.pdf
```

## Common Tasks

### Extract Text from Scanned PDFs
```python
# Requires: pip install pytesseract pdf2image
import pytesseract
from pdf2image import convert_from_path

# Convert PDF to images
images = convert_from_path('scanned.pdf')

# OCR each page
text = ""
for i, image in enumerate(images):
    text += f"Page {i+1}:\n"
    text += pytesseract.image_to_string(image)
    text += "\n\n"

print(text)
```

### Add Watermark
```python
from pypdf import PdfReader, PdfWriter

# Create watermark (or load existing)
watermark = PdfReader("watermark.pdf").pages[0]

# Apply to all pages
reader = PdfReader("document.pdf")
writer = PdfWriter()

for page in reader.pages:
    page.merge_page(watermark)
    writer.add_page(page)

with open("watermarked.pdf", "wb") as output:
    writer.write(output)
```

### Extract Images
```bash
# Using pdfimages (poppler-utils)
pdfimages -j input.pdf output_prefix

# This extracts all images as output_prefix-000.jpg, output_prefix-001.jpg, etc.
```

### Password Protection
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()

for page in reader.pages:
    writer.add_page(page)

# Add password
writer.encrypt("userpassword", "ownerpassword")

with open("encrypted.pdf", "wb") as output:
    writer.write(output)
```

## Quick Reference

| Task | Best Tool | Command/Code |
|------|-----------|--------------|
| Merge PDFs | pypdf | `writer.add_page(page)` |
| Split PDFs | pypdf | One page per file |
| Extract text | pdfplumber | `page.extract_text()` |
| Extract tables | pdfplumber | `page.extract_tables()` |
| Create PDFs | reportlab | Canvas or Platypus |
| Command line merge | qpdf | `qpdf --empty --pages ...` |
| OCR scanned PDFs | pytesseract | Convert to image first |
| Fill PDF forms | pdf-lib or pypdf (see forms.md) | See forms.md |

## Next Steps

- For advanced pypdfium2 usage, see reference.md
- For JavaScript libraries (pdf-lib), see reference.md
- If you need to fill out a PDF form, follow the instructions in forms.md
- For troubleshooting guides, see reference.md

[Evidence block]
No Skills: `20`
With Skills: `20`
Delta: `0`
Failure summary: field-constrained PDF artifact; required vs omitted form sections and no-extra-fill discipline dominate
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

[Outer-loop candidate block]
Source round: outer-loop-round0
Next round: outer-loop-round1
Candidate id: engineering-composition::round1::differentiating
Candidate mode: differentiating
Pair reason: full_matrix_eval
Next pair plan mode: full_matrix
Use this as a candidate schema rerun, not as an accepted final schema.
