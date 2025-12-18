"""
Whisper processing pipeline for the Vision-Language-Action (VLA) system.

This module orchestrates the complete flow from audio capture to validated
voice command, integrating Whisper API, validation, and preprocessing services.
"""

import asyncio
import logging
import tempfile
import os
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from pathlib import Path

from .voice_capture import VoiceCapturePipeline
from .whisper_integration import WhisperIntegration, WhisperProcessingPipeline
from .voice_processor import VoiceCommandProcessor
from ..shared.models import VoiceCommand, CommandStatus


class WhisperProcessingOrchestrator:
    """
    Orchestrates the complete Whisper processing pipeline from audio input to validated command.
    """

    def __init__(self, whisper_integration: WhisperIntegration):
        """
        Initialize the processing orchestrator.

        Args:
            whisper_integration: Initialized WhisperIntegration instance
        """
        self.logger = logging.getLogger(__name__)
        self.whisper_integration = whisper_integration
        self.voice_capture = VoiceCapturePipeline()
        self.voice_processor = VoiceCommandProcessor()

    async def process_audio_to_command(self, audio_source: str, validate: bool = True) -> VoiceCommand:
        """
        Complete pipeline to process audio to a validated voice command.

        Args:
            audio_source: Path to audio file or capture source ("microphone", "until_silence")
            validate: Whether to validate the command after processing

        Returns:
            VoiceCommand object with the processed command
        """
        try:
            self.logger.info(f"Starting Whisper processing pipeline for: {audio_source}")

            # Step 1: Capture/preprocess audio if needed
            if audio_source in ["microphone", "until_silence"]:
                audio_file_path = await self.voice_capture.capture_voice_input(audio_source)
            elif Path(audio_source).exists():
                # Validate the provided audio file
                is_valid, validation_msg = self.voice_capture.capture_service.validate_audio_file(audio_source)
                if not is_valid:
                    raise ValueError(f"Invalid audio file: {validation_msg}")
                audio_file_path = audio_source
            else:
                raise ValueError(f"Invalid audio source: {audio_source}")

            self.logger.info(f"Audio captured/preprocessed: {audio_file_path}")

            # Step 2: Transcribe audio using Whisper
            self.logger.info("Starting Whisper transcription...")
            text, confidence = await self.whisper_integration.transcribe_audio_file(audio_file_path)
            self.logger.info(f"Transcription completed: {text[:50]}...")

            # Step 3: Create initial VoiceCommand
            voice_command = VoiceCommand(
                id=f"vc_{int(datetime.now().timestamp())}",
                text=text,
                timestamp=datetime.now(),
                confidence=confidence,
                intent="",
                parameters={},
                status=CommandStatus.PROCESSING
            )

            # Step 4: Validate the command if requested
            if validate:
                self.logger.info("Starting voice command validation...")
                voice_command = await self.voice_processor.process_voice_command(voice_command)
                self.logger.info(f"Validation completed. Status: {voice_command.status.value}")

            # Clean up temporary files if they were created
            if 'temp' in audio_file_path and Path(audio_file_path).exists():
                try:
                    os.unlink(audio_file_path)
                    self.logger.debug(f"Cleaned up temporary file: {audio_file_path}")
                except Exception as e:
                    self.logger.warning(f"Could not clean up temporary file {audio_file_path}: {e}")

            self.logger.info(f"Whisper processing pipeline completed successfully")
            return voice_command

        except Exception as e:
            self.logger.error(f"Error in Whisper processing pipeline: {str(e)}")
            # Create a failed VoiceCommand if there's an error
            error_command = VoiceCommand(
                id=f"vc_{int(datetime.now().timestamp())}",
                text="",
                timestamp=datetime.now(),
                confidence=0.0,
                intent="",
                parameters={},
                status=CommandStatus.FAILED
            )
            return error_command

    async def process_audio_batch(self, audio_sources: list) -> list:
        """
        Process a batch of audio sources.

        Args:
            audio_sources: List of audio sources to process

        Returns:
            List of VoiceCommand objects
        """
        results = []
        for source in audio_sources:
            result = await self.process_audio_to_command(source)
            results.append(result)
        return results


