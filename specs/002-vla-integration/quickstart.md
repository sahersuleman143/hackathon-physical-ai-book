# Quickstart Guide: Vision-Language-Action (VLA) Integration

## Overview

This guide provides a quick introduction to the Vision-Language-Action (VLA) system for humanoid robots. The VLA system enables robots to understand natural language commands and execute them through a combination of speech recognition, cognitive planning, and robotic action execution.

## Prerequisites

- ROS 2 Humble Hawksbill installed
- Python 3.11 or higher
- OpenAI API key (for Whisper and GPT integration)
- Basic understanding of ROS 2 concepts

## Setup

1. **Install Dependencies**
   ```bash
   pip install openai speech-recognition pyaudio
   ```

2. **Configure API Keys**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

3. **Initialize the VLA System**
   ```python
   from vla_integration import VLAController

   controller = VLAController()
   controller.initialize()
   ```

## Basic Usage

### Voice Command Processing
```python
# Start listening for voice commands
result = controller.listen_for_command()

# Process the command through the VLA pipeline
action_plan = controller.process_voice_command(result.text)
```

### Cognitive Planning
```python
# Generate action plan from user intent
plan = controller.generate_action_plan(
    intent="Move forward 2 meters",
    environmental_context=controller.get_environment()
)
```

### Execute Actions
```python
# Execute the planned actions
execution_result = controller.execute_plan(plan)

# Check the result
print(f"Plan executed: {execution_result.overall_status}")
```

## Example Workflow

1. **Voice Input**: "Please move to the red cube and pick it up"
2. **Speech Recognition**: Convert to text using Whisper
3. **Intent Processing**: Extract intent and parameters using LLM
4. **Action Planning**: Generate sequence of navigation and manipulation actions
5. **Execution**: Execute actions on the humanoid robot
6. **Feedback**: Provide confirmation to the user

## Testing

Run the basic functionality test:
```bash
python -m pytest tests/basic_vla_test.py
```

## Next Steps

- Explore Chapter 1: Voice-to-Action for detailed Whisper integration
- Study Chapter 2: Cognitive Planning for LLM-based task decomposition
- Complete Chapter 3: Capstone Project for full integration examples