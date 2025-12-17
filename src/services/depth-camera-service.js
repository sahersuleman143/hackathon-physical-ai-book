/**
 * Depth Camera Service
 * Handles the generation and processing of depth camera sensor data for 3D perception
 */

class DepthCameraService {
  constructor() {
    this.imageHistory = [];
    this.maxHistorySize = 10; // Number of images to keep in history
    this.cameraParams = {
      width: 640,        // Image width in pixels
      height: 480,       // Image height in pixels
      fov: 60,           // Field of view in degrees
      near: 0.1,         // Near clipping plane (meters)
      far: 10.0,         // Far clipping plane (meters)
      format: 'R8G8B8'   // Color format
    };
  }

  // Generate a depth camera image based on the robot's environment
  generateDepthImage(robotPosition, environment) {
    const image = {
      timestamp: Date.now(),
      frame_id: 'camera_frame',
      width: this.cameraParams.width,
      height: this.cameraParams.height,
      format: this.cameraParams.format,
      rgb_data: this.generateRGBData(robotPosition, environment),
      depth_data: this.generateDepthData(robotPosition, environment),
      camera_info: {
        width: this.cameraParams.width,
        height: this.cameraParams.height,
        intrinsic_matrix: this.computeIntrinsicMatrix(),
        distortion_coefficients: [0, 0, 0, 0, 0] // No distortion for simulation
      }
    };

    // Add to history
    this.imageHistory.push(image);
    if (this.imageHistory.length > this.maxHistorySize) {
      this.imageHistory.shift();
    }

    return image;
  }

  // Generate RGB image data
  generateRGBData(robotPosition, environment) {
    // Create a simulated RGB image array
    const pixelCount = this.cameraParams.width * this.cameraParams.height;
    const rgbData = new Array(pixelCount);

    // For simulation, we'll create a simple pattern
    for (let i = 0; i < pixelCount; i++) {
      // Create a gradient based on position
      const row = Math.floor(i / this.cameraParams.width);
      const col = i % this.cameraParams.width;

      // Simple pattern: blue sky, green ground, red obstacles
      if (row < this.cameraParams.height * 0.4) {
        // Sky region
        rgbData[i] = {
          r: 135,  // Sky blue
          g: 206,
          b: 235
        };
      } else {
        // Ground region
        rgbData[i] = {
          r: 34,   // Green ground
          g: 139,
          b: 34
        };
      }

      // Add some random obstacles based on environment
      if (this.isPixelObstacle(row, col, robotPosition, environment)) {
        rgbData[i] = {
          r: 255,  // Red obstacle
          g: 0,
          b: 0
        };
      }
    }

    return rgbData;
  }

  // Generate depth data
  generateDepthData(robotPosition, environment) {
    // Create a simulated depth image array
    const pixelCount = this.cameraParams.width * this.cameraParams.height;
    const depthData = new Array(pixelCount);

    for (let i = 0; i < pixelCount; i++) {
      const row = Math.floor(i / this.cameraParams.width);
      const col = i % this.cameraParams.width;

      // Calculate depth based on position in the image and environment
      const depth = this.calculateDepthForPixel(row, col, robotPosition, environment);

      // Add some noise to simulate real sensor behavior
      const noise = (Math.random() - 0.5) * 0.05; // ±2.5cm noise
      depthData[i] = Math.max(
        this.cameraParams.near,
        Math.min(this.cameraParams.far, depth + noise)
      );
    }

    return depthData;
  }

  // Check if a pixel should represent an obstacle
  isPixelObstacle(row, col, robotPosition, environment) {
    // In a real implementation, this would perform 3D raycasting
    // For simulation, we'll create a simple check

    // Get the direction vector for this pixel
    const direction = this.pixelToDirection(row, col);

    // Check if there's an obstacle in this direction
    if (environment.obstacles) {
      for (const obstacle of environment.obstacles) {
        // Simple check based on angular position
        const obstacleDir = {
          x: obstacle.position.x - robotPosition.x,
          y: obstacle.position.y - robotPosition.y
        };

        // Normalize direction vectors
        const obstacleDist = Math.sqrt(obstacleDir.x * obstacleDir.x + obstacleDir.y * obstacleDir.y);
        if (obstacleDist > 0) {
          obstacleDir.x /= obstacleDist;
          obstacleDir.y /= obstacleDist;
        }

        // Calculate angle between camera direction and obstacle direction
        const dotProduct = direction.x * obstacleDir.x + direction.y * obstacleDir.y;
        const angle = Math.acos(Math.max(-1, Math.min(1, dotProduct)));

        // If the angle is small enough, consider it an obstacle in the pixel
        if (angle < 0.1 && obstacleDist < 5.0) { // 0.1 radians ~ 5.7 degrees
          return true;
        }
      }
    }

    return false;
  }

