/**
 * Simple Test Example for Nova API
 * 
 * This example provides a minimal working example for testing the Nova API integration.
 * It uses the Nova Lite model with a small embedded video string for quick validation.
 */

import { NovaClient } from '../utils/nova-client';
import * as fs from 'fs';
import * as path from 'path';
import { SystemMessage } from '../types/nova.types';

async function main() {
  try {
    console.log('🧪 Running Nova API Simple Test Example');
    console.log('---------------------------------------');
    
    // Create a Nova client with the Lite model
    const novaClient = new NovaClient('amazon.nova-pro-v1:0'); // Using lite model for faster/cheaper processing
    
    // Check if we have a test video in the media directory
    const testVideoPath = path.join(__dirname, '../../media/test.mp4');
    
    if (!fs.existsSync(testVideoPath)) {
      console.log('⚠️ No test.mp4 found in media directory.');
      console.log('Creating a placeholder test video file for demonstration purposes...');
      
      // Path to create the placeholder file
      const placeholderFile = path.join(__dirname, '../../media/placeholder.txt');
      fs.writeFileSync(placeholderFile, 'This is a placeholder for test.mp4.\n\nPlease create a very small (1-3MB) video file named test.mp4 in the media directory.');
      
      console.log('📝 Created placeholder.txt. Please create a test.mp4 file that is very small (1-3MB).');
      return;
    }
    
    // Get file stats
    const stats = fs.statSync(testVideoPath);
    const fileSizeMB = stats.size / (1024 * 1024);
    
    console.log(`📊 Test Video Details:`);
    console.log(`  - Path: ${testVideoPath}`);
    console.log(`  - Size: ${fileSizeMB.toFixed(2)} MB`);
    
    if (fileSizeMB > 25) {
      console.error('❌ ERROR: Video is larger than 25MB (base64). Please use a smaller video for testing.');
      console.log('Recommended size: 1-3MB, duration: 3-5 seconds.');
      return;
    }
    
    console.log('🔄 Processing video with Nova Lite model...');
    console.log('   This may take 15-30 seconds...');
    
    // Define system message for better results
    const systemMessages: SystemMessage[] = [
      {
        text: "You are a helpful assistant that provides concise descriptions of video content."
      }
    ];
    
    // Process the video
    const result = await novaClient.processLocalVideo(
      testVideoPath,
      "Describe what's happening in this video in one short paragraph.",
      systemMessages,
      { maxTokens: 300 }
    );
    
    console.log('\n✅ Success! Nova API Response:');
    console.log('---------------------------------------');
    console.log(result);
    console.log('---------------------------------------');
    
    // Extract just the text response
    const textResponse = novaClient.extractTextFromResponse(result);
    console.log('\n📝 Text Response:');
    console.log(textResponse);
    
    // Token usage information
    if (result && result.usage) {
      console.log(`\n📊 Token Usage:`);
      console.log(`  - Input Tokens: ${result.usage.inputTokens}`);
      console.log(`  - Output Tokens: ${result.usage.outputTokens}`);
      console.log(`  - Total Tokens: ${result.usage.totalTokens}`);
    }
    
    console.log('\n🎉 Test completed successfully!');
    console.log('You can now use the NovaClient in your application.');
    
  } catch (error) {
    console.error('❌ Error running Nova API test:');
    if (error instanceof Error) {
      console.error(`  - Error: ${error.message}`);
      console.error(`  - Stack: ${error.stack}`);
      
      // Provide troubleshooting guidance based on error message
      if (error.message.includes('ValidationException')) {
        console.log('\n🔍 Troubleshooting Suggestions:');
        console.log('  1. Ensure your video is very small (under 25MB (base64), ideally 1-3MB)');
        console.log('  2. Try a shorter video (3-5 seconds)');
        console.log('  3. Verify your AWS credentials and region are correct');
        console.log('  4. Ensure you have access to the Nova models in AWS Bedrock');
      } else if (error.message.includes('AccessDeniedException')) {
        console.log('\n🔍 Troubleshooting Suggestions:');
        console.log('  1. Verify you have requested access to Nova models in AWS Bedrock');
        console.log('  2. Check your IAM permissions for Bedrock');
        console.log('  3. Ensure your AWS credentials are correct');
      }
    } else {
      console.error(error);
    }
  }
}

// Run the example
main(); 