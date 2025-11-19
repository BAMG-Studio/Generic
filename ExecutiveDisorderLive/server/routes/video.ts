import { Router } from "express";
import { generateCrisisVideos, generateVideo } from "../lib/runwayml";

const router = Router();

// Generate crisis videos endpoint
router.post("/generate-crisis-videos", async (req, res) => {
  try {
    console.log("Starting crisis video generation...");
    const results = await generateCrisisVideos();
    
    res.json({
      success: true,
      message: "Crisis videos generation completed",
      results
    });
  } catch (error: any) {
    console.error("Crisis video generation error:", error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Generate custom video endpoint
router.post("/generate", async (req, res) => {
  try {
    const { prompt, duration = 5 } = req.body;
    
    if (!prompt) {
      return res.status(400).json({ error: "Prompt is required" });
    }
    
    console.log(`Generating video with prompt: ${prompt}`);
    const videoUrl = await generateVideo(prompt, duration);
    
    res.json({
      success: true,
      url: videoUrl,
      prompt
    });
  } catch (error: any) {
    console.error("Video generation error:", error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

export default router;