import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

interface AssetFile {
  name: string;
  path: string;
  size: number;
  category: string;
  destination: string;
}

function getFileSize(filePath: string): number {
  try {
    const stats = fs.statSync(filePath);
    return stats.size;
  } catch {
    return 0;
  }
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

function scanDirectory(dir: string, category: string, destinationBase: string): AssetFile[] {
  const assets: AssetFile[] = [];
  
  if (!fs.existsSync(dir)) {
    return assets;
  }

  function scan(currentDir: string, relativePath: string = '') {
    const entries = fs.readdirSync(currentDir, { withFileTypes: true });
    
    for (const entry of entries) {
      const fullPath = path.join(currentDir, entry.name);
      const relPath = path.join(relativePath, entry.name);
      
      if (entry.isDirectory()) {
        scan(fullPath, relPath);
      } else if (entry.isFile()) {
        const ext = path.extname(entry.name).toLowerCase();
        if (['.png', '.jpg', '.jpeg', '.mp4', '.mp3', '.wav', '.ogg', '.md', '.json'].includes(ext)) {
          assets.push({
            name: entry.name,
            path: fullPath,
            size: getFileSize(fullPath),
            category,
            destination: path.join(destinationBase, relPath)
          });
        }
      }
    }
  }
  
  scan(dir);
  return assets;
}

async function createInventory() {
  console.log('📋 CREATING COMPREHENSIVE ASSET INVENTORY');
  console.log('==========================================\n');

  const allAssets: AssetFile[] = [];

  // Scan scene images
  console.log('📸 Scanning scene images...');
  const sceneAssets = scanDirectory(
    'Dropbox/Replit/Scenes',
    'Backgrounds',
    'Dropbox/Replit/ExecutiveDisorder_Assets/05_Backgrounds'
  );
  allAssets.push(...sceneAssets);
  console.log(`   Found ${sceneAssets.length} scene files`);

  // Scan videos
  console.log('🎥 Scanning videos...');
  const videoAssets = scanDirectory(
    'Dropbox/Replit/Videos',
    'Videos',
    'Dropbox/Replit/ExecutiveDisorder_Assets/09_Video_Assets'
  );
  allAssets.push(...videoAssets);
  console.log(`   Found ${videoAssets.length} video files`);

  // Scan audio
  console.log('🎵 Scanning audio files...');
  const audioAssets = scanDirectory(
    'client/public/sounds',
    'Audio',
    'Dropbox/Replit/ExecutiveDisorder_Assets/06_Audio'
  );
  allAssets.push(...audioAssets);
  console.log(`   Found ${audioAssets.length} audio files`);

  // Scan documentation
  console.log('📄 Scanning documentation...');
  const docFiles = [
    'VARIATIONS_COMPLETE_OCT10.md',
    'RUNWAY_STATUS_OCT10.md',
    'ZAPSPLAT_DOWNLOAD_LIST.md',
    'AUDIO_REQUIREMENTS.md',
    'FILE_MANIFEST_VARIATIONS.md',
    'UPLOAD_VERIFICATION_LOG.md',
    'replit.md'
  ].filter(file => fs.existsSync(file));
  
  for (const file of docFiles) {
    allAssets.push({
      name: file,
      path: file,
      size: getFileSize(file),
      category: 'Documentation',
      destination: `Dropbox/Replit/ExecutiveDisorder_Assets/08_Data_Files/${file}`
    });
  }
  console.log(`   Found ${docFiles.length} documentation files`);

  // Calculate totals
  const totalSize = allAssets.reduce((sum, asset) => sum + asset.size, 0);
  
  console.log('\n==========================================');
  console.log('📊 INVENTORY SUMMARY');
  console.log('==========================================\n');
  console.log(`Total Assets: ${allAssets.length}`);
  console.log(`Total Size: ${formatBytes(totalSize)}\n`);

  // Group by category
  const byCategory: Record<string, AssetFile[]> = {};
  for (const asset of allAssets) {
    if (!byCategory[asset.category]) {
      byCategory[asset.category] = [];
    }
    byCategory[asset.category].push(asset);
  }

  console.log('Assets by Category:');
  for (const [category, assets] of Object.entries(byCategory)) {
    const catSize = assets.reduce((sum, a) => sum + a.size, 0);
    console.log(`   ${category}: ${assets.length} files (${formatBytes(catSize)})`);
  }

  // Create JSON inventory
  const inventory = {
    createdAt: new Date().toISOString(),
    totalAssets: allAssets.length,
    totalSize: totalSize,
    totalSizeFormatted: formatBytes(totalSize),
    categories: byCategory,
    assets: allAssets
  };

  const inventoryPath = 'Dropbox/Replit/ASSET_INVENTORY.json';
  fs.writeFileSync(inventoryPath, JSON.stringify(inventory, null, 2));
  console.log(`\n✅ Inventory saved to: ${inventoryPath}`);

  // Create markdown summary
  let markdown = `# Executive Disorder - Complete Asset Inventory\n`;
  markdown += `**Generated:** ${new Date().toLocaleString()}\n\n`;
  markdown += `## Summary\n\n`;
  markdown += `- **Total Assets:** ${allAssets.length}\n`;
  markdown += `- **Total Size:** ${formatBytes(totalSize)}\n\n`;
  markdown += `## Assets by Category\n\n`;
  
  for (const [category, assets] of Object.entries(byCategory)) {
    const catSize = assets.reduce((sum, a) => sum + a.size, 0);
    markdown += `### ${category} (${assets.length} files, ${formatBytes(catSize)})\n\n`;
    
    // Group by subdirectory
    const bySubdir: Record<string, AssetFile[]> = {};
    for (const asset of assets) {
      const subdir = path.dirname(asset.path).split('/').pop() || 'root';
      if (!bySubdir[subdir]) {
        bySubdir[subdir] = [];
      }
      bySubdir[subdir].push(asset);
    }
    
    for (const [subdir, files] of Object.entries(bySubdir)) {
      markdown += `**${subdir}:**\n`;
      for (const file of files.slice(0, 10)) {
        markdown += `- ${file.name} (${formatBytes(file.size)})\n`;
      }
      if (files.length > 10) {
        markdown += `- ... and ${files.length - 10} more files\n`;
      }
      markdown += `\n`;
    }
  }

  markdown += `## Asset Destinations\n\n`;
  markdown += `All assets will be copied to \`Dropbox/Replit/ExecutiveDisorder_Assets/\`:\n\n`;
  markdown += `- **05_Backgrounds** - ${byCategory['Backgrounds']?.length || 0} scene images\n`;
  markdown += `- **09_Video_Assets** - ${byCategory['Videos']?.length || 0} video files\n`;
  markdown += `- **06_Audio** - ${byCategory['Audio']?.length || 0} audio files\n`;
  markdown += `- **08_Data_Files** - ${byCategory['Documentation']?.length || 0} documentation files\n`;

  const mdPath = 'Dropbox/Replit/ASSET_INVENTORY.md';
  fs.writeFileSync(mdPath, markdown);
  console.log(`✅ Summary saved to: ${mdPath}\n`);

  return inventory;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  createInventory()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error('Fatal error:', error);
      process.exit(1);
    });
}

export { createInventory };
