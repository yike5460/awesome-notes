import { NovaClient } from '../utils/nova-client';
import path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs';
import { createCanvas, loadImage } from 'canvas';

// The maximum size of the video file to process, 25 MB for base64, and 1GB for S3 URI, refer to https://docs.aws.amazon.com/nova/latest/userguide/modalities-video.html#:~:text=The%20Amazon%20Nova%20models%20allow,S3%20URI%20for%20video%20understanding.
const MAX_RECOMMENDED_SIZE_MB = 25;

const execAsync = promisify(exec);

/**
 * Extract a frame from a video file using ffmpeg
 * @param videoPath Path to the video file
 * @param outputPath Path to save the extracted frame
 * @param frameTime Time of the frame to extract (in seconds)
 * @returns Promise that resolves when the frame is extracted
 */
async function extractFrameFromVideo(videoPath: string, outputPath: string, frameTime: number = 0): Promise<string> {
  try {
    console.log(`Extracting frame at ${frameTime}s from ${videoPath}...`);
    await execAsync(`ffmpeg -i "${videoPath}" -ss ${frameTime} -frames:v 1 -q:v 2 "${outputPath}" -y`);
    console.log(`Frame extracted and saved to ${outputPath}`);
    return outputPath;
  } catch (error) {
    console.error('Error extracting frame:', error);
    throw error;
  }
}

/**
 * Draw bounding boxes on an image using Node Canvas
 * @param imagePath Path to the input image
 * @param outputPath Path to save the output image
 * @param boundingBoxes Array of bounding boxes to draw
 * @returns Promise that resolves when the image is saved
 */
