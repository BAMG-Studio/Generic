import { Dropbox } from "dropbox";
import fs from "fs/promises";
import path from "path";

const API_KEY = process.env.RUNWAYML_API_SECRET || "";
const API_URL = "https://api.dev.runwayml.com/v1";

interface VideoGenerationRequest {
  model: string;
  prompt_text: string;
  width?: number;
  height?: number;
  duration?: number;
  seed?: number;
}

interface VideoGenerationResponse {
  id: string;
  status: string;
  created_at: string;
  failure?: string;
  output?: string[];
}

// Generate video using Runway ML Gen-3 Alpha Turbo
export async function generateVideo(prompt: string, duration = 5): Promise<string> {
  const request: VideoGenerationRequest = {
    model: "gen3a_turbo",
    prompt_text: prompt,
    width: 1280,
    height: 720,
    duration: duration,
    seed: Math.floor(Math.random() * 1000000)
  };

  try {
    // Start video generation task
    const response = await fetch(`${API_URL}/tasks`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${API_KEY}`,
        "X-Runway-Version": "2024-11-06",
        "Content-Type": "application/json"
      },
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      throw new Error(`Failed to start video generation: ${response.statusText}`);
    }

    const task: VideoGenerationResponse = await response.json();
    console.log(`Started video generation task: ${task.id}`);

    // Poll for completion
    let completed = false;
    let videoUrl = "";
    let attempts = 0;
    const maxAttempts = 120; // 10 minutes max wait

    while (!completed && attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 5000)); // Wait 5 seconds between polls
      
      const statusResponse = await fetch(`${API_URL}/tasks/${task.id}`, {
        headers: {
          "Authorization": `Bearer ${API_KEY}`,
          "X-Runway-Version": "2024-11-06"
        }
      });

      if (!statusResponse.ok) {
        throw new Error(`Failed to check task status: ${statusResponse.statusText}`);
      }

      const statusData: VideoGenerationResponse = await statusResponse.json();
      
      if (statusData.status === "SUCCEEDED" && statusData.output) {
        completed = true;
        videoUrl = statusData.output[0];
        console.log(`Video generation completed: ${videoUrl}`);
      } else if (statusData.status === "FAILED") {
        throw new Error(`Video generation failed: ${statusData.failure || "Unknown error"}`);
      }
      
      attempts++;
      console.log(`Polling attempt ${attempts}/${maxAttempts}, status: ${statusData.status}`);
    }

    if (!completed) {
      throw new Error("Video generation timed out after 10 minutes");
    }

    return videoUrl;
  } catch (error) {
    console.error("Video generation error:", error);
    throw error;
  }
}

// Generate multiple crisis videos
export async function generateCrisisVideos() {
  const crisisPrompts = [
    {
      name: "economic-meltdown",
      prompt: "Breaking news broadcast studio, dramatic red alerts on screens, STOCK MARKET CRASH headlines, panicked news anchors, financial charts plummeting, emergency economic crisis coverage, professional TV news set, cinematic lighting, high-quality broadcast footage"
    },
    {
      name: "alien-invasion",
      prompt: "Breaking news TV broadcast, UFO hovering over city skyline visible through studio window, FIRST CONTACT alert banner, shocked news anchors pointing at sky, emergency broadcast graphics, professional news studio with alien ships in background, cinematic sci-fi atmosphere"
    },
    {
      name: "zombie-outbreak",
      prompt: "Emergency news broadcast, disheveled news anchor, ZOMBIE OUTBREAK warning graphics, chaos visible through studio windows, emergency alert system activated, apocalyptic news coverage, dark dramatic lighting, horror movie atmosphere in professional news studio"
    },
    {
      name: "climate-disaster",
      prompt: "Breaking news weather center, massive hurricane on radar screens, CLIMATE EMERGENCY headlines, meteorologist pointing at extreme weather maps, flooding and storms visible on monitors, professional broadcast studio, urgent weather crisis coverage"
    },
    {
      name: "political-scandal",
      prompt: "Breaking news political coverage, PRESIDENTIAL SCANDAL banner, serious news anchors discussing crisis, government building on screens, leaked documents graphics, professional news studio, dramatic political emergency broadcast, cinematic journalism footage"
    }
  ];

  const results = [];
  
  for (const crisis of crisisPrompts) {
    try {
      console.log(`Generating crisis video: ${crisis.name}`);
      const videoUrl = await generateVideo(crisis.prompt, 5);
      
      // Download and save video
      const videoResponse = await fetch(videoUrl);
      const videoBuffer = await videoResponse.arrayBuffer();
      
      // Save to local file
      const videoPath = path.join(process.cwd(), "client", "public", "videos", "crisis", `crisis-${crisis.name}.mp4`);
      await fs.writeFile(videoPath, Buffer.from(videoBuffer));
      
      // Also save to Dropbox if available
      try {
        const dropboxToken = process.env.DROPBOX_ACCESS_TOKEN;
        if (dropboxToken) {
          const dbx = new Dropbox({ accessToken: dropboxToken });
          await dbx.filesUpload({
            path: `/Replit/ExecutiveDisorder_Assets/09_Video_Assets/Crisis/${crisis.name}.mp4`,
            contents: Buffer.from(videoBuffer)
          });
          console.log(`Saved ${crisis.name} to Dropbox`);
        }
      } catch (dbxError) {
        console.error(`Failed to save to Dropbox: ${dbxError}`);
      }
      
      results.push({
        name: crisis.name,
        path: `/videos/crisis/crisis-${crisis.name}.mp4`,
        url: videoUrl,
        success: true
      });
      
      console.log(`✅ Generated and saved: ${crisis.name}`);
      
      // Wait between generations to avoid rate limits
      await new Promise(resolve => setTimeout(resolve, 2000));
    } catch (error) {
      console.error(`Failed to generate ${crisis.name}:`, error);
      results.push({
        name: crisis.name,
        success: false,
        error: String(error)
      });
    }
  }
  
  return results;
}