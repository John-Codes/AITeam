const { defineConfig } = require("cypress");
module.exports = defineConfig({
  e2e: {
    baseUrl: 'https://aiteam-app-vpvo8.ondigitalocean.app/ai-team/',
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
  },
});