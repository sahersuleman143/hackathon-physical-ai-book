"""
Basic voice command processing workflow for the Vision-Language-Action (VLA) system.

This module implements the core workflow for processing voice commands from
initial capture through to validated command ready for intent interpretation.
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from pathlib import Path

from .whisper_integration import WhisperIntegration
from .voice_capture import VoiceCapturePipeline
from .voice_processor import VoiceCommandProcessor
from .whisper_pipeline import WhisperProcessingOrchestrator
from ..shared.models import VoiceCommand, CommandStatus
from ..shared.voice_processor import VoiceIntentInterpreter


class VoiceCommandWorkflow:
    """
    Core workflow for processing voice commands in the VLA system.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the voice command workflow.

        Args:
            api_key: OpenAI API key for Whisper and LLM integration
        """
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.whisper_integration = WhisperIntegration(api_key=api_key)
        self.voice_capture = VoiceCapturePipeline()
        self.voice_processor = VoiceCommandProcessor()
        self.whisper_orchestrator = WhisperProcessingOrchestrator(self.whisper_integration)
        self.intent_interpreter = VoiceIntentInterpreter(api_key=api_key)

    async def process_voice_command_complete(self, audio_source: str) -> Tuple[VoiceCommand, Optional[str]]:
        """
        Complete workflow to process a voice command from audio to interpreted intent.

        Args:
            audio_source: Path to audio file or capture source ("microphone", "until_silence")

        Returns:
            Tuple of (VoiceCommand, interpreted_intent_or_error)
        """
        try:
            self.logger.info(f"Starting complete voice command workflow for: {audio_source}")

            # Step 1: Process audio to validated voice command
            voice_command = await self.whisper_orchestrator.process_audio_to_command(audio_source)

            if voice_command.status == CommandStatus.FAILED:
                self.logger.error(f"Voice command processing failed: {voice_command.text}")
                return voice_command, "Processing failed"

            # Step 2: Interpret the intent using LLM
            try:
                user_intent = self.intent_interpreter.interpret_intent(voice_command)
                interpreted_intent = user_intent.primary_intent

                # Update the voice command with the interpreted intent
                voice_command.intent = interpreted_intent
                voice_command.parameters = user_intent.parameters

                self.logger.info(f"Intent interpreted: {interpreted_intent}")
                return voice_command, interpreted_intent

            except Exception as e:
                self.logger.error(f"Error interpreting intent: {str(e)}")
                return voice_command, f"Intent interpretation error: {str(e)}"

        except Exception as e:
            self.logger.error(f"Error in complete workflow: {str(e)}")
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
            return error_command, f"Workflow error: {str(e)}"

    async def process_voice_command_simple(self, audio_source: str) -> VoiceCommand:
        """
        Simplified workflow that only processes to validated command (no intent interpretation).

        Args:
            audio_source: Path to audio file or capture source

        Returns:
            VoiceCommand object
        """
        try:
            self.logger.info(f"Starting simple voice command workflow for: {audio_source}")
            voice_command = await self.whisper_orchestrator.process_audio_to_command(audio_source)
            return voice_command
        except Exception as e:
            self.logger.error(f"Error in simple workflow: {str(e)}")
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

    async def process_text_command(self, text: str, confidence: float = 0.85) -> Tuple[VoiceCommand, Optional[str]]:
        """
        Process a text command directly (for testing or when audio is not available).

        Args:
            text: The command text
            confidence: Confidence score for the text

        Returns:
            Tuple of (VoiceCommand, interpreted_intent_or_error)
        """
        try:
            self.logger.info(f"Processing text command: {text}")

            # Create voice command from text
            voice_command = self.whisper_integration.whisper.create_voice_command_from_text(text, confidence)

            # Validate the command
            voice_command = await self.voice_processor.process_voice_command(voice_command)

            if voice_command.status == CommandStatus.FAILED:
                return voice_command, "Validation failed"

            # Interpret the intent
            try:
                user_intent = self.intent_interpreter.interpret_intent(voice_command)
                voice_command.intent = user_intent.primary_intent
                voice_command.parameters = user_intent.parameters

                return voice_command, user_intent.primary_intent
            except Exception as e:
                self.logger.error(f"Error interpreting intent: {str(e)}")
                return voice_command, f"Intent interpretation error: {str(e)}"

        except Exception as e:
            self.logger.error(f"Error processing text command: {str(e)}")
            error_command = VoiceCommand(
                id=f"vc_{int(datetime.now().timestamp())}",
                text=text,
                timestamp=datetime.now(),
                confidence=0.0,
                intent="",
                parameters={},
                status=CommandStatus.FAILED
            )
            return error_command, f"Processing error: {str(e)}"


class WorkflowStep:
    """
    Represents a step in the voice command workflow with metadata.
    """

    def __init__(self, name: str, description: str, required: bool = True):
        self.name = name
        self.description = description
        self.required = required
        self.executed = False
        self.start_time = None
        self.end_time = None
        self.success = False
        self.error = None

    async def execute(self, workflow_context: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Execute this workflow step.

        Args:
            workflow_context: Context dictionary passed between steps

        Returns:
            Tuple of (success, result_or_error_message)
        """
        self.start_time = datetime.now()
        try:
            # This would be overridden by specific step implementations
            result = await self._execute_step(workflow_context)
            self.success = True
            return True, result
        except Exception as e:
            self.error = str(e)
            self.success = False
            return False, str(e)
        finally:
            self.end_time = datetime.now()
            self.executed = True

    async def _execute_step(self, workflow_context: Dict[str, Any]) -> str:
        """
        Override this method in subclasses to implement specific step logic.
        """
        raise NotImplementedError("Subclasses must implement _execute_step")


