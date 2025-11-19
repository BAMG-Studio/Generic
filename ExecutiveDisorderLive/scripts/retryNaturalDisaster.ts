import RunwayML from '@runwayml/sdk';
import { readFileSync } from 'fs';
import { join } from 'path';
import { writeFile } from 'fs/promises';

const client = new RunwayML({
  apiKey: process.env.RUNWAYML_API_SECRET
});

async function generateVideo() {
  console.log('🎬 Retrying: Natural Disaster Emergency');
  
  try {
    // Load the newscast studio background image
    const imagePath = join(process.cwd(), 'attached_assets/generated_images/Empty_newscast_studio_background_318e0376.png');
    const imageBuffer = readFileSync(imagePath);
    const base64Image = `data:image/png;base64,${imageBuffer.toString('base64')}`;
    
    // Adjusted prompt - simpler, less complex
    const prompt = 'Dramatic hurricane satellite view: Massive spinning storm system over ocean, white spiral cloud formation, red and orange weather alert graphics overlay, meteorological radar display, severe weather emergency visualization, cinematic disaster broadcast quality';
    
    const task = await client.imageToVideo.create({
      model: 'gen3a_turbo',
      promptImage: base64Image,
      promptText: prompt,
      duration: 10,
      ratio: '1280:768'
    });
    
    console.log(`⏳ Task created: ${task.id}`);
    
    // Poll for completion
    let attempts = 0;
    const maxAttempts = 60;
    
    while (attempts < maxAttempts) {
      const status = await client.tasks.retrieve(task.id);
      
      if (status.status === 'SUCCEEDED') {
        console.log(`✅ Video generated successfully!`);
        
        if (status.output && status.output.length > 0) {
          const videoUrl = status.output[0];
          console.log(`📥 Downloading from: ${videoUrl}`);
          
          const response = await fetch(videoUrl);
          const buffer = await response.arrayBuffer();
          
          const dropboxPath = 'Dropbox/Replit/ExecutiveDisorder_Assets/09_Video_Assets/Crisis/crisis-natural-disaster.mp4';
          const publicPath = 'client/public/videos/crisis/crisis-natural-disaster.mp4';
          
          const videoBuffer = Buffer.from(buffer);
          await writeFile(dropboxPath, videoBuffer);
          await writeFile(publicPath, videoBuffer);
          
          console.log(`💾 Saved to Dropbox: ${dropboxPath}`);
          console.log(`💾 Saved to public: ${publicPath}`);
          console.log(`✨ Success!`);
          return;
        }
      } else if (status.status === 'FAILED') {
        throw new Error(`Video generation failed: ${status.failure}`);
      }
      
      console.log(`⏳ Status: ${status.status}... (${attempts + 1}/${maxAttempts})`);
      await new Promise(resolve => setTimeout(resolve, 10000));
      attempts++;
    }
    
    throw new Error('Video generation timed out');
  } catch (error) {
    console.error(`❌ Error:`, error);
  }
}

generateVideo();
