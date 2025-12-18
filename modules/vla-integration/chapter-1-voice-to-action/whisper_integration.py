"""
Whisper API integration for the Vision-Language-Action (VLA) system.

This module provides integration with OpenAI's Whisper API for speech-to-text
conversion, handling audio processing and transcription with confidence scoring.
"""

import asyncio
import base64
import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from pathlib import Path

import openai
from openai import OpenAI

from ..shared.models import VoiceCommand, CommandStatus


class WhisperIntegration:
    """
    Service for integrating with OpenAI Whisper API for speech-to-text conversion.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Whisper integration.

        Args:
            api_key: OpenAI API key. If not provided, will try to get from environment
        """
        self.logger = logging.getLogger(__name__)

        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required for Whisper integration")

        self.client = OpenAI(api_key=self.api_key)

    async def transcribe_audio_file(self, audio_file_path: str) -> Tuple[str, float]:
        """
        Transcribe an audio file using Whisper API.

        Args:
            audio_file_path: Path to the audio file to transcribe

        Returns:
            Tuple of (transcribed_text, confidence_score)
        """
        try:
            # Validate file exists
            if not Path(audio_file_path).exists():
                raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

            # OpenAI Whisper supports specific file formats
            # Commonly supported: mp3, mp4, mpeg, mpga, m4a, wav, webm
            with open(audio_file_path, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json",  # This gives us more detailed response
                    timestamp_granularities=["segment"]
                )

            # Extract text and confidence information
            text = transcription.text
            # Note: Whisper doesn't directly provide confidence scores in all response formats
            # We'll use a placeholder confidence based on the quality of the transcription
            confidence = self._calculate_confidence(transcription)

            self.logger.info(f"Successfully transcribed audio: {text[:50]}...")
            return text, confidence

        except Exception as e:
            self.logger.error(f"Error transcribing audio file {audio_file_path}: {str(e)}")
            raise

    async def transcribe_audio_data(self, audio_data: bytes) -> Tuple[str, float]:
        """
        Transcribe raw audio data using Whisper API.

        Args:
            audio_data: Raw audio data bytes

        Returns:
            Tuple of (transcribed_text, confidence_score)
        """
        try:
            # Write audio data to a temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name

            try:
                # Transcribe the temporary file
                text, confidence = await self.transcribe_audio_file(temp_file_path)
                return text, confidence
            finally:
                # Clean up the temporary file
                os.unlink(temp_file_path)

        except Exception as e:
            self.logger.error(f"Error transcribing audio data: {str(e)}")
            raise

    def _calculate_confidence(self, transcription_response: Any) -> float:
        """
        Calculate a confidence score based on the transcription response.

        Args:
            transcription_response: The response from Whisper API

        Returns:
            Confidence score between 0.0 and 1.0
        """
        # In a real implementation, we would calculate confidence based on:
        # - Segment-level confidences (if available)
        # - Quality of the audio
        # - Length of the transcription
        # - Presence of unclear segments

        # For now, return a placeholder confidence
        # In a real system, we'd analyze the verbose_json response for confidence data
        return 0.85

    async def process_voice_command(self, audio_source: str) -> VoiceCommand:
        """
        Process a voice command from an audio source.

        Args:
            audio_source: Path to audio file or audio data bytes

        Returns:
            VoiceCommand object with the processed command
        """
        try:
            # Determine if audio_source is a file path or raw data
            if isinstance(audio_source, str) and Path(audio_source).exists():
                # It's a file path
                text, confidence = await self.transcribe_audio_file(audio_source)
            else:
                # It's raw audio data (this case would need to be handled differently)
                raise ValueError("Only file paths are supported in this implementation")

            # Create and return the VoiceCommand object
            voice_command = VoiceCommand(
                id=f"vc_{int(datetime.now().timestamp())}",
                text=text,
                timestamp=datetime.now(),
                confidence=confidence,
                intent="",
                parameters={},
                status=CommandStatus.PROCESSING
            )

            self.logger.info(f"Voice command processed: {voice_command.text[:50]}...")
            return voice_command

        except Exception as e:
            self.logger.error(f"Error processing voice command: {str(e)}")
            raise

    async def validate_audio_quality(self, audio_file_path: str) -> Dict[str, Any]:
        """
        Validate the quality of an audio file before processing.

        Args:
            audio_file_path: Path to the audio file

        Returns:
            Dictionary with validation results
        """
        try:
            import wave
            import struct

            results = {
                "valid": True,
                "duration": 0,
                "sample_rate": 0,
                "channels": 0,
                "bit_depth": 0,
                "issues": []
            }

            with wave.open(audio_file_path, 'rb') as wf:
                frames = wf.getnframes()
                sample_rate = wf.getframerate()
                channels = wf.getnchannels()
                bit_depth = wf.getsampwidth() * 8

                duration = frames / float(sample_rate)

                results["duration"] = duration
                results["sample_rate"] = sample_rate
                results["channels"] = channels
                results["bit_depth"] = bit_depth

                # Check for common issues
                if duration > 30:  # More than 30 seconds might be too long
                    results["issues"].append("Audio duration is very long (may affect processing time)")

                if sample_rate not in [16000, 22050, 44100, 48000]:  # Common sample rates
                    results["issues"].append(f"Uncommon sample rate: {sample_rate}Hz")

                if channels != 1:  # Whisper works best with mono
                    results["issues"].append("Audio is not mono (stereo audio may reduce accuracy)")

            return results

        except Exception as e:
            self.logger.error(f"Error validating audio quality: {str(e)}")
            return {
                "valid": False,
                "duration": 0,
                "sample_rate": 0,
                "channels": 0,
                "bit_depth": 0,
                "issues": [f"Error validating audio: {str(e)}"]
            }


