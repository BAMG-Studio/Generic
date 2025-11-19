import OpenAI from "openai";
import fs from 'fs';
import https from 'https';

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

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

async function fixDianaHappy() {
  console.log('📰 Fixing Diana Newsworthy happy portrait...\n');

  const prompt = `Political satire character: professional news anchor woman with elegant appearance,
    big exaggerated smile showing joy and enthusiasm, cheerful broadcast journalist expression,
    vibrant saturated colors, comedic caricature style, meme-worthy but professional,
    TV news personality aesthetic, exaggerated positive emotion,
    semi-realistic digital painting with humorous edge, shareable political satire art.`;

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
      await downloadImage(imageUrl, 'client/public/characters/diana-newsworthy-happy.png');
      console.log('✓ Successfully generated Diana Newsworthy happy portrait!');
    }
  } catch (error) {
    console.error('Failed:', error);
  }
}

fixDianaHappy().catch(console.error);