async function drawBoundingBoxes(
  imagePath: string,
  outputPath: string,
  boundingBoxes: Array<{[category: string]: number[]}>,
  imageWidth: number,
  imageHeight: number
): Promise<string> {
  try {
    console.log('Drawing bounding boxes on image...');
    
    // Load the image
    const image = await loadImage(imagePath);
    
    // Create a canvas with the same dimensions as the image
    const canvas = createCanvas(image.width, image.height);
    const ctx = canvas.getContext('2d');
    
    // Draw the image on the canvas
    ctx.drawImage(image, 0, 0);
    
    // Define a color map for common object categories
    const colorMap: {[key: string]: string} = {
      person: '#FF0000',     // Red
      car: '#00FF00',        // Green
      dog: '#0000FF',        // Blue
      cat: '#FF00FF',        // Magenta
      chair: '#FFFF00',      // Yellow
      table: '#00FFFF',      // Cyan
      building: '#FFA500',   // Orange
      tree: '#008000',       // Dark Green
      water: '#00BFFF',      // Deep Sky Blue
      bicycle: '#8B4513',    // Brown
      book: '#4B0082',       // Indigo
      bottle: '#800080',     // Purple
      bowl: '#A52A2A',       // Brown
      bus: '#556B2F',        // Dark Olive Green
      clock: '#483D8B',      // Dark Slate Blue
      cup: '#8FBC8F',        // Dark Sea Green
      door: '#2F4F4F',       // Dark Slate Gray
      keyboard: '#5F9EA0',   // Cadet Blue
      laptop: '#6495ED',     // Cornflower Blue
      monitor: '#7FFFD4',    // Aquamarine
      mouse: '#D2691E',      // Chocolate
      phone: '#DC143C',      // Crimson
      plant: '#228B22',      // Forest Green
      sofa: '#B8860B',       // Dark Goldenrod
      tv: '#4682B4',         // Steel Blue
      window: '#87CEEB',     // Sky Blue
      text: '#9932CC',       // Dark Orchid
      flower: '#FF1493',     // Deep Pink
      fruit: '#FF8C00',      // Dark Orange
      vegetable: '#32CD32',  // Lime Green
      sign: '#DAA520',       // Goldenrod
      light: '#F0E68C',      // Khaki
      fan: '#40E0D0',        // Turquoise
      umbrella: '#800000',   // Maroon
      handbag: '#9370DB',    // Medium Purple
      tie: '#191970',        // Midnight Blue
      suitcase: '#BDB76B',   // Dark Khaki
      microwave: '#CD853F',  // Peru
      oven: '#D2B48C',       // Tan
      toaster: '#BC8F8F',    // Rosy Brown
      sink: '#4169E1',       // Royal Blue
      refrigerator: '#FA8072', // Salmon
      blender: '#F08080',    // Light Coral
      notebook: '#CD5C5C',   // Indian Red
      alarm: '#B22222',      // Firebrick
      vase: '#FF6347',       // Tomato
      scissors: '#FF4500',   // Orange Red
      'teddy bear': '#DA70D6', // Orchid
      'hair drier': '#BA55D3', // Medium Orchid
      toothbrush: '#9400D3', // Dark Violet
      necklace: '#8A2BE2',   // Blue Violet
      ring: '#9932CC',       // Dark Orchid
      bracelet: '#8B008B',   // Dark Magenta
      earrings: '#800080',   // Purple
      watch: '#4B0082',      // Indigo
      machine: '#483D8B',    // Dark Slate Blue
      piano: '#6A5ACD',      // Slate Blue
      guitar: '#7B68EE',     // Medium Slate Blue
      drum: '#6495ED',       // Cornflower Blue
      violin: '#4169E1',     // Royal Blue
      flute: '#1E90FF',      // Dodger Blue
      bridge: '#00BFFF',     // Deep Sky Blue
      road: '#87CEEB',       // Sky Blue
      mountain: '#B0C4DE',   // Light Steel Blue
      river: '#ADD8E6',      // Light Blue
      lake: '#B0E0E6',       // Powder Blue
      ocean: '#5F9EA0',      // Cadet Blue
      beach: '#F0FFFF',      // Azure
      forest: '#7CFC00',     // Lawn Green
      field: '#7FFF00',      // Chartreuse
      grass: '#ADFF2F',      // Green Yellow
      vehicle: '#006400',    // Dark Green
    };
    
    /**
     * Generate a color based on the string (for categories not in the color map)
     * This ensures each category gets a unique but consistent color
     */
    function generateColorFromString(str: string): string {
      // Simple hash function to generate a number from a string
      let hash = 0;
      for (let i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
      }
      
      // Convert the hash to a color
      let color = '#';
      for (let i = 0; i < 3; i++) {
        // Get a value between 0-255 for each RGB component
        // Ensure colors are not too dark (< 50) or too light (> 200)
        const value = ((hash >> (i * 8)) & 0xFF);
        const adjustedValue = Math.max(50, Math.min(200, value));
        color += adjustedValue.toString(16).padStart(2, '0');
      }
      
      return color;
    }
    
    // Draw each bounding box
    boundingBoxes.forEach(box => {
      const category = Object.keys(box)[0];
      const [x1, y1, x2, y2] = box[category];
      
      // Calculate the width and height of the rectangle
      const width = x2 - x1;
      const height = y2 - y1;
      
      // Get color for this category or generate one
      const color = colorMap[category.toLowerCase()] || generateColorFromString(category);
      
      // Draw the rectangle
      ctx.strokeStyle = color;
      ctx.lineWidth = 3;
      ctx.strokeRect(x1, y1, width, height);
      
      // Draw the label with background for better visibility
      const labelText = category;
      const fontSize = 16;
      ctx.font = `${fontSize}px Arial`;
      const textMetrics = ctx.measureText(labelText);
      const textWidth = textMetrics.width;
      const textHeight = fontSize;
      
      // Draw background for text
      ctx.fillStyle = color;
      ctx.fillRect(x1, y1 > textHeight ? y1 - textHeight : y1, textWidth + 6, textHeight + 2);
      
      // Draw the label
      ctx.fillStyle = 'white';
      ctx.fillText(labelText, x1 + 3, y1 > textHeight ? y1 - 3 : y1 + textHeight - 1);
    });
    
    // Add a legend to the image
    const uniqueCategories = new Set<string>();
    boundingBoxes.forEach(box => {
      const category = Object.keys(box)[0];
      uniqueCategories.add(category);
    });
    
    if (uniqueCategories.size > 0) {
      // Draw legend background
      const legendPadding = 10;
      const legendItemHeight = 25;
      const legendWidth = 150;
      const legendHeight = (uniqueCategories.size * legendItemHeight) + (legendPadding * 2);
      
      // Position the legend in the top-right corner with some padding
      const legendX = canvas.width - legendWidth - 10;
      const legendY = 10;
      
      // Draw semi-transparent background
      ctx.fillStyle = 'rgba(0, 0, 0, 0.6)';
      ctx.fillRect(legendX, legendY, legendWidth, legendHeight);
      
      // Draw legend title
      ctx.fillStyle = 'white';
      ctx.font = 'bold 14px Arial';
      ctx.fillText('Detected Objects:', legendX + legendPadding, legendY + 20);
      
      // Draw legend items
      let itemY = legendY + 40;
      Array.from(uniqueCategories).forEach(category => {
        const color = colorMap[category.toLowerCase()] || generateColorFromString(category);
        
        // Draw color box
        ctx.fillStyle = color;
        ctx.fillRect(legendX + legendPadding, itemY - 12, 15, 15);
        
        // Draw category name
        ctx.fillStyle = 'white';
        ctx.font = '14px Arial';
        ctx.fillText(category, legendX + legendPadding + 25, itemY);
        
        itemY += legendItemHeight;
      });
    }
    
    // Save the canvas to a file
    const buffer = canvas.toBuffer('image/jpeg');
    fs.writeFileSync(outputPath, buffer);
    
    console.log(`Image with bounding boxes saved to ${outputPath}`);
    return outputPath;
  } catch (error) {
    console.error('Error drawing bounding boxes:', error);
    throw error;
  }
}

