import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function ensureDir(dirPath: string) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
}

function copyFile(source: string, dest: string) {
  ensureDir(path.dirname(dest));
  fs.copyFileSync(source, dest);
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

async function copyAssetsToExecutiveDisorder() {
  console.log('📦 COPYING ASSETS TO ExecutiveDisorder_Assets');
  console.log('==========================================\n');

  const baseDestination = 'Dropbox/Replit/ExecutiveDisorder_Assets';
  let totalCopied = 0;
  let totalBytes = 0;

  // Copy scene images to 05_Backgrounds
  console.log('📸 Copying scene images to 05_Backgrounds/...');
  const scenesSource = 'Dropbox/Replit/Scenes';
  const scenesDestBase = path.join(baseDestination, '05_Backgrounds');
  
  if (fs.existsSync(scenesSource)) {
    function copyScenesRecursive(srcDir: string, destDir: string) {
      const entries = fs.readdirSync(srcDir, { withFileTypes: true });
      
      for (const entry of entries) {
        const srcPath = path.join(srcDir, entry.name);
        const destPath = path.join(destDir, entry.name);
        
        if (entry.isDirectory()) {
          ensureDir(destPath);
          copyScenesRecursive(srcPath, destPath);
        } else if (entry.isFile()) {
          const stats = fs.statSync(srcPath);
          copyFile(srcPath, destPath);
          totalCopied++;
          totalBytes += stats.size;
        }
      }
    }
    
    copyScenesRecursive(scenesSource, scenesDestBase);
    console.log(`   ✅ Copied scene images to ${scenesDestBase}\n`);
  }

  // Copy videos to 09_Video_Assets
  console.log('🎥 Copying videos to 09_Video_Assets/...');
  const videosSource = 'Dropbox/Replit/Videos';
  const videosDestBase = path.join(baseDestination, '09_Video_Assets');
  
  if (fs.existsSync(videosSource)) {
    function copyVideosRecursive(srcDir: string, destDir: string) {
      const entries = fs.readdirSync(srcDir, { withFileTypes: true });
      
      for (const entry of entries) {
        const srcPath = path.join(srcDir, entry.name);
        const destPath = path.join(destDir, entry.name);
        
        if (entry.isDirectory()) {
          ensureDir(destPath);
          copyVideosRecursive(srcPath, destPath);
        } else if (entry.isFile()) {
          const stats = fs.statSync(srcPath);
          copyFile(srcPath, destPath);
          totalCopied++;
          totalBytes += stats.size;
        }
      }
    }
    
    copyVideosRecursive(videosSource, videosDestBase);
    console.log(`   ✅ Copied videos to ${videosDestBase}\n`);
  }

  // Copy audio files to 06_Audio
  console.log('🎵 Copying audio files to 06_Audio/...');
  const audioSource = 'client/public/sounds';
  const audioDestBase = path.join(baseDestination, '06_Audio/Placeholders');
  
  if (fs.existsSync(audioSource)) {
    const audioFiles = fs.readdirSync(audioSource).filter(f => 
      ['.mp3', '.wav', '.ogg'].includes(path.extname(f).toLowerCase())
    );
    
    ensureDir(audioDestBase);
    for (const file of audioFiles) {
      const srcPath = path.join(audioSource, file);
      const destPath = path.join(audioDestBase, file);
      const stats = fs.statSync(srcPath);
      copyFile(srcPath, destPath);
      totalCopied++;
      totalBytes += stats.size;
    }
    console.log(`   ✅ Copied ${audioFiles.length} audio placeholders to ${audioDestBase}\n`);
  }

  // Copy documentation to 08_Data_Files
  console.log('📄 Copying documentation to 08_Data_Files/...');
  const docsDestBase = path.join(baseDestination, '08_Data_Files/Documentation');
  ensureDir(docsDestBase);
  
  const docFiles = [
    'VARIATIONS_COMPLETE_OCT10.md',
    'RUNWAY_STATUS_OCT10.md',
    'ZAPSPLAT_DOWNLOAD_LIST.md',
    'AUDIO_REQUIREMENTS.md',
    'FILE_MANIFEST_VARIATIONS.md',
    'UPLOAD_VERIFICATION_LOG.md',
    'replit.md',
    'Dropbox/Replit/ASSET_INVENTORY.json',
    'Dropbox/Replit/ASSET_INVENTORY.md'
  ].filter(file => fs.existsSync(file));
  
  for (const file of docFiles) {
    const fileName = path.basename(file);
    const destPath = path.join(docsDestBase, fileName);
    const stats = fs.statSync(file);
    copyFile(file, destPath);
    totalCopied++;
    totalBytes += stats.size;
  }
  console.log(`   ✅ Copied ${docFiles.length} documentation files to ${docsDestBase}\n`);

  // Copy AI-generated assets tracking to 10_AI_Generated
  console.log('🤖 Creating AI generation tracking in 10_AI_Generated/...');
  const aiDestBase = path.join(baseDestination, '10_AI_Generated');
  ensureDir(aiDestBase);
  
  const aiGenerationLog = {
    lastUpdated: new Date().toISOString(),
    generations: {
      scenes: {
        provider: 'Stock Image Tool',
        count: 105,
        mainScenes: 15,
        variations: 90,
        totalSize: '158 MB',
        location: '05_Backgrounds/'
      },
      videos: {
        provider: 'Runway ML Gen-3 Alpha Turbo',
        count: 14,
        animatedBackgrounds: 5,
        eventClips: 9,
        totalSize: '78 MB',
        location: '09_Video_Assets/'
      },
      audio: {
        provider: 'Pending - Zapsplat Manual Download',
        count: 74,
        status: 'Manual download required',
        location: '06_Audio/SFX/'
      },
      music: {
        provider: 'Pending - Mubert API',
        status: 'Awaiting API key',
        location: '06_Audio/Music/'
      }
    }
  };
  
  fs.writeFileSync(
    path.join(aiDestBase, 'AI_GENERATION_LOG.json'),
    JSON.stringify(aiGenerationLog, null, 2)
  );
  console.log(`   ✅ Created AI generation tracking\n`);

  console.log('==========================================');
  console.log('📊 COPY SUMMARY');
  console.log('==========================================\n');
  console.log(`✅ Total Files Copied: ${totalCopied}`);
  console.log(`📦 Total Size: ${formatBytes(totalBytes)}\n`);
  
  console.log('Destination Structure:');
  console.log(`   ${baseDestination}/`);
  console.log(`   ├── 05_Backgrounds/ (105 scene images)`);
  console.log(`   ├── 06_Audio/ (3 placeholder files)`);
  console.log(`   ├── 08_Data_Files/ (documentation)`);
  console.log(`   ├── 09_Video_Assets/ (14 videos)`);
  console.log(`   └── 10_AI_Generated/ (tracking logs)\n`);
  
  console.log('✨ Asset consolidation complete!\n');
  
  return {
    totalCopied,
    totalBytes,
    destination: baseDestination
  };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  copyAssetsToExecutiveDisorder()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error('Fatal error:', error);
      process.exit(1);
    });
}

export { copyAssetsToExecutiveDisorder };
