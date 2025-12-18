"""
Speech processing code examples for the Vision-Language-Action (VLA) system.

This module provides practical examples and educational code snippets for
voice command processing, demonstrating various aspects of the Whisper
integration and voice processing pipeline.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any
import numpy as np

# Import the VLA system modules
from ..shared.models import VoiceCommand, CommandStatus
from .whisper_integration import WhisperIntegration
from .voice_capture import VoiceCapturePipeline
from .voice_processor import VoiceCommandProcessor, VoiceCommandValidator
from .whisper_pipeline import WhisperProcessingOrchestrator
from .basic_workflow import VoiceCommandWorkflow


# Configure logging for examples
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_1_basic_transcription():
    """
    Example 1: Basic Whisper transcription with file input.

    This example demonstrates the simplest use of the Whisper API integration
    to transcribe an audio file to text.
    """
    print("=== Example 1: Basic Whisper Transcription ===")

    # Note: This example requires a valid OpenAI API key
    # For demonstration purposes, we'll show the structure
    print("This example shows how to transcribe an audio file using Whisper:")
    print("# whisper = WhisperIntegration(api_key='your-api-key')")
    print("# text, confidence = await whisper.transcribe_audio_file('path/to/audio.wav')")
    print("# print(f'Transcribed: {text}')")
    print("# print(f'Confidence: {confidence}')")

    # In a real implementation:
    """
    whisper = WhisperIntegration(api_key="your-api-key")
    text, confidence = await whisper.transcribe_audio_file("path/to/audio.wav")
    print(f"Transcribed: {text}")
    print(f"Confidence: {confidence:.2f}")
    """


async def example_2_microphone_capture():
    """
    Example 2: Capturing voice input from microphone.

    This example shows how to capture voice input directly from the microphone
    and process it through the VLA system.
    """
    print("\n=== Example 2: Microphone Voice Capture ===")

    print("This example demonstrates capturing voice input from the microphone:")
    print("# capture = VoiceCapturePipeline()")
    print("# audio_file = await capture.capture_voice_input('microphone', duration=5.0)")
    print("# print(f'Captured: {audio_file}')")

    # In a real implementation:
    """
    capture = VoiceCapturePipeline()
    audio_file = await capture.capture_voice_input('microphone', duration=5.0)
    print(f"Captured: {audio_file}")
    """


async def example_3_complete_workflow():
    """
    Example 3: Complete voice command workflow.

    This example demonstrates the full workflow from audio capture to
    validated voice command ready for intent interpretation.
    """
    print("\n=== Example 3: Complete Voice Command Workflow ===")

    print("This example shows the complete workflow:")
    print("# workflow = VoiceCommandWorkflow(api_key='your-api-key')")
    print("# command, intent = await workflow.process_voice_command_complete('microphone')")
    print("# print(f'Command: {command.text}')")
    print("# print(f'Intent: {intent}')")
    print("# print(f'Confidence: {command.confidence}')")

    # In a real implementation:
    """
    workflow = VoiceCommandWorkflow(api_key="your-api-key")
    command, intent = await workflow.process_voice_command_complete('microphone')
    print(f"Command: {command.text}")
    print(f"Intent: {intent}")
    print(f"Confidence: {command.confidence:.2f}")
    print(f"Status: {command.status.value}")
    """


async def example_4_command_validation():
    """
    Example 4: Voice command validation and confidence scoring.

    This example demonstrates how voice commands are validated and scored
    for quality before processing.
    """
    print("\n=== Example 4: Command Validation and Confidence Scoring ===")

    # Create a validator instance
    validator = VoiceCommandValidator()

    # Test various command texts
    test_commands = [
        "Move forward 2 meters",  # Good command
        "Go to the kitchen",      # Good command
        "Um like go forward",     # Poor quality with filler words
        "Go",                     # Too short
        "Pick up the red cube",   # Good manipulation command
    ]

    for text in test_commands:
        is_valid, issues = validator.validate_command_text(text)
        confidence = validator.calculate_text_confidence(text)

        print(f"Command: '{text}'")
        print(f"  Valid: {is_valid}")
        print(f"  Confidence: {confidence:.2f}")
        if issues:
            print(f"  Issues: {', '.join(issues)}")
        print()


async def example_5_pipeline_processing():
    """
    Example 5: Using the Whisper processing pipeline.

    This example shows how to use the orchestrated pipeline that combines
    Whisper integration with validation and preprocessing.
    """
    print("\n=== Example 5: Whisper Processing Pipeline ===")

    print("This example demonstrates the processing pipeline:")
    print("# whisper = WhisperIntegration(api_key='your-api-key')")
    print("# orchestrator = WhisperProcessingOrchestrator(whisper)")
    print("# command = await orchestrator.process_audio_to_command('path/to/audio.wav')")
    print("# print(f'Processed: {command.text}')")

    # In a real implementation:
    """
    whisper = WhisperIntegration(api_key="your-api-key")
    orchestrator = WhisperProcessingOrchestrator(whisper)
    command = await orchestrator.process_audio_to_command('path/to/audio.wav')
    print(f"Processed: {command.text}")
    print(f"Confidence: {command.confidence:.2f}")
    print(f"Status: {command.status.value}")
    """


async def example_6_error_handling():
    """
    Example 6: Error handling and robust processing.

    This example demonstrates how to handle errors and implement robust
    processing for voice commands.
    """
    print("\n=== Example 6: Error Handling and Robust Processing ===")

    try:
        # Simulate processing with error handling
        print("Processing voice command with error handling...")

        # Create a mock voice command with low confidence
        low_conf_command = VoiceCommand(
            id="test_1",
            text="Um like maybe go or something",
            timestamp=datetime.now(),
            confidence=0.2,  # Low confidence
            intent="",
            parameters={},
            status=CommandStatus.PENDING
        )

        # Process with validation
        processor = VoiceCommandProcessor()
        result = await processor.process_voice_command(low_conf_command)

        print(f"Command: {result.text}")
        print(f"Status: {result.status.value}")
        print(f"Confidence: {result.confidence:.2f}")

        # Show suggestions for improvement
        suggestions = processor.suggest_command_correction(result.text)
        if suggestions:
            print(f"Suggestions: {suggestions}")

    except Exception as e:
        print(f"Error in processing: {e}")


async def example_7_batch_processing():
    """
    Example 7: Batch processing of multiple voice commands.

    This example demonstrates how to process multiple voice commands
    efficiently in batch mode.
    """
    print("\n=== Example 7: Batch Processing ===")

    # Simulate processing multiple commands
    sample_texts = [
        "Move forward 1 meter",
        "Turn left 90 degrees",
        "Pick up the object",
        "Stop moving"
    ]

    processor = VoiceCommandProcessor()
    whisper = WhisperIntegration()  # This won't work without API key, just for structure

    print("Processing batch of commands:")
    for i, text in enumerate(sample_texts, 1):
        # Create a voice command from text (for demonstration)
        try:
            cmd = whisper.whisper.create_voice_command_from_text(text, confidence=0.8)
            result = await processor.process_voice_command(cmd)
            print(f"  {i}. '{result.text}' -> {result.status.value} (conf: {result.confidence:.2f})")
        except Exception as e:
            print(f"  {i}. Error processing '{text}': {e}")


async def example_8_educational_demo():
    """
    Example 8: Educational demonstration for students.

    This example provides a complete demonstration suitable for educational
    purposes, showing how voice commands flow through the system.
    """
    print("\n=== Example 8: Educational Demonstration ===")

    print("Voice Command Processing Pipeline Demonstration")
    print("=" * 50)

    # Simulate the complete process step by step
    print("\nStep 1: Audio Capture")
    print("  - Student speaks command: 'Move forward 2 meters'")
    print("  - System captures audio from microphone")

    print("\nStep 2: Speech-to-Text Transcription")
    print("  - Whisper API converts audio to text")
    print("  - Result: 'Move forward 2 meters'")

    print("\nStep 3: Command Validation")
    print("  - System validates command structure")
    print("  - Checks for proper command patterns")
    print("  - Calculates confidence score")

    print("\nStep 4: Intent Interpretation")
    print("  - LLM interprets the intent")
    print("  - Result: 'navigation' intent with parameters")

    print("\nStep 5: Action Planning")
    print("  - System generates action plan")
    print("  - Plan: Move robot forward 2 meters")

    print("\nStep 6: Execution")
    print("  - Robot executes the planned action")
    print("  - Confirmation provided to student")


async def example_9_quality_assessment():
    """
    Example 9: Audio quality assessment and preprocessing.

    This example demonstrates how audio quality is assessed and improved
    before processing.
    """
    print("\n=== Example 9: Audio Quality Assessment ===")

    capture = VoiceCapturePipeline()

    print("Audio quality assessment includes:")
    print("1. Duration validation (should be 0.1s to 30s)")
    print("2. Sample rate verification (should be standard rate)")
    print("3. Channel verification (should be mono)")
    print("4. Noise level assessment")

    # Show how validation works
    print("\nValidation example:")
    print("# is_valid, message = capture.capture_service.validate_audio_file('audio.wav')")
    print("# print(f'Valid: {is_valid}, Message: {message}')")


async def example_10_performance_metrics():
    """
    Example 10: Performance metrics and monitoring.

    This example shows how to track performance metrics for voice processing.
    """
    print("\n=== Example 10: Performance Metrics ===")

    # Simulate tracking metrics
    metrics = {
        "transcription_accuracy": 0.92,
        "average_confidence": 0.78,
        "processing_time": 1.2,  # seconds
        "success_rate": 0.89,
        "command_types": {
            "navigation": 45,
            "manipulation": 30,
            "detection": 15,
            "other": 10
        }
    }

    print("Performance Metrics:")
    for key, value in metrics.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for sub_key, sub_value in value.items():
                print(f"    {sub_key}: {sub_value}")
        else:
            print(f"  {key}: {value}")


def run_all_examples():
    """
    Run all examples in sequence.
    """
    print("Vision-Language-Action System - Speech Processing Examples")
    print("=" * 60)

    # Run each example
    examples = [
        example_1_basic_transcription,
        example_2_microphone_capture,
        example_3_complete_workflow,
        example_4_command_validation,
        example_5_pipeline_processing,
        example_6_error_handling,
        example_7_batch_processing,
        example_8_educational_demo,
        example_9_quality_assessment,
        example_10_performance_metrics
    ]

    for example_func in examples:
        try:
            asyncio.run(example_func())
        except Exception as e:
            print(f"Error running {example_func.__name__}: {e}")

        # Add a separator between examples
        if example_func != examples[-1]:
            print("\n" + "-" * 40)


# Additional utility functions for educational purposes

def create_command_analysis(text: str) -> Dict[str, Any]:
    """
    Analyze a voice command and provide educational feedback.

    Args:
        text: The command text to analyze

    Returns:
        Dictionary with analysis results
    """
    analysis = {
        "command": text,
        "length": len(text),
        "word_count": len(text.split()),
        "has_navigation": any(word in text.lower() for word in ["move", "go", "forward", "backward", "left", "right"]),
        "has_manipulation": any(word in text.lower() for word in ["pick", "grasp", "take", "put", "place"]),
        "has_detection": any(word in text.lower() for word in ["find", "locate", "detect", "see"]),
        "suggestions": []
    }

    # Add suggestions based on analysis
    if analysis["word_count"] < 3:
        analysis["suggestions"].append("Command is very short - try adding more specific details")

    if not (analysis["has_navigation"] or analysis["has_manipulation"] or analysis["has_detection"]):
        analysis["suggestions"].append("Command doesn't clearly indicate robot action - add navigation, manipulation, or detection words")

    if "um" in text.lower() or "uh" in text.lower():
        analysis["suggestions"].append("Avoid filler words like 'um' or 'uh' for clearer commands")

    return analysis


def demonstrate_command_analysis():
    """
    Demonstrate command analysis with sample commands.
    """
    print("\n=== Command Analysis Demonstration ===")

    sample_commands = [
        "Move forward 2 meters",
        "Go to the red cube",
        "Pick up that thing",
        "Um go forward I think",
        "Stop",
        "Find the blue object"
    ]

    for cmd in sample_commands:
        analysis = create_command_analysis(cmd)
        print(f"\nCommand: '{cmd}'")
        print(f"  Length: {analysis['length']} chars, {analysis['word_count']} words")
        print(f"  Types: Nav={analysis['has_navigation']}, Manip={analysis['has_manipulation']}, Detect={analysis['has_detection']}")
        if analysis['suggestions']:
            print(f"  Suggestions: {', '.join(analysis['suggestions'])}")
        else:
            print("  Suggestions: Command looks good!")


if __name__ == "__main__":
    # Run all examples
    run_all_examples()

    # Also run the command analysis demonstration
    demonstrate_command_analysis()

    print("\n" + "=" * 60)
    print("All speech processing examples completed!")
    print("These examples demonstrate various aspects of voice command processing")
    print("in the Vision-Language-Action system for educational purposes.")