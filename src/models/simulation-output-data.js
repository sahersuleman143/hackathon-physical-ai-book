/**
 * Simulation Output Data Model
 * Represents data output from simulations including robot state, sensor data, and physics interactions
 */

class SimulationOutputData {
  constructor(
    timestamp = Date.now(),
    robotState = {},
    sensorData = {},
    physicsInteractions = [],
    environmentState = {}
  ) {
    this.timestamp = timestamp; // time in simulation
    this.robotState = robotState; // position, orientation, joint angles
    this.sensorData = sensorData; // data from all attached sensors
    this.physicsInteractions = physicsInteractions; // collision events, forces, etc.
    this.environmentState = environmentState; // state of environment objects
    this.createdAt = new Date();
  }

  // Update robot state
  updateRobotState(newState) {
    this.robotState = { ...this.robotState, ...newState };
    this.timestamp = Date.now();
  }

  // Update sensor data
  updateSensorData(newSensorData) {
    this.sensorData = { ...this.sensorData, ...newSensorData };
    this.timestamp = Date.now();
  }

  // Add a physics interaction
  addPhysicsInteraction(interaction) {
    this.physicsInteractions.push(interaction);
    this.timestamp = Date.now();
  }

  // Update environment state
  updateEnvironmentState(newState) {
    this.environmentState = { ...this.environmentState, ...newState };
    this.timestamp = Date.now();
  }

  // Validate the simulation output data
  validate() {
    const errors = [];

    if (typeof this.timestamp !== 'number') {
      errors.push('Timestamp must be a number');
    }

    if (!this.robotState || typeof this.robotState !== 'object') {
      errors.push('Robot state must be an object');
    }

    if (!this.sensorData || typeof this.sensorData !== 'object') {
      errors.push('Sensor data must be an object');
    }

    if (!Array.isArray(this.physicsInteractions)) {
      errors.push('Physics interactions must be an array');
    }

    if (!this.environmentState || typeof this.environmentState !== 'object') {
      errors.push('Environment state must be an object');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  // Get simulation output data state
  getState() {
    return {
      timestamp: this.timestamp,
      robotState: this.robotState,
      sensorData: this.sensorData,
      physicsInteractions: this.physicsInteractions,
      environmentState: this.environmentState,
      createdAt: this.createdAt
    };
  }

  // Create a summary of the simulation output
  getSummary() {
    return {
      timestamp: this.timestamp,
      robotStateSummary: {
        position: this.robotState.position,
        orientation: this.robotState.orientation,
        jointAngles: this.robotState.jointAngles
      },
      sensorCount: Object.keys(this.sensorData).length,
      physicsInteractionCount: this.physicsInteractions.length,
      environmentObjectCount: Object.keys(this.environmentState).length
    };
  }
}

module.exports = SimulationOutputData;