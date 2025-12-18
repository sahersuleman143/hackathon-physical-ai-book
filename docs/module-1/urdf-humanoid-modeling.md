# Humanoid Structure with URDF

## Purpose of URDF in Humanoid Robotics

URDF (Unified Robot Description Format) is an XML-based format used to describe robot models in ROS. For humanoid robotics, URDF serves as the blueprint that defines:

- Physical structure: links (rigid bodies) and their properties
- Kinematic structure: joints connecting links and their motion constraints
- Visual representation: how the robot appears in simulation and visualization tools
- Collision properties: shapes used for collision detection

URDF is essential for:
- Robot simulation in Gazebo and other simulators
- Visualization in RViz
- Kinematic analysis and motion planning
- Robot calibration and control

## Links, Joints, and Kinematic Chains

### Links

Links represent rigid bodies in the robot. For a humanoid robot, typical links include:

- Base link (usually the pelvis or torso)
- Limb segments (upper arm, lower arm, thigh, shank, foot)
- End effectors (hands)
- Sensors (cameras, IMUs)

Each link can have:
- Inertial properties (mass, center of mass, inertia tensor)
- Visual geometry (for display)
- Collision geometry (for physics simulation)

### Joints

Joints define the connection between links and specify the allowed motion. Common joint types for humanoid robots:

- **Revolute**: Rotational joint with limited range (e.g., elbow, knee)
- **Continuous**: Rotational joint without limits (e.g., shoulder yaw)
- **Prismatic**: Linear sliding joint (rarely used in humanoid robots)
- **Fixed**: No motion allowed (e.g., sensor mounting)

### Kinematic Chains

Kinematic chains form the pathways from base to end effectors. For humanoid robots, this typically includes:

- Left and right arm chains
- Left and right leg chains
- Spine and head chain

## Preparing Humanoid Models for Simulation

A complete humanoid URDF model typically includes:

```xml
<?xml version="1.0"?>
<robot name="humanoid_robot">
  <!-- Base link -->
  <link name="base_link">
    <inertial>
      <mass value="10.0" />
      <origin xyz="0 0 0" />
      <inertia ixx="1.0" ixy="0.0" ixz="0.0" iyy="1.0" iyz="0.0" izz="1.0" />
    </inertial>
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0" />
      <geometry>
        <box size="0.5 0.3 0.8" />
      </geometry>
    </visual>
    <collision>
      <origin xyz="0 0 0" rpy="0 0 0" />
      <geometry>
        <box size="0.5 0.3 0.8" />
      </geometry>
    </collision>
  </link>

  <!-- Example joint connecting torso to hip -->
  <joint name="torso_to_hip" type="revolute">
    <parent link="base_link" />
    <child link="hip" />
    <origin xyz="0 0 0.4" rpy="0 0 0" />
    <axis xyz="0 0 1" />
    <limit lower="-1.57" upper="1.57" effort="100.0" velocity="1.0" />
  </joint>

  <link name="hip">
    <!-- Hip link definition -->
  </link>
</robot>
```

## Sample URDF Files and Explanations

When creating humanoid models, consider these best practices:

1. **Start simple**: Begin with a basic skeleton and add complexity gradually
2. **Use consistent naming**: Follow conventions for joint and link names
3. **Define proper inertial properties**: Essential for realistic simulation
4. **Include transmission elements**: Define how actuators connect to joints
5. **Validate the model**: Check for kinematic loops and proper connectivity

A complete humanoid model will include all major body segments connected through appropriate joints, with realistic inertial properties and collision geometries that approximate the physical robot's characteristics.