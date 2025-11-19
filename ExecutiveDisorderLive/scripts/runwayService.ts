import RunwayML from '@runwayml/sdk';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Initialize Runway ML client
const runway = new RunwayML({
  apiKey: process.env.RUNWAY_API_KEY
});

export interface VideoGenerationOptions {
  promptImage: string; // URL or base64 data URI (required for gen3a_turbo)
  promptText: string;
  duration?: 5 | 10;
  ratio?: '1280:768' | '768:1280';
  outputPath: string;
  filename: string;
}

/**
 * Generate video from image using Runway ML Gen-3 Alpha Turbo
 */
export async function generateImageToVideo(options: VideoGenerationOptions): Promise<string> {
  const {
    promptImage,
    promptText,
    duration = 10,
    ratio = '1280:768',
    outputPath,
    filename
  } = options;

  console.log(`\n🎬 Generating video: ${filename}`);
  console.log(`   Prompt: "${promptText}"`);
  console.log(`   Duration: ${duration}s`);
  console.log(`   Ratio: ${ratio}`);

  try {
    // Create image-to-video task
    const taskPromise = runway.imageToVideo.create({
      model: 'gen3a_turbo',
      promptImage: promptImage,
      promptText: promptText,
      duration: duration,
      ratio: ratio
    });

    const task = await taskPromise;
    console.log(`   Task ID: ${task.id}`);
    console.log(`   Status: Processing...`);

    // Wait for task completion (10 minute timeout)
    const result = await taskPromise.waitForTaskOutput({ 
      timeout: 600000 // 10 minutes
    });

    if (result.status === 'SUCCEEDED' && result.output) {
      const videoUrl = Array.isArray(result.output) ? result.output[0] : result.output;
      
      console.log(`   ✅ Video generated successfully!`);
      console.log(`   Video URL: ${videoUrl}`);

      // Download the video
      const videoPath = await downloadVideo(videoUrl, outputPath, filename);
      
      return videoPath;
    } else {
      throw new Error(`Task failed with status: ${result.status}`);
    }
  } catch (error) {
    console.error(`   ❌ Error generating video:`, error);
    throw error;
  }
}

/**
 * Download video from URL to local filesystem
 */
async function downloadVideo(url: string, outputPath: string, filename: string): Promise<string> {
  try {
    // Ensure output directory exists
    const fullPath = path.join(process.cwd(), outputPath);
    if (!fs.existsSync(fullPath)) {
      fs.mkdirSync(fullPath, { recursive: true });
    }

    const filePath = path.join(fullPath, filename);

    console.log(`   📥 Downloading video to: ${filePath}`);

    // Download video using fetch
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`Failed to download video: ${response.statusText}`);
    }

    const buffer = await response.arrayBuffer();
    fs.writeFileSync(filePath, Buffer.from(buffer));

    const fileSize = (fs.statSync(filePath).size / (1024 * 1024)).toFixed(2);
    console.log(`   ✅ Video downloaded (${fileSize} MB)`);

    return filePath;
  } catch (error) {
    console.error(`   ❌ Error downloading video:`, error);
    throw error;
  }
}

/**
 * Convert local image to base64 data URI
 */
export function imageToDataUri(imagePath: string): string {
  const fullPath = path.join(process.cwd(), imagePath);
  const imageBuffer = fs.readFileSync(fullPath);
  const base64 = imageBuffer.toString('base64');
  
  // Determine MIME type from extension
  const ext = path.extname(imagePath).toLowerCase();
  const mimeType = ext === '.png' ? 'image/png' : 'image/jpeg';
  
  return `data:${mimeType};base64,${base64}`;
}

/**
 * Check Runway ML API status
 */
export async function checkRunwayStatus(): Promise<boolean> {
  try {
    console.log('🔍 Checking Runway ML API status...');
    
    if (!process.env.RUNWAY_API_KEY) {
      console.error('❌ RUNWAY_API_KEY not found in environment');
      return false;
    }
    
    console.log('✅ Runway ML API key is configured');
    return true;
  } catch (error) {
    console.error('❌ Runway ML API error:', error);
    return false;
  }
}
