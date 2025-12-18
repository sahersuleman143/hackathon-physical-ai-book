/**
 * LiDAR Service
 * Handles the generation and processing of LiDAR sensor data for navigation and mapping
 */

class LidarService {
  constructor() {
    this.scanHistory = [];
    this.maxHistorySize = 50; // Number of scans to keep in history
    this.laserParams = {
      rangeMin: 0.1,      // Minimum range (meters)
      rangeMax: 10.0,     // Maximum range (meters)
      fov: Math.PI,       // Field of view (radians) - 180 degrees
      resolution: 0.5,    // Angular resolution in degrees
      samples: 361        // Number of samples (for 180 degrees at 0.5 degree resolution)
    };
  }

  // Generate a LiDAR scan based on the robot's environment
  generateLidarScan(robotPosition, environment) {
    const scan = {
      timestamp: Date.now(),
      frame_id: 'lidar_frame',
      angle_min: -this.laserParams.fov / 2,
      angle_max: this.laserParams.fov / 2,
      angle_increment: this.laserParams.fov / (this.laserParams.samples - 1),
      time_increment: 0.0,
      scan_time: 0.1, // 10Hz
      range_min: this.laserParams.rangeMin,
      range_max: this.laserParams.rangeMax,
      ranges: [],
      intensities: []
    };

    // Generate range data for each angle
    for (let i = 0; i < this.laserParams.samples; i++) {
      const angle = scan.angle_min + i * scan.angle_increment;
      const range = this.simulateDistance(robotPosition, angle, environment);

      scan.ranges.push(range);
      // Simulate intensity based on distance and surface properties
      const intensity = this.calculateIntensity(range);
      scan.intensities.push(intensity);
    }

    // Add to history
    this.scanHistory.push(scan);
    if (this.scanHistory.length > this.maxHistorySize) {
      this.scanHistory.shift();
    }

    return scan;
  }

  // Simulate distance measurement using raycasting
  simulateDistance(robotPosition, angle, environment) {
    // In a real implementation, this would perform raycasting against the environment
    // For simulation purposes, we'll create a simplified environment model

    // Create a simplified model of the environment
    const obstacles = environment.obstacles || [
      { position: { x: 2, y: 0, z: 0 }, size: 0.5 },
      { position: { x: -1, y: 1, z: 0 }, size: 0.5 },
      { position: { x: 0, y: -2, z: 0 }, size: 0.5 }
    ];

    // Calculate ray direction
    const rayDir = {
      x: Math.cos(angle),
      y: Math.sin(angle)
    };

    let minDistance = this.laserParams.rangeMax;

    // Check for intersections with obstacles
    for (const obstacle of obstacles) {
      const distance = this.calculateDistanceToObstacle(
        robotPosition,
        rayDir,
        obstacle
      );

      if (distance > 0 && distance < minDistance) {
        minDistance = distance;
      }
    }

    // Add some noise to simulate real sensor behavior
    const noise = (Math.random() - 0.5) * 0.05; // ±2.5cm noise
    return Math.max(this.laserParams.rangeMin, Math.min(this.laserParams.rangeMax, minDistance + noise));
  }

  // Calculate distance from robot to an obstacle
  calculateDistanceToObstacle(robotPos, rayDir, obstacle) {
    // Simplified distance calculation for a circular/spherical obstacle
    const dx = obstacle.position.x - robotPos.x;
    const dy = obstacle.position.y - robotPos.y;

    // Distance from robot to obstacle center
    const centerDistance = Math.sqrt(dx * dx + dy * dy);

    // Distance to obstacle surface
    const surfaceDistance = centerDistance - obstacle.size;

    // Check if the ray actually hits the obstacle
    const angleToObstacle = Math.atan2(dy, dx);
    const angleDiff = Math.abs(angleToObstacle - Math.atan2(rayDir.y, rayDir.x));

    // If the ray is pointing roughly toward the obstacle
    if (angleDiff < Math.PI / 4 || angleDiff > 7 * Math.PI / 4) {
      return surfaceDistance;
    }

    return -1; // No hit
  }

