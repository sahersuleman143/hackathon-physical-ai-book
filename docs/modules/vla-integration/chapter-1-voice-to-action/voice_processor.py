"""
Voice command validation and processing module for the Vision-Language-Action (VLA) system.

This module handles validation of voice commands, confidence scoring, and
initial processing before sending to intent interpretation.
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import numpy as np

from ..shared.models import VoiceCommand, CommandStatus


class VoiceCommandValidator:
    """
    Service for validating voice commands and calculating confidence scores.
    """

    def __init__(self):
        """
        Initialize the voice command validator.
        """
        self.logger = logging.getLogger(__name__)

        # Define patterns for valid commands
        self.command_patterns = [
            # Navigation commands
            r'\b(move|go|walk|drive|navigate)\b.*\b(forward|backward|left|right|up|down)\b',
            r'\b(goto|go to|move to|navigate to)\b.*',
            r'\b(forward|backward|left|right|up|down)\b.*\b(meter|foot|step)\b',

            # Manipulation commands
            r'\b(pick|grasp|take|grab|lift|hold)\b.*\b(up|object|item)\b',
            r'\b(place|put|set|drop|release)\b.*',
            r'\b(move|lift|rotate|turn)\b.*\b(object|item|thing)\b',

            # Detection commands
            r'\b(find|locate|detect|see|spot)\b.*',
            r'\b(look|search|scan)\b.*\b(for|at)\b',

            # General commands
            r'\b(stop|halt|pause|wait|stand)\b',
            r'\b(how|what|where|when)\b.*\b(are|is|do|can)\b'  # Question commands
        ]

        # Define common stop words that might indicate low-quality commands
        self.stop_words = {
            'um', 'uh', 'like', 'you', 'know', 'well', 'so', 'actually',
            'basically', 'literally', 'very', 'really', 'quite', 'pretty'
        }

    def validate_command_text(self, text: str) -> Tuple[bool, List[str]]:
        """
        Validate the text of a voice command.

        Args:
            text: The transcribed voice command text

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        # Check if text is empty
        if not text or not text.strip():
            issues.append("Command text is empty")
            return False, issues

        # Check minimum length
        if len(text.strip()) < 3:
            issues.append("Command text is too short (less than 3 characters)")

        # Check for excessive stop words (indicating unclear speech)
        words = text.lower().split()
        stop_word_count = sum(1 for word in words if word in self.stop_words)
        if len(words) > 0 and (stop_word_count / len(words)) > 0.3:  # More than 30% stop words
            issues.append("Command contains excessive filler words")

        # Check if command matches expected patterns
        if not any(re.search(pattern, text.lower()) for pattern in self.command_patterns):
            issues.append("Command does not match expected robot command patterns")

        # Check for excessive punctuation or special characters
        special_char_ratio = len(re.findall(r'[^\w\s]', text)) / len(text)
        if special_char_ratio > 0.1:  # More than 10% special characters
            issues.append("Command contains excessive special characters (may indicate transcription errors)")

        is_valid = len(issues) == 0
        return is_valid, issues

    def calculate_text_confidence(self, text: str, original_confidence: float = None) -> float:
        """
        Calculate a confidence score for the transcribed text based on quality indicators.

        Args:
            text: The transcribed voice command text
            original_confidence: Original confidence from speech-to-text service (if available)

        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not text or not text.strip():
            return 0.0

        # Start with original confidence if provided, otherwise use a base score
        confidence = original_confidence if original_confidence is not None else 0.7

        # Adjust based on text quality
        words = text.lower().split()

        # Reduce confidence for excessive stop words
        stop_word_count = sum(1 for word in words if word in self.stop_words)
        if len(words) > 0:
            stop_word_ratio = stop_word_count / len(words)
            confidence *= (1 - stop_word_ratio * 0.3)  # Reduce up to 30% for stop words

        # Increase confidence if command matches expected patterns
        pattern_matches = sum(1 for pattern in self.command_patterns if re.search(pattern, text.lower()))
        if pattern_matches > 0:
            confidence += 0.1 * min(pattern_matches, 3)  # Up to 30% boost for pattern matches
            confidence = min(confidence, 1.0)  # Cap at 1.0

        # Reduce confidence for very long commands (might be unclear)
        if len(words) > 15:  # Arbitrary threshold for "too long"
            confidence *= 0.8

        # Reduce confidence for commands with excessive special characters
        special_char_ratio = len(re.findall(r'[^\w\s]', text)) / len(text)
        if special_char_ratio > 0.1:
            confidence *= 0.7

        # Ensure confidence is within bounds
        confidence = max(0.0, min(1.0, confidence))

        return confidence

    def validate_voice_command(self, voice_command: VoiceCommand) -> Tuple[bool, List[str], float]:
        """
        Validate a complete VoiceCommand object.

        Args:
            voice_command: The VoiceCommand to validate

        Returns:
            Tuple of (is_valid, list_of_issues, adjusted_confidence)
        """
        issues = []

        # Validate text
        text_valid, text_issues = self.validate_command_text(voice_command.text)
        if not text_valid:
            issues.extend(text_issues)

        # Validate confidence score
        if not (0.0 <= voice_command.confidence <= 1.0):
            issues.append(f"Confidence score {voice_command.confidence} is out of valid range [0.0, 1.0]")

        # Validate other fields
        if not voice_command.id:
            issues.append("Voice command ID is missing")

        # Calculate adjusted confidence based on text quality
        adjusted_confidence = self.calculate_text_confidence(voice_command.text, voice_command.confidence)

        # Check if adjusted confidence is too low
        if adjusted_confidence < 0.3:
            issues.append(f"Adjusted confidence score {adjusted_confidence:.2f} is below minimum threshold (0.3)")

        is_valid = len(issues) == 0 and adjusted_confidence >= 0.3
        return is_valid, issues, adjusted_confidence


class VoiceCommandProcessor:
    """
    Service for processing voice commands with validation and confidence scoring.
    """

    def __init__(self):
        """
        Initialize the voice command processor.
        """
        self.logger = logging.getLogger(__name__)
        self.validator = VoiceCommandValidator()

    async def process_voice_command(self, voice_command: VoiceCommand) -> VoiceCommand:
        """
        Process a voice command with validation and confidence adjustment.

        Args:
            voice_command: The voice command to process

        Returns:
            Processed VoiceCommand with updated status and confidence
        """
        try:
            self.logger.info(f"Processing voice command: {voice_command.text[:50]}...")

            # Validate the command
            is_valid, issues, adjusted_confidence = self.validator.validate_voice_command(voice_command)

            # Update the voice command with adjusted confidence
            voice_command.confidence = adjusted_confidence

            if is_valid:
                voice_command.status = CommandStatus.PROCESSING
                self.logger.info(f"Voice command validated successfully with confidence {adjusted_confidence:.2f}")
            else:
                voice_command.status = CommandStatus.FAILED
                self.logger.warning(f"Voice command validation failed: {', '.join(issues)}")

            # Log validation results
            if issues:
                for issue in issues:
                    self.logger.debug(f"Validation issue: {issue}")

            return voice_command

        except Exception as e:
            self.logger.error(f"Error processing voice command: {str(e)}")
            # Mark as failed if there's an exception
            voice_command.status = CommandStatus.FAILED
            return voice_command

    async def process_command_batch(self, voice_commands: List[VoiceCommand]) -> List[VoiceCommand]:
        """
        Process a batch of voice commands.

        Args:
            voice_commands: List of voice commands to process

        Returns:
            List of processed voice commands
        """
        processed_commands = []

        for command in voice_commands:
            processed = await self.process_voice_command(command)
            processed_commands.append(processed)

        return processed_commands

    def suggest_command_correction(self, text: str) -> List[str]:
        """
        Suggest possible corrections for a potentially unclear command.

        Args:
            text: The potentially unclear command text

        Returns:
            List of suggested corrected commands
        """
        suggestions = []

        # Simple corrections - in a real system, this would use more sophisticated NLP
        text_lower = text.lower().strip()

        # Navigation corrections
        if re.search(r'\b(gow|goe|ow)\b', text_lower):
            suggestions.append(text.replace('gow', 'go').replace('goe', 'go').replace('ow', 'go'))

        if re.search(r'\b(mive|movee|mov)\b', text_lower):
            suggestions.append(text.replace('mive', 'move').replace('movee', 'move').replace('mov', 'move'))

        # Common misrecognitions
        if 'for word' in text_lower:
            suggestions.append(text.replace('for word', 'forward'))
        elif 'for ward' in text_lower:
            suggestions.append(text.replace('for ward', 'forward'))

        if 'pick up' not in text_lower and ('pick' in text_lower or 'up' in text_lower):
            if 'pick' in text_lower and 'up' not in text_lower:
                suggestions.append(text + ' up')
            elif 'up' in text_lower and 'pick' not in text_lower:
                suggestions.append('pick ' + text)

        return suggestions


class ConfidenceScorer:
    """
    Advanced confidence scoring for voice commands.
    """

    def __init__(self):
        """
        Initialize the confidence scorer.
        """
        self.logger = logging.getLogger(__name__)

    def score_command_contextual(self, text: str, environment_context: Optional[Dict] = None,
                                robot_capabilities: Optional[List[str]] = None) -> float:
        """
        Score a command based on contextual information.

        Args:
            text: The command text
            environment_context: Context about the environment
            robot_capabilities: List of robot capabilities

        Returns:
            Contextual confidence score
        """
        base_score = 0.7  # Base score

        # Check if command aligns with robot capabilities
        if robot_capabilities:
            command_lower = text.lower()
            has_capability_match = False

            for capability in robot_capabilities:
                if capability.lower() in command_lower:
                    has_capability_match = True
                    base_score += 0.1
                    break

            if not has_capability_match:
                # Check if command implies a capability the robot might have
                if any(word in command_lower for word in ['move', 'go', 'navigate', 'pick', 'grasp', 'take']):
                    base_score += 0.05

        # Check if command mentions objects that exist in environment
        if environment_context and 'objects' in environment_context:
            object_names = [obj.get('type', '').lower() for obj in environment_context['objects']]
            for obj_name in object_names:
                if obj_name and obj_name in text.lower():
                    base_score += 0.1
                    break

        # Ensure score is within bounds
        return max(0.0, min(1.0, base_score))

    def score_command_completeness(self, text: str) -> float:
        """
        Score how complete a command appears to be.

        Args:
            text: The command text

        Returns:
            Completeness confidence score
        """
        # A simple completeness score based on command structure
        words = text.strip().split()

        if len(words) < 2:
            return 0.3  # Very short commands are likely incomplete

        # Check for action-object patterns
        command_patterns = [
            r'\b(pick|grasp|take|grab)\b.*\b(object|item|cup|box|ball)\b',
            r'\b(go|move|walk|navigate)\b.*\b(to|toward|the)\b',
            r'\b(find|locate|detect)\b.*\b(object|item|person|thing)\b'
        ]

        if any(re.search(pattern, text.lower()) for pattern in command_patterns):
            return 0.9  # Good structure

        # Default score based on length
        if len(words) >= 4:
            return 0.7  # Good length
        elif len(words) >= 3:
            return 0.6  # Decent length
        else:
            return 0.5  # Short but might be valid


# Example usage and testing functions
async def example_voice_validation():
    """
    Example function demonstrating voice command validation and confidence scoring.
    """
    print("=== Voice Command Validation Example ===")

    # Initialize the processor
    processor = VoiceCommandProcessor()
    scorer = ConfidenceScorer()

    # Example 1: Valid command
    print("\nExample 1: Valid command")
    valid_command = VoiceCommand(
        id="vc_1",
        text="Move forward 2 meters",
        timestamp=datetime.now(),
        confidence=0.85,
        intent="",
        parameters={},
        status=CommandStatus.PENDING
    )

    processed = await processor.process_voice_command(valid_command)
    print(f"Original: '{valid_command.text}'")
    print(f"Original confidence: {valid_command.confidence:.2f}")
    print(f"Processed confidence: {processed.confidence:.2f}")
    print(f"Status: {processed.status.value}")

    # Example 2: Invalid command (too short)
    print("\nExample 2: Invalid command (too short)")
    short_command = VoiceCommand(
        id="vc_2",
        text="Go",
        timestamp=datetime.now(),
        confidence=0.75,
        intent="",
        parameters={},
        status=CommandStatus.PENDING
    )

    processed_short = await processor.process_voice_command(short_command)
    print(f"Original: '{short_command.text}'")
    print(f"Original confidence: {short_command.confidence:.2f}")
    print(f"Processed confidence: {processed_short.confidence:.2f}")
    print(f"Status: {processed_short.status.value}")

    # Example 3: Command with potential misrecognition
    print("\nExample 3: Command with potential misrecognition")
    misrec_command = VoiceCommand(
        id="vc_3",
        text="Gow forward to the cup",
        timestamp=datetime.now(),
        confidence=0.65,
        intent="",
        parameters={},
        status=CommandStatus.PENDING
    )

    processed_misrec = await processor.process_voice_command(misrec_command)
    print(f"Original: '{misrec_command.text}'")
    print(f"Original confidence: {misrec_command.confidence:.2f}")
    print(f"Processed confidence: {processed_misrec.confidence:.2f}")
    print(f"Status: {processed_misrec.status.value}")

    # Show suggestions for the misrecognized command
    suggestions = processor.suggest_command_correction(misrec_command.text)
    if suggestions:
        print(f"Suggested corrections: {suggestions}")

    # Example 4: Contextual scoring
    print("\nExample 4: Contextual confidence scoring")
    env_context = {
        "objects": [
            {"type": "red cup", "id": "obj_1"},
            {"type": "blue box", "id": "obj_2"}
        ]
    }
    robot_caps = ["navigation", "manipulation"]

    contextual_score = scorer.score_command_contextual(
        "Pick up the red cup",
        env_context,
        robot_caps
    )
    print(f"Command: 'Pick up the red cup'")
    print(f"Contextual confidence: {contextual_score:.2f}")

    completeness_score = scorer.score_command_completeness("Pick up the red cup")
    print(f"Completeness score: {completeness_score:.2f}")


if __name__ == "__main__":
    # Run the example
    asyncio.run(example_voice_validation())