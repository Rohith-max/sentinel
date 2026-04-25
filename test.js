#!/usr/bin/env node

const SentinelCI = require('./index');

async function test() {
  console.log('🧪 Testing SentinelCI NPM wrapper...');
  
  try {
    const sci = new SentinelCI();
    
    console.log('✅ SentinelCI class created');
    
    // Test Python detection
    await sci.init();
    console.log('✅ Python detection works');
    
    // Test version command
    console.log('📋 Testing version command...');
    await sci.version();
    
    console.log('🎉 All tests passed!');
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  test();
}