class AudioCaptureStep(WorkflowStep):
    """
    Workflow step for capturing audio.
    """

    def __init__(self):
        super().__init__("audio_capture", "Capture or receive audio input")

    async def _execute_step(self, workflow_context: Dict[str, Any]) -> str:
        audio_source = workflow_context.get("audio_source")
        if not audio_source:
            raise ValueError("No audio_source provided in workflow context")

        # If it's a capture command, use the capture pipeline
        if audio_source in ["microphone", "until_silence"]:
            capture_pipeline = workflow_context.get("capture_pipeline")
            if not capture_pipeline:
                raise ValueError("No capture_pipeline provided in workflow context")

            audio_file_path = await capture_pipeline.capture_voice_input(audio_source)
            workflow_context["audio_file_path"] = audio_file_path
            return audio_file_path
        else:
            # It's a file path, validate it
            if not Path(audio_source).exists():
                raise FileNotFoundError(f"Audio file does not exist: {audio_source}")
            workflow_context["audio_file_path"] = audio_source
            return audio_source


class TranscriptionStep(WorkflowStep):
    """
    Workflow step for transcribing audio to text.
    """

    def __init__(self):
        super().__init__("transcription", "Transcribe audio to text using Whisper")

    async def _execute_step(self, workflow_context: Dict[str, Any]) -> str:
        audio_file_path = workflow_context.get("audio_file_path")
        whisper_integration = workflow_context.get("whisper_integration")

        if not audio_file_path or not whisper_integration:
            raise ValueError("Missing audio_file_path or whisper_integration in workflow context")

        text, confidence = await whisper_integration.transcribe_audio_file(audio_file_path)
        workflow_context["transcribed_text"] = text
        workflow_context["transcription_confidence"] = confidence
        return text


