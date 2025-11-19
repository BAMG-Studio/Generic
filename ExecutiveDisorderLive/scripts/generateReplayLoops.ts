import RunwayML from '@runwayml/sdk';
import fs from 'fs';
import path from 'path';

const client = new RunwayML({ apiKey: process.env.RUNWAYML_API_SECRET });

const OUTPUT_DIR = 'Dropbox/Replit/ExecutiveDisorder_Assets/09_Video_Assets/Replay_Loop_Videos';

// Ensure output directory exists
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

// 15 seamless loop video prompts for political satire gameplay backgrounds
const REPLAY_LOOPS = [
  {
    filename: 'government-office-ambient',
    prompt: 'Seamless loop: Professional government office interior, American flags, mahogany desk, dim lighting, subtle papers moving from air conditioning, cinematic atmosphere, political ambiance, 4K quality',
    duration: 8
  },
  {
    filename: 'political-rally-crowd',
    prompt: 'Seamless loop: Energetic political rally crowd waving signs and flags, cheering supporters, red white and blue colors, dynamic movement, rally atmosphere, satirical political energy, cinematic',
    duration: 8
  },
  {
    filename: 'breaking-news-ticker',
    prompt: 'Seamless loop: Modern newsroom background, multiple TV screens showing breaking news alerts, scrolling news tickers, dynamic graphics, media center ambiance, professional broadcast quality',
    duration: 8
  },
  {
    filename: 'capitol-building-exterior',
    prompt: 'Seamless loop: US Capitol building exterior establishing shot, dramatic cloudy sky, American flag waving, golden hour lighting, cinematic government architecture, political power symbolism',
    duration: 8
  },
  {
    filename: 'press-conference-room',
    prompt: 'Seamless loop: White House press conference room, podium with presidential seal, multiple camera flashes popping, media photographers, official government setting, dramatic lighting',
    duration: 8
  },
  {
    filename: 'protest-demonstration',
    prompt: 'Seamless loop: Peaceful political protest crowd, diverse people holding creative satirical signs, chanting, democratic demonstration, political activism energy, cinematic documentary style',
    duration: 8
  },
  {
    filename: 'campaign-headquarters',
    prompt: 'Seamless loop: Busy campaign headquarters war room, multiple TV screens, volunteers on phones, election maps on walls, chaotic energy, political campaign atmosphere, documentary realism',
    duration: 8
  },
  {
    filename: 'stock-market-displays',
    prompt: 'Seamless loop: Wall Street trading floor screens, stock market tickers scrolling, economic data displays, financial charts fluctuating, business news ambiance, corporate atmosphere',
    duration: 8
  },
  {
    filename: 'media-circus-exterior',
    prompt: 'Seamless loop: Outside government building, dozens of news vans, satellite dishes, reporters preparing, media circus atmosphere, political scandal energy, journalistic chaos',
    duration: 8
  },
  {
    filename: 'debate-stage-empty',
    prompt: 'Seamless loop: Presidential debate stage, two podiums, American flags backdrop, dramatic stage lighting, empty and anticipatory, political theater setting, professional broadcast quality',
    duration: 8
  },
  {
    filename: 'crisis-situation-room',
    prompt: 'Seamless loop: White House situation room, large conference table, multiple monitors showing world maps, red phone, tense atmosphere, classified briefing ambiance, cinematic realism',
    duration: 8
  },
  {
    filename: 'oval-office-view',
    prompt: 'Seamless loop: Oval Office interior from side angle, Resolute desk, presidential flags, morning light through windows, powerful atmosphere, iconic political setting, cinematic quality',
    duration: 8
  },
  {
    filename: 'legislative-chamber',
    prompt: 'Seamless loop: Congressional chamber interior, rows of seats, American flag, official government proceedings atmosphere, democratic institution setting, architectural grandeur, cinematic',
    duration: 8
  },
  {
    filename: 'international-summit',
    prompt: 'Seamless loop: International diplomatic summit room, circular table, multiple national flags, formal meeting atmosphere, global politics setting, professional lighting, cinematic quality',
    duration: 8
  },
  {
    filename: 'election-night-boards',
    prompt: 'Seamless loop: Election night broadcast studio, large electoral map boards, vote counters updating, news anchor desks, dramatic lighting, democratic process visualization, broadcast quality',
    duration: 8
  }
];

async function generateReplayLoops() {
  console.log('═'.repeat(70));
  console.log('🎬 GENERATING 15 REPLAY LOOP VIDEOS');
  console.log('   Political Satire Gameplay Backgrounds');
  console.log('   Model: Google Veo3 via Runway ML');
  console.log('   Duration: 8 seconds each (seamless loops)');
  console.log('═'.repeat(70) + '\n');

  const results = [];
  
  for (let i = 0; i < REPLAY_LOOPS.length; i++) {
    const loop = REPLAY_LOOPS[i];
    console.log(`\n[${ i + 1}/15] Generating: ${loop.filename}`);
    console.log(`   Prompt: ${loop.prompt.substring(0, 80)}...`);
    
    try {
      // Create text-to-video task
      const task = await client.textToVideo.create({
        promptText: loop.prompt,
        model: 'veo3',
        duration: loop.duration,
        ratio: '1280:720'
      });

      console.log(`   ⏳ Task created: ${task.id}`);
      console.log(`   ⏳ Waiting for video generation...`);

      // Poll for completion
      let videoTask = task;
      while (videoTask.status !== 'SUCCEEDED' && videoTask.status !== 'FAILED') {
        await new Promise(resolve => setTimeout(resolve, 5000));
        videoTask = await client.tasks.retrieve(task.id);
        
        if (videoTask.status === 'RUNNING') {
          const progress = videoTask.progress || 0;
          console.log(`   ⏳ Progress: ${Math.round(progress * 100)}%`);
        }
      }

      if (videoTask.status === 'FAILED') {
        console.error(`   ❌ Failed: ${videoTask.failure || 'Unknown error'}`);
        results.push({ filename: loop.filename, status: 'failed', error: videoTask.failure });
        continue;
      }

      // Download the video
      if (videoTask.output && videoTask.output.length > 0) {
        const videoUrl = videoTask.output[0];
        console.log(`   📥 Downloading video...`);
        
        const response = await fetch(videoUrl);
        const buffer = await response.arrayBuffer();
        
        const outputPath = path.join(OUTPUT_DIR, `${loop.filename}.mp4`);
        fs.writeFileSync(outputPath, Buffer.from(buffer));
        
        const stats = fs.statSync(outputPath);
        const sizeMB = (stats.size / (1024 * 1024)).toFixed(2);
        
        console.log(`   ✅ Saved: ${loop.filename}.mp4 (${sizeMB} MB)`);
        
        results.push({
          filename: loop.filename,
          status: 'success',
          size: sizeMB,
          path: outputPath
        });
      } else {
        console.error(`   ❌ No video output received`);
        results.push({ filename: loop.filename, status: 'failed', error: 'No output' });
      }
      
    } catch (error: any) {
      console.error(`   ❌ Error: ${error.message}`);
      results.push({ filename: loop.filename, status: 'failed', error: error.message });
    }
    
    // Small delay between requests
    if (i < REPLAY_LOOPS.length - 1) {
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  }

  // Summary
  console.log('\n' + '═'.repeat(70));
  console.log('📊 GENERATION SUMMARY');
  console.log('═'.repeat(70));
  
  const successful = results.filter(r => r.status === 'success');
  const failed = results.filter(r => r.status === 'failed');
  
  console.log(`\n✅ Successful: ${successful.length}/15`);
  console.log(`❌ Failed: ${failed.length}/15\n`);
  
  if (successful.length > 0) {
    const totalSize = successful.reduce((sum, r) => sum + parseFloat(r.size || '0'), 0);
    console.log(`📦 Total size: ${totalSize.toFixed(2)} MB`);
    console.log(`📂 Location: ${OUTPUT_DIR}\n`);
    
    console.log('Generated videos:');
    successful.forEach(r => {
      console.log(`   ✓ ${r.filename}.mp4 (${r.size} MB)`);
    });
  }
  
  if (failed.length > 0) {
    console.log('\nFailed videos:');
    failed.forEach(r => {
      console.log(`   ✗ ${r.filename}: ${r.error}`);
    });
  }
  
  console.log('\n' + '═'.repeat(70));
  console.log('🎬 REPLAY LOOP GENERATION COMPLETE!');
  console.log('═'.repeat(70));
  
  return results;
}

// Run the generation
generateReplayLoops().catch(console.error);
