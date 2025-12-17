// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    // Intro page (docs/intro.md)
    'intro',

    {
      type: 'category',
      label: 'Module 1: ROS 2 Foundation',
      items: [
        'module-1/intro-to-ros2',
        'module-1/rclpy-agent-integration',
        'module-1/urdf-humanoid-modeling',
      ],
    },

    {
      type: 'category',
      label: 'Module 2: Digital Twin',
      items: [
        'digital-twin/intro',
        'digital-twin/simulating-sensors',
        'digital-twin/unity-interaction',
      ],
    },

    {
      type: 'category',
      label: 'Module 3: AI-Robot Brain',
      items: [
        'module-3/isaac-sim',
        'module-3/isaac-ros',
        'module-3/nav2',
      ],
    },
  ],
};

module.exports = sidebars;