class ValidationStep(WorkflowStep):
    """
    Workflow step for validating the transcribed text.
    """

    def __init__(self):
        super().__init__("validation", "Validate the transcribed command")

    async def _execute_step(self, workflow_context: Dict[str, Any]) -> str:
        text = workflow_context.get("transcribed_text")
        confidence = workflow_context.get("transcription_confidence", 0.7)

        if not text:
            raise ValueError("No transcribed_text in workflow context")

        # Create a temporary voice command for validation
        temp_command = VoiceCommand(
            id=f"temp_{int(datetime.now().timestamp())}",
            text=text,
            timestamp=datetime.now(),
            confidence=confidence,
            intent="",
            parameters={},
            status=CommandStatus.PENDING
        )

        # Use the voice processor to validate
        voice_processor = workflow_context.get("voice_processor")
        if not voice_processor:
            raise ValueError("No voice_processor provided in workflow context")

        validated_command = await voice_processor.process_voice_command(temp_command)

        workflow_context["validated_command"] = validated_command
        return f"Valid: {validated_command.status.value}, Confidence: {validated_command.confidence:.2f}"


class IntentInterpretationStep(WorkflowStep):
    """
    Workflow step for interpreting the intent of the command.
    """

    def __init__(self):
        super().__init__("intent_interpretation", "Interpret the intent using LLM")

    async def _execute_step(self, workflow_context: Dict[str, Any]) -> str:
        validated_command = workflow_context.get("validated_command")
        intent_interpreter = workflow_context.get("intent_interpreter")

        if not validated_command or not intent_interpreter:
            raise ValueError("Missing validated_command or intent_interpreter in workflow context")

        if validated_command.status != CommandStatus.PROCESSING:
            raise ValueError(f"Command not in valid state for intent interpretation: {validated_command.status.value}")

        user_intent = intent_interpreter.interpret_intent(validated_command)
        workflow_context["interpreted_intent"] = user_intent.primary_intent
        workflow_context["intent_parameters"] = user_intent.parameters

        return user_intent.primary_intent