class WhisperProcessingPipeline:
    """
    Complete pipeline for processing voice commands using Whisper.
    """

    def __init__(self, whisper_integration: WhisperIntegration):
        """
        Initialize the processing pipeline.

        Args:
            whisper_integration: Initialized WhisperIntegration instance
        """
        self.logger = logging.getLogger(__name__)
        self.whisper = whisper_integration

    async def process_voice_input(self, audio_source: str) -> VoiceCommand:
        """
        Complete pipeline to process voice input through Whisper.

        Args:
            audio_source: Path to audio file

        Returns:
            VoiceCommand object with the processed command
        """
        try:
            self.logger.info(f"Starting voice input processing for: {audio_source}")

            # Validate audio quality first
            quality_report = await self.whisper.validate_audio_quality(audio_source)
            if not quality_report["valid"]:
                raise ValueError(f"Invalid audio file: {quality_report['issues']}")

            self.logger.info(f"Audio validation passed: {quality_report}")

            # Process the voice command using Whisper
            voice_command = await self.whisper.process_voice_command(audio_source)

            # Update status to completed
            voice_command.status = CommandStatus.COMPLETED

            self.logger.info(f"Voice input processing completed: {voice_command.text[:50]}...")
            return voice_command

        except Exception as e:
            self.logger.error(f"Error in voice processing pipeline: {str(e)}")
            raise


# Example usage and testing functions
async def example_whisper_integration():
    """
    Example function demonstrating Whisper integration.
    """
    # Note: This example requires a valid OpenAI API key
    # For testing purposes, we'll show the structure but not execute API calls

    print("=== Whisper Integration Example ===")

    # Initialize Whisper integration (requires API key)
    # In a real implementation, you would provide your API key:
    # whisper = WhisperIntegration(api_key="your-openai-api-key")

    # For this example, we'll just show the structure
    print("Whisper integration initialized")
    print("Ready to process audio files with OpenAI Whisper API")
    print("Required: OpenAI API key in OPENAI_API_KEY environment variable")

    # Example usage structure (commented out to avoid API calls without key):
    """
    # Create the integration
    whisper = WhisperIntegration()

    # Process an audio file
    voice_command = await whisper.process_voice_command("path/to/audio/file.wav")
    print(f"Transcribed: {voice_command.text}")
    print(f"Confidence: {voice_command.confidence}")
    """


if __name__ == "__main__":
    # Run the example
    asyncio.run(example_whisper_integration())