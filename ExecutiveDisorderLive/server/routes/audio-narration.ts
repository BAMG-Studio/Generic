import { Router } from "express";
import { ElevenLabsClient, play } from "elevenlabs";
import fs from "fs/promises";
import path from "path";
import { Dropbox } from "dropbox";

const router = Router();

// Initialize ElevenLabs client
const elevenlabs = new ElevenLabsClient({
  apiKey: process.env.ELEVENLABS_API_KEY
});

// Voice IDs for different contexts
const VOICE_IDS = {
  narrator: "21m00Tcm4TlvDq8ikWAM", // Rachel (narrator voice)
  announcer: "pNInz6obpgDQGcFmaJgB", // Adam (news anchor)
  dramatic: "AZnzlk1XvdvUeBnXmlld", // Domi (dramatic)
  professional: "EXAVITQu4vr4xnSDxMaL", // Sarah (professional)
};

// Generate comprehensive game narration
export async function generateGameNarration() {
  const narrationScripts = [
    {
      name: "welcome",
      text: "Welcome to Executive Disorder, the political satire game where your decisions shape the fate of democracy. Choose your character wisely, as each leader brings unique challenges and opportunities. Navigate through political crises, media scandals, and economic disasters. Can you survive fifty turns in office? Let the chaos begin!",
      voice: VOICE_IDS.narrator,
      category: "intro"
    },
    {
      name: "character-selection",
      text: "Select your political champion from twelve unique leaders. Each character has their own strengths, weaknesses, and special abilities. Will you choose a populist firebrand, a diplomatic mastermind, or a corporate tycoon? Your choice determines your path to power or downfall.",
      voice: VOICE_IDS.narrator,
      category: "menu"
    },
    {
      name: "game-start",
      text: "You have taken office. The nation watches your every move. Balance popularity with the people, stability in government, trust from the media, and economic health. Remember, if any resource drops to zero, your political career ends. Good luck, and may democracy survive your leadership!",
      voice: VOICE_IDS.professional,
      category: "gameplay"
    },
    {
      name: "crisis-alert",
      text: "Breaking news! A major crisis has erupted. This is not a drill. Your immediate response will determine the fate of millions. Choose carefully, as crisis decisions have amplified consequences. The world is watching, and history will judge your actions.",
      voice: VOICE_IDS.announcer,
      category: "crisis"
    },
    {
      name: "low-resources-warning",
      text: "Warning! Your resources are critically low. The government teeters on the edge of collapse. One wrong decision could end everything. Consider your options carefully. Sometimes the hardest choices require the strongest wills.",
      voice: VOICE_IDS.dramatic,
      category: "warning"
    },
    {
      name: "victory-announcement",
      text: "Congratulations! You have successfully completed fifty turns in office. Against all odds, you've navigated the treacherous waters of politics and emerged victorious. Your legacy is secured, and democracy lives to fight another day. Well played, leader!",
      voice: VOICE_IDS.narrator,
      category: "ending"
    },
    {
      name: "defeat-announcement",
      text: "Your political career has come to an end. Whether through scandal, economic collapse, revolution, or loss of public trust, your time in office is over. Learn from your mistakes, and perhaps you'll fare better next time. Democracy is resilient, even if you weren't.",
      voice: VOICE_IDS.dramatic,
      category: "ending"
    },
    {
      name: "turn-transition",
      text: "Another decision awaits. The political landscape shifts constantly. What worked yesterday may fail tomorrow. Adapt, survive, and remember: in politics, there are no permanent friends or enemies, only permanent interests.",
      voice: VOICE_IDS.professional,
      category: "gameplay"
    },
    {
      name: "popularity-boost",
      text: "The people love you! Your approval ratings are soaring. Crowds chant your name in the streets. But remember, popularity is fleeting. Today's hero is tomorrow's villain. Use this momentum wisely.",
      voice: VOICE_IDS.narrator,
      category: "feedback"
    },
    {
      name: "stability-crisis",
      text: "Government stability is crumbling! Bureaucrats resign in protest. Opposition parties smell blood in the water. Coalition partners threaten to withdraw support. Act quickly to restore order before complete collapse.",
      voice: VOICE_IDS.dramatic,
      category: "warning"
    },
    {
      name: "media-scandal",
      text: "Breaking: Major scandal rocks the administration! The media is in a feeding frenzy. Every news outlet demands answers. Your press secretary has gone into hiding. Damage control is essential, or this could be the end.",
      voice: VOICE_IDS.announcer,
      category: "crisis"
    },
    {
      name: "economic-meltdown",
      text: "Economic disaster looms! Markets are in free fall. Unemployment skyrockets. The treasury is empty. Citizens demand action as their savings evaporate. This is your greatest test yet.",
      voice: VOICE_IDS.dramatic,
      category: "crisis"
    },
    {
      name: "how-to-play",
      text: "Welcome to the tutorial. In Executive Disorder, you make decisions that affect four key resources: Popularity with citizens, Government Stability, Media Trust, and Economic Health. Each decision card presents choices with different consequences. Keep all resources above zero to survive. Reach turn fifty to achieve victory. Special events occur every five turns. Crisis mode activates when any resource drops below thirty percent. Good luck!",
      voice: VOICE_IDS.professional,
      category: "tutorial"
    },
    {
      name: "achievement-unlocked",
      text: "Achievement unlocked! You've reached a significant milestone in your political journey. Your accomplishments will be remembered in the annals of history. Or at least until the next election cycle.",
      voice: VOICE_IDS.narrator,
      category: "feedback"
    },
    {
      name: "special-ability",
      text: "Special ability activated! Your unique leadership trait grants you a temporary advantage. Use this power wisely, as it may not come again when you need it most.",
      voice: VOICE_IDS.professional,
      category: "gameplay"
    }
  ];

  const results = [];
  
  for (const script of narrationScripts) {
    try {
      console.log(`Generating narration: ${script.name}`);
      
      // Generate audio with ElevenLabs
      const audioStream = await elevenlabs.generate({
        voice: script.voice,
        text: script.text,
        model_id: "eleven_monolingual_v1"
      });
      
      // Convert stream to buffer
      const chunks = [];
      for await (const chunk of audioStream) {
        chunks.push(chunk);
      }
      const audioBuffer = Buffer.concat(chunks);
      
      // Save to local file
      const audioPath = path.join(
        process.cwd(), 
        "client", 
        "public", 
        "audio", 
        "narration",
        `${script.name}.mp3`
      );
      
      await fs.mkdir(path.dirname(audioPath), { recursive: true });
      await fs.writeFile(audioPath, audioBuffer);
      
      // Save to Dropbox
      try {
        const dropboxToken = process.env.DROPBOX_ACCESS_TOKEN;
        if (dropboxToken) {
          const dbx = new Dropbox({ accessToken: dropboxToken });
          await dbx.filesUpload({
            path: `/Replit/ExecutiveDisorder_Assets/06_Audio/Narration/${script.name}.mp3`,
            contents: audioBuffer
          });
          console.log(`Saved ${script.name} to Dropbox`);
        }
      } catch (dbxError) {
        console.error(`Failed to save to Dropbox: ${dbxError}`);
      }
      
      results.push({
        name: script.name,
        path: `/audio/narration/${script.name}.mp3`,
        category: script.category,
        success: true
      });
      
      console.log(`✅ Generated: ${script.name}`);
      
      // Small delay between generations
      await new Promise(resolve => setTimeout(resolve, 500));
    } catch (error) {
      console.error(`Failed to generate ${script.name}:`, error);
      results.push({
        name: script.name,
        success: false,
        error: String(error)
      });
    }
  }
  
  return results;
}