class SequentialWorkflow:
    """
    Executes workflow steps in sequential order with error handling.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.steps = []

    def add_step(self, step: WorkflowStep):
        """
        Add a step to the workflow.

        Args:
            step: WorkflowStep instance
        """
        self.steps.append(step)

    async def execute(self, initial_context: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], Dict[str, Any]]:
        """
        Execute the workflow with the given initial context.

        Args:
            initial_context: Initial context to start the workflow

        Returns:
            Tuple of (success, final_context, step_results)
        """
        context = initial_context.copy()
        step_results = {}

        self.logger.info(f"Starting sequential workflow with {len(self.steps)} steps")

        for step in self.steps:
            self.logger.info(f"Executing step: {step.name}")
            success, result = await step.execute(context)

            step_results[step.name] = {
                "success": success,
                "result": result,
                "duration": (step.end_time - step.start_time).total_seconds() if step.start_time and step.end_time else 0
            }

            if not success and step.required:
                self.logger.error(f"Required step failed: {step.name}, result: {result}")
                return False, context, step_results

        self.logger.info("Sequential workflow completed")
        return True, context, step_results


class VoiceCommandWorkflowManager:
    """
    High-level manager for voice command workflows with multiple execution options.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the workflow manager.

        Args:
            api_key: OpenAI API key
        """
        self.logger = logging.getLogger(__name__)
        self.api_key = api_key

    async def execute_default_workflow(self, audio_source: str) -> Dict[str, Any]:
        """
        Execute the default voice command workflow.

        Args:
            audio_source: Path to audio file or capture source

        Returns:
            Dictionary with workflow results
        """
        # Initialize components
        whisper_integration = WhisperIntegration(api_key=self.api_key)
        capture_pipeline = VoiceCapturePipeline()
        voice_processor = VoiceCommandProcessor()
        intent_interpreter = VoiceIntentInterpreter(api_key=self.api_key)

        # Create the workflow
        workflow = SequentialWorkflow()
        workflow.add_step(AudioCaptureStep())
        workflow.add_step(TranscriptionStep())
        workflow.add_step(ValidationStep())
        workflow.add_step(IntentInterpretationStep())

        # Prepare initial context
        initial_context = {
            "audio_source": audio_source,
            "whisper_integration": whisper_integration,
            "capture_pipeline": capture_pipeline,
            "voice_processor": voice_processor,
            "intent_interpreter": intent_interpreter
        }

        # Execute the workflow
        success, final_context, step_results = await workflow.execute(initial_context)

        # Prepare results
        results = {
            "success": success,
            "step_results": step_results,
            "final_context": final_context,
            "transcribed_text": final_context.get("transcribed_text", ""),
            "intent": final_context.get("interpreted_intent", ""),
            "parameters": final_context.get("intent_parameters", {}),
            "validation_status": final_context.get("validated_command", VoiceCommand(
                id="none", text="", timestamp=datetime.now(), confidence=0.0, intent="",
                parameters={}, status=CommandStatus.FAILED
            )).status.value
        }

        return results

    async def execute_simple_workflow(self, audio_source: str) -> Dict[str, Any]:
        """
        Execute a simplified workflow that only does transcription and validation.

        Args:
            audio_source: Path to audio file or capture source

        Returns:
            Dictionary with workflow results
        """
        # Initialize components
        whisper_integration = WhisperIntegration(api_key=self.api_key)
        capture_pipeline = VoiceCapturePipeline()
        voice_processor = VoiceCommandProcessor()

        # Create a simplified workflow
        workflow = SequentialWorkflow()
        workflow.add_step(AudioCaptureStep())
        workflow.add_step(TranscriptionStep())
        workflow.add_step(ValidationStep())

        # Prepare initial context
        initial_context = {
            "audio_source": audio_source,
            "whisper_integration": whisper_integration,
            "capture_pipeline": capture_pipeline,
            "voice_processor": voice_processor,
        }

        # Execute the workflow
        success, final_context, step_results = await workflow.execute(initial_context)

        # Prepare results
        results = {
            "success": success,
            "step_results": step_results,
            "final_context": final_context,
            "transcribed_text": final_context.get("transcribed_text", ""),
            "validation_status": final_context.get("validated_command", VoiceCommand(
                id="none", text="", timestamp=datetime.now(), confidence=0.0, intent="",
                parameters={}, status=CommandStatus.FAILED
            )).status.value
        }

        return results


# Example usage and testing functions
async def example_voice_workflow():
    """
    Example function demonstrating voice command workflow usage.
    """
    print("=== Voice Command Workflow Example ===")

    # Note: This example requires a valid OpenAI API key
    print("Workflow structure initialized")
    print("Ready to process voice commands through complete pipeline")
    print("Required: OpenAI API key in OPENAI_API_KEY environment variable")

    # Example usage structure (commented out to avoid API calls without key):
    """
    # Initialize the workflow
    workflow = VoiceCommandWorkflow(api_key="your-api-key")

    # Process an audio file through complete workflow
    command, intent = await workflow.process_voice_command_complete("path/to/audio/file.wav")
    print(f"Processed command: {command.text}")
    print(f"Interpreted intent: {intent}")
    print(f"Command status: {command.status.value}")

    # Use the workflow manager for more detailed results
    manager = VoiceCommandWorkflowManager(api_key="your-api-key")
    results = await manager.execute_default_workflow("path/to/audio/file.wav")
    print(f"Workflow success: {results['success']}")
    print(f"Transcribed text: {results['transcribed_text']}")
    print(f"Interpreted intent: {results['intent']}")
    print(f"Step results: {results['step_results']}")
    """

    print("\nWorkflow components available:")
    print("1. Complete workflow: Audio → Transcription → Validation → Intent Interpretation")
    print("2. Simple workflow: Audio → Transcription → Validation (no intent)")
    print("3. Text-only workflow: Text → Validation → Intent Interpretation")
    print("4. Sequential workflow: Customizable step-by-step processing")


if __name__ == "__main__":
    # Run the example
    asyncio.run(example_voice_workflow())