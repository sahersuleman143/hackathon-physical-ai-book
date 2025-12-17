# Quickstart Guide: Digital Twin (Gazebo & Unity)

## Prerequisites

Before starting with the Digital Twin examples, ensure you have the following installed:

- **Gazebo**: Version 11 or higher (for physics simulation)
- **Unity Hub**: With Unity 2021.3 LTS or higher
- **Docusaurus**: Node.js 16+ with npm/yarn
- **Git**: For version control
- **Basic knowledge**: Robotics fundamentals and simulation concepts

## Setting Up the Environment

### 1. Clone the Repository
```bash
git clone <repository-url>
cd hackathon-physical-ai-book
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Verify Gazebo Installation
```bash
gazebo --version
```

### 4. Verify Unity Installation
Launch Unity Hub and ensure you have a compatible Unity version installed.

## Running the First Example: Humanoid Simulation in Gazebo

### 1. Navigate to the Example
```bash
cd static/simulation-assets/gazebo-models
```

### 2. Launch Gazebo with the Humanoid Model
```bash
gazebo humanoid.urdf
```

### 3. Observe Physics Behavior
- Watch the humanoid model respond to gravity
- Use Gazebo's interface to apply forces to the robot
- Observe joint constraints and collision detection

## Running the Second Example: Sensor Navigation

### 1. Launch the Sensor-Enabled Robot
```bash
roslaunch (Note: Using provided launch files in examples)
```

### 2. Observe Sensor Data
- LiDAR: Check point cloud visualization
- Depth Camera: View depth map output
- IMU: Monitor orientation and acceleration data

### 3. Navigate Through Environment
- Use provided control scripts to move the robot
- Observe how sensor data changes with robot movement
- Complete the navigation exercise as described in the tutorial

## Running the Third Example: Unity Interaction Scene

### 1. Open Unity Project
- Launch Unity Hub
- Open the project in `static/simulation-assets/unity-scenes`
- Load the interactive-task.unity scene

### 2. Run the Simulation
- Press Play in Unity Editor
- Interact with the scene using mouse/keyboard controls
- Observe synchronization with Gazebo simulation data

## Building the Documentation

### 1. Start Local Server
```bash
npm start
```

### 2. View Documentation
Open your browser to `http://localhost:3000` to view the complete documentation.

## Troubleshooting

### Common Issues:

1. **Gazebo won't launch**
   - Ensure proper installation and graphics drivers
   - Try running with `gazebo --verbose` for detailed logs

2. **Unity scene not loading**
   - Check that all assets are properly imported
   - Verify Unity version compatibility

3. **Documentation build fails**
   - Run `npm install` again to ensure all dependencies
   - Check Node.js version requirements

## Next Steps

After completing the quickstart:
1. Read the full documentation chapters
2. Complete all three hands-on examples
3. Experiment with modifying parameters to understand system behavior
4. Explore advanced features in the reference materials