import RunwayML from '@runwayml/sdk';
import { readFileSync } from 'fs';
import { join } from 'path';

const client = new RunwayML({
  apiKey: process.env.RUNWAYML_API_SECRET
});

interface CrisisVideo {
  id: string;
  title: string;
  prompt: string;
  filename: string;
}

const crisisVideos: CrisisVideo[] = [
  {
    id: 'economic-crash',
    title: 'Economic Market Crash',
    prompt: 'Dramatic financial crisis broadcast screen: Large digital displays showing plummeting red stock market graphs, multiple glowing financial tickers with negative numbers cascading downward, Wall Street trading floor monitors flashing red alerts, dramatic red and orange warning lighting, urgent financial data visualization, economic charts crashing in real-time, cinematic broadcast quality',
    filename: 'crisis-economic-crash.mp4'
  },
  {
    id: 'diplomatic-crisis',
    title: 'International Diplomatic Crisis',
    prompt: 'Emergency geopolitical broadcast screen: Animated world map with red conflict zones pulsing, diplomatic crisis indicators lighting up across continents, United Nations chamber empty with dramatic lighting, international flags arranged in tense formation, glowing red warning graphics overlay, urgent global emergency visualization, cinematic news broadcast aesthetic',
    filename: 'crisis-diplomatic-emergency.mp4'
  },
  {
    id: 'natural-disaster',
    title: 'Natural Disaster Emergency',
    prompt: 'Severe weather emergency broadcast: Massive hurricane spiral on satellite imagery, dramatic weather radar showing category 5 storm system in red and orange, lightning strikes illuminating dark storm clouds, emergency warning graphics pulsing, meteorological data screens showing extreme conditions, turbulent atmospheric visuals, cinematic disaster broadcast quality',
    filename: 'crisis-natural-disaster.mp4'
  },
  {
    id: 'cyber-attack',
    title: 'Cyber Security Breach',
    prompt: 'Cyber emergency broadcast visualization: Matrix-style cascading green code on dark screens, network infrastructure maps with red breach indicators spreading, server room with blinking red error lights, digital firewall being penetrated with glowing red alerts, cybersecurity threat dashboard showing critical warnings, dramatic blue and red tech lighting, urgent digital crisis aesthetic',
    filename: 'crisis-cyber-attack.mp4'
  },
  {
    id: 'health-emergency',
    title: 'Public Health Crisis',
    prompt: 'Medical emergency broadcast visualization: Animated disease outbreak map with red infection zones spreading across continents, hospital emergency entrance lit with flashing red lights, medical facility corridor with urgent warning signs, epidemiological charts showing exponential growth curves, health crisis data dashboards, dramatic red medical emergency lighting, urgent healthcare crisis atmosphere',
    filename: 'crisis-health-emergency.mp4'
  }
];

async function generateCrisisVideo(video: CrisisVideo) {
  console.log(`\n🎬 Generating: ${video.title}`);
  console.log(`📝 Prompt: ${video.prompt.substring(0, 100)}...`);

  try {
    // Load the newscast studio background image
    const imagePath = join(process.cwd(), 'attached_assets/generated_images/Empty_newscast_studio_background_318e0376.png');
    const imageBuffer = readFileSync(imagePath);
    const base64Image = `data:image/png;base64,${imageBuffer.toString('base64')}`;
    
    // Generate video using Gen3a Turbo (12 seconds)
    const task = await client.imageToVideo.create({
      model: 'gen3a_turbo',
      promptImage: base64Image,
      promptText: video.prompt,
      duration: 10, // 10 seconds (close to 12)
      ratio: '1280:768' // Landscape format for newscast
    });

    console.log(`⏳ Task created: ${task.id}`);
    
    // Poll for completion
    let attempts = 0;
    const maxAttempts = 60; // 10 minutes max (10 second intervals)
    
    while (attempts < maxAttempts) {
      const status = await client.tasks.retrieve(task.id);
      
      if (status.status === 'SUCCEEDED') {
        console.log(`✅ Video generated successfully!`);
        
        // Download video
        if (status.output && status.output.length > 0) {
          const videoUrl = status.output[0];
          console.log(`📥 Downloading from: ${videoUrl}`);
          
          const response = await fetch(videoUrl);
          const buffer = await response.arrayBuffer();
          
          // Save to both Dropbox and public folders
          const fs = await import('fs/promises');
          const dropboxPath = `Dropbox/Replit/ExecutiveDisorder_Assets/09_Video_Assets/Crisis/${video.filename}`;
          const publicPath = `client/public/videos/crisis/${video.filename}`;
          
          const videoBuffer = Buffer.from(buffer);
          await fs.writeFile(dropboxPath, videoBuffer);
          await fs.writeFile(publicPath, videoBuffer);
          
          console.log(`💾 Saved to Dropbox: ${dropboxPath}`);
          console.log(`💾 Saved to public: ${publicPath}`);
          return { success: true, path: dropboxPath };
        }
      } else if (status.status === 'FAILED') {
        throw new Error(`Video generation failed: ${status.failure}`);
      }
      
      console.log(`⏳ Status: ${status.status}... (${attempts + 1}/${maxAttempts})`);
      await new Promise(resolve => setTimeout(resolve, 10000)); // Wait 10 seconds
      attempts++;
    }
    
    throw new Error('Video generation timed out');
  } catch (error) {
    console.error(`❌ Error generating ${video.title}:`, error);
    return { success: false, error: String(error) };
  }
}

async function main() {
  console.log('🎥 Executive Disorder - Crisis Newscast Video Generator');
  console.log('=' .repeat(60));
  
  const results: Array<{ video: string; success: boolean; path?: string; error?: string }> = [];
  
  // Generate videos sequentially to avoid rate limits
  for (const video of crisisVideos) {
    const result = await generateCrisisVideo(video);
    results.push({ video: video.title, ...result });
    
    // Wait between generations to respect rate limits
    if (crisisVideos.indexOf(video) < crisisVideos.length - 1) {
      console.log('\n⏸️  Waiting 30 seconds before next generation...\n');
      await new Promise(resolve => setTimeout(resolve, 30000));
    }
  }
  
  console.log('\n' + '=' .repeat(60));
  console.log('📊 Generation Summary:');
  results.forEach(r => {
    console.log(`  ${r.success ? '✅' : '❌'} ${r.video}`);
  });
  
  const successful = results.filter(r => r.success).length;
  console.log(`\n✨ Successfully generated ${successful}/${results.length} crisis videos`);
}

main().catch(console.error);
