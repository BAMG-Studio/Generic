import Anthropic from '@anthropic-ai/sdk';
import Runway from '@runwayml/sdk';
import fs from 'fs';
import path from 'path';

interface EndingCinematic {
  id: string;
  name: string;
  prompt: string;
  description: string;
  outcome: string;
}

const endingCinematics: EndingCinematic[] = [
  {
    id: 'victory-triumph',
    name: 'Victory and Triumph',
    prompt: 'Cinematic video of triumphant presidential victory celebration, confetti falling, cheering crowds waving American flags, fireworks exploding in night sky behind White House, golden hour lighting, crowd chanting, balloons releasing, victorious atmosphere, cinematic political satire style, dramatic wide shots',
    description: 'Player achieved high scores in all resources - ultimate political success',
    outcome: 'Perfect Victory'
  },
  {
    id: 'scandal-impeachment',
    name: 'Scandal and Impeachment',
    prompt: 'Cinematic video of political scandal aftermath, empty presidential podium with microphones, scattered papers flying, news reporters rushing forward, camera flashes erupting, dramatic courtroom gavel slamming, serious faced judges, impeachment document signing, dark moody lighting, political downfall, cinematic drama',
    description: 'Low media perception and popularity - corruption scandal ending',
    outcome: 'Impeachment'
  },
  {
    id: 'economic-collapse',
    name: 'Economic Collapse',
    prompt: 'Cinematic video of economic disaster, stock market displays showing red declining graphs, Wall Street traders in panic, papers flying everywhere, empty treasury vault doors opening, protesters holding economic crisis signs, bread lines forming, dramatic stormy sky, financial catastrophe, cinematic political satire',
    description: 'Economy resource completely depleted - financial disaster',
    outcome: 'Economic Ruin'
  },
  {
    id: 'revolution-uprising',
    name: 'Revolution and Uprising',
    prompt: 'Cinematic video of civil uprising, massive protest crowds marching toward capitol building, people holding revolution signs, peaceful demonstration turning intense, smoke rising in background, dramatic sunset lighting, chanting protesters, political change movement, cinematic wide shots, democratic revolution atmosphere',
    description: 'Stability resource critically low - civil unrest ending',
    outcome: 'People\'s Revolution'
  },
  {
    id: 'nuclear-catastrophe',
    name: 'Nuclear Catastrophe',
    prompt: 'Cinematic video of diplomatic crisis escalation, tense situation room with military officers, red alert lights flashing, missile launch warning screens, empty oval office with ominous red glow, mushroom cloud forming in distance through window, apocalyptic dark atmosphere, political satire worst case scenario, dramatic cinematic ending',
    description: 'All resources critically low - complete failure ending',
    outcome: 'Catastrophic Failure'
  }
];

async function generateEndingCinematics() {
  const apiKey = process.env.RUNWAYML_API_SECRET;
  
  if (!apiKey) {
    console.error('❌ Error: RUNWAYML_API_SECRET not found in environment variables');
    process.exit(1);
  }

  const client = new Runway({ apiKey });

  // Create output directory
  const outputDir = 'Dropbox/Replit/ExecutiveDisorder_Assets/09_Video_Assets/Ending_Cinematics';
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  console.log('🎬 Generating 5 Ending Cinematics for Executive Disorder\n');
  console.log('='.repeat(70));

  for (let i = 0; i < endingCinematics.length; i++) {
    const ending = endingCinematics[i];
    
    console.log(`\n[${i + 1}/5] Generating: ${ending.name}`);
    console.log(`📝 Outcome: ${ending.outcome}`);
    console.log(`💭 Prompt: ${ending.prompt.substring(0, 80)}...`);

    try {
      // Generate video using Runway ML Veo3
      console.log('⏳ Creating video task...');
      
      const imageToVideo = await client.imageToVideo.create({
        model: 'gen3a_turbo',
        promptImage: 'https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=1280&h=720&fit=crop', // Political/government themed base
        promptText: ending.prompt,
        duration: 10,
        ratio: '1280:768' // Landscape 16:9 format
      });

      const taskId = imageToVideo.id;
      console.log(`✅ Task created: ${taskId}`);
      console.log('⏳ Waiting for video generation...');

      // Poll for completion
      let task = await client.tasks.retrieve(taskId);
      let attempts = 0;
      const maxAttempts = 60; // 5 minutes max

      while (task.status !== 'SUCCEEDED' && task.status !== 'FAILED' && attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 5000)); // Wait 5 seconds
        task = await client.tasks.retrieve(taskId);
        attempts++;
        
        if (attempts % 6 === 0) { // Every 30 seconds
          console.log(`  ⏳ Still generating... (${attempts * 5}s elapsed)`);
        }
      }

      if (task.status === 'SUCCEEDED' && task.output && task.output.length > 0) {
        const videoUrl = task.output[0];
        console.log(`✅ Video generated successfully!`);
        console.log(`📥 Downloading from: ${videoUrl}`);

        // Download the video
        const response = await fetch(videoUrl);
        const arrayBuffer = await response.arrayBuffer();
        const buffer = Buffer.from(arrayBuffer);

        // Save to file
        const filename = `ending-${ending.id}.mp4`;
        const filepath = path.join(outputDir, filename);
        fs.writeFileSync(filepath, buffer);

        const fileSizeMB = (buffer.length / 1024 / 1024).toFixed(2);
        console.log(`💾 Saved: ${filename} (${fileSizeMB} MB)`);
        console.log(`📂 Location: ${filepath}`);

      } else {
        console.error(`❌ Video generation failed for: ${ending.name}`);
        console.error(`   Status: ${task.status}`);
        if (task.failure) {
          console.error(`   Error: ${task.failure}`);
        }
      }

    } catch (error: any) {
      console.error(`❌ Error generating ${ending.name}:`, error.message);
      if (error.status === 402) {
        console.error('💳 API Credit Limit Reached - Cannot continue generation');
        break;
      }
    }

    console.log('-'.repeat(70));
  }

  console.log('\n✅ Ending Cinematics Generation Complete!');
  console.log(`📂 All videos saved to: ${outputDir}`);
  console.log('\n📊 Summary:');
  
  // List generated files
  const files = fs.readdirSync(outputDir).filter(f => f.endsWith('.mp4'));
  let totalSize = 0;
  
  files.forEach(file => {
    const filepath = path.join(outputDir, file);
    const stats = fs.statSync(filepath);
    const sizeMB = (stats.size / 1024 / 1024).toFixed(2);
    totalSize += stats.size;
    console.log(`  ✅ ${file} - ${sizeMB} MB`);
  });

  console.log(`\n📦 Total: ${files.length} videos, ${(totalSize / 1024 / 1024).toFixed(2)} MB`);
  console.log('\n🎯 Next Steps:');
  console.log('  1. Copy videos to client/public/videos/ending-cinematics/');
  console.log('  2. Upload to Dropbox cloud storage');
  console.log('  3. Create documentation manifest');
}

// Run the generation
generateEndingCinematics().catch(console.error);
