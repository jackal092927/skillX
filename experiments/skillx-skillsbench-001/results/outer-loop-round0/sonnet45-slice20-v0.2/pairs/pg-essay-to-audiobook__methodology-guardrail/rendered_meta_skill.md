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
Task name: pg-essay-to-audiobook
Task summary: Can you help me find some essays from paul graham's website, and turn them into an audio book using TTS? The essays i want to listened are:
Task constraints:
- seed schema prior: orchestration-delegation
- verifier mode: deterministic-output-contract
- workflow topology: staged-multi-step
- tool surface regime: tool-heavy-script-optional
- primary pattern: pipeline
- annotation confidence: high
- secondary patterns: tool-wrapper, reviewer
Task output requirements:
- verifier note: deterministic-output-contract
- current skill count: 4

[Current Task skill block]
Current Task skill:
## audiobook
---
name: audiobook
description: "Create audiobooks from web content or text files. Handles content fetching, text processing, and TTS conversion with automatic fallback between ElevenLabs, OpenAI TTS, and gTTS."
---

# Audiobook Creation Guide

Create audiobooks from web articles, essays, or text files. This skill covers the full pipeline: content fetching, text processing, and audio generation.

## Quick Start

```python
import os

# 1. Check which TTS API is available
def get_tts_provider():
    if os.environ.get("ELEVENLABS_API_KEY"):
        return "elevenlabs"
    elif os.environ.get("OPENAI_API_KEY"):
        return "openai"
    else:
        return "gtts"  # Free, no API key needed

provider = get_tts_provider()
print(f"Using TTS provider: {provider}")
```

## Step 1: Fetching Web Content

### IMPORTANT: Verify fetched content is complete

WebFetch and similar tools may return summaries instead of full text. Always verify:

```python
import subprocess

def fetch_article_content(url):
    """Fetch article content using curl for reliability."""
    # Use curl to get raw HTML - more reliable than web fetch tools
    result = subprocess.run(
        ["curl", "-s", url],
        capture_output=True,
        text=True
    )
    html = result.stdout

    # Strip HTML tags (basic approach)
    import re
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    return text
```

### Content verification checklist

Before converting to audio, verify:
- [ ] Text length is reasonable for the source (articles typically 1,000-10,000+ words)
- [ ] Content includes actual article text, not just navigation/headers
- [ ] No "summary" or "key points" headers that indicate truncation

```python
def verify_content(text, expected_min_chars=1000):
    """Basic verification that content is complete."""
    if len(text) < expected_min_chars:
        print(f"WARNING: Content may be truncated ({len(text)} chars)")
        return False
    if "summary" in text.lower()[:500] or "key points" in text.lower()[:500]:
        print("WARNING: Content appears to be a summary, not full text")
        return False
    return True
```

## Step 2: Text Processing

### Clean and prepare text for TTS

```python
import re

def clean_text_for_tts(text):
    """Clean text for better TTS output."""
    # Remove URLs
    text = re.sub(r'http[s]?://\S+', '', text)

    # Remove footnote markers like [1], [2]
    text = re.sub(r'\[\d+\]', '', text)

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove special characters that confuse TTS
    text = re.sub(r'[^\w\s.,!?;:\'"()-]', '', text)

    return text.strip()

def chunk_text(text, max_chars=4000):
    """Split text into chunks at sentence boundaries."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_chars:
            current_chunk += sentence + " "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + " "

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks
```

## Step 3: TTS Conversion with Fallback

### Automatic provider selection

```python
import os
import subprocess

def create_audiobook(text, output_path):
    """Convert text to audiobook with automatic TTS provider selection."""

    # Check available providers
    has_elevenlabs = bool(os.environ.get("ELEVENLABS_API_KEY"))
    has_openai = bool(os.environ.get("OPENAI_API_KEY"))

    if has_elevenlabs:
        print("Using ElevenLabs TTS (highest quality)")
        return create_with_elevenlabs(text, output_path)
    elif has_openai:
        print("Using OpenAI TTS (high quality)")
        return create_with_openai(text, output_path)
    else:
        print("Using gTTS (free, no API key required)")
        return create_with_gtts(text, output_path)
```

### ElevenLabs implementation

