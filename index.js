/**
 * SentinelCI - AI-Powered Security Scanning and Autonomous Remediation Platform
 * 
 * This is an NPM wrapper for the Python-based SentinelCI package.
 * It automatically installs and manages the Python dependency.
 */

const { spawn } = require('cross-spawn');
const which = require('which');

class SentinelCI {
  constructor() {
    this.pythonCmd = null;
  }

  async init() {
    this.pythonCmd = await this.findPython();
    if (!this.pythonCmd) {
      throw new Error('Python 3.11+ is required but not found');
    }
    
    // Ensure sentinelci is installed
    await this.ensureInstalled();
  }

  async findPython() {
    const candidates = ['python3', 'python', 'py'];
    
    for (const cmd of candidates) {
      try {
        await which(cmd);
        const result = spawn.sync(cmd, ['--version'], { stdio: 'pipe' });
        
        if (result.status === 0) {
          const version = result.stdout.toString().trim();
          const match = version.match(/Python (\d+)\.(\d+)/);
          
          if (match) {
            const major = parseInt(match[1]);
            const minor = parseInt(match[2]);
            
            if (major === 3 && minor >= 11) {
              return cmd;
            }
          }
        }
      } catch (error) {
        // Continue to next candidate
      }
    }
    
    return null;
  }

  async ensureInstalled() {
    const result = spawn.sync(this.pythonCmd, ['-c', 'import sentinelci'], { stdio: 'pipe' });
    
    if (result.status !== 0) {
      console.log('Installing SentinelCI Python package...');
      const installResult = spawn.sync(this.pythonCmd, ['-m', 'pip', 'install', 'sentinelci'], { 
        stdio: 'inherit' 
      });
      
      if (installResult.status !== 0) {
        throw new Error('Failed to install SentinelCI Python package');
      }
    }
  }

  async run(args = []) {
    if (!this.pythonCmd) {
      await this.init();
    }

    return new Promise((resolve, reject) => {
      const child = spawn(this.pythonCmd, ['-m', 'sentinelci.cli'].concat(args), { 
        stdio: 'inherit' 
      });

      child.on('exit', (code) => {
        resolve(code || 0);
      });

      child.on('error', (error) => {
        reject(error);
      });
    });
  }

  async scan(options = {}) {
    const args = ['scan'];
    
    if (options.path) args.push('--path', options.path);
    if (options.severity) args.push('--severity', options.severity);
    if (options.format) args.push('--format', options.format);
    if (options.output) args.push('--output', options.output);
    if (options.diff) args.push('--diff');
    if (options.watch) args.push('--watch');
    
    return this.run(args);
  }

  async onboard() {
    return this.run(['onboard']);
  }

  async version() {
    return this.run(['version']);
  }
}

module.exports = SentinelCI;