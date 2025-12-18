# VLA System API Contracts

## Voice Command Processing API

### POST /voice/commands
Process a voice command and return an action plan

**Request**:
```json
{
  "audio_data": "base64_encoded_audio",
  "user_id": "string",
  "context": {
    "environmental_context": "object",
    "robot_state": "object"
  }
}
```

**Response**:
```json
{
  "command_id": "string",
  "transcript": "string",
  "confidence": 0.95,
  "intent": "string",
  "action_plan": {
    "id": "string",
    "actions": [
      {
        "type": "string",
        "parameters": "object",
        "priority": 1
      }
    ],
    "estimated_duration": 120.5
  }
}
```

**Errors**:
- 400: Invalid audio format or missing required fields
- 422: Unable to process command due to unclear speech
- 500: Internal processing error

## Action Planning API

### POST /planning/generate
Generate an action plan from a text command

**Request**:
```json
{
  "command_text": "string",
  "environmental_context": "object",
  "robot_capabilities": ["string"]
}
```

**Response**:
```json
{
  "plan_id": "string",
  "actions": [
    {
      "id": "string",
      "type": "navigation|manipulation|detection",
      "parameters": "object",
      "dependencies": ["string"]
    }
  ],
  "estimated_duration": 120.5,
  "confidence": 0.85
}
```

## Execution API

### POST /execution/execute
Execute an action plan on the robot

**Request**:
```json
{
  "plan_id": "string",
  "actions": ["object"]
}
```

**Response**:
```json
{
  "execution_id": "string",
  "status": "executing|completed|failed",
  "results": [
    {
      "action_id": "string",
      "status": "success|failed|skipped",
      "details": "string"
    }
  ]
}
```

## Status API

### GET /status/robot
Get current robot state

**Response**:
```json
{
  "robot_state": {
    "position": {"x": 0.0, "y": 0.0, "z": 0.0},
    "orientation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0},
    "battery_level": 0.85,
    "available_capabilities": ["navigation", "manipulation"],
    "safety_status": "safe"
  },
  "environmental_context": {
    "objects": ["object"],
    "navigable_areas": ["object"],
    "timestamp": "2025-12-17T10:00:00Z"
  }
}
```