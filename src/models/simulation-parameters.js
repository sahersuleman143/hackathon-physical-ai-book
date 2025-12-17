/**
 * Simulation Parameters Model
 * Represents configurable physics properties, environmental conditions, and robot characteristics
 */

class SimulationParameters {
  constructor(
    gravity = { x: 0, y: 0, z: -9.81 },
    timeStep = 0.001,
    realTimeFactor = 1.0,
    collisionDetection = {},
    solverSettings = {}
  ) {
    this.gravity = gravity; // x, y, z components of gravitational acceleration
    this.timeStep = timeStep; // simulation time step in seconds
    this.realTimeFactor = realTimeFactor; // ratio of simulation time to real time
    this.collisionDetection = collisionDetection; // settings for collision detection algorithm
    this.solverSettings = solverSettings; // physics solver parameters
    this.createdAt = new Date();
    this.updatedAt = new Date();
  }

  // Update gravity parameters
  updateGravity(newGravity) {
    this.gravity = { ...this.gravity, ...newGravity };
    this.updatedAt = new Date();
  }

  // Update time step
  updateTimeStep(newTimeStep) {
    if (typeof newTimeStep === 'number' && newTimeStep > 0) {
      this.timeStep = newTimeStep;
      this.updatedAt = new Date();
    } else {
      throw new Error('Time step must be a positive number');
    }
  }

  // Update real time factor
  updateRealTimeFactor(newRealTimeFactor) {
    if (typeof newRealTimeFactor === 'number' && newRealTimeFactor > 0) {
      this.realTimeFactor = newRealTimeFactor;
      this.updatedAt = new Date();
    } else {
      throw new Error('Real time factor must be a positive number');
    }
  }

  // Update collision detection settings
  updateCollisionDetection(newSettings) {
    this.collisionDetection = { ...this.collisionDetection, ...newSettings };
    this.updatedAt = new Date();
  }

  // Update solver settings
  updateSolverSettings(newSettings) {
    this.solverSettings = { ...this.solverSettings, ...newSettings };
    this.updatedAt = new Date();
  }

  // Validate the simulation parameters
  validate() {
    const errors = [];

    if (!this.gravity || typeof this.gravity !== 'object') {
      errors.push('Gravity must be an object with x, y, z components');
    } else {
      if (typeof this.gravity.x !== 'number' ||
          typeof this.gravity.y !== 'number' ||
          typeof this.gravity.z !== 'number') {
        errors.push('Gravity components must be numbers');
      }
    }

    if (typeof this.timeStep !== 'number' || this.timeStep <= 0) {
      errors.push('Time step must be a positive number');
    }

    if (typeof this.realTimeFactor !== 'number' || this.realTimeFactor <= 0) {
      errors.push('Real time factor must be a positive number');
    }

    if (!this.collisionDetection || typeof this.collisionDetection !== 'object') {
      errors.push('Collision detection settings must be an object');
    }

    if (!this.solverSettings || typeof this.solverSettings !== 'object') {
      errors.push('Solver settings must be an object');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  // Get simulation parameters state
  getState() {
    return {
      gravity: this.gravity,
      timeStep: this.timeStep,
      realTimeFactor: this.realTimeFactor,
      collisionDetection: this.collisionDetection,
      solverSettings: this.solverSettings,
      createdAt: this.createdAt,
      updatedAt: this.updatedAt
    };
  }
}

module.exports = SimulationParameters;