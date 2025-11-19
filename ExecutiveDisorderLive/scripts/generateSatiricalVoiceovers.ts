import ElevenLabs from "elevenlabs";
import fs from 'fs';
import path from 'path';

const OUTPUT_DIR = 'Dropbox/Replit/ExecutiveDisorder_Assets/06_Audio/voiceovers';

// Ensure output directory exists
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

const client = new ElevenLabs({
  apiKey: process.env.ELEVENLABS_API_KEY
});

// Satirical voiceover lines for each scene
const VOICEOVERS = [
  {
    id: 'power-ascension',
    text: "From zero... to hero? More like from zero... to political chaos!",
    voice: "Brian", // Professional narrator voice
    filename: 'power-ascension-vo.mp3'
  },
  {
    id: 'political-chaos',
    text: "Welcome to the Oval Office. Where everything that can go wrong... will go wrong!",
    voice: "Chris", // Enthusiastic voice
    filename: 'political-chaos-vo.mp3'
  },
  {
    id: 'media-frenzy',
    text: "Breaking news: Everything is breaking! Including your approval rating!",
    voice: "Adam", // Deep, dramatic voice
    filename: 'media-frenzy-vo.mp3'
  },
  {
    id: 'critical-decision',
    text: "Every choice matters. Especially the wrong ones.",
    voice: "Antoni", // Soft, ominous voice
    filename: 'critical-decision-vo.mp3'
  },
  {
    id: 'grand-opening',
    text: "In a world of political chaos... one person must make impossible decisions... Welcome to Executive Disorder!",
    voice: "Brian", // Epic trailer voice
    filename: 'grand-opening-vo.mp3'
  }
];

async function generateVoiceover(text: string, voice: string, filename: string) {
  console.log(`\n🎙️  Generating: ${filename}`);
  console.log(`   Text: "${text}"`);
  console.log(`   Voice: ${voice}`);

  try {
    const audio = await client.generate({
      voice: voice,
      text: text,
      model_id: "eleven_multilingual_v2"
    });

    const outputPath = path.join(OUTPUT_DIR, filename);
    const chunks: Buffer[] = [];
    
    for await (const chunk of audio) {
      chunks.push(chunk);
    }
    
    const audioBuffer = Buffer.concat(chunks);
    fs.writeFileSync(outputPath, audioBuffer);
    
    const sizeMB = (audioBuffer.length / (1024 * 1024)).toFixed(2);
    console.log(`   ✅ Generated successfully! (${sizeMB} MB)`);
    
    return outputPath;
  } catch (error: any) {
    console.error(`   ❌ Error generating voiceover: ${error.message}`);
    throw error;
  }
}

async function generateAllVoiceovers() {
  console.log('═══════════════════════════════════════════════════════════');
  console.log('🎙️  GENERATING SATIRICAL VOICEOVERS');
  console.log('   Provider: ElevenLabs');
  console.log('   Style: Political satire comedy');
  console.log('═══════════════════════════════════════════════════════════\n');

  const results: string[] = [];

  for (const vo of VOICEOVERS) {
    try {
      const path = await generateVoiceover(vo.text, vo.voice, vo.filename);
      results.push(path);
    } catch (error) {
      console.error(`Failed to generate ${vo.id}:`, error);
    }
  }

  console.log('\n' + '═'.repeat(70));
  console.log('📊 VOICEOVER GENERATION SUMMARY');
  console.log('═'.repeat(70));
  console.log(`\n✅ Successfully generated: ${results.length}/${VOICEOVERS.length} voiceovers\n`);

  if (results.length > 0) {
    console.log('🎙️  Generated Voiceovers:');
    results.forEach((path, index) => {
      console.log(`   ${index + 1}. ${path.split('/').pop()}`);
    });
  }

  console.log('\n' + '═'.repeat(70));
  console.log('🎉 Voiceover generation complete!');
  console.log('═'.repeat(70));
}

// Run the generator
generateAllVoiceovers().catch(console.error);
