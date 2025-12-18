"""
Action execution service for the Vision-Language-Action (VLA) integration system.

This module handles the execution of action plans on the robot, including
navigation, manipulation, and detection tasks, with safety protocol enforcement.
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from .models import (
    Action, ActionType, ActionPlan, CommandStatus,
    ActionResult, ExecutionResult, RobotState, EnvironmentalContext
)


@dataclass
class ExecutionConfig:
    """Configuration for action execution"""
    safety_check_interval: float = 1.0  # seconds
    max_execution_time: float = 300.0    # seconds (5 minutes)
    enable_safety_protocols: bool = True


class ActionExecutor:
    """
    Service for executing action plans on the robot.
    """

    def __init__(self, config: Optional[ExecutionConfig] = None):
        """
        Initialize the action executor.

        Args:
            config: Execution configuration
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or ExecutionConfig()

    async def execute_action_plan(self, action_plan: ActionPlan) -> ExecutionResult:
        """
        Execute an action plan on the robot.

        Args:
            action_plan: The action plan to execute

        Returns:
            ExecutionResult object with the execution results
        """
        try:
            self.logger.info(f"Starting execution of action plan {action_plan.id}")

            # Update plan status to executing
            action_plan.status = CommandStatus.PROCESSING

            start_time = datetime.now()
            results = []

            # Execute each action in the plan
            for i, action in enumerate(action_plan.actions):
                # Check for dependencies before executing
                if action.dependencies:
                    # In a real implementation, we'd check if dependencies completed successfully
                    pass

                # Execute the action
                result = await self._execute_single_action(action, i)
                results.append(result)

                # Check safety protocols between actions
                if self.config.enable_safety_protocols:
                    await self._check_safety_protocols()

            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()

            # Determine overall status
            successful_actions = sum(1 for r in results if r.status == "success")
            overall_status = "success" if successful_actions == len(results) else \
                           "partial" if successful_actions > 0 else "failure"

            # Create execution result
            execution_result = ExecutionResult(
                id=f"er_{int(datetime.now().timestamp())}",
                action_plan_id=action_plan.id,
                results=results,
                overall_status=overall_status,
                execution_time=execution_time,
                timestamp=datetime.now()
            )

            self.logger.info(f"Action plan execution completed with status: {overall_status}")
            return execution_result

        except Exception as e:
            self.logger.error(f"Error executing action plan: {str(e)}")
            raise

    async def _execute_single_action(self, action: Action, action_index: int) -> ActionResult:
        """
        Execute a single action.

        Args:
            action: The action to execute
            action_index: Index of the action in the plan

        Returns:
            ActionResult object with the result of the action
        """
        start_time = datetime.now()
        action_id = f"action_{action_index}"

        try:
            self.logger.info(f"Executing action {action_index}: {action.type.value}")

            # Execute action based on type
            if action.type == ActionType.NAVIGATION:
                result = await self._execute_navigation_action(action)
            elif action.type == ActionType.MANIPULATION:
                result = await self._execute_manipulation_action(action)
            elif action.type == ActionType.DETECTION:
                result = await self._execute_detection_action(action)
            else:
                result = ActionResult(
                    action_id=action_id,
                    status="failed",
                    details=f"Unknown action type: {action.type.value}",
                    duration=0.0
                )

            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            result.duration = duration

            self.logger.info(f"Action {action_index} completed with status: {result.status}")
            return result

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            error_result = ActionResult(
                action_id=action_id,
                status="failed",
                details=f"Error executing action: {str(e)}",
                duration=duration
            )
            self.logger.error(f"Action {action_index} failed: {str(e)}")
            return error_result

    async def _execute_navigation_action(self, action: Action) -> ActionResult:
        """
        Execute a navigation action.

        Args:
            action: The navigation action to execute

        Returns:
            ActionResult object
        """
        try:
            action_params = action.parameters
            action_type = action_params.get("action", "unknown")

            if action_type == "navigate_to":
                # Navigate to a specific location
                target_location = action_params.get("target_location", "unknown")
                self.logger.info(f"Navigating to location: {target_location}")
                # Simulate navigation
                await asyncio.sleep(2.0)  # Simulate time for navigation

                return ActionResult(
                    action_id="navigation_action",
                    status="success",
                    details=f"Navigated to {target_location}",
                    duration=2.0
                )

            elif action_type == "move_direction":
                # Move in a specific direction
                direction = action_params.get("direction", "forward")
                distance = action_params.get("distance", 1.0)
                self.logger.info(f"Moving {direction} for {distance} meters")
                # Simulate movement
                await asyncio.sleep(1.5)  # Simulate time for movement

                return ActionResult(
                    action_id="navigation_action",
                    status="success",
                    details=f"Moved {direction} for {distance}m",
                    duration=1.5
                )

            elif action_type == "move_toward":
                # Move toward a direction
                direction = action_params.get("direction", "forward")
                self.logger.info(f"Moving toward {direction}")
                # Simulate movement
                await asyncio.sleep(1.0)  # Simulate time for movement

                return ActionResult(
                    action_id="navigation_action",
                    status="success",
                    details=f"Moved toward {direction}",
                    duration=1.0
                )

            elif action_type == "move_forward":
                # Move forward a default distance
                distance = action_params.get("distance", 1.0)
                self.logger.info(f"Moving forward {distance} meters")
                # Simulate movement
                await asyncio.sleep(1.0)  # Simulate time for movement

                return ActionResult(
                    action_id="navigation_action",
                    status="success",
                    details=f"Moved forward {distance}m",
                    duration=1.0
                )

            elif action_type == "stop":
                # Stop the robot
                self.logger.info("Stopping robot")
                # Simulate stop command
                await asyncio.sleep(0.5)

                return ActionResult(
                    action_id="navigation_action",
                    status="success",
                    details="Robot stopped",
                    duration=0.5
                )

            else:
                return ActionResult(
                    action_id="navigation_action",
                    status="failed",
                    details=f"Unknown navigation action: {action_type}",
                    duration=0.0
                )

        except Exception as e:
            return ActionResult(
                action_id="navigation_action",
                status="failed",
                details=f"Navigation error: {str(e)}",
                duration=0.0
            )

    async def _execute_manipulation_action(self, action: Action) -> ActionResult:
        """
        Execute a manipulation action.

        Args:
            action: The manipulation action to execute

        Returns:
            ActionResult object
        """
        try:
            action_params = action.parameters
            action_type = action_params.get("action", "unknown")

            if action_type in ["pick_up", "grasp", "take", "grab"]:
                # Pick up an object
                object_id = action_params.get("object_id", "unknown")
                object_type = action_params.get("object_type", "unknown")
                self.logger.info(f"Attempting to pick up {object_type} (ID: {object_id})")
                # Simulate manipulation
                await asyncio.sleep(2.5)  # Simulate time for manipulation

                return ActionResult(
                    action_id="manipulation_action",
                    status="success",
                    details=f"Picked up {object_type}",
                    duration=2.5
                )

            elif action_type in ["place", "put_down", "release", "drop"]:
                # Place an object down
                object_id = action_params.get("object_id", "unknown")
                self.logger.info(f"Attempting to place object (ID: {object_id})")
                # Simulate manipulation
                await asyncio.sleep(2.0)  # Simulate time for manipulation

                return ActionResult(
                    action_id="manipulation_action",
                    status="success",
                    details="Object placed",
                    duration=2.0
                )

            elif action_type == "move_arm":
                # Move the robot's arm
                position = action_params.get("position", "default")
                self.logger.info(f"Moving arm to {position}")
                # Simulate arm movement
                await asyncio.sleep(1.5)

                return ActionResult(
                    action_id="manipulation_action",
                    status="success",
                    details=f"Arm moved to {position}",
                    duration=1.5
                )

            elif action_type == "idle":
                # Idle action
                reason = action_params.get("reason", "no specific reason")
                self.logger.info(f"Idling: {reason}")
                # Simulate idle
                await asyncio.sleep(0.5)

                return ActionResult(
                    action_id="manipulation_action",
                    status="success",
                    details=f"Idling: {reason}",
                    duration=0.5
                )

            else:
                return ActionResult(
                    action_id="manipulation_action",
                    status="failed",
                    details=f"Unknown manipulation action: {action_type}",
                    duration=0.0
                )

        except Exception as e:
            return ActionResult(
                action_id="manipulation_action",
                status="failed",
                details=f"Manipulation error: {str(e)}",
                duration=0.0
            )

    async def _execute_detection_action(self, action: Action) -> ActionResult:
        """
        Execute a detection action.

        Args:
            action: The detection action to execute

        Returns:
            ActionResult object
        """
        try:
            action_params = action.parameters
            action_type = action_params.get("action", "unknown")

            if action_type == "detect_objects":
                # Detect specific objects
                object_type = action_params.get("object_type", "any")
                search_area = action_params.get("search_area", "current_area")
                self.logger.info(f"Detecting {object_type} objects in {search_area}")
                # Simulate detection
                await asyncio.sleep(1.0)  # Simulate time for detection

                return ActionResult(
                    action_id="detection_action",
                    status="success",
                    details=f"Completed detection of {object_type} objects in {search_area}",
                    duration=1.0
                )

            elif action_type == "scan_environment":
                # Scan the entire environment
                self.logger.info("Scanning environment")
                # Simulate scanning
                await asyncio.sleep(2.0)  # Simulate time for scanning

                return ActionResult(
                    action_id="detection_action",
                    status="success",
                    details="Environment scan completed",
                    duration=2.0
                )

            elif action_type == "report_status":
                # Report robot status
                self.logger.info("Reporting robot status")
                # Simulate status reporting
                await asyncio.sleep(0.5)

                return ActionResult(
                    action_id="detection_action",
                    status="success",
                    details="Status reported",
                    duration=0.5
                )

            elif action_type == "search_for_object":
                # Search for a specific object
                object_type = action_params.get("object_type", "unknown")
                self.logger.info(f"Searching for {object_type}")
                # Simulate search
                await asyncio.sleep(1.5)  # Simulate time for searching

                return ActionResult(
                    action_id="detection_action",
                    status="success",
                    details=f"Search for {object_type} completed",
                    duration=1.5
                )

            else:
                return ActionResult(
                    action_id="detection_action",
                    status="failed",
                    details=f"Unknown detection action: {action_type}",
                    duration=0.0
                )

        except Exception as e:
            return ActionResult(
                action_id="detection_action",
                status="failed",
                details=f"Detection error: {str(e)}",
                duration=0.0
            )

    async def _check_safety_protocols(self):
        """
        Check safety protocols during execution.
        """
        # In a real implementation, this would check various safety parameters
        # like obstacle detection, robot status, environment changes, etc.
        self.logger.debug("Safety protocols check passed")

    def validate_action_plan(self, action_plan: ActionPlan) -> List[str]:
        """
        Validate an action plan before execution.

        Args:
            action_plan: The action plan to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if not action_plan.actions:
            errors.append("Action plan has no actions")

        for i, action in enumerate(action_plan.actions):
            if action.type not in [at for at in ActionType]:
                errors.append(f"Action {i}: Invalid action type '{action.type}'")

            # Check dependencies refer to valid action indices
            for dep in action.dependencies:
                if not any(f"action_{j}" == dep for j in range(len(action_plan.actions))):
                    errors.append(f"Action {i}: Invalid dependency '{dep}'")

        return errors


class SafetyProtocolEnforcer:
    """
    Service for enforcing safety protocols during action execution.
    """

    def __init__(self):
        """
        Initialize the safety protocol enforcer.
        """
        self.logger = logging.getLogger(__name__)

    def check_action_safety(self, action: Action, robot_state: RobotState,
                           environmental_context: EnvironmentalContext) -> bool:
        """
        Check if an action is safe to execute given the current state.

        Args:
            action: The action to check
            robot_state: Current robot state
            environmental_context: Current environmental context

        Returns:
            True if action is safe, False otherwise
        """
        # Check battery level
        if robot_state.battery_level < 0.1:  # Less than 10% battery
            self.logger.warning("Action blocked: Low battery level")
            return False

        # Check safety status
        if robot_state.safety_status.value == "unsafe":
            self.logger.warning("Action blocked: Robot in unsafe state")
            return False

        # For navigation actions, check for obstacles
        if action.type == ActionType.NAVIGATION:
            if self._check_navigation_safety(action, environmental_context):
                return True
            else:
                return False

        # For manipulation actions, check if robot is capable
        if action.type == ActionType.MANIPULATION:
            if "manipulation" not in robot_state.available_capabilities:
                self.logger.warning("Action blocked: Robot not capable of manipulation")
                return False

        # Default: action is safe
        return True

    def _check_navigation_safety(self, action: Action, environmental_context: EnvironmentalContext) -> bool:
        """
        Check if a navigation action is safe.

        Args:
            action: The navigation action to check
            environmental_context: Current environmental context

        Returns:
            True if navigation is safe, False otherwise
        """
        # Check for obstacles in the path
        # In a real implementation, this would use more sophisticated path planning
        if environmental_context.obstacles:
            self.logger.info(f"Found {len(environmental_context.obstacles)} obstacles, checking path...")
            # For now, assume navigation is safe if obstacles exist but are avoidable
            return True

        return True

    def enforce_safety_constraints(self, action_plan: ActionPlan, robot_state: RobotState,
                                  environmental_context: EnvironmentalContext) -> ActionPlan:
        """
        Enforce safety constraints on an action plan.

        Args:
            action_plan: The original action plan
            robot_state: Current robot state
            environmental_context: Current environmental context

        Returns:
            Safe action plan (possibly modified)
        """
        # In a real implementation, this would modify the action plan to ensure safety
        # For now, we'll just validate each action and potentially skip unsafe ones
        safe_actions = []

        for action in action_plan.actions:
            if self.check_action_safety(action, robot_state, environmental_context):
                safe_actions.append(action)
            else:
                self.logger.warning(f"Skipping unsafe action: {action.type.value}")

        # Return a new action plan with only safe actions
        safe_plan = ActionPlan(
            id=f"safe_{action_plan.id}",
            voice_command_id=action_plan.voice_command_id,
            actions=safe_actions,
            status=action_plan.status,
            created_at=action_plan.created_at,
            estimated_duration=action_plan.estimated_duration
        )

        return safe_plan


# Example usage and testing functions
async def example_action_execution():
    """
    Example function demonstrating action execution.
    """
    executor = ActionExecutor()
    safety_enforcer = SafetyProtocolEnforcer()

    # Create a simple action plan for demonstration
    actions = [
        Action(
            type=ActionType.NAVIGATION,
            parameters={"action": "move_forward", "distance": 1.0},
            priority=1,
            dependencies=[]
        ),
        Action(
            type=ActionType.DETECTION,
            parameters={"action": "scan_environment"},
            priority=2,
            dependencies=[]
        )
    ]

    action_plan = ActionPlan(
        id="example_plan_1",
        voice_command_id="vc_1",
        actions=actions,
        status=CommandStatus.PENDING,
        created_at=datetime.now(),
        estimated_duration=10.0
    )

    # Validate the action plan
    validation_errors = executor.validate_action_plan(action_plan)
    if validation_errors:
        print("Validation errors found:")
        for error in validation_errors:
            print(f"  - {error}")
        return

    print("Executing example action plan...")
    execution_result = await executor.execute_action_plan(action_plan)

    print(f"Execution completed with overall status: {execution_result.overall_status}")
    print(f"Execution time: {execution_result.execution_time:.2f} seconds")
    for i, result in enumerate(execution_result.results):
        print(f"  Action {i+1}: {result.status} - {result.details}")


if __name__ == "__main__":
    # Run the example
    asyncio.run(example_action_execution())