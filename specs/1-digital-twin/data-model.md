# Data Model: Digital Twin (Gazebo & Unity)

## Digital Twin Environment
- **Name**: String (identifier for the environment)
- **Description**: Text (educational content about the environment)
- **Physics Parameters**: Object (gravity, friction, damping settings)
- **Components**: Array (list of robot and sensor models in the environment)

## Humanoid Robot Model
- **Name**: String (identifier for the robot)
- **Description**: Text (educational content about the robot)
- **URDF Path**: String (path to the URDF file)
- **Joint Configuration**: Object (joint limits, types, dynamics)
- **Physical Properties**: Object (mass, inertia, collision properties)
- **Attached Sensors**: Array (list of sensors attached to the robot)

## Sensor Configuration
- **Type**: Enum (LiDAR, Depth Camera, IMU)
- **Name**: String (identifier for the sensor)
- **Position**: Object (x, y, z coordinates relative to parent link)
- **Orientation**: Object (roll, pitch, yaw relative to parent link)
- **Parameters**: Object (sensor-specific settings like range, resolution, etc.)
- **Output Format**: String (format of the sensor data)

## Simulation Parameters
- **Gravity**: Object (x, y, z components of gravitational acceleration)
- **Time Step**: Number (simulation time step in seconds)
- **Real Time Factor**: Number (ratio of simulation time to real time)
- **Collision Detection**: Object (settings for collision detection algorithm)
- **Solver Settings**: Object (physics solver parameters)

## Unity Scene Configuration
- **Name**: String (identifier for the Unity scene)
- **Description**: Text (educational content about the scene)
- **Objects**: Array (list of objects in the scene)
- **Lighting**: Object (lighting configuration)
- **Camera Settings**: Object (camera position, angle, etc.)
- **Interaction Elements**: Array (interactive elements for human-robot interaction)

## Learning Module
- **Title**: String (name of the learning module)
- **Description**: Text (overview of the learning objectives)
- **Prerequisites**: Array (knowledge or skills required)
- **Learning Objectives**: Array (specific outcomes students should achieve)
- **Steps**: Array (sequence of activities)
- **Resources**: Array (files, links, or materials needed)
- **Assessment**: Object (criteria for evaluating success)

## Simulation Output Data
- **Timestamp**: Number (time in simulation)
- **Robot State**: Object (position, orientation, joint angles)
- **Sensor Data**: Object (data from all attached sensors)
- **Physics Interactions**: Array (collision events, forces, etc.)
- **Environment State**: Object (state of environment objects)