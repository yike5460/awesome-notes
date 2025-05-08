import { NovaClient } from '../utils/nova-client';

async function main() {
  try {
    // S3 URI of your video file
    const s3Uri = 's3://video-search-dev-ap-northeast-1/RawVideos/2025-04-12/0412/b93e2638-77c9-4aec-8981-b1013c272498/黑神话-神笔马良.mp4';
    const videoFormat = 'mp4';
    
    // Optional: S3 bucket owner account ID
    const bucketOwner = ''; // Replace with your bucket owner account ID
    
    // Create a new Nova client
    const novaClient = new NovaClient();
    
    // Define system messages for the model
    const systemMessages = [
      {
        text: 'You are an expert video content analyzer. Analyze the following video clip and provide a comprehensive summary.',
      },
    ];
    
    // Define the prompt to send with the video
    const prompt = 'Analyze this video and provide a summary of the key events. What is the main activity shown in the video?';
    
    // Process the video with recommended inference parameters for video understanding
    const inferenceConfig = {
      maxTokens: 400,
      temperature: 0, // Starting with temperature=0 as recommended
      topP: 0.1,
      topK: 1, // Starting with topK=1 as recommended
    };
    
    console.log('Processing S3 video...');
    const response = await novaClient.processS3Video(
      s3Uri,
      videoFormat,
      prompt,
      bucketOwner,
      systemMessages,
      inferenceConfig
    );
    
    // Extract and print the text response
    const textResponse = novaClient.extractTextFromResponse(response);
    console.log('\nModel Response:');
    console.log(textResponse);
    
    // Print usage information
    console.log('\nToken Usage:');
    console.log(`Input Tokens: ${response.usage.inputTokens}`);
    console.log(`Output Tokens: ${response.usage.outputTokens}`);
    console.log(`Total Tokens: ${response.usage.totalTokens}`);
  } catch (error) {
    console.error('Error in S3 video processing example:', error);
  }
}

// Run the example
main(); 