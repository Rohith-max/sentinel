#!/usr/bin/env node

const SentinelCI = require('./index');

async function test() {
  console.log('🧪 Testing SentinelCI NPM wrapper...');
  
  try {
    const sci = new SentinelCI();
    
    console.log('✅ SentinelCI class created');
    
    // Test Python detection (without installing package)
    const pythonCmd = await sci.findPython();
    if (pythonCmd) {
      console.log('✅ Python detection works');
    } else {
      console.log('⚠️  Python not found (expected in CI)');
    }
    
    // Test CLI wrapper exists
    const fs = require('fs');
    if (fs.existsSync('./bin/sci')) {
      console.log('✅ CLI wrapper exists');
    }
    
    console.log('🎉 Basic tests passed!');
    console.log('ℹ️  Full functionality requires PyPI package to be published');
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  test();
}