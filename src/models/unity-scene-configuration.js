/**
 * Unity Scene Configuration Model
 * Represents configuration for Unity scenes including objects, lighting, and interaction elements
 */

class UnitySceneConfiguration {
  constructor(
    name = '',
    description = '',
    objects = [],
    lighting = {},
    cameraSettings = {},
    interactionElements = []
  ) {
    this.id = this.generateId();
    this.name = name;
    this.description = description;
    this.objects = objects; // list of objects in the scene
    this.lighting = lighting; // lighting configuration
    this.cameraSettings = cameraSettings; // camera position, angle, etc.
    this.interactionElements = interactionElements; // interactive elements for human-robot interaction
    this.createdAt = new Date();
    this.updatedAt = new Date();
  }

  // Generate a unique ID for the scene
  generateId() {
    return 'scene_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }

  // Add an object to the scene
  addObject(object) {
    this.objects.push(object);
    this.updatedAt = new Date();
  }

  // Remove an object from the scene
  removeObject(objectId) {
    this.objects = this.objects.filter(obj => obj.id !== objectId);
    this.updatedAt = new Date();
  }

  // Add an interaction element to the scene
  addInteractionElement(element) {
    this.interactionElements.push(element);
    this.updatedAt = new Date();
  }

  // Remove an interaction element from the scene
  removeInteractionElement(elementId) {
    this.interactionElements = this.interactionElements.filter(el => el.id !== elementId);
    this.updatedAt = new Date();
  }

  // Update lighting configuration
  updateLighting(newLighting) {
    this.lighting = { ...this.lighting, ...newLighting };
    this.updatedAt = new Date();
  }

  // Update camera settings
  updateCameraSettings(newCameraSettings) {
    this.cameraSettings = { ...this.cameraSettings, ...newCameraSettings };
    this.updatedAt = new Date();
  }

  // Validate the scene configuration
  validate() {
    const errors = [];

    if (!this.name || typeof this.name !== 'string') {
      errors.push('Name is required and must be a string');
    }

    if (!this.description || typeof this.description !== 'string') {
      errors.push('Description is required and must be a string');
    }

    if (!Array.isArray(this.objects)) {
      errors.push('Objects must be an array');
    }

    if (!this.lighting || typeof this.lighting !== 'object') {
      errors.push('Lighting must be an object');
    }

    if (!this.cameraSettings || typeof this.cameraSettings !== 'object') {
      errors.push('Camera settings must be an object');
    }

    if (!Array.isArray(this.interactionElements)) {
      errors.push('Interaction elements must be an array');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  // Get scene configuration state
  getState() {
    return {
      id: this.id,
      name: this.name,
      description: this.description,
      objects: this.objects,
      lighting: this.lighting,
      cameraSettings: this.cameraSettings,
      interactionElements: this.interactionElements,
      createdAt: this.createdAt,
      updatedAt: this.updatedAt
    };
  }
}

module.exports = UnitySceneConfiguration;