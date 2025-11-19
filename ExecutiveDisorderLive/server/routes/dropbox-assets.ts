import { Router } from "express";
import { Dropbox, files } from "dropbox";
import path from "path";

const router = Router();

// Recursively list all files in Dropbox folder
async function listAllFiles(dbx: Dropbox, folderPath: string): Promise<files.FileMetadataReference[]> {
  const allFiles: files.FileMetadataReference[] = [];
  
  async function listRecursive(path: string) {
    try {
      let hasMore = true;
      let cursor = "";
      
      while (hasMore) {
        const response = cursor 
          ? await dbx.filesListFolderContinue({ cursor })
          : await dbx.filesListFolder({ path, recursive: true, include_non_downloadable_files: false });
        
        for (const entry of response.result.entries) {
          if (entry['.tag'] === 'file') {
            allFiles.push(entry as files.FileMetadataReference);
          }
        }
        
        hasMore = response.result.has_more;
        cursor = response.result.cursor;
      }
    } catch (error: any) {
      console.error(`Error listing files in ${path}:`, error);
    }
  }
  
  await listRecursive(folderPath);
  return allFiles;
}

// Categorize assets by type and purpose
function categorizeAssets(files: files.FileMetadataReference[]) {
  const categories = {
    images: {
      characters: [] as any[],
      cards: [] as any[],
      backgrounds: [] as any[],
      ui: [] as any[],
      endings: [] as any[],
      other: [] as any[]
    },
    audio: {
      music: [] as any[],
      effects: [] as any[],
      narration: [] as any[],
      other: [] as any[]
    },
    videos: {
      cinematics: [] as any[],
      backgrounds: [] as any[],
      crisis: [] as any[],
      other: [] as any[]
    },
    data: {
      cards: [] as any[],
      characters: [] as any[],
      other: [] as any[]
    }
  };
  
  for (const file of files) {
    const ext = path.extname(file.name).toLowerCase();
    const pathLower = file.path_lower || "";
    
    const fileInfo = {
      name: file.name,
      path: file.path_display,
      size: file.size,
      modified: file.client_modified
    };
    
    // Categorize images
    if (['.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg'].includes(ext)) {
      if (pathLower.includes('character') || pathLower.includes('leader') || pathLower.includes('portrait')) {
        categories.images.characters.push(fileInfo);
      } else if (pathLower.includes('card') || pathLower.includes('decision')) {
        categories.images.cards.push(fileInfo);
      } else if (pathLower.includes('background') || pathLower.includes('scene')) {
        categories.images.backgrounds.push(fileInfo);
      } else if (pathLower.includes('ui') || pathLower.includes('button') || pathLower.includes('logo')) {
        categories.images.ui.push(fileInfo);
      } else if (pathLower.includes('ending') || pathLower.includes('finale')) {
        categories.images.endings.push(fileInfo);
      } else {
        categories.images.other.push(fileInfo);
      }
    }
    // Categorize audio
    else if (['.mp3', '.wav', '.ogg', '.m4a', '.aac'].includes(ext)) {
      if (pathLower.includes('music') || pathLower.includes('theme') || pathLower.includes('soundtrack')) {
        categories.audio.music.push(fileInfo);
      } else if (pathLower.includes('effect') || pathLower.includes('sfx') || pathLower.includes('sound')) {
        categories.audio.effects.push(fileInfo);
      } else if (pathLower.includes('narration') || pathLower.includes('voice') || pathLower.includes('speech')) {
        categories.audio.narration.push(fileInfo);
      } else {
        categories.audio.other.push(fileInfo);
      }
    }
    // Categorize videos
    else if (['.mp4', '.webm', '.mov', '.avi'].includes(ext)) {
      if (pathLower.includes('cinematic') || pathLower.includes('intro') || pathLower.includes('opening')) {
        categories.videos.cinematics.push(fileInfo);
      } else if (pathLower.includes('background') || pathLower.includes('loop')) {
        categories.videos.backgrounds.push(fileInfo);
      } else if (pathLower.includes('crisis') || pathLower.includes('news') || pathLower.includes('event')) {
        categories.videos.crisis.push(fileInfo);
      } else {
        categories.videos.other.push(fileInfo);
      }
    }
    // Categorize data files
    else if (['.json', '.yaml', '.yml', '.txt', '.md'].includes(ext)) {
      if (pathLower.includes('card') || pathLower.includes('decision')) {
        categories.data.cards.push(fileInfo);
      } else if (pathLower.includes('character') || pathLower.includes('leader')) {
        categories.data.characters.push(fileInfo);
      } else {
        categories.data.other.push(fileInfo);
      }
    }
  }
  
  return categories;
}

// Get all assets organized by category
router.get("/assets/scan", async (req, res) => {
  const dropboxToken = process.env.DROPBOX_ACCESS_TOKEN;
  
  if (!dropboxToken) {
    return res.status(401).json({ error: "Dropbox access token not configured" });
  }
  
  try {
    const dbx = new Dropbox({ accessToken: dropboxToken });
    
    console.log("🔍 Scanning all Dropbox assets...");
    const allFiles = await listAllFiles(dbx, "/Replit/ExecutiveDisorder_Assets");
    
    console.log(`Found ${allFiles.length} total files`);
    
    const categorized = categorizeAssets(allFiles);
    
    // Generate summary
    const summary = {
      total: allFiles.length,
      images: {
        total: Object.values(categorized.images).flat().length,
        characters: categorized.images.characters.length,
        cards: categorized.images.cards.length,
        backgrounds: categorized.images.backgrounds.length,
        ui: categorized.images.ui.length,
        endings: categorized.images.endings.length,
        other: categorized.images.other.length
      },
      audio: {
        total: Object.values(categorized.audio).flat().length,
        music: categorized.audio.music.length,
        effects: categorized.audio.effects.length,
        narration: categorized.audio.narration.length,
        other: categorized.audio.other.length
      },
      videos: {
        total: Object.values(categorized.videos).flat().length,
        cinematics: categorized.videos.cinematics.length,
        backgrounds: categorized.videos.backgrounds.length,
        crisis: categorized.videos.crisis.length,
        other: categorized.videos.other.length
      },
      data: {
        total: Object.values(categorized.data).flat().length,
        cards: categorized.data.cards.length,
        characters: categorized.data.characters.length,
        other: categorized.data.other.length
      }
    };
    
    res.json({
      summary,
      assets: categorized
    });
  } catch (error: any) {
    console.error("Error scanning Dropbox assets:", error);
    res.status(500).json({ error: "Failed to scan assets", message: error.message });
  }
});

// Get specific asset file
router.get("/assets/get", async (req, res) => {
  const { path: filePath } = req.query;
  
  if (!filePath || typeof filePath !== 'string') {
    return res.status(400).json({ error: "File path is required" });
  }
  
  const dropboxToken = process.env.DROPBOX_ACCESS_TOKEN;
  if (!dropboxToken) {
    return res.status(401).json({ error: "Dropbox access token not configured" });
  }
  
  try {
    const dbx = new Dropbox({ accessToken: dropboxToken });
    
    const response = await dbx.filesGetTemporaryLink({ path: filePath });
    
    res.json({
      link: response.result.link,
      metadata: response.result.metadata
    });
  } catch (error: any) {
    console.error(`Error getting asset ${filePath}:`, error);
    res.status(500).json({ error: "Failed to get asset", message: error.message });
  }
});

export default router;