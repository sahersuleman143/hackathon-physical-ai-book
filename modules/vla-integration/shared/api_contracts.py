"""
API contract definitions for the Vision-Language-Action (VLA) integration system.

This module defines the API contracts for voice processing, planning, execution,
and status endpoints based on the VLA system contracts.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

from .models import (
    VoiceCommand, ActionPlan, ExecutionResult,
    RobotState, EnvironmentalContext, UserIntent
)


class APIResponseCode(Enum):
    """API response codes for the VLA system"""
    SUCCESS = 200
    CREATED = 201
    ACCEPTED = 202
    BAD_REQUEST = 400
    UNPROCESSABLE_ENTITY = 422
    INTERNAL_ERROR = 500


@dataclass
class APIResponse:
    """Base API response structure"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None


# Voice Command Processing API Contracts

@dataclass
class VoiceCommandRequest:
    """
    Request structure for processing a voice command.

    Fields:
    - audio_data: Base64 encoded audio data
    - user_id: Optional user identifier
    - context: Optional environmental and robot context
    """
    audio_data: str
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


@dataclass
class VoiceCommandResponse:
    """
    Response structure for voice command processing.

    Fields:
    - command_id: Unique identifier for the command
    - transcript: Transcribed text from audio
    - confidence: Confidence score from speech-to-text
    - intent: Interpreted intent from LLM processing
    - action_plan: Generated action plan if successful
    """
    command_id: str
    transcript: str
    confidence: float
    intent: str
    action_plan: Optional[ActionPlan] = None


# Action Planning API Contracts

@dataclass
class ActionPlanRequest:
    """
    Request structure for generating an action plan.

    Fields:
    - command_text: Text command to generate plan for
    - environmental_context: Current environmental context
    - robot_capabilities: List of available robot capabilities
    """
    command_text: str
    environmental_context: EnvironmentalContext
    robot_capabilities: List[str]


@dataclass
class ActionPlanResponse:
    """
    Response structure for action plan generation.

    Fields:
    - plan_id: Unique identifier for the action plan
    - actions: List of generated actions
    - estimated_duration: Estimated time to complete in seconds
    - confidence: Confidence in the generated plan
    """
    plan_id: str
    actions: List[Dict[str, Any]]  # Using dict since Action contains complex types
    estimated_duration: float
    confidence: float


# Execution API Contracts

@dataclass
class ExecutionRequest:
    """
    Request structure for executing an action plan.

    Fields:
    - plan_id: ID of the action plan to execute
    - actions: List of actions to execute (optional override)
    """
    plan_id: str
    actions: Optional[List[Dict[str, Any]]] = None


@dataclass
class ExecutionResponse:
    """
    Response structure for action plan execution.

    Fields:
    - execution_id: Unique identifier for the execution
    - status: Current execution status
    - results: Results of executed actions
    """
    execution_id: str
    status: str
    results: List[Dict[str, Any]]  # Using dict since ActionResult contains complex types


# Status API Contracts

@dataclass
class StatusResponse:
    """
    Response structure for robot status.

    Fields:
    - robot_state: Current robot state
    - environmental_context: Current environmental context
    """
    robot_state: RobotState
    environmental_context: EnvironmentalContext


# Error Response Contract

@dataclass
class ErrorResponse:
    """
    Standard error response structure.

    Fields:
    - error_code: Machine-readable error code
    - message: Human-readable error message
    - details: Optional detailed error information
    """
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None


# API Path Definitions
class APIPaths:
    """Path definitions for the VLA system API"""
    VOICE_COMMANDS = "/voice/commands"
    PLANNING_GENERATE = "/planning/generate"
    EXECUTION_EXECUTE = "/execution/execute"
    STATUS_ROBOT = "/status/robot"
    HEALTH_CHECK = "/health"


# API Contract Validation Functions

def validate_voice_command_request(request: VoiceCommandRequest) -> List[str]:
    """
    Validate a voice command request.

    Args:
        request: The request to validate

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Check if audio_data is provided and is valid base64
    if not request.audio_data:
        errors.append("audio_data is required")

    # Check if audio_data is properly formatted (basic check)
    if request.audio_data and not isinstance(request.audio_data, str):
        errors.append("audio_data must be a string")

    return errors


def validate_action_plan_request(request: ActionPlanRequest) -> List[str]:
    """
    Validate an action plan request.

    Args:
        request: The request to validate

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Check if command_text is provided and not empty
    if not request.command_text or not request.command_text.strip():
        errors.append("command_text is required and cannot be empty")

    # Check if robot_capabilities is provided
    if not request.robot_capabilities:
        errors.append("robot_capabilities is required")

    return errors


def validate_execution_request(request: ExecutionRequest) -> List[str]:
    """
    Validate an execution request.

    Args:
        request: The request to validate

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Check if plan_id is provided and not empty
    if not request.plan_id or not request.plan_id.strip():
        errors.append("plan_id is required and cannot be empty")

    return errors


# Example API Usage Patterns

def example_voice_command_flow():
    """
    Example of how the API contracts would be used in practice.
    """
    print("=== VLA API Contract Example ===")

    # Example voice command request
    voice_request = VoiceCommandRequest(
        audio_data="base64_encoded_audio_data_here",
        user_id="user_123",
        context={
            "environmental_context": "env_context_object",
            "robot_state": "robot_state_object"
        }
    )

    # Validate the request
    validation_errors = validate_voice_command_request(voice_request)
    if validation_errors:
        print(f"Validation errors: {validation_errors}")
        return

    # Example response (in a real implementation, this would come from processing)
    response = VoiceCommandResponse(
        command_id="vc_12345",
        transcript="Move forward 2 meters",
        confidence=0.92,
        intent="navigation"
    )

    print(f"Processed command: {response.transcript}")
    print(f"Confidence: {response.confidence}")
    print(f"Intent: {response.intent}")


def example_action_planning_flow():
    """
    Example of action planning API flow.
    """
    print("\n=== Action Planning Example ===")

    # Example environmental context (simplified)
    env_context = EnvironmentalContext(
        id="env_123",
        timestamp=datetime.now(),
        objects=[],
        navigable_areas=[],
        obstacles=[],
        robot_position=None  # Will be set in real implementation
    )

    # Example planning request
    plan_request = ActionPlanRequest(
        command_text="Go to the kitchen and pick up the red cup",
        environmental_context=env_context,
        robot_capabilities=["navigation", "manipulation"]
    )

    # Validate the request
    validation_errors = validate_action_plan_request(plan_request)
    if validation_errors:
        print(f"Validation errors: {validation_errors}")
        return

    print(f"Planning for command: {plan_request.command_text}")
    print(f"Robot capabilities: {plan_request.robot_capabilities}")


if __name__ == "__main__":
    example_voice_command_flow()
    example_action_planning_flow()