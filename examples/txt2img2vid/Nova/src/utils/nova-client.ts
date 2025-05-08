import { BedrockRuntimeClient, InvokeModelCommand } from '@aws-sdk/client-bedrock-runtime';
import * as fs from 'fs';
import * as path from 'path';
import { NovaResponse, SystemMessage, ContentType, InferenceConfig, Message } from '../types/nova.types';
import dotenv from 'dotenv';

dotenv.config();

// Define interface for Bedrock API request body
interface BedrockRequestBody {
  messages: Message[];
  inferenceConfig: {
    maxTokens?: number;
    temperature?: number;
    topP?: number;
    topK?: number;
    stopSequences?: string[];
  };
  system?: SystemMessage[];
  [key: string]: any; // Allow for additional properties
}

export class NovaClient {
  private client: BedrockRuntimeClient;
  private modelId: string;
  private lastResponse: NovaResponse | null = null;

  constructor(modelId?: string) {
    this.client = new BedrockRuntimeClient({
      region: process.env.AWS_REGION || 'us-east-1',
    });
    // Make sure to use the correct model ID format
    // For Nova, model IDs should include the region prefix if necessary
    this.modelId = modelId || process.env.NOVA_MODEL_ID || 'amazon.nova-pro-v1:0';
  }

  /**
   * Process a local video file
   * @param videoPath Path to the local video file
   * @param prompt The prompt to send with the video
   * @param systemMessages Optional system messages
   * @param inferenceConfig Optional inference configuration
   * @returns The model response
   */
  public async processLocalVideo(
    videoPath: string,
    prompt: string,
    systemMessages?: SystemMessage[],
    inferenceConfig?: InferenceConfig
  ): Promise<NovaResponse> {
    try {
      // Extract format from file extension and ensure it's one of the supported formats
      const rawFormat = path.extname(videoPath).slice(1).toLowerCase();
      const supportedFormats = ["mkv", "mov", "mp4", "webm", "three_gp", "flv", "mpeg", "mpg", "wmv"];
      const videoFormat = supportedFormats.includes(rawFormat) ? rawFormat : "mp4"; // Default to mp4 if not supported
      
      console.log(`Video format: ${videoFormat}`);
      
      // Check file size before attempting to read
      const stats = fs.statSync(videoPath);
      const fileSizeInMB = stats.size / (1024 * 1024);
      console.log(`Video file size: ${fileSizeInMB.toFixed(2)} MB`);
      
      // Warn if file is large - might hit API limits
      if (fileSizeInMB > 25) {
        console.warn(`WARNING: Video file is ${fileSizeInMB.toFixed(2)} MB, which may exceed API limits. Consider reducing the file size.`);
      }
      
      // Read video file as binary data and encode as base64
      const videoBuffer = fs.readFileSync(videoPath);
      const videoBase64 = videoBuffer.toString('base64');

      // Following the format from the JavaScript SDK v3 examples, detailed schema refer to https://docs.aws.amazon.com/nova/latest/userguide/complete-request-schema.html
      const requestBody: BedrockRequestBody = {
        messages: [
          {
            role: 'user',
            content: [
              {
                video: {
                  format: videoFormat,
                  source: {
                    bytes: videoBase64
                  }
                }
              },
              {
                text: prompt
              }
            ]
          }
        ],
        inferenceConfig: {
          maxTokens: inferenceConfig?.maxTokens || 300
        }
      };

      // Add system messages if provided
      if (systemMessages && systemMessages.length > 0) {
        requestBody.system = systemMessages;
      }
      
      console.log(`Invoking model: ${this.modelId}`);
      console.log(`Request structure: ${Object.keys(requestBody).join(', ')}`);
      
      // Log the full request body structure (without the actual video bytes for brevity)
      const logRequestBody = JSON.parse(JSON.stringify(requestBody)); // Deep clone
      if (logRequestBody.messages && logRequestBody.messages[0]?.content) {
        const videoContent = logRequestBody.messages[0].content.find((c: any) => 'video' in c);
        if (videoContent && 'video' in videoContent && videoContent.video.source.bytes) {
          videoContent.video.source.bytes = `[Base64 encoded video - ${(videoBase64.length / 1024 / 1024).toFixed(2)}MB]`;
        }
      }
      console.log('Full request body:', JSON.stringify(logRequestBody, null, 2));
      
      // Validate the request structure
      if (!requestBody.messages || !Array.isArray(requestBody.messages) || requestBody.messages.length === 0) {
        throw new Error('Invalid request: messages array is required and must not be empty');
      }
      
      if (requestBody.messages[0].role !== 'user') {
        throw new Error('Invalid request: first message must have role "user"');
      }
      
      // Format matches JavaScript SDK v3 examples for Bedrock
      const command = new InvokeModelCommand({
        modelId: this.modelId,
        contentType: "application/json",
        accept: "application/json",
        body: JSON.stringify(requestBody)
      });

      const response = await this.client.send(command);
      const responseBody = JSON.parse(
        new TextDecoder().decode(response.body)
      ) as NovaResponse;
      
      // Store the last response
      this.lastResponse = responseBody;
      
      return responseBody;
    } catch (error) {
      console.error('Error processing local video:', error);
      throw error;
    }
  }

