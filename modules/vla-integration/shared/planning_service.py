"""
Cognitive planning service for the Vision-Language-Action (VLA) integration system.

This module handles the decomposition of complex commands into sequences of simpler,
executable actions, with dependency resolution and plan adjustment capabilities.
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum

from .models import (
    Action, ActionType, ActionPlan, CommandStatus,
    VoiceCommand, UserIntent, EnvironmentalContext, RobotState
)


class PlanningStrategy(Enum):
    """Different strategies for task decomposition"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HIERARCHICAL = "hierarchical"


class CognitivePlanner:
    """
    Service for decomposing complex commands into executable action plans.
    """

    def __init__(self):
        """
        Initialize the cognitive planner.
        """
        self.logger = logging.getLogger(__name__)

    def generate_action_plan(
        self,
        voice_command: VoiceCommand,
        user_intent: UserIntent,
        environmental_context: EnvironmentalContext,
        robot_state: RobotState,
        strategy: PlanningStrategy = PlanningStrategy.SEQUENTIAL
    ) -> ActionPlan:
        """
        Generate an action plan from a voice command and environmental context.

        Args:
            voice_command: The original voice command
            user_intent: The interpreted user intent
            environmental_context: Current environmental context
            robot_state: Current robot state
            strategy: Planning strategy to use

        Returns:
            ActionPlan object with the generated plan
        """
        try:
            # Generate actions based on intent
            actions = self._generate_actions_from_intent(
                user_intent,
                environmental_context,
                robot_state,
                strategy
            )

            # Create and return the ActionPlan
            action_plan = ActionPlan(
                id=f"ap_{int(datetime.now().timestamp())}",
                voice_command_id=voice_command.id,
                actions=actions,
                status=CommandStatus.PENDING,
                created_at=datetime.now(),
                estimated_duration=self._estimate_duration(actions)
            )

            self.logger.info(f"Action plan generated with {len(actions)} actions")
            return action_plan

        except Exception as e:
            self.logger.error(f"Error generating action plan: {str(e)}")
            raise

    def _generate_actions_from_intent(
        self,
        user_intent: UserIntent,
        environmental_context: EnvironmentalContext,
        robot_state: RobotState,
        strategy: PlanningStrategy
    ) -> List[Action]:
        """
        Generate a list of actions based on the user intent.

        Args:
            user_intent: The interpreted user intent
            environmental_context: Current environmental context
            robot_state: Current robot state
            strategy: Planning strategy to use

        Returns:
            List of Action objects
        """
        actions = []

        # Based on the primary intent, generate appropriate actions
        primary_intent = user_intent.primary_intent.lower()
        parameters = user_intent.parameters

        if primary_intent == "navigation":
            actions = self._generate_navigation_actions(parameters, environmental_context, robot_state)
        elif primary_intent == "manipulation":
            actions = self._generate_manipulation_actions(parameters, environmental_context, robot_state)
        elif primary_intent == "detection":
            actions = self._generate_detection_actions(parameters, environmental_context, robot_state)
        elif primary_intent == "status":
            actions = self._generate_status_actions()
        elif primary_intent == "stop":
            actions = [Action(
                type=ActionType.NAVIGATION,
                parameters={"action": "stop"},
                priority=1,
                dependencies=[]
            )]
        else:
            # Default to a simple action for unrecognized intents
            actions = [Action(
                type=ActionType.NAVIGATION,
                parameters={"action": "wait", "reason": "unrecognized_intent"},
                priority=1,
                dependencies=[]
            )]

        return actions

    def _generate_navigation_actions(
        self,
        parameters: Dict[str, Any],
        environmental_context: EnvironmentalContext,
        robot_state: RobotState
    ) -> List[Action]:
        """
        Generate navigation actions based on parameters.

        Args:
            parameters: Parameters from intent interpretation
            environmental_context: Current environmental context
            robot_state: Current robot state

        Returns:
            List of navigation actions
        """
        actions = []

        # Handle different navigation scenarios
        if "location" in parameters:
            # Navigate to a specific location
            actions.append(Action(
                type=ActionType.NAVIGATION,
                parameters={
                    "action": "navigate_to",
                    "target_location": parameters["location"],
                    "current_position": robot_state.position
                },
                priority=1,
                dependencies=[]
            ))
        elif "direction" in parameters and "distance" in parameters:
            # Move in a specific direction
            actions.append(Action(
                type=ActionType.NAVIGATION,
                parameters={
                    "action": "move_direction",
                    "direction": parameters["direction"],
                    "distance": parameters["distance"],
                    "current_position": robot_state.position
                },
                priority=1,
                dependencies=[]
            ))
        elif "direction" in parameters:
            # Move in a general direction
            actions.append(Action(
                type=ActionType.NAVIGATION,
                parameters={
                    "action": "move_toward",
                    "direction": parameters["direction"],
                    "current_position": robot_state.position
                },
                priority=1,
                dependencies=[]
            ))
        else:
            # Default navigation action
            actions.append(Action(
                type=ActionType.NAVIGATION,
                parameters={
                    "action": "move_forward",
                    "distance": 1.0  # Default 1 meter
                },
                priority=1,
                dependencies=[]
            ))

        return actions

    def _generate_manipulation_actions(
        self,
        parameters: Dict[str, Any],
        environmental_context: EnvironmentalContext,
        robot_state: RobotState
    ) -> List[Action]:
        """
        Generate manipulation actions based on parameters.

        Args:
            parameters: Parameters from intent interpretation
            environmental_context: Current environmental context
            robot_state: Current robot state

        Returns:
            List of manipulation actions
        """
        actions = []

        if "object" in parameters and "action" in parameters:
            object_name = parameters["object"]
            manipulation_action = parameters["action"]

            # First, navigate to the object if needed
            target_object = None
            for obj in environmental_context.objects:
                if object_name.lower() in obj.type.lower():
                    target_object = obj
                    break

            if target_object:
                # Navigate to object
                actions.append(Action(
                    type=ActionType.NAVIGATION,
                    parameters={
                        "action": "navigate_to",
                        "target_position": target_object.position,
                        "approach_distance": 0.5  # 0.5m from object
                    },
                    priority=1,
                    dependencies=[]
                ))

                # Manipulate object
                actions.append(Action(
                    type=ActionType.MANIPULATION,
                    parameters={
                        "action": manipulation_action,
                        "object_id": target_object.id,
                        "object_type": target_object.type,
                        "object_position": target_object.position
                    },
                    priority=2,
                    dependencies=[f"action_{len(actions)-1}"]  # Depends on navigation
                ))
            else:
                # Object not found, add detection action
                actions.append(Action(
                    type=ActionType.DETECTION,
                    parameters={
                        "action": "search_for_object",
                        "object_type": object_name
                    },
                    priority=1,
                    dependencies=[]
                ))
        else:
            # Default manipulation action
            actions.append(Action(
                type=ActionType.MANIPULATION,
                parameters={
                    "action": "idle",
                    "reason": "insufficient_parameters"
                },
                priority=1,
                dependencies=[]
            ))

        return actions

    def _generate_detection_actions(
        self,
        parameters: Dict[str, Any],
        environmental_context: EnvironmentalContext,
        robot_state: RobotState
    ) -> List[Action]:
        """
        Generate detection actions based on parameters.

        Args:
            parameters: Parameters from intent interpretation
            environmental_context: Current environmental context
            robot_state: Current robot state

        Returns:
            List of detection actions
        """
        actions = []

        if "object_type" in parameters:
            actions.append(Action(
                type=ActionType.DETECTION,
                parameters={
                    "action": "detect_objects",
                    "object_type": parameters["object_type"],
                    "search_area": parameters.get("location", "current_area")
                },
                priority=1,
                dependencies=[]
            ))
        else:
            # Default detection action
            actions.append(Action(
                type=ActionType.DETECTION,
                parameters={
                    "action": "scan_environment"
                },
                priority=1,
                dependencies=[]
            ))

        return actions

    def _generate_status_actions(self) -> List[Action]:
        """
        Generate status reporting actions.

        Returns:
            List of status actions
        """
        return [Action(
            type=ActionType.DETECTION,
            parameters={
                "action": "report_status"
            },
            priority=1,
            dependencies=[]
        )]

    def _estimate_duration(self, actions: List[Action]) -> float:
        """
        Estimate the total duration for executing the action plan.

        Args:
            actions: List of actions to estimate duration for

        Returns:
            Estimated duration in seconds
        """
        base_time_per_action = 5.0  # Base time per action in seconds
        total_time = len(actions) * base_time_per_action

        # Add extra time for complex actions
        for action in actions:
            if action.type == ActionType.MANIPULATION:
                total_time += 3.0  # Additional time for manipulation
            elif action.type == ActionType.NAVIGATION:
                # Navigation might take longer depending on distance
                distance = action.parameters.get("distance", 1.0)
                total_time += distance * 0.5  # 0.5s per meter

        return total_time

    def adjust_plan_for_obstacles(
        self,
        action_plan: ActionPlan,
        environmental_context: EnvironmentalContext
    ) -> ActionPlan:
        """
        Adjust an action plan to account for detected obstacles.

        Args:
            action_plan: The original action plan
            environmental_context: Updated environmental context with obstacles

        Returns:
            Adjusted action plan
        """
        try:
            # For now, just log that we're adjusting the plan
            # In a real implementation, this would modify the plan based on obstacles
            self.logger.info(f"Adjusting plan {action_plan.id} for obstacles")

            # Create a copy of the action plan with adjusted status
            adjusted_plan = ActionPlan(
                id=f"adj_{action_plan.id}",
                voice_command_id=action_plan.voice_command_id,
                actions=action_plan.actions,
                status=action_plan.status,
                created_at=datetime.now(),
                estimated_duration=action_plan.estimated_duration
            )

            return adjusted_plan

        except Exception as e:
            self.logger.error(f"Error adjusting plan for obstacles: {str(e)}")
            return action_plan  # Return original plan if adjustment fails


