---
id: whisper_pipeline
title: Whisper Processing Pipeline
---

# Whisper Processing Pipeline

The Whisper pipeline handles **speech-to-text transcription**:

1. Receive preprocessed audio.
2. Use the Whisper model to generate text.
3. Score transcription confidence.
4. Pass text to **command validator** for further processing.

This pipeline is asynchronous and supports real-time or batch processing.