/**
 * Sleep for a specified number of milliseconds
 * @param ms Milliseconds to sleep
 * @returns Promise that resolves after the specified time
 */
function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Retry a function with exponential backoff
 * @param fn Function to retry
 * @param retries Maximum number of retries
 * @param initialDelay Initial delay in milliseconds
 * @param maxDelay Maximum delay in milliseconds
 * @returns Promise that resolves with the function result
 */
async function retryWithExponentialBackoff<T>(
  fn: () => Promise<T>,
  retries: number = 5,
  initialDelay: number = 1000,
  maxDelay: number = 60000
): Promise<T> {
  let currentDelay = initialDelay;
  let attempts = 0;
  
  while (true) {
    try {
      return await fn();
    } catch (error: any) {
      attempts++;
      
      // If we've reached the maximum number of retries, throw the error
      if (attempts >= retries) {
        throw error;
      }
      
      // Check if the error is a throttling error
      const isThrottlingError = error.toString().includes('ThrottlingException') ||
                               error.toString().includes('TooManyRequestsException') ||
                               error.toString().includes('Too many requests');
      
      // If it's not a throttling error, throw it
      if (!isThrottlingError) {
        throw error;
      }
      
      // Calculate the next delay with jitter (±20%)
      const jitter = currentDelay * (0.8 + Math.random() * 0.4);
      const nextDelay = Math.min(jitter, maxDelay);
      
      console.log(`API throttling detected. Retrying in ${(nextDelay/1000).toFixed(1)} seconds... (Attempt ${attempts} of ${retries})`);
      await sleep(nextDelay);
      
      // Exponential backoff: double the delay for the next attempt
      currentDelay = currentDelay * 2;
    }
  }
}

