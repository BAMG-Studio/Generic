import { generateImageToVideo, imageToDataUri, checkRunwayStatus } from './runwayService.ts';
import { uploadToDropbox } from './dropboxUpload.ts';

interface SceneToAnimate {
  name: string;
  imagePath: string;
  prompt: string;
  duration: 5 | 10;
  outputFilename: string;
}

// Define 5 key scenes to animate
const scenesToAnimate: SceneToAnimate[] = [
  {
    name: 'Oval Office',
    imagePath: 'Dropbox/Replit/Scenes/Backgrounds/oval-office.png',
    prompt: 'Subtle camera zoom, American flag gently waving in breeze, fireplace flames flickering softly, warm lighting with natural shadows moving slightly, presidential atmosphere, cinematic quality',
    duration: 10,
    outputFilename: 'oval-office-animated.mp4'
  },
  {
    name: 'Press Room',
    imagePath: 'Dropbox/Replit/Scenes/Backgrounds/press-room.png',
    prompt: 'Press corps reporters subtly shifting in seats, camera flashes flickering, slight head movements, papers rustling, anticipation in the air, broadcast quality lighting',
    duration: 10,
    outputFilename: 'press-room-animated.mp4'
  },
  {
    name: 'White House Exterior',
    imagePath: 'Dropbox/Replit/Scenes/Backgrounds/white-house-exterior.png',
    prompt: 'Clouds slowly drifting across blue sky, American flag waving on flagpole, fountain water flowing, trees swaying gently in breeze, cinematic establishing shot, presidential majesty',
    duration: 10,
    outputFilename: 'white-house-exterior-animated.mp4'
  },
  {
    name: 'Breaking News Set',
    imagePath: 'Dropbox/Replit/Scenes/NewsScenes/breaking-news-set.png',
    prompt: 'News studio screens flickering with graphics, subtle camera movement, studio lights pulsing slightly, background monitors displaying data, urgent broadcast atmosphere, HD quality',
    duration: 10,
    outputFilename: 'breaking-news-set-animated.mp4'
  },
  {
    name: 'Rally Stage',
    imagePath: 'Dropbox/Replit/Scenes/PublicSpaces/rally-stage.png',
    prompt: 'Massive crowd swaying and waving flags, campaign banners fluttering, stage lights sweeping across audience, people cheering with raised hands, political energy, wide cinematic shot',
    duration: 10,
    outputFilename: 'rally-stage-animated.mp4'
  }
];

async function generateAllAnimatedBackgrounds() {
  console.log('🎬 GENERATING ANIMATED SCENE BACKGROUNDS');
  console.log('==========================================\n');

  // Check Runway API status
  const isReady = await checkRunwayStatus();
  if (!isReady) {
    console.error('❌ Runway ML API not ready. Please check your API key.');
    process.exit(1);
  }

  const results: { scene: string; localPath: string; dropboxPath: string }[] = [];
  const outputDir = 'Dropbox/Replit/Videos/AnimatedBackgrounds';

  console.log(`📁 Output directory: ${outputDir}\n`);
  console.log(`🎥 Generating ${scenesToAnimate.length} animated backgrounds...\n`);

  for (let i = 0; i < scenesToAnimate.length; i++) {
    const scene = scenesToAnimate[i];
    console.log(`\n[${ i + 1}/${scenesToAnimate.length}] ${scene.name}`);
    console.log('─'.repeat(50));

    try {
      // Convert image to data URI
      console.log(`   📸 Loading source image: ${scene.imagePath}`);
      const imageDataUri = imageToDataUri(scene.imagePath);
      
      // Generate video
      const videoPath = await generateImageToVideo({
        promptImage: imageDataUri,
        promptText: scene.prompt,
        duration: scene.duration,
        ratio: '1280:768',
        outputPath: outputDir,
        filename: scene.outputFilename
      });

      console.log(`   ✅ Video saved locally: ${videoPath}`);

      // Upload to Dropbox backend
      const dropboxPath = await uploadToDropbox(
        videoPath,
        `/Replit/Art/Videos/AnimatedBackgrounds/${scene.outputFilename}`
      );

      console.log(`   ☁️  Uploaded to Dropbox: ${dropboxPath}`);

      results.push({
        scene: scene.name,
        localPath: videoPath,
        dropboxPath: dropboxPath
      });

      // Add delay between generations to avoid rate limits
      if (i < scenesToAnimate.length - 1) {
        console.log('\n   ⏳ Waiting 5 seconds before next generation...');
        await new Promise(resolve => setTimeout(resolve, 5000));
      }

    } catch (error) {
      console.error(`   ❌ Failed to generate ${scene.name}:`, error);
    }
  }

  // Print summary
  console.log('\n\n==========================================');
  console.log('📊 GENERATION SUMMARY');
  console.log('==========================================\n');
  console.log(`✅ Successfully generated: ${results.length}/${scenesToAnimate.length} videos\n`);

  if (results.length > 0) {
    console.log('Generated Videos:');
    results.forEach((result, idx) => {
      console.log(`   ${idx + 1}. ${result.scene}`);
      console.log(`      Local: ${result.localPath}`);
      console.log(`      Dropbox: ${result.dropboxPath}\n`);
    });
  }

  console.log('✨ Animated backgrounds generation complete!\n');
  
  return results;
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  generateAllAnimatedBackgrounds()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error('Fatal error:', error);
      process.exit(1);
    });
}

export { generateAllAnimatedBackgrounds };