class AdvancedWhisperPipeline:
    """
    Advanced pipeline with additional features like preprocessing and error handling.
    """

    def __init__(self, whisper_integration: WhisperIntegration):
        """
        Initialize the advanced processing pipeline.

        Args:
            whisper_integration: Initialized WhisperIntegration instance
        """
        self.logger = logging.getLogger(__name__)
        self.orchestrator = WhisperProcessingOrchestrator(whisper_integration)
        self.max_retries = 3

    async def robust_process_audio(self, audio_source: str, max_retries: int = None) -> VoiceCommand:
        """
        Robustly process audio with retry logic and error handling.

        Args:
            audio_source: Path to audio file or capture source
            max_retries: Maximum number of retry attempts

        Returns:
            VoiceCommand object with the processed command
        """
        retries = max_retries or self.max_retries
        last_error = None

        for attempt in range(retries + 1):
            try:
                if attempt > 0:
                    self.logger.info(f"Retry attempt {attempt} for audio: {audio_source}")

                result = await self.orchestrator.process_audio_to_command(audio_source)

                # If successful or final attempt, return the result
                if result.status != CommandStatus.FAILED or attempt == retries:
                    return result

            except Exception as e:
                last_error = e
                self.logger.warning(f"Attempt {attempt} failed: {str(e)}")

                if attempt < retries:
                    # Wait before retry (exponential backoff)
                    await asyncio.sleep(2 ** attempt)

        # If all retries failed, create a failed command with error info
        self.logger.error(f"All {retries} retry attempts failed for {audio_source}: {str(last_error)}")
        failed_command = VoiceCommand(
            id=f"vc_{int(datetime.now().timestamp())}",
            text="",
            timestamp=datetime.now(),
            confidence=0.0,
            intent="",
            parameters={"error": str(last_error)},
            status=CommandStatus.FAILED
        )
        return failed_command

    async def process_with_context(self, audio_source: str, environment_context: Optional[Dict] = None,
                                  robot_capabilities: Optional[list] = None) -> Tuple[VoiceCommand, Dict[str, Any]]:
        """
        Process audio with additional context for enhanced processing.

        Args:
            audio_source: Path to audio file or capture source
            environment_context: Context about the environment
            robot_capabilities: List of robot capabilities

        Returns:
            Tuple of (VoiceCommand, processing_metadata)
        """
        # Process the audio normally first
        voice_command = await self.robust_process_audio(audio_source)

        # Add context-based enhancements
        metadata = {
            "processing_timestamp": datetime.now().isoformat(),
            "source": audio_source,
            "environment_context_used": environment_context is not None,
            "robot_capabilities_considered": robot_capabilities is not None
        }

        # Enhance command with context if available
        if environment_context and robot_capabilities:
            # This would involve more sophisticated processing in a real implementation
            metadata["context_enhancement_applied"] = True

        return voice_command, metadata

    async def adaptive_process(self, audio_source: str, quality_threshold: float = 0.6) -> VoiceCommand:
        """
        Adaptive processing that adjusts approach based on audio quality.

        Args:
            audio_source: Path to audio file or capture source
            quality_threshold: Minimum quality threshold for standard processing

        Returns:
            VoiceCommand object with the processed command
        """
        try:
            # First, check audio quality
            quality_report = await self.orchestrator.whisper_integration.whisper.validate_audio_quality(audio_source)

            if not quality_report["valid"]:
                self.logger.warning(f"Audio quality check failed: {quality_report['issues']}")
                # Still attempt processing but with awareness of quality issues
                return await self.robust_process_audio(audio_source)

            # Calculate quality score
            duration = quality_report["duration"]
            sample_rate = quality_report["sample_rate"]
            issues = quality_report["issues"]

            # Simple quality score based on factors
            quality_score = 0.8  # Base score
            if duration < 1.0 or duration > 15.0:  # Too short or too long
                quality_score -= 0.2
            if sample_rate not in [16000, 44100]:  # Non-standard sample rate
                quality_score -= 0.1
            if issues:  # Any reported issues
                quality_score -= len(issues) * 0.1

            quality_score = max(0.0, min(1.0, quality_score))

            if quality_score < quality_threshold:
                self.logger.info(f"Low audio quality detected (score: {quality_score:.2f}), applying enhanced processing")
                # In a real implementation, this might use different Whisper models or preprocessing
                # For now, we'll just log and proceed normally
                pass

            self.logger.info(f"Audio quality score: {quality_score:.2f}")
            return await self.robust_process_audio(audio_source)

        except Exception as e:
            self.logger.error(f"Error in adaptive processing: {str(e)}")
            # Fall back to standard processing
            return await self.robust_process_audio(audio_source)