  /**
   * Process a video from an S3 bucket
   * @param s3Uri S3 URI of the video file (s3://bucket-name/object-key)
   * @param format Video format (e.g., 'mp4')
   * @param prompt The prompt to send with the video
   * @param bucketOwner Optional bucket owner account ID
   * @param systemMessages Optional system messages
   * @param inferenceConfig Optional inference configuration
   * @returns The model response
   */
  public async processS3Video(
    s3Uri: string,
    format: string,
    prompt: string,
    bucketOwner?: string,
    systemMessages?: SystemMessage[],
    inferenceConfig?: InferenceConfig
  ): Promise<NovaResponse> {
    try {
      // Validate format is one of the supported formats
      const supportedFormats = ["mkv", "mov", "mp4", "webm", "three_gp", "flv", "mpeg", "mpg", "wmv"];
      const videoFormat = supportedFormats.includes(format) ? format : "mp4"; // Default to mp4 if not supported
      
      console.log(`Video format: ${videoFormat}`);
      
      // Following the format from the JavaScript SDK v3 examples
      const requestBody: BedrockRequestBody = {
        messages: [
          {
            role: 'user',
            content: [
              {
                video: {
                  format: videoFormat,
                  source: {
                    s3Location: {
                      uri: s3Uri,
                      ...(bucketOwner && { bucketOwner })
                    }
                  }
                }
              },
              {
                text: prompt
              }
            ]
          }
        ],
        inferenceConfig: {
          maxTokens: inferenceConfig?.maxTokens || 300
        }
      };

      // Add system messages if provided
      if (systemMessages && systemMessages.length > 0) {
        requestBody.system = systemMessages;
      }
      
      console.log(`Invoking model: ${this.modelId}`);
      
      const command = new InvokeModelCommand({
        modelId: this.modelId,
        contentType: "application/json",
        accept: "application/json",
        body: JSON.stringify(requestBody)
      });

      const response = await this.client.send(command);
      const responseBody = JSON.parse(
        new TextDecoder().decode(response.body)
      ) as NovaResponse;
      
      return responseBody;
    } catch (error) {
      console.error('Error processing S3 video:', error);
      throw error;
    }
  }

  /**
   * Process a local image file
   * @param imagePath Path to the local image file
   * @param prompt The prompt to send with the image
   * @param systemMessages Optional system messages
   * @param inferenceConfig Optional inference configuration
   * @returns The model response
   */
  public async processLocalImage(
    imagePath: string,
    prompt: string,
    systemMessages?: SystemMessage[],
    inferenceConfig?: InferenceConfig
  ): Promise<NovaResponse> {
    try {
      // Check file size before attempting to read
      const stats = fs.statSync(imagePath);
      const fileSizeInMB = stats.size / (1024 * 1024);
      console.log(`Image file size: ${fileSizeInMB.toFixed(2)} MB`);
      
      // Warn if file is large - might hit API limits
      if (fileSizeInMB > 5) {
        console.warn(`WARNING: Image file is ${fileSizeInMB.toFixed(2)} MB, which may exceed API limits. Consider reducing the file size.`);
      }
      
      // Read image file as binary data and encode as base64
      const imageBuffer = fs.readFileSync(imagePath);
      const imageBase64 = imageBuffer.toString('base64');
      
      // Get image format from file extension
      const imageFormat = path.extname(imagePath).slice(1).toLowerCase();
      const supportedFormats = ["jpeg", "jpg", "png", "gif", "webp"];
      const format = supportedFormats.includes(imageFormat) ? imageFormat : "jpeg"; // Default to jpeg if not supported
      
      console.log(`Image format: ${format}`);

      // Following the format from the JavaScript SDK v3 examples
      const requestBody: BedrockRequestBody = {
        messages: [
          {
            role: 'user',
            content: [
              {
                image: {
                  format: format,
                  source: {
                    bytes: imageBase64
                  }
                }
              },
              {
                text: prompt
              }
            ]
          }
        ],
        inferenceConfig: {
          maxTokens: inferenceConfig?.maxTokens || 300
        }
      };

      // Add system messages if provided
      if (systemMessages && systemMessages.length > 0) {
        requestBody.system = systemMessages;
      }
      
      console.log(`Invoking model: ${this.modelId}`);
      console.log(`Request structure: ${Object.keys(requestBody).join(', ')}`);
      
      // Log the full request body structure (without the actual image bytes for brevity)
      const logRequestBody = JSON.parse(JSON.stringify(requestBody)); // Deep clone
      if (logRequestBody.messages && logRequestBody.messages[0]?.content) {
        const imageContent = logRequestBody.messages[0].content.find((c: any) => 'image' in c);
        if (imageContent && 'image' in imageContent && imageContent.image.source.bytes) {
          imageContent.image.source.bytes = `[Base64 encoded image - ${(imageBase64.length / 1024 / 1024).toFixed(2)}MB]`;
        }
      }
      console.log('Full request body:', JSON.stringify(logRequestBody, null, 2));
      
      // Format matches JavaScript SDK v3 examples for Bedrock
      const command = new InvokeModelCommand({
        modelId: this.modelId,
        contentType: "application/json",
        accept: "application/json",
        body: JSON.stringify(requestBody)
      });

      const response = await this.client.send(command);
      const responseBody = JSON.parse(
        new TextDecoder().decode(response.body)
      ) as NovaResponse;
      
      // Store the last response
      this.lastResponse = responseBody;
      
      return responseBody;
    } catch (error) {
      console.error('Error processing local image:', error);
      throw error;
    }
  }

  /**
   * Extract the text content from the response
   * @param response The model response
   * @returns The extracted text
   */
  public extractTextFromResponse(response: NovaResponse): string {
    const textContent = response.output.message.content.find(
      (item) => 'text' in item
    ) as { text: string } | undefined;

    return textContent?.text || '';
  }
  
  /**
   * Get the last response from the model
   * @returns The last response or null if no response has been received
   */
  public getLastResponse(): NovaResponse | null {
    return this.lastResponse;
  }
} 