/**
 * Extract frames from a video at specified intervals
 * @param videoPath Path to the video file
 * @param outputDir Directory to save the extracted frames
 * @param frameCount Number of frames to extract (used if frameInterval is not provided)
 * @param frameInterval Interval between frames in seconds (takes precedence over frameCount)
 * @returns Array of paths to the extracted frames
 */
async function extractFramesFromVideo(
  videoPath: string,
  outputDir: string,
  frameCount: number = 5,
  frameInterval?: number
): Promise<string[]> {
  try {
    // Get video duration using ffprobe
    const { stdout: durationOutput } = await execAsync(`ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "${videoPath}"`);
    const duration = parseFloat(durationOutput.trim());
    console.log(`Video duration: ${duration.toFixed(2)} seconds`);
    
    // Calculate frame times based on interval or count
    let frameTimes: number[];
    
    if (frameInterval) {
      // Calculate number of frames based on interval and duration
      const calculatedFrameCount = Math.max(1, Math.floor(duration / frameInterval));
      console.log(`Extracting frames at ${frameInterval}s intervals (${calculatedFrameCount} frames total)`);
      
      // Generate frame times at regular intervals
      frameTimes = [];
      for (let time = frameInterval; time < duration; time += frameInterval) {
        frameTimes.push(time);
      }
    } else {
      // Use the specified frame count and distribute evenly
      console.log(`Extracting ${frameCount} frames evenly distributed across the video...`);
      const interval = duration / (frameCount + 1);
      frameTimes = Array.from({ length: frameCount }, (_, i) => (i + 1) * interval);
    }
    
    // Create output directory if it doesn't exist
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    // Extract frames
    const framePaths: string[] = [];
    for (let i = 0; i < frameTimes.length; i++) {
      const frameTime = frameTimes[i];
      const frameOutputPath = path.join(outputDir, `${path.basename(videoPath, path.extname(videoPath))}_frame_${i+1}.jpg`);
      await extractFrameFromVideo(videoPath, frameOutputPath, frameTime);
      framePaths.push(frameOutputPath);
    }
    
    console.log(`Extracted ${framePaths.length} frames from video`);
    return framePaths;
  } catch (error) {
    console.error('Error extracting frames from video:', error);
    throw error;
  }
}

/**
 * Process a single image frame to detect objects
 * @param imagePath Path to the image file
 * @param novaClient Nova client instance
 * @param systemMessages System messages for the model
 * @param inferenceConfig Inference configuration
 */