```python
import requests

def create_with_elevenlabs(text, output_path):
    """Generate audiobook using ElevenLabs API."""
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel - calm female voice

    chunks = chunk_text(text, max_chars=4500)
    audio_files = []

    for i, chunk in enumerate(chunks):
        chunk_file = f"/tmp/chunk_{i:03d}.mp3"

        response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={
                "xi-api-key": api_key,
                "Content-Type": "application/json"
            },
            json={
                "text": chunk,
                "model_id": "eleven_turbo_v2_5",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
            }
        )

        if response.status_code == 200:
            with open(chunk_file, "wb") as f:
                f.write(response.content)
            audio_files.append(chunk_file)
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return False

    return concatenate_audio(audio_files, output_path)
```

### OpenAI TTS implementation

```python
def create_with_openai(text, output_path):
    """Generate audiobook using OpenAI TTS API."""
    api_key = os.environ.get("OPENAI_API_KEY")

    chunks = chunk_text(text, max_chars=4000)
    audio_files = []

    for i, chunk in enumerate(chunks):
        chunk_file = f"/tmp/chunk_{i:03d}.mp3"

        response = requests.post(
            "https://api.openai.com/v1/audio/speech",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "tts-1",
                "input": chunk,
                "voice": "onyx",  # Deep male voice, good for essays
                "response_format": "mp3"
            }
        )

        if response.status_code == 200:
            with open(chunk_file, "wb") as f:
                f.write(response.content)
            audio_files.append(chunk_file)
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return False

    return concatenate_audio(audio_files, output_path)
```

### gTTS implementation (free fallback)

```python
def create_with_gtts(text, output_path):
    """Generate audiobook using gTTS (free, no API key)."""
    from gtts import gTTS
    from pydub import AudioSegment

    chunks = chunk_text(text, max_chars=4500)
    audio_files = []

    for i, chunk in enumerate(chunks):
        chunk_file = f"/tmp/chunk_{i:03d}.mp3"

        tts = gTTS(text=chunk, lang='en', slow=False)
        tts.save(chunk_file)
        audio_files.append(chunk_file)

    return concatenate_audio(audio_files, output_path)
```

### Audio concatenation

```python
def concatenate_audio(audio_files, output_path):
    """Concatenate multiple audio files using ffmpeg."""
    if not audio_files:
        return False

    # Create file list for ffmpeg
    list_file = "/tmp/audio_list.txt"
    with open(list_file, "w") as f:
        for audio_file in audio_files:
            f.write(f"file '{audio_file}'\n")

    # Concatenate with ffmpeg
    result = subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", list_file, "-c", "copy", output_path
    ], capture_output=True)

    # Cleanup temp files
    import os
    for f in audio_files:
        os.unlink(f)
    os.unlink(list_file)

    return result.returncode == 0
```

## Complete Example

```python
#!/usr/bin/env python3
"""Create audiobook from web articles."""

import os
import re
import subprocess
import requests

# ... include all helper functions above ...

def main():
    # Fetch articles
    urls = [
        "https://example.com/article1",
        "https://example.com/article2"
    ]

    all_text = ""
    for url in urls:
        print(f"Fetching: {url}")
        text = fetch_article_content(url)

        if not verify_content(text):
            print(f"WARNING: Content from {url} may be incomplete")

        all_text += f"\n\n{text}"

    # Clean and convert
    clean_text = clean_text_for_tts(all_text)
    print(f"Total text: {len(clean_text)} characters")

    # Create audiobook
    success = create_audiobook(clean_text, "/root/audiobook.mp3")

    if success:
        print("Audiobook created successfully!")
    else:
        print("Failed to create audiobook")

if __name__ == "__main__":
    main()
```

## TTS Provider Comparison

| Provider | Quality | Cost | API Key Required | Best For |
|----------|---------|------|------------------|----------|
| ElevenLabs | Excellent | Paid | Yes | Professional audiobooks |
| OpenAI TTS | Very Good | Paid | Yes | General purpose |
| gTTS | Good | Free | No | Testing, budget projects |

## Troubleshooting

### "Content appears to be a summary"
- Use `curl` directly instead of web fetch tools
- Verify the URL is correct and accessible
- Check if the site requires JavaScript rendering

### "API key not found"
- Check environment variables: `echo $OPENAI_API_KEY`
- Ensure keys are exported in the shell
- Fall back to gTTS if no paid API keys available

