// @ts-check
// `@type` JSDoc annotations allow IDEs and type-checking tools to autocomplete and validate

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Physical AI Book',
  tagline: 'Bridging AI and Robotics',
  favicon: 'img/favicon.ico',

  // Production URL
  url: 'https://sahersuleman143.github.io',

  // GitHub Pages project base path
  baseUrl: '/hackathon-physical-ai-book/',

  // GitHub deployment config
  organizationName: 'sahersuleman143',
  projectName: 'hackathon-physical-ai-book',

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl:
            'https://github.com/sahersuleman143/hackathon-physical-ai-book/tree/main/',
        },
        blog: false,
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      image: 'img/social-card.png',
      navbar: {
        title: 'Physical AI Book',
        logo: {
          alt: 'Physical AI Book Logo',
          src: 'img/logo.jpeg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'Module 1: ROS 2 Foundation',
          },
          {
            href: 'https://github.com/sahersuleman143/hackathon-physical-ai-book',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Docs',
            items: [
              {
                label: 'Module 1: ROS 2 Foundation',
                to: '/docs/module-1/intro-to-ros2',
              },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'Stack Overflow',
                href: 'https://stackoverflow.com/questions/tagged/docusaurus',
              },
              {
                label: 'Discord',
                href: 'https://discordapp.com/invite/docusaurus',
              },
              {
                label: 'Twitter',
                href: 'https://twitter.com/docusaurus',
              },
            ],
          },
          {
            title: 'More',
            items: [
              {
                label: 'GitHub',
                href: 'https://github.com/sahersuleman143/hackathon-physical-ai-book',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Physical AI Book.`,
      },
      prism: {
        theme: require('prism-react-renderer').themes.github,
        darkTheme: require('prism-react-renderer').themes.dracula,
      },
    }),
};

module.exports = config;