async function processImageFrame(
  imagePath: string,
  novaClient: NovaClient,
  systemMessages: any[],
  inferenceConfig: any
): Promise<{
  annotatedOutputPath: string;
  detectedObjects: Array<{category: string; count: number}>;
  boundingBoxes: Array<{[category: string]: number[]}>;
}> {
  console.log(`\nProcessing image frame: ${path.basename(imagePath)}`);
  
  // Define the prompt for object detection
  const prompt = `Detect bounding boxes of all objects in this image with high confidence. Output in a list of bounding box format.
Output example:
[
    {"person": [x1, y1, x2, y2]},
    {"car": [x1, y1, x2, y2]},
    {"dog": [x1, y1, x2, y2]},
    ...
]

The coordinates should be in the range [0, 1000) for both x and y axes, where (0,0) is the top-left corner and (1000,1000) is the bottom-right corner.

Result:`;

  // Process the image with the Nova API using retry logic
  const response = await retryWithExponentialBackoff(
    async () => {
      return await novaClient.processLocalImage(
        imagePath,
        prompt,
        systemMessages,
        inferenceConfig
      );
    },
    5,  // Maximum 5 retries
    2000, // Start with 2 second delay
    30000 // Maximum 30 second delay
  );
  
  // Extract and print the text response
  const textResponse = novaClient.extractTextFromResponse(response);
  console.log('\nDetection Results:');
  console.log(textResponse);
  
  // Get image dimensions
  const image = await loadImage(imagePath);
  const imageWidth = image.width;
  const imageHeight = image.height;
  console.log(`Image dimensions: ${imageWidth}x${imageHeight}`);
  
  // Parse and process the bounding boxes
  const detectedObjects: Array<{category: string; count: number}> = [];
  const annotatedOutputPath = imagePath.replace(/\.jpg$/, '_annotated.jpg');
  let scaledBoxes: Array<{[category: string]: number[]}> = [];
  
  try {
    // Try to extract and parse JSON from the response
    const jsonMatch = textResponse.match(/\[\s*\{.*\}\s*\]/s);
    if (jsonMatch) {
      const boundingBoxes = JSON.parse(jsonMatch[0]);
      console.log('\nProcessed Bounding Boxes:');
      
      // Scale the bounding boxes from [0, 1000) to actual image dimensions
      scaledBoxes = boundingBoxes.map((box: any) => {
        const category = Object.keys(box)[0];
        const [x1, y1, x2, y2] = box[category];
        
        // Count detected objects by category
        const existingCategory = detectedObjects.find(obj => obj.category === category);
        if (existingCategory) {
          existingCategory.count++;
        } else {
          detectedObjects.push({ category, count: 1 });
        }
        
        return {
          [category]: [
            Math.round(x1 * imageWidth / 1000),
            Math.round(y1 * imageHeight / 1000),
            Math.round(x2 * imageWidth / 1000),
            Math.round(y2 * imageHeight / 1000)
          ]
        };
      });
      
      console.log('Scaled to image dimensions:');
      console.log(JSON.stringify(scaledBoxes, null, 2));
      
      // Draw bounding boxes on the image
      await drawBoundingBoxes(imagePath, annotatedOutputPath, scaledBoxes, imageWidth, imageHeight);
      
      console.log(`\nBounding box visualization saved to: ${annotatedOutputPath}`);
    } else {
      console.log('No valid bounding box data found in the response.');
      // Create a copy of the frame without annotations
      fs.copyFileSync(imagePath, annotatedOutputPath);
    }
  } catch (error) {
    console.error('Error processing bounding boxes:', error);
    console.log('Raw response might not contain valid bounding box data.');
    // Create a copy of the frame without annotations
    fs.copyFileSync(imagePath, annotatedOutputPath);
  }
  
  return {
    annotatedOutputPath,
    detectedObjects,
    boundingBoxes: scaledBoxes
  };
}

