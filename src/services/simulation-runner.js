/**
 * Simulation Runner Service
 * Orchestrates the overall simulation process including physics, collision detection, and joint dynamics
 */

const PhysicsSimulationService = require('./physics-simulation');
const CollisionDetectionService = require('./collision-detection');
const JointDynamicsService = require('./joint-dynamics');
const HumanoidRobot = require('../models/humanoid-robot');

class SimulationRunner {
  constructor(simulationParams) {
    this.physicsService = new PhysicsSimulationService(simulationParams);
    this.collisionService = new CollisionDetectionService();
    this.jointDynamicsService = new JointDynamicsService();

    this.robots = [];
    this.environmentObjects = [];
    this.isRunning = false;
    this.simulationStep = 0;
    this.maxSteps = 10000; // Prevent infinite simulations

    this.lastUpdateTime = Date.now();
  }

  // Add a robot to the simulation
  addRobot(robot) {
    if (!(robot instanceof HumanoidRobot) && (!robot.id || !robot.urdfPath)) {
      throw new Error('Invalid robot provided');
    }

    // Initialize joint dynamics for the robot
    this.jointDynamicsService.initializeJoints(robot);

    this.robots.push(robot);
    return robot.id;
  }

  // Add an environment object to the simulation
  addObject(obj) {
    if (!obj.id || !obj.position) {
      throw new Error('Object must have an id and position');
    }

    this.environmentObjects.push(obj);
  }

  // Start the simulation
  start() {
    if (this.isRunning) {
      console.warn('Simulation is already running');
      return false;
    }

    this.isRunning = true;
    this.simulationStep = 0;
    this.physicsService.startSimulation();

    console.log('Simulation started');
    this.lastUpdateTime = Date.now();

    // Run the simulation loop
    this.simulationLoop();
    return true;
  }

  // Stop the simulation
  stop() {
    this.isRunning = false;
    this.physicsService.stopSimulation();
    console.log('Simulation stopped');
  }

  // Main simulation loop
  simulationLoop() {
    if (!this.isRunning || this.simulationStep >= this.maxSteps) {
      this.stop();
      return;
    }

    const currentTime = Date.now();
    const deltaTime = (currentTime - this.lastUpdateTime) / 1000; // Convert to seconds
    this.lastUpdateTime = currentTime;

    // Run a single simulation step
    this.runSimulationStep(deltaTime);

    // Schedule the next step using setTimeout to prevent blocking
    setTimeout(() => this.simulationLoop(), 10); // ~100 Hz update rate

    this.simulationStep++;
  }

  // Run a single simulation step
  runSimulationStep(deltaTime) {
    // Apply physics to all robots
    for (const robot of this.robots) {
      // Apply joint dynamics to update robot joint states
      this.jointDynamicsService.updateAllJoints(robot, robot.controlInputs || {}, deltaTime);

      // Apply physics simulation (gravity, etc.) to the robot
      this.physicsService.applyPhysicsToRobot(robot, deltaTime);
    }

    // Detect and handle collisions
    const allObjects = [...this.robots, ...this.environmentObjects];
    const collisions = this.collisionService.detectCollisionsInEnvironment(allObjects);

    // Process collisions
    for (const collision of collisions) {
      this.handleCollision(collision);
    }

    // Update any other simulation aspects here
    this.updateSimulationState();
  }

  // Handle a collision event
  handleCollision(collision) {
    // In a real implementation, this would handle the physics response
    // For now, we'll just log the collision
    console.log(`Collision detected between ${collision.object1.id} and ${collision.object2.id}`);

    // Calculate collision response
    const response = this.collisionService.calculateCollisionResponse(
      collision.object1,
      collision.object2
    );

    // Update the objects with the response
    collision.object1.velocity = response.obj1.velocity || collision.object1.velocity;
    collision.object2.velocity = response.obj2.velocity || collision.object2.velocity;
  }

  // Update the overall simulation state
  updateSimulationState() {
    // Update any global simulation parameters
    // This could include things like environmental conditions, time of day, etc.
  }

  // Set control inputs for a robot
  setRobotControlInputs(robotId, controlInputs) {
    const robot = this.robots.find(r => r.id === robotId);
    if (!robot) {
      throw new Error(`Robot with ID ${robotId} not found`);
    }

    robot.controlInputs = controlInputs;
  }

  // Get the current simulation state
  getSimulationState() {
    return {
      isRunning: this.isRunning,
      simulationStep: this.simulationStep,
      robots: this.robots.map(robot => ({
        id: robot.id,
        name: robot.name,
        position: robot.position,
        jointStates: this.jointDynamicsService.getAllJointStates()
      })),
      environmentObjects: [...this.environmentObjects],
      physicsStatus: this.physicsService.getStatus(),
      collisionInfo: {
        activeCollisions: this.collisionService.getActiveCollisionsCount(),
        history: this.collisionService.getCollisionHistory()
      },
      timestamp: Date.now()
    };
  }

  // Reset the simulation to initial state
  reset() {
    this.stop();

    // Reset all services
    this.physicsService.stopSimulation();
    this.collisionService.clearHistory();

    // Reset robots to initial state
    for (const robot of this.robots) {
      this.jointDynamicsService.resetJoints(robot);
    }

    this.simulationStep = 0;
    console.log('Simulation reset to initial state');
  }

  // Get simulation statistics
  getStatistics() {
    return {
      robotCount: this.robots.length,
      environmentObjectCount: this.environmentObjects.length,
      totalCollisions: this.collisionService.getCollisionHistory().length,
      simulationStep: this.simulationStep,
      physicsStatus: this.physicsService.getStatus()
    };
  }

  // Load simulation state from a saved state
  loadState(simulationState) {
    this.robots = simulationState.robots || [];
    this.environmentObjects = simulationState.environmentObjects || [];
    this.simulationStep = simulationState.simulationStep || 0;

    // Reinitialize services with the loaded state
    for (const robot of this.robots) {
      this.jointDynamicsService.initializeJoints(robot);
    }
  }

  // Save current simulation state
  saveState() {
    return {
      robots: this.robots,
      environmentObjects: this.environmentObjects,
      simulationStep: this.simulationStep,
      timestamp: Date.now(),
      physicsParameters: this.physicsService.simulationParams.getState()
    };
  }
}

module.exports = SimulationRunner;