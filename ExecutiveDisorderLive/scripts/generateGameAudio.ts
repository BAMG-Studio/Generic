/**
 * Batch Audio Generation Script for Executive Disorder
 * 
 * Usage: npm run generate-audio
 * 
 * This script pre-generates voice lines for:
 * - Character introductions
 * - News broadcasts
 * - Decision card narration
 * - Game events
 */

import { elevenlabs } from '../server/services/elevenlabs';
import { characters } from '../client/src/data/characters';

interface AudioAsset {
  text: string;
  character?: string;
  filename: string;
  category: 'intro' | 'news' | 'card' | 'event';
}

const gameAudioAssets: AudioAsset[] = [
  // Character Introductions
  {
    text: "Welcome to Executive Disorder, where political chaos meets comedic catastrophe. Choose your leader wisely... or don't. It probably won't matter.",
    filename: 'intro_welcome.mp3',
    category: 'intro'
  },
  
  // Character-specific introductions
  ...characters.map(char => ({
    text: char.fullBio,
    character: char.name,
    filename: `intro_${char.id}.mp3`,
    category: 'intro' as const
  })),

  // News Broadcasts
  {
    text: "Breaking news: The president has made another decision. Economists are screaming. The public is confused. More at 11.",
    filename: 'news_generic_01.mp3',
    category: 'news'
  },
  {
    text: "This just in: Political chaos continues as expected. Experts say they're no longer surprised by anything. We'll keep you updated on developments.",
    filename: 'news_generic_02.mp3',
    category: 'news'
  },
  {
    text: "In a stunning turn of events, something happened in Washington. Details are unclear, but everyone has an opinion.",
    filename: 'news_generic_03.mp3',
    category: 'news'
  },

  // Game Events
  {
    text: "Your approval rating is plummeting faster than your last economic policy.",
    filename: 'event_low_approval.mp3',
    category: 'event'
  },
  {
    text: "The people love you! Or maybe they just love chaos. Hard to tell anymore.",
    filename: 'event_high_approval.mp3',
    category: 'event'
  },
  {
    text: "Economic disaster alert! Your fiscal policies have consequences. Who knew?",
    filename: 'event_economic_crisis.mp3',
    category: 'event'
  },
  {
    text: "Congratulations! You've somehow managed to make things worse. Impressive.",
    filename: 'event_failure.mp3',
    category: 'event'
  },
  {
    text: "Against all odds, that actually worked. Don't get used to it.",
    filename: 'event_success.mp3',
    category: 'event'
  },

  // Decision Card Narration
  {
    text: "A crisis approaches. Your response will determine the fate of millions. No pressure.",
    filename: 'card_crisis_intro.mp3',
    category: 'card'
  },
  {
    text: "Time to make a decision. Choose carefully... or don't. We're not your parents.",
    filename: 'card_decision_time.mp3',
    category: 'card'
  },
];

async function generateAllAudio() {
  console.log('🎙️ Starting Executive Disorder Audio Generation');
  console.log(`📊 Total assets to generate: ${gameAudioAssets.length}`);
  console.log('');

  const results = {
    success: 0,
    failed: 0,
    errors: [] as string[]
  };

  for (let i = 0; i < gameAudioAssets.length; i++) {
    const asset = gameAudioAssets[i];
    const progress = `[${i + 1}/${gameAudioAssets.length}]`;

    try {
      console.log(`${progress} Generating: ${asset.filename}`);
      
      const voiceId = asset.character
        ? elevenlabs.getCharacterVoice(asset.character)
        : undefined;

      await elevenlabs.generateSpeech({
        text: asset.text,
        voiceId,
        outputPath: asset.filename
      });

      results.success++;
      console.log(`✅ Success: ${asset.filename}`);
    } catch (error: any) {
      results.failed++;
      const errorMsg = `${asset.filename}: ${error.message}`;
      results.errors.push(errorMsg);
      console.error(`❌ Failed: ${errorMsg}`);
    }

    console.log('');
  }

  // Summary
  console.log('');
  console.log('═══════════════════════════════════════════');
  console.log('📊 Audio Generation Complete');
  console.log('═══════════════════════════════════════════');
  console.log(`✅ Successful: ${results.success}`);
  console.log(`❌ Failed: ${results.failed}`);
  console.log(`📁 Total: ${gameAudioAssets.length}`);
  console.log('');

  if (results.errors.length > 0) {
    console.log('❌ Errors:');
    results.errors.forEach(err => console.log(`   - ${err}`));
    console.log('');
  }

  console.log('🎵 Audio files saved to: client/public/audio/voice/');
  console.log('');
}

// Run the script
generateAllAudio()
  .then(() => {
    console.log('🎉 Audio generation script completed!');
    process.exit(0);
  })
  .catch((error) => {
    console.error('💥 Fatal error:', error);
    process.exit(1);
  });
