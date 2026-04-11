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
Task name: multilingual-video-dubbing
Task summary: Give you a video with source audio /root/input.mp4, the precise time window where the speech must occur /root/segments.srt. The transcript for the original speaker /root/source_text.srt. The target language /root/target_language.txt. and the reference script /root/reference_target_text.srt. Help me to do the multilingual dubbing. We want:
Task constraints:
- seed schema prior: analytic-pipeline
- verifier mode: deterministic-artifact-plus-stage-check
- workflow topology: staged-multi-step
- tool surface regime: tool-heavy-script-recommended
- primary pattern: pipeline
- annotation confidence: high
- secondary patterns: tool-wrapper, reviewer
Task output requirements:
- verifier note: deterministic-artifact-plus-stage-check
- current skill count: 6

[Current Task skill block]
Current Task skill:
## ffmpeg-audio-processing
---
name: FFmpeg Audio Processing
description: Extract, normalize, mix, and process audio tracks - audio manipulation and analysis
---

# FFmpeg Audio Processing Skill

Extract, normalize, mix, and process audio tracks from video files.

## When to Use

- Extract audio from video
- Normalize audio levels
- Mix multiple audio tracks
- Convert audio formats
- Extract specific channels
- Adjust audio volume

## Extract Audio

```bash
# Extract as MP3
ffmpeg -i video.mp4 -vn -acodec libmp3lame -q:a 2 audio.mp3

# Extract as AAC (copy, no re-encode)
ffmpeg -i video.mp4 -vn -c:a copy audio.aac

# Extract as WAV (uncompressed)
ffmpeg -i video.mp4 -vn -acodec pcm_s16le audio.wav

# Extract specific audio stream
ffmpeg -i video.mp4 -map 0:a:1 -c:a copy audio2.aac
```

## Normalize Audio

```bash
# Normalize loudness (ITU-R BS.1770-4)
ffmpeg -i input.mp4 -af "loudnorm=I=-23:TP=-1.5:LRA=11" output.mp4

# Simple normalization
ffmpeg -i input.mp4 -af "volume=2.0" output.mp4

# Peak normalization
ffmpeg -i input.mp4 -af "volumedetect" -f null -
# Then use the detected peak to normalize
ffmpeg -i input.mp4 -af "volume=0.5" output.mp4
```

## Volume Adjustment

```bash
# Increase volume by 6dB
ffmpeg -i input.mp4 -af "volume=6dB" output.mp4

# Decrease volume by 3dB
ffmpeg -i input.mp4 -af "volume=-3dB" output.mp4

# Set absolute volume
ffmpeg -i input.mp4 -af "volume=0.5" output.mp4
```

## Channel Operations

```bash
# Extract left channel
ffmpeg -i stereo.mp3 -map_channel 0.0.0 left.mp3

# Extract right channel
ffmpeg -i stereo.mp3 -map_channel 0.0.1 right.mp3

# Convert stereo to mono
ffmpeg -i stereo.mp3 -ac 1 mono.mp3

# Convert mono to stereo
ffmpeg -i mono.mp3 -ac 2 stereo.mp3
```

## Mix Audio Tracks

```bash
# Replace audio track
ffmpeg -i video.mp4 -i audio.mp3 -c:v copy -map 0:v:0 -map 1:a:0 output.mp4

# Mix two audio tracks
ffmpeg -i video.mp4 -i audio2.mp3 \
  -filter_complex "[0:a][1:a]amix=inputs=2:duration=first" \
  -c:v copy output.mp4

# Mix with volume control
ffmpeg -i video.mp4 -i bgm.mp3 \
  -filter_complex "[0:a]volume=1.0[voice];[1:a]volume=0.3[music];[voice][music]amix=inputs=2:duration=first" \
  -c:v copy output.mp4
```

## Audio Delay

```bash
# Delay audio by 0.5 seconds
ffmpeg -i video.mp4 -itsoffset 0.5 -i video.mp4 \
  -map 0:v -map 1:a -c copy output.mp4

# Using adelay filter (milliseconds)
ffmpeg -i input.mp4 -af "adelay=500|500" output.mp4
```

## Sample Rate Conversion

```bash
# Resample to 48kHz
ffmpeg -i input.mp4 -af "aresample=48000" output.mp4

# Resample audio only
ffmpeg -i input.mp4 -vn -af "aresample=48000" -ar 48000 audio.wav
```

## Audio Filters