  // Calculate simulated intensity value
  calculateIntensity(range) {
    // In real LiDAR, intensity depends on surface properties and distance
    // For simulation, use a simple model based on distance
    const maxIntensity = 255;
    const baseIntensity = maxIntensity * 0.7; // Base intensity

    // Intensity decreases with distance (simplified inverse square law)
    const distanceFactor = Math.max(0.1, 1 - (range / this.laserParams.rangeMax));

    // Add some variation
    const variation = 0.9 + Math.random() * 0.2; // 90-110% of calculated value

    return Math.floor(baseIntensity * distanceFactor * variation);
  }

  // Process LiDAR data for navigation
  processForNavigation(lidarData) {
    // Extract features useful for navigation
    const navigationData = {
      timestamp: lidarData.timestamp,
      obstacleDistances: this.extractObstacleDistances(lidarData),
      freeSpaceAngles: this.findFreeSpaceDirections(lidarData),
      closestObstacle: this.findClosestObstacle(lidarData),
      navigationClearance: this.calculateNavigationClearance(lidarData)
    };

    return navigationData;
  }

  // Extract obstacle distances from LiDAR data
  extractObstacleDistances(lidarData) {
    const obstacles = [];
    const threshold = 2.0; // Consider anything closer than 2m as an obstacle

    for (let i = 0; i < lidarData.ranges.length; i++) {
      const range = lidarData.ranges[i];
      if (range > lidarData.range_min && range < threshold) {
        obstacles.push({
          angle: lidarData.angle_min + i * lidarData.angle_increment,
          distance: range,
          intensity: lidarData.intensities[i]
        });
      }
    }

    return obstacles;
  }

  // Find directions with free space
  findFreeSpaceDirections(lidarData) {
    const freeSpace = [];
    const minDistance = 3.0; // Consider free space if > 3m

    for (let i = 0; i < lidarData.ranges.length; i++) {
      const range = lidarData.ranges[i];
      if (range > minDistance && range < lidarData.range_max) {
        freeSpace.push({
          angle: lidarData.angle_min + i * lidarData.angle_increment,
          distance: range
        });
      }
    }

    return freeSpace;
  }

  // Find the closest obstacle
  findClosestObstacle(lidarData) {
    let minDistance = lidarData.range_max;
    let closestIndex = -1;

    for (let i = 0; i < lidarData.ranges.length; i++) {
      const range = lidarData.ranges[i];
      if (range > lidarData.range_min && range < minDistance) {
        minDistance = range;
        closestIndex = i;
      }
    }

    if (closestIndex !== -1) {
      return {
        angle: lidarData.angle_min + closestIndex * lidarData.angle_increment,
        distance: minDistance,
        intensity: lidarData.intensities[closestIndex]
      };
    }

    return null;
  }

  // Calculate navigation clearance (space available for movement)
  calculateNavigationClearance(lidarData) {
    const frontSector = this.getSectorData(lidarData, -Math.PI/6, Math.PI/6); // Front 60 degrees
    const leftSector = this.getSectorData(lidarData, Math.PI/3, 2*Math.PI/3); // Left 60 degrees
    const rightSector = this.getSectorData(lidarData, -2*Math.PI/3, -Math.PI/3); // Right 60 degrees

    return {
      front: frontSector,
      left: leftSector,
      right: rightSector
    };
  }

  // Get data for a specific angular sector
  getSectorData(lidarData, startAngle, endAngle) {
    const sectorReadings = [];

    for (let i = 0; i < lidarData.ranges.length; i++) {
      const angle = lidarData.angle_min + i * lidarData.angle_increment;

      // Normalize angles to [-π, π]
      let normalizedAngle = angle;
      while (normalizedAngle < -Math.PI) normalizedAngle += 2 * Math.PI;
      while (normalizedAngle > Math.PI) normalizedAngle -= 2 * Math.PI;

      if (normalizedAngle >= startAngle && normalizedAngle <= endAngle) {
        sectorReadings.push(lidarData.ranges[i]);
      }
    }

    if (sectorReadings.length === 0) {
      return {
        minDistance: lidarData.range_max,
        maxDistance: lidarData.range_max,
        averageDistance: lidarData.range_max
      };
    }

    const min = Math.min(...sectorReadings);
    const max = Math.max(...sectorReadings);
    const avg = sectorReadings.reduce((a, b) => a + b, 0) / sectorReadings.length;

    return {
      minDistance: min,
      maxDistance: max,
      averageDistance: avg
    };
  }

