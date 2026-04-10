[Common wrapper]
You are revising a Task skill, not directly solving the task.
Use the provided Meta schema as class-level guidance.
Your goal is to improve the Task skill for this task while preserving useful existing structure.

[Meta schema block]
Category: orchestration-delegation
Semantic intent: Coordinate ordered external actions or substeps where sequence and dependency management matter.
Emphasize:
- constraint extraction before action
- ordering across dependent steps / systems
- state handoff between stages or tools
- fail-safe finalization and side-effect awareness
Avoid:
- eager direct completion without dependency checks
- reviewer-only prompts that lack execution choreography
- over-abstract synthesis that ignores operational order
Expected good fit:
- scheduling / delegation workflows
- multi-system action coordination
- tasks where one substep creates constraints for the next
Expected bad fit:
- static artifact-only tasks
- deep scientific analysis pipelines
Hypothesized primary failure modes:
- unavailable in prompt-bank-v0.1; use task-local evidence instead
Meta schema seed guidance:
You are revising a skill for an orchestration/delegation task.
Optimize the skill as a coordination protocol, not just as a content-generation prompt.

Prioritize:
1. extracting constraints before taking actions,
2. preserving correct action order across dependent systems or stages,
3. making state handoffs explicit,
4. preventing side effects from happening before prerequisites are checked.

If the task is failing, first strengthen dependency ordering and handoff logic before adding more general reasoning guidance.

[Task context block]
Task name: latex-formula-extraction
Task summary: You are helping to extract all latex formulas in its own line from a research paper. The paper is (`latex_paper.pdf`).
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
- current skill count: 2

[Current Task skill block]
Current Task skill:
## marker
---
name: marker
description: Convert PDF documents to Markdown using marker_single. Use when Claude needs to extract text content from PDFs while preserving LaTeX formulas, equations, and document structure. Ideal for academic papers and technical documents containing mathematical notation.
---

# Marker PDF-to-Markdown Converter

Convert PDFs to Markdown while preserving LaTeX formulas and document structure. Uses the `marker_single` CLI from the marker-pdf package.

## Dependencies
- `marker_single` on PATH (`pip install marker-pdf` if missing)
- Python 3.10+ (available in the task image)

## Quick Start

```python
from scripts.marker_to_markdown import pdf_to_markdown

markdown_text = pdf_to_markdown("paper.pdf")
print(markdown_text)
```

## Python API

- `pdf_to_markdown(pdf_path, *, timeout=600, cleanup=True) -> str`
  - Runs `marker_single --output_format markdown --disable_image_extraction`
  - `cleanup=True`: use a temp directory and delete after reading the Markdown
  - `cleanup=False`: keep outputs in `<pdf_stem>_marker/` next to the PDF
  - Exceptions: `FileNotFoundError` if the PDF is missing, `RuntimeError` for marker failures, `TimeoutError` if it exceeds the timeout
- Tips: bump `timeout` for large PDFs; set `cleanup=False` to inspect intermediate files

## Command-Line Usage

```bash
# Basic conversion (prints markdown to stdout)
python scripts/marker_to_markdown.py paper.pdf

# Keep temporary files
python scripts/marker_to_markdown.py paper.pdf --keep-temp

# Custom timeout
python scripts/marker_to_markdown.py paper.pdf --timeout 600
```

## Output Locations
- `cleanup=True`: outputs stored in a temporary directory and removed automatically
- `cleanup=False`: outputs saved to `<pdf_stem>_marker/`; markdown lives at `<pdf_stem>_marker/<pdf_stem>/<pdf_stem>.md` when present (otherwise the first `.md` file is used)

## Troubleshooting
- `marker_single` not found: install `marker-pdf` or ensure the CLI is on PATH
- No Markdown output: re-run with `--keep-temp`/`cleanup=False` and check `stdout`/`stderr` saved in the output folder

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
No Skills: `0`
With Skills: `0`
Delta: `0`
Failure summary: extract display formulas into exact markdown/latex lines with a light syntax-fix review pass
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