```bash
# High-pass filter (remove low frequencies)
ffmpeg -i input.mp4 -af "highpass=f=200" output.mp4

# Low-pass filter (remove high frequencies)
ffmpeg -i input.mp4 -af "lowpass=f=3000" output.mp4

# Band-pass filter
ffmpeg -i input.mp4 -af "bandpass=f=1000:width_type=h:w=500" output.mp4

# Fade in/out
ffmpeg -i input.mp4 -af "afade=t=in:st=0:d=2,afade=t=out:st=8:d=2" output.mp4
```

## Audio Analysis

```bash
# Detect volume levels
ffmpeg -i input.mp4 -af "volumedetect" -f null -

# Measure loudness (LUFS)
ffmpeg -i input.mp4 -af "ebur128=peak=true" -f null -

# Get audio statistics
ffprobe -v error -select_streams a:0 \
  -show_entries stream=sample_rate,channels,bit_rate \
  -of json input.mp4
```

## Combine Multiple Audio Files

```bash
# Concatenate audio files
ffmpeg -i "concat:audio1.mp3|audio2.mp3|audio3.mp3" -c copy output.mp3

# Using file list
# file 'audio1.mp3'
# file 'audio2.mp3'
ffmpeg -f concat -safe 0 -i list.txt -c copy output.mp3
```

## Notes

- Use `-vn` to disable video when extracting audio
- `-map` to select specific streams
- `-af` for audio filters
- `-ac` for channel count
- `-ar` for sample rate
- Normalization may require two passes for accurate results

## ffmpeg-format-conversion
---
name: FFmpeg Format Conversion
description: Convert media files between formats - video containers, audio formats, and codec transcoding
---

# FFmpeg Format Conversion Skill

Convert media files between different formats and containers.

## When to Use

- Convert video containers (MP4, MKV, AVI, etc.)
- Convert audio formats (MP3, AAC, WAV, etc.)
- Transcode to different codecs
- Copy streams without re-encoding (fast)

## Basic Conversion

```bash
# Convert container format (re-encode)
ffmpeg -i input.avi output.mp4

# Copy streams without re-encoding (fast, no quality loss)
ffmpeg -i input.mp4 -c copy output.mkv

# Convert with specific codec
ffmpeg -i input.mp4 -c:v libx264 -c:a aac output.mp4
```

## Video Codec Conversion

```bash
# H.264
ffmpeg -i input.mp4 -c:v libx264 output.mp4

# H.265 (better compression)
ffmpeg -i input.mp4 -c:v libx265 output.mp4

# VP9 (web optimized)
ffmpeg -i input.mp4 -c:v libvpx-vp9 output.webm

# AV1 (modern codec)
ffmpeg -i input.mp4 -c:v libaom-av1 output.mp4
```

## Audio Format Conversion

```bash
# MP3
ffmpeg -i input.wav -acodec libmp3lame -q:a 2 output.mp3

# AAC
ffmpeg -i input.wav -c:a aac -b:a 192k output.m4a

# Opus (best quality/bitrate)
ffmpeg -i input.wav -c:a libopus -b:a 128k output.opus

# FLAC (lossless)
ffmpeg -i input.wav -c:a flac output.flac
```

## Quality Settings

```bash
# CRF (Constant Rate Factor) - lower is better quality
ffmpeg -i input.mp4 -c:v libx264 -crf 23 output.mp4

# Bitrate
ffmpeg -i input.mp4 -b:v 2M -b:a 192k output.mp4

# Two-pass encoding (best quality)
ffmpeg -i input.mp4 -c:v libx264 -b:v 2M -pass 1 -f null /dev/null
ffmpeg -i input.mp4 -c:v libx264 -b:v 2M -pass 2 output.mp4
```

## Presets

```bash
# Encoding speed presets (faster = larger file)
ffmpeg -i input.mp4 -c:v libx264 -preset fast output.mp4
# Options: ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow

# Quality presets
ffmpeg -i input.mp4 -c:v libx264 -preset slow -crf 18 output.mp4
```

## Batch Conversion

```bash
# Convert all MKV to MP4
for f in *.mkv; do
  ffmpeg -i "$f" -c copy "${f%.mkv}.mp4"
done

# Convert with re-encoding
for f in *.avi; do
  ffmpeg -i "$f" -c:v libx264 -c:a aac "${f%.avi}.mp4"
done
```

## Common Codecs

### Video
- **H.264** (libx264) - Universal compatibility
- **H.265** (libx265) - Better compression
- **VP9** (libvpx-vp9) - Open standard
- **AV1** (libaom-av1) - Modern codec

