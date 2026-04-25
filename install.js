#!/usr/bin/env node

const { spawn } = require('cross-spawn');
const which = require('which');

async function install() {
  console.log('🚀 Setting up SentinelCI...');
  
  try {
    // Check if Python is available
    const pythonCmd = await findPython();
    if (!pythonCmd) {
      console.error('❌ Error: Python 3.11+ is required but not found.');
      console.error('📥 Please install Python from https://python.org/downloads/');
      console.error('');
      console.error('After installing Python, run:');
      console.error('  npm install sentinelci');
      process.exit(1);
    }

    console.log(`✅ Found Python: ${pythonCmd}`);
    
    // Check Python version
    const versionResult = spawn.sync(pythonCmd, ['--version'], { stdio: 'pipe' });
    if (versionResult.status === 0) {
      const version = versionResult.stdout.toString().trim();
      console.log(`✅ Python version: ${version}`);
    }

    console.log('📦 Installing SentinelCI Python package...');
    
    // Install the Python package
    const installResult = spawn.sync(pythonCmd, ['-m', 'pip', 'install', 'sentinelci'], { 
      stdio: 'inherit' 
    });
    
    if (installResult.status !== 0) {
      console.error('❌ Failed to install SentinelCI Python package.');
      console.error('');
      console.error('Please try manually:');
      console.error('  pip install sentinelci');
      process.exit(1);
    }

    console.log('');
    console.log('🎉 SentinelCI installed successfully!');
    console.log('');
    console.log('Quick start:');
    console.log('  npx sentinelci onboard    # Setup wizard');
    console.log('  npx sentinelci scan       # Scan current directory');
    console.log('  npx sentinelci --help     # Show all commands');
    console.log('');

  } catch (error) {
    console.error('❌ Installation failed:', error.message);
    process.exit(1);
  }
}

async function findPython() {
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

if (require.main === module) {
  install();
}