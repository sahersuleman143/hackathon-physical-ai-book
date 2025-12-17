# Quickstart: Setting up Docusaurus for ROS 2 Documentation

**Feature**: 001-ros2-foundation
**Date**: 2025-12-16

## Prerequisites

- Node.js v18+ installed
- npm or yarn package manager
- Git for version control

## Setup Steps

### 1. Install Docusaurus
```bash
npm init docusaurus@latest docs-website classic
```

### 2. Navigate to project directory
```bash
cd docs-website
```

### 3. Install additional dependencies (if needed)
```bash
npm install
```

### 4. Create module directory structure
```bash
mkdir -p docs/module-1
```

### 5. Create chapter files
```bash
touch docs/module-1/intro-to-ros2.md
touch docs/module-1/rclpy-agent-integration.md
touch docs/module-1/urdf-humanoid-modeling.md
```

### 6. Update sidebar configuration
Edit `sidebars.js` to include the new chapters:

```javascript
module.exports = {
  docs: [
    {
      type: 'category',
      label: 'Module 1: The Robotic Nervous System (ROS 2)',
      items: [
        'module-1/intro-to-ros2',
        'module-1/rclpy-agent-integration',
        'module-1/urdf-humanoid-modeling',
      ],
    },
  ],
};
```

### 7. Start development server
```bash
npm start
```

## Configuration for GitHub Pages

### Update docusaurus.config.js
```javascript
module.exports = {
  // ...
  url: 'https://your-username.github.io',
  baseUrl: '/your-repo-name/',
  projectName: 'your-repo-name',
  organizationName: 'your-username',
  deploymentBranch: 'gh-pages',
  // ...
};
```

## Deployment

### Build static files
```bash
npm run build
```

### Deploy to GitHub Pages
```bash
npm run deploy
```