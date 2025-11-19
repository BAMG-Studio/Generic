#!/usr/bin/env tsx

/**
 * Comprehensive audit of Dropbox/Replit asset folders
 * Identifies what exists and what's missing
 */

import { readdirSync, statSync, existsSync } from 'fs';
import { join } from 'path';
import { writeFileSync } from 'fs';

interface FolderStats {
  path: string;
  fileCount: number;
  totalSize: number;
  fileTypes: Record<string, number>;
  files: string[];
  isEmpty: boolean;
}

function getFileExtension(filename: string): string {
  const ext = filename.split('.').pop()?.toLowerCase();
  return ext || 'no-extension';
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function auditFolder(folderPath: string): FolderStats {
  const stats: FolderStats = {
    path: folderPath,
    fileCount: 0,
    totalSize: 0,
    fileTypes: {},
    files: [],
    isEmpty: true
  };

  if (!existsSync(folderPath)) {
    return stats;
  }

  try {
    const items = readdirSync(folderPath);
    
    for (const item of items) {
      const itemPath = join(folderPath, item);
      const itemStat = statSync(itemPath);
      
      if (itemStat.isFile()) {
        stats.fileCount++;
        stats.totalSize += itemStat.size;
        stats.isEmpty = false;
        stats.files.push(item);
        
        const ext = getFileExtension(item);
        stats.fileTypes[ext] = (stats.fileTypes[ext] || 0) + 1;
      } else if (itemStat.isDirectory()) {
        // Recursively count subdirectories
        const subStats = auditFolder(itemPath);
        stats.fileCount += subStats.fileCount;
        stats.totalSize += subStats.totalSize;
        if (!subStats.isEmpty) stats.isEmpty = false;
      }
    }
  } catch (error) {
    console.error(`Error reading ${folderPath}:`, error);
  }

  return stats;
}

function auditDropboxAssets() {
  console.log('📊 Executive Disorder - Dropbox Asset Audit\n');
  console.log('='.repeat(80) + '\n');

  const baseDir = 'Dropbox/Replit';
  const categories = [
    { name: 'Audio - Music', path: `${baseDir}/Art/Audio/Music` },
    { name: 'Audio - SFX', path: `${baseDir}/Art/SFX` },
    { name: 'Character Portraits - Main', path: `${baseDir}/characters/main-portraits` },
    { name: 'Character Portraits - Variations', path: `${baseDir}/characters/variations` },
    { name: 'Character Portraits - Executives', path: `${baseDir}/Portraits/Executives` },
    { name: 'Character Portraits - Staff', path: `${baseDir}/Portraits/Staff` },
    { name: 'Character Portraits - Citizens', path: `${baseDir}/Portraits/Citizens` },
    { name: 'Character Portraits - International', path: `${baseDir}/Portraits/International` },
    { name: 'Character Portraits - Stakeholders', path: `${baseDir}/Portraits/Stakeholders` },
    { name: 'Crisis Characters - All Types', path: `${baseDir}/Crisis` },
    { name: 'Card Assets - EDX Series', path: `${baseDir}/Art/Cards/EDX_Series` },
    { name: 'Card Assets - EDX1 Series', path: `${baseDir}/Art/Cards/EDX1_Series` },
    { name: 'Card Assets - EDX2 Series', path: `${baseDir}/Art/Cards/EDX2_Series` },
    { name: 'Card Assets - EDX3 Series', path: `${baseDir}/Art/Cards/EDX3_Series` },
    { name: 'Logos - Brand', path: `${baseDir}/Brand/Logos` },
    { name: 'Logos - Variations', path: `${baseDir}/logos` },
    { name: 'Scenes - Backgrounds', path: `${baseDir}/Scenes/Backgrounds` },
    { name: 'Scenes - Crisis', path: `${baseDir}/Scenes/CrisisScenes` },
    { name: 'Scenes - Meeting Rooms', path: `${baseDir}/Scenes/MeetingRooms` },
    { name: 'Scenes - News', path: `${baseDir}/Scenes/NewsScenes` },
    { name: 'Scenes - Public Spaces', path: `${baseDir}/Scenes/PublicSpaces` },
    { name: 'UI Assets - Icons', path: `${baseDir}/Art/UI/Icons` },
    { name: 'UI Assets - General', path: `${baseDir}/ui-assets` },
    { name: '3D Models', path: `${baseDir}/Art/3D/Models` },
    { name: '3D Models - General', path: `${baseDir}/models` },
    { name: 'Textures', path: `${baseDir}/textures` },
    { name: 'Fonts', path: `${baseDir}/fonts` },
    { name: 'Generated Images', path: `${baseDir}/generated-images` },
    { name: 'Video - Openings', path: `${baseDir}/Art/Video/Openings` },
    { name: 'Code Backups', path: `${baseDir}/code-backups` }
  ];

  const results: Array<FolderStats & { category: string }> = [];
  let totalFiles = 0;
  let totalSize = 0;

  for (const category of categories) {
    const stats = auditFolder(category.path);
    results.push({ ...stats, category: category.name });
    totalFiles += stats.fileCount;
    totalSize += stats.totalSize;

    const status = stats.isEmpty ? '❌ EMPTY' : '✅';
    const size = formatBytes(stats.totalSize);
    console.log(`${status} ${category.name.padEnd(35)} ${String(stats.fileCount).padStart(4)} files  ${size.padStart(10)}`);
  }

  console.log('\n' + '='.repeat(80));
  console.log(`📊 Total: ${totalFiles} files, ${formatBytes(totalSize)}`);
  console.log('='.repeat(80) + '\n');

  // Identify missing or empty categories
  const emptyCategories = results.filter(r => r.isEmpty);
  const populatedCategories = results.filter(r => !r.isEmpty);

  console.log('🚨 EMPTY/MISSING FOLDERS:\n');
  if (emptyCategories.length === 0) {
    console.log('   ✅ No empty folders found!\n');
  } else {
    emptyCategories.forEach(cat => {
      console.log(`   ❌ ${cat.category}`);
      console.log(`      Path: ${cat.path}`);
      console.log('');
    });
  }

  console.log('✅ POPULATED FOLDERS:\n');
  populatedCategories.forEach(cat => {
    console.log(`   📁 ${cat.category} - ${cat.fileCount} files`);
    const types = Object.entries(cat.fileTypes).map(([ext, count]) => `${count} ${ext}`).join(', ');
    if (types) console.log(`      Types: ${types}`);
    console.log('');
  });

  // Generate detailed report
  const report = `# Executive Disorder - Asset Audit Report
**Date:** ${new Date().toISOString()}
**Total Assets:** ${totalFiles} files
**Total Size:** ${formatBytes(totalSize)}

---

## 📊 Asset Inventory by Category

${results.map(r => `### ${r.category}
- **Path:** \`${r.path}\`
- **Status:** ${r.isEmpty ? '❌ EMPTY' : '✅ Populated'}
- **Files:** ${r.fileCount}
- **Size:** ${formatBytes(r.totalSize)}
${r.fileCount > 0 ? `- **Types:** ${Object.entries(r.fileTypes).map(([ext, count]) => `${count} .${ext}`).join(', ')}` : ''}
${r.files.length > 0 && r.files.length <= 20 ? `\n**Files:**\n${r.files.map(f => `  - ${f}`).join('\n')}` : ''}
`).join('\n')}

