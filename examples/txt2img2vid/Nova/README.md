# Amazon Nova API TypeScript Integration

This project demonstrates how to use the Amazon Nova API for video understanding and analysis through AWS Bedrock using TypeScript, focusing on backend development without a web frontend.

## Setup Instructions

1. Clone this repository
2. Install dependencies: `npm install`
3. Configure your AWS credentials by either:
   - Setting environment variables (`AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`)
   - Using AWS CLI: `aws configure`
   - Creating a `.env` file based on `.env.example`

## Configuration

Create a `.env` file in the root directory with the following content:

```
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
```

Ensure that your AWS account has access to Amazon Bedrock and the Nova model.

## ⚠️ CRITICAL: Video Size Requirements

Nova API has **strict requirements** for video processing:

- **Maximum size: 25MB (base64) or 1GB (S3 URI)** - The API will reject larger files with validation errors
- **Recommended: 2-3MB** - Very small, short clips work best
- **Duration: 3-8 seconds** - Keep videos extremely short
- **Resolution: 480p or 720p** - Higher resolutions increase file size without benefit
- **Content: Simple and clear** - Videos with clear subjects and minimal motion work best

For detailed guidance on creating small videos, see [media/README.md](media/README.md).

## Examples

### Processing a Local Video

```typescript
import { NovaClient } from '../utils/nova-client';
import fs from 'fs';
import path from 'path';

async function main() {
  const videoPath = path.join(__dirname, '../../media/your-small-video.mp4');
  
  // Create Nova client with Lite model
  const novaClient = new NovaClient({
    modelId: 'amazon.nova-pro-v1:0',
    region: process.env.AWS_REGION || 'us-east-1',
  });
  
  // Process video with prompt
  const result = await novaClient.processLocalVideo({
    videoPath,
    prompt: "Describe what's happening in this video in detail."
  });
  
  console.log('Video Analysis Result:', result);
}

main().catch(console.error);
```

Run the example:

```bash
npm run example:local-video
```

### Processing Multiple Videos

This example processes all video files in the `media` directory:

```bash
npm run example:batch
```

## Available Models

There are two Nova models available:

1. **Nova Lite**: `amazon.nova-pro-v1:0`
   - Faster processing
   - Lower cost
   - Suitable for basic descriptions

2. **Nova Pro**: `amazon.nova-v1:0`
   - More detailed analysis
   - Higher cost
   - Better for complex video understanding

## API Reference

### NovaClient

```typescript
// Initialize the client
const novaClient = new NovaClient({
  modelId: 'amazon.nova-pro-v1:0', // or 'amazon.nova-v1:0' for Pro
  region: 'us-east-1'
});

// Process a local video file
const result = await novaClient.processLocalVideo({
  videoPath: '/path/to/small-video.mp4',
  prompt: 'Describe this video',
  systemPrompt: 'You are an assistant that describes videos accurately'
});

// Process a video from S3
const s3Result = await novaClient.processS3Video({
  s3Uri: 's3://your-bucket/your-video.mp4',
  prompt: 'Describe this video'
});
```

## Troubleshooting

If you encounter errors:

1. **ValidationException: Malformed input request**
   - Ensure your video is under 25MB (base64)
   - Try using an even smaller or shorter video (2-3MB)
   - Verify your AWS credentials have Bedrock access
   - Ensure your request follows the correct schema (no `schemaVersion` field)
   - Verify the video format is one of the supported formats: "mkv", "mov", "mp4", "webm", "three_gp", "flv", "mpeg", "mpg", "wmv"

2. **AccessDeniedException**
   - Verify your AWS account has Bedrock API access
   - Ensure you've requested access to Nova models
   - Check your IAM permissions

3. **ThrottlingException**
   - Implement exponential backoff in your requests
   - Contact AWS to increase your rate limits

## License

MIT

## Resources

- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Nova Model Information](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-nova.html)
- [AWS SDK for JavaScript v3 Documentation](https://docs.aws.amazon.com/AWSJavaScriptSDK/v3/latest/) 