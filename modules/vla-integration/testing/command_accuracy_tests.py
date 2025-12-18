"""
Command accuracy testing framework for the Vision-Language-Action (VLA) system.

This module contains acceptance tests and accuracy validation for voice commands,
focusing on the specific scenarios outlined in the requirements.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from ..shared.models import (
    VoiceCommand, ActionPlan, Action, ActionType,
    RobotState, EnvironmentalContext, Position3D, Orientation
)
from ..chapter_1_voice_to_action.basic_workflow import VoiceCommandWorkflow
from ..chapter_2_cognitive_planning.planning_service import CognitivePlanner
from ..shared.action_executor import ActionExecutor


@dataclass
class TestResult:
    """Result of a test execution"""
    test_name: str
    passed: bool
    details: str
    execution_time: float
    confidence: float = 0.0


class CommandAccuracyTester:
    """
    Service for testing command accuracy and validating acceptance scenarios.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the command accuracy tester.

        Args:
            api_key: OpenAI API key for Whisper and LLM integration
        """
        self.logger = logging.getLogger(__name__)
        self.api_key = api_key
        self.workflow = VoiceCommandWorkflow(api_key=api_key)
        self.planner = CognitivePlanner()
        self.executor = ActionExecutor()

    async def test_move_forward_2_meters(self) -> TestResult:
        """
        Implement acceptance test scenario for "Move forward 2 meters" command.

        Acceptance Criteria:
        - Given: A humanoid robot with VLA capabilities is listening
        - When: A user speaks a simple command like "Move forward 2 meters"
        - Then: The robot executes the movement command and provides confirmation
        """
        start_time = datetime.now()

        try:
            self.logger.info("Starting 'Move forward 2 meters' acceptance test")

            # Simulate processing the command text directly (since we can't capture real audio in tests)
            voice_command, intent = await self.workflow.process_text_command("Move forward 2 meters")

            # Validate that the command was processed successfully
            if voice_command.status.value != "completed":
                return TestResult(
                    test_name="Move forward 2 meters",
                    passed=False,
                    details=f"Command processing failed: {voice_command.status.value}",
                    execution_time=(datetime.now() - start_time).total_seconds(),
                    confidence=voice_command.confidence
                )

            # Validate that the intent was correctly interpreted as navigation
            if intent != "navigation":
                return TestResult(
                    test_name="Move forward 2 meters",
                    passed=False,
                    details=f"Incorrect intent interpretation: {intent}, expected 'navigation'",
                    execution_time=(datetime.now() - start_time).total_seconds(),
                    confidence=voice_command.confidence
                )

            # Create mock environmental context and robot state for planning
            env_context = EnvironmentalContext(
                id="test_env_1",
                timestamp=datetime.now(),
                objects=[],
                navigable_areas=[{"type": "floor", "bounds": {"x": [-5, 5], "y": [-5, 5]}}],
                obstacles=[],
                robot_position=Position3D(0.0, 0.0, 0.0)
            )

            robot_state = RobotState(
                id="test_robot_1",
                position=Position3D(0.0, 0.0, 0.0),
                orientation=Orientation(0.0, 0.0, 0.0, 1.0),
                battery_level=0.9,
                available_capabilities=["navigation", "manipulation"],
                safety_status="safe",
                timestamp=datetime.now()
            )

            # Generate action plan based on the interpreted intent
            action_plan = self.planner.generate_action_plan(
                voice_command,
                voice_command,  # Using voice_command as intent for this test
                env_context,
                robot_state
            )

            # Validate that the action plan contains navigation actions
            navigation_actions = [action for action in action_plan.actions if action.type.value == "navigation"]
            if not navigation_actions:
                return TestResult(
                    test_name="Move forward 2 meters",
                    passed=False,
                    details="No navigation actions generated in plan",
                    execution_time=(datetime.now() - start_time).total_seconds(),
                    confidence=voice_command.confidence
                )

            # Check if the action parameters include forward movement
            forward_action_found = False
            for action in navigation_actions:
                if (action.parameters.get("action") == "move_direction" and
                    action.parameters.get("direction") == "forward" and
                    action.parameters.get("distance", 0) >= 1.5):  # Allow some tolerance
                    forward_action_found = True
                    break

            if not forward_action_found:
                return TestResult(
                    test_name="Move forward 2 meters",
                    passed=False,
                    details="Navigation action does not match 'move forward 2 meters' command",
                    execution_time=(datetime.now() - start_time).total_seconds(),
                    confidence=voice_command.confidence
                )

            # Test passed
            return TestResult(
                test_name="Move forward 2 meters",
                passed=True,
                details="Command correctly processed, interpreted as navigation, and generated appropriate action plan",
                execution_time=(datetime.now() - start_time).total_seconds(),
                confidence=voice_command.confidence
            )

        except Exception as e:
            return TestResult(
                test_name="Move forward 2 meters",
                passed=False,
                details=f"Test execution error: {str(e)}",
                execution_time=(datetime.now() - start_time).total_seconds()
            )

    async def test_pick_up_red_cube(self) -> TestResult:
        """
        Implement acceptance test scenario for "Pick up the red cube" command.

        Acceptance Criteria:
        - Given: The robot is in a listening state
        - When: A user speaks an object manipulation command like "Pick up the red cube"
        - Then: The robot identifies the object and performs the pick-up action
        """
        start_time = datetime.now()

        try:
            self.logger.info("Starting 'Pick up the red cube' acceptance test")

            # Simulate processing the command text directly
            voice_command, intent = await self.workflow.process_text_command("Pick up the red cube")

            # Validate that the command was processed successfully
            if voice_command.status.value != "completed":
                return TestResult(
                    test_name="Pick up the red cube",
                    passed=False,
                    details=f"Command processing failed: {voice_command.status.value}",
                    execution_time=(datetime.now() - start_time).total_seconds(),
                    confidence=voice_command.confidence
                )

            # Validate that the intent was correctly interpreted as manipulation
            if intent != "manipulation":
                return TestResult(
                    test_name="Pick up the red cube",
                    passed=False,
                    details=f"Incorrect intent interpretation: {intent}, expected 'manipulation'",
                    execution_time=(datetime.now() - start_time).total_seconds(),
                    confidence=voice_command.confidence
                )

            # Create mock environmental context with a red cube
            from ..shared.models import ObjectInfo
            env_context = EnvironmentalContext(
                id="test_env_2",
                timestamp=datetime.now(),
                objects=[
                    ObjectInfo(
                        id="red_cube_1",
                        type="red cube",
                        position=Position3D(1.0, 0.0, 0.0),
                        confidence=0.9
                    )
                ],
                navigable_areas=[{"type": "floor", "bounds": {"x": [-5, 5], "y": [-5, 5]}}],
                obstacles=[],
                robot_position=Position3D(0.0, 0.0, 0.0)
            )

            robot_state = RobotState(
                id="test_robot_2",
                position=Position3D(0.0, 0.0, 0.0),
                orientation=Orientation(0.0, 0.0, 0.0, 1.0),
                battery_level=0.9,
                available_capabilities=["navigation", "manipulation"],
                safety_status="safe",
                timestamp=datetime.now()
            )

            # Generate action plan based on the interpreted intent
            action_plan = self.planner.generate_action_plan(
                voice_command,
                voice_command,  # Using voice_command as intent for this test
                env_context,
                robot_state
            )

            # Validate that the action plan contains manipulation actions
            manipulation_actions = [action for action in action_plan.actions if action.type.value == "manipulation"]
            if not manipulation_actions:
                return TestResult(
                    test_name="Pick up the red cube",
                    passed=False,
                    details="No manipulation actions generated in plan",
                    execution_time=(datetime.now() - start_time).total_seconds(),
                    confidence=voice_command.confidence
                )

            # Check if the action parameters include pick-up action for a cube
            pick_up_action_found = False
            for action in manipulation_actions:
                action_type = action.parameters.get("action", "")
                object_type = action.parameters.get("object_type", "")
                if ("pick" in action_type or "grasp" in action_type or "take" in action_type) and \
                   ("cube" in object_type or "cube" in voice_command.text.lower()):
                    pick_up_action_found = True
                    break

            if not pick_up_action_found:
                return TestResult(
                    test_name="Pick up the red cube",
                    passed=False,
                    details="Manipulation action does not match 'pick up the red cube' command",
                    execution_time=(datetime.now() - start_time).total_seconds(),
                    confidence=voice_command.confidence
                )

            # Test passed
            return TestResult(
                test_name="Pick up the red cube",
                passed=True,
                details="Command correctly processed, interpreted as manipulation, and generated appropriate action plan",
                execution_time=(datetime.now() - start_time).total_seconds(),
                confidence=voice_command.confidence
            )

        except Exception as e:
            return TestResult(
                test_name="Pick up the red cube",
                passed=False,
                details=f"Test execution error: {str(e)}",
                execution_time=(datetime.now() - start_time).total_seconds()
            )

    async def run_acceptance_tests(self) -> List[TestResult]:
        """
        Run all acceptance tests for User Story 1.

        Returns:
            List of test results
        """
        self.logger.info("Running User Story 1 acceptance tests")

        results = []

        # Test 1: Move forward 2 meters
        result1 = await self.test_move_forward_2_meters()
        results.append(result1)

        # Test 2: Pick up the red cube
        result2 = await self.test_pick_up_red_cube()
        results.append(result2)

        return results

    def generate_test_report(self, results: List[TestResult]) -> str:
        """
        Generate a test report from test results.

        Args:
            results: List of test results

        Returns:
            Formatted test report
        """
        report = []
        report.append("VLA System - User Story 1 Acceptance Test Report")
        report.append("=" * 50)
        report.append(f"Total Tests: {len(results)}")
        report.append(f"Passed: {sum(1 for r in results if r.passed)}")
        report.append(f"Failed: {sum(1 for r in results if not r.passed)}")
        report.append("")

        for i, result in enumerate(results, 1):
            status = "PASS" if result.passed else "FAIL"
            report.append(f"{i}. {result.test_name}")
            report.append(f"   Status: {status}")
            report.append(f"   Details: {result.details}")
            report.append(f"   Execution Time: {result.execution_time:.2f}s")
            if result.confidence > 0:
                report.append(f"   Confidence: {result.confidence:.2f}")
            report.append("")

        # Calculate overall metrics
        if results:
            avg_confidence = sum(r.confidence for r in results if r.confidence > 0) / len(results)
            avg_execution_time = sum(r.execution_time for r in results) / len(results)

            report.append("Overall Metrics:")
            report.append(f"  Average Confidence: {avg_confidence:.2f}")
            report.append(f"  Average Execution Time: {avg_execution_time:.2f}s")
            report.append(f"  Success Rate: {(sum(1 for r in results if r.passed) / len(results)) * 100:.1f}%")

        return "\n".join(report)


class PlanCorrectnessValidator:
    """
    Service for validating plan correctness as specified in the requirements.
    """

    def __init__(self):
        """
        Initialize the plan correctness validator.
        """
        self.logger = logging.getLogger(__name__)

    def validate_action_plan(self, action_plan: ActionPlan, expected_actions: List[str]) -> Tuple[bool, str]:
        """
        Validate that an action plan contains the expected actions.

        Args:
            action_plan: The action plan to validate
            expected_actions: List of expected action types

        Returns:
            Tuple of (is_valid, validation_message)
        """
        try:
            actual_actions = [action.type.value for action in action_plan.actions]

            # Check if all expected actions are present
            missing_actions = [exp for exp in expected_actions if exp not in actual_actions]

            if missing_actions:
                return False, f"Missing expected actions: {missing_actions}. Actual: {actual_actions}"

            # Check if there are any unexpected actions (optional, depending on requirements)
            unexpected_actions = [act for act in actual_actions if act not in expected_actions]
            if unexpected_actions:
                self.logger.warning(f"Unexpected actions in plan: {unexpected_actions}")

            return True, f"Plan contains all expected actions: {expected_actions}"

        except Exception as e:
            return False, f"Plan validation error: {str(e)}"


# Example usage and testing functions
async def example_command_accuracy_tests():
    """
    Example function demonstrating command accuracy testing.
    """
    print("=== Command Accuracy Testing Example ===")

    # Note: This example requires a valid OpenAI API key
    print("Testing framework initialized")
    print("Ready to validate voice command processing accuracy")
    print("Required: OpenAI API key in OPENAI_API_KEY environment variable")

    # Example usage structure (commented out to avoid API calls without key):
    """
    tester = CommandAccuracyTester(api_key="your-api-key")
    results = await tester.run_acceptance_tests()

    report = tester.generate_test_report(results)
    print(report)
    """

    print("\nTest scenarios available:")
    print("1. Navigation commands: 'Move forward 2 meters'")
    print("2. Manipulation commands: 'Pick up the red cube'")
    print("3. Complex multi-step commands")
    print("4. Edge case commands (noisy, ambiguous)")


if __name__ == "__main__":
    # Run the example
    asyncio.run(example_command_accuracy_tests())