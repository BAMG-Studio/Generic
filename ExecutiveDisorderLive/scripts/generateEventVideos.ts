import { generateImageToVideo, imageToDataUri, checkRunwayStatus } from './runwayService.ts';
import { uploadToDropbox } from './dropboxUpload.ts';

interface EventVideo {
  name: string;
  baseImage: string;
  prompt: string;
  duration: 5 | 10;
  outputFilename: string;
}

// Define 10 dramatic event videos for game moments
const eventVideos: EventVideo[] = [
  {
    name: 'Breaking News Alert',
    baseImage: 'Dropbox/Replit/Scenes/NewsScenes/breaking-news-set.png',
    prompt: 'Breaking news graphics rapidly appearing, red alert banners flashing, urgent BREAKING NEWS text animation, news ticker scrolling fast, dramatic zoom into screen, high-intensity broadcast moment',
    duration: 5,
    outputFilename: 'event-breaking-news.mp4'
  },
  {
    name: 'Economic Crash',
    baseImage: 'Dropbox/Replit/Scenes/CrisisScenes/economic-crisis.png',
    prompt: 'Stock market numbers plummeting rapidly in red, traders panicking and gesturing frantically, screens showing downward arrows, papers flying, chaos on trading floor, financial disaster unfolding',
    duration: 5,
    outputFilename: 'event-economic-crash.mp4'
  },
  {
    name: 'Natural Disaster',
    baseImage: 'Dropbox/Replit/Scenes/CrisisScenes/natural-disaster.png',
    prompt: 'Disaster map with spreading red zones, weather radar showing approaching storm, emergency alerts flashing, satellite imagery of hurricane, crisis management center in action, urgent atmosphere',
    duration: 5,
    outputFilename: 'event-natural-disaster.mp4'
  },
  {
    name: 'Protest Escalation',
    baseImage: 'Dropbox/Replit/Scenes/PublicSpaces/protest-square.png',
    prompt: 'Massive crowd surging forward with protest signs, chanting and raising fists, banners waving intensely, political energy building, dramatic crowd movement, civil unrest atmosphere',
    duration: 5,
    outputFilename: 'event-protest-escalation.mp4'
  },
  {
    name: 'Scandal Reveal',
    baseImage: 'Dropbox/Replit/Scenes/Backgrounds/press-room.png',
    prompt: 'Press corps erupting with camera flashes, reporters jumping to feet shouting questions, microphones thrust forward, shocked reactions, dramatic revelation moment, media frenzy',
    duration: 5,
    outputFilename: 'event-scandal-reveal.mp4'
  },
  {
    name: 'Victory Celebration',
    baseImage: 'Dropbox/Replit/Scenes/PublicSpaces/rally-stage.png',
    prompt: 'Confetti and balloons falling from above, crowd cheering wildly waving American flags, campaign staff celebrating on stage, victory speech atmosphere, triumphant political moment',
    duration: 5,
    outputFilename: 'event-victory-celebration.mp4'
  },
  {
    name: 'Defeat Announcement',
    baseImage: 'Dropbox/Replit/Scenes/Backgrounds/oval-office.png',
    prompt: 'Somber mood with person walking away from camera toward window, head bowed, American flag drooping, shadows lengthening, melancholic atmosphere, political defeat, end of an era',
    duration: 5,
    outputFilename: 'event-defeat.mp4'
  },
  {
    name: 'Crisis Alert',
    baseImage: 'Dropbox/Replit/Scenes/Backgrounds/situation-room.png',
    prompt: 'Red alert lights flashing, screens displaying urgent threat data, military officials rushing to positions, phone ringing urgently, maps showing crisis zones, high-stakes situation room emergency',
    duration: 5,
    outputFilename: 'event-crisis-alert.mp4'
  },
  {
    name: 'Diplomatic Tension',
    baseImage: 'Dropbox/Replit/Scenes/MeetingRooms/international-summit.png',
    prompt: 'Delegates staring intensely across negotiation table, flags of nations prominent, tense body language, uncomfortable shifting in seats, diplomatic standoff, international relations crisis',
    duration: 5,
    outputFilename: 'event-diplomatic-tension.mp4'
  },
  {
    name: 'Media Chaos',
    baseImage: 'Dropbox/Replit/Scenes/NewsScenes/tv-studio.png',
    prompt: 'Multiple TV screens showing conflicting news stories, split screens with arguing pundits, news chyrons rapidly changing, social media feeds scrolling fast, information overload, media circus',
    duration: 5,
    outputFilename: 'event-media-chaos.mp4'
  }
];

async function generateAllEventVideos() {
  console.log('🎬 GENERATING EVENT VIDEO CLIPS');
  console.log('==========================================\n');

  // Check Runway API status
  const isReady = await checkRunwayStatus();
  if (!isReady) {
    console.error('❌ Runway ML API not ready. Please check your API key.');
    process.exit(1);
  }

  const results: { event: string; localPath: string; dropboxPath: string }[] = [];
  const outputDir = 'Dropbox/Replit/Videos/Events';

  console.log(`📁 Output directory: ${outputDir}\n`);
  console.log(`🎥 Generating ${eventVideos.length} event video clips...\n`);

  for (let i = 0; i < eventVideos.length; i++) {
    const event = eventVideos[i];
    console.log(`\n[${i + 1}/${eventVideos.length}] ${event.name}`);
    console.log('─'.repeat(50));

    try {
      // Convert image to data URI
      console.log(`   📸 Loading source image: ${event.baseImage}`);
      const imageDataUri = imageToDataUri(event.baseImage);
      
      // Generate video
      const videoPath = await generateImageToVideo({
        promptImage: imageDataUri,
        promptText: event.prompt,
        duration: event.duration,
        ratio: '1280:768',
        outputPath: outputDir,
        filename: event.outputFilename
      });

      console.log(`   ✅ Video saved locally: ${videoPath}`);

      // Upload to Dropbox backend
      const dropboxPath = await uploadToDropbox(
        videoPath,
        `/Replit/Art/Videos/Events/${event.outputFilename}`
      );

      console.log(`   ☁️  Uploaded to Dropbox: ${dropboxPath}`);

      results.push({
        event: event.name,
        localPath: videoPath,
        dropboxPath: dropboxPath
      });

      // Add delay between generations to avoid rate limits
      if (i < eventVideos.length - 1) {
        console.log('\n   ⏳ Waiting 5 seconds before next generation...');
        await new Promise(resolve => setTimeout(resolve, 5000));
      }

    } catch (error) {
      console.error(`   ❌ Failed to generate ${event.name}:`, error);
    }
  }

  // Print summary
  console.log('\n\n==========================================');
  console.log('📊 GENERATION SUMMARY');
  console.log('==========================================\n');
  console.log(`✅ Successfully generated: ${results.length}/${eventVideos.length} videos\n`);

  if (results.length > 0) {
    console.log('Generated Event Videos:');
    results.forEach((result, idx) => {
      console.log(`   ${idx + 1}. ${result.event}`);
      console.log(`      Local: ${result.localPath}`);
      console.log(`      Dropbox: ${result.dropboxPath}\n`);
    });
  }

  console.log('✨ Event videos generation complete!\n');
  
  return results;
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  generateAllEventVideos()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error('Fatal error:', error);
      process.exit(1);
    });
}

export { generateAllEventVideos };