### Audio
- **AAC** (aac) - Universal
- **MP3** (libmp3lame) - Legacy
- **Opus** (libopus) - Best quality/bitrate
- **FLAC** (flac) - Lossless

## Notes

- Use `-c copy` when possible for speed (no re-encoding)
- Re-encoding is slower but allows codec/quality changes
- CRF 18-23 is good quality range for H.264
- Preset affects encoding speed vs file size tradeoff

## ffmpeg-media-info
---
name: FFmpeg Media Info
description: Analyze media file properties - duration, resolution, bitrate, codecs, and stream information
---

# FFmpeg Media Info Skill

Extract and analyze media file metadata using ffprobe and ffmpeg.

## When to Use

- Get video/audio file properties
- Check codec information
- Verify resolution and bitrate
- Analyze stream details
- Debug media file issues

## Basic Info Commands

```bash
# Show all file info
ffmpeg -i input.mp4

# JSON format (detailed)
ffprobe -v quiet -print_format json -show_format -show_streams input.mp4

# Simple format
ffprobe -v quiet -print_format json -show_format input.mp4
```

## Duration

```bash
# Get duration in seconds
ffprobe -v error -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 input.mp4

# Duration with timestamp format
ffprobe -v error -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 -sexagesimal input.mp4
```

## Resolution

```bash
# Get video resolution
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height \
  -of csv=s=x:p=0 input.mp4

# Get resolution as JSON
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height \
  -of json input.mp4
```

## Bitrate

```bash
# Get overall bitrate
ffprobe -v error -show_entries format=bit_rate \
  -of default=noprint_wrappers=1:nokey=1 input.mp4

# Get video bitrate
ffprobe -v error -select_streams v:0 \
  -show_entries stream=bit_rate \
  -of default=noprint_wrappers=1:nokey=1 input.mp4
```

## Codec Information

```bash
# Video codec
ffprobe -v error -select_streams v:0 \
  -show_entries stream=codec_name,codec_long_name \
  -of default=noprint_wrappers=1 input.mp4

# Audio codec
ffprobe -v error -select_streams a:0 \
  -show_entries stream=codec_name,codec_long_name \
  -of default=noprint_wrappers=1 input.mp4
```

## Sample Rate and Channels

```bash
# Audio sample rate
ffprobe -v error -select_streams a:0 \
  -show_entries stream=sample_rate \
  -of default=noprint_wrappers=1:nokey=1 input.mp4

# Audio channels
ffprobe -v error -select_streams a:0 \
  -show_entries stream=channels \
  -of default=noprint_wrappers=1:nokey=1 input.mp4
```

## Stream Count

```bash
# Count video streams
ffprobe -v error -select_streams v -show_entries stream=index \
  -of csv=p=0 input.mp4 | wc -l

# Count audio streams
ffprobe -v error -select_streams a -show_entries stream=index \
  -of csv=p=0 input.mp4 | wc -l
```

## Frame Rate

```bash
# Get frame rate
ffprobe -v error -select_streams v:0 \
  -show_entries stream=r_frame_rate \
  -of default=noprint_wrappers=1:nokey=1 input.mp4
```

## Notes

- Use `-v error` to suppress warnings
- `-of json` for structured output
- `-select_streams` to target specific streams (v:0 for first video, a:0 for first audio)

## ffmpeg-video-editing
---
name: FFmpeg Video Editing
description: Cut, trim, concatenate, and split video files - basic video editing operations
---

# FFmpeg Video Editing Skill

Basic video editing operations: cutting, trimming, concatenating, and splitting videos.

## When to Use

- Cut segments from video
- Trim video length
- Concatenate multiple videos
- Split video into parts
- Extract specific time ranges

## Cutting and Trimming

```bash
# Cut from 10s to 30s (using -ss and -to)
ffmpeg -ss 00:00:10 -to 00:00:30 -i input.mp4 -c copy output.mp4

# Cut from 10s for 20 seconds duration
ffmpeg -ss 00:00:10 -t 20 -i input.mp4 -c copy output.mp4

# First 60 seconds
ffmpeg -t 60 -i input.mp4 -c copy output.mp4

# Last 30 seconds (need duration first)
ffmpeg -sseof -30 -i input.mp4 -c copy output.mp4
```

## Precise Cutting

```bash
# With re-encoding (more precise)
ffmpeg -ss 00:00:10 -i input.mp4 -t 20 -c:v libx264 -c:a aac output.mp4

# Keyframe-accurate (faster, may be less precise)
ffmpeg -ss 00:00:10 -i input.mp4 -t 20 -c copy output.mp4
```

## Concatenation