  // Get recent scan history
  getScanHistory(count = 10) {
    if (count >= this.scanHistory.length) {
      return [...this.scanHistory];
    }
    return this.scanHistory.slice(-count);
  }

  // Detect obstacles in specific region
  detectObstaclesInRegion(lidarData, centerX, centerY, radius) {
    // This method would typically be used with known robot position
    // For simulation, we'll just return a basic obstacle detection
    const obstacles = this.extractObstacleDistances(lidarData);
    return obstacles.filter(obs => obs.distance <= radius);
  }

  // Set LiDAR parameters
  setParameters(params) {
    this.laserParams = { ...this.laserParams, ...params };
    // Recalculate samples if resolution changed
    if (params.resolution || params.fov) {
      this.laserParams.samples = Math.floor(this.laserParams.fov /
        (this.laserParams.resolution * Math.PI / 180)) + 1;
    }
  }

  // Get current LiDAR parameters
  getParameters() {
    return { ...this.laserParams };
  }

  // Create a 2D map from LiDAR data (simplified)
  create2DMap(lidarData, robotPosition, resolution = 0.1) {
    // This is a very simplified approach to creating a 2D map from LiDAR data
    // In practice, this would involve sophisticated SLAM algorithms

    const map = {
      resolution: resolution,
      width: 200, // 20m map at 0.1m resolution
      height: 200,
      origin: {
        x: robotPosition.x - 10, // 10m around robot
        y: robotPosition.y - 10
      },
      data: new Array(200 * 200).fill(-1) // Initialize as unknown (-1)
    };

    // Fill in known free space and obstacles based on LiDAR readings
    for (let i = 0; i < lidarData.ranges.length; i++) {
      const angle = lidarData.angle_min + i * lidarData.angle_increment;
      const range = lidarData.ranges[i];

      if (range > lidarData.range_min && range < lidarData.range_max) {
        // Calculate position of detected obstacle
        const x = robotPosition.x + range * Math.cos(angle);
        const y = robotPosition.y + range * Math.sin(angle);

        // Convert to map coordinates
        const mapX = Math.floor((x - map.origin.x) / map.resolution);
        const mapY = Math.floor((y - map.origin.y) / map.resolution);

        if (mapX >= 0 && mapX < map.width && mapY >= 0 && mapY < map.height) {
          map.data[mapY * map.width + mapX] = 100; // Obstacle (100% occupancy)
        }

        // Mark path as free space
        this.markFreeSpaceOnMap(map, robotPosition, { x, y });
      }
    }

    return map;
  }

  // Mark free space along the ray from robot to detected point
  markFreeSpaceOnMap(map, robotPos, targetPos) {
    const dx = targetPos.x - robotPos.x;
    const dy = targetPos.y - robotPos.y;
    const distance = Math.sqrt(dx * dx + dy * dy);
    const steps = Math.floor(distance / map.resolution);

    for (let i = 0; i < steps; i++) {
      const x = robotPos.x + (dx * i) / steps;
      const y = robotPos.y + (dy * i) / steps;

      const mapX = Math.floor((x - map.origin.x) / map.resolution);
      const mapY = Math.floor((y - map.origin.y) / map.resolution);

      if (mapX >= 0 && mapX < map.width && mapY >= 0 && mapY < map.height) {
        if (map.data[mapY * map.width + mapX] === -1) {
          map.data[mapY * map.width + mapX] = 0; // Mark as free space
        }
      }
    }
  }
}

module.exports = LidarService;