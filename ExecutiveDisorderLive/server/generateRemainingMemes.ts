import OpenAI from "openai";
import fs from 'fs';
import https from 'https';
import { characters } from "../client/src/data/characters.js";

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

const memeEmotions = {
  neutral: "confident smirk, meme-worthy expression, internet culture vibe, slightly cocky look",
  happy: "huge exaggerated grin, over-the-top joy, thumbs up energy, viral meme happiness",
  angry: "hilariously angry face, comically red, exaggerated rage, meme-level fury",
  stressed: "absurdly stressed, sweating profusely, comedic panic, meltdown face"
};

async function downloadImage(url: string, filename: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const dir = filename.substring(0, filename.lastIndexOf('/'));
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    
    const file = fs.createWriteStream(filename);
    https.get(url, (response) => {
      response.pipe(file);
      file.on('finish', () => {
        file.close();
        resolve();
      });
    }).on('error', (err) => {
      fs.unlink(filename, () => {});
      reject(err);
    });
  });
}

async function generateMemePortrait(
  character: any,
  emotion: string,
  emotionDesc: string
) {
  const prompt = `Hilarious political satire character portrait, perfect for memes and internet sharing.
    ${character.appearance}, ${character.personality}, ${emotionDesc}.
    Bold exaggerated political caricature, absurdist comedy style, 
    vibrant saturated colors, comedic proportions, internet meme aesthetic,
    funny facial expression perfect for viral sharing, bold outlines,
    satirical and hilarious, meme-worthy character design,
    political comedy gold, social media ready,
    semi-realistic digital painting with comedic exaggeration,
    professional quality but extremely funny, shareable political humor.
    Make it hilariously absurd while still looking polished.`;

  try {
    const response = await openai.images.generate({
      model: "dall-e-3",
      prompt: prompt,
      n: 1,
      size: "1024x1024",
      quality: "hd",
      style: "vivid"
    });

    const imageUrl = response.data?.[0]?.url;
    if (imageUrl) {
      const filename = `client/public/characters/${character.id}-${emotion}.png`;
      await downloadImage(imageUrl, filename);
      console.log(`✓ Generated ${emotion} meme portrait for ${character.name}`);
      return true;
    }
  } catch (error) {
    console.error(`Failed to generate ${emotion} for ${character.name}:`, error);
    return false;
  }
}

async function generateRemaining() {
  console.log('😂 Continuing meme generation...\n');

  // Start from General Steel's stressed emotion (index 5)
  const remainingWork = [
    { charIndex: 5, emotions: ['stressed'] }, // General Steel
    { charIndex: 6, emotions: ['neutral', 'happy', 'angry', 'stressed'] }, // Dr. Technocrat
    { charIndex: 7, emotions: ['neutral', 'happy', 'angry', 'stressed'] }, // Johnny Public
    { charIndex: 8, emotions: ['neutral', 'happy', 'angry', 'stressed'] }, // Diana Newsworthy
    { charIndex: 9, emotions: ['neutral', 'happy', 'angry', 'stressed'] }, // Senator Tradition
  ];

  for (const work of remainingWork) {
    const character = characters[work.charIndex];
    console.log(`\n🎭 Generating for ${character.name}...`);
    
    for (const emotion of work.emotions) {
      const emotionDesc = memeEmotions[emotion as keyof typeof memeEmotions];
      await generateMemePortrait(character, emotion, emotionDesc);
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  }

  console.log('\n\n✅ ALL MEME PORTRAITS COMPLETE!');
  console.log('😂 All 10 characters with 4 emotions each are ready!');
}

generateRemaining().catch(console.error);