### Method 1: File List (Recommended)

```bash
# Create list.txt file:
# file 'video1.mp4'
# file 'video2.mp4'
# file 'video3.mp4'

ffmpeg -f concat -safe 0 -i list.txt -c copy output.mp4
```

### Method 2: Same Codec Files

```bash
# If all videos have same codec/format
ffmpeg -i "concat:video1.mp4|video2.mp4|video3.mp4" -c copy output.mp4
```

### Method 3: Re-encode (Different Codecs)

```bash
# Re-encode for compatibility
ffmpeg -f concat -safe 0 -i list.txt -c:v libx264 -c:a aac output.mp4
```

## Splitting Video

```bash
# Split into 60-second segments
ffmpeg -i input.mp4 -c copy -f segment -segment_time 60 \
  -reset_timestamps 1 output_%03d.mp4

# Split at specific timestamps
ffmpeg -i input.mp4 -ss 00:00:00 -t 00:01:00 -c copy part1.mp4
ffmpeg -i input.mp4 -ss 00:01:00 -t 00:01:00 -c copy part2.mp4
```

## Extract Segment with Re-encoding

```bash
# When you need to change quality/codec
ffmpeg -ss 00:00:10 -i input.mp4 -t 20 \
  -c:v libx264 -crf 23 -c:a aac -b:a 192k output.mp4
```

## Multiple Segments

```bash
# Extract multiple segments
ffmpeg -i input.mp4 \
  -ss 00:00:10 -t 00:00:05 -c copy segment1.mp4 \
  -ss 00:01:00 -t 00:00:10 -c copy segment2.mp4
```

## Notes

- Use `-c copy` for speed (no re-encoding)
- `-ss` before `-i` is faster but less precise
- `-ss` after `-i` is more precise but slower
- Concatenation requires same codec/format for `-c copy`
- Use file list method for best concatenation results

## ffmpeg-video-filters
---
name: FFmpeg Video Filters
description: Apply video filters - scale, crop, watermark, speed, blur, and visual effects
---

# FFmpeg Video Filters Skill

Apply video filters for scaling, cropping, watermarks, speed changes, and visual effects.

## When to Use

- Resize videos
- Crop video frames
- Add watermarks or overlays
- Change playback speed
- Apply blur or other effects
- Adjust brightness/contrast

## Scaling

```bash
# Scale to 720p (maintain aspect ratio)
ffmpeg -i input.mp4 -vf scale=-2:720 output.mp4

# Scale to specific width (maintain aspect ratio)
ffmpeg -i input.mp4 -vf scale=1280:-2 output.mp4

# Scale to exact dimensions (may distort)
ffmpeg -i input.mp4 -vf scale=1920:1080 output.mp4

# Scale with algorithm
ffmpeg -i input.mp4 -vf scale=1280:720:flags=lanczos output.mp4
```

## Cropping

```bash
# Crop to 16:9 from center
ffmpeg -i input.mp4 -vf "crop=1920:1080" output.mp4

# Crop with offset (x:y:width:height)
ffmpeg -i input.mp4 -vf "crop=1920:1080:0:0" output.mp4

# Crop from specific position
ffmpeg -i input.mp4 -vf "crop=800:600:100:50" output.mp4
```

## Watermarks and Overlays

```bash
# Add image watermark (top-left)
ffmpeg -i input.mp4 -i logo.png \
  -filter_complex "overlay=10:10" output.mp4

# Bottom-right watermark
ffmpeg -i input.mp4 -i logo.png \
  -filter_complex "overlay=W-w-10:H-h-10" output.mp4

# Center watermark
ffmpeg -i input.mp4 -i logo.png \
  -filter_complex "overlay=(W-w)/2:(H-h)/2" output.mp4
```

## Speed Changes

```bash
# Speed up 2x
ffmpeg -i input.mp4 -vf "setpts=0.5*PTS" -af "atempo=2.0" output.mp4

# Slow down 0.5x
ffmpeg -i input.mp4 -vf "setpts=2.0*PTS" -af "atempo=0.5" output.mp4

# Speed up video only (no audio)
ffmpeg -i input.mp4 -vf "setpts=0.5*PTS" -an output.mp4
```

## Blur Effects

```bash
# Blur entire video
ffmpeg -i input.mp4 -vf "boxblur=10:5" output.mp4

# Blur specific region (coordinates x:y:w:h)
ffmpeg -i input.mp4 -vf "boxblur=10:5:x=100:y=100:w=200:h=200" output.mp4

# Gaussian blur
ffmpeg -i input.mp4 -vf "gblur=sigma=5" output.mp4
```