---

## 🚨 Empty Folders Requiring Assets

${emptyCategories.length === 0 ? '✅ **No empty folders found!**' : emptyCategories.map(cat => `### ${cat.category}
- **Path:** \`${cat.path}\`
- **Action:** Generate or source assets for this category
`).join('\n')}

---

## 📈 Asset Statistics

### By File Type
${(() => {
  const allTypes: Record<string, number> = {};
  results.forEach(r => {
    Object.entries(r.fileTypes).forEach(([ext, count]) => {
      allTypes[ext] = (allTypes[ext] || 0) + count;
    });
  });
  return Object.entries(allTypes)
    .sort((a, b) => b[1] - a[1])
    .map(([ext, count]) => `- **.${ext}:** ${count} files`)
    .join('\n');
})()}

### Top Categories by File Count
${populatedCategories
  .sort((a, b) => b.fileCount - a.fileCount)
  .slice(0, 10)
  .map((cat, i) => `${i + 1}. **${cat.category}** - ${cat.fileCount} files (${formatBytes(cat.totalSize)})`)
  .join('\n')}

---

## 🎯 Recommendations

### Immediate Priorities
${emptyCategories.length > 0 ? emptyCategories.slice(0, 5).map((cat, i) => `${i + 1}. Generate assets for **${cat.category}**`).join('\n') : '✅ All critical asset categories are populated'}

### Asset Quality Check
- Verify all audio files > 32 bytes (check for placeholders)
- Ensure all character portraits are high resolution
- Check card thumbnails for consistency
- Validate 3D model formats (GLB/GLTF)

### Backup & Sync
- ✅ ${totalFiles} files backed up in Dropbox
- 📊 ${formatBytes(totalSize)} total storage used
- 🔄 Regular sync recommended for new assets

---

**Generated by:** Asset Audit Script
**Last Run:** ${new Date().toISOString()}
`;

  writeFileSync('Dropbox/Replit/ASSET_AUDIT_REPORT.md', report);
  console.log('📄 Detailed report saved to: Dropbox/Replit/ASSET_AUDIT_REPORT.md');
}

auditDropboxAssets();