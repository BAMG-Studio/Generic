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
  'opening-03-power-ascension-final.mp4',
  'opening-01-political-chaos-final.mp4',
  'opening-02-media-frenzy-final.mp4',
  'opening-04-critical-decision-final.mp4'
];

async function createGrandCinematic() {
  console.log('═══════════════════════════════════════════════════════════');
  console.log('🎬 CREATING GRAND OPENING CINEMATIC');
  console.log('   Sequence: Power Ascension → Chaos → Media → Decision');
  console.log('   Duration: ~48 seconds total');
  console.log('═══════════════════════════════════════════════════════════\n');

  try {
    // Create concat file list for simple concatenation
    const concatListPath = path.join(SOURCE_DIR, 'concat_list.txt');
    const concatContent = SEQUENCE.map(s => `file '${s}'`).join('\n');
    fs.writeFileSync(concatListPath, concatContent);
    
    console.log('📝 Video sequence:');
    SEQUENCE.forEach((s, i) => {
      console.log(`   ${i + 1}. ${s}`);
    });
    console.log('');

    const outputPath = path.join(OUTPUT_DIR, 'grand-opening-cinematic.mp4');
    
    // Simple concatenation with re-encoding for smooth playback
    console.log('🎬 Combining videos...');
    
    const command = `ffmpeg -f concat -safe 0 -i "${concatListPath}" -c:v libx264 -preset medium -crf 23 -c:a aac -b:a 192k "${outputPath}" -y`;

    const { stdout, stderr } = await execAsync(command, { maxBuffer: 10 * 1024 * 1024 });
    
    const stats = fs.statSync(outputPath);
    const sizeMB = (stats.size / (1024 * 1024)).toFixed(2);
    
    console.log(`   ✅ Grand cinematic created successfully!`);
    console.log(`   💾 Size: ${sizeMB} MB`);
    
    // Get actual duration using ffprobe
    const durationCmd = `ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "${outputPath}"`;
    const { stdout: durationOut } = await execAsync(durationCmd);
    const duration = parseFloat(durationOut.trim()).toFixed(1);
    
    console.log(`   ⏱️  Duration: ${duration} seconds`);
    
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
    console.log(`⏱️  Duration: ${duration} seconds`);
    console.log(`\n🎬 Sequence breakdown:`);
    console.log(`   0:00-0:12  Power Ascension → Rise to political power`);
    console.log(`   0:12-0:24  Political Chaos → Reality of governance`);
    console.log(`   0:24-0:36  Media Frenzy → Public scrutiny intensifies`);
    console.log(`   0:36-0:48  Critical Decision → Your choices matter`);
    console.log(`\n💫 Full cinematic experience with Executive Disorder branding!`);
    console.log('═'.repeat(70));
    
    return outputPath;
  } catch (error: any) {
    console.error(`   ❌ Error creating grand cinematic: ${error.message}`);
    console.error(error.stack);
    throw error;
  }
}

// Run the creation
createGrandCinematic().catch(console.error);
