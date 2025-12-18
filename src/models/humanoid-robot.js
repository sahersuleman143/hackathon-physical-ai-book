/**
 * Humanoid Robot Model
 * Represents the physical representation of a human-like robot with joints, sensors, and dynamic properties
 */

class HumanoidRobot {
  constructor(name, description, urdfPath, jointConfiguration = {}, physicalProperties = {}, attachedSensors = []) {
    this.id = this.generateId();
    this.name = name;
    this.description = description;
    this.urdfPath = urdfPath;
    this.jointConfiguration = jointConfiguration; // joint limits, types, dynamics
    this.physicalProperties = physicalProperties; // mass, inertia, collision properties
    this.attachedSensors = attachedSensors; // list of sensors attached to the robot
    this.createdAt = new Date();
    this.updatedAt = new Date();
  }

  // Generate a unique ID for the robot
  generateId() {
    return 'robot_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }

  // Add a sensor to the robot
  addSensor(sensor) {
    this.attachedSensors.push(sensor);
    this.updatedAt = new Date();
  }

  // Remove a sensor from the robot
  removeSensor(sensorId) {
    this.attachedSensors = this.attachedSensors.filter(sensor => sensor.id !== sensorId);
    this.updatedAt = new Date();
  }

  // Update joint configuration
  updateJointConfiguration(newConfiguration) {
    this.jointConfiguration = { ...this.jointConfiguration, ...newConfiguration };
    this.updatedAt = new Date();
  }

  // Update physical properties
  updatePhysicalProperties(newProperties) {
    this.physicalProperties = { ...this.physicalProperties, ...newProperties };
    this.updatedAt = new Date();
  }

  // Validate the robot configuration
  validate() {
    const errors = [];

    if (!this.name || typeof this.name !== 'string') {
      errors.push('Name is required and must be a string');
    }

    if (!this.urdfPath || typeof this.urdfPath !== 'string') {
      errors.push('URDF path is required and must be a string');
    }

    if (!this.jointConfiguration || typeof this.jointConfiguration !== 'object') {
      errors.push('Joint configuration must be an object');
    }

    if (!this.physicalProperties || typeof this.physicalProperties !== 'object') {
      errors.push('Physical properties must be an object');
    }

    if (!Array.isArray(this.attachedSensors)) {
      errors.push('Attached sensors must be an array');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  // Get robot state
  getState() {
    return {
      id: this.id,
      name: this.name,
      description: this.description,
      urdfPath: this.urdfPath,
      jointConfiguration: this.jointConfiguration,
      physicalProperties: this.physicalProperties,
      attachedSensors: this.attachedSensors,
      createdAt: this.createdAt,
      updatedAt: this.updatedAt
    };
  }
}

module.exports = HumanoidRobot;