### "Audio chunks don't sound continuous"
- Ensure chunking happens at sentence boundaries
- Consider adding small pauses between sections
- Use consistent voice settings across all chunks

## elevenlabs-tts
---
name: elevenlabs-tts
description: "ElevenLabs Text-to-Speech API for high-quality speech synthesis."
---

# ElevenLabs Text-to-Speech

Generate high-quality speech audio from text using the ElevenLabs API.

## Authentication

The API key is available as environment variable:
```bash
ELEVENLABS_API_KEY
```

Include in request header:
```
xi-api-key: $ELEVENLABS_API_KEY
```

## API Endpoints

### Text-to-Speech
```
POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}
```

**Request Body:**
```json
{
  "text": "Your text here",
  "model_id": "eleven_turbo_v2_5",
  "voice_settings": {
    "stability": 0.5,
    "similarity_boost": 0.5
  }
}
```

**Response:** Audio bytes (mp3 format by default)

## Popular Voice IDs

- `21m00Tcm4TlvDq8ikWAM` - Rachel (female, calm)
- `EXAVITQu4vr4xnSDxMaL` - Bella (female, soft)
- `ErXwobaYiN019PkySvjV` - Antoni (male, warm)
- `TxGEqnHWrfWFTfGW9XjX` - Josh (male, deep)

## Python Example

```python
import os
import requests

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel

def text_to_speech(text, output_path):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "text": text,
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        return True
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return False
```

## Handling Long Text

ElevenLabs has a ~5000 character limit per request. For long documents:

1. Split text into chunks at sentence boundaries
2. Generate audio for each chunk
3. Concatenate using ffmpeg or pydub:

```bash
# Create file list
echo "file 'chunk1.mp3'" > files.txt
echo "file 'chunk2.mp3'" >> files.txt

# Concatenate
ffmpeg -f concat -safe 0 -i files.txt -c copy output.mp3
```

## Best Practices

- Split at sentence boundaries to avoid cutting words
- Check rate limits (varies by subscription tier)
- Cache generated audio to avoid redundant API calls

## gtts
---
name: gtts
description: "Google Text-to-Speech (gTTS) for converting text to audio. Use when creating audiobooks, podcasts, or speech synthesis from text. Handles long text by chunking at sentence boundaries and concatenating audio segments with pydub."
---

# Google Text-to-Speech (gTTS)

gTTS is a Python library that converts text to speech using Google's Text-to-Speech API. It's free to use and doesn't require an API key.

## Installation

```bash
pip install gtts pydub
```

pydub is useful for manipulating and concatenating audio files.

## Basic Usage

```python
from gtts import gTTS

# Create speech
tts = gTTS(text="Hello, world!", lang='en')

# Save to file
tts.save("output.mp3")
```

## Language Options

```python
# US English (default)
tts = gTTS(text="Hello", lang='en')

# British English
tts = gTTS(text="Hello", lang='en', tld='co.uk')

# Slow speech
tts = gTTS(text="Hello", lang='en', slow=True)
```

## Python Example for Long Text

```python
from gtts import gTTS
from pydub import AudioSegment
import tempfile
import os
import re

def chunk_text(text, max_chars=4500):
    """Split text into chunks at sentence boundaries."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_chars:
            current_chunk += sentence + " "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + " "

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def text_to_audiobook(text, output_path):
    """Convert long text to a single audio file."""
    chunks = chunk_text(text)
    audio_segments = []

    for i, chunk in enumerate(chunks):
        # Create temp file for this chunk
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
            tmp_path = tmp.name

        # Generate speech
        tts = gTTS(text=chunk, lang='en', slow=False)
        tts.save(tmp_path)

        # Load and append
        segment = AudioSegment.from_mp3(tmp_path)
        audio_segments.append(segment)

        # Cleanup
        os.unlink(tmp_path)

    # Concatenate all segments
    combined = audio_segments[0]
    for segment in audio_segments[1:]:
        combined += segment

    # Export
    combined.export(output_path, format="mp3")
```

## Handling Large Documents

gTTS has a character limit per request (~5000 chars). For long documents:

1. Split text into chunks at sentence boundaries
2. Generate audio for each chunk using gTTS
3. Use pydub to concatenate the chunks

## Alternative: Using ffmpeg for Concatenation