// Generate character-specific voice lines
export async function generateCharacterVoices() {
  const characters = [
    { id: "truther", voice: VOICE_IDS.dramatic, line: "The truth is out there, and I will expose it all!" },
    { id: "commander", voice: VOICE_IDS.professional, line: "Discipline and order will restore this nation to greatness." },
    { id: "dealmaker", voice: VOICE_IDS.narrator, line: "Everything is negotiable. Let's make a deal that works for everyone." },
    { id: "activist", voice: VOICE_IDS.narrator, line: "Change starts from the grassroots. Power to the people!" },
    { id: "technocrat", voice: VOICE_IDS.professional, line: "Data doesn't lie. Let the algorithms guide our decisions." },
    { id: "wildcard", voice: VOICE_IDS.dramatic, line: "Why be predictable when chaos is so much more fun?" }
  ];
  
  const results = [];
  
  for (const character of characters) {
    try {
      const audioStream = await elevenlabs.generate({
        voice: character.voice,
        text: character.line,
        model_id: "eleven_monolingual_v1"
      });
      
      const chunks = [];
      for await (const chunk of audioStream) {
        chunks.push(chunk);
      }
      const audioBuffer = Buffer.concat(chunks);
      
      const audioPath = path.join(
        process.cwd(),
        "client",
        "public",
        "audio",
        "characters",
        `${character.id}-intro.mp3`
      );
      
      await fs.mkdir(path.dirname(audioPath), { recursive: true });
      await fs.writeFile(audioPath, audioBuffer);
      
      results.push({
        character: character.id,
        path: `/audio/characters/${character.id}-intro.mp3`,
        success: true
      });
      
      console.log(`✅ Generated character voice: ${character.id}`);
    } catch (error) {
      console.error(`Failed to generate voice for ${character.id}:`, error);
      results.push({
        character: character.id,
        success: false,
        error: String(error)
      });
    }
  }
  
  return results;
}

// API Endpoints
router.post("/generate-narration", async (req, res) => {
  try {
    console.log("Generating game narration...");
    const results = await generateGameNarration();
    
    res.json({
      success: true,
      message: "Narration generation completed",
      results
    });
  } catch (error: any) {
    console.error("Narration generation error:", error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

router.post("/generate-character-voices", async (req, res) => {
  try {
    console.log("Generating character voices...");
    const results = await generateCharacterVoices();
    
    res.json({
      success: true,
      message: "Character voice generation completed",
      results
    });
  } catch (error: any) {
    console.error("Character voice generation error:", error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

export default router;