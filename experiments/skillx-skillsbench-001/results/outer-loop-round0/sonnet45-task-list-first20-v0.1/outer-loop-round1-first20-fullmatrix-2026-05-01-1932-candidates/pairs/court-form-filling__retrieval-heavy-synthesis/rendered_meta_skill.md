[Common wrapper]
You are revising a Task skill, not directly solving the task.
Use the provided Meta schema as class-level guidance.
Your goal is to improve the Task skill for this task while preserving useful existing structure.

[Meta schema block]
Category: retrieval-heavy-synthesis
Semantic intent: Gather evidence from sources, compress it correctly, and synthesize an output without dropping support.
Emphasize:
- retrieval plan that explicitly identifies external sources and access paths before processing
- evidence tracking with explicit provenance chains linking each claim to its supporting external source
- compression that preserves source citations and provenance chains alongside synthesized output
- abstain / unknown behavior when evidence is insufficient
- external source grounding discipline - explicitly identify and track which external source (file, API, database, document) supports each claim
- explicit provenance chains - maintain traceable mappings from output claims back to specific input evidence locations
- multi-source reconciliation - handle conflicting or partial evidence across multiple external sources with explicit conflict resolution
Avoid:
- unsupported synthesis
- hallucinated joins across sources
- excessive workflow scaffolding that obscures evidence use
- treating staged data processing as retrieval-synthesis when the task does not require external source provenance tracking
Expected good fit:
- information search
- handbook / database grounded QA
- report or answer generation from external sources
- tasks requiring multi-source evidence reconciliation with explicit provenance tracking
Expected bad fit:
- simulator/control tasks
- code patch workflows
- staged multi-step data processing pipelines without explicit external source grounding requirements
- tasks where the primary challenge is workflow orchestration rather than evidence provenance discipline
Hypothesized primary failure modes:
- unavailable in prompt-bank-v0.1; use task-local evidence instead
Meta schema seed guidance:
You are revising a skill for a retrieval-heavy-synthesis task.
Schema intent: Gather evidence from sources, compress it correctly, and synthesize an output without dropping support.

Outer-loop update mode: differentiating. Keep the Render layer fixed and change only schema-level guidance.

Prioritize:
1. retrieval plan that explicitly identifies external sources and access paths before processing
2. evidence tracking with explicit provenance chains linking each claim to its supporting external source
3. compression that preserves source citations and provenance chains alongside synthesized output
4. abstain / unknown behavior when evidence is insufficient
5. external source grounding discipline - explicitly identify and track which external source (file, API, database, document) supports each claim
6. explicit provenance chains - maintain traceable mappings from output claims back to specific input evidence locations
7. multi-source reconciliation - handle conflicting or partial evidence across multiple external sources with explicit conflict resolution

Avoid:
1. unsupported synthesis
2. hallucinated joins across sources
3. excessive workflow scaffolding that obscures evidence use
4. treating staged data processing as retrieval-synthesis when the task does not require external source provenance tracking

Good fit when:
- information search
- handbook / database grounded QA
- report or answer generation from external sources
- tasks requiring multi-source evidence reconciliation with explicit provenance tracking

Bad fit when:
- simulator/control tasks
- code patch workflows
- staged multi-step data processing pipelines without explicit external source grounding requirements
- tasks where the primary challenge is workflow orchestration rather than evidence provenance discipline

Primary failure modes to guard against:
- boundary ambiguity with analytic-pipeline on tasks that process data but don't require external source provenance tracking
- schema assignment to pipeline-pattern tasks that lack load-bearing evidence grounding requirements

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
Candidate id: retrieval-heavy-synthesis::round1::differentiating
Candidate mode: differentiating
Pair reason: assigned_support;competitor_check
Next pair plan mode: full_matrix
Use this as a candidate schema rerun, not as an accepted final schema.
