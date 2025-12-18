"""
Voice command processing service for the Vision-Language-Action (VLA) integration system.

This module handles the processing of voice commands from capture to intent interpretation,
including speech-to-text conversion using OpenAI Whisper and initial validation.
"""

import asyncio
import base64
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from openai import OpenAI
import pyaudio
import wave
import json

from .models import VoiceCommand, CommandStatus, UserIntent


class VoiceCommandProcessor:
    """
    Service for processing voice commands from capture to intent interpretation.
    """

    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the voice command processor.

        Args:
            openai_api_key: OpenAI API key for Whisper and LLM integration
        """
        self.logger = logging.getLogger(__name__)
        self.openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None

        # Audio configuration
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.chunk = 1024
        self.record_seconds = 5  # Default recording duration

    def capture_voice_input(self, duration: int = 5) -> str:
        """
        Capture voice input from the microphone and save as WAV file.

        Args:
            duration: Recording duration in seconds

        Returns:
            Path to the recorded audio file
        """
        audio = pyaudio.PyAudio()

        # Start recording
        stream = audio.open(
            format=self.audio_format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )

        self.logger.info(f"Recording for {duration} seconds...")
        frames = []

        for _ in range(0, int(self.rate / self.chunk * duration)):
            data = stream.read(self.chunk)
            frames.append(data)

        self.logger.info("Recording finished.")

        # Stop recording
        stream.stop_stream()
        stream.close()
        audio.terminate()

        # Save the recorded audio to a WAV file
        filename = f"temp_recording_{int(datetime.now().timestamp())}.wav"
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(audio.get_sample_size(self.audio_format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(frames))

        return filename

    def transcribe_audio(self, audio_file_path: str) -> str:
        """
        Transcribe audio file to text using OpenAI Whisper API.

        Args:
            audio_file_path: Path to the audio file to transcribe

        Returns:
            Transcribed text
        """
        if not self.openai_client:
            raise ValueError("OpenAI API key is required for Whisper transcription")

        with open(audio_file_path, "rb") as audio_file:
            transcription = self.openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            return transcription.text

    def validate_voice_command(self, text: str, confidence: float) -> bool:
        """
        Validate a voice command based on text and confidence score.

        Args:
            text: The transcribed text
            confidence: Confidence score from speech-to-text processing

        Returns:
            True if the command is valid, False otherwise
        """
        # Check if text is not empty
        if not text.strip():
            self.logger.warning("Voice command text is empty")
            return False

        # Check if confidence is within valid range
        if not 0.0 <= confidence <= 1.0:
            self.logger.warning(f"Confidence score {confidence} is out of valid range [0.0, 1.0]")
            return False

        # Check if confidence is above minimum threshold (e.g., 0.5)
        if confidence < 0.5:
            self.logger.warning(f"Confidence score {confidence} is below minimum threshold")
            return False

        return True

    def process_voice_input(self, audio_file_path: str) -> VoiceCommand:
        """
        Process a voice input file through the complete pipeline.

        Args:
            audio_file_path: Path to the audio file

        Returns:
            VoiceCommand object with the processed command
        """
        try:
            # Transcribe the audio
            transcribed_text = self.transcribe_audio(audio_file_path)

            # For now, we'll use a placeholder confidence score
            # In a real implementation, this would come from the Whisper API
            confidence = 0.85  # Placeholder confidence

            # Validate the command
            if not self.validate_voice_command(transcribed_text, confidence):
                raise ValueError(f"Invalid voice command: {transcribed_text}")

            # Create and return the VoiceCommand object
            voice_command = VoiceCommand(
                id=f"vc_{int(datetime.now().timestamp())}",
                text=transcribed_text,
                timestamp=datetime.now(),
                confidence=confidence,
                intent="",  # Will be set later by LLM processing
                parameters={},  # Will be set later by LLM processing
                status=CommandStatus.PROCESSING
            )

            self.logger.info(f"Voice command processed: {voice_command.text}")
            return voice_command

        except Exception as e:
            self.logger.error(f"Error processing voice input: {str(e)}")
            raise

    def create_voice_command_from_text(self, text: str, confidence: float = 0.85) -> VoiceCommand:
        """
        Create a VoiceCommand object directly from text (for testing purposes).

        Args:
            text: The voice command text
            confidence: Confidence score (default 0.85)

        Returns:
            VoiceCommand object
        """
        if not self.validate_voice_command(text, confidence):
            raise ValueError(f"Invalid voice command: {text}")

        return VoiceCommand(
            id=f"vc_{int(datetime.now().timestamp())}",
            text=text,
            timestamp=datetime.now(),
            confidence=confidence,
            intent="",
            parameters={},
            status=CommandStatus.PENDING
        )


class VoiceIntentInterpreter:
    """
    Service for interpreting voice command intent using LLMs.
    """

    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the intent interpreter.

        Args:
            openai_api_key: OpenAI API key for LLM integration
        """
        self.logger = logging.getLogger(__name__)
        self.openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None

    def interpret_intent(self, voice_command: VoiceCommand) -> UserIntent:
        """
        Interpret the intent of a voice command using an LLM.

        Args:
            voice_command: The voice command to interpret

        Returns:
            UserIntent object with interpreted intent and parameters
        """
        if not self.openai_client:
            raise ValueError("OpenAI API key is required for intent interpretation")

        # Define the prompt for intent interpretation
        prompt = f"""
        Analyze the following voice command and extract the intent and parameters.
        Voice command: "{voice_command.text}"

        Provide the response in the following JSON format:
        {{
            "primary_intent": "the main action the user wants performed",
            "parameters": {{
                "key": "value"
            }},
            "confidence": 0.85
        }}

        The primary intent should be one of: "navigation", "manipulation", "detection", "status", "stop", or "other".
        For navigation: parameters should include "direction", "distance", "location"
        For manipulation: parameters should include "object", "action", "position"
        For detection: parameters should include "object_type", "location"
        """

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=200
            )

            # Parse the response
            response_text = response.choices[0].message.content.strip()

            # Extract JSON from response (in case the model includes additional text)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = response_text[json_start:json_end]
                parsed_response = json.loads(json_str)
            else:
                # If no JSON found, create a basic response
                parsed_response = {
                    "primary_intent": "other",
                    "parameters": {},
                    "confidence": 0.5
                }

            # Create and return the UserIntent object
            user_intent = UserIntent(
                id=f"ui_{int(datetime.now().timestamp())}",
                voice_command_id=voice_command.id,
                primary_intent=parsed_response.get("primary_intent", "other"),
                parameters=parsed_response.get("parameters", {}),
                confidence=parsed_response.get("confidence", 0.5),
                created_at=datetime.now()
            )

            self.logger.info(f"Intent interpreted: {user_intent.primary_intent}")
            return user_intent

        except Exception as e:
            self.logger.error(f"Error interpreting intent: {str(e)}")
            # Return a default intent in case of error
            return UserIntent(
                id=f"ui_{int(datetime.now().timestamp())}",
                voice_command_id=voice_command.id,
                primary_intent="other",
                parameters={},
                confidence=0.3,
                created_at=datetime.now()
            )


# Example usage and testing functions
def example_voice_processing():
    """
    Example function demonstrating voice command processing.
    """
    # This is a placeholder for testing purposes
    # In a real implementation, you would use actual audio files

    processor = VoiceCommandProcessor()

    # Example: Create a voice command from text (for testing)
    voice_cmd = processor.create_voice_command_from_text("Move forward 2 meters")
    print(f"Created voice command: {voice_cmd.text}")

    # Example: Interpret intent (requires OpenAI API key)
    # interpreter = VoiceIntentInterpreter(openai_api_key="your-api-key")
    # intent = interpreter.interpret_intent(voice_cmd)
    # print(f"Interpreted intent: {intent.primary_intent}")


if __name__ == "__main__":
    example_voice_processing()