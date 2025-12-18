// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    // Intro page
    'intro',

    // Module 1: ROS 2 Foundation
    {
      type: 'category',
      label: 'Module 1: ROS 2 Foundation',
      items: [
        'module-1/intro-to-ros2',
        'module-1/rclpy-agent-integration',
        'module-1/urdf-humanoid-modeling',
      ],
    },

    // Module 2: Digital Twin
    {
      type: 'category',
      label: 'Module 2: Digital Twin',
      items: [
        'digital-twin/intro',
        'digital-twin/simulating-sensors',
        'digital-twin/unity-interaction',
      ],
    },

    // Module 3: AI-Robot Brain
    {
      type: 'category',
      label: 'Module 3: AI-Robot Brain',
      items: [
        'module-3/isaac-sim',
        'module-3/isaac-ros',
        'module-3/nav2',
      ],
    },

    // Module 4: Vision-Language-Action
    {
      type: 'category',
      label: 'Module 4: Vision-Language-Action',
      items: [
        'modules/vla-integration/chapter-1-voice-to-action/intro',
        'modules/vla-integration/chapter-1-voice-to-action/basic_workflow',
        'modules/vla-integration/chapter-1-voice-to-action/voice_capture',
        'modules/vla-integration/chapter-1-voice-to-action/voice_processor',
        'modules/vla-integration/chapter-1-voice-to-action/whisper-integration',
        'modules/vla-integration/chapter-1-voice-to-action/whisper_pipeline',
        'modules/vla-integration/chapter-1-voice-to-action/speech-processing-examples',
        
      ],
    },
  ],
};

module.exports = sidebars;