class TaskDecomposer:
    """
    Service for decomposing complex tasks into simpler subtasks.
    """

    def __init__(self):
        """
        Initialize the task decomposer.
        """
        self.logger = logging.getLogger(__name__)

    def decompose_task(self, command_text: str) -> List[str]:
        """
        Decompose a complex command into a list of simpler subtasks.

        Args:
            command_text: The complex command to decompose

        Returns:
            List of simpler subtasks
        """
        # This is a simple implementation - in a real system, this would use
        # more sophisticated NLP and planning algorithms
        subtasks = []

        # Convert command to lowercase for easier processing
        cmd_lower = command_text.lower()

        # Identify common task patterns
        if "and" in cmd_lower:
            # Split on 'and' to identify multiple tasks
            parts = cmd_lower.split("and")
            for part in parts:
                part = part.strip()
                if part:
                    subtasks.append(part.capitalize())
        elif "then" in cmd_lower:
            # Split on 'then' to identify sequential tasks
            parts = cmd_lower.split("then")
            for part in parts:
                part = part.strip()
                if part:
                    subtasks.append(part.capitalize())
        else:
            # Single task
            subtasks.append(command_text)

        return subtasks

    def create_decomposition_example(self, command: str) -> Dict[str, Any]:
        """
        Create an example of task decomposition for educational purposes.

        Args:
            command: The command to decompose

        Returns:
            Dictionary with decomposition example
        """
        subtasks = self.decompose_task(command)

        return {
            "original_command": command,
            "decomposed_tasks": subtasks,
            "task_count": len(subtasks),
            "explanation": f"The command '{command}' was decomposed into {len(subtasks)} simpler tasks."
        }


