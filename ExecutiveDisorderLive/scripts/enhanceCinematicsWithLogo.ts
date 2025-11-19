import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs';
import path from 'path';

const execAsync = promisify(exec);

const SOURCE_DIR = 'Dropbox/Replit/ExecutiveDisorder_Assets/09_Video_Assets/Opening_Cinematics_Extended';
const LOGO_PATH = 'Dropbox/Replit/logos/executive-disorder-logo.png';
const OUTPUT_DIR = 'Dropbox/Replit/ExecutiveDisorder_Assets/09_Video_Assets/Opening_Cinematics_Final';
const GAME_OUTPUT_DIR = 'client/public/videos/opening-cinematics-final';

const CINEMATICS = [
  {
    input: 'opening-01-political-chaos-extended.mp4',
    output: 'opening-01-political-chaos-final.mp4',
    name: 'Political Chaos',
    text: 'CHAOS INCOMING'
  },
  {
    input: 'opening-02-media-frenzy-extended.mp4',
    output: 'opening-02-media-frenzy-final.mp4',
    name: 'Media Frenzy',
    text: 'BREAKING NEWS'
  },
  {
    input: 'opening-03-power-ascension-extended.mp4',
    output: 'opening-03-power-ascension-final.mp4',
    name: 'Power Ascension',
    text: 'RISE TO POWER'
  },
  {
    input: 'opening-04-critical-decision-extended.mp4',
    output: 'opening-04-critical-decision-final.mp4',
    name: 'Critical Decision',
    text: 'CHOOSE WISELY'
  }
];

async function addLogoOverlay(inputPath: string, outputPath: string, videoName: string, overlayText: string) {
  console.log(`\n🎬 Enhancing: ${videoName}`);
  console.log(`   Adding logo overlay and title card...`);

  try {
    // Complex ffmpeg filter:
    // 1. Fade in logo at 9s (last 3 seconds of 12s video)
    // 2. Add "EXECUTIVE DISORDER" text below logo
    // 3. Add scene-specific text above
    // 4. Fade to black at the very end
    const command = `ffmpeg -i "${inputPath}" -i "${LOGO_PATH}" -filter_complex "\
[1:v]scale=400:-1,fade=in:st=9:d=0.5:alpha=1,fade=out:st=11.5:d=0.5:alpha=1[logo];\
[0:v][logo]overlay=(W-w)/2:(H-h)/2-50:enable='between(t,9,12)'[v1];\
[v1]drawtext=text='${overlayText}':fontsize=32:fontcolor=white:x=(w-text_w)/2:y=h/2-200:enable='between(t,9,12)':alpha='if(lt(t,9.5),(t-9)*2,if(gt(t,11.5),(12-t)*2,1))'[v2];\
[v2]drawtext=text='EXECUTIVE DISORDER':fontsize=48:fontcolor=gold:borderw=2:bordercolor=black:x=(w-text_w)/2:y=h/2+150:enable='between(t,9.5,12)':alpha='if(lt(t,10),(t-9.5)*2,if(gt(t,11.5),(12-t)*2,1))'[vout]" \
-map "[vout]" -map 0:a -c:v libx264 -preset medium -crf 23 -c:a copy "${outputPath}" -y`;

    await execAsync(command);
    
    const stats = fs.statSync(outputPath);
    const sizeMB = (stats.size / (1024 * 1024)).toFixed(2);
    
    console.log(`   ✅ Enhanced successfully!`);
    console.log(`   💾 Size: ${sizeMB} MB`);
    
    return outputPath;
  } catch (error: any) {
    console.error(`   ❌ Error enhancing video: ${error.message}`);
    throw error;
  }
}

async function enhanceAllCinematics() {
  console.log('═══════════════════════════════════════════════════════════');
  console.log('🎨 ENHANCING OPENING CINEMATICS');
  console.log('   Adding: Executive Disorder logo + title cards');
  console.log('   Duration: 12 seconds each with logo reveal');
  console.log('═══════════════════════════════════════════════════════════\n');

  // Create output directories
  [OUTPUT_DIR, GAME_OUTPUT_DIR].forEach(dir => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
      console.log(`📁 Created directory: ${dir}`);
    }
  });

  const results: { name: string; size: string; path: string }[] = [];

  for (const cinematic of CINEMATICS) {
    const inputPath = path.join(SOURCE_DIR, cinematic.input);
    const outputPath = path.join(OUTPUT_DIR, cinematic.output);

    try {
      if (!fs.existsSync(inputPath)) {
        console.log(`   ⚠️  Skipping ${cinematic.name}: Source file not found`);
        continue;
      }

      // Add logo overlay
      await addLogoOverlay(inputPath, outputPath, cinematic.name, cinematic.text);

      // Copy to game public folder
      const gameOutputPath = path.join(GAME_OUTPUT_DIR, cinematic.output);
      fs.copyFileSync(outputPath, gameOutputPath);
      console.log(`   📂 Copied to game assets`);

      const stats = fs.statSync(outputPath);
      const sizeMB = (stats.size / (1024 * 1024)).toFixed(2);

      results.push({
        name: cinematic.name,
        size: `${sizeMB} MB`,
        path: cinematic.output
      });

    } catch (error) {
      console.error(`❌ Failed to enhance ${cinematic.name}:`, error);
    }
  }

  // Print summary
  console.log('\n' + '═'.repeat(70));
  console.log('📊 ENHANCEMENT SUMMARY');
  console.log('═'.repeat(70));
  console.log(`\n✅ Successfully enhanced: ${results.length}/${CINEMATICS.length} videos\n`);

  if (results.length > 0) {
    console.log('🎬 Enhanced Videos:');
    results.forEach((result, index) => {
      console.log(`   ${index + 1}. ${result.name} - ${result.size}`);
      console.log(`      File: ${result.path}`);
      console.log('');
    });

    const totalSize = results.reduce((sum, r) => sum + parseFloat(r.size), 0);
    console.log(`📦 Total Size: ${totalSize.toFixed(2)} MB`);
    console.log(`\n✨ All videos now feature Executive Disorder logo and title cards!`);
  }

  console.log('\n' + '═'.repeat(70));
  console.log('🎉 Enhancement complete!');
  console.log('═'.repeat(70));
}

// Run the enhancement
enhanceAllCinematics().catch(console.error);