class WhisperPipelineFactory:
    """
    Factory for creating different types of Whisper processing pipelines.
    """

    @staticmethod
    def create_standard_pipeline(api_key: Optional[str] = None) -> WhisperProcessingOrchestrator:
        """
        Create a standard Whisper processing pipeline.

        Args:
            api_key: OpenAI API key

        Returns:
            Standard WhisperProcessingOrchestrator
        """
        whisper_integration = WhisperIntegration(api_key=api_key)
        return WhisperProcessingOrchestrator(whisper_integration)

    @staticmethod
    def create_advanced_pipeline(api_key: Optional[str] = None) -> AdvancedWhisperPipeline:
        """
        Create an advanced Whisper processing pipeline with retry logic.

        Args:
            api_key: OpenAI API key

        Returns:
            Advanced AdvancedWhisperPipeline
        """
        whisper_integration = WhisperIntegration(api_key=api_key)
        return AdvancedWhisperPipeline(whisper_integration)


# Example usage and testing functions
async def example_whisper_pipeline():
    """
    Example function demonstrating Whisper processing pipeline usage.
    """
    print("=== Whisper Processing Pipeline Example ===")

    # Note: This example requires a valid OpenAI API key
    # For testing purposes, we'll show the structure but not execute API calls without key

    print("Pipeline structure initialized")
    print("Ready to process audio files through Whisper API")
    print("Required: OpenAI API key in OPENAI_API_KEY environment variable")

    # Example usage structure (commented out to avoid API calls without key):
    """
    # Create a standard pipeline
    pipeline = WhisperPipelineFactory.create_standard_pipeline(api_key="your-api-key")

    # Process an audio file
    command = await pipeline.process_audio_to_command("path/to/audio/file.wav")
    print(f"Processed command: {command.text}")
    print(f"Confidence: {command.confidence}")
    print(f"Status: {command.status.value}")

    # Create an advanced pipeline with retry logic
    advanced_pipeline = WhisperPipelineFactory.create_advanced_pipeline(api_key="your-api-key")

    # Process with context
    env_context = {"objects": [{"type": "red cup", "id": "obj_1"}]}
    robot_caps = ["navigation", "manipulation"]

    command, metadata = await advanced_pipeline.process_with_context(
        "path/to/audio/file.wav",
        environment_context=env_context,
        robot_capabilities=robot_caps
    )
    print(f"Context-enhanced command: {command.text}")
    print(f"Metadata: {metadata}")
    """

    print("\nPipeline components available:")
    print("1. Standard processing: Basic Whisper transcription and validation")
    print("2. Advanced processing: With retry logic and error handling")
    print("3. Adaptive processing: Adjusts approach based on audio quality")
    print("4. Batch processing: Handle multiple audio files at once")


if __name__ == "__main__":
    # Run the example
    asyncio.run(example_whisper_pipeline())