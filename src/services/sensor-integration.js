/**
 * Sensor Integration Service
 * Manages the integration of various sensors (LiDAR, Depth Camera, IMU) with the simulation
 */

const SensorConfiguration = require('../models/sensor-configuration');

class SensorIntegrationService {
  constructor() {
    this.sensors = new Map(); // Store all sensors by ID
    this.attachedSensors = new Map(); // Map robot IDs to their sensors
    this.sensorDataBuffer = new Map(); // Buffer for sensor data
    this.isRunning = false;
  }

  // Attach a sensor to a robot
  attachSensorToRobot(robotId, sensorConfig) {
    if (!(sensorConfig instanceof SensorConfiguration)) {
      sensorConfig = new SensorConfiguration(
        sensorConfig.type,
        sensorConfig.name,
        sensorConfig.position,
        sensorConfig.orientation,
        sensorConfig.parameters,
        sensorConfig.outputFormat
      );
    }

    // Validate sensor configuration
    const validation = sensorConfig.validate();
    if (!validation.isValid) {
      throw new Error(`Invalid sensor configuration: ${validation.errors.join(', ')}`);
    }

    // Add sensor to the system
    this.sensors.set(sensorConfig.id, sensorConfig);

    // Associate sensor with robot
    if (!this.attachedSensors.has(robotId)) {
      this.attachedSensors.set(robotId, []);
    }
    this.attachedSensors.get(robotId).push(sensorConfig.id);

    // Initialize data buffer for this sensor
    this.sensorDataBuffer.set(sensorConfig.id, []);

    console.log(`Sensor ${sensorConfig.name} (${sensorConfig.id}) attached to robot ${robotId}`);
    return sensorConfig.id;
  }

  // Remove a sensor from a robot
  removeSensorFromRobot(robotId, sensorId) {
    if (!this.attachedSensors.has(robotId)) {
      throw new Error(`No sensors attached to robot ${robotId}`);
    }

    const robotSensors = this.attachedSensors.get(robotId);
    const sensorIndex = robotSensors.indexOf(sensorId);

    if (sensorIndex === -1) {
      throw new Error(`Sensor ${sensorId} not found on robot ${robotId}`);
    }

    // Remove from robot's sensor list
    robotSensors.splice(sensorIndex, 1);

    // Remove from system
    this.sensors.delete(sensorId);
    this.sensorDataBuffer.delete(sensorId);

    console.log(`Sensor ${sensorId} removed from robot ${robotId}`);
  }

  // Get all sensors attached to a robot
  getSensorsForRobot(robotId) {
    if (!this.attachedSensors.has(robotId)) {
      return [];
    }

    const sensorIds = this.attachedSensors.get(robotId);
    return sensorIds.map(id => this.sensors.get(id));
  }

  // Generate sensor data for a specific sensor type
  generateSensorData(robot, sensorType) {
    const sensorData = {
      timestamp: Date.now(),
      sensorType: sensorType,
      robotId: robot.id
    };

    switch (sensorType) {
      case 'LiDAR':
        return this.generateLidarData(robot, sensorData);
      case 'Depth Camera':
        return this.generateDepthCameraData(robot, sensorData);
      case 'IMU':
        return this.generateImuData(robot, sensorData);
      default:
        throw new Error(`Unsupported sensor type: ${sensorType}`);
    }
  }

  // Generate LiDAR data
  generateLidarData(robot, baseData) {
    // Simulate LiDAR data based on robot position and environment
    // In a real implementation, this would raycast into the environment
    const lidarData = {
      ...baseData,
      type: 'LiDAR',
      ranges: [], // Array of distance measurements
      intensities: [], // Array of intensity values
      angle_min: -Math.PI / 2, // -90 degrees
      angle_max: Math.PI / 2,  // 90 degrees
      angle_increment: Math.PI / 360, // 0.5 degree increments
      range_min: 0.1,
      range_max: 10.0
    };

    // Generate simulated range data (simplified)
    const numRays = 360; // Half circle for 180 degree FOV
    for (let i = 0; i < numRays; i++) {
      // In a real simulation, this would be based on actual environment
      // For now, simulate some obstacles at various distances
      const distance = 2.0 + Math.sin(i * Math.PI / 180) * 1.5 + Math.random() * 0.5;
      lidarData.ranges.push(distance);
      lidarData.intensities.push(100 + Math.random() * 50); // Simulated intensity
    }

    return lidarData;
  }