If you prefer ffmpeg over pydub:

```bash
# Create file list
echo "file 'chunk1.mp3'" > files.txt
echo "file 'chunk2.mp3'" >> files.txt

# Concatenate
ffmpeg -f concat -safe 0 -i files.txt -c copy output.mp3
```

## Best Practices

- Split at sentence boundaries to avoid cutting words mid-sentence
- Use `slow=False` for natural speech speed
- Handle network errors gracefully (gTTS requires internet)
- Consider adding brief pauses between chapters/sections

## Limitations

- Requires internet connection (uses Google's servers)
- Voice quality is good but not as natural as paid services
- Limited voice customization options
- May have rate limits for very heavy usage

## openai-tts
---
name: openai-tts
description: "OpenAI Text-to-Speech API for high-quality speech synthesis. Use for generating natural-sounding audio from text with customizable voices and tones."
---

# OpenAI Text-to-Speech

Generate high-quality spoken audio from text using OpenAI's TTS API.

## Authentication

The API key is available as environment variable:
```bash
OPENAI_API_KEY
```

## Models

- `gpt-4o-mini-tts` - Newest, most reliable. Supports tone/style instructions.
- `tts-1` - Lower latency, lower quality
- `tts-1-hd` - Higher quality, higher latency

## Voice Options

Built-in voices (English optimized):
- `alloy`, `ash`, `ballad`, `coral`, `echo`, `fable`
- `nova`, `onyx`, `sage`, `shimmer`, `verse`
- `marin`, `cedar` - **Recommended for best quality**

Note: `tts-1` and `tts-1-hd` only support: alloy, ash, coral, echo, fable, onyx, nova, sage, shimmer.

## Python Example

```python
from pathlib import Path
from openai import OpenAI

client = OpenAI()  # Uses OPENAI_API_KEY env var

# Basic usage
with client.audio.speech.with_streaming_response.create(
    model="gpt-4o-mini-tts",
    voice="coral",
    input="Hello, world!",
) as response:
    response.stream_to_file("output.mp3")

# With tone instructions (gpt-4o-mini-tts only)
with client.audio.speech.with_streaming_response.create(
    model="gpt-4o-mini-tts",
    voice="coral",
    input="Today is a wonderful day!",
    instructions="Speak in a cheerful and positive tone.",
) as response:
    response.stream_to_file("output.mp3")
```

## Handling Long Text

For long documents, split into chunks and concatenate:

```python
from openai import OpenAI
from pydub import AudioSegment
import tempfile
import re
import os

client = OpenAI()

def chunk_text(text, max_chars=4000):
    """Split text into chunks at sentence boundaries."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_chars:
            current_chunk += sentence + " "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + " "

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def text_to_audiobook(text, output_path):
    """Convert long text to audio file."""
    chunks = chunk_text(text)
    audio_segments = []

    for chunk in chunks:
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
            tmp_path = tmp.name

        with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="coral",
            input=chunk,
        ) as response:
            response.stream_to_file(tmp_path)

        segment = AudioSegment.from_mp3(tmp_path)
        audio_segments.append(segment)
        os.unlink(tmp_path)

    # Concatenate all segments
    combined = audio_segments[0]
    for segment in audio_segments[1:]:
        combined += segment

    combined.export(output_path, format="mp3")
```

## Output Formats

- `mp3` - Default, general use
- `opus` - Low latency streaming
- `aac` - Digital compression (YouTube, iOS)
- `flac` - Lossless compression
- `wav` - Uncompressed, low latency
- `pcm` - Raw samples (24kHz, 16-bit)

```python
with client.audio.speech.with_streaming_response.create(
    model="gpt-4o-mini-tts",
    voice="coral",
    input="Hello!",
    response_format="wav",  # Specify format
) as response:
    response.stream_to_file("output.wav")
```

## Best Practices

- Use `marin` or `cedar` voices for best quality
- Split text at sentence boundaries for long content
- Use `wav` or `pcm` for lowest latency
- Add `instructions` parameter to control tone/style (gpt-4o-mini-tts only)

[Evidence block]
No Skills: `0`
With Skills: `0`
Delta: `0`
Failure summary: instruction is a clean two-system workflow: retrieve specified Paul Graham essays online and turn them into one audiobook via remote or local TTS
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
