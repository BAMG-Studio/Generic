import { generateImageToVideo, imageToDataUri, checkRunwayStatus, VideoGenerationOptions } from './runwayService.js';
import path from 'path';

/**
 * Extended Opening Cinematics - 10 second versions
 * Using Gen-3 Alpha Turbo for maximum duration
 */

const EXTENDED_CINEMATICS = [
  {
    id: '01',
    name: 'political-chaos-extended',
    prompt: 'Dramatic camera push into chaotic presidential Oval Office. Papers explosively flying everywhere, red emergency lights flashing intensely, shadowy advisors frantically arguing around the desk. Phone ringing urgently. Cinematic chaos building to crescendo. Presidential seal visible. High tension political drama.',
    duration: 10 as const,
    description: 'Political Chaos - Extended (10s)'
  },
  {
    id: '02',
    name: 'media-frenzy-extended',
    prompt: 'Dynamic sweeping camera through frenzied newsroom. Multiple Breaking News banners rapidly flashing, reporters frantically typing, cameras flashing, emergency broadcast lights strobing. Phones ringing everywhere. Papers flying. Television screens showing political chaos. Media circus intensifying. Cinematic news drama.',
    duration: 10 as const,
    description: 'Media Frenzy - Extended (10s)'
  },
  {
    id: '03',
    name: 'power-ascension-extended',
    prompt: 'Epic cinematic crane shot rising up grand government building steps at golden hour sunset. Dramatic silhouette climbing toward power. American flags waving majestically. Warm orange and purple sky. Lens flare. Shadows lengthening. Inspiring orchestral moment. Journey to leadership.',
    duration: 10 as const,
    description: 'Power Ascension - Extended (10s)'
  },
  {
    id: '04',
    name: 'critical-decision-extended',
    prompt: 'Intense slow-motion close-up of hand hovering over executive desk with APPROVED and REJECTED rubber stamps. Red emergency phone ringing. Important policy documents spread out. Tense deliberation. Weight of choice. Fingers trembling slightly. Dramatic lighting. Presidential decision moment.',
    duration: 10 as const,
    description: 'Critical Decision - Extended (10s)'
  },
  {
    id: '05',
    name: 'absurd-spectacle-extended',
    prompt: 'Surreal theatrical political rally stage with empty podium center. Confetti falling in dramatic slow motion. Multiple spotlights sweeping. American flags waving. Crowd sounds fading. Absurdist political theater. Satirical atmosphere. Cinematic irony. Grand but hollow spectacle.',
    duration: 10 as const,
    description: 'Absurd Spectacle - Extended (10s)'
  }
];

async function generateExtendedCinematics() {
  console.log('═══════════════════════════════════════════════');
  console.log('🎬 EXTENDED OPENING CINEMATICS GENERATION');
  console.log('   Duration: 10 seconds each (25% longer!)');
  console.log('   Model: Gen-3 Alpha Turbo');
  console.log('   Resolution: 1280x768 HD');
  console.log('═══════════════════════════════════════════════\n');

  // Check Runway ML status
  const isReady = await checkRunwayStatus();
  if (!isReady) {
    console.error('❌ Runway ML not ready. Please check API key.');
    process.exit(1);
  }

  // We need a seed image for Gen-3 Alpha Turbo
  // Using a simple approach: create a blank/gradient image or use existing texture
  const seedImage = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==';

  const outputPath = 'Dropbox/Replit/ExecutiveDisorder_Assets/09_Video_Assets/Opening_Cinematics_Extended';
  const gameOutputPath = 'client/public/videos/opening-cinematics-extended';

  const results: { id: string; name: string; path: string; size: string }[] = [];

  for (const cinematic of EXTENDED_CINEMATICS) {
    try {
      console.log(`\n${'='.repeat(60)}`);
      console.log(`📹 Generating: ${cinematic.description}`);
      console.log(`${'='.repeat(60)}`);

      const filename = `opening-${cinematic.id}-${cinematic.name}.mp4`;

      // Generate to Dropbox location
      const dropboxPath = await generateImageToVideo({
        promptImage: seedImage,
        promptText: cinematic.prompt,
        duration: cinematic.duration,
        ratio: '1280:768',
        outputPath: outputPath,
        filename: filename
      });

      // Also copy to game public folder
      const fs = await import('fs');
      const gameFullPath = path.join(process.cwd(), gameOutputPath);
      if (!fs.existsSync(gameFullPath)) {
        fs.mkdirSync(gameFullPath, { recursive: true });
      }
      
      const gameFilePath = path.join(gameFullPath, filename);
      fs.copyFileSync(dropboxPath, gameFilePath);

      const fileSize = (fs.statSync(dropboxPath).size / (1024 * 1024)).toFixed(2);

      results.push({
        id: cinematic.id,
        name: cinematic.description,
        path: filename,
        size: `${fileSize} MB`
      });

      console.log(`✅ Successfully generated ${cinematic.description}`);
      console.log(`   📂 Saved to: ${outputPath}/${filename}`);
      console.log(`   📂 Game copy: ${gameOutputPath}/${filename}`);
      console.log(`   💾 Size: ${fileSize} MB`);

    } catch (error) {
      console.error(`❌ Failed to generate ${cinematic.description}:`, error);
    }
  }

  // Print summary
  console.log('\n' + '═'.repeat(60));
  console.log('📊 EXTENDED CINEMATICS GENERATION SUMMARY');
  console.log('═'.repeat(60));
  console.log(`\n✅ Successfully generated: ${results.length}/${EXTENDED_CINEMATICS.length} videos\n`);

  if (results.length > 0) {
    console.log('📹 Generated Videos:');
    results.forEach((result, index) => {
      console.log(`   ${index + 1}. ${result.name}`);
      console.log(`      File: ${result.path}`);
      console.log(`      Size: ${result.size}`);
      console.log('');
    });

    const totalSize = results.reduce((sum, r) => sum + parseFloat(r.size), 0);
    console.log(`📦 Total Size: ${totalSize.toFixed(2)} MB`);
    console.log(`⏱️  Total Duration: ${results.length * 10} seconds`);
    console.log(`\n💡 These extended cinematics are 25% longer than the original 8-second versions!`);
  }

  console.log('\n' + '═'.repeat(60));
  console.log('🎉 Extended cinematics generation complete!');
  console.log('═'.repeat(60));
}

// Run the generator
generateExtendedCinematics().catch(console.error);