  // Generate Depth Camera data
  generateDepthCameraData(robot, baseData) {
    // Simulate depth camera data
    const cameraData = {
      ...baseData,
      type: 'Depth Camera',
      width: 640,
      height: 480,
      depth_image: [], // Simulated depth data
      rgb_image: [],  // Simulated RGB data
      field_of_view: 60, // degrees
      format: 'R8G8B8'
    };

    // Generate simulated depth data (simplified)
    const totalPixels = cameraData.width * cameraData.height;
    for (let i = 0; i < totalPixels; i++) {
      // Simulate depth values based on distance from robot to objects in environment
      const depth = 1.0 + Math.random() * 9.0; // Distance from 1m to 10m
      cameraData.depth_image.push(depth);
    }

    // Generate simulated RGB data
    for (let i = 0; i < totalPixels; i++) {
      cameraData.rgb_image.push({
        r: Math.floor(Math.random() * 255),
        g: Math.floor(Math.random() * 255),
        b: Math.floor(Math.random() * 255)
      });
    }

    return cameraData;
  }

  // Generate IMU data
  generateImuData(robot, baseData) {
    // Simulate IMU data based on robot's movement and orientation
    const imuData = {
      ...baseData,
      type: 'IMU',
      orientation: {
        x: robot.orientation ? robot.orientation.x || 0 : 0,
        y: robot.orientation ? robot.orientation.y || 0 : 0,
        z: robot.orientation ? robot.orientation.z || 0 : 0,
        w: robot.orientation ? robot.orientation.w || 1 : 1
      },
      angular_velocity: {
        x: (Math.random() - 0.5) * 0.1, // Small random angular velocity
        y: (Math.random() - 0.5) * 0.1,
        z: (Math.random() - 0.5) * 0.1
      },
      linear_acceleration: {
        x: (Math.random() - 0.5) * 2.0, // Random linear acceleration
        y: (Math.random() - 0.5) * 2.0,
        z: 9.8 + (Math.random() - 0.5) // Gravity + small variation
      },
      magnetic_field: {
        x: 0.2 + (Math.random() - 0.5) * 0.05,
        y: 0.0 + (Math.random() - 0.5) * 0.05,
        z: 0.4 + (Math.random() - 0.5) * 0.05
      }
    };

    return imuData;
  }

  // Process sensor data for all sensors on a robot
  processSensorDataForRobot(robot) {
    if (!this.attachedSensors.has(robot.id)) {
      return {}; // No sensors attached to this robot
    }

    const robotSensorData = {};
    const sensorIds = this.attachedSensors.get(robot.id);

    for (const sensorId of sensorIds) {
      const sensor = this.sensors.get(sensorId);
      if (sensor) {
        const data = this.generateSensorData(robot, sensor.type);
        robotSensorData[sensorId] = data;

        // Add to buffer
        if (!this.sensorDataBuffer.has(sensorId)) {
          this.sensorDataBuffer.set(sensorId, []);
        }
        const buffer = this.sensorDataBuffer.get(sensorId);
        buffer.push(data);

        // Limit buffer size
        if (buffer.length > 100) { // Keep last 100 readings
          buffer.shift();
        }
      }
    }

    return robotSensorData;
  }

  // Get recent sensor data for a specific sensor
  getRecentSensorData(sensorId, count = 1) {
    if (!this.sensorDataBuffer.has(sensorId)) {
      return [];
    }

    const buffer = this.sensorDataBuffer.get(sensorId);
    if (count >= buffer.length) {
      return [...buffer];
    }

    return buffer.slice(-count);
  }

  // Get sensor by ID
  getSensor(sensorId) {
    return this.sensors.get(sensorId);
  }

  // Start sensor data collection
  start() {
    this.isRunning = true;
    console.log('Sensor integration service started');
  }

  // Stop sensor data collection
  stop() {
    this.isRunning = false;
    console.log('Sensor integration service stopped');
  }

  // Get sensor statistics
  getSensorStats() {
    const stats = {
      totalSensors: this.sensors.size,
      attachedSensors: 0,
      robotCount: this.attachedSensors.size,
      sensorTypes: {}
    };

    // Count sensor types
    for (const sensor of this.sensors.values()) {
      if (!stats.sensorTypes[sensor.type]) {
        stats.sensorTypes[sensor.type] = 0;
      }
      stats.sensorTypes[sensor.type]++;
    }

    // Count attached sensors
    for (const sensorIds of this.attachedSensors.values()) {
      stats.attachedSensors += sensorIds.length;
    }

    return stats;
  }

  // Simulate sensor failure
  simulateSensorFailure(sensorId) {
    if (!this.sensors.has(sensorId)) {
      throw new Error(`Sensor ${sensorId} not found`);
    }

    // In a real implementation, this would affect the sensor's data output
    console.log(`Simulating failure for sensor ${sensorId}`);
    return true;
  }

  // Reset a sensor to working state
  resetSensor(sensorId) {
    if (!this.sensors.has(sensorId)) {
      throw new Error(`Sensor ${sensorId} not found`);
    }

    // In a real implementation, this would restore the sensor's functionality
    console.log(`Resetting sensor ${sensorId}`);
    return true;
  }
}

module.exports = SensorIntegrationService;