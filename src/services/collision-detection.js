/**
 * Collision Detection Service
 * Handles detection and response for collisions between objects in the simulation
 */

class CollisionDetectionService {
  constructor() {
    this.collisionPairs = new Set(); // Track pairs of objects that have collided
    this.collisionHistory = []; // Track collision history
    this.maxHistorySize = 1000; // Maximum number of collisions to keep in history
  }

  // Detect collision between two objects using bounding box method
  detectCollision(obj1, obj2) {
    if (!obj1.position || !obj2.position) {
      return false;
    }

    // Get bounding box dimensions for each object
    const obj1Bounds = this.getBoundingBox(obj1);
    const obj2Bounds = this.getBoundingBox(obj2);

    // Check for bounding box collision
    const collision = this.checkBoundingBoxCollision(
      obj1.position, obj1Bounds,
      obj2.position, obj2Bounds
    );

    if (collision) {
      // Record the collision if it's a new pair
      const pairId = this.getCollisionPairId(obj1, obj2);
      if (!this.collisionPairs.has(pairId)) {
        this.collisionPairs.add(pairId);
        this.recordCollision(obj1, obj2);
      }
    } else {
      // Remove the pair from active collisions if they're no longer colliding
      const pairId = this.getCollisionPairId(obj1, obj2);
      this.collisionPairs.delete(pairId);
    }

    return collision;
  }

  // Get bounding box dimensions for an object
  getBoundingBox(obj) {
    // Default bounding box if not specified
    if (!obj.physicalProperties || !obj.physicalProperties.dimensions) {
      return { width: 0.1, height: 0.1, depth: 0.1 };
    }

    const dims = obj.physicalProperties.dimensions;
    return {
      width: dims.x || dims.width || 0.1,
      height: dims.y || dims.height || 0.1,
      depth: dims.z || dims.depth || 0.1
    };
  }

  // Check collision using axis-aligned bounding box (AABB) method
  checkBoundingBoxCollision(pos1, bounds1, pos2, bounds2) {
    // Calculate half-dimensions for each object
    const half1 = {
      x: bounds1.width / 2,
      y: bounds1.height / 2,
      z: bounds1.depth / 2
    };

    const half2 = {
      x: bounds2.width / 2,
      y: bounds2.height / 2,
      z: bounds2.depth / 2
    };

    // Calculate positions of bounding box centers
    const center1 = { x: pos1.x, y: pos1.y, z: pos1.z };
    const center2 = { x: pos2.x, y: pos2.y, z: pos2.z };

    // Check for overlap on each axis
    const xOverlap = Math.abs(center1.x - center2.x) < (half1.x + half2.x);
    const yOverlap = Math.abs(center1.y - center2.y) < (half1.y + half2.y);
    const zOverlap = Math.abs(center1.z - center2.z) < (half1.z + half2.z);

    return xOverlap && yOverlap && zOverlap;
  }

  // Get a unique ID for a collision pair to avoid duplicate collision detection
  getCollisionPairId(obj1, obj2) {
    // Use IDs if available, otherwise use positions as a fallback
    const id1 = obj1.id || `${obj1.position.x},${obj1.position.y},${obj1.position.z}`;
    const id2 = obj2.id || `${obj2.position.x},${obj2.position.y},${obj2.position.z}`;

    // Create a consistent pair ID regardless of object order
    return id1 < id2 ? `${id1}-${id2}` : `${id2}-${id1}`;
  }

  // Record collision in history
  recordCollision(obj1, obj2) {
    const collision = {
      timestamp: Date.now(),
      object1: { id: obj1.id, name: obj1.name },
      object2: { id: obj2.id, name: obj2.name },
      position: {
        x: (obj1.position.x + obj2.position.x) / 2,
        y: (obj1.position.y + obj2.position.y) / 2,
        z: (obj1.position.z + obj2.position.z) / 2
      }
    };

    this.collisionHistory.push(collision);

    // Limit history size
    if (this.collisionHistory.length > this.maxHistorySize) {
      this.collisionHistory.shift();
    }
  }

  // Detect collisions between all objects in a list
  detectCollisionsInEnvironment(objects) {
    const collisions = [];

    for (let i = 0; i < objects.length; i++) {
      for (let j = i + 1; j < objects.length; j++) {
        if (this.detectCollision(objects[i], objects[j])) {
          collisions.push({
            object1: objects[i],
            object2: objects[j],
            timestamp: Date.now()
          });
        }
      }
    }

    return collisions;
  }

  // Get collision history
  getCollisionHistory() {
    return [...this.collisionHistory]; // Return a copy to prevent external modification
  }

  // Get the number of active collisions
  getActiveCollisionsCount() {
    return this.collisionPairs.size;
  }

  // Clear collision history
  clearHistory() {
    this.collisionHistory = [];
    this.collisionPairs.clear();
  }

  // Calculate collision response (simplified)
  calculateCollisionResponse(obj1, obj2, collisionNormal = { x: 0, y: 0, z: 1 }) {
    // This is a simplified collision response calculation
    // In a real implementation, this would use more sophisticated physics

    // Calculate relative velocity
    const relVelocity = {
      x: obj2.velocity.x - obj1.velocity.x,
      y: obj2.velocity.y - obj1.velocity.y,
      z: obj2.velocity.z - obj1.velocity.z
    };

    // Calculate velocity along normal
    const velAlongNormal = relVelocity.x * collisionNormal.x +
                          relVelocity.y * collisionNormal.y +
                          relVelocity.z * collisionNormal.z;

    // Don't resolve if objects are moving apart
    if (velAlongNormal > 0) {
      return { obj1: obj1, obj2: obj2 };
    }

    // Calculate restitution (bounciness)
    const restitution = Math.min(obj1.physicalProperties.restitution || 0.5,
                                obj2.physicalProperties.restitution || 0.5);

    // Calculate impulse scalar
    const impulse = -(1 + restitution) * velAlongNormal;
    const impulseScalar = impulse / (obj1.physicalProperties.mass + obj2.physicalProperties.mass);

    // Apply impulse
    const impulseVector = {
      x: impulseScalar * collisionNormal.x,
      y: impulseScalar * collisionNormal.y,
      z: impulseScalar * collisionNormal.z
    };

    // Update velocities
    if (obj1.physicalProperties.mass > 0) {
      obj1.velocity.x += impulseVector.x / obj1.physicalProperties.mass;
      obj1.velocity.y += impulseVector.y / obj1.physicalProperties.mass;
      obj1.velocity.z += impulseVector.z / obj1.physicalProperties.mass;
    }

    if (obj2.physicalProperties.mass > 0) {
      obj2.velocity.x -= impulseVector.x / obj2.physicalProperties.mass;
      obj2.velocity.y -= impulseVector.y / obj2.physicalProperties.mass;
      obj2.velocity.z -= impulseVector.z / obj2.physicalProperties.mass;
    }

    return { obj1, obj2 };
  }
}

module.exports = CollisionDetectionService;