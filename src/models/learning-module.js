/**
 * Learning Module Model
 * Represents structured educational content including theory, examples, and hands-on exercises
 */

class LearningModule {
  constructor(
    title = '',
    description = '',
    prerequisites = [],
    learningObjectives = [],
    steps = [],
    resources = [],
    assessment = {}
  ) {
    this.id = this.generateId();
    this.title = title;
    this.description = description;
    this.prerequisites = prerequisites; // knowledge or skills required
    this.learningObjectives = learningObjectives; // specific outcomes students should achieve
    this.steps = steps; // sequence of activities
    this.resources = resources; // files, links, or materials needed
    this.assessment = assessment; // criteria for evaluating success
    this.createdAt = new Date();
    this.updatedAt = new Date();
    this.isCompleted = false;
  }

  // Generate a unique ID for the learning module
  generateId() {
    return 'module_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }

  // Add a prerequisite
  addPrerequisite(prerequisite) {
    this.prerequisites.push(prerequisite);
    this.updatedAt = new Date();
  }

  // Add a learning objective
  addLearningObjective(objective) {
    this.learningObjectives.push(objective);
    this.updatedAt = new Date();
  }

  // Add a step to the module
  addStep(step) {
    this.steps.push(step);
    this.updatedAt = new Date();
  }

  // Add a resource to the module
  addResource(resource) {
    this.resources.push(resource);
    this.updatedAt = new Date();
  }

  // Update assessment criteria
  updateAssessment(newAssessment) {
    this.assessment = { ...this.assessment, ...newAssessment };
    this.updatedAt = new Date();
  }

  // Mark the module as completed
  markCompleted() {
    this.isCompleted = true;
    this.updatedAt = new Date();
  }

  // Validate the learning module
  validate() {
    const errors = [];

    if (!this.title || typeof this.title !== 'string') {
      errors.push('Title is required and must be a string');
    }

    if (!this.description || typeof this.description !== 'string') {
      errors.push('Description is required and must be a string');
    }

    if (!Array.isArray(this.prerequisites)) {
      errors.push('Prerequisites must be an array');
    }

    if (!Array.isArray(this.learningObjectives)) {
      errors.push('Learning objectives must be an array');
    }

    if (!Array.isArray(this.steps)) {
      errors.push('Steps must be an array');
    }

    if (!Array.isArray(this.resources)) {
      errors.push('Resources must be an array');
    }

    if (!this.assessment || typeof this.assessment !== 'object') {
      errors.push('Assessment must be an object');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  // Get learning module state
  getState() {
    return {
      id: this.id,
      title: this.title,
      description: this.description,
      prerequisites: this.prerequisites,
      learningObjectives: this.learningObjectives,
      steps: this.steps,
      resources: this.resources,
      assessment: this.assessment,
      isCompleted: this.isCompleted,
      createdAt: this.createdAt,
      updatedAt: this.updatedAt
    };
  }
}

module.exports = LearningModule;