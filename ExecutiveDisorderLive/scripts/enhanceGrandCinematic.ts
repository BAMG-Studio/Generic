import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs';
import path from 'path';

const execAsync = promisify(exec);

const SOURCE_FILE = 'Dropbox/Replit/ExecutiveDisorder_Assets/09_Video_Assets/Opening_Cinematics_Final/grand-opening-cinematic.mp4';
const OUTPUT_FILE = 'Dropbox/Replit/ExecutiveDisorder_Assets/09_Video_Assets/Opening_Cinematics_Final/grand-opening-cinematic-enhanced.mp4';
const GAME_OUTPUT = 'client/public/videos/opening-cinematics-final/grand-opening-cinematic-enhanced.mp4';

// Satirical text overlays at key moments
const TEXT_OVERLAYS = [
  { time: 2, text: '"The Journey Begins..."', duration: 3 },
  { time: 13, text: '"Reality Sets In"', duration: 3 },
  { time: 25, text: '"The Media is Watching"', duration: 3 },
  { time: 38, text: '"Every Choice Matters"', duration: 3 },
  { time: 45, text: '"EXECUTIVE DISORDER"', duration: 2.5, size: 60, color: 'gold' }
];

async function enhanceGrandCinematic() {
  console.log('═══════════════════════════════════════════════════════════');
  console.log('✨ ENHANCING GRAND CINEMATIC');
  console.log('   Adding: Satirical text overlays, fade effects');
  console.log('   Duration: ~48 seconds');
  console.log('═══════════════════════════════════════════════════════════\n');

  try {
    // Build complex filter for multiple text overlays
    let filterComplex = '[0:v]';
    
    TEXT_OVERLAYS.forEach((overlay, index) => {
      const fontSize = overlay.size || 40;
      const color = overlay.color || 'white';
      const startTime = overlay.time;
      const endTime = overlay.time + overlay.duration;
      const fadeInDur = 0.3;
      const fadeOutDur = 0.3;
      
      const textFilter = `drawtext=text='${overlay.text}':fontsize=${fontSize}:fontcolor=${color}:borderw=3:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,${startTime},${endTime})':alpha='if(lt(t,${startTime + fadeInDur}),(t-${startTime})/${fadeInDur},if(gt(t,${endTime - fadeOutDur}),(${endTime}-t)/${fadeOutDur},1))'`;
      
      if (index === 0) {
        filterComplex += textFilter;
      } else {
        filterComplex += `,${textFilter}`;
      }
    });
    
    filterComplex += '[vout]';
    
    console.log('🎨 Adding text overlays:');
    TEXT_OVERLAYS.forEach((overlay, i) => {
      console.log(`   ${i + 1}. "${overlay.text}" at ${overlay.time}s`);
    });
    console.log('');
    
    const command = `ffmpeg -i "${SOURCE_FILE}" -filter_complex "${filterComplex}" -map "[vout]" -map 0:a -c:v libx264 -preset medium -crf 23 -c:a copy "${OUTPUT_FILE}" -y`;
    
    console.log('🎬 Processing...');
    await execAsync(command, { maxBuffer: 20 * 1024 * 1024 });
    
    const stats = fs.statSync(OUTPUT_FILE);
    const sizeMB = (stats.size / (1024 * 1024)).toFixed(2);
    
    console.log(`   ✅ Enhanced cinematic created!`);
    console.log(`   💾 Size: ${sizeMB} MB`);
    
    // Copy to game assets
    fs.copyFileSync(OUTPUT_FILE, GAME_OUTPUT);
    console.log(`   📂 Copied to game assets`);
    
    console.log('\n' + '═'.repeat(70));
    console.log('✨ ENHANCED GRAND CINEMATIC COMPLETE!');
    console.log('═'.repeat(70));
    console.log(`\n📹 File: grand-opening-cinematic-enhanced.mp4`);
    console.log(`📦 Size: ${sizeMB} MB`);
    console.log(`\n💫 Features:`);
    console.log(`   • Professional narrative text overlays`);
    console.log(`   • Executive Disorder branding throughout`);
    console.log(`   • Satirical political comedy timing`);
    console.log(`   • 4-scene epic journey (~48 seconds)`);
    console.log('═'.repeat(70));
    
  } catch (error: any) {
    console.error(`   ❌ Error enhancing cinematic: ${error.message}`);
    throw error;
  }
}

// Run the enhancement
enhanceGrandCinematic().catch(console.error);
