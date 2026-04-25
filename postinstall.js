#!/usr/bin/env node

const { spawn } = require('cross-spawn');
const which = require('which');

async function postInstall() {
  try {
    // Check if Python is available
    const pythonCmd = await findPython();
    if (!pythonCmd) {
      console.log('⚠️  Python 3.11+ not found. SentinelCI requires Python to run.');
      console.log('📥 Install Python from: https://python.org/downloads/');
      console.log('');
      console.log('After installing Python, the package will work automatically.');
      return;
    }

    // Silently check if sentinelci is already installed
    const result = spawn.sync(pythonCmd, ['-c', 'import sentinelci'], { stdio: 'pipe' });
    
    if (result.status !== 0) {
      console.log('📦 Installing SentinelCI Python package...');
      const installResult = spawn.sync(pythonCmd, ['-m', 'pip', 'install', 'sentinelci'], { 
        stdio: 'pipe' 
      });
      
      if (installResult.status === 0) {
        console.log('✅ SentinelCI ready to use!');
        console.log('');
        console.log('Try: npx sentinelci onboard');
      } else {
        console.log('⚠️  Could not auto-install Python package.');
        console.log('Please run: pip install sentinelci');
      }
    } else {
      console.log('✅ SentinelCI is ready to use!');
    }

  } catch (error) {
    // Silent failure - don't break npm install
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
  postInstall();
}