# Example usage and testing functions
def example_cognitive_planning():
    """
    Example function demonstrating cognitive planning.
    """
    from .models import Position3D, Orientation

    planner = CognitivePlanner()
    decomposer = TaskDecomposer()

    # Example: Decompose a complex task
    complex_command = "Go to the kitchen and pick up the red cup then bring it to the table"
    decomposition = decomposer.create_decomposition_example(complex_command)
    print("Task Decomposition Example:")
    print(f"Original: {decomposition['original_command']}")
    print(f"Decomposed: {decomposition['decomposed_tasks']}")
    print()

    # Example: Create a simple voice command and intent for planning
    # Note: This is simplified - in reality, these would come from voice processing
    class MockVoiceCommand:
        def __init__(self, text, cmd_id="mock_vc_1"):
            self.text = text
            self.id = cmd_id

    class MockUserIntent:
        def __init__(self, primary_intent, parameters):
            self.primary_intent = primary_intent
            self.parameters = parameters

    class MockEnvironmentalContext:
        def __init__(self):
            self.objects = []
            self.id = "mock_env_1"
            self.timestamp = datetime.now()
            self.navigable_areas = []
            self.obstacles = []
            self.robot_position = Position3D(0.0, 0.0, 0.0)

    class MockRobotState:
        def __init__(self):
            self.id = "mock_robot_1"
            self.position = Position3D(0.0, 0.0, 0.0)
            self.orientation = Orientation(0.0, 0.0, 0.0, 1.0)
            self.battery_level = 0.8
            self.available_capabilities = ["navigation", "manipulation"]
            self.safety_status = "safe"
            self.timestamp = datetime.now()

    # Create mock objects
    voice_cmd = MockVoiceCommand("Move forward 2 meters")
    user_intent = MockUserIntent("navigation", {"direction": "forward", "distance": 2.0})
    env_context = MockEnvironmentalContext()
    robot_state = MockRobotState()

    # Generate action plan
    try:
        action_plan = planner.generate_action_plan(
            voice_cmd, user_intent, env_context, robot_state
        )
        print(f"Generated action plan with {len(action_plan.actions)} actions")
        for i, action in enumerate(action_plan.actions):
            print(f"  Action {i+1}: {action.type.value} - {action.parameters}")
    except Exception as e:
        print(f"Error in example: {e}")


if __name__ == "__main__":
    example_cognitive_planning()