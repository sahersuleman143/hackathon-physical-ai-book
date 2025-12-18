/**
 * Sensor Configuration Model
 * Represents configuration for various sensors (LiDAR, Depth Camera, IMU)
 */

class SensorConfiguration {
  constructor(type, name, position = { x: 0, y: 0, z: 0 }, orientation = { roll: 0, pitch: 0, yaw: 0 }, parameters = {}, outputFormat = '') {
    this.id = this.generateId();
    this.type = type; // Enum: LiDAR, Depth Camera, IMU
    this.name = name;
    this.position = position; // x, y, z coordinates relative to parent link
    this.orientation = orientation; // roll, pitch, yaw relative to parent link
    this.parameters = parameters; // sensor-specific settings like range, resolution, etc.
    this.outputFormat = outputFormat; // format of the sensor data
    this.createdAt = new Date();
    this.updatedAt = new Date();
  }

  // Generate a unique ID for the sensor
  generateId() {
    return 'sensor_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }

  // Validate the sensor configuration
  validate() {
    const errors = [];

    if (!this.type || !['LiDAR', 'Depth Camera', 'IMU'].includes(this.type)) {
      errors.push('Type is required and must be one of: LiDAR, Depth Camera, IMU');
    }

    if (!this.name || typeof this.name !== 'string') {
      errors.push('Name is required and must be a string');
    }

    if (!this.position || typeof this.position !== 'object') {
      errors.push('Position must be an object with x, y, z coordinates');
    } else {
      if (typeof this.position.x !== 'number' || typeof this.position.y !== 'number' || typeof this.position.z !== 'number') {
        errors.push('Position coordinates must be numbers');
      }
    }

    if (!this.orientation || typeof this.orientation !== 'object') {
      errors.push('Orientation must be an object with roll, pitch, yaw values');
    } else {
      if (typeof this.orientation.roll !== 'number' ||
          typeof this.orientation.pitch !== 'number' ||
          typeof this.orientation.yaw !== 'number') {
        errors.push('Orientation values must be numbers');
      }
    }

    if (!this.parameters || typeof this.parameters !== 'object') {
      errors.push('Parameters must be an object');
    }

    if (!this.outputFormat || typeof this.outputFormat !== 'string') {
      errors.push('Output format is required and must be a string');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  // Update sensor parameters
  updateParameters(newParameters) {
    this.parameters = { ...this.parameters, ...newParameters };
    this.updatedAt = new Date();
  }

  // Update position
  updatePosition(newPosition) {
    this.position = { ...this.position, ...newPosition };
    this.updatedAt = new Date();
  }

  // Update orientation
  updateOrientation(newOrientation) {
    this.orientation = { ...this.orientation, ...newOrientation };
    this.updatedAt = new Date();
  }

  // Get sensor configuration state
  getState() {
    return {
      id: this.id,
      type: this.type,
      name: this.name,
      position: this.position,
      orientation: this.orientation,
      parameters: this.parameters,
      outputFormat: this.outputFormat,
      createdAt: this.createdAt,
      updatedAt: this.updatedAt
    };
  }
}

module.exports = SensorConfiguration;