async function main() {
  try {
    // Path to your local video file - use a small video file (under 25MB)
    const videoPath = path.resolve(__dirname, '../../media/短片3.mp4');
    
    console.log(`Using video file: ${videoPath}`);
    
    // Check if the video file exists
    if (!fs.existsSync(videoPath)) {
      console.error(`Error: Video file not found at ${videoPath}`);
      console.log('Please make sure the video file exists or create a small test video:');
      console.log('ffmpeg -i media/Beach.mp4 -vf "scale=320:240" -t 3 -c:v libx264 -crf 28 -c:a aac -b:a 64k media/small/Beach_small.mp4');
      return;
    }
    
    // Get file size
    const stats = fs.statSync(videoPath);
    const fileSizeInMB = stats.size / (1024 * 1024);
    console.log(`Video file size: ${fileSizeInMB.toFixed(2)} MB`);
    
    // Warn if file is too large
    if (fileSizeInMB > MAX_RECOMMENDED_SIZE_MB) {
      console.warn(`WARNING: Video file is ${fileSizeInMB.toFixed(2)} MB, which exceeds the recommended limit.`);
      console.warn('The API may reject this file. Consider using a smaller video file.');
    }
    
    // Create output directory for frames
    const frameOutputDir = path.resolve(__dirname, '../../media/frames');
    if (!fs.existsSync(frameOutputDir)) {
      fs.mkdirSync(frameOutputDir, { recursive: true });
    }
    
    // Get video duration to determine frame extraction strategy
    const { stdout: durationOutput } = await execAsync(`ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "${videoPath}"`);
    const duration = parseFloat(durationOutput.trim());
    
    // Determine frame interval based on video duration
    let frameInterval: number;
    if (duration < 10) {
      frameInterval = 1; // 1 frame per second for short videos
    } else if (duration < 60) {
      frameInterval = 5; // 1 frame every 5 seconds for medium videos
    } else {
      frameInterval = 10; // 1 frame every 10 seconds for long videos
    }
    
    console.log(`\nVideo duration: ${duration.toFixed(2)} seconds. Extracting frames every ${frameInterval} seconds...`);
    const framePaths = await extractFramesFromVideo(videoPath, frameOutputDir, undefined, frameInterval);
    
    // Create a new Nova client
    // Use Nova Pro or Premier for better object detection
    const novaClient = new NovaClient('amazon.nova-pro-v1:0');
    
    // Define system messages for the model
    const systemMessages = [
      {
        text: 'You are an expert in computer vision and object detection. When given an image, detect all visible objects with their bounding box coordinates. Identify as many different object categories as possible (people, vehicles, animals, furniture, etc.) and provide accurate bounding box coordinates for each detected object.',
      },
    ];
    
    // Process the frames with recommended inference parameters for object detection
    const inferenceConfig = {
      maxTokens: 1000,
      temperature: 0, // Keeping temperature=0 for more precise detection
      topP: 0.1,
      topK: 1, // Keeping topK=1 for more precise detection
    };
    
    const results = [];
    let totalInputTokens = 0;
    let totalOutputTokens = 0;
    
    // Process each frame with exponential backoff retry logic
    for (let i = 0; i < framePaths.length; i++) {
      try {
        const result = await processImageFrame(
          framePaths[i],
          novaClient,
          systemMessages,
          inferenceConfig
        );
        
        results.push({
          framePath: framePaths[i],
          ...result
        });
        
        // Add token usage
        const response = novaClient.getLastResponse();
        if (response) {
          totalInputTokens += response.usage.inputTokens;
          totalOutputTokens += response.usage.outputTokens;
        }
      } catch (error) {
        console.error(`Error processing frame ${i+1}:`, error);
        // Continue with next frame
      }
    }
    
    // Create a summary of all detected objects across all frames
    const objectSummary = new Map<string, number>();
    results.forEach(result => {
      result.detectedObjects.forEach((obj: {category: string; count: number}) => {
        const currentCount = objectSummary.get(obj.category) || 0;
        objectSummary.set(obj.category, currentCount + obj.count);
      });
    });
    
    // Print summary
    console.log('\n===== OBJECT DETECTION SUMMARY =====');
    console.log(`Total frames processed successfully: ${results.length} of ${framePaths.length}`);
    console.log('\nDetected objects across all frames:');
    
    if (objectSummary.size > 0) {
      // Sort categories alphabetically for better readability
      const sortedCategories = Array.from(objectSummary.entries()).sort((a, b) => a[0].localeCompare(b[0]));
      
      sortedCategories.forEach(([category, count]) => {
        console.log(`- ${category}: ${count} instance(s)`);
      });
    } else {
      console.log('No objects detected');
    }
    
    // Print token usage
    console.log('\nTotal Token Usage:');
    console.log(`Input Tokens: ${totalInputTokens}`);
    console.log(`Output Tokens: ${totalOutputTokens}`);
    console.log(`Total Tokens: ${totalInputTokens + totalOutputTokens}`);
    
    if (results.length > 0) {
      console.log('\nAnnotated frames saved to:');
      results.forEach(result => {
        console.log(`- ${result.annotatedOutputPath}`);
      });
    }
    
    // Add note about throttling if not all frames were processed
    if (results.length < framePaths.length) {
      console.log('\nNote: Some frames were not processed due to API throttling.');
      console.log('Try running the example again with fewer frames or a longer delay between API calls.');
    }
  } catch (error) {
    console.error('Error in bounding box detection example:', error);
  }
}

// Run the example
main(); 