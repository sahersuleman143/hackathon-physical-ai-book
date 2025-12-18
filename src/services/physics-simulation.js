/**
 * Physics Simulation Service
 * Handles gravity, collision detection, and joint dynamics for the simulation
 */

const SimulationParameters = require('../models/simulation-parameters');

class PhysicsSimulationService {
  constructor(simulationParams = new SimulationParameters()) {
    this.simulationParams = simulationParams;
    this.isRunning = false;
    this.currentTime = 0;
  }

  // Set simulation parameters
  setSimulationParameters(params) {
    if (params instanceof SimulationParameters) {
      this.simulationParams = params;
    } else {
      this.simulationParams = new SimulationParameters(
        params.gravity,
        params.timeStep,
        params.realTimeFactor,
        params.collisionDetection,
        params.solverSettings
      );
    }
  }

  // Apply gravity to an object
  applyGravity(object, deltaTime = this.simulationParams.timeStep) {
    if (!object.physicalProperties || !object.physicalProperties.mass) {
      throw new Error('Object must have physical properties with mass defined');
    }

    const gravity = this.simulationParams.gravity;
    const mass = object.physicalProperties.mass;

    // Calculate gravitational force: F = m * g
    const force = {
      x: mass * gravity.x,
      y: mass * gravity.y,
      z: mass * gravity.z
    };

    // Update object velocity based on force (simplified)
    if (object.velocity) {
      const acceleration = {
        x: force.x / mass,
        y: force.y / mass,
        z: force.z / mass
      };

      object.velocity.x += acceleration.x * deltaTime;
      object.velocity.y += acceleration.y * deltaTime;
      object.velocity.z += acceleration.z * deltaTime;
    }

    // Update object position based on velocity
    if (object.position && object.velocity) {
      object.position.x += object.velocity.x * deltaTime;
      object.position.y += object.velocity.y * deltaTime;
      object.position.z += object.velocity.z * deltaTime;
    }

    return object;
  }

  // Calculate collision response between two objects
  calculateCollisionResponse(obj1, obj2) {
    // Simplified collision response calculation
    // In a real implementation, this would use more sophisticated physics
    const response = {
      obj1Force: { x: 0, y: 0, z: 0 },
      obj2Force: { x: 0, y: 0, z: 0 },
      collisionDetected: false
    };

    // Simple sphere collision detection
    const dx = obj2.position.x - obj1.position.x;
    const dy = obj2.position.y - obj1.position.y;
    const dz = obj2.position.z - obj1.position.z;
    const distance = Math.sqrt(dx * dx + dy * dy + dz * dz);

    // Calculate combined radius for collision detection
    const r1 = obj1.physicalProperties.radius || 0.1;
    const r2 = obj2.physicalProperties.radius || 0.1;
    const minDistance = r1 + r2;

    if (distance < minDistance) {
      response.collisionDetected = true;

      // Normalize collision vector
      const nx = dx / distance;
      const ny = dy / distance;
      const nz = dz / distance;

      // Calculate collision response forces
      const collisionForce = 10.0; // This would be calculated based on mass, velocity, etc.
      response.obj1Force = {
        x: -nx * collisionForce,
        y: -ny * collisionForce,
        z: -nz * collisionForce
      };
      response.obj2Force = {
        x: nx * collisionForce,
        y: ny * collisionForce,
        z: nz * collisionForce
      };
    }

    return response;
  }

  // Apply physics to a robot model
  applyPhysicsToRobot(robot, deltaTime = this.simulationParams.timeStep) {
    if (!robot || !robot.urdfPath) {
      throw new Error('Robot must be defined with a URDF path');
    }

    // Apply gravity to the robot
    this.applyGravity(robot, deltaTime);

    // Apply joint constraints if defined
    if (robot.jointConfiguration && robot.jointStates) {
      this.applyJointConstraints(robot);
    }

    // Update simulation time
    this.currentTime += deltaTime;

    return robot;
  }

  // Apply joint constraints to limit movement
  applyJointConstraints(robot) {
    if (!robot.jointConfiguration || !robot.jointStates) {
      return robot;
    }

    // Apply joint limits to each joint
    for (const jointName in robot.jointConfiguration) {
      const jointConfig = robot.jointConfiguration[jointName];
      const jointState = robot.jointStates[jointName];

      if (jointConfig.limits && jointState) {
        // Apply position limits
        if (jointConfig.limits.position) {
          if (jointState.position < jointConfig.limits.position.min) {
            jointState.position = jointConfig.limits.position.min;
            jointState.velocity = 0; // Stop movement when limit reached
          } else if (jointState.position > jointConfig.limits.position.max) {
            jointState.position = jointConfig.limits.position.max;
            jointState.velocity = 0; // Stop movement when limit reached
          }
        }

        // Apply velocity limits
        if (jointConfig.limits.velocity) {
          if (jointState.velocity > jointConfig.limits.velocity) {
            jointState.velocity = jointConfig.limits.velocity;
          } else if (jointState.velocity < -jointConfig.limits.velocity) {
            jointState.velocity = -jointConfig.limits.velocity;
          }
        }

        // Apply effort limits
        if (jointConfig.limits.effort) {
          if (jointState.effort > jointConfig.limits.effort) {
            jointState.effort = jointConfig.limits.effort;
          } else if (jointState.effort < -jointConfig.limits.effort) {
            jointState.effort = -jointConfig.limits.effort;
          }
        }
      }
    }

    return robot;
  }

  // Start the physics simulation
  startSimulation() {
    this.isRunning = true;
    this.currentTime = 0;
    console.log('Physics simulation started');
  }

  // Stop the physics simulation
  stopSimulation() {
    this.isRunning = false;
    console.log('Physics simulation stopped');
  }

  // Get current simulation time
  getCurrentTime() {
    return this.currentTime;
  }

  // Get simulation status
  getStatus() {
    return {
      isRunning: this.isRunning,
      currentTime: this.currentTime,
      parameters: this.simulationParams.getState()
    };
  }
}

module.exports = PhysicsSimulationService;