  // Calculate depth for a specific pixel
  calculateDepthForPixel(row, col, robotPosition, environment) {
    // Convert pixel coordinates to a 3D ray direction
    const direction = this.pixelToDirection(row, col);

    // In a real implementation, this would raycast against the 3D environment
    // For simulation, we'll return a distance based on simple geometry

    // Default distance (far plane)
    let distance = this.cameraParams.far;

    // Check for obstacles in the environment
    if (environment.obstacles) {
      for (const obstacle of environment.obstacles) {
        // Calculate distance to this obstacle in the given direction
        const obsDir = {
          x: obstacle.position.x - robotPosition.x,
          y: obstacle.position.y - robotPosition.y
        };

        const obsDistance = Math.sqrt(obsDir.x * obsDir.x + obsDir.y * obsDir.y);
        if (obsDistance < distance) {
          distance = obsDistance;
        }
      }
    }

    return distance;
  }

  // Convert pixel coordinates to a 3D direction vector
  pixelToDirection(row, col) {
    // Calculate normalized image coordinates (-1 to 1)
    const x = (col - this.cameraParams.width / 2) / (this.cameraParams.width / 2);
    const y = (row - this.cameraParams.height / 2) / (this.cameraParams.height / 2);

    // Convert to 3D direction (simplified for top-down projection)
    // In a real camera, this would use the intrinsic matrix
    const fovRad = this.cameraParams.fov * Math.PI / 180;
    const angleX = x * fovRad / 2;
    const angleY = -y * fovRad / 2; // Flip Y for image coordinates

    // Create a 3D direction vector
    const direction = {
      x: Math.sin(angleX),
      y: Math.sin(angleY),
      z: Math.cos(angleX) * Math.cos(angleY)
    };

    // Normalize the vector
    const length = Math.sqrt(direction.x * direction.x + direction.y * direction.y + direction.z * direction.z);
    if (length > 0) {
      direction.x /= length;
      direction.y /= length;
      direction.z /= length;
    }

    return direction;
  }

  // Compute the camera intrinsic matrix
  computeIntrinsicMatrix() {
    const fx = (this.cameraParams.width / 2) / Math.tan((this.cameraParams.fov * Math.PI / 180) / 2);
    const fy = fx; // Assume square pixels
    const cx = this.cameraParams.width / 2;
    const cy = this.cameraParams.height / 2;

    return [fx, 0, cx, 0, fy, cy, 0, 0, 1]; // 3x3 matrix as array
  }

  // Process depth data for 3D point cloud
  createPointCloud(depthImage) {
    const points = [];
    const intrinsic = depthImage.camera_info.intrinsic_matrix;

    // Extract intrinsic matrix values
    const fx = intrinsic[0];
    const fy = intrinsic[3];
    const cx = intrinsic[2];
    const cy = intrinsic[5];

    for (let y = 0; y < depthImage.height; y++) {
      for (let x = 0; x < depthImage.width; x++) {
        const idx = y * depthImage.width + x;
        const depth = depthImage.depth_data[idx];

        // Skip invalid depth values
        if (depth <= depthImage.camera_info.near || depth >= depthImage.camera_info.far) {
          continue;
        }

        // Convert pixel coordinates to 3D world coordinates
        const worldX = (x - cx) * depth / fx;
        const worldY = (y - cy) * depth / fy;
        const worldZ = depth;

        // Get RGB color for this point
        const color = depthImage.rgb_data[idx];

        points.push({
          x: worldX,
          y: worldY,
          z: worldZ,
          r: color ? color.r : 255,
          g: color ? color.g : 255,
          b: color ? color.b : 255
        });
      }
    }

    return points;
  }

  // Get object segmentation from depth image
  segmentObjects(depthImage, minDepth = 0.5, maxDepth = 5.0) {
    const segments = [];
    const validPoints = [];

    // Collect all valid points within depth range
    for (let i = 0; i < depthImage.depth_data.length; i++) {
      const depth = depthImage.depth_data[i];
      if (depth >= minDepth && depth <= maxDepth) {
        const row = Math.floor(i / depthImage.width);
        const col = i % depthImage.width;
        validPoints.push({ x: col, y: row, depth: depth, idx: i });
      }
    }

    // Simple clustering of nearby points to form segments
    while (validPoints.length > 0) {
      const seedPoint = validPoints.shift();
      const segment = [seedPoint];

      // Find nearby points to group together
      for (let i = validPoints.length - 1; i >= 0; i--) {
        const point = validPoints[i];
        const dist = Math.sqrt(
          Math.pow(point.x - seedPoint.x, 2) +
          Math.pow(point.y - seedPoint.y, 2)
        );

        if (dist < 20) { // Group pixels within 20 pixels
          segment.push(point);
          validPoints.splice(i, 1);
        }
      }

      if (segment.length > 10) { // Only consider segments with more than 10 points
        segments.push(segment);
      }
    }

    return segments;
  }

  // Get recent image history
  getImageHistory(count = 5) {
    if (count >= this.imageHistory.length) {
      return [...this.imageHistory];
    }
    return this.imageHistory.slice(-count);
  }

  // Process depth data for navigation
  processForNavigation(depthImage) {
    const navigationData = {
      timestamp: depthImage.timestamp,
      obstaclePoints: this.extractObstaclePoints(depthImage),
      groundPoints: this.extractGroundPoints(depthImage),
      freeSpacePoints: this.extractFreeSpacePoints(depthImage),
      depthStats: this.calculateDepthStats(depthImage)
    };

    return navigationData;
  }

  // Extract obstacle points from depth data
  extractObstaclePoints(depthImage, threshold = 2.0) {
    const points = [];

    for (let i = 0; i < depthImage.depth_data.length; i++) {
      const depth = depthImage.depth_data[i];
      if (depth > depthImage.camera_info.near && depth < threshold) {
        const row = Math.floor(i / depthImage.width);
        const col = i % depthImage.width;

        points.push({
          x: col,
          y: row,
          depth: depth,
          color: depthImage.rgb_data[i]
        });
      }
    }

    return points;
  }

  // Extract ground points from depth data
  extractGroundPoints(depthImage) {
    const points = [];
    // For simulation, assume ground is in the lower half of the image
    const groundStartRow = Math.floor(depthImage.height * 0.6);

    for (let i = 0; i < depthImage.depth_data.length; i++) {
      const row = Math.floor(i / depthImage.width);
      if (row >= groundStartRow) {
        const depth = depthImage.depth_data[i];
        if (depth > depthImage.camera_info.near && depth < depthImage.camera_info.far) {
          const col = i % depthImage.width;

          points.push({
            x: col,
            y: row,
            depth: depth,
            color: depthImage.rgb_data[i]
          });
        }
      }
    }

    return points;
  }

  // Extract free space points from depth data
  extractFreeSpacePoints(depthImage, threshold = 3.0) {
    const points = [];

    for (let i = 0; i < depthImage.depth_data.length; i++) {
      const depth = depthImage.depth_data[i];
      if (depth > threshold && depth < depthImage.camera_info.far) {
        const row = Math.floor(i / depthImage.width);
        const col = i % depthImage.width;

        points.push({
          x: col,
          y: row,
          depth: depth,
          color: depthImage.rgb_data[i]
        });
      }
    }

    return points;
  }

  // Calculate depth statistics
  calculateDepthStats(depthImage) {
    let sum = 0;
    let count = 0;
    let min = Infinity;
    let max = -Infinity;

    for (const depth of depthImage.depth_data) {
      if (depth > depthImage.camera_info.near && depth < depthImage.camera_info.far) {
        sum += depth;
        count++;
        min = Math.min(min, depth);
        max = Math.max(max, depth);
      }
    }

    return {
      average: count > 0 ? sum / count : 0,
      min: isFinite(min) ? min : 0,
      max: isFinite(max) ? max : 0,
      count: count
    };
  }

  // Set camera parameters
  setParameters(params) {
    this.cameraParams = { ...this.cameraParams, ...params };
  }

  // Get current camera parameters
  getParameters() {
    return { ...this.cameraParams };
  }

  // Simulate camera noise
  addNoise(depthImage, noiseLevel = 0.05) {
    const noisyImage = { ...depthImage };
    noisyImage.depth_data = depthImage.depth_data.map(depth => {
      if (depth > depthImage.camera_info.near && depth < depthImage.camera_info.far) {
        const noise = (Math.random() - 0.5) * noiseLevel;
        return Math.max(
          depthImage.camera_info.near,
          Math.min(depthImage.camera_info.far, depth + noise)
        );
      }
      return depth;
    });

    return noisyImage;
  }
}

module.exports = DepthCameraService;