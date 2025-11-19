#!/usr/bin/env tsx
/**
 * Sync upscaled and new images to Dropbox
 * Replaces old versions to save space
 */

import { Dropbox } from 'dropbox';
import { promises as fs } from 'fs';
import path from 'path';

// Dropbox client setup (from Replit integration)
let connectionSettings: any;

async function getAccessToken() {
  if (connectionSettings && connectionSettings.settings.expires_at && new Date(connectionSettings.settings.expires_at).getTime() > Date.now()) {
    return connectionSettings.settings.access_token;
  }
  
  const hostname = process.env.REPLIT_CONNECTORS_HOSTNAME;
  const xReplitToken = process.env.REPL_IDENTITY 
    ? 'repl ' + process.env.REPL_IDENTITY 
    : process.env.WEB_REPL_RENEWAL 
    ? 'depl ' + process.env.WEB_REPL_RENEWAL 
    : null;

  if (!xReplitToken) {
    throw new Error('X_REPLIT_TOKEN not found for repl/depl');
  }

  connectionSettings = await fetch(
    'https://' + hostname + '/api/v2/connection?include_secrets=true&connector_names=dropbox',
    {
      headers: {
        'Accept': 'application/json',
        'X_REPLIT_TOKEN': xReplitToken
      }
    }
  ).then(res => res.json()).then(data => data.items?.[0]);

  const accessToken = connectionSettings?.settings?.access_token || connectionSettings.settings?.oauth?.credentials?.access_token;

  if (!connectionSettings || !accessToken) {
    throw new Error('Dropbox not connected');
  }
  return accessToken;
}

async function getDropboxClient() {
  const accessToken = await getAccessToken();
  return new Dropbox({ accessToken });
}

// File upload helper
async function uploadFile(dbx: Dropbox, localPath: string, dropboxPath: string) {
  const fileContent = await fs.readFile(localPath);
  
  try {
    await dbx.filesUpload({
      path: dropboxPath,
      contents: fileContent,
      mode: { '.tag': 'overwrite' }, // Replace existing files
      autorename: false,
      mute: true,
    });
    return true;
  } catch (error: any) {
    console.error(`❌ Failed to upload ${localPath}: ${error.message}`);
    return false;
  }
}

// Get all files from directory
async function getFiles(dir: string, extension: string = '.png'): Promise<string[]> {
  try {
    const files = await fs.readdir(dir);
    return files.filter(f => f.endsWith(extension)).map(f => path.join(dir, f));
  } catch {
    return [];
  }
}

// Main sync function
async function syncToDropbox() {
  console.log('🔄 Starting Dropbox Sync...\n');
  console.log('📂 Target: /Replit/ExecutiveDisorder_Assets/\n');
  
  const dbx = await getDropboxClient();
  
  let uploaded = 0;
  let failed = 0;
  
  // 1. Sync Character Portraits (01_Characters/)
  console.log('📸 Syncing Character Portraits...');
  const characterFiles = await getFiles('client/public/characters');
  
  for (const file of characterFiles) {
    const filename = path.basename(file);
    const dropboxPath = `/Replit/ExecutiveDisorder_Assets/01_Characters/${filename}`;
    
    console.log(`   Uploading: ${filename}`);
    const success = await uploadFile(dbx, file, dropboxPath);
    if (success) {
      uploaded++;
      console.log(`   ✅ Success (replaced old version)`);
    } else {
      failed++;
    }
  }
  
  // 2. Sync Generated Images (10_AI_Generated/)
  console.log('\n🎨 Syncing Generated Images...');
  const generatedFiles = await getFiles('attached_assets/generated_images');
  
  for (const file of generatedFiles) {
    const filename = path.basename(file);
    const dropboxPath = `/Replit/ExecutiveDisorder_Assets/10_AI_Generated/${filename}`;
    
    console.log(`   Uploading: ${filename}`);
    const success = await uploadFile(dbx, file, dropboxPath);
    if (success) {
      uploaded++;
      console.log(`   ✅ Success`);
    } else {
      failed++;
    }
  }
  
  // 3. Sync UI Elements (04_UI_Elements/)
  console.log('\n🖼️  Syncing UI Elements...');
  const uiFiles = await getFiles('client/public/ui');
  
  for (const file of uiFiles) {
    const filename = path.basename(file);
    const dropboxPath = `/Replit/ExecutiveDisorder_Assets/04_UI_Elements/${filename}`;
    
    console.log(`   Uploading: ${filename}`);
    const success = await uploadFile(dbx, file, dropboxPath);
    if (success) {
      uploaded++;
      console.log(`   ✅ Success`);
    } else {
      failed++;
    }
  }
  
  // 4. Sync Backgrounds (05_Backgrounds/)
  console.log('\n🌄 Syncing Backgrounds...');
  const backgroundFiles = await getFiles('client/public/backgrounds');
  
  for (const file of backgroundFiles) {
    const filename = path.basename(file);
    const dropboxPath = `/Replit/ExecutiveDisorder_Assets/05_Backgrounds/${filename}`;
    
    console.log(`   Uploading: ${filename}`);
    const success = await uploadFile(dbx, file, dropboxPath);
    if (success) {
      uploaded++;
      console.log(`   ✅ Success`);
    } else {
      failed++;
    }
  }
  
  // 5. Sync Crisis Videos (09_Video_Assets/)
  console.log('\n🎬 Syncing Crisis Videos...');
  const videoFiles = await getFiles('client/public/videos/crisis', '.mp4');
  
  for (const file of videoFiles) {
    const filename = path.basename(file);
    const dropboxPath = `/Replit/ExecutiveDisorder_Assets/09_Video_Assets/${filename}`;
    
    console.log(`   Uploading: ${filename}`);
    const success = await uploadFile(dbx, file, dropboxPath);
    if (success) {
      uploaded++;
      console.log(`   ✅ Success`);
    } else {
      failed++;
    }
  }
  
  // 6. Sync Documentation Files (08_Data_Files/)
  console.log('\n📄 Syncing Documentation...');
  const docFiles = [
    'ASSET_MANIFEST.md',
    'AUDIO_REQUIREMENTS.md',
    'IMAGE_OPTIMIZATION_REPORT.md',
    'UPSCALING_COMPLETE_SUMMARY.md',
  ];
  
  for (const filename of docFiles) {
    try {
      const dropboxPath = `/Replit/ExecutiveDisorder_Assets/08_Data_Files/${filename}`;
      console.log(`   Uploading: ${filename}`);
      const success = await uploadFile(dbx, filename, dropboxPath);
      if (success) {
        uploaded++;
        console.log(`   ✅ Success`);
      } else {
        failed++;
      }
    } catch (e) {
      console.log(`   ⏭️  Skipped (file not found)`);
    }
  }
  
  // Summary
  console.log('\n' + '='.repeat(50));
  console.log('✨ Sync Complete!');
  console.log('='.repeat(50));
  console.log(`✅ Uploaded: ${uploaded} files`);
  console.log(`❌ Failed: ${failed} files`);
  console.log(`📂 Location: /Replit/ExecutiveDisorder_Assets/`);
  console.log('\n📝 Note: Old versions have been replaced to save space');
}

// Run the sync
syncToDropbox().catch(console.error);
