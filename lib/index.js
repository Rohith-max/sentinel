/**
 * SentinelCI Library
 * Programmatic API for Node.js applications
 */

const SentinelCI = require('../index');

module.exports = {
  SentinelCI,
  
  // Convenience functions
  async scan(options = {}) {
    const sci = new SentinelCI();
    return sci.scan(options);
  },

  async onboard() {
    const sci = new SentinelCI();
    return sci.onboard();
  },

  async version() {
    const sci = new SentinelCI();
    return sci.version();
  }
};