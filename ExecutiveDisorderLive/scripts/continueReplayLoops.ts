import RunwayML from '@runwayml/sdk';
import fs from 'fs';
import path from 'path';

const client = new RunwayML({ apiKey: process.env.RUNWAYML_API_SECRET });

const OUTPUT_DIR = 'Dropbox/Replit/ExecutiveDisorder_Assets/09_Video_Assets/Replay_Loop_Videos';

// Remaining loops to generate
const REPLAY_LOOPS = [
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

async function continueGeneration() {
  console.log('═'.repeat(70));
  console.log('🎬 CONTINUING REPLAY LOOP VIDEO GENERATION');
  console.log(`   Generating remaining 10 videos`);
  console.log('═'.repeat(70) + '\n');

  const results = [];
  
  for (let i = 0; i < REPLAY_LOOPS.length; i++) {
    const loop = REPLAY_LOOPS[i];
    const outputPath = path.join(OUTPUT_DIR, `${loop.filename}.mp4`);
    
    // Skip if already exists
    if (fs.existsSync(outputPath)) {
      console.log(`[${i + 1}/10] Skipping: ${loop.filename} (already exists)`);
      results.push({ filename: loop.filename, status: 'skipped' });
      continue;
    }
    
    console.log(`\n[${i + 1}/10] Generating: ${loop.filename}`);
    console.log(`   Prompt: ${loop.prompt.substring(0, 80)}...`);
    
    try {
      const task = await client.textToVideo.create({
        promptText: loop.prompt,
        model: 'veo3',
        duration: loop.duration,
        ratio: '1280:720'
      });

      console.log(`   ⏳ Task created: ${task.id}`);
      console.log(`   ⏳ Waiting for video generation...`);

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

      if (videoTask.output && videoTask.output.length > 0) {
        const videoUrl = videoTask.output[0];
        console.log(`   📥 Downloading video...`);
        
        const response = await fetch(videoUrl);
        const buffer = await response.arrayBuffer();
        
        fs.writeFileSync(outputPath, Buffer.from(buffer));
        
        const stats = fs.statSync(outputPath);
        const sizeMB = (stats.size / (1024 * 1024)).toFixed(2);
        
        console.log(`   ✅ Saved: ${loop.filename}.mp4 (${sizeMB} MB)`);
        
        results.push({ filename: loop.filename, status: 'success', size: sizeMB });
      }
      
    } catch (error: any) {
      console.error(`   ❌ Error: ${error.message}`);
      results.push({ filename: loop.filename, status: 'failed', error: error.message });
    }
    
    if (i < REPLAY_LOOPS.length - 1) {
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  }

  // Summary
  console.log('\n' + '═'.repeat(70));
  console.log('📊 CONTINUATION SUMMARY');
  console.log('═'.repeat(70));
  
  const successful = results.filter(r => r.status === 'success');
  const failed = results.filter(r => r.status === 'failed');
  const skipped = results.filter(r => r.status === 'skipped');
  
  console.log(`\n✅ Successful: ${successful.length}`);
  console.log(`❌ Failed: ${failed.length}`);
  console.log(`⏭️  Skipped: ${skipped.length}\n`);
  
  if (successful.length > 0) {
    console.log('Generated videos:');
    successful.forEach(r => {
      console.log(`   ✓ ${r.filename}.mp4 (${r.size} MB)`);
    });
  }
  
  console.log('\n' + '═'.repeat(70));
}

continueGeneration().catch(console.error);