## Brightness and Contrast

```bash
# Adjust brightness and contrast
ffmpeg -i input.mp4 -vf "eq=brightness=0.1:contrast=1.2" output.mp4

# Increase brightness
ffmpeg -i input.mp4 -vf "eq=brightness=0.2" output.mp4

# Adjust saturation
ffmpeg -i input.mp4 -vf "eq=saturation=1.5" output.mp4
```

## Rotation

```bash
# Rotate 90 degrees clockwise
ffmpeg -i input.mp4 -vf "transpose=1" output.mp4

# Rotate 90 degrees counter-clockwise
ffmpeg -i input.mp4 -vf "transpose=2" output.mp4

# Rotate 180 degrees
ffmpeg -i input.mp4 -vf "transpose=1,transpose=1" output.mp4
```

## Multiple Filters

```bash
# Chain multiple filters
ffmpeg -i input.mp4 -vf "scale=1280:720,crop=800:600:100:50" output.mp4

# Complex filter chain
ffmpeg -i input.mp4 -i logo.png \
  -filter_complex "[0:v]scale=1280:720[scaled];[scaled][1:v]overlay=10:10" \
  output.mp4
```

## Fade Effects

```bash
# Fade in (first 2 seconds)
ffmpeg -i input.mp4 -vf "fade=t=in:st=0:d=2" output.mp4

# Fade out (last 2 seconds)
ffmpeg -i input.mp4 -vf "fade=t=out:st=10:d=2" output.mp4

# Fade in and out
ffmpeg -i input.mp4 -vf "fade=t=in:st=0:d=2,fade=t=out:st=8:d=2" output.mp4
```

## Notes

- Use `-vf` for video filters
- Multiple filters separated by commas
- Use `-filter_complex` for complex operations
- Overlay positions: W=width, H=height, w=overlay width, h=overlay height
- Speed changes require both video (setpts) and audio (atempo) filters

## text-to-speech
---

name: "TTS Audio Mastering"
description: "Practical mastering steps for TTS audio: cleanup, loudness normalization, alignment, and delivery specs."
---

# SKILL: TTS Audio Mastering

This skill focuses on producing clean, consistent, and delivery-ready TTS audio for video tasks. It covers speech cleanup, loudness normalization, segment boundaries, and export specs.

## 1. TTS Engine & Output Basics

Choose a TTS engine based on deployment constraints and quality needs:

* **Neural offline** (e.g., Kokoro): stable, high quality, no network dependency.
* **Cloud TTS** (e.g., Edge-TTS / OpenAI TTS): convenient, higher naturalness but network-dependent.
* **Formant TTS** (e.g., espeak-ng): for prototyping only; often less natural.

**Key rule:** Always confirm the **native sample rate** of the generated audio before resampling for video delivery.

---

## 2. Speech Cleanup (Per Segment)

Apply lightweight processing to avoid common artifacts:

* **Rumble/DC removal:** high-pass filter around **20 Hz**
* **Harshness control:** optional low-pass around **16 kHz** (helps remove digital fizz)
* **Click/pop prevention:** short fades at boundaries (e.g., **50 ms** fade-in and fade-out)

Recommended FFmpeg pattern (example):

* Add filters in a single chain, and keep them consistent across segments.

---

## 3. Loudness Normalization

Target loudness depends on the benchmark/task spec. A common target is ITU-R BS.1770 loudness measurement:

* **Integrated loudness:** **-23 LUFS**
* **True peak:** around **-1.5 dBTP**
* **LRA:** around **11** (optional)

Recommended workflow:

1. **Measure loudness** using FFmpeg `ebur128` (or equivalent meter).
2. **Apply normalization** (e.g., `loudnorm`) as the final step after cleanup and timing edits.
3. If you adjust tempo/duration after normalization, re-normalize again.

---

## 4. Timing & Segment Boundary Handling

When stitching segment-level TTS into a full track:

* Match each segment to its target window as closely as possible.
* If a segment is shorter than its window, pad with silence.
* If a segment is longer, use gentle duration control (small speed change) or truncate carefully.
* Always apply boundary fades after padding/trimming to avoid clicks.

**Sync guideline:** keep end-to-end drift small (e.g., **<= 0.2s**) unless the task states otherwise.

[Evidence block]
No Skills: `40`
With Skills: `100`
Delta: `60`
Failure summary: translation-aligned TTS, segment timing control, loudness constraints, and muxed dubbed-video output form a tightly staged AV pipeline
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
