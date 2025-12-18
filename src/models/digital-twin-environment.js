/**
 * Digital Twin Environment Model
 * Represents the combined Gazebo-Unity simulation system that provides physics and visualization capabilities
 */

class DigitalTwinEnvironment {
  constructor(name, description, physicsParameters = {}, components = []) {
    this.name = name;
    this.description = description;
    this.physicsParameters = physicsParameters; // gravity, friction, damping settings
    this.components = components; // list of robot and sensor models in the environment
    this.createdAt = new Date();
    this.updatedAt = new Date();
  }

  // Add a component to the environment
  addComponent(component) {
    this.components.push(component);
    this.updatedAt = new Date();
  }

  // Remove a component from the environment
  removeComponent(componentId) {
    this.components = this.components.filter(comp => comp.id !== componentId);
    this.updatedAt = new Date();
  }

  // Update physics parameters
  updatePhysicsParameters(newParameters) {
    this.physicsParameters = { ...this.physicsParameters, ...newParameters };
    this.updatedAt = new Date();
  }

  // Validate the environment configuration
  validate() {
    const errors = [];

    if (!this.name || typeof this.name !== 'string') {
      errors.push('Name is required and must be a string');
    }

    if (!this.description || typeof this.description !== 'string') {
      errors.push('Description is required and must be a string');
    }

    if (!this.physicsParameters || typeof this.physicsParameters !== 'object') {
      errors.push('Physics parameters must be an object');
    }

    if (!Array.isArray(this.components)) {
      errors.push('Components must be an array');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  // Get environment state
  getState() {
    return {
      name: this.name,
      description: this.description,
      physicsParameters: this.physicsParameters,
      components: this.components,
      createdAt: this.createdAt,
      updatedAt: this.updatedAt
    };
  }
}

module.exports = DigitalTwinEnvironment;