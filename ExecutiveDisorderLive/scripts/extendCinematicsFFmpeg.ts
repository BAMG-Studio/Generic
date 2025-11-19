import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs';
import path from 'path';

const execAsync = promisify(exec);

const SOURCE_DIR = 'Dropbox/Replit/ExecutiveDisorder_Assets/09_Video_Assets/Opening_Cinematics';
const OUTPUT_DIR = 'Dropbox/Replit/ExecutiveDisorder_Assets/09_Video_Assets/Opening_Cinematics_Extended';
const GAME_OUTPUT_DIR = 'client/public/videos/opening-cinematics-extended';

// Speed factor: 0.67 means slow down to 67% speed (8s becomes ~12s)
const SPEED_FACTOR = 0.67;
const TARGET_DURATION = 12; // seconds

const CINEMATICS = [
  {
    input: 'opening-01-political-chaos.mp4',
    output: 'opening-01-political-chaos-extended.mp4',
    name: 'Political Chaos'
  },
  {
    input: 'opening-02-media-frenzy.mp4',
    output: 'opening-02-media-frenzy-extended.mp4',
    name: 'Media Frenzy'
  },
  {
    input: 'opening-03-power-ascension.mp4',
    output: 'opening-03-power-ascension-extended.mp4',
    name: 'Power Ascension'
  },
  {
    input: 'opening-04-critical-decision.mp4',
    output: 'opening-04-critical-decision-extended.mp4',
    name: 'Critical Decision'
  },
  {
    input: 'opening-05-absurd-spectacle.mp4',
    output: 'opening-05-absurd-spectacle-extended.mp4',
    name: 'Absurd Spectacle'
  }
];

async function extendVideo(inputPath: string, outputPath: string, videoName: string) {
  console.log(`\n🎬 Extending: ${videoName}`);
  console.log(`   Input: ${inputPath}`);
  console.log(`   Output: ${outputPath}`);
  console.log(`   Method: Slow down to ${(SPEED_FACTOR * 100).toFixed(0)}% speed (${TARGET_DURATION}s total)`);

  try {
    // FFmpeg command to slow down video
    // setpts filter adjusts video timestamps, atempo adjusts audio
    const command = `ffmpeg -i "${inputPath}" -filter_complex "[0:v]setpts=${1/SPEED_FACTOR}*PTS[v];[0:a]atempo=${SPEED_FACTOR}[a]" -map "[v]" -map "[a]" -c:v libx264 -preset medium -crf 23 -c:a aac -b:a 192k "${outputPath}" -y`;

    const { stdout, stderr } = await execAsync(command);
    
    const stats = fs.statSync(outputPath);
    const sizeMB = (stats.size / (1024 * 1024)).toFixed(2);
    
    console.log(`   ✅ Extended successfully!`);
    console.log(`   💾 Size: ${sizeMB} MB`);
    
    return outputPath;
  } catch (error: any) {
    console.error(`   ❌ Error extending video: ${error.message}`);
    throw error;
  }
}

async function extendAllCinematics() {
  console.log('═══════════════════════════════════════════════════════════');
  console.log('🎬 EXTENDING OPENING CINEMATICS');
  console.log(`   Original Duration: 8 seconds`);
  console.log(`   Extended Duration: ${TARGET_DURATION} seconds (50% longer!)`);
  console.log(`   Method: Cinematic slow-motion effect`);
  console.log('═══════════════════════════════════════════════════════════\n');

  // Create output directories
  [OUTPUT_DIR, GAME_OUTPUT_DIR].forEach(dir => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
      console.log(`📁 Created directory: ${dir}`);
    }
  });

  const results: { name: string; size: string; dropboxPath: string; gamePath: string }[] = [];

  for (const cinematic of CINEMATICS) {
    const inputPath = path.join(SOURCE_DIR, cinematic.input);
    const dropboxOutputPath = path.join(OUTPUT_DIR, cinematic.output);
    const gameOutputPath = path.join(GAME_OUTPUT_DIR, cinematic.output);

    try {
      if (!fs.existsSync(inputPath)) {
        console.log(`   ⚠️  Skipping ${cinematic.name}: Source file not found`);
        continue;
      }

      // Extend to Dropbox location
      await extendVideo(inputPath, dropboxOutputPath, cinematic.name);

      // Copy to game public folder
      fs.copyFileSync(dropboxOutputPath, gameOutputPath);
      console.log(`   📂 Copied to game assets: ${gameOutputPath}`);

      const stats = fs.statSync(dropboxOutputPath);
      const sizeMB = (stats.size / (1024 * 1024)).toFixed(2);

      results.push({
        name: cinematic.name,
        size: `${sizeMB} MB`,
        dropboxPath: dropboxOutputPath,
        gamePath: gameOutputPath
      });

    } catch (error) {
      console.error(`❌ Failed to extend ${cinematic.name}:`, error);
    }
  }

  // Print summary
  console.log('\n' + '═'.repeat(70));
  console.log('📊 EXTENSION SUMMARY');
  console.log('═'.repeat(70));
  console.log(`\n✅ Successfully extended: ${results.length}/${CINEMATICS.length} videos\n`);

  if (results.length > 0) {
    console.log('📹 Extended Videos:');
    results.forEach((result, index) => {
      console.log(`   ${index + 1}. ${result.name} - ${result.size}`);
      console.log(`      Dropbox: ${result.dropboxPath}`);
      console.log(`      Game: ${result.gamePath}`);
      console.log('');
    });

    const totalSize = results.reduce((sum, r) => sum + parseFloat(r.size), 0);
    console.log(`📦 Total Size: ${totalSize.toFixed(2)} MB`);
    console.log(`⏱️  Total Duration: ${results.length * TARGET_DURATION} seconds`);
    console.log(`\n💡 Videos are now ${TARGET_DURATION}s each (${((TARGET_DURATION / 8 - 1) * 100).toFixed(0)}% longer!)`);
    console.log(`✨ Cinematic slow-motion effect adds drama and scope!`);
  }

  console.log('\n' + '═'.repeat(70));
  console.log('🎉 Extension complete!');
  console.log('═'.repeat(70));
}

// Run the extension
extendAllCinematics().catch(console.error);
