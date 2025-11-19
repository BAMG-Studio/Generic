import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs';
import path from 'path';

const execAsync = promisify(exec);

const SOURCE_DIR = 'Dropbox/Replit/ExecutiveDisorder_Assets/09_Video_Assets/Opening_Cinematics_Final';
const OUTPUT_DIR = 'Dropbox/Replit/ExecutiveDisorder_Assets/09_Video_Assets/Opening_Cinematics_Final';
const GAME_OUTPUT_DIR = 'client/public/videos/opening-cinematics-final';

// Order as requested: opening-03, opening-01, opening-02, opening-04
const SEQUENCE = [
  {
    file: 'opening-03-power-ascension-final.mp4',
    name: 'Power Ascension',
    transition: 'fade' // Fade to next
  },
  {
    file: 'opening-01-political-chaos-final.mp4',
    name: 'Political Chaos',
    transition: 'wipeleft' // Wipe left to next
  },
  {
    file: 'opening-02-media-frenzy-final.mp4',
    name: 'Media Frenzy',
    transition: 'slidedown' // Slide down to next
  },
  {
    file: 'opening-04-critical-decision-final.mp4',
    name: 'Critical Decision',
    transition: 'fadeblack' // Fade to black at end
  }
];

async function createGrandCinematic() {
  console.log('═══════════════════════════════════════════════════════════');
  console.log('🎬 CREATING GRAND OPENING CINEMATIC');
  console.log('   Sequence: Power Ascension → Chaos → Media Frenzy → Decision');
  console.log('   Features: Professional transitions, comedy timing');
  console.log('   Duration: ~48 seconds total');
  console.log('═══════════════════════════════════════════════════════════\n');

  try {
    // Create concat file list
    const concatListPath = path.join(SOURCE_DIR, 'concat_list.txt');
    const concatContent = SEQUENCE.map(s => `file '${s.file}'`).join('\n');
    fs.writeFileSync(concatListPath, concatContent);
    
    console.log('📝 Created concat list:');
    SEQUENCE.forEach((s, i) => {
      console.log(`   ${i + 1}. ${s.name} (${s.transition} transition)`);
    });
    console.log('');

    const outputPath = path.join(OUTPUT_DIR, 'grand-opening-cinematic.mp4');
    
    // Complex ffmpeg command with xfade transitions
    // Each video is ~12 seconds, transitions at 11.5s of each clip
    console.log('🎨 Applying professional transitions...');
    
    const command = `ffmpeg -i "${path.join(SOURCE_DIR, SEQUENCE[0].file)}" \
-i "${path.join(SOURCE_DIR, SEQUENCE[1].file)}" \
-i "${path.join(SOURCE_DIR, SEQUENCE[2].file)}" \
-i "${path.join(SOURCE_DIR, SEQUENCE[3].file)}" \
-filter_complex "\
[0:v][1:v]xfade=transition=fade:duration=0.5:offset=11.5[v01];\
[v01][2:v]xfade=transition=wipeleft:duration=0.5:offset=23[v012];\
[v012][3:v]xfade=transition=slidedown:duration=0.5:offset=34.5[vout];\
[0:a][1:a]acrossfade=d=0.5[a01];\
[a01][2:a]acrossfade=d=0.5[a012];\
[a012][3:a]acrossfade=d=0.5[aout]" \
-map "[vout]" -map "[aout]" -c:v libx264 -preset medium -crf 23 -c:a aac -b:a 192k "${outputPath}" -y`;

    const { stdout, stderr } = await execAsync(command);
    
    const stats = fs.statSync(outputPath);
    const sizeMB = (stats.size / (1024 * 1024)).toFixed(2);
    const duration = 46; // Approximate
    
    console.log(`   ✅ Grand cinematic created successfully!`);
    console.log(`   💾 Size: ${sizeMB} MB`);
    console.log(`   ⏱️  Duration: ~${duration} seconds`);
    
    // Copy to game assets
    const gameOutputPath = path.join(GAME_OUTPUT_DIR, 'grand-opening-cinematic.mp4');
    fs.copyFileSync(outputPath, gameOutputPath);
    console.log(`   📂 Copied to game assets`);
    
    // Clean up concat list
    fs.unlinkSync(concatListPath);
    
    console.log('\n' + '═'.repeat(70));
    console.log('✨ GRAND CINEMATIC COMPLETE!');
    console.log('═'.repeat(70));
    console.log(`\n📹 File: grand-opening-cinematic.mp4`);
    console.log(`📦 Size: ${sizeMB} MB`);
    console.log(`⏱️  Duration: ~${duration} seconds`);
    console.log(`\n🎬 Sequence breakdown:`);
    console.log(`   0:00-0:12  Power Ascension (Rise to power)`);
    console.log(`   0:12-0:24  Political Chaos (The reality hits)`);
    console.log(`   0:24-0:36  Media Frenzy (Public scrutiny)`);
    console.log(`   0:36-0:46  Critical Decision (Make your choice)`);
    console.log(`\n💫 Features professional fade, wipe, and slide transitions!`);
    console.log('═'.repeat(70));
    
    return outputPath;
  } catch (error: any) {
    console.error(`   ❌ Error creating grand cinematic: ${error.message}`);
    throw error;
  }
}

// Run the creation
createGrandCinematic().